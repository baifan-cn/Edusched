# Security and Compliance

## Data protection

- TLS everywhere; HSTS
- Encryption at rest (Postgres TDE options and S3 SSE)
- Secret management (Kubernetes secrets + external vault optional)

数据分级（示例）：

- P0（PII/敏感数据）：学生/教师个人信息、联系方式、课表明细
- P1（业务敏感）：排课约束、评分、调度策略
- P2（低敏）：公开元数据、非个体化统计

保护措施：字段级脱敏、最小可见面（RBAC）、导出加水印。

### 私有化部署安全加固

- 私有 CA/企业 PKI 集成；内外网分区与零信任网段
- 镜像签名与策略（如 Cosign/OPA Gatekeeper）

## Identity and access

- OIDC SSO（已选能力）；JWT-based sessions；可选管理员 2FA
- RBAC with least privilege

最小权限：服务账号分离（API/Worker/CI）、数据库最小权限角色（只读/读写/迁移）。

## Multi-tenant isolation

- `tenant_id` scoping and optional RLS

### 多校区与租户

- 校区维度标签与访问控制；租户/校区双层隔离可选

## Compliance

- GDPR and China PIPL awareness
- Data retention and deletion policies
- Audit logging for critical actions

数据主体请求：导出/更正/删除流程及响应 SLA；删除前快照与审计保留。
