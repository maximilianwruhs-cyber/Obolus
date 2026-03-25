import random
import requests
import json
from typing import Optional

from ..core.genome import Genome
from ..core.agent import MinerAgent
import config


class Forge:
    def __init__(self, ollama_url=None, available_models=None):
        self.mutation_history = []
        self.generation_count = 0
        self.ollama_url = ollama_url or f"{config.OLLAMA_URL}/api/generate"
        self.available_models = available_models or [config.DEFAULT_MODEL]

    def analyze_failure(self, dead_agent, metrics_history=None, fitness_result=None):
        """Analyze why the agent failed, using FitnessResult if available."""
        # Use structured fitness data if available
        if fitness_result is not None:
            reason = fitness_result.reason or "unknown"
            Q = fitness_result.quality
            E = fitness_result.efficiency
            V = fitness_result.variance_penalty

            if "low_quality" in reason:
                return (f"Low Quality (Q={Q:.3f}): Output correctness is below threshold. "
                        f"Agent needs better reasoning or more precise answers.")
            if "no_efficiency_gain" in reason:
                return (f"Energy Waste (E={E:.3f}): Consuming more energy than baseline. "
                        f"Agent must produce the same quality with fewer tokens.")
            if "low_score" in reason:
                return (f"Weak Fitness (z={fitness_result.z_score:.4f}, V={V:.3f}): "
                        f"Combined quality×efficiency is too low or output is too inconsistent.")
            if reason == "invalid_energy_measurement":
                return "Invalid Energy: Measurement failure. System error, not agent fault."
            return f"Fitness Rejected: {reason}"

        # Legacy fallback for metrics_history dicts
        if metrics_history:
            avg_efficiency = (
                sum([m.get("efficiency", 0) for m in metrics_history]) / len(metrics_history)
            )
            if avg_efficiency < 0.5:
                return "Extreme Entropy: Too many tokens for the quality provided."

        if dead_agent.wallet.balance <= 0:
            return "Energy Depletion: Burn rate exceeded rewards consistently."
        return "Stagnation: Low quality scores compared to competitors."

    def evolve_genome(self, parent_agent, failure_reason, fitness_result=None):
        """Uses a local LLM to evolve the system prompt."""
        if not self.ollama_url:
            return f"{parent_agent.genome.system_prompt} (Mock Mutation: Be more precise.)"

        # Build fitness context for the Meta-LLM
        fitness_context = ""
        if fitness_result is not None:
            fitness_context = (
                f"\n        METRICS:\n"
                f"          Quality (Q):  {fitness_result.quality:.4f}\n"
                f"          Efficiency (E): {fitness_result.efficiency:.4f}\n"
                f"          Variance (V): {fitness_result.variance_penalty:.4f}\n"
                f"          z-score:      {fitness_result.z_score:.4f}\n"
            )

        evolution_prompt = f"""
        [OBOLUS EVOLUTIONARY FORGE]
        You are a genetic optimizer for AI agents.

        SUCCESSFUL PARENT DNA: "{parent_agent.genome.system_prompt}"
        REASON FOR COMPETITOR DEATH: "{failure_reason}"
        {fitness_context}
        GOAL: Rewrite the System Prompt for a new offspring.
        The offspring must retain the core identity of the parent but specifically solve the failure reason.
        Keep the prompt concise and efficient.

        NEW SYSTEM PROMPT:
        """
        try:
            payload = {
                "model": config.DEFAULT_MODEL,
                "prompt": evolution_prompt,
                "stream": False,
                "options": {"num_predict": 100, "temperature": 0.7},
            }
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            data = response.json()
            return data.get("response", parent_agent.genome.system_prompt).strip()
        except Exception as e:
            print(f"  [FORGE ERROR] Real evolution failed: {e}")
            return f"{parent_agent.genome.system_prompt} (Fallback Mutation: Be precise.)"

    def _pick_model(self, dead_agent, best_parent, fitness_result=None):
        """Select model for new agent. May mutate to a different model."""
        if len(self.available_models) <= 1:
            return best_parent.genome.model

        # If the dead agent was inefficient (low E), try a smaller model
        if fitness_result and fitness_result.reason and "no_efficiency_gain" in fitness_result.reason:
            # Sort models by name (heuristic: smaller param count = earlier)
            sorted_models = sorted(self.available_models)
            current_idx = None
            for i, m in enumerate(sorted_models):
                if m == dead_agent.genome.model:
                    current_idx = i
                    break
            # Try to go one model smaller
            if current_idx is not None and current_idx > 0:
                chosen = sorted_models[current_idx - 1]
                print(f"  [FORGE] Model mutation: {dead_agent.genome.model} → {chosen} (efficiency pressure)")
                return chosen

        # If quality was too low, try a larger model
        if fitness_result and fitness_result.reason and "low_quality" in fitness_result.reason:
            sorted_models = sorted(self.available_models)
            current_idx = None
            for i, m in enumerate(sorted_models):
                if m == dead_agent.genome.model:
                    current_idx = i
                    break
            if current_idx is not None and current_idx < len(sorted_models) - 1:
                chosen = sorted_models[current_idx + 1]
                print(f"  [FORGE] Model mutation: {dead_agent.genome.model} → {chosen} (quality pressure)")
                return chosen

        # Otherwise inherit from best parent
        return best_parent.genome.model

    def rebirth(self, dead_agent, survivors, epoch, metrics_history=None, fitness_result=None):
        """Creates a new agent based on top performers and failure analysis."""
        self.generation_count += 1
        failure_reason = "System Wipe"

        if not survivors:
            print("  [FORGE] No survivors found. Spawning from baseline...")
            model = random.choice(self.available_models)
            new_genome = Genome("Be helpful and concise.", model, 0.5)
            parent_id = "Baseline"
        else:
            best_parent = max(survivors, key=lambda a: a.wallet.balance)
            print(f"  [FORGE] Selecting {best_parent.agent_id} as Genetic Alpha.")

            failure_reason = self.analyze_failure(dead_agent, metrics_history, fitness_result)
            new_prompt = self.evolve_genome(best_parent, failure_reason, fitness_result)
            new_model = self._pick_model(dead_agent, best_parent, fitness_result)

            new_temp = max(
                0.1,
                min(1.0, best_parent.genome.temperature + random.uniform(-0.1, 0.1)),
            )
            new_genome = Genome(
                system_prompt=new_prompt,
                model=new_model,
                temperature=round(new_temp, 2),
            )
            parent_id = best_parent.agent_id

        new_id = f"{dead_agent.agent_id.split('_')[0]}_v{self.generation_count}"
        new_agent = MinerAgent(new_id, new_genome, initial_balance=50.0)

        self.mutation_history.append(
            {
                "epoch": epoch,
                "parent": parent_id,
                "child": new_id,
                "model": new_genome.model,
                "mutation_prompt": new_genome.system_prompt,
                "reason": failure_reason,
            }
        )
        return new_agent
