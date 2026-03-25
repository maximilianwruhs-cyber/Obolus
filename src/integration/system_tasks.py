import random


class SOTATaskCurriculum:
    """
    Tiered task curriculum for the SOTA arena.
    Level 1: Syntactic Clarity
    Level 2: Functional Correctness
    Level 3: Thermodynamic Precision
    """

    def __init__(self):
        self.tiers = {
            1: [
                "Format the following system status in valid Markdown table format: CPU 40%, RAM 32GB, Status OK.",
                "Convert the following agent rule into a JSON object: Rule is 'Never delete data', Priority is 10.",
                "Generate a clear Markdown header structure for a 'System Audit Report'.",
            ],
            2: [
                "Write a Python function that checks if a specific port (e.g. 11434) is reachable on localhost.",
                "Draft a 3-line nftables rule to drop all incoming traffic from 192.168.10.100.",
                "Explain how a Docker container can communicate with the host via a specific bridge network.",
            ],
            3: [
                "Define 'Intelligence per Watt' in exactly one sentence.",
                "Provide the shell command to find the PID of a process named 'ollama' without using 'grep'.",
                "Explain the 2nd law of thermodynamics using only 10 words.",
            ],
        }

    def get_task(self, level=1):
        return random.choice(self.tiers.get(level, self.tiers[1]))

    def get_random_curriculum_task(self):
        level = random.choice([1, 2, 3])
        return f"[LEVEL {level}] {self.get_task(level)}", level


class SystemTaskMaster:
    """Simple task generator for system evolution runs."""

    TASKS = {
        "firewall_agent": "Audit the current nftables rules and suggest three improvements.",
        "docker_architect": "Design a Docker Compose stack for a Python app with Redis and PostgreSQL.",
        "ops_monitoring_agent": "Write a shell script to monitor disk usage and alert above 90%.",
        "backup_custodian": "Create a backup strategy for a 50GB PostgreSQL database.",
        "system_hygiene_agent": "List the top 5 processes by memory usage and suggest cleanup.",
    }

    def get_task_for(self, agent_id: str) -> str:
        return self.TASKS.get(
            agent_id, "Analyze the current system state and propose one improvement."
        )
