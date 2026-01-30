import faiss
import numpy as np

class LongTermMemory:
    def __init__(self, embedding_dim: int = 384):
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata = []

    def add(self, embedding, meta):
        self.index.add(np.array([embedding]).astype("float32"))
        self.metadata.append(meta)

    def search(self, embedding, k=3):
        # If no memory yet, return empty
        if len(self.metadata) == 0:
            return []

        distances, indices = self.index.search(
            np.array([embedding]).astype("float32"), k
        ) 

        results = []
        for idx in indices[0]:
            # FAISS returns -1 or out-of-range when empty / padded
            if idx == -1:
                continue
            if idx >= len(self.metadata):
                continue
            results.append(self.metadata[idx])

        return results
