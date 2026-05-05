from capacity_manager import CapacityManager
from priority_engine import PriorityEngine
from metrics import Metrics
from policy_engine import PolicyEngine
from quota_manager import QuotaManager
from escalation_engine import EscalationEngine

class ControlPlaneV3:
    def __init__(self, clusters):
        self.clusters = clusters
        self.capacity = CapacityManager()
        self.priority = PriorityEngine()
        self.metrics = Metrics()
        self.policy = PolicyEngine()
        self.quota = QuotaManager()
        self.escalation = EscalationEngine()

    def run(self, jobs):
        # compute utilization
        self.capacity.compute_utilization(self.clusters)

        # policy-based ranking
        ranked = self.policy.rank(jobs)

        # simple quota tracking
        usage_ratio_by_team = {}
        team_allocated = {}
        total_allocated = 0

        assignments = {}
        decisions = {}

        for job in ranked:
            team = job.get('team', 'Unknown')
            if not self.quota.allowed(job, usage_ratio_by_team):
                assignments[job['id']] = 'QUEUED'
                decisions[job['id']] = self.escalation.decide(job)
                continue

            assigned = False
            for c in self.clusters:
                if c.get('healthy', False) and c.get('free', 0) >= job.get('gpus', 0):
                    c['free'] -= job['gpus']
                    assignments[job['id']] = c['name']
                    decisions[job['id']] = 'Platform Auto'
                    assigned = True
                    # update usage
                    team_allocated[team] = team_allocated.get(team, 0) + job['gpus']
                    total_allocated += job['gpus']
                    usage_ratio_by_team = self.quota.update_usage(job, usage_ratio_by_team, total_allocated, team_allocated)
                    break

            if not assigned:
                assignments[job['id']] = 'QUEUED'
                decisions[job['id']] = self.escalation.decide(job)

        metrics = self.metrics.record(assignments)
        return assignments, decisions, metrics

if __name__ == '__main__':
    clusters = [
        {'name': 'A', 'capacity': 800, 'used': 760, 'free': 40, 'healthy': False},
        {'name': 'B', 'capacity': 500, 'used': 300, 'free': 200, 'healthy': True},
        {'name': 'C', 'capacity': 400, 'used': 200, 'free': 200, 'healthy': True}
    ]

    jobs = [
        {'id': 1, 'team': 'Training', 'gpus': 50, 'business_priority': 5, 'deadline_risk': 4, 'revenue_impact': 5, 'customer_impact': 3, 'fair_share_used': 0.2},
        {'id': 2, 'team': 'Inference', 'gpus': 100, 'business_priority': 4, 'deadline_risk': 3, 'revenue_impact': 5, 'customer_impact': 5, 'fair_share_used': 0.1},
        {'id': 3, 'team': 'Research', 'gpus': 20, 'business_priority': 3, 'deadline_risk': 2, 'revenue_impact': 2, 'customer_impact': 1, 'fair_share_used': 0.6}
    ]

    cp = ControlPlaneV3(clusters)
    assignments, decisions, metrics = cp.run(jobs)

    print('Assignments:', assignments)
    print('Decisions:', decisions)
    print('Metrics:', metrics)
