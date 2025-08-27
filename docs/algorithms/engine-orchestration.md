# Engine Orchestration

## Lifecycle

- draft → running → feasible → optimized → published
- Idempotency keys; retries
- Checkpoints for pause/resume; rollback on cancel

## Components

- Worker (Celery/RQ) running OR‑Tools CP‑SAT and local search
- Redis queue and pub/sub for progress
- DB for inputs/outputs and audit

## Events

- Progress updates, conflict alerts, publish notifications via WS
