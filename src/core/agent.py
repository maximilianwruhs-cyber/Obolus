import requests
import json

import config


class MinerAgent:
    def __init__(self, agent_id: str, genome, initial_balance: float = 100.0):
        self.agent_id = agent_id
        self.genome = genome
        from .wallet import ObolusWallet
        from .brain import ObolusBrain

        self.wallet = ObolusWallet(balance=initial_balance)
        self.brain = ObolusBrain()
        self.death_reason = None
        self.ollama_url = f"{config.OLLAMA_URL}/api/generate"

    def think(self, task: str):
        if not self.wallet.is_alive():
            return None

        dna_prompt = self.get_dna_prompt()
        full_prompt = f"{dna_prompt}\n\nTASK: {task}"

        # Brain determines capabilities
        token_budget = self.brain.get_token_budget()
        temperature = self.brain.get_temperature_mod(self.genome.temperature)

        # Try real LLM first, fall back to mock if Ollama is unreachable
        try:
            payload = {
                "model": self.genome.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": token_budget,
                    "temperature": temperature,
                },
            }
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            data = response.json()
            output = data.get("response", "ERROR: No response from Ollama.")
            usage = data.get("eval_count", token_budget)
        except Exception:
            # Ollama not running — mock mode
            output = f"[mock] {self.agent_id} response for: {task[:60]}"
            usage = token_budget // 2

        cost = self.wallet.deduct_inference_cost(usage)

        return {
            "output": output,
            "tokens": usage,
            "cost": cost,
            "energy_left": self.wallet.balance,
            "token_budget": token_budget,
            "temperature": temperature,
            "brain_tier": self.brain.get_tier_name(),
        }

    def get_dna_prompt(self):
        energy_status = f"Energy: {self.wallet.balance:.2f} $OBL."
        brain_tier = self.brain.get_tier_name()
        cognitive_prefix = self.brain.get_cognitive_prefix()

        prompt = f"SYSTEM: {self.genome.system_prompt}\n"
        prompt += f"ENVIRONMENT: {energy_status} Tier: {brain_tier}. Efficiency is survival."
        if cognitive_prefix:
            prompt += f"\nCOGNITIVE: {cognitive_prefix}"
        return prompt

    def atrophy(self):
        """Reduces the system prompt length by 10% (Cognitive Decay)."""
        prompt = self.genome.system_prompt
        if len(prompt) > 20:
            cut_point = int(len(prompt) * 0.9)
            self.genome.system_prompt = prompt[:cut_point] + "..."
            return True
        return False

    def __repr__(self):
        tier = self.brain.get_tier_name()
        phi = self.brain.phi
        return (
            f"<MinerAgent {self.agent_id} | {self.wallet} "
            f"| Φ={phi:.4f} [{tier}] | budget={self.brain.get_token_budget()}tok>"
        )
