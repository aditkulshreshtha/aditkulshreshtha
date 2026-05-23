from scheduler import Scheduler
from token_allocator import TokenAllocator
from metrics import Metrics

scheduler = Scheduler()
allocator = TokenAllocator()
metrics = Metrics()

requests = [
    {"id": 1, "priority": "high"},
    {"id": 2, "priority": "medium"},
    {"id": 3, "priority": "low"},
    {"id": 4, "priority": "high"},
    {"id": 5, "priority": "low"},
]

system_load = 0.65

for request in requests:

    # simulate increasing load
    system_load += 0.08

    state = scheduler.submit(request, system_load)

    if state == "rejected":
        metrics.record_rejected()

        print(
            f"[REJECTED] Request {request['id']} "
            f"priority={request['priority']}"
        )
        continue

    if state == "queued":
        metrics.record_queued()

    tokens = allocator.allocate(
        request["priority"],
        system_load
    )

    model = allocator.choose_model(
        request["priority"],
        system_load
    )

    cost = allocator.estimate_cost(tokens, model)

    # fallback logic under extreme pressure
    if system_load > 0.90:
        model = "cheap"
        metrics.record_fallback()

    metrics.record_processed(tokens, cost)

    print(
        f"[{state.upper()}] "
        f"Request={request['id']} "
        f"priority={request['priority']} "
        f"load={round(system_load, 2)} "
        f"tokens={tokens} "
        f"model={model} "
        f"cost=${round(cost, 4)}"
    )

print("\n=== FINAL METRICS ===")

summary = metrics.summary(system_load)

for k, v in summary.items():
    print(f"{k}: {v}")
