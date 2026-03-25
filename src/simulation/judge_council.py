import requests
import json
import re

import config


class SOTAJudgeCouncil:
    """Consensus evaluation through three different perspectives."""

    def __init__(self, ollama_url=None):
        self.ollama_url = ollama_url or f"{config.OLLAMA_URL}/api/generate"

    def evaluate_consensus(self, task, agent_output):
        perspectives = [
            "You are a strict technical auditor. Rate accuracy and security (0.0 to 1.0).",
            "You are a thermodynamic engineer. Rate precision and conciseness (0.0 to 1.0).",
            "You are a Chief of Staff. Rate system-wide utility and logic (0.0 to 1.0).",
        ]
        scores = []
        for persona in perspectives:
            score = self._ask_judge(persona, task, agent_output)
            scores.append(score)

        avg_quality_y = sum(scores) / len(scores)
        return round(avg_quality_y, 4), scores

    def _ask_judge(self, persona, task, output):
        prompt = (
            f"[JUDGE COUNCIL]\n{persona}\n\n"
            f"TASK: {task}\nAGENT RESPONSE: {output}\n\n"
            f"Provide ONLY a numeric score between 0.0 and 1.0. No text.\nSCORE:"
        )
        try:
            payload = {
                "model": config.DEFAULT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 5, "temperature": 0.1},
            }
            resp = requests.post(self.ollama_url, json=payload, timeout=60)
            text = resp.json().get("response", "0.5")
            match = re.search(r"([0-1]\.[0-9]+|[0-1])", text)
            return float(match.group(1)) if match else 0.5
        except Exception:
            return 0.5
