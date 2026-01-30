import sqlite3
from datetime import datetime
import json

class InvestigationStore:
    def __init__(self, db_path="investigations.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            decision TEXT,
            evidence TEXT,
            created_at TEXT
        )
        """)
        self.conn.commit()

    def save(self, report):
        self.conn.execute(
            """
            INSERT INTO investigations
            (transaction_id, decision, evidence, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                report["transaction_id"],
                str(report["decision"]),
                json.dumps(report["evidence"]),
                datetime.utcnow().isoformat()
            )
        )
        self.conn.commit()