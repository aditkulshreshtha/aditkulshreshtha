# AI Infrastructure Control Plane

A portfolio-grade Python project that demonstrates how an AI platform can manage GPU capacity, failover, and workload prioritization across multiple clusters.

## Why this project matters

Modern AI platforms need more than GPUs. They need an operating layer that can answer:

- Which jobs should run first?
- What happens when a cluster fails?
- How do we protect inference capacity?
- How do we reduce queue delays and idle spend?
- How do executives understand infrastructure risk?

This project models a simplified AI infrastructure control plane with reusable scheduling logic.

## Core capabilities

- GPU cluster health detection
- Priority-based workload scheduling
- Queue fallback when capacity is unavailable
- Failover-aware allocation
- Capacity and utilization reporting
- Executive-ready metrics framing

## Architecture

```text
AI Workloads
   ↓
Global Scheduler
   ↓
AI Infra Control Plane
   ├── Capacity Manager
   ├── Failover Engine
   ├── Priority Scheduler
   └── Metrics Reporter
   ↓
GPU Clusters
```

## Example scenario

Cluster A fails during peak load. The control plane:

1. Removes Cluster A from eligible scheduling
2. Sorts workloads by priority
3. Allocates jobs to healthy clusters
4. Queues jobs that cannot be safely placed
5. Produces metrics for leadership review

## Run locally

```bash
python src/control_plane.py
```

## Example output

```text
Job assignments:
{1: 'B', 2: 'B', 3: 'C', 4: 'QUEUED'}
```

## TPM / Leadership lens

This project demonstrates how a technical program leader thinks across:

- infrastructure reliability
- GPU capacity constraints
- business prioritization
- incident response
- executive communication
- cost-aware operations

## Metrics to track

| Metric | Why it matters |
|---|---|
| GPU utilization | Measures fleet efficiency |
| Queue wait time | Measures developer/customer friction |
| Failover recovery time | Measures resilience |
| Jobs rerouted | Measures automation effectiveness |
| SLA impact | Measures customer risk |
| Idle capacity | Measures waste |

## Disclaimer

This is a public portfolio simulation using synthetic data only. It contains no proprietary, confidential, or employer-specific information.
