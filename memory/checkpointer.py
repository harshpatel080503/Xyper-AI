import json
import os
from datetime import datetime

class FileCheckpointer:
    def __init__(self, path="checkpoints"):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def save(self, state):
        ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S_%f")
        filepath = os.path.join(self.path, f"{ts}.json")

        with open(filepath, "w") as f:
            json.dump(state, f, default=str)