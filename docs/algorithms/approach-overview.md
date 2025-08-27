# Algorithm Approach Overview

## Strategy

Two‑stage hybrid:
1. Feasibility via CP‑SAT (hard constraints)
2. Optimization via weighted soft constraints with fairness

## Heuristics

- Warm‑start: graph coloring, largest degree first, saturation degree ordering
- Local search/Tabu for improvements; deterministic seeds

## Orchestration

- Jobs: draft → running → feasible → optimized → published
- Checkpoints, pause/resume, cancellation
- Progress events via Redis/WebSocket
