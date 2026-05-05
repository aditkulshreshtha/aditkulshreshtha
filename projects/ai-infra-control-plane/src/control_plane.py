class AIInfraControlPlane:
    def __init__(self, clusters):
        self.clusters = clusters

    def healthy_clusters(self):
        return [c for c in self.clusters if c.get('healthy', False)]

    def allocate(self, jobs):
        clusters = self.healthy_clusters()
        jobs = sorted(jobs, key=lambda j: j.get('priority', 0), reverse=True)
        assignments = {}

        for job in jobs:
            assigned = False
            for c in clusters:
                if c.get('free', 0) >= job.get('gpus', 0):
                    c['free'] -= job['gpus']
                    assignments[job['id']] = c['name']
                    assigned = True
                    break
            if not assigned:
                assignments[job['id']] = 'QUEUED'

        return assignments

if __name__ == '__main__':
    clusters = [
        {'name': 'A', 'free': 0, 'healthy': False},
        {'name': 'B', 'free': 200, 'healthy': True},
        {'name': 'C', 'free': 200, 'healthy': True}
    ]

    jobs = [
        {'id': 1, 'gpus': 50, 'priority': 5},
        {'id': 2, 'gpus': 100, 'priority': 4},
        {'id': 3, 'gpus': 20, 'priority': 3},
        {'id': 4, 'gpus': 80, 'priority': 2}
    ]

    cp = AIInfraControlPlane(clusters)
    print('Job assignments:')
    print(cp.allocate(jobs))
