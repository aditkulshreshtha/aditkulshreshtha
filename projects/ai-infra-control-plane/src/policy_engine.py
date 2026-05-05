class PolicyEngine:
    """Scores workloads using business and operational signals."""

    def score(self, job):
        return (
            job.get('business_priority', 0) * 0.30 +
            job.get('deadline_risk', 0) * 0.25 +
            job.get('revenue_impact', 0) * 0.25 +
            job.get('customer_impact', 0) * 0.15 -
            job.get('fair_share_used', 0) * 0.05
        )

    def rank(self, jobs):
        enriched = []
        for job in jobs:
            job = dict(job)
            job['policy_score'] = round(self.score(job), 2)
            enriched.append(job)
        return sorted(enriched, key=lambda j: j['policy_score'], reverse=True)
