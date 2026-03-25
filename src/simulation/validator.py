import random


class LocalValidator:
    def __init__(self):
        self.tasks = [
            "Write a Python script to sort a list.",
            "Explain the 2nd law of thermodynamics.",
            "Solve 123 * 456.",
            "Draft a system prompt for a helpful assistant.",
        ]

    def generate_task(self):
        return random.choice(self.tasks)

    def evaluate(self, output: str) -> float:
        """Returns a score between 0.0 and 1.0."""
        return round(random.uniform(0.1, 1.0), 2)

    def calculate_payout(self, score: float, base_reward: float = 10.0) -> float:
        """Payout scales with quality."""
        return score * base_reward


class SystemValidatorV1:
    """System-level validator for agent task evaluation."""

    def evaluate(self, agent_id: str, task: str, output: str, tokens: int) -> dict:
        word_count = len(output.split())
        q_score = min(1.0, max(0.1, word_count / 60.0))
        efficiency = min(1.0, max(0.01, 50 / max(1, tokens)))
        return {
            "agent_id": agent_id,
            "q_score": round(q_score, 4),
            "efficiency": round(efficiency, 4),
            "tokens": tokens,
        }
