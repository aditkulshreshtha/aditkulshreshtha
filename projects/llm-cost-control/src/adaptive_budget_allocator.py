class AdaptiveBudgetAllocator:
    def __init__(self):
        self.base = {
            'critical':4000,
            'deep_reasoning':3000,
            'default':1500,
            'low_cost':500
        }

    def allocate(self, intent, value_score, system_load):
        base = self.base.get(intent,1000)
        scaled = base * (1 + value_score/10)
        if system_load > 0.8:
            scaled *= 0.7
        return int(min(scaled,8000))
