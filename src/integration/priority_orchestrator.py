import json
import os

import config


class ObolusPriorityOrchestrator:
    """
    Manages system priority based on the formula z = x / y.
    x = Resource share (0.0 - 1.0)
    y = Value of mined tokens (OBL)
    z = Weighting (lower is better/more efficient)
    """

    def __init__(self, state_path=None):
        self.state_path = state_path or str(
            config.DATA_DIR / "system_priority_state.json"
        )
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f:
                self.state = json.load(f)
        else:
            self.state = {
                "agents": {},
                "total_system_load": 1.0,
                "difficulty": 1.0,
                "total_tokens_per_round": config.TOTAL_TOKENS_PER_ROUND,
            }

    def adjust_difficulty(self):
        avg_z = (
            sum([a["z"] for a in self.state["agents"].values()])
            / len(self.state["agents"])
            if self.state["agents"]
            else 1.0
        )
        if avg_z < 0.05:
            self.state["difficulty"] = round(
                self.state.get("difficulty", 1.0) + 0.1, 2
            )
            print(
                f"  [ORCHESTRATOR] Efficiency high! Difficulty raised to {self.state['difficulty']}"
            )
        self.save_state()

    def save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=4)

    def update_z_weighting(self, agent_id, resource_share_x, reward_y):
        if agent_id not in self.state["agents"]:
            self.state["agents"][agent_id] = {"z": 1.0, "balance": 50.0, "last_x": 0.1}

        safe_y = max(reward_y, 0.001)
        new_z = resource_share_x / safe_y

        current = self.state["agents"][agent_id]
        current["z"] = round((current["z"] * 0.5) + (new_z * 0.5), 6)
        current["balance"] = round(current["balance"] + reward_y, 2)
        current["last_x"] = resource_share_x

        self.save_state()
        return current["z"]

    def get_elastic_quotas(self, agent_ids, total_tokens=None):
        if total_tokens is None:
            total_tokens = config.TOTAL_TOKENS_PER_ROUND

        weights = {}
        total_inverse_z = 0

        for aid in agent_ids:
            agent_data = self.state["agents"].get(aid, {"z": 1.0})
            z = agent_data.get("z", 1.0)
            inv_z = 1.0 / max(z, 0.0001)
            weights[aid] = inv_z
            total_inverse_z += inv_z

        quotas = {}
        for aid in agent_ids:
            share = weights[aid] / total_inverse_z
            quotas[aid] = max(16, int(total_tokens * share))

        return quotas

    def get_leaderboard(self):
        return sorted(self.state["agents"].items(), key=lambda x: x[1]["z"])
