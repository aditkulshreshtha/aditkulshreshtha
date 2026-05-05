from intent_classifier import IntentClassifier
from value_estimator import ValueEstimator
from adaptive_budget_allocator import AdaptiveBudgetAllocator
from context_optimizer_v3 import ContextOptimizer
from model_selector import ModelSelector
from feedback_loop import FeedbackLoop


def run(request, history, system_load=0.5):
    intent = IntentClassifier().classify(request)
    value = ValueEstimator().estimate(request)

    budget = AdaptiveBudgetAllocator().allocate(intent, value, system_load)

    context = ContextOptimizer().optimize(history, budget)

    model = ModelSelector().choose(intent, budget)

    tokens_used = min(len(context), budget)

    feedback = FeedbackLoop().update(tokens_used, success_score=0.8)

    return {
        'intent':intent,
        'budget':budget,
        'model':model,
        'tokens_used':tokens_used,
        'feedback':feedback
    }


if __name__ == '__main__':
    request = {
        'text':'design a scalable system',
        'revenue_impact':5,
        'user_tier_weight':3,
        'deadline_urgency':4
    }

    history = list(range(2000))

    print(run(request, history))
