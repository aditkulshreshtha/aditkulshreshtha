# Unified AI System

A runnable simulation that combines AI infrastructure load, token allocation, queueing, fallback behavior, and cost control.

## Problem
AI systems become expensive and unreliable when token usage, context size, GPU load, and request priority are managed independently.

## Solution
This project simulates a unified control layer that:

- allocates token budgets based on priority and load
- trims context before model calls
- queues lower-priority work under pressure
- rejects work when the queue is overloaded
- applies fallback under extreme load
- reports cost, tokens, queue size, rejections, and final GPU load

## Run

```bash
python main.py
```

## Expected output

The simulation prints total cost, total tokens, processed requests, rejections, queue size, and final GPU load.

## Tradeoffs

| Decision | Benefit | Risk |
|---|---|---|
| Queue lower-priority work | Protects system stability | Users may wait longer |
| Reject under overload | Prevents collapse | Lost work / poor UX |
| Reduce tokens under load | Controls cost and latency | Lower answer quality |
| Expensive model for high priority | Better quality | Higher cost |

## Portfolio angle

This demonstrates how an AI TPM can think across software orchestration, infrastructure capacity, token economics, fallback behavior, and measurable operational tradeoffs.
