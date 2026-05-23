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
    {"id": 6, "priority": "medium"},
    {"id": 7, "priority": "high"},
]

# starting system pressure
system_load = 0.65

print("\n=== STARTING UNIFIED AI SYSTEM SIMULATION ===\n")

for request in requests:

    # simulate increasing pressure/load
    system_load += 0.08

    state = scheduler.submit(request, system_load)

    # rejection handling
    if state == "rejected":
        metrics.record_rejected()

        print(
            f"[REJECTED] "
            f"Request={request['id']} "
            f"priority={request['priority']} "
            f"load={round(system_load, 2)}"
        )

        continue

    # queue handling
    if state == "queued":
        metrics.record_queued()

        print(
            f"[QUEUED] "
            f"Request={request['id']} "
            f"priority={request['priority']} "
            f"load={round(system_load, 2)}"
        )

        continue

    # allocate token budget
    tokens = allocator.allocate(
        request["priority"],
        system_load
    )

    # choose model tier
    model = allocator.choose_model(
        request["priority"],
        system_load
    )

    # fallback behavior during overload
    if system_load > 0.90:
        model = "cheap"
        metrics.record_fallback()

    # estimate operational cost
    cost = allocator.estimate_cost(tokens, model)

    # estimate gpu impact
    gpu_load = allocator.estimate_gpu_load(tokens, model)

    # update metrics
    metrics.record_processed(tokens, cost)

    print(
        f"[PROCESSED] "
        f"Request={request['id']} "
        f"priority={request['priority']} "
        f"load={round(system_load, 2)} "
        f"tokens={tokens} "
        f"model={model} "
        f"gpu_load={round(gpu_load, 2)} "
        f"cost=${round(cost, 4)}"
    )

print("\n=== FINAL METRICS ===\n")

summary = metrics.summary(system_load)

for key, value in summary.items():
    print(f"{key}: {value}")

print("\n=== SIMULATION COMPLETE ===")
