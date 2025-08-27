# Deployment Topologies

- Dev: docker-compose，单机 Postgres 与 Redis（便于本地开发）
- Staging: Kubernetes，单区域；私有化镜像仓库与私有 CA 集成
- Production（私有化为主）：Kubernetes，多可用区；托管/自建 Postgres（PITR），为计算型作业（RQ worker）配置专用节点池
- Ingress: Nginx；cert-manager 管理 TLS（内网/自签或对接企业 CA）
- CD: 以 ArgoCD（GitOps）为主，或使用 GitHub Actions 部署到自管集群
