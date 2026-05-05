from intent_classifier import IntentClassifier
from value_estimator import ValueEstimator
from adaptive_budget_allocator import AdaptiveBudgetAllocator
from context_manager import ContextManager
from model_selector import ModelSelector
from feedback_loop_v2 import FeedbackLoop
from cost_controller_v2 import CostController
from system_state import SystemState

state = SystemState(daily_limit=10.0)

def run(request, history, system_load=0.5):
    intent = IntentClassifier().classify(request['text'])
    value = ValueEstimator().estimate(request)

    budget = AdaptiveBudgetAllocator().allocate(intent, value, system_load)

    context = ContextManager().build_context(history, budget)

    tokens_used = min(len(context), budget)

    cost = CostController().compute(tokens_used)

    if not state.can_spend(cost):
        return {'error': 'Budget exceeded', 'total_cost': state.total_cost}

    state.update(tokens_used, cost, request.get('team','default'))

    adjusted_budget = FeedbackLoop().adjust_budget(0.8, budget)

    return {
        'intent': intent,
        'budget': budget,
        'adjusted_budget': adjusted_budget,
        'tokens_used': tokens_used,
        'cost': cost,
        'total_cost': state.total_cost
    }

if __name__ == '__main__':
    request = {
        'text': 'design scalable architecture',
        'revenue_impact': 5,
        'user_tier_weight': 3,
        'deadline_urgency': 4,
        'team': 'infra'
    }

    history = list(range(2000))

    print(run(request, history))
