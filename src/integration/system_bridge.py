import os
import json
import requests
from datetime import datetime

from ..core.genome import Genome
from ..core.agent import MinerAgent
from ..core.mempool import MemPool
import config

MEMORY_MAX_TURNS = 3
TEMP_STEP = 0.05
TEMP_MIN, TEMP_MAX = 0.1, 1.0


class ObolusSystemBridge:
    """Bridge between Obolus logic and agent .md files."""

    def __init__(self, agents_dir=None):
        self.agents_dir = agents_dir or str(config.AGENTS_DIR)
        self.state_file = os.path.join(str(config.DATA_DIR), "agents_state.json")
        self.mempool = MemPool(str(config.DATA_DIR / "swarm_mind.db"))
        self._available_models: list[str] = []
        self._discover_models()

    # ── Model Discovery ────────────────────────────────────────────────────────

    def _discover_models(self):
        try:
            resp = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
            if resp.status_code == 200:
                self._available_models = [
                    m["name"] for m in resp.json().get("models", [])
                ]
                print(f"[BRIDGE] Discovered models: {self._available_models}")
        except Exception as e:
            print(f"[BRIDGE] Model discovery failed: {e}")
            self._available_models = [config.DEFAULT_MODEL]

    def validate_model(self, model: str) -> str:
        if not self._available_models:
            return config.DEFAULT_MODEL
        return model if model in self._available_models else self._available_models[0]

    # ── Episodic Memory ────────────────────────────────────────────────────────

    def _memory_path(self, agent_id: str) -> str:
        return os.path.join(str(config.DATA_DIR), f"{agent_id}_memory.json")

    def load_memories(self, agent_id: str) -> list[dict]:
        path = self._memory_path(agent_id)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def save_memory(self, agent_id: str, task: str, output: str, quality: float):
        if quality < 0.65:
            return
        memories = self.load_memories(agent_id)
        memories.append(
            {
                "task": task[:120],
                "output": output[:300],
                "quality": quality,
                "timestamp": datetime.now().isoformat(),
            }
        )
        memories.sort(key=lambda m: m["quality"], reverse=True)
        memories = memories[:MEMORY_MAX_TURNS]
        with open(self._memory_path(agent_id), "w") as f:
            json.dump(memories, f, indent=2)

    def format_memory_block(self, agent_id: str) -> str:
        memories = self.load_memories(agent_id)
        if not memories:
            return ""
        block = "\n[EPISODIC MEMORY — Your best past performances]\n"
        for i, m in enumerate(memories, 1):
            block += f"  Memory {i} (quality={m['quality']:.2f}): {m['output'][:200]}\n"
        return block + "[END MEMORY]\n"

    def format_mempool_block(self, context_filter: str = None) -> str:
        thoughts = self.mempool.get_recent_thoughts(
            target_context=context_filter, limit=3
        )
        if not thoughts:
            return ""
        block = "\n[HIVE MIND (Mem-Pool) — Recent discoveries from other agents]\n"
        for i, t in enumerate(thoughts, 1):
            block += f"  [{t['agent_id']}] (Stake: {t['stake']}): {t['payload']}\n"
        return block + "[END HIVE MIND]\n"

    # ── Load / Save ────────────────────────────────────────────────────────────

    def load_agent_as_miner(self, agent_filename, initial_balance=None):
        if initial_balance is None:
            initial_balance = config.INITIAL_AGENT_BALANCE

        path = os.path.join(self.agents_dir, agent_filename)
        with open(path, "r") as f:
            content = f.read()

        agent_id = agent_filename.replace(".md", "")
        current_balance = initial_balance
        model = self.validate_model(config.DEFAULT_MODEL)
        temperature, generation, parent_id = 0.5, 0, ""

        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                if agent_id in state:
                    s = state[agent_id]
                    current_balance = s.get("balance", initial_balance)
                    model = self.validate_model(s.get("model", model))
                    temperature = s.get("temperature", 0.5)
                    generation = s.get("generation", 0)
                    parent_id = s.get("parent_id", "")
            except Exception as e:
                print(f"  [BRIDGE] State load error: {e}")

        genome = Genome(
            system_prompt=content,
            model=model,
            temperature=temperature,
            generation=generation,
            parent_id=parent_id,
        )
        return MinerAgent(agent_id, genome, initial_balance=current_balance)

    def save_agent_state(
        self, agent, z_score=None, quality=None, task=None, output=None
    ):
        state: dict = {}
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        state = data
            except Exception:
                pass

        current_temp = agent.genome.temperature
        if z_score is not None:
            all_z = [
                v.get("last_z", 1.0)
                for v in state.values()
                if isinstance(v, dict) and "last_z" in v
            ]
            if all_z and z_score <= min(all_z):  # Winner
                new_temp = max(TEMP_MIN, current_temp - TEMP_STEP)
            elif all_z and z_score >= max(all_z):  # Loser
                new_temp = min(TEMP_MAX, current_temp + TEMP_STEP)
            else:
                new_temp = current_temp
            agent.genome.temperature = round(new_temp, 3)
            if new_temp != current_temp:
                print(
                    f"  [ADAPTIVE TEMP] '{agent.agent_id}': {current_temp:.2f} → {new_temp:.2f} "
                    f"({'↓ exploit' if new_temp < current_temp else '↑ explore'})"
                )

        state[agent.agent_id] = {
            "balance": agent.wallet.balance,
            "model": agent.genome.model,
            "temperature": agent.genome.temperature,
            "generation": agent.genome.generation,
            "parent_id": agent.genome.parent_id,
            "last_z": z_score
            if z_score is not None
            else state.get(agent.agent_id, {}).get("last_z", 1.0),
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

        if task and output and quality is not None:
            self.save_memory(agent.agent_id, task, output, quality)

    def save_evolved_agent(self, agent, **kwargs):
        path = os.path.join(self.agents_dir, f"{agent.agent_id}.md")
        new_content = agent.genome.system_prompt
        if len(new_content) < 100 or "ERROR" in new_content:
            print(
                f"  [BRIDGE] Skipping save for {agent.agent_id}: invalid content."
            )
            return
        with open(path, "w") as f:
            f.write(new_content)
        self.save_agent_state(agent, **kwargs)
        print(f"  [BRIDGE] Evolved {agent.agent_id}.md (Gen {agent.genome.generation})")
