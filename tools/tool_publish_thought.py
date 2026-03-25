#!/usr/bin/env python3
"""
Hive Mind Publisher — agents publish thoughts to the shared Mem-Pool.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.core.mempool import MemPool


def main():
    if len(sys.argv) < 5:
        print("Usage: tool_publish_thought.py <agent_id> <context> <payload_json> <stake>")
        sys.exit(1)

    agent_id = sys.argv[1]
    context = sys.argv[2]
    payload = json.loads(sys.argv[3])
    stake = float(sys.argv[4])

    pool = MemPool(str(config.DATA_DIR / "swarm_mind.db"))
    row_id = pool.publish(agent_id, context, payload, stake)
    print(f"Published thought #{row_id} by {agent_id} (stake: {stake})")


if __name__ == "__main__":
    main()
