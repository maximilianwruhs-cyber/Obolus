import sqlite3
import json
import time
import os


class MemPool:
    """
    The Hive Mind Mem-Pool.
    A high-concurrency SQLite database in WAL mode.
    Allows agents to publish, stake, and read discoveries across the swarm.
    """

    def __init__(self, db_path="swarm_mind.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mem_pool (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    agent_id TEXT,
                    task_context TEXT,
                    payload TEXT,
                    stake REAL DEFAULT 0.0,
                    upvotes INTEGER DEFAULT 0,
                    downvotes INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def publish(self, agent_id: str, task_context: str, payload: dict, stake: float = 0.0) -> int:
        payload_str = json.dumps(payload)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO mem_pool (timestamp, agent_id, task_context, payload, stake) VALUES (?, ?, ?, ?, ?)",
                (time.time(), agent_id, task_context, payload_str, stake),
            )
            conn.commit()
            return cursor.lastrowid

    def get_recent_thoughts(self, target_context: str = None, limit: int = 5) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if target_context:
                cursor.execute(
                    "SELECT * FROM mem_pool WHERE task_context LIKE ? ORDER BY stake DESC, timestamp DESC LIMIT ?",
                    (f"%{target_context}%", limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM mem_pool ORDER BY stake DESC, timestamp DESC LIMIT ?",
                    (limit,),
                )
            return [dict(row) for row in cursor.fetchall()]

    def consensus_vote(self, thought_id: int, agent_id: str, is_upvote: bool, stake_amount: float = 0.0):
        column = "upvotes" if is_upvote else "downvotes"
        with self._get_connection() as conn:
            conn.execute(
                f"UPDATE mem_pool SET {column} = {column} + 1, stake = stake + ? WHERE id = ?",
                (stake_amount, thought_id),
            )
            conn.commit()

    def wipe_pool(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM mem_pool")
            conn.execute("VACUUM")


if __name__ == "__main__":
    pool = MemPool("/tmp/test_swarm.db")
    pool.publish("agent_alpha", "Find highest port", {"port": 8080}, stake=5.0)
    pool.publish("agent_beta", "Find highest port", {"port": 9090}, stake=10.0)
    thoughts = pool.get_recent_thoughts()
    print("Mem-Pool state:")
    for t in thoughts:
        print(f"[{t['agent_id']}] Stake: {t['stake']} -> {t['payload']}")
    os.remove("/tmp/test_swarm.db")
