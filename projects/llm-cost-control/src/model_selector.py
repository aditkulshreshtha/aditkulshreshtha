class ModelSelector:
    def choose(self, intent, budget):
        if intent == 'low_cost':
            return 'cheap-model'
        if budget > 3000:
            return 'high-quality-model'
        return 'balanced-model'
