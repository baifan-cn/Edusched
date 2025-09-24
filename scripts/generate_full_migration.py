#!/usr/bin/env python3
"""生成完整的初始迁移文件。

这个脚本根据SQLAlchemy模型生成完整的初始迁移文件。
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入所有模型
from edusched.infrastructure.database.models import (
    Base, School, Campus, Building, Room, Teacher, Subject, Course,
    Grade, ClassGroup, Section, Timeslot, WeekPattern, Calendar,
    Constraint, Timetable, Assignment, SchedulingJob
)
from edusched.domain.models import WeekDay, PeriodType, ConstraintType, SchedulingStatus
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects.postgresql import UUID

def generate_migration():
    """生成完整的迁移文件。"""
    revision_id = uuid4().hex[:12]

    # 创建迁移文件内容
    content = f'''"""Initial migration: Create all tables for Edusched

Revision ID: {revision_id}
Revises: None
Create Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "{revision_id}"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum types first
    op.execute("CREATE TYPE weekday AS ENUM ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')")
    op.execute("CREATE TYPE period_type AS ENUM ('REGULAR', 'BREAK', 'LUNCH', 'ACTIVITY')")
    op.execute("CREATE TYPE constraint_type AS ENUM ('HARD', 'SOFT')")
    op.execute("CREATE TYPE scheduling_status AS ENUM ('DRAFT', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')")

    # Create tables
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

    op.create_table(
        'campuses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('travel_time_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('is_main', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_campuses_school_code', 'school_id', 'code'),
        sa.Index('idx_campuses_tenant_school', 'tenant_id', 'school_id')
    )

    op.create_table(
        'grades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_grades_code', 'tenant_id', 'code'),
        sa.Index('idx_grades_level', 'tenant_id', 'level')
    )

    op.create_table(
        'subjects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_subjects_code', 'tenant_id', 'code'),
        sa.Index('idx_subjects_category', 'tenant_id', 'category')
    )

    op.create_table(
        'buildings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('campus_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('floors', sa.Integer(), nullable=False, default=1),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['campus_id'], ['campuses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_buildings_campus_code', 'campus_id', 'code'),
        sa.Index('idx_buildings_tenant_campus', 'tenant_id', 'campus_id')
    )

    op.create_table(
        'teachers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('max_hours_per_day', sa.Integer(), nullable=False, default=8),
        sa.Column('max_hours_per_week', sa.Integer(), nullable=False, default=40),
        sa.Column('preferred_time_slots', sa.JSON(), nullable=False, default=[]),
        sa.Column('unavailable_time_slots', sa.JSON(), nullable=False, default=[]),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_teachers_employee_id', 'tenant_id', 'employee_id'),
        sa.Index('idx_teachers_email', 'tenant_id', 'email'),
        sa.Index('idx_teachers_department', 'tenant_id', 'department')
    )

    op.create_table(
        'class_groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('grade_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('student_count', sa.Integer(), nullable=False),
        sa.Column('homeroom_teacher_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['grade_id'], ['grades.id'], ),
        sa.ForeignKeyConstraint(['homeroom_teacher_id'], ['teachers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_class_groups_grade_code', 'grade_id', 'code'),
        sa.Index('idx_class_groups_tenant_grade', 'tenant_id', 'grade_id')
    )

    op.create_table(
        'courses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('credits', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('hours_per_week', sa.Integer(), nullable=False),
        sa.Column('total_hours', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_courses_subject_code', 'subject_id', 'code'),
        sa.Index('idx_courses_tenant_subject', 'tenant_id', 'subject_id')
    )

    op.create_table(
        'rooms',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('building_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('room_type', sa.String(length=50), nullable=False, default='classroom'),
        sa.Column('features', sa.JSON(), nullable=False, default={{}}),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_rooms_building_code', 'building_id', 'code'),
        sa.Index('idx_rooms_tenant_building', 'tenant_id', 'building_id'),
        sa.Index('idx_rooms_capacity', 'tenant_id', 'capacity'),
        sa.Index('idx_rooms_type', 'tenant_id', 'room_type')
    )

    op.create_table(
        'timeslots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('week_day', postgresql.ENUM('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', name='weekday'), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('period_number', sa.Integer(), nullable=False),
        sa.Column('is_break', sa.Boolean(), nullable=False, default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_timeslots_week_day', 'tenant_id', 'week_day'),
        sa.Index('idx_timeslots_period_number', 'tenant_id', 'period_number'),
        sa.CheckConstraint('end_time > start_time', name='check_end_time_after_start')
    )

    op.create_table(
        'week_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_alternating', sa.Boolean(), nullable=False, default=False),
        sa.Column('weeks', sa.JSON(), nullable=False, default=[]),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_week_patterns_name', 'tenant_id', 'name'),
        sa.Index('idx_week_patterns_alternating', 'tenant_id', 'is_alternating')
    )

    op.create_table(
        'sections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('class_group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('teacher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('room_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('hours_per_week', sa.Integer(), nullable=False),
        sa.Column('period_type', postgresql.ENUM('REGULAR', 'BREAK', 'LUNCH', 'ACTIVITY', name='period_type'), nullable=False, default='REGULAR'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_sections_course_code', 'course_id', 'code'),
        sa.Index('idx_sections_teacher', 'tenant_id', 'teacher_id'),
        sa.Index('idx_sections_class_group', 'tenant_id', 'class_group_id'),
        sa.Index('idx_sections_period_type', 'tenant_id', 'period_type')
    )

    op.create_table(
        'constraints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('constraint_type', postgresql.ENUM('HARD', 'SOFT', name='constraint_type'), nullable=False),
        sa.Column('weight', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False, default={{}}),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_constraints_name', 'tenant_id', 'name'),
        sa.Index('idx_constraints_type', 'tenant_id', 'constraint_type'),
        sa.CheckConstraint('weight >= 0 AND weight <= 1', name='check_weight_range')
    )

    op.create_table(
        'calendars',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('academic_year', sa.String(length=20), nullable=False),
        sa.Column('semester', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('week_patterns', sa.JSON(), nullable=False, default=[]),
        sa.Column('holidays', sa.JSON(), nullable=False, default=[]),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_calendars_school_academic', 'school_id', 'academic_year', 'semester'),
        sa.Index('idx_calendars_tenant_school', 'tenant_id', 'school_id'),
        sa.CheckConstraint('end_date > start_date', name='check_end_date_after_start')
    )

    op.create_table(
        'timetables',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('calendar_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('DRAFT', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='scheduling_status'), nullable=False, default='DRAFT'),
        sa.Column('constraints', sa.JSON(), nullable=False, default=[]),
        sa.Column('extra_metadata', sa.JSON(), nullable=False, default={{}}),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['calendar_id'], ['calendars.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_timetables_calendar', 'calendar_id'),
        sa.Index('idx_timetables_status', 'tenant_id', 'status'),
        sa.Index('idx_timetables_tenant_calendar', 'tenant_id', 'calendar_id')
    )

    op.create_table(
        'assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('timetable_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timeslot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('room_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('week_pattern_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=False, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['timetable_id'], ['timetables.id'], ),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ),
        sa.ForeignKeyConstraint(['timeslot_id'], ['timeslots.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['week_pattern_id'], ['week_patterns.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_assignments_timetable_section', 'timetable_id', 'section_id'),
        sa.Index('idx_assignments_timeslot_room', 'timeslot_id', 'room_id'),
        sa.Index('idx_assignments_tenant_timetable', 'tenant_id', 'timetable_id')
    )

    op.create_table(
        'scheduling_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('timetable_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('DRAFT', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='scheduling_status'), nullable=False),
        sa.Column('progress', sa.Numeric(precision=3, scale=2), nullable=False, default=0.0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result_metadata', sa.JSON(), nullable=False, default={{}}),
        sa.Column('worker_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['timetable_id'], ['timetables.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_scheduling_jobs_timetable', 'timetable_id'),
        sa.Index('idx_scheduling_jobs_status', 'tenant_id', 'status'),
        sa.Index('idx_scheduling_jobs_worker', 'tenant_id', 'worker_id'),
        sa.CheckConstraint('progress >= 0 AND progress <= 1', name='check_progress_range')
    )

    # Create alembic_version table
    op.create_table('alembic_version',
        sa.Column('version_num', sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint('version_num')
    )

    # Insert current version
    op.bulk_insert(op.table('alembic_version'), [{{'version_num': '{revision_id}'}}])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('alembic_version')
    op.drop_table('scheduling_jobs')
    op.drop_table('assignments')
    op.drop_table('timetables')
    op.drop_table('calendars')
    op.drop_table('constraints')
    op.drop_table('sections')
    op.drop_table('week_patterns')
    op.drop_table('timeslots')
    op.drop_table('rooms')
    op.drop_table('courses')
    op.drop_table('class_groups')
    op.drop_table('teachers')
    op.drop_table('buildings')
    op.drop_table('subjects')
    op.drop_table('grades')
    op.drop_table('campuses')
    op.drop_table('schools')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS scheduling_status')
    op.execute('DROP TYPE IF EXISTS constraint_type')
    op.execute('DROP TYPE IF EXISTS period_type')
    op.execute('DROP TYPE IF EXISTS weekday')
'''

    # 写入迁移文件
    migration_dir = project_root / "migrations" / "versions"
    migration_file = migration_dir / f"{revision_id}_initial_migration_create_all_tables.py"

    with open(migration_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"完整的初始迁移文件已创建: {migration_file}")
    print(f"修订ID: {revision_id}")
    print("这个迁移文件包含了所有必需的表、索引和约束")

if __name__ == "__main__":
    generate_migration()