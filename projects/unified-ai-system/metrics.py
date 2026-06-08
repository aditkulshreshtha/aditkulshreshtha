class Metrics:
    def __init__(self):
        self.processed = 0
        self.queued = 0
        self.drained = 0
        self.rejected = 0
        self.granted_tokens = 0
        self.requested_tokens = 0
        self.trimmed_tokens = 0
        self.unserved_tokens = 0
        self.total_cost = 0.0
        self.fallbacks = 0
        self.model_optimizations = 0
        self.rejection_reasons = {}
        self.latency_by_priority = {}
        self.processed_by_priority = {}
        self.peak_load = 0.0

    def update_peak_load(self, load):
        self.peak_load = max(self.peak_load, load)

    def record_processed(self, tokens, cost, latency_ticks=0, priority="unknown"):
        self.processed += 1
        self.granted_tokens += tokens
        self.total_cost += cost
        self.latency_by_priority.setdefault(priority, []).append(latency_ticks)
        self.processed_by_priority[priority] = self.processed_by_priority.get(priority, 0) + 1

    def record_requested(self, tokens):
        self.requested_tokens += tokens

    def record_trimmed(self, tokens):
        self.trimmed_tokens += tokens

    def record_optimization(self, decision):
        if decision["accepted"]:
            self.record_trimmed(decision["trimmed_tokens"])

        if decision["action"] in {"model_optimized", "trim_and_optimize"}:
            self.model_optimizations += 1

    def record_queued(self):
        self.queued += 1

    def record_drained(self):
        self.drained += 1

    def record_rejected(self, reason=None):
        self.rejected += 1
        if reason:
            self.rejection_reasons[reason] = self.rejection_reasons.get(reason, 0) + 1

    def record_unserved(self, tokens):
        self.unserved_tokens += tokens

    def record_fallback(self):
        self.fallbacks += 1

    def summary(self, final_load, remaining_queue):
        latency_by_priority = {}
        for priority, latencies in self.latency_by_priority.items():
            if not latencies:
                continue

            sorted_latencies = sorted(latencies)
            latency_by_priority[priority] = {
                "avg": round(sum(sorted_latencies) / len(sorted_latencies), 2),
                "p95": self.percentile(sorted_latencies, 95),
                "p99": self.percentile(sorted_latencies, 99),
                "max": sorted_latencies[-1],
            }

        token_accounting_delta = (
            self.requested_tokens
            - self.granted_tokens
            - self.trimmed_tokens
            - self.unserved_tokens
        )

        return {
            "processed": self.processed,
            "processed_by_priority": self.processed_by_priority,
            "queued_initial": self.queued,
            "drained": self.drained,
            "remaining_queue": remaining_queue,
            "rejected": self.rejected,
            "fallbacks": self.fallbacks,
            "model_optimizations": self.model_optimizations,
            "rejection_reasons": self.rejection_reasons,
            "requested_tokens": self.requested_tokens,
            "granted_tokens": self.granted_tokens,
            "trimmed_tokens": self.trimmed_tokens,
            "unserved_tokens": self.unserved_tokens,
            "token_accounting_delta": token_accounting_delta,
            "total_cost": round(self.total_cost, 4),
            "latency_ticks_by_priority": latency_by_priority,
            "peak_system_load": round(self.peak_load, 2),
            "final_system_load": round(final_load, 2),
        }

    def percentile(self, sorted_values, percentile):
        if not sorted_values:
            return None

        index = int(round((percentile / 100) * (len(sorted_values) - 1)))
        return sorted_values[index]
