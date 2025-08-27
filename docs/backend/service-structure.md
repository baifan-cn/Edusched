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

## Phase 1 脚手架（待实施清单）

- 目录：
  - `backend/app/routers/`（按资源分组：teachers、rooms、sections、jobs 等）
  - `backend/app/schemas/`（Pydantic v2 模型；Request/Response DTO）
  - `backend/core/config.py`（settings：env/读取器；uv 兼容）
  - `backend/core/logging.py`（JSON 结构化日志 + OTel 注入）
  - `backend/core/security.py`（OIDC 验证、RBAC 装饰器）
  - `backend/domain/models.py`（SQLAlchemy 2.0 声明式）
  - `backend/domain/repositories.py`（仓储 + 单元工作）
  - `backend/workers/`（RQ 队列：排课作业处理器）
  - `backend/migrations/`（Alembic 初始化）
  - `backend/tests/`（pytest 结构）

- 工具链：
  - 包管理：uv（锁文件与分发）
  - 代码质量：ruff + mypy + pytest + pytest-asyncio + pre-commit
  - 可观测性：opentelemetry-sdk + prometheus-client
  - 错误监控：sentry-sdk（按需）

- 配置：
  - 环境变量：`DATABASE_URL`、`REDIS_URL`、`OIDC_ISSUER`、`OIDC_AUDIENCE`
  - 日志：`LOG_LEVEL`、`LOG_FORMAT=json`、`OTEL_EXPORTER_OTLP_ENDPOINT`

- 启动：
  - `uvicorn app.main:app --workers N --factory`
