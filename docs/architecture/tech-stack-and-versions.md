# Tech Stack and Versions (Context7 research)

This file will capture pinned versions, rationales, documentation links, and migration notes.

## Backend

- Python 3.12.x
- FastAPI (latest)
- Pydantic v2
- SQLAlchemy 2.0
- Alembic
- Uvicorn
- httpx
- Redis
- Celery or RQ (to be decided with tradeoffs)
- OR‑Tools
- OpenTelemetry
- Prometheus client
- Sentry SDK

## Frontend

- Vue 3 (latest)
- Vite 5/6
- TypeScript (latest)
- Pinia
- Vue Router 4
- UI: Element Plus or Naive UI (TBD)
- ECharts
- vue‑i18n
- ESLint/Prettier
- Vitest
- Playwright

## Packaging

- uv or Poetry (TBD after research) for backend
- pnpm for frontend

## Auth

- OIDC (Keycloak/Auth0/Azure AD) + JWT; passwordless option

## Ops

- Docker, Compose, Kubernetes, Postgres 16+, Redis 7+
- S3‑compatible object storage
- Nginx ingress, cert‑manager, ArgoCD/GitHub Actions

## Notes

- Add exact versions and links after Context7 research.
