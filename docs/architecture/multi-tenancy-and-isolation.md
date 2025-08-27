# Multi-tenancy and Isolation

## Model

- `tenant_id` column on all tenant-scoped tables
- Optional Postgres Row Level Security (RLS)

## Isolation

- App-level scoping per request via JWT claims
- Optional schema-per-tenant for large enterprise (TBD)

## Security

- Encryption in transit and at rest
- Minimal privileges; separate service accounts
