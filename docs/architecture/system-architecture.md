# System Architecture

## Overview

- Modular monorepo with separable services
- API Gateway (FastAPI) + scheduling worker(s)
- Data service, import/export, notification service
- Postgres, Redis, S3‑compatible storage

## Cross‑cutting

- OpenTelemetry tracing; Prometheus metrics; structured JSON logging
- RBAC + multi‑tenant isolation (tenant_id; optional Postgres RLS)
- Encryption in transit and at rest

## Diagrams

- Context, container, and component diagrams (to be added)
