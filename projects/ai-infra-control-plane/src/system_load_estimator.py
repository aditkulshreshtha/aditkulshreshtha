class SystemLoadEstimator:
    def get_load(self, clusters):
        total = 0
        used = 0
        for c in clusters:
            total += c.get('capacity',0)
            used += c.get('used',0)
        if total == 0:
            return 0.0
        utilization = used/total
        if utilization > 0.85:
            return 0.9
        if utilization > 0.7:
            return 0.7
        return 0.5
