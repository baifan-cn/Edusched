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

## 私有化与多校区考虑

- 私有化部署优先：无外部托管依赖，镜像可推送至企业私有仓库
- 多校区：支持跨校区约束（出行时间缓冲）、资源标签（校区/楼栋/设备）与调度可达性控制

## Diagrams

- Context, container, and component diagrams (to be added)
