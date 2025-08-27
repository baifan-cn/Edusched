# Multi-tenancy and Isolation

## Model

- `tenant_id` column on all tenant-scoped tables
- Optional Postgres Row Level Security (RLS)
 - `campus_id` 作为细粒度访问边界（可选、按资源）

## Isolation

- App-level scoping per request via JWT claims
- Optional schema-per-tenant for large enterprise (TBD)
 - 校区维度隔离：对资源打标签（campus_id），并在查询与授权中强制过滤

### 读/写策略示例（应用层）

- 读：在查询构造时强制 `WHERE tenant_id = :tenant_id AND (campus_id IS NULL OR campus_id IN (:campus_ids))`
- 写：校验请求主体的 `tenant_id/campus_id` 是否在调用者授权范围内；拒绝跨校区写入（除非角色具备跨校区权限）

## Security

- Encryption in transit and at rest
- Minimal privileges; separate service accounts
 - 可选启用 Postgres RLS（按 tenant_id/campus_id）以增强隔离
