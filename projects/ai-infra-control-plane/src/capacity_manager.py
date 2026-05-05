class CapacityManager:
    def compute_utilization(self, clusters):
        for c in clusters:
            cap = c.get('capacity', 0) or 1
            c['utilization'] = c.get('used', 0) / cap
        return clusters

    def classify(self, clusters):
        hot = [c for c in clusters if c.get('utilization', 0) > 0.85]
        cool = [c for c in clusters if c.get('utilization', 0) < 0.60]
        return hot, cool

    def rebalance(self, clusters, max_move=50):
        self.compute_utilization(clusters)
        hot, cool = self.classify(clusters)
        for h in hot:
            for c in cool:
                movable = min(max_move, max(0, h.get('used', 0) - int(h.get('capacity', 0) * 0.80)))
                if movable > 0 and c.get('used', 0) + movable <= c.get('capacity', 0):
                    h['used'] -= movable
                    c['used'] += movable
        return clusters
