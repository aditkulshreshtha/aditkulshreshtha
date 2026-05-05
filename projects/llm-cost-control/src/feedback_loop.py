class FeedbackLoop:
    def update(self, tokens_used, success_score):
        return {
            'tokens_used':tokens_used,
            'success':success_score,
            'needs_adjustment': success_score < 0.7
        }
