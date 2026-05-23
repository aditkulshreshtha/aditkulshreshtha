class Metrics:
    def __init__(self):
        self.processed = 0
        self.queued = 0
        self.drained = 0
        self.rejected = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.fallbacks = 0
        self.peak_load = 0.0

    def update_peak_load(self, load):
        self.peak_load = max(self.peak_load, load)

    def record_processed(self, tokens, cost):
        self.processed += 1
        self.total_tokens += tokens
        self.total_cost += cost

    def record_queued(self):
        self.queued += 1

    def record_drained(self):
        self.drained += 1

    def record_rejected(self):
        self.rejected += 1

    def record_fallback(self):
        self.fallbacks += 1

    def summary(self, final_load, remaining_queue):
        return {
            "processed": self.processed,
            "queued_initial": self.queued,
            "drained": self.drained,
            "remaining_queue": remaining_queue,
            "rejected": self.rejected,
            "fallbacks": self.fallbacks,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "peak_system_load": round(self.peak_load, 2),
            "final_system_load": round(final_load, 2),
        }
