class SystemState:
    def __init__(self, daily_limit=10.0):
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.request_history = []
        self.team_usage = {}
        self.daily_limit = daily_limit

    def can_spend(self, cost):
        return (self.total_cost + cost) <= self.daily_limit

    def update(self, tokens, cost, team):
        self.total_tokens_used += tokens
        self.total_cost += cost
        self.team_usage[team] = self.team_usage.get(team, 0) + tokens
        self.request_history.append({
            'tokens': tokens,
            'cost': cost,
            'team': team
        })
