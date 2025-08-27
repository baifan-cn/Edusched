# Architecture Diagram: Component

Textual placeholder for the C4 Component diagram.

- API components:
  - Routers (teachers, rooms, sections, timetables, jobs)
  - Schemas (Pydantic v2 DTOs)
  - Auth (OIDC validation, RBAC)
  - Services (domain orchestration)
  - Repositories (SQLAlchemy 2.0)
  - Observability (OTel, Prometheus)
- Worker components:
  - Job handler (enqueue/dequeue)
  - Model builder (variables/constraints)
  - Solver (CP-SAT/local search)
  - Result writer (assignments, score)
  - Progress publisher (Redis Pub/Sub)
- Frontend components:
  - Timetable workspace (grid, drag/drop)
  - Stores (Pinia)
  - API client (OpenAPI generated + interceptors)
