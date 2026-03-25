#!/usr/bin/env python3
"""
Model Orchestrator — query, pull, and swap Ollama models.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Import config if available, else use env/defaults
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import config
    OLLAMA_URL = config.OLLAMA_URL
except ImportError:
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def pull_model(model_name: str) -> dict:
    print(f"📡 [MODEL] Pulling model: {model_name}...")
    try:
        payload = {"name": model_name, "stream": False}
        resp = requests.post(f"{OLLAMA_URL}/api/pull", json=payload, timeout=600)
        resp.raise_for_status()
        return {"status": "success", "message": f"Model {model_name} downloaded."}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": f"Download for {model_name} timed out."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to pull model: {e}"}


def list_installed_models() -> dict:
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return {"status": "success", "models": models}
    except Exception as e:
        return {"status": "error", "message": f"Failed to query models: {e}"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: tool_model_orchestration.py [pull <model> | list]"
        }))
        sys.exit(1)

    action = sys.argv[1]
    if action == "list":
        result = list_installed_models()
    elif action == "pull" and len(sys.argv) == 3:
        result = pull_model(sys.argv[2])
    else:
        result = {"status": "error", "message": "Invalid action or missing arguments."}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
