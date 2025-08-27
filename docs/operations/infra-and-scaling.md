# Infrastructure and Scaling

## Environments

- Dev: docker-compose
- Staging: Kubernetes single region
- Prod: Kubernetes multi-AZ

## Scaling

- HPA for API
- Dedicated node pool for compute workers
- Redis sizing and connection pools

## Storage

- Postgres managed service (PITR)
- S3-compatible object storage for imports/exports
