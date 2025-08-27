# CI/CD（私有化优先）

## Pipelines

- Lint, type-check, test, security scan (SAST)
- Build Docker images; push to 企业私有镜像仓库（Harbor/Artifactory/ACR 等）
- Deploy to environments via ArgoCD（首选）或 GitHub Actions → 自管集群

## Quality gates

- Coverage thresholds; linting enforced via pre-commit/Husky；容器镜像扫描（Trivy/Grype）与依赖安全扫描
