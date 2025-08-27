# Integration and Imports

## Imports

- CSV/Excel templates with validation
- SIS connectors 通过适配器模式：
  - PowerSchool/本地标准（如 xEdu 等）
  - 统一抽象接口：拉取/推送、字段映射、增量同步
  - 私有化部署注意：网络连通、认证方式（API Key/OIDC 代理）、节流与速率限制
- Dry-run mode with detailed errors
- Mapping wizard for columns/fields
- Audit trail of changes

## Exports

- PDF/Excel/CSV
- ICS calendar per teacher/class/room
- API endpoints for downstream consumption

## 选择与取舍（SIS 解释）

- 若学校已有标准化 SIS：优先对接，确保只读导入与最小权限
- 若无：提供 CSV/Excel 模板与向导，保证数据质量与可回滚
- 审计：所有导入/导出均记录审计事件，便于追踪与合规
