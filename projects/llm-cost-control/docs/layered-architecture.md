# Layered LLM Cost Control Architecture

## Goal
Help users and teams reduce LLM token usage without requiring them to understand token mechanics.

## Core Principle
Do not send everything to the model. Send the smallest useful context that preserves answer quality.

## Layers

### Layer 1: Intent Router
Classifies the request:
- simple answer
- code assistance
- knowledge lookup
- deep reasoning
- report generation

### Layer 2: Token Budget Policy
Controls how many tokens a request can use based on intent, service tier, user/team limits, and current system load.

### Layer 3: Context File Manager
Uses structured context files instead of full raw conversation history.

### Layer 4: Age-Based Context OS
Context becomes cheaper and shorter as it ages:
- fresh context: full detail
- recent context: summarized
- old context: concept tags only
- archive: retrieved only when needed

### Layer 5: Concept Graph / Agent Memory
Instead of dumping long files, retrieve by enterprise-safe concepts:
- product requirements
- incident history
- architecture decisions
- customer support patterns
- security controls
- reliability risks
- cost optimization
- model evaluation

### Layer 6: Scheduled Job Controller
Background jobs run with strict token budgets, summary-only mode, and skip rules for low-value runs.

## Tradeoffs

| Design Choice | Benefit | Cost / Risk |
|---|---|---|
| Trim context aggressively | Lower cost and latency | May remove useful nuance |
| Summarize old context | Keeps long-term memory cheap | Summaries can lose detail or encode bias |
| Retrieve by concept tags | More relevant context | Requires good tagging/index quality |
| Cache repeated prompts | Reduces repeated token spend | Risk of stale answers |
| Strict daily job budgets | Prevents silent cost growth | Important jobs may be skipped |
| Smaller models for simple tasks | Lower cost | Lower quality on ambiguous tasks |

## Production Questions

- What quality loss is acceptable for lower token spend?
- Which requests deserve full context?
- When should a scheduled job be skipped?
- How do we detect stale cached answers?
- Who can override token budgets during incidents?

## Outcome
Lower cost, lower latency, better focus, and more sustainable experimentation.
