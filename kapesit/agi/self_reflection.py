import numpy as np
class SelfReflection:
    def __init__(self):
        self.performance_history = []
    def evaluate(self, metrics):
        self.performance_history.append(metrics)
        return np.mean([m['score'] for m in self.performance_history])
    def suggest_improvement(self):
        if not self.performance_history:
            return None
        last = self.performance_history[-1]
        if last['score'] < 0.8:
            return 'Increase training, adjust hyperparameters.'
        return 'Continue current strategy.' 