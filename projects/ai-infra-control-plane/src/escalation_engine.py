class EscalationEngine:
    """Determines who has final say under contention."""

    def decide(self, job):
        if job.get('revenue_impact', 0) >= 5 and job.get('deadline_risk', 0) >= 5:
            return 'Capacity Council'
        if job.get('business_priority', 0) >= 4:
            return 'Platform Auto'
        return 'Queue'
