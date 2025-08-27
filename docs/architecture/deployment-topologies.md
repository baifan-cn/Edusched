# Deployment Topologies

- Dev: docker-compose, single-node Postgres and Redis
- Staging: Kubernetes, single region
- Production: Kubernetes, multi-AZ, managed Postgres, node pool for compute workers
- Ingress via Nginx; cert-manager for TLS
- ArgoCD or GitHub Actions for GitOps/CD
