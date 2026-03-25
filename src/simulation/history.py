import json
import os


class HistoryManager:
    def __init__(self, filepath=None):
        if filepath is None:
            import config
            filepath = str(config.DATA_DIR / "evolution_history.json")
        self.filepath = filepath

    def save(self, history):
        with open(self.filepath, "w") as f:
            json.dump(history, f, indent=4)
        print(f"  [HISTORY] Evolution logs saved to {self.filepath}")

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                return json.load(f)
        return []
