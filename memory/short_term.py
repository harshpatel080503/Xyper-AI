class ShortTermMemory:
    def __init__(self):
        self.cache = {}
    
    def set(self, key, value):
        self.cache[key] = value

    def get(self, key, default=None):
        return self.cache.get(key, default)
    
    def clear(self):
        self.cache.clear()