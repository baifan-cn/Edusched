# Architecture Diagram: Context

Textual placeholder for the C4 Context diagram.

- System: Edusched (school timetabling)
- Primary users: Scheduler, School Admin, Teacher, Viewer
- External systems:
  - OIDC Provider (Keycloak/Auth0/Azure AD)
  - Email/SMS gateway
  - SIS (Student Information System)
  - Object Storage (S3-compatible)
- Trust boundaries:
  - External identity boundary (OIDC)
  - Internet/DMZ vs. cluster internal network
- Data flows:
  - SPA ↔ API (REST/WebSocket)
  - API ↔ Postgres/Redis/S3
  - API ↔ RQ (enqueue jobs)
  - Worker ↔ Redis (dequeue/progress)
  - Worker ↔ Postgres (results)
