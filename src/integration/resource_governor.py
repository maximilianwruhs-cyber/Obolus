import json
import os

import config


class GZMOThermalGovernor:
    """
    Elastic Grid Governor.
    Ensures all agents can run simultaneously by dynamically splitting capacity.
    """

    def __init__(self, state_path=None):
        self.state_path = state_path or str(config.DATA_DIR / "governor_state.json")
        self.max_system_load = 1.0
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f:
                self.state = json.load(f)
        else:
            self.state = {"critical_mode": False}

    def calculate_elastic_quotas(self, agents_with_ranks, total_base_capacity=1024):
        if not agents_with_ranks:
            return {}

        total_rank_sum = sum([rank for _, rank in agents_with_ranks])
        quotas = {}

        for agent_id, rank in agents_with_ranks:
            share = rank / total_rank_sum
            agent_quota = max(16, int(total_base_capacity * share))
            quotas[agent_id] = agent_quota

        return quotas
