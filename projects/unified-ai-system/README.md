# Unified AI System

A runnable simulation that combines AI infrastructure load, token allocation, queueing, fallback behavior, and cost control.

## Problem
AI systems become expensive and unreliable when token usage, context size, GPU load, and request priority are managed independently.

Token maxing is especially dangerous because every request can look valid in isolation while the aggregate system runs out of context window, GPU headroom, or cost budget. A production control plane needs to decide whether to serve the full request, trim context, switch models, queue work, or reject work before it degrades the entire system.

## Solution
This project simulates a unified control layer that:

- accepts incoming requests with requested and minimum useful token budgets
- simulates request arrival over time with tick-based load and recovery
- reserves capacity for high-priority requests before calculating pressure
- applies a smooth pressure curve instead of abrupt load tiers
- jointly optimizes model selection and token budget based on load, priority, cost, quality, and GPU pressure
- commits granted GPU and cost back into the next control-loop decision
- retries queued work when load recovers and expires it when deadlines pass
- rejects work with specific reasons when token demand, quality, cost, GPU budget, or SLA constraints cannot be met
- reports cost, requested tokens, granted tokens, trimmed tokens, unserved tokens, queue size, model optimizations, rejections, latency, and final GPU load

## Run

```bash
python main.py
```

Optionally run with a custom request workload:

```bash
python main.py --requests-file requests.json
```

## Expected output

The simulation prints tick-by-tick decisions plus total cost, requested tokens, granted tokens, trimmed tokens, unserved tokens, processed requests, rejections, queue size, model optimizations, latency percentiles, and final GPU load.

## Control-plane logic

```text
Request arrivals
      |
      v
Scheduler -----> Queue -----> Retry / expire by deadline
      |             ^
      v             |
TokenAllocator -----+
      |
      v
CapacityManager ---> next tick load
      |
      v
Metrics
```

Each request includes:

- `priority`: high, medium, or low
- `requested_tokens`: the full context the caller wants
- `minimum_tokens`: the smallest useful context budget for the task
- `minimum_quality`: the lowest acceptable estimated answer quality
- `arrival_tick`: when the request enters the system
- `deadline_tick`: when queued work expires

The capacity manager tracks committed GPU and per-tick cost. When a request is served, its granted tokens and selected model add GPU load. Each tick recovers `0.22` GPU-load units and resets the per-tick cost budget. This closes the feedback loop: allocator decisions change the future load that the allocator reads.

Metrics keep served-token trimming separate from rejected-token demand. `trimmed_tokens` means the request was accepted with reduced context. `unserved_tokens` means the request was rejected, expired, or otherwise not served. Latency is reported by priority with average, p95, p99, and max tick delay.

The simulation validates token conservation at the end of each run:

```text
requested_tokens = granted_tokens + trimmed_tokens + unserved_tokens
```

Queue draining is capacity-aware. The scheduler returns one ready request at a time, then the main control loop re-checks load before draining another request. This avoids draining a batch based on stale pre-commit capacity.

The optimizer first converts raw system load into priority-adjusted effective load. High-priority work receives reserved headroom, so critical requests degrade later than best-effort traffic.

It then uses a continuous pressure curve. As effective load rises above the safe range, the available token budget shrinks smoothly instead of dropping at hard thresholds.

The optimizer evaluates model and token choices together:

- `premium`: highest quality, highest cost and GPU pressure
- `balanced`: middle path for protected work under pressure
- `cheap`: lowest cost fallback for noncritical or degraded workloads

For each model, the system estimates how many tokens can be safely granted under current GPU pressure and remaining cost budget. It then scores options by quality, token coverage, and cost efficiency. This allows the control plane to choose a cheaper model with more context when that is better than using a premium model with severe context trimming.

If no model can meet the request's minimum useful token budget, the request is rejected as `below_minimum_tokens`. If the estimated answer quality is too low, it is rejected as `below_quality_threshold`. If effective system load is too high, it is rejected as `system_overload`. If low-priority work is dropped before optimization to protect the system, it is reported as `low_priority_load_shed`. If queued work misses its deadline, it is reported as `deadline_expired`.

Accepted requests also report a `trim_strategy`. High-priority requests preserve answer quality by summarizing low-relevance context instead of blindly dropping history. Medium-priority requests first drop stale context and then summarize because the quality bar is lower but still meaningful. Low-priority requests use the cheapest strategy and drop the oldest context.

- `summarize_low_relevance` for high-priority requests
- `drop_oldest_then_summarize` for medium-priority requests
- `drop_oldest` for low-priority requests

## Sample output

