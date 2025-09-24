# 数据库迁移管理指南

本文档介绍如何使用Alembic管理Edusched项目的数据库迁移。

## 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [迁移命令](#迁移命令)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)
- [多租户支持](#多租户支持)

## 概述

Edusched使用[Alembic](https://alembic.sqlalchemy.org/)作为数据库迁移工具。Alembic是SQLAlchemy的官方迁移工具，提供了强大的数据库版本控制功能。

### 特性

- ✅ 支持SQLAlchemy 2.0
- ✅ 自动生成迁移脚本
- ✅ 支持PostgreSQL特有功能（枚举类型、JSON等）
- ✅ 多租户架构支持
- ✅ 完整的升级和降级支持
- ✅ 迁移历史追踪

## 快速开始

### 1. 环境准备

确保已安装项目依赖：

```bash
# 安装项目依赖
uv pip install -e .

# 或使用pip
pip install -e .
```

### 2. 数据库连接

配置数据库连接参数。可以通过以下方式之一：

#### 方式1：使用完整URL（推荐）

在`.env`文件中设置：

```env
DATABASE_URL=postgresql://edusched:edusched@localhost:5432/edusched
```

#### 方式2：使用单独参数

在`.env`文件中设置：

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=edusched
DB_USER=edusched
DB_PASSWORD=edusched
```

### 3. 初始化数据库

首次运行前，需要创建数据库：

```bash
# 使用Makefile
make db-init

# 或手动创建
createdb -U edusched -h localhost -p 5432 edusched
```

### 4. 运行迁移

```bash
# 升级到最新版本
make migrate-up

# 或使用脚本
python3 scripts/migrate.py upgrade
```

## 迁移命令

### 基本命令

#### 查看当前版本

```bash
make migrate-current
# 或
python3 scripts/migrate.py current
```

#### 查看迁移历史

```bash
make migrate-history
# 或
python3 scripts/migrate.py history --verbose
```

#### 检查迁移状态

```bash
make migrate-check
# 或
python3 scripts/migrate.py check
```

### 创建新迁移

当修改了数据模型后，需要创建新的迁移：

```bash
# 创建迁移（自动检测更改）
make migrate-new MSG="添加用户首选项字段"

# 或使用脚本
python3 scripts/migrate.py revision --message "添加用户首选项字段" --autogenerate
```

### 升级和降级

#### 升级数据库

```bash
# 升级到最新版本
make migrate-up

# 升级到指定版本
python3 scripts/migrate.py upgrade --revision abc123
```

#### 降级数据库

```bash
# 降级到指定版本
make migrate-down REV=abc123

# 或使用脚本
python3 scripts/migrate.py downgrade abc123
```

### 生成SQL脚本

有时需要先生成SQL脚本而不是直接执行：

```bash
# 生成升级SQL
python3 scripts/migrate.py upgrade --sql > upgrade.sql

# 生成降级SQL
python3 scripts/migrate.py downgrade abc123 --sql > downgrade.sql
```

## 最佳实践

### 1. 迁移命名

使用清晰、描述性的迁移消息：

```bash
# 好的例子
make migrate-new MSG="add_teacher_max_hours_constraint"
make migrate-new MSG="create_student_attendance_table"
make migrate-new MSG="update_credits_field_precision"

# 避免的例子
make migrate-new MSG="update"
make migrate-new MSG="fix"
make migrate-new MSG="new changes"
```

### 2. 迁移文件管理

- 每个迁移文件应该是自包含的
- 避免在单个迁移中包含过多更改
- 保持迁移文件的顺序性

### 3. 数据安全

**重要：在生产环境运行迁移前，务必备份数据库！**

```bash
# PostgreSQL备份示例
pg_dump -U edusched -h localhost -p 5432 edusched > backup.sql
```

### 4. 测试迁移

在应用到生产环境前，始终在测试环境验证迁移：

```bash
# 1. 在测试数据库运行迁移
DATABASE_URL=postgresql://edusched:test@localhost:5432/edusched_test python3 scripts/migrate.py upgrade

# 2. 运行测试套件
pytest

# 3. 验证降级
python3 scripts/migrate.py downgrade previous_version
```

### 5. 团队协作

- 在合并代码前运行所有迁移
- 确保迁移脚本可以重复执行
- 及时处理迁移冲突

## 故障排除

### 常见错误

#### 1. 数据库连接错误

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) ...
```

**解决方案：**
- 检查数据库服务是否运行
- 验证连接参数是否正确
- 确保数据库已创建

#### 2. 迁移历史不一致

```
alembic.exc.CommandError: Online migration expected revision ...
```

**解决方案：**
```bash
# 检查当前状态
python3 scripts/migrate.py current

# 如果数据库为空，可以标记为初始版本
python3 scripts/migrate.py stamp head
```

#### 3. 外键约束错误

```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.ForeignKeyViolation) ...
```

**解决方案：**
- 检查表删除顺序
- 可能需要先删除数据再删除表
- 在降级函数中调整操作顺序

#### 4. 枚举类型错误

```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.InvalidObjectDefinition) ...
```

**解决方案：**
- 确保在创建表前先创建枚举类型
- 在降级时最后删除枚举类型

### 调试技巧

#### 1. 启用详细日志

临时修改`alembic.ini`中的日志级别：

```ini
[logger_sqlalchemy]
level = INFO
handlers =
qualname = sqlalchemy.engine
```

#### 2. 生成SQL而不执行

使用`--sql`选项查看将要执行的SQL：

```bash
python3 scripts/migrate.py upgrade --sql
```

#### 3. 使用单步执行

对于复杂的迁移，可以逐步执行：

```bash
# 生成SQL
python3 scripts/migrate.py upgrade --sql > migration.sql

# 手动检查和执行
psql -U edusched -d edusched -f migration.sql
```

## 多租户支持

Edusched支持多租户架构，所有表都包含`tenant_id`字段以确保数据隔离。

### 租户相关注意事项

1. **自动过滤**：所有查询都会自动包含`tenant_id`条件
2. **迁移影响**：迁移会应用到所有租户的数据
3. **索引设计**：每个表都有基于`tenant_id`的复合索引

### 租户特定迁移

如果需要为特定租户运行迁移：

```python
# 在迁移脚本中
def upgrade():
    # 为特定租户执行操作
    op.execute("UPDATE table SET ... WHERE tenant_id = 'tenant1'")
```

## 迁移脚本示例

### 添加新表

```python
def upgrade() -> None:
    """添加新表 example。"""
    op.create_table(
        'examples',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_examples_tenant_name', 'tenant_id', 'name')
    )

def downgrade() -> None:
    """删除表 example。"""
    op.drop_table('examples')
```

### 添加新列

```python
def upgrade() -> None:
    """添加新列到 users 表。"""
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, default=True))

def downgrade() -> None:
    """从 users 表删除列。"""
    op.drop_column('users', 'phone')
    op.drop_column('users', 'is_active')
```

### 创建索引

```python
def upgrade() -> None:
    """创建性能优化索引。"""
    op.create_index('idx_users_email_tenant', 'users', ['tenant_id', 'email'], unique=True)

def downgrade() -> None:
    """删除索引。"""
    op.drop_index('idx_users_email_tenant', 'users')
```

## 参考资源

- [Alembic官方文档](https://alembic.sqlalchemy.org/en/latest/)
- [SQLAlchemy 2.0文档](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)

## 贡献指南

如果发现迁移相关的问题或需要改进：

1. 查看现有的迁移文件作为参考
2. 遵循命名约定
3. 包含适当的升级和降级逻辑
4. 在PR中描述更改的内容和原因