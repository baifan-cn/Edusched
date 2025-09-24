# 迁移示例

本文档提供了常见的数据库迁移场景示例。

## 目录

- [添加新表](#添加新表)
- [修改表结构](#修改表结构)
- [添加索引](#添加索引)
- [处理枚举类型](#处理枚举类型)
- [数据迁移](#数据迁移)
- [添加约束](#添加约束)

## 添加新表

当需要添加全新的数据模型时：

```python
"""Add teacher preferences table

Revision ID: a1b2c3d4e5f6
Revises: 69174d2c9756
Create Date: 2024-01-15 10:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '69174d2c9756'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add teacher preferences table."""
    op.create_table(
        'teacher_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('teacher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('preferred_days', sa.JSON(), nullable=False, default=[]),
        sa.Column('preferred_time_ranges', sa.JSON(), nullable=False, default=[]),
        sa.Column('avoided_rooms', sa.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False, default=[]),
        sa.Column('max_daily_classes', sa.Integer(), nullable=False, default=6),
        sa.Column('min_break_minutes', sa.Integer(), nullable=False, default=30),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_teacher_preferences_teacher', 'teacher_id'),
        sa.Index('idx_teacher_preferences_tenant', 'tenant_id')
    )


def downgrade() -> None:
    """Remove teacher preferences table."""
    op.drop_table('teacher_preferences')
```

## 修改表结构

### 添加新列

```python
"""Add soft delete to all tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2024-01-15 11:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add deleted_at column for soft delete."""
    # 批量添加到所有需要的表
    tables = [
        'schools', 'campuses', 'buildings', 'rooms', 'teachers',
        'subjects', 'courses', 'grades', 'class_groups', 'sections',
        'timeslots', 'week_patterns', 'calendars', 'constraints',
        'timetables', 'assignments', 'scheduling_jobs'
    ]

    for table in tables:
        op.add_column(
            table,
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
        )

        # 添加索引以提高查询性能
        op.create_index(
            f'idx_{table}_deleted_at',
            table,
            ['deleted_at']
        )


def downgrade() -> None:
    """Remove soft delete columns."""
    tables = [
        'schools', 'campuses', 'buildings', 'rooms', 'teachers',
        'subjects', 'courses', 'grades', 'class_groups', 'sections',
        'timeslots', 'week_patterns', 'calendars', 'constraints',
        'timetables', 'assignments', 'scheduling_jobs'
    ]

    # 反向顺序删除
    for table in reversed(tables):
        op.drop_index(f'idx_{table}_deleted_at', table_name=table)
        op.drop_column(table, 'deleted_at')
```

### 修改列属性

```python
"""Extend teacher name field length

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2024-01-15 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Extend name column length in teachers table."""
    # PostgreSQL可以自动增加字段长度
    op.alter_column(
        'teachers',
        'name',
        existing_type=sa.String(length=200),
        type_=sa.String(length=300),
        existing_nullable=False
    )


def downgrade() -> None:
    """Revert name column length."""
    # 减少长度需要确保没有超长的数据
    op.alter_column(
        'teachers',
        'name',
        existing_type=sa.String(length=300),
        type_=sa.String(length=200),
        existing_nullable=False
    )
```

## 添加索引

```python
"""Add performance indexes

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2024-01-15 15:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite indexes for common queries."""
    # 优化教师查询
    op.create_index(
        'idx_teachers_department_active',
        'teachers',
        ['tenant_id', 'department', 'is_active']
    )

    # 优化教室查询
    op.create_index(
        'idx_rooms_building_type_active',
        'rooms',
        ['tenant_id', 'building_id', 'room_type', 'is_active']
    )

    # 优化课程表查询
    op.create_index(
        'idx_timetables_calendar_status',
        'timetables',
        ['tenant_id', 'calendar_id', 'status']
    )


def downgrade() -> None:
    """Remove added indexes."""
    op.drop_index('idx_teachers_department_active', 'teachers')
    op.drop_index('idx_rooms_building_type_active', 'rooms')
    op.drop_index('idx_timetables_calendar_status', 'timetables')
```

## 处理枚举类型

```python
"""Add new period types

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2024-01-16 09:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new period types to enum."""
    # PostgreSQL需要先创建新类型
    op.execute("CREATE TYPE period_type_new AS ENUM ('REGULAR', 'BREAK', 'LUNCH', 'ACTIVITY', 'ASSEMBLY', 'EXAM')")

    # 修改列使用新类型
    op.execute("ALTER TABLE sections ALTER COLUMN period_type TYPE period_type_new USING period_type::text::period_type_new")
    op.execute("ALTER TABLE sections DROP CONSTRAINT IF EXISTS chk_sections_period_type")

    # 更新timeslots表中的period_type
    op.execute("ALTER TABLE timeslots ALTER COLUMN period_type TYPE period_type_new USING period_type::text::period_type_new")

    # 删除旧类型，重命名新类型
    op.execute("DROP TYPE period_type")
    op.execute("ALTER TYPE period_type_new RENAME TO period_type")


def downgrade() -> None:
    """Revert period type changes."""
    # 创建旧类型
    op.execute("CREATE TYPE period_type_old AS ENUM ('REGULAR', 'BREAK', 'LUNCH', 'ACTIVITY')")

    # 强制将新值转为旧值
    op.execute("""
        ALTER TABLE sections
        ALTER COLUMN period_type TYPE period_type_old
        USING
            CASE
                WHEN period_type::text IN ('REGULAR', 'BREAK', 'LUNCH', 'ACTIVITY')
                THEN period_type::text::period_type_old
                ELSE 'REGULAR'::period_type_old
            END
    """)

    op.execute("""
        ALTER TABLE timeslots
        ALTER COLUMN period_type TYPE period_type_old
        USING
            CASE
                WHEN period_type::text IN ('REGULAR', 'BREAK', 'LUNCH', 'ACTIVITY')
                THEN period_type::text::period_type_old
                ELSE 'REGULAR'::period_type_old
            END
    """)

    # 清理
    op.execute("DROP TYPE period_type")
    op.execute("ALTER TYPE period_type_old RENAME TO period_type")
```

## 数据迁移

```python
"""Migrate room features to new format

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2024-01-16 10:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate room features from text to JSON."""
    # 添加新列
    op.add_column(
        'rooms',
        sa.Column('features_new', sa.JSON(), nullable=False, default=dict)
    )

    # 获取数据库连接
    connection = op.get_bind()
    session = sessionmaker(bind=connection)()

    try:
        # 迁移数据
        connection.execute("""
            UPDATE rooms
            SET features_new = CASE
                WHEN features IS NOT NULL AND features != ''
                THEN json_build_object(
                    'equipment', string_to_array(features, ','),
                    'migrated', true
                )
                ELSE json_build_object('migrated', false)
            END
        """)

        session.commit()
    finally:
        session.close()

    # 删除旧列，重命名新列
    op.drop_column('rooms', 'features')
    op.alter_column('rooms', 'features_new', new_column_name='features')


def downgrade() -> None:
    """Revert room features migration."""
    # 添加旧列
    op.add_column(
        'rooms',
        sa.Column('features_old', sa.Text(), nullable=True)
    )

    # 获取数据库连接
    connection = op.get_bind()
    session = sessionmaker(bind=connection)()

    try:
        # 迁移数据
        connection.execute("""
            UPDATE rooms
            SET features_old = CASE
                WHEN features->>'equipment' IS NOT NULL
                THEN array_to_string((features->'equipment')::text[], ',')
                ELSE NULL
            END
        """)

        session.commit()
    finally:
        session.close()

    # 清理
    op.drop_column('rooms', 'features')
    op.alter_column('rooms', 'features_old', new_column_name='features')
```

## 添加约束

```python
"""Add data integrity constraints

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2024-01-16 13:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add data validation constraints."""
    # 确保学分大于0
    op.create_check_constraint(
        "chk_credits_positive",
        "courses",
        "credits > 0"
    )

    # 确保学生人数非负
    op.create_check_constraint(
        "chk_student_count_non_negative",
        "class_groups",
        "student_count >= 0"
    )

    # 确保时间段的开始时间早于结束时间
    op.create_check_constraint(
        "chk_timeslot_time_order",
        "timeslots",
        "start_time < end_time"
    )

    # 确保权重在0-1之间
    op.create_check_constraint(
        "chk_constraint_weight_range",
        "constraints",
        "weight >= 0 AND weight <= 1"
    )


def downgrade() -> None:
    """Remove added constraints."""
    op.drop_constraint("chk_credits_positive", "courses", type_="check")
    op.drop_constraint("chk_student_count_non_negative", "class_groups", type_="check")
    op.drop_constraint("chk_timeslot_time_order", "timeslots", type_="check")
    op.drop_constraint("chk_constraint_weight_range", "constraints", type_="check")
```

## 批量操作示例

```python
"""Add audit columns to existing tables

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2024-01-16 15:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2a3'
down_revision: Union[str, None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add last_modified_by column to track user changes."""
    # 需要添加的表列表
    tables_to_update = [
        'schools', 'campuses', 'buildings', 'rooms', 'teachers',
        'subjects', 'courses', 'grades', 'class_groups', 'sections',
        'timeslots', 'week_patterns', 'calendars', 'constraints',
        'timetables', 'assignments'
    ]

    # 批量添加列
    for table in tables_to_update:
        op.add_column(
            table,
            sa.Column('last_modified_by', sa.String(length=100), nullable=True)
        )

        # 为该列创建索引以提高查询性能
        op.create_index(
            f'idx_{table}_last_modified_by',
            table,
            ['last_modified_by']
        )


def downgrade() -> None:
    """Remove last_modified_by columns."""
    tables_to_update = [
        'schools', 'campuses', 'buildings', 'rooms', 'teachers',
        'subjects', 'courses', 'grades', 'class_groups', 'sections',
        'timeslots', 'week_patterns', 'calendars', 'constraints',
        'timetables', 'assignments'
    ]

    # 反向顺序删除
    for table in reversed(tables_to_update):
        op.drop_index(f'idx_{table}_last_modified_by', table_name=table)
        op.drop_column(table, 'last_modified_by')
```

## 最佳实践

1. **保持迁移简单**：每个迁移只做一个逻辑更改
2. **提供降级路径**：始终实现`downgrade()`函数
3. **数据安全**：在修改数据前先备份
4. **测试迁移**：在测试环境充分测试后再应用到生产
5. **文档记录**：在迁移消息中清晰描述更改内容