```text
--- TICK 1 load=0.45 remaining_gpu=1.25 remaining_cost=$0.018 queue=0 ---
[TICK 1:PROCESSED] Request=1 priority=high load_before=0.45 load_after=1.05 action=trim_and_optimize granted_tokens=3000 trim_strategy=summarize_low_relevance model=balanced queue_wait=0
[TICK 1:QUEUED] Request=2 priority=medium load=1.05 deadline=3 requested_tokens=3200

--- TICK 2 load=0.83 remaining_gpu=0.87 remaining_cost=$0.018 queue=1 ---
[TICK 2:QUEUED] Request=3 priority=low load=0.83 deadline=5 requested_tokens=1400
[TICK 2:PROCESSED] Request=4 priority=high load_before=0.83 load_after=1.35 action=trim_and_optimize granted_tokens=3000 trim_strategy=summarize_low_relevance model=balanced queue_wait=0

--- TICK 3 load=1.21 remaining_gpu=0.49 remaining_cost=$0.018 queue=2 ---
[TICK 3:REJECTED] Request=5 priority=low reason=low_priority_load_shed requested_tokens=2200 queue_wait=0
[TICK 3:QUEUED] Request=6 priority=medium load=1.21 deadline=6 requested_tokens=4800

--- TICK 4 load=0.99 remaining_gpu=0.71 remaining_cost=$0.018 queue=3 ---
[TICK 4:REJECTED] Request=2 priority=medium reason=deadline_expired requested_tokens=3200 queue_wait=3
[TICK 4:PROCESSED:REJECTED] Request=7 priority=high reason=below_minimum_tokens requested_tokens=9000 best_effort_tokens=2640 model=balanced

--- TICK 5 load=0.77 remaining_gpu=0.93 remaining_cost=$0.018 queue=2 ---
[TICK 5:DRAINED] Request=6 priority=medium load_before=0.77 load_after=0.95 action=trim_and_optimize granted_tokens=2000 model=cheap queue_wait=2

processed: 3
processed_by_priority: {'high': 2, 'medium': 1}
rejection_reasons: {'low_priority_load_shed': 1, 'deadline_expired': 2, 'below_minimum_tokens': 1}
requested_tokens: 34600
granted_tokens: 8000
trimmed_tokens: 10800
unserved_tokens: 15800
token_accounting_delta: 0
latency_ticks_by_priority: {'high': {'avg': 0.0, 'p95': 0, 'p99': 0, 'max': 0}, 'medium': {'avg': 2.0, 'p95': 2, 'p99': 2, 'max': 2}}
peak_system_load: 1.21
final_system_load: 0.51
```

## Tradeoffs

| Decision | Benefit | Risk | This project's stance |
|---|---|---|---|
| Reserve capacity for critical work | Protects high-priority requests | Lower-priority users may wait or fail | Prefer protecting critical traffic over equal treatment under load |
| Feed grants back into load | Shows cascade and recovery behavior | Simulation needs more tuning | Make allocator decisions visible in future capacity |
| Queue lower-priority work with deadlines | Protects system stability | Users may wait or expire | Queue only when recovery can plausibly happen before the deadline |
| Reject under overload | Prevents collapse | Lost work / poor UX | Accept lost low-priority work over cascade failure |
| Reduce tokens under load | Controls cost and latency | Lower answer quality | Serve reduced context only when minimum quality and token floors still hold |
| Optimize model under pressure | Preserves throughput | May reduce answer quality | Prefer cheaper model plus more context when it beats premium with severe trimming |
| Enforce quality thresholds | Avoids bad answers | More requests may be rejected | Reject bad answers instead of making reliability metrics look better |
| Expensive model for high priority | Better quality when capacity allows | Higher cost | Use premium only when the system can afford it |

## Lessons from the run

- High-priority requests were protected with zero tick latency, but they pushed load high enough to delay and expire medium/low-priority work. This is the intended tradeoff: critical traffic survives, best-effort traffic absorbs pressure.
- Request 6 drained only after load recovered below the queue threshold. This shows the queue is not a black hole; recovery behavior directly controls whether queued work becomes useful or expires.
- Request 7 was rejected even though it was high priority because the best feasible option could grant only 2,640 tokens against a 3,000-token minimum. The system avoids spending GPU on an answer that would miss the caller's minimum useful context.
- The run requested 34,600 tokens but granted 8,000. The difference split into 10,800 served-token trims and 15,800 unserved rejected/expired tokens, with `token_accounting_delta: 0` proving the accounting is closed.

## What's not modeled yet

This is a control-plane simulation, not a production inference gateway. Useful next steps would be:

- Real context trimming. `trim_strategy` is currently a policy label; production code would need actual chunk ranking, summarization, and prompt packing.
- Request profiling. The simulation accepts `requested_tokens` and `minimum_tokens`; a real platform would derive those from the prompt, documents, code diff, output budget, and task policy.
- Dynamic arrival rates. Requests currently arrive at hardcoded ticks; a stronger simulation would generate bursty, steady-state, and incident-style traffic patterns.
- Multi-region capacity pools. The capacity manager models one shared GPU pool; production systems often route across regions, clusters, or model-serving backends.
- Adaptive policies. Thresholds, recovery rate, model weights, and deadlines are static; production policies would be tuned from telemetry and eval outcomes.
- Real cost and latency curves. GPU load and cost are simplified estimates; production systems would use measured model latency, queue depth, memory pressure, and provider pricing.
- Backpressure responses. Rejection is logged, but a real API would return retry-after hints, partial-result options, or a request to narrow scope.

## Portfolio angle

This demonstrates AI infrastructure product judgment: protecting critical traffic, making degradation explicit, connecting token economics to GPU capacity, and using metrics to explain why the control plane accepted, degraded, queued, or rejected each request.
