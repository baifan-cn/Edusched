# Security and Compliance

## Data protection

- TLS everywhere; HSTS
- Encryption at rest (Postgres TDE options and S3 SSE)
- Secret management (Kubernetes secrets + external vault optional)

## Identity and access

- OIDC SSO; JWT-based sessions; optional 2FA for admins
- RBAC with least privilege

## Multi-tenant isolation

- `tenant_id` scoping and optional RLS

## Compliance

- GDPR and China PIPL awareness
- Data retention and deletion policies
- Audit logging for critical actions
