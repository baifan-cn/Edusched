# Authentication and RBAC

## Authentication

- OIDC（已选能力）：优先支持企业常用提供方（Keycloak/Auth0/Azure AD）
- JWT tokens; refresh flow as per provider
- Optional passwordless for limited roles if needed

## Authorization

- Role-based: SuperAdmin, SchoolAdmin, Scheduler, Teacher, Student, Viewer
- Resource-level checks with tenant scoping

### 角色-权限矩阵（示例）

- SuperAdmin：全租户读写、系统配置、审计导出
- SchoolAdmin：本租户学校范围读写、用户与角色绑定、发布课表
- Scheduler：排课相关资源读写（sections/assignments/timetables/jobs/imports）
- Teacher：查看个人课表、提交可用性、申请调课（受限）
- Viewer：只读

资源操作（示例）：

- `timetables`：读（Viewer+）、写（Scheduler+）、发布（SchoolAdmin+）
- `assignments`：读（Viewer+）、写（Scheduler+）
- `imports/exports`：导入（Scheduler+）、导出（Viewer+）

### 多租户/多校区/多学校边界

- SchoolAdmin 默认限于本租户内的授权学校集合；可配置是否跨学校管理。
- 跨校区访问需具备相应角色/授权范围；默认教师仅可访问/编辑与自身相关资源。

### 敏感字段脱敏

- 对电话、邮箱等 PII 字段在非必要场景下按角色脱敏显示（如 `138****1234`）。

## Session management

- Short-lived tokens; revocation via provider（与 OIDC 配置一致）
- CSRF protections for browser flows

## OIDC 登录流（SPA 授权码 + PKCE）

- 前端发起授权码流程（PKCE），回调后以代码换取 `access_token`/`refresh_token`
- 后端仅验证与资源访问（Bearer），刷新在前端或 BFF 端点进行
- 注销：前端清理本地会话并调用 OP 的 `end_session_endpoint`

## RLS 策略草案（Postgres 可选）

- 全局：`ALTER TABLE <t> ENABLE ROW LEVEL SECURITY;`
- 读取策略：`USING (tenant_id = current_setting('app.tenant_id')::uuid AND (campus_id IS NULL OR campus_id = ANY (current_setting('app.campus_ids')::uuid[])))`
- 写入策略：在读取条件基础上加 `WITH CHECK (...)`

## 审计事件字典（示例）

- `timetable.published`：包含 `timetable_id`, `actor`, `diff`
- `assignment.updated`：包含 `assignment_id`, `before`, `after`, `reason`
