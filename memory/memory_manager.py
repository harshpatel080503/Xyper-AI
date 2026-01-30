import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.embeddings import EmbeddingModel

class MemoryManager:
    def __init__(self):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.embedder = EmbeddingModel()

    def remember_case(self, case_summary: str, metadata: dict):
        embedding = self.embedder.embed(case_summary)
        self.ltm.add(embedding, metadata)

    def recall_similar(self, query: str):
        embedding = self.embedder.embed(query)
        return self.ltm.search(embedding)