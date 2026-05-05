class Metrics:
    def __init__(self):
        self.data = {
            'assigned': 0,
            'queued': 0,
            'total_jobs': 0
        }

    def record(self, assignments):
        self.data['total_jobs'] = len(assignments)
        self.data['assigned'] = sum(1 for v in assignments.values() if v != 'QUEUED')
        self.data['queued'] = sum(1 for v in assignments.values() if v == 'QUEUED')
        return self.data
