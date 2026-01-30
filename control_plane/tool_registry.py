class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.call_counts = {}
        self.failures = {}
    
    def register(self, name, func, fallback=None):
        self.tools[name] = {
            "func": func,
            "fallback": fallback
        }
        self.call_counts[name] = 0
        self.failures[name] = 0

    def call(self, name, *args, **kwargs):
        if name not in self.tools:
            raise ValueError("Tool not registered")
        try:
            return self.tools[name]["func"](*args, **kwargs)
        except Exception:
            self.failures[name] += 1
            if self.tools[name]["fallback"]:
                return self.tools[name]["fallback"](*args, **kwargs)
        
        self.call_counts[name] += 1
        return self.tools[name](*args, **kwargs)