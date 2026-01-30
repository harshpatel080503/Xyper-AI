import json
import os

class FeedbackStore:
    def __init__(self, path="feedback"):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def record(self, transaction_id, decision, human_label, notes=""):
        record = {
            "transaction_id": transaction_id,
            "system_decision": decision,
            "human_label": human_label,
            "notes": notes
        }
        with open(f"{self.path}/{transaction_id}.json", "w") as f:
            json.dump(record, f, indent=2)