# LLM Cost Control System

## Overview
Controls token usage, context size, and cost for LLM workloads.

## Key Ideas
- Token budgets per request/team
- Context trimming
- Caching
- Experiment sampling
- Cost tracking

## Flow
User -> Budget -> Context -> Cache -> Router -> LLM -> Cost
