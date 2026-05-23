class TokenAllocator:
    """Allocates token budgets based on request priority and system load."""

    BASE_BUDGETS = {
        "high": 3000,
        "medium": 1500,
        "low": 600,
    }

    MODEL_COST_MULTIPLIER = {
        "cheap": 0.5,
        "balanced": 1.0,
        "premium": 2.0,
    }

    def allocate(self, priority: str, system_load: float) -> int:
        budget = self.BASE_BUDGETS.get(priority, 1000)

        if system_load >= 0.90:
            budget = int(budget * 0.50)
        elif system_load >= 0.75:
            budget = int(budget * 0.75)

        return max(budget, 200)

    def choose_model(self, priority: str, system_load: float) -> str:
        if system_load >= 0.90:
            return "cheap"
        if priority == "high":
            return "premium"
        if priority == "medium":
            return "balanced"
        return "cheap"

    def estimate_cost(self, tokens: int, model: str) -> float:
        multiplier = self.MODEL_COST_MULTIPLIER.get(model, 1.0)
        return (tokens / 1000.0) * 0.002 * multiplier

    def estimate_gpu_load(self, tokens: int, model: str) -> float:
        multiplier = self.MODEL_COST_MULTIPLIER.get(model, 1.0)
        return (tokens * multiplier) / 5000.0
