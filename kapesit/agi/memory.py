import numpy as np
class EpisodicMemory:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.memory = []
    def store(self, episode):
        if len(self.memory) >= self.capacity:
            self.memory.pop(0)
        self.memory.append(episode)
    def recall(self, idx=None):
        if idx is None:
            return self.memory[-1] if self.memory else None
        return self.memory[idx] if idx < len(self.memory) else None
class SemanticMemory:
    def __init__(self):
        self.knowledge = {}
    def add(self, concept, info):
        self.knowledge[concept] = info
    def get(self, concept):
        return self.knowledge.get(concept, None)
    def search(self, keyword):
        return {k: v for k, v in self.knowledge.items() if keyword in k or keyword in str(v)} 