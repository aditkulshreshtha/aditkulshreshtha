import argparse
import json

from scheduler import Scheduler
from token_allocator import TokenAllocator
from metrics import Metrics


class CapacityManager:
    """Tracks committed GPU/cost and derives system load over time."""

    def __init__(self, base_load=0.45, gpu_budget=1.25, cost_budget=0.018, decay_rate=0.22):
        self.base_load = base_load
        self.gpu_budget = gpu_budget
        self.cost_budget = cost_budget
        self.decay_rate = decay_rate
        self.committed_gpu = 0.0
        self.committed_cost = 0.0

    def current_load(self):
        return min(self.base_load + self.committed_gpu, 1.35)

    def remaining_gpu(self):
        return max(self.gpu_budget - self.committed_gpu, 0.0)

    def remaining_cost(self):
        return max(self.cost_budget - self.committed_cost, 0.0)

    def commit(self, decision):
        self.committed_gpu += decision["gpu_load"]
        self.committed_cost += decision["cost"]

    def recover(self):
        self.committed_gpu = max(self.committed_gpu - self.decay_rate, 0.0)
        self.committed_cost = 0.0


DEFAULT_REQUESTS = [
    {
        "id": 1,
        "arrival_tick": 1,
        "deadline_tick": 2,
        "priority": "high",
        "requested_tokens": 6200,
        "minimum_tokens": 2200,
        "minimum_quality": 0.30,
    },
    {
        "id": 2,
        "arrival_tick": 1,
        "deadline_tick": 3,
        "priority": "medium",
        "requested_tokens": 3200,
        "minimum_tokens": 900,
        "minimum_quality": 0.28,
    },
    {
        "id": 3,
        "arrival_tick": 2,
        "deadline_tick": 5,
        "priority": "low",
        "requested_tokens": 1400,
        "minimum_tokens": 300,
        "minimum_quality": 0.18,
    },
    {
        "id": 4,
        "arrival_tick": 2,
        "deadline_tick": 3,
        "priority": "high",
        "requested_tokens": 7800,
        "minimum_tokens": 1800,
        "minimum_quality": 0.24,
    },
    {
        "id": 5,
        "arrival_tick": 3,
        "deadline_tick": 4,
        "priority": "low",
        "requested_tokens": 2200,
        "minimum_tokens": 400,
        "minimum_quality": 0.16,
    },
    {
        "id": 6,
        "arrival_tick": 3,
        "deadline_tick": 6,
        "priority": "medium",
        "requested_tokens": 4800,
        "minimum_tokens": 700,
        "minimum_quality": 0.20,
    },
    {
        "id": 7,
        "arrival_tick": 4,
        "deadline_tick": 5,
        "priority": "high",
        "requested_tokens": 9000,
        "minimum_tokens": 3000,
        "minimum_quality": 0.30,
    },
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the unified AI control-plane simulation."
    )
    parser.add_argument(
        "--requests-file",
        help="Optional JSON file containing a list of request objects.",
    )
    return parser.parse_args()


def load_requests(path):
    if not path:
        return DEFAULT_REQUESTS

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def reject_request(request, reason, tick, metrics):
    metrics.record_rejected(reason)
    metrics.record_unserved(request["requested_tokens"])
    print(
        f"[TICK {tick}:REJECTED] "
        f"Request={request['id']} "
        f"priority={request['priority']} "
        f"reason={reason} "
        f"requested_tokens={request['requested_tokens']} "
        f"queue_wait={tick - request.get('queued_at', tick)}"
    )


