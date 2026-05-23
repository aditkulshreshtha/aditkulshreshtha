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

system_load = 0.65

print("\n=== STARTING UNIFIED AI SYSTEM SIMULATION ===\n")

# INITIAL REQUEST PROCESSING
for request in requests:

    system_load += 0.08
    metrics.update_peak_load(system_load)

    state = scheduler.submit(request, system_load)

    if state == "rejected":
        metrics.record_rejected()

        print(
            f"[REJECTED] "
            f"Request={request['id']} "
            f"priority={request['priority']} "
            f"load={round(system_load, 2)}"
        )

        continue

    if state == "queued":
        metrics.record_queued()

        print(
            f"[QUEUED] "
            f"Request={request['id']} "
            f"priority={request['priority']} "
            f"load={round(system_load, 2)}"
        )

        continue

    tokens = allocator.allocate(
        request["priority"],
        system_load
    )

    normal_model = allocator.choose_model(
        request["priority"],
        0.0
    )

    model = allocator.choose_model(
        request["priority"],
        system_load
    )

    if system_load >= 0.90 and model == "cheap" and normal_model != "cheap":
        metrics.record_fallback()

    cost = allocator.estimate_cost(tokens, model)

    gpu_load = allocator.estimate_gpu_load(tokens, model)

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

# RECOVERY PHASE
print("\n=== RECOVERY / QUEUE DRAIN PHASE ===\n")

while scheduler.queue:

    # simulate recovery
    system_load -= 0.12

    if system_load < 0.50:
        system_load = 0.50
    metrics.update_peak_load(system_load)

    request = scheduler.queue.pop(0)

    metrics.record_drained()

    tokens = allocator.allocate(
        request["priority"],
        system_load
    )

    normal_model = allocator.choose_model(
        request["priority"],
        0.0
    )

    model = allocator.choose_model(
        request["priority"],
        system_load
    )

    if system_load >= 0.90 and model == "cheap" and normal_model != "cheap":
        metrics.record_fallback()

    cost = allocator.estimate_cost(tokens, model)

    metrics.record_processed(tokens, cost)

    print(
        f"[DRAINED] "
        f"Request={request['id']} "
        f"priority={request['priority']} "
        f"load={round(system_load, 2)} "
        f"tokens={tokens} "
        f"model={model} "
        f"cost=${round(cost, 4)}"
    )

print("\n=== FINAL METRICS ===\n")

summary = metrics.summary(
    system_load,
    scheduler.queue_size()
)

for key, value in summary.items():
    print(f"{key}: {value}")

print("\n=== SIMULATION COMPLETE ===")
