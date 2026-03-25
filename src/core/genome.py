from dataclasses import dataclass, field


@dataclass
class Genome:
    system_prompt: str
    model: str
    temperature: float = 0.7
    context_window: int = 4096
    # Genealogy — updated by the Forge on each evolution
    generation: int = 0
    parent_id: str = ""

    def to_dict(self):
        return {
            "model": self.model,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt,
            "generation": self.generation,
            "parent_id": self.parent_id,
        }
