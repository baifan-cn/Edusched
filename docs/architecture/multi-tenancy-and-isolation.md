# Multi-tenancy and Isolation

## Model

- `tenant_id` column on all tenant-scoped tables
- Optional Postgres Row Level Security (RLS)

## Isolation

- App-level scoping per request via JWT claims
- Optional schema-per-tenant for large enterprise (TBD)
 - 校区维度隔离：对资源打标签（campus_id），并在查询与授权中强制过滤

## Security

- Encryption in transit and at rest
- Minimal privileges; separate service accounts
 - 可选启用 Postgres RLS（按 tenant_id/campus_id）以增强隔离
