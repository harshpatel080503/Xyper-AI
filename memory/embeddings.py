import hashlib
import numpy as np

class EmbeddingModel:
    """
    Offline, deterministic embedding model.
    No API keys.
    No external dependencies.
    Perfect for development & testing.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed(self, text: str):
        hash_bytes = hashlib.sha256(text.encode("utf-8")).digest()

        vector = np.frombuffer(hash_bytes, dtype=np.uint8).astype("float32")

        if len(vector) < self.dim:
            vector = np.pad(vector, (0, self.dim - len(vector)))
        else:
            vector = vector[:self.dim]
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector