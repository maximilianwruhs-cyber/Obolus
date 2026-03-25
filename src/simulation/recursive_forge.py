import os
import requests
import json

import config


class RecursiveForge:
    """Allows agents to rewrite their own Python helpers for efficiency."""

    def __init__(self):
        self.tool_dir = str(config.PROJECT_ROOT / "src" / "tools_evolved")
        os.makedirs(self.tool_dir, exist_ok=True)

    def evolve_tool_code(self, tool_name, original_code, improvement_prompt):
        ollama_url = f"{config.OLLAMA_URL}/api/generate"

        system_instructions = """
        [RECURSIVE FORGE - TOOL EVOLUTION]
        You are an Expert Software Engineer for Python and Thermodynamics.
        Task: Refactor the provided code for maximum execution speed and minimal resource usage.
        Constraint: Return ONLY the raw Python code. No markdown blocks, no explanations.
        """

        full_prompt = f"{improvement_prompt}\n\nORIGINAL CODE:\n{original_code}"

        payload = {
            "model": config.DEFAULT_MODEL,
            "system": system_instructions,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }

        try:
            response = requests.post(ollama_url, json=payload, timeout=60)
            new_code = response.json().get("response", "").strip()

            if "import" in new_code or "def" in new_code:
                tool_path = os.path.join(self.tool_dir, f"{tool_name}_v.py")
                with open(tool_path, "w") as f:
                    f.write(new_code)
                return tool_path, True
        except Exception as e:
            return str(e), False
        return "Invalid output from LLM", False


if __name__ == "__main__":
    forge = RecursiveForge()
    print("[RECURSIVE FORGE] Tool Forge Ready.")
