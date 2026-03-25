#!/usr/bin/env python3
"""
Core Rewrite Tool — allows agents to securely patch Obolus source code.
Auto-backup + syntax check + rollback on failure.
"""

import os
import sys
import json
import shutil
import ast
import subprocess
from pathlib import Path

# Restrict rewriting to the Obolus src directory
OBULUS_ROOT = Path(__file__).parent.parent.resolve()


def check_syntax(file_path: str) -> bool:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ast.parse(f.read(), filename=file_path)
        return True
    except SyntaxError:
        return False


def rewrite_core(relative_file_path: str, new_code: str) -> dict:
    target_path = (OBULUS_ROOT / relative_file_path).resolve()

    if not str(target_path).startswith(str(OBULUS_ROOT)):
        return {"status": "error", "message": f"Access Denied: Cannot modify files outside of {OBULUS_ROOT}"}

    if not target_path.exists():
        return {"status": "error", "message": f"File {relative_file_path} not found."}

    backup_path = f"{target_path}.godhead.bak"

    try:
        shutil.copy2(str(target_path), backup_path)

        with open(str(target_path), "w", encoding="utf-8") as f:
            f.write(new_code)

        if not check_syntax(str(target_path)):
            shutil.copy2(backup_path, str(target_path))
            return {"status": "error", "message": "Syntax Error. Rollback successful."}

        compile_check = subprocess.run(
            [sys.executable, "-m", "py_compile", str(target_path)],
            capture_output=True, text=True,
        )
        if compile_check.returncode != 0:
            shutil.copy2(backup_path, str(target_path))
            return {"status": "error", "message": f"Compilation failed: {compile_check.stderr}. Rollback successful."}

        os.remove(backup_path)
        return {"status": "success", "message": f"Core rewrite successful: {relative_file_path}"}

    except Exception as e:
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, str(target_path))
        return {"status": "error", "message": f"Rewrite failed: {e}. System rolled back."}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"status": "error", "message": "Usage: tool_core_rewrite.py <relative_path> <new_code>"}))
        sys.exit(1)
    result = rewrite_core(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
