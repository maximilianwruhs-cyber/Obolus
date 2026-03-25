#!/usr/bin/env python3
"""
Forge Service — creates persistent microservices from agent-generated code.
Writes a Python file and creates a systemd --user unit for it.
"""

import os
import sys
import subprocess
from pathlib import Path

SERVICES_DIR = Path(__file__).parent.parent / "data" / "microservices"


def forge_service(service_name: str, raw_code: str) -> str:
    SERVICES_DIR.mkdir(parents=True, exist_ok=True)

    py_file = SERVICES_DIR / f"{service_name}.py"
    with open(py_file, "w") as f:
        f.write(raw_code)

    unit_name = f"obulus-{service_name}"
    unit_content = f"""[Unit]
Description=Obolus Microservice: {service_name}
After=network.target

[Service]
ExecStart={sys.executable} {py_file}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""
    unit_dir = Path.home() / ".config" / "systemd" / "user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    unit_file = unit_dir / f"{unit_name}.service"

    with open(unit_file, "w") as f:
        f.write(unit_content)

    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "--now", unit_name], check=True)
        return f"SUCCESS: Service '{unit_name}' created and started."
    except Exception as e:
        return f"ERROR: Service creation failed: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: tool_forge_service.py <service_name> <python_code>")
        sys.exit(1)
    print(forge_service(sys.argv[1], sys.argv[2]))
