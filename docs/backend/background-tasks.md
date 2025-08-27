# Background Tasks

## Job queue

- Celery or RQ workers for long-running scheduling jobs
- Redis as broker and pub/sub for progress

## Patterns

- Idempotent job handlers with checkpoints
- Cancellation and rollback
- Backoff and retries for transient failures
