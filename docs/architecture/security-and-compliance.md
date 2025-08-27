# Security and Compliance

## Data protection

- TLS everywhere; HSTS
- Encryption at rest (Postgres TDE options and S3 SSE)
- Secret management (Kubernetes secrets + external vault optional)

### 私有化部署安全加固

- 私有 CA/企业 PKI 集成；内外网分区与零信任网段
- 镜像签名与策略（如 Cosign/OPA Gatekeeper）

## Identity and access

- OIDC SSO（已选能力）；JWT-based sessions；可选管理员 2FA
- RBAC with least privilege

## Multi-tenant isolation

- `tenant_id` scoping and optional RLS

### 多校区与租户

- 校区维度标签与访问控制；租户/校区双层隔离可选

## Compliance

- GDPR and China PIPL awareness
- Data retention and deletion policies
- Audit logging for critical actions
