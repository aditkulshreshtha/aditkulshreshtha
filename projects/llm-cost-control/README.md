# Adaptive LLM Token Allocation System

## Overview

A production-style simulation for controlling LLM token usage, context size, model choice, and experimentation cost.

The core idea: tokens should be treated like a scarce compute resource, not an unlimited prompt budget.

## Problem

LLM systems become expensive when:

- every request gets too much context
- background jobs run without strict budgets
- experiments run on too much traffic
- expensive models are used for low-value tasks
- old context is repeatedly sent instead of summarized or retrieved

## Solution

An adaptive allocation layer that decides per request:

- how many tokens to allow
- how much context to include
- which model tier to use
- whether an experiment should run
- whether the outcome should update future policy

## Architecture

```text
Request
  ↓
Intent Classifier
  ↓
Value Estimator
  ↓
Adaptive Budget Allocator
  ↓
Context Optimizer
  ↓
Model Selector
  ↓
LLM Call / Simulation
  ↓
Feedback Loop
```

## Modules

```text
src/
  intent_classifier.py
  value_estimator.py
  adaptive_budget_allocator.py
  context_optimizer_v3.py
  model_selector.py
  feedback_loop.py
  adaptive_token_system_v3.py
```

## Production Tradeoffs

| Decision | Benefit | Risk |
|---|---|---|
| Adaptive budgets | Better cost control | Less predictable user experience |
| Aggressive context trimming | Lower latency and cost | Quality may degrade |
| Model tiering | Saves money on simple work | Cheap models can miss nuance |
| Value-based prioritization | Aligns spend to business impact | Can create fairness concerns |
| Feedback-based tuning | Improves over time | Adds operational complexity |
| Cron/job limits | Prevents silent cost growth | Useful background work may be skipped |

## Metrics

- tokens requested
- tokens allocated
- tokens used
- estimated cost
- model tier selected
- quality / success score
- budget rejection rate
- average context compression ratio

## Why this matters

At scale, token waste becomes infrastructure waste. A TPM or platform leader needs to manage token usage like GPU capacity: budgeted, prioritized, measured, and continuously optimized.
