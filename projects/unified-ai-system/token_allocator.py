class TokenAllocator:
    """Optimizes token budgets and model choice under infrastructure pressure."""

    BASE_BUDGETS = {
        "high": 3000,
        "medium": 1500,
        "low": 600,
    }

    MINIMUM_BUDGETS = {
        "high": 1800,
        "medium": 800,
        "low": 250,
    }

    MODEL_PROFILES = {
        "cheap": {
            "cost_multiplier": 0.5,
            "gpu_multiplier": 0.45,
            "max_tokens": 2000,
            "quality": 0.65,
        },
        "balanced": {
            "cost_multiplier": 1.0,
            "gpu_multiplier": 1.0,
            "max_tokens": 4000,
            "quality": 0.82,
        },
        "premium": {
            "cost_multiplier": 2.0,
            "gpu_multiplier": 1.8,
            "max_tokens": 8000,
            "quality": 0.95,
        },
    }

    PRIORITY_SETTINGS = {
        "high": {
            "reserved_capacity": 0.20,
            "quality_weight": 0.65,
            "coverage_weight": 0.30,
            "cost_weight": 0.05,
            "baseline_model": "premium",
        },
        "medium": {
            "reserved_capacity": 0.08,
            "quality_weight": 0.45,
            "coverage_weight": 0.40,
            "cost_weight": 0.15,
            "baseline_model": "balanced",
        },
        "low": {
            "reserved_capacity": 0.0,
            "quality_weight": 0.20,
            "coverage_weight": 0.45,
            "cost_weight": 0.35,
            "baseline_model": "cheap",
        },
    }

    MAX_SAFE_LOAD = 1.10

    def effective_load(self, priority: str, system_load: float) -> float:
        settings = self.PRIORITY_SETTINGS.get(priority, self.PRIORITY_SETTINGS["medium"])
        return max(system_load - settings["reserved_capacity"], 0.0)

    def pressure_multiplier(self, effective_load: float) -> float:
        if effective_load <= 0.70:
            return 1.0

        pressure = min(max((effective_load - 0.70) / 0.40, 0.0), 1.0)
        return round(1.0 - (pressure * 0.55), 2)

    def estimate_cost(self, tokens: int, model: str) -> float:
        profile = self.MODEL_PROFILES.get(model, self.MODEL_PROFILES["balanced"])
        return (tokens / 1000.0) * 0.002 * profile["cost_multiplier"]

    def estimate_gpu_load(self, tokens: int, model: str) -> float:
        profile = self.MODEL_PROFILES.get(model, self.MODEL_PROFILES["balanced"])
        return (tokens * profile["gpu_multiplier"]) / 5000.0

    def score_option(self, priority: str, requested_tokens: int, tokens: int, profile) -> float:
        settings = self.PRIORITY_SETTINGS.get(priority, self.PRIORITY_SETTINGS["medium"])
        coverage = min(tokens / requested_tokens, 1.0)
        cost_efficiency = 1.0 / profile["cost_multiplier"]

        return (
            profile["quality"] * settings["quality_weight"]
            + coverage * settings["coverage_weight"]
            + cost_efficiency * settings["cost_weight"]
        )

    def trim_strategy(self, priority: str, trimmed_tokens: int) -> str:
        if trimmed_tokens <= 0:
            return "none"
        if priority == "high":
            return "summarize_low_relevance"
        if priority == "medium":
            return "drop_oldest_then_summarize"
        return "drop_oldest"

    def optimize(self, request, system_load: float, remaining_gpu: float, remaining_cost: float):
        priority = request["priority"]
        requested_tokens = request.get("requested_tokens", self.BASE_BUDGETS.get(priority, 1000))
        minimum_tokens = request.get("minimum_tokens", self.MINIMUM_BUDGETS.get(priority, 500))
        minimum_quality = request.get("minimum_quality", 0.0)
        settings = self.PRIORITY_SETTINGS.get(priority, self.PRIORITY_SETTINGS["medium"])

        effective_load = self.effective_load(priority, system_load)
        pressure_multiplier = self.pressure_multiplier(effective_load)
        base_budget = self.BASE_BUDGETS.get(priority, 1000)
        safe_budget = int(base_budget * pressure_multiplier)

        if effective_load >= self.MAX_SAFE_LOAD:
            return {
                "accepted": False,
                "action": "reject_system_overload",
                "reason": "system_overload",
                "requested_tokens": requested_tokens,
                "tokens": 0,
                "trimmed_tokens": requested_tokens,
                "model": None,
                "quality_score": 0.0,
                "cost": 0.0,
                "gpu_load": 0.0,
                "effective_load": round(effective_load, 2),
                "trim_strategy": "none",
            }

        options = []

        for model, profile in self.MODEL_PROFILES.items():
            model_gpu_relief = 1.0 / profile["gpu_multiplier"]
            model_budget = int(safe_budget * model_gpu_relief)
            tokens = min(requested_tokens, model_budget, profile["max_tokens"])
            gpu_load = self.estimate_gpu_load(tokens, model)
            cost = self.estimate_cost(tokens, model)

            if tokens <= 0 or gpu_load > remaining_gpu or cost > remaining_cost:
                continue

            options.append({
                "model": model,
                "tokens": tokens,
                "score": self.score_option(priority, requested_tokens, tokens, profile),
                "profile": profile,
                "cost": cost,
                "gpu_load": gpu_load,
            })

        if not options:
            return {
                "accepted": False,
                "action": "reject_no_capacity",
                "reason": "no_model_capacity",
                "requested_tokens": requested_tokens,
                "tokens": 0,
                "trimmed_tokens": requested_tokens,
                "model": None,
                "quality_score": 0.0,
                "cost": 0.0,
                "gpu_load": 0.0,
                "effective_load": round(effective_load, 2),
                "trim_strategy": "none",
            }

        feasible_options = [
            option for option in options
            if option["tokens"] >= minimum_tokens
        ]

        if not feasible_options:
            best_effort = max(options, key=lambda option: option["tokens"])
            return {
                "accepted": False,
                "action": "reject_below_minimum_tokens",
                "reason": "below_minimum_tokens",
                "requested_tokens": requested_tokens,
                "tokens": best_effort["tokens"],
                "trimmed_tokens": requested_tokens - best_effort["tokens"],
                "model": best_effort["model"],
                "quality_score": 0.0,
                "cost": 0.0,
                "gpu_load": self.estimate_gpu_load(best_effort["tokens"], best_effort["model"]),
                "effective_load": round(effective_load, 2),
                "trim_strategy": self.trim_strategy(priority, requested_tokens - best_effort["tokens"]),
            }

        quality_feasible_options = []
        for option in feasible_options:
            quality_score = option["profile"]["quality"] * min(option["tokens"] / requested_tokens, 1.0)
            if quality_score >= minimum_quality:
                quality_feasible_options.append(option)

        if not quality_feasible_options:
            best_effort = max(feasible_options, key=lambda option: option["score"])
            quality_score = best_effort["profile"]["quality"] * min(best_effort["tokens"] / requested_tokens, 1.0)

            return {
                "accepted": False,
                "action": "reject_below_quality_threshold",
                "reason": "below_quality_threshold",
                "requested_tokens": requested_tokens,
                "tokens": best_effort["tokens"],
                "trimmed_tokens": requested_tokens - best_effort["tokens"],
                "model": best_effort["model"],
                "quality_score": round(min(quality_score, best_effort["profile"]["quality"]), 2),
                "cost": 0.0,
                "gpu_load": best_effort["gpu_load"],
                "effective_load": round(effective_load, 2),
                "trim_strategy": self.trim_strategy(priority, requested_tokens - best_effort["tokens"]),
            }

        best = max(quality_feasible_options, key=lambda option: option["score"])

        action = "full"
        if best["tokens"] < requested_tokens:
            action = "trim_context"
        if best["model"] != settings["baseline_model"]:
            action = "model_optimized" if action == "full" else "trim_and_optimize"

        quality_score = best["profile"]["quality"] * min(best["tokens"] / requested_tokens, 1.0)

        return {
            "accepted": True,
            "action": action,
            "reason": "accepted",
            "requested_tokens": requested_tokens,
            "tokens": best["tokens"],
            "trimmed_tokens": requested_tokens - best["tokens"],
            "model": best["model"],
            "quality_score": round(min(quality_score, best["profile"]["quality"]), 2),
            "cost": best["cost"],
            "gpu_load": best["gpu_load"],
            "effective_load": round(effective_load, 2),
            "trim_strategy": self.trim_strategy(priority, requested_tokens - best["tokens"]),
        }
