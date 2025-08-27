# 技术栈与版本（Context7 研究）

本文件作为研究与决策的单一来源，记录精确版本、权衡理由、官方文档链接与迁移注意事项。以下版本基于联网查询（注册表/官网），需在落地前以发行说明再次核验。

## 后端

| 组件 | 版本 | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Python | 3.12.x | https://www.python.org/downloads/ | 主流、性能改进 | 3.11.x | C 扩展兼容性、镜像体积 |
| FastAPI | 待定 | https://fastapi.tiangolo.com/ | ASGI 生态、OpenAPI 生成 | Starlite、Django REST | 与 Pydantic v2 集成注意 |
| Pydantic | 2.11.7 | https://docs.pydantic.dev/latest/ | 性能与类型支持 | dataclasses、msgspec | v1→v2 语法/配置变更（`model_config` 等） |
| SQLAlchemy | 2.0.43 | https://docs.sqlalchemy.org/en/20/ | 成熟 ORM、2.0 API | TortoiseORM | 2.0 风格、typed statements、异步会话 |
| Alembic | 待定 | https://alembic.zzzcomputing.com/ | 版本化迁移 | Prisma | 迁移脚本幂等、向后兼容策略 |
| Uvicorn | 0.35.0 | https://www.uvicorn.org/ | 生产可用 ASGI 服务 | Hypercorn | HTTP/2、UVLoop 配置与兼容性 |
| httpx | 0.28.1 | https://www.python-httpx.org/ | 同步/异步一致 | requests | 超时/重试/连接池统一封装 |
| redis (python) | 6.4.0 | https://redis-py.readthedocs.io/ | 官方/社区稳定客户端 | —— | 连接池、断线重连、超时策略 |
| RQ | 2.5.0 | https://python-rq.org/ | 轻量、Redis 原生、便于私有化 | Celery、Dramatiq | 定时/重试/可观测性需方案化整合 |
| OR-Tools | 9.14.6206 | https://developers.google.com/optimization | CP-SAT 求解器 | —— | 二进制依赖、CPU 指令集、容器镜像体积 |
| OpenTelemetry SDK | 1.36.0 | https://opentelemetry.io/docs/languages/python/ | 统一追踪标准 | —— | 采样、导出器（OTLP）、上下文传播 |
| Prometheus client | 0.22.1 | https://github.com/prometheus/client_python | 指标标准化 | —— | 指标命名/标签基数控制 |
| Sentry SDK | 2.35.1 | https://docs.sentry.io/platforms/python/ | 错误聚合与性能 | —— | PII 脱敏、采样率、发布关联 |

## 前端

| 组件 | 版本 | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Vue | 3.5.20 | https://vuejs.org/ | 组合式 API、TS 友好 | React、Svelte | RFC/次要破坏性变更关注 |
| Vite | 7.1.3 | https://vitejs.dev/ | 快速构建、插件生态 | Webpack | Node 版本门槛、插件兼容 |
| TypeScript | 待定 | https://www.typescriptlang.org/ | 类型安全 | —— | tsconfig 严格模式、DOM lib 版本 |
| Pinia | 3.0.3 | https://pinia.vuejs.org/ | 轻量状态管理 | —— | Store 设计约定、SSR 注意点 |
| Vue Router | 4.5.1 | https://router.vuejs.org/ | 官方路由 | —— | 守卫、懒加载、滚动行为 |
| Element Plus | 2.11.1 | https://element-plus.org/ | 生态成熟、组件覆盖广 | Naive UI | 设计语言与主题定制、A11y |
| ECharts | 6.0.0 | https://echarts.apache.org/ | 大数据渲染 | Chart.js | 按需加载、性能优化 |
| vue-i18n | 11.1.11 | https://vue-i18n.intlify.dev/ | i18n 标准方案 | i18next | 词条懒加载、消息格式化 |
| ESLint | 待定 | https://eslint.org/ | 代码规范 | —— | 规则冲突处理、TS/Vue 插件版本配套 |
| Prettier | 3.6.2 | https://prettier.io/ | 统一格式 | —— | 与 ESLint 协调、禁用冲突规则 |
| Vitest | 待定 | https://vitest.dev/ | Vite 原生测试 | Jest | 覆盖率与快照策略、TS 配置 |
| Playwright | 1.55.0 | https://playwright.dev/ | 多浏览器 E2E | Cypress | 浏览器依赖下载与并行策略 |

## 打包与包管理

| 领域 | 方案 | 版本 | 官方链接 | 选择理由 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| 后端包管理 | uv（已选） | 待定 | https://docs.astral.sh/uv/ | 速度快、可复现 | 与 Poetry 的兼容与迁移 |
| 前端包管理 | pnpm | 待定 | https://pnpm.io/ | workspace、硬链接去重 | 锁文件、CI 一致性 |

## 认证与授权

| 能力 | 方案 | 版本 | 官方链接 | 选择理由 | 注意事项 |
| --- | --- | --- | --- | --- | --- |
| OIDC | Keycloak/Auth0/Azure AD | 待定 | https://openid.net/specs/openid-connect-core-1_0.html | 合规、生态成熟 | 多租户域隔离、属性映射 |
| Keycloak 文档 | —— | —— | https://www.keycloak.org/documentation | 参考实现 | Realm/客户端/角色映射 |
| Auth0 文档 | —— | —— | https://auth0.com/docs/protocols/oidc | 参考实现 | 租户与连接器 |
| Azure AD（Entra ID） | —— | —— | https://learn.microsoft.com/azure/active-directory/develop/v2-protocols-oidc | 参考实现 | 应用注册与声明 |
| JWT | JWS | —— | https://www.rfc-editor.org/rfc/rfc7519 | 无状态鉴权 | 过期、撤销、换发 |

