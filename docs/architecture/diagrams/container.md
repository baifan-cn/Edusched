# Architecture Diagram: Container

Textual placeholder for the C4 Container diagram.

- Containers:
  - SPA (Vue 3)
  - API Gateway (FastAPI + Uvicorn)
  - Scheduling Worker (RQ + OR-Tools)
  - Data Service (SQLAlchemy/Alembic)
  - Import/Export Service
  - Notification Service (optional)
  - Postgres (16+)
  - Redis (7+)
  - Object Storage (S3-compatible)
  - Ingress-NGINX + cert-manager
- Contracts:
  - REST `/v1/*` and WebSocket `/ws/*`
  - RQ queues: default/high/low; JSON payloads; idempotency-key headers carried into job meta
  - DB access via repositories; transactions with unit-of-work
  - S3 object naming: `tenants/{tenant_id}/...`
- Trust boundaries:
  - Ingress to API; API to data plane
  - Admin-only endpoints and RBAC enforcement
