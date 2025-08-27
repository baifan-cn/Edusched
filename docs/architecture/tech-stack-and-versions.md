# 技术栈与版本（Context7 研究）

本文件作为研究与决策的单一来源，记录精确版本、权衡理由、官方文档链接与迁移注意事项。

## 研究与决策模板

请在完成 Context7 调研后填写下表（示例字段；保持精确版本号与链接）。

### 后端

| 组件 | 版本 | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Python | 3.12.x |  |  | 3.11.x | C 扩展兼容性、打包工具支持 |
| FastAPI | latest |  |  | Starlite, Django REST | ASGI 生态、OpenAPI 生成 |
| Pydantic | v2.x |  |  | dataclasses, msgspec | v1→v2 变更、性能差异 |
| SQLAlchemy | 2.0.x |  |  | TortoiseORM | 2.0 异步/声明式用法更新 |
| Alembic | x.y |  |  | Prisma | 版本化迁移策略 |
| Uvicorn | x.y |  |  | Hypercorn | HTTP/2、UVLoop 支持 |
| httpx | x.y |  |  | requests | 同步/异步一致 API |
| Redis 客户端 | x.y |  |  | aiokafka | 连接池、断线重连 |
| 队列（Celery/RQ） | 待定 |  |  | Dramatiq | Bro ker、可观测性、重试策略 |
| OR-Tools | x.y |  |  | —— | CP-SAT 版本与性能差异 |
| OpenTelemetry | x.y |  |  | —— | 采样与导出器配置 |
| Prometheus client | x.y |  |  | —— | 指标命名与标签规范 |
| Sentry SDK | x.y |  |  | —— | PII 脱敏、采样率 |

### 前端

| 组件 | 版本 | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Vue | 3.x |  |  | React, Svelte | 组合式 API、TS 支持 |
| Vite | 5/6 |  |  | Webpack | 性能、插件生态 |
| TypeScript | latest |  |  | Flow | 严格模式策略 |
| Pinia | x.y |  |  | Vuex(legacy) | Store 结构与模块化 |
| Vue Router | 4.x |  |  | —— | 路由守卫与懒加载 |
| UI 库 | 待定 |  |  | 另一备选 | 设计语言与组件覆盖 |
| ECharts | x.y |  |  | Chart.js | 大数据渲染性能 |
| vue-i18n | x.y |  |  | i18next | 懒加载词条、消息格式化 |
| ESLint/Prettier | x.y |  |  | —— | 规则集与格式化冲突 |
| Vitest | x.y |  |  | Jest | Vite 原生集成 |
| Playwright | x.y |  |  | Cypress | 浏览器覆盖、并行策略 |

### 打包与包管理

| 领域 | 方案 | 版本 | 链接 | 选择理由 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| 后端包管理 | uv 或 Poetry（待定） |  |  |  | 锁文件、可复现构建 |
| 前端包管理 | pnpm |  |  |  | workspace、去重性能 |

### 认证与授权

| 能力 | 方案 | 版本 | 链接 | 选择理由 | 注意事项 |
| --- | --- | --- | --- | --- | --- |
| OIDC | Keycloak/Auth0/Azure AD |  |  | 生态、合规、托管选项 | 多租户 Realm/租户隔离 |
| JWT | JWS |  |  | 无状态鉴权 | 过期、撤销策略 |
| 无密码 | 可选 |  |  | 降低摩擦 | 风险控制、范围限定 |

### 运维与基础设施

| 组件 | 版本 | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Docker/Compose | x.y |  |  | Podman | 本地/CI 一致性 |
| Kubernetes | x.y |  |  | —— | 版本与 API 兼容窗口 |
| Postgres | 16+ |  |  | 15 | 扩展、PITR、性能 |
| Redis | 7+ |  |  | —— | 持久化/哨兵/集群 |
| 对象存储 | S3 兼容 |  |  | —— | SSE、生命周期策略 |
| Ingress | Nginx |  |  | Traefik | 证书、超时、限流 |
| 证书 | cert-manager |  |  | —— | ACME、证书轮转 |
| GitOps/CD | ArgoCD/GitHub Actions |  |  | —— | 多环境推广策略 |

## 研究记录与链接

- 日期：
- 结论摘要：
- 证据（官方文档、发布日志、示例）：

> 注：禁止基于记忆确定版本。需引用权威来源并记录迁移风险。
