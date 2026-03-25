#!/usr/bin/env python3
"""
Process Reaper — grants agents permission to stop/start non-critical services.
"""

import sys
import subprocess
import json

ALLOWED_SERVICES = [
    "ollama.service",
    "syncthing.service",
    "tracker-miner-fs-3.service",
]


def reap_process(service_name: str, action: str) -> str:
    if service_name not in ALLOWED_SERVICES:
        return f"CRITICAL ERROR: Permission denied. Allowed: {ALLOWED_SERVICES}"

    if action not in ["stop", "start", "restart", "status"]:
        return f"ERROR: Invalid action '{action}'. Use stop, start, restart, or status."

    try:
        if action == "status":
            result = subprocess.run(
                ["systemctl", "--user", "is-active", service_name],
                capture_output=True, text=True,
            )
            return f"Service {service_name} status: {result.stdout.strip()}"
        else:
            subprocess.run(["systemctl", "--user", action, service_name], check=True)
            return f"SUCCESS: '{action}' performed on {service_name}."
    except Exception as e:
        return f"ERROR: Failed to {action} {service_name}: {e}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            payload = json.loads(sys.argv[1])
            service = payload.get("service_name")
            action = payload.get("action")
            if service and action:
                print(reap_process(service, action))
            else:
                print("ERROR: Missing service_name or action.")
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON payload.")
    else:
        print("ERROR: No arguments provided.")
