class ValueEstimator:
    def estimate(self, request):
        return (
            request.get('revenue_impact',1)*0.4 +
            request.get('user_tier_weight',1)*0.3 +
            request.get('deadline_urgency',1)*0.3
        )
