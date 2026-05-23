class Metrics:
    def __init__(self):
        self.processed = 0
        self.queued = 0
        self.rejected = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.fallbacks = 0

    def record_processed(self, tokens, cost):
        self.processed += 1
        self.total_tokens += tokens
        self.total_cost += cost

    def record_queued(self):
        self.queued += 1

    def record_rejected(self):
        self.rejected += 1

    def record_fallback(self):
        self.fallbacks += 1

    def summary(self, final_load):
        return {
            'processed': self.processed,
            'queued': self.queued,
            'rejected': self.rejected,
            'fallbacks': self.fallbacks,
            'total_tokens': self.total_tokens,
            'total_cost': round(self.total_cost, 4),
            'final_system_load': round(final_load, 2),
        }
