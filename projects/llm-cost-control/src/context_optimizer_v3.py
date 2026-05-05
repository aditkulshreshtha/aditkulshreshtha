class ContextOptimizer:
    def optimize(self, history, max_tokens):
        if len(history) > max_tokens:
            return history[-500:]
        return history
