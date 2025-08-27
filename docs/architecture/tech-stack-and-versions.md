# 技术栈与版本（Context7 研究）

本文件作为研究与决策的单一来源，记录精确版本、权衡理由、官方文档链接与迁移注意事项。当前仅确定方向性选择；具体版本需完成 Context7 调研后钉住并附官方链接。

## 研究与决策模板（待填）

### 后端

| 组件 | 版本（待定） | 官方链接（待填） | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Python | 3.12.x |  | 主流、性能改进 | 3.11.x | C 扩展兼容性、镜像体积 |
| FastAPI |  |  | ASGI 生态、OpenAPI 生成 | Starlite、Django REST | 与 Pydantic v2 集成注意 |
| Pydantic | v2.x |  | 性能与类型支持 | dataclasses、msgspec | v1→v2 语法与行为差异 |
| SQLAlchemy | 2.0.x |  | 成熟 ORM、2.0 API | TortoiseORM | 同步/异步会话管理 |
| Alembic |  |  | 版本化迁移 | Prisma | 向后兼容策略 |
| Uvicorn |  |  | 生产可用 ASGI 服务 | Hypercorn | HTTP/2、UVLoop 配置 |
| httpx |  |  | 同步/异步一致 | requests | 超时、重试、连接池策略 |
| Redis 客户端 |  |  | 官方/社区稳定客户端 | —— | 连接池、断线重连 |
| 队列 | RQ（已选） |  | 轻量、Redis 原生、便于私有化 | Celery、Dramatiq | 定时/重试/可观测性需方案化 |
| OR-Tools |  |  | CP-SAT 求解器 | —— | 二进制依赖、CPU 指令集 |
| OpenTelemetry |  |  | 统一追踪标准 | —— | 采样与导出器选择 |
| Prometheus client |  |  | 指标标准化 | —— | 标签维度与基数控制 |
| Sentry SDK |  |  | 错误聚合与性能 | —— | PII 脱敏、采样率 |

### 前端

| 组件 | 版本（待定） | 官方链接（待填） | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Vue | 3.x |  | 组合式 API、TS 友好 | React、Svelte | 严格类型策略 |
| Vite | 5/6 |  | 快速构建、插件生态 | Webpack | 与 Vitest 集成 |
| TypeScript | 最新稳定 |  | 类型安全 | —— | tsconfig 严格模式 |
| Pinia |  |  | 轻量状态管理 | —— | Store 设计约定 |
| Vue Router | 4.x |  | 官方路由 | —— | 守卫、懒加载 |
| UI 库 | Element Plus（已选） |  | 生态成熟、组件覆盖广 | Naive UI | 设计语言与主题定制 |
| ECharts |  |  | 大数据渲染 | Chart.js | 性能与按需加载 |
| vue-i18n |  |  | i18n 标准方案 | i18next | 词条懒加载 |
| ESLint/Prettier |  |  | 团队一致性 | —— | 规则冲突处理 |
| Vitest |  |  | Vite 原生测试 | Jest | 覆盖率与快照策略 |
| Playwright |  |  | 多浏览器 E2E | Cypress | 并行与报告 |

### 打包与包管理

| 领域 | 方案（已选/待定） | 版本（待定） | 官方链接（待填） | 选择理由 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| 后端包管理 | uv（已选） |  |  | 速度快、可复现 | 与 Poetry 的兼容与迁移 |
| 前端包管理 | pnpm |  |  | workspace、硬链接去重 | 锁文件、CI 一致性 |

### 认证与授权

| 能力 | 方案 | 版本（待定） | 官方链接（待填） | 选择理由 | 注意事项 |
| --- | --- | --- | --- | --- | --- |
| OIDC | Keycloak/Auth0/Azure AD |  |  | 合规、生态成熟 | 多租户域隔离、属性映射 |
| JWT | JWS |  |  | 无状态鉴权 | 过期、撤销、换发 |
| 无密码 | 可选 |  |  | 降低摩擦 | 风险控制、范围限定 |

### 运维与基础设施

| 组件 | 版本（待定） | 官方链接（待填） | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Docker/Compose |  |  | 本地与 CI 一致性 | Podman | Rootless、镜像规范 |
| Kubernetes |  |  | 标准编排 | —— | API 兼容窗口 |
| Postgres | 16+ |  | 可靠与特性 | 15 | 扩展、PITR |
| Redis | 7+ |  | 队列/缓存/发布订阅 | —— | 持久化/哨兵/集群 |
| 对象存储 | S3 兼容 |  | 私有化可用 | —— | SSE、生命周期策略 |
| Ingress | Nginx |  | 成熟生态 | Traefik | 超时、限流、WAF |
| 证书 | cert-manager |  | 自动签发与轮换 | —— | ACME、私有 CA 集成 |
| GitOps/CD | ArgoCD/GitHub Actions |  | 可观测与回滚 | —— | 多环境推广策略 |

## 研究记录与链接（留空待填）

- 日期：
- 结论摘要：
- 证据（官方文档、发布日志、示例）：

> 禁止基于记忆确定版本。需引用权威来源并记录迁移风险。