# Backend Service Structure

## Monorepo layout (planned)

- `backend/app/` — FastAPI app (routers, schemas, dependencies)
- `backend/core/` — config, logging, security
- `backend/domain/` — models and repositories
- `backend/workers/` — scheduling engine jobs
- `backend/migrations/` — Alembic
- `backend/tests/`

## Standards

- Ruff, mypy, pytest, pytest-asyncio, pre-commit
