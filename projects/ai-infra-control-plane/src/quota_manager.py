class QuotaManager:
    """Enforces per-team share to avoid starvation and hogging."""

    def __init__(self, quotas=None):
        # quotas are percentages of total free capacity
        self.quotas = quotas or {
            'Inference': 0.30,
            'Training': 0.40,
            'Research': 0.20
        }

    def allowed(self, job, usage_ratio_by_team):
        team = job.get('team', 'Unknown')
        used_ratio = usage_ratio_by_team.get(team, 0)
        limit = self.quotas.get(team, 0.10)
        return used_ratio < limit

    def update_usage(self, job, usage_ratio_by_team, total_allocated, team_allocated):
        team = job.get('team', 'Unknown')
        if total_allocated > 0:
            usage_ratio_by_team[team] = team_allocated.get(team, 0) / total_allocated
        return usage_ratio_by_team
