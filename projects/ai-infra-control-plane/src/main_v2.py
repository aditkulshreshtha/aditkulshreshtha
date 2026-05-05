from capacity_manager import CapacityManager
from priority_engine import PriorityEngine
from metrics import Metrics

class ControlPlaneV2:
    def __init__(self, clusters):
        self.clusters = clusters
        self.capacity = CapacityManager()
        self.priority = PriorityEngine()
        self.metrics = Metrics()

    def run(self, jobs):
        self.capacity.compute_utilization(self.clusters)
        jobs = self.priority.sort(jobs)

        assignments = {}
        for job in jobs:
            assigned = False
            for c in self.clusters:
                if c.get('healthy', False) and c.get('free', 0) >= job.get('gpus', 0):
                    c['free'] -= job['gpus']
                    assignments[job['id']] = c['name']
                    assigned = True
                    break
            if not assigned:
                assignments[job['id']] = 'QUEUED'

        return assignments, self.metrics.record(assignments)

if __name__ == '__main__':
    clusters = [
        {'name': 'A', 'capacity': 800, 'used': 760, 'free': 40, 'healthy': False},
        {'name': 'B', 'capacity': 500, 'used': 300, 'free': 200, 'healthy': True},
        {'name': 'C', 'capacity': 400, 'used': 200, 'free': 200, 'healthy': True}
    ]

    jobs = [
        {'id': 1, 'gpus': 50, 'priority': 5},
        {'id': 2, 'gpus': 100, 'priority': 4},
        {'id': 3, 'gpus': 20, 'priority': 3},
        {'id': 4, 'gpus': 80, 'priority': 2}
    ]

    cp = ControlPlaneV2(clusters)
    assignments, metrics = cp.run(jobs)

    print('Assignments:', assignments)
    print('Metrics:', metrics)
