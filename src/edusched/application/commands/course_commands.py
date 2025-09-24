"""课程管理相关命令。

包含创建、更新、删除课程等操作的命令定义。
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from ..base import BaseCommand


class CreateSubjectCommand(BaseCommand):
    """创建学科命令。"""
    name: str
    code: str
    category: str
    description: Optional[str] = None
    is_active: bool = True


class UpdateSubjectCommand(BaseCommand):
    """更新学科命令。"""
    subject_id: UUID
    name: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DeleteSubjectCommand(BaseCommand):
    """删除学科命令。"""
    subject_id: UUID


class CreateCourseCommand(BaseCommand):
    """创建课程命令。"""
    subject_id: UUID
    name: str
    code: str
    description: Optional[str] = None
    credits: Decimal
    hours_per_week: int
    total_hours: int
    is_active: bool = True


class UpdateCourseCommand(BaseCommand):
    """更新课程命令。"""
    course_id: UUID
    subject_id: Optional[UUID] = None
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[Decimal] = None
    hours_per_week: Optional[int] = None
    total_hours: Optional[int] = None
    is_active: Optional[bool] = None


class DeleteCourseCommand(BaseCommand):
    """删除课程命令。"""
    course_id: UUID


class CreateGradeCommand(BaseCommand):
    """创建年级命令。"""
    name: str
    code: str
    level: int
    description: Optional[str] = None


class UpdateGradeCommand(BaseCommand):
    """更新年级命令。"""
    grade_id: UUID
    name: Optional[str] = None
    code: Optional[str] = None
    level: Optional[int] = None
    description: Optional[str] = None


class DeleteGradeCommand(BaseCommand):
    """删除年级命令。"""
    grade_id: UUID


class CreateClassGroupCommand(BaseCommand):
    """创建班级命令。"""
    grade_id: UUID
    name: str
    code: str
    student_count: int
    homeroom_teacher_id: Optional[UUID] = None
    description: Optional[str] = None


class UpdateClassGroupCommand(BaseCommand):
    """更新班级命令。"""
    class_group_id: UUID
    grade_id: Optional[UUID] = None
    name: Optional[str] = None
    code: Optional[str] = None
    student_count: Optional[int] = None
    homeroom_teacher_id: Optional[UUID] = None
    description: Optional[str] = None


class DeleteClassGroupCommand(BaseCommand):
    """删除班级命令。"""
    class_group_id: UUID


class CreateSectionCommand(BaseCommand):
    """创建教学段命令。"""
    course_id: UUID
    class_group_id: UUID
    teacher_id: UUID
    room_id: Optional[UUID] = None
    name: str
    code: str
    hours_per_week: int
    period_type: str = "regular"
    is_locked: bool = False
    notes: Optional[str] = None


class UpdateSectionCommand(BaseCommand):
    """更新教学段命令。"""
    section_id: UUID
    course_id: Optional[UUID] = None
    class_group_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    name: Optional[str] = None
    code: Optional[str] = None
    hours_per_week: Optional[int] = None
    period_type: Optional[str] = None
    is_locked: Optional[bool] = None
    notes: Optional[str] = None


class DeleteSectionCommand(BaseCommand):
    """删除教学段命令。"""
    section_id: UUID


class LockSectionCommand(BaseCommand):
    """锁定教学段命令。"""
    section_id: UUID


class UnlockSectionCommand(BaseCommand):
    """解锁教学段命令。"""
    section_id: UUID