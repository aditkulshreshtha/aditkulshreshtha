# Layered LLM Cost Control Architecture

## Goal
Help even a naive user reduce token usage without understanding tokens deeply.

## Core Principle
Do not send everything to the LLM. Send the smallest useful context.

## Layers

### Layer 1: User Intent Router
Classifies the request:
- simple answer
- code help
- memory lookup
- deep reasoning
- report generation

### Layer 2: Token Budget Policy
Controls how many tokens a request can use based on intent and user/team budget.

### Layer 3: Context File Manager
Uses structured context files instead of full chat history.

### Layer 4: Age-Based Context OS
Context becomes cheaper/shorter as it ages:
- fresh context: full detail
- recent context: summarized
- old context: concept tags only
- archive: retrieved only when needed

### Layer 5: Concept Graph / OpenClaw-Style Memory
Instead of dumping long files, retrieve by concepts:
- career
- finance
- AI infra
- GPU systems
- token control
- home
- travel

### Layer 6: Cron Job Controller
Daily jobs run with strict budgets and summary-only mode.

## Outcome
Lower cost, lower latency, better focus, and more sustainable experimentation.
