# 数据库迁移目录

这个目录包含了Edusched项目的所有数据库迁移文件。

## 目录结构

- `versions/` - 包含所有的迁移脚本文件
- `env.py` - Alembic环境配置
- `script.py.mako` - 迁移脚本模板

## 迁移命名规范

迁移文件采用以下命名模式：
```
{revision}_{slug}.py
```

其中：
- `{revision}` - 唯一的修订ID（自动生成）
- `{slug}` - 基于迁移消息的简短描述

## 运行迁移

### 升级数据库到最新版本
```bash
alembic upgrade head
```

### 降级到指定版本
```bash
alembic downgrade {revision}
```

### 查看迁移历史
```bash
alembic history --verbose
```

### 创建新的迁移
```bash
alembic revision --autogenerate -m "描述信息"
```

## 多租户支持

本项目的迁移系统支持多租户架构。所有的表都包含`tenant_id`字段以确保数据隔离。

## 注意事项

1. **永远不要手动修改迁移文件** - 所有更改都应该通过新的迁移来完成
2. **在提交代码前运行测试** - 确保迁移不会破坏现有数据
3. **在生产环境运行迁移前备份数据库**