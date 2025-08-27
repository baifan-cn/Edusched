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

### 部署拓扑（文本框架）

- 环境：Dev（docker-compose）、Staging（单区 K8s）、Prod（多可用区 K8s，私有化）
- 组件：
  - API 网关（FastAPI）：/v1 REST + WebSocket；OIDC 认证；RBAC；OpenTelemetry
  - 数据服务：SQLAlchemy 仓储/工作单元；Alembic 迁移；审计日志
  - 调度引擎 Worker（RQ）：OR‑Tools CP‑SAT + 本地搜索；Redis 队列与进度发布
  - 导入/导出：CSV/Excel 模板；SIS 适配器；对象存储（S3 兼容）
  - 通知：邮件/SMS/Webhook（可选）
  - 数据库：Postgres（16+）；Redis（7+）
  - 入口：Ingress‑NGINX + cert‑manager；ArgoCD（GitOps/CD）

### 组件关系（文本框架）

- 前端（Vue 3 + Element Plus）→ API（FastAPI）
- API → 数据库（Postgres）、对象存储（S3）；发布事件到 Redis Pub/Sub
- API → RQ 队列（提交作业）；Worker 消费作业并写回结果（Postgres）
- Worker → 通过 Redis Pub/Sub 推送进度；API 将进度透传到 WebSocket 客户端
- OIDC 提供方（Keycloak/Auth0/Azure AD）→ API 网关的认证与令牌校验