def process_request(request, tick, label, allocator, metrics, capacity):
    load = capacity.current_load()
    decision = allocator.optimize(
        request,
        load,
        capacity.remaining_gpu(),
        capacity.remaining_cost(),
    )

    metrics.record_optimization(decision)

    if not decision["accepted"]:
        metrics.record_rejected(decision["reason"])
        metrics.record_unserved(decision["requested_tokens"])
        print(
            f"[TICK {tick}:{label}:REJECTED] "
            f"Request={request['id']} "
            f"priority={request['priority']} "
            f"load={round(load, 2)} "
            f"effective_load={decision['effective_load']} "
            f"reason={decision['reason']} "
            f"requested_tokens={decision['requested_tokens']} "
            f"best_effort_tokens={decision['tokens']} "
            f"model={decision['model']} "
            f"quality={decision['quality_score']} "
            f"minimum_quality={request['minimum_quality']} "
            f"remaining_gpu={round(capacity.remaining_gpu(), 2)} "
            f"remaining_cost=${round(capacity.remaining_cost(), 4)}"
        )
        return

    capacity.commit(decision)
    metrics.record_processed(
        decision["tokens"],
        decision["cost"],
        tick - request.get("arrival_tick", tick),
        request["priority"],
    )

    if decision["action"] in {"model_optimized", "trim_and_optimize"}:
        metrics.record_fallback()

    print(
        f"[TICK {tick}:{label}] "
        f"Request={request['id']} "
        f"priority={request['priority']} "
        f"load_before={round(load, 2)} "
        f"load_after={round(capacity.current_load(), 2)} "
        f"effective_load={decision['effective_load']} "
        f"action={decision['action']} "
        f"requested_tokens={decision['requested_tokens']} "
        f"granted_tokens={decision['tokens']} "
        f"trimmed_tokens={decision['trimmed_tokens']} "
        f"trim_strategy={decision['trim_strategy']} "
        f"model={decision['model']} "
        f"quality={decision['quality_score']} "
        f"gpu_load={round(decision['gpu_load'], 2)} "
        f"cost=${round(decision['cost'], 4)} "
        f"queue_wait={tick - request.get('queued_at', tick)}"
    )


def run_simulation(requests):
    scheduler = Scheduler()
    allocator = TokenAllocator()
    metrics = Metrics()
    capacity = CapacityManager()

    print("\n=== STARTING UNIFIED AI SYSTEM SIMULATION ===\n")

    max_tick = max(request["deadline_tick"] for request in requests) + 2

    for tick in range(1, max_tick + 1):
        print(
            f"\n--- TICK {tick} "
            f"load={round(capacity.current_load(), 2)} "
            f"remaining_gpu={round(capacity.remaining_gpu(), 2)} "
            f"remaining_cost=${round(capacity.remaining_cost(), 4)} "
            f"queue={scheduler.queue_size()} ---"
        )

        metrics.update_peak_load(capacity.current_load())

        for expired in scheduler.expire(tick):
            reject_request(expired, "deadline_expired", tick, metrics)

        arrivals = [
            request for request in requests
            if request["arrival_tick"] == tick
        ]

        for request in arrivals:
            metrics.record_requested(request["requested_tokens"])

            state = scheduler.submit(request, capacity.current_load(), tick)

            if state == "rejected":
                reject_request(request, "low_priority_load_shed", tick, metrics)
                continue

            if state == "queued":
                metrics.record_queued()
                print(
                    f"[TICK {tick}:QUEUED] "
                    f"Request={request['id']} "
                    f"priority={request['priority']} "
                    f"load={round(capacity.current_load(), 2)} "
                    f"deadline={request['deadline_tick']} "
                    f"requested_tokens={request['requested_tokens']}"
                )
                continue

            process_request(request, tick, "PROCESSED", allocator, metrics, capacity)

        while True:
            drained = scheduler.drain_ready(capacity.current_load(), tick)
            if not drained:
                break

            metrics.record_drained()
            process_request(drained, tick, "DRAINED", allocator, metrics, capacity)

        capacity.recover()
        metrics.update_peak_load(capacity.current_load())

        future_arrivals = any(
            request["arrival_tick"] > tick
            for request in requests
        )
        if not future_arrivals and scheduler.queue_size() == 0:
            break

    print("\n=== FINAL METRICS ===\n")

    summary = metrics.summary(
        capacity.current_load(),
        scheduler.queue_size()
    )

    for key, value in summary.items():
        print(f"{key}: {value}")

    assert summary["token_accounting_delta"] == 0

    print("\n=== SIMULATION COMPLETE ===")


if __name__ == "__main__":
    args = parse_args()
    run_simulation(load_requests(args.requests_file))
