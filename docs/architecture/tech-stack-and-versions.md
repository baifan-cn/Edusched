# 技术栈与版本（Context7 研究）

本文件作为研究与决策的单一来源，记录精确版本、权衡理由、官方文档链接与迁移注意事项。当前仅确定方向性选择；具体版本需完成 Context7 调研后钉住并附官方链接。

## 研究与决策模板（待填）

### 后端

| 组件 | 版本（待定） | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Python | 3.12.x | https://www.python.org/downloads/ | 主流、性能改进 | 3.11.x | C 扩展兼容性、镜像体积 |
| FastAPI |  | https://fastapi.tiangolo.com/ | ASGI 生态、OpenAPI 生成 | Starlite、Django REST | 与 Pydantic v2 集成注意 |
| Pydantic | v2.x | https://docs.pydantic.dev/latest/ | 性能与类型支持 | dataclasses、msgspec | v1→v2 语法与行为差异 |
| SQLAlchemy | 2.0.x | https://docs.sqlalchemy.org/en/20/ | 成熟 ORM、2.0 API | TortoiseORM | 同步/异步会话管理 |
| Alembic |  | https://alembic.zzzcomputing.com/ | 版本化迁移 | Prisma | 向后兼容策略 |
| Uvicorn |  | https://www.uvicorn.org/ | 生产可用 ASGI 服务 | Hypercorn | HTTP/2、UVLoop 配置 |
| httpx |  | https://www.python-httpx.org/ | 同步/异步一致 | requests | 超时、重试、连接池策略 |
| Redis 客户端 |  | https://redis-py.readthedocs.io/ | 官方/社区稳定客户端 | —— | 连接池、断线重连 |
| 队列 | RQ（已选） | https://python-rq.org/ | 轻量、Redis 原生、便于私有化 | Celery、Dramatiq | 定时/重试/可观测性需方案化 |
| OR-Tools |  | https://developers.google.com/optimization | CP-SAT 求解器 | —— | 二进制依赖、CPU 指令集 |
| OpenTelemetry |  | https://opentelemetry.io/docs/languages/python/ | 统一追踪标准 | —— | 采样与导出器选择 |
| Prometheus client |  | https://github.com/prometheus/client_python | 指标标准化 | —— | 标签维度与基数控制 |
| Sentry SDK |  | https://docs.sentry.io/platforms/python/ | 错误聚合与性能 | —— | PII 脱敏、采样率 |

### 前端

| 组件 | 版本（待定） | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Vue | 3.x | https://vuejs.org/ | 组合式 API、TS 友好 | React、Svelte | 严格类型策略 |
| Vite | 5/6 | https://vitejs.dev/ | 快速构建、插件生态 | Webpack | 与 Vitest 集成 |
| TypeScript | 最新稳定 | https://www.typescriptlang.org/ | 类型安全 | —— | tsconfig 严格模式 |
| Pinia |  | https://pinia.vuejs.org/ | 轻量状态管理 | —— | Store 设计约定 |
| Vue Router | 4.x | https://router.vuejs.org/ | 官方路由 | —— | 守卫、懒加载 |
| UI 库 | Element Plus（已选） | https://element-plus.org/ | 生态成熟、组件覆盖广 | Naive UI | 设计语言与主题定制 |
| ECharts |  | https://echarts.apache.org/ | 大数据渲染 | Chart.js | 性能与按需加载 |
| vue-i18n |  | https://vue-i18n.intlify.dev/ | i18n 标准方案 | i18next | 词条懒加载 |
| ESLint |  | https://eslint.org/ | 代码规范 | —— | 规则冲突处理 |
| Prettier |  | https://prettier.io/ | 统一格式 | —— | 规则冲突处理 |
| Vitest |  | https://vitest.dev/ | Vite 原生测试 | Jest | 覆盖率与快照策略 |
| Playwright |  | https://playwright.dev/ | 多浏览器 E2E | Cypress | 并行与报告 |

### 打包与包管理

| 领域 | 方案（已选/待定） | 版本（待定） | 官方链接 | 选择理由 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| 后端包管理 | uv（已选） |  | https://docs.astral.sh/uv/ | 速度快、可复现 | 与 Poetry 的兼容与迁移 |
| 前端包管理 | pnpm |  | https://pnpm.io/ | workspace、硬链接去重 | 锁文件、CI 一致性 |

### 认证与授权

| 能力 | 方案 | 版本（待定） | 官方链接 | 选择理由 | 注意事项 |
| --- | --- | --- | --- | --- | --- |
| OIDC | Keycloak/Auth0/Azure AD |  | https://openid.net/specs/openid-connect-core-1_0.html | 合规、生态成熟 | 多租户域隔离、属性映射 |
| Keycloak 文档 |  |  | https://www.keycloak.org/documentation | 参考实现 | Realm/客户端/角色映射 |
| Auth0 文档 |  |  | https://auth0.com/docs/protocols/oidc | 参考实现 | 租户与连接器 |
| Azure AD（Entra ID） |  |  | https://learn.microsoft.com/azure/active-directory/develop/v2-protocols-oidc | 参考实现 | 应用注册与声明 |
| JWT | JWS |  | https://www.rfc-editor.org/rfc/rfc7519 | 无状态鉴权 | 过期、撤销、换发 |

### 运维与基础设施

| 组件 | 版本（待定） | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Docker |  | https://docs.docker.com/ | 容器打包 | —— | 镜像减重与签名 |
| Docker Compose |  | https://docs.docker.com/compose/ | 本地编排 | Podman | 环境一致性 |
| Kubernetes |  | https://kubernetes.io/docs/home/ | 标准编排 | —— | API 兼容窗口 |
| Postgres | 16+ | https://www.postgresql.org/docs/ | 可靠与特性 | 15 | 扩展、PITR |
| Redis | 7+ | https://redis.io/docs/latest/ | 队列/缓存/发布订阅 | —— | 持久化/哨兵/集群 |
| 对象存储（S3） |  | https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html | 生态兼容 | MinIO | SSE、生命周期策略 |
| Ingress-NGINX |  | https://kubernetes.github.io/ingress-nginx/ | 成熟生态 | Traefik | 超时、限流、WAF |
| cert-manager |  | https://cert-manager.io/docs/ | 证书自动化 | —— | ACME、私有 CA 集成 |
| ArgoCD |  | https://argo-cd.readthedocs.io/ | GitOps/CD | —— | 多环境推广策略 |
| GitHub Actions |  | https://docs.github.com/actions | CI/CD | —— | Runner 权限与缓存 |

## 研究记录与链接（留空待填）

- 日期：
- 结论摘要：
- 证据（官方文档、发布日志、示例）：

> 禁止基于记忆确定版本。需引用权威来源并记录迁移风险。