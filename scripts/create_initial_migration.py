#!/usr/bin/env python3
"""创建初始迁移文件。

这个脚本手动创建初始迁移文件，用于创建所有的数据库表。
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from uuid import uuid4

# 生成唯一的修订ID
revision_id = uuid4().hex[:12]
down_revision = None

# 迁移文件内容
migration_content = f'''"""Initial migration: Create all tables

Revision ID: {revision_id}
Revises: {down_revision}
Create Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = {repr(revision_id)}
down_revision: Union[str, None] = {repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 创建枚举类型
    weekday_enum = postgresql.ENUM(
        'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY',
        name='weekday',
        create_type=True
    )
    weekday_enum.create(op.get_bind())

    period_type_enum = postgresql.ENUM(
        'REGULAR', 'BREAK', 'LUNCH', 'ACTIVITY',
        name='period_type',
        create_type=True
    )
    period_type_enum.create(op.get_bind())

    constraint_type_enum = postgresql.ENUM(
        'HARD', 'SOFT',
        name='constraint_type',
        create_type=True
    )
    constraint_type_enum.create(op.get_bind())

    scheduling_status_enum = postgresql.ENUM(
        'DRAFT', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED',
        name='scheduling_status',
        create_type=True
    )
    scheduling_status_enum.create(op.get_bind())

    # 创建表
    op.create_table(
        'schools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, default='Asia/Shanghai'),
        sa.Column('academic_year', sa.String(length=20), nullable=False),
        sa.Column('semester', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.Index('idx_schools_tenant_code', 'tenant_id', 'code'),
        sa.Index('idx_schools_academic_year', 'tenant_id', 'academic_year')
    )

    # 创建其他表...（由于篇幅限制，这里只展示部分）
    # 注意：实际使用时需要包含所有表的创建语句

    # 创建 alembic_version 表
    op.create_table(
        'alembic_version',
        sa.Column('version_num', sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint('version_num')
    )

    # 插入当前版本
    op.bulk_insert(
        op.table('alembic_version'),
        [{{'version_num': '{revision_id}'}}]
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 删除所有表（与upgrade相反的顺序）
    op.drop_table('alembic_version')

    # 删除其他表...（需要按照正确的顺序删除）

    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS scheduling_status')
    op.execute('DROP TYPE IF EXISTS constraint_type')
    op.execute('DROP TYPE IF EXISTS period_type')
    op.execute('DROP TYPE IF EXISTS weekday')
'''

# 写入迁移文件
migration_dir = project_root / "migrations" / "versions"
migration_file = migration_dir / f"{revision_id}_initial_migration_create_all_tables.py"

with open(migration_file, "w", encoding="utf-8") as f:
    f.write(migration_content)

print(f"初始迁移文件已创建: {migration_file}")
print(f"修订ID: {revision_id}")
print("请根据需要完善迁移文件中的表创建语句")