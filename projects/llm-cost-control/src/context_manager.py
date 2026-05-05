class ContextManager:
    def build_context(self, history, max_tokens):
        if len(history) <= max_tokens:
            return history

        # tiered compression
        recent = history[-300:]
        older = history[-1000:-300]

        # simulate summarization by trimming
        summary = older[:200]

        return summary + recent
