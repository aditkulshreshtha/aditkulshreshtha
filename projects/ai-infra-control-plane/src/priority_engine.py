class PriorityEngine:
    def sort(self, jobs):
        return sorted(jobs, key=lambda j: j.get('priority', 0), reverse=True)