## 运维与基础设施

| 组件 | 版本 | 官方链接 | 选择理由 | 备选方案 | 迁移注意事项 |
| --- | --- | --- | --- | --- | --- |
| Docker | 待定 | https://docs.docker.com/ | 容器打包 | —— | 镜像减重与签名（Cosign） |
| Docker Compose | 待定 | https://docs.docker.com/compose/ | 本地编排 | Podman | 环境一致性 |
| Kubernetes | 待定 | https://kubernetes.io/docs/home/ | 标准编排 | —— | API 兼容窗口、Ingress 适配 |
| Postgres | 16+ | https://www.postgresql.org/docs/ | 可靠与特性 | 15 | 扩展、PITR、RLS |
| Redis | 7+ | https://redis.io/docs/latest/ | 队列/缓存/发布订阅 | —— | 持久化/哨兵/集群 |
| S3 兼容对象存储 | —— | https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html | 生态兼容 | MinIO | SSE、生命周期策略 |
| Ingress-NGINX | 待定 | https://kubernetes.github.io/ingress-nginx/ | 成熟生态 | Traefik | 超时、限流、WAF |
| cert-manager | 待定 | https://cert-manager.io/docs/ | 证书自动化 | —— | ACME、私有 CA 集成 |
| ArgoCD | 待定 | https://argo-cd.readthedocs.io/ | GitOps/CD | —— | 多环境推广策略 |
| GitHub Actions | 待定 | https://docs.github.com/actions | CI/CD | —— | Runner 权限与缓存 |

## 备注

- 标注“待定”的条目将在落地前根据发行/兼容矩阵最终确认。
- 强制使用官方文档与发行说明作为依据；禁止基于记忆确定版本。
- 重要变更需记录迁移脚本/步骤、回滚策略与兼容期。

## 兼容矩阵（初稿，最终以 Context7 研究为准）

- 后端运行时
  - Python 3.12.x + FastAPI（待定） + Pydantic v2.11.x + Uvicorn 0.35.x
  - SQLAlchemy 2.0.x + Alembic（待定）
  - Redis 7.x + RQ 2.5.x
- 前端工具链
  - Node.js LTS（待定） + pnpm（待定）
  - Vue 3.5.x + Vite 7.1.x + TypeScript（待定，strict=true）
  - ESLint（待定） + Prettier 3.6.x + Vitest（待定） + Playwright 1.55.x
- 集群与运维
  - Kubernetes（待定） + Ingress-NGINX（待定） + cert-manager（待定）
  - ArgoCD（待定）/GitHub Actions（待定）

说明：以上矩阵用于评估兼容性窗口，避免出现不受支持的组合；最终版本需在 Context7 拉取各官方“支持矩阵/Release Notes”后钉住。

## 迁移与破坏性变更注意事项

- Pydantic v1 → v2：`BaseModel` 配置迁移到 `model_config`；`validate_*` 钩子变化；序列化行为差异。
- SQLAlchemy 1.4/以下 → 2.0：使用 2.0 风格；同步/异步 Session 区分；`select()` 返回与类型提示变化。
- FastAPI（待定大版本）：依赖注入与 `response_model` 行为在新版本检查严格度差异；Starlette 升级同步。
- TypeScript（待定大版本）：严格模式下 DOM/Node lib 版本不一致导致类型报错；`moduleResolution` 策略升级。
- ESLint v9（若采用）：插件生态与扁平化配置变更；需迁移到 `eslint.config.js`。
- Vitest 2（若采用）：覆盖率提供方变化（V8/istanbul）；`happy-dom`/`jsdom` 差异。
- Kubernetes（待定）：API 弃用（如 Ingress v1beta1→v1 已完成，继续关注 CRD 变更）。

## 私有化镜像源与离线安装指引（草案）

- 私有镜像仓库
  - 使用企业 Harbor/Artifactory/ACR；复制上游镜像到私有仓库，启用镜像签名与拉取策略。
  - 建议镜像命名：`registry.corp/edusched/<component>:<version>`；通过 Helm/Kustomize 覆盖镜像地址。
- 上游镜像清单（示例）
  - `python:<minor>-slim`（后端基础镜像）
  - `node:<minor>-bullseye`（前端构建）
  - `postgres:<major>`、`redis:<major>`、`nginxinc/nginx-unprivileged`（如需）
  - `ingress-nginx/controller:<version>`、`jetstack/cert-manager-controller:<version>`、`argoproj/argocd:<version>`
- 离线安装
  - 预拉取并保存镜像：`docker pull ... && docker save -o images.tar ...`；在离线环境 `docker load -i images.tar`。
  - 依赖包离线缓存：后端使用 uv 的 `uv cache`；前端使用 pnpm store + 离线镜像（`pnpm fetch`）。
  - 证书与仓库认证：预置 CA 证书到节点信任；在 CI/集群侧配置 docker registry secret。

> 注：标注“待定”的版本将在 Context7 研究完成后一次性钉住，并附上对应官方链接与迁移注意事项引用。