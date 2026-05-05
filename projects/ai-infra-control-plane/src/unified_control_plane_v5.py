from system_load_estimator import SystemLoadEstimator

# import token system
import sys
sys.path.append('../../llm-cost-control/src')

from adaptive_token_system_v4 import run as token_run

class UnifiedControlPlane:
    def __init__(self, clusters):
        self.clusters = clusters
        self.load_estimator = SystemLoadEstimator()

    def run(self, request, history):
        # step 1: get system load from GPU infra
        system_load = self.load_estimator.get_load(self.clusters)

        # step 2: run token allocation with load awareness
        token_result = token_run(request, history, system_load=system_load)

        # step 3: simulate GPU allocation impact
        tokens_used = token_result.get('tokens_used',0)

        # assume tokens map to GPU load (simplified)
        added_load = tokens_used / 10000.0

        for c in self.clusters:
            if c.get('healthy',True):
                c['used'] += int(added_load * c.get('capacity',0) * 0.5)

        return {
            'system_load': system_load,
            'token_result': token_result,
            'updated_clusters': self.clusters
        }

if __name__ == '__main__':
    clusters = [
        {'name':'A','capacity':800,'used':760,'healthy':False},
        {'name':'B','capacity':500,'used':300,'healthy':True},
        {'name':'C','capacity':400,'used':200,'healthy':True}
    ]

    cp = UnifiedControlPlane(clusters)

    request = {
        'text':'design scalable architecture',
        'revenue_impact':5,
        'user_tier_weight':3,
        'deadline_urgency':4,
        'team':'infra'
    }

    history = list(range(2000))

    print(cp.run(request, history))
