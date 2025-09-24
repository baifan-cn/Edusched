"""教师管理相关命令。

包含创建、更新、删除教师等操作的命令定义。
"""

from datetime import time
from typing import List, Optional
from uuid import UUID

from ..base import BaseCommand


class CreateTeacherCommand(BaseCommand):
    """创建教师命令。"""
    employee_id: str
    name: str
    email: str
    phone: Optional[str] = None
    department: str
    title: Optional[str] = None
    max_hours_per_day: int = 8
    max_hours_per_week: int = 40
    preferred_time_slots: List[time] = []
    unavailable_time_slots: List[time] = []
    is_active: bool = True


class UpdateTeacherCommand(BaseCommand):
    """更新教师命令。"""
    teacher_id: UUID
    employee_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    max_hours_per_day: Optional[int] = None
    max_hours_per_week: Optional[int] = None
    preferred_time_slots: Optional[List[time]] = None
    unavailable_time_slots: Optional[List[time]] = None
    is_active: Optional[bool] = None


class DeleteTeacherCommand(BaseCommand):
    """删除教师命令。"""
    teacher_id: UUID


class SetTeacherAvailabilityCommand(BaseCommand):
    """设置教师可用性命令。"""
    teacher_id: UUID
    preferred_time_slots: List[time]
    unavailable_time_slots: List[time]


class UpdateTeacherWorkloadCommand(BaseCommand):
    """更新教师工作量限制命令。"""
    teacher_id: UUID
    max_hours_per_day: int
    max_hours_per_week: int