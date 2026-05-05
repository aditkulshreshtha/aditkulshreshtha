import random

class TokenBudget:
    def allowed(self, tokens, max_tokens):
        return tokens <= max_tokens

class ContextOptimizer:
    def trim(self, history, limit=1000):
        return history[-limit:]

class CostController:
    def estimate(self, tokens, price_per_1k=0.002):
        return (tokens/1000)*price_per_1k

class ExperimentRouter:
    def allow(self, pct=0.1):
        return random.random() < pct

class Cache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value

if __name__ == '__main__':
    budget = TokenBudget()
    context = ContextOptimizer()
    cost = CostController()
    router = ExperimentRouter()
    cache = Cache()

    request_tokens = 1200
    max_tokens = 1000

    if not budget.allowed(request_tokens, max_tokens):
        print('Rejected: token budget exceeded')
    else:
        print('Allowed')

    print('Estimated cost:', cost.estimate(request_tokens))
