"""时间表管理相关命令。

包含创建、更新、删除时间表等操作的命令定义。
"""

from datetime import datetime, time
from typing import List, Optional
from uuid import UUID

from ..base import BaseCommand


class CreateCalendarCommand(BaseCommand):
    """创建日历命令。"""
    school_id: UUID
    name: str
    academic_year: str
    semester: str
    start_date: datetime
    end_date: datetime
    week_patterns: List[UUID] = []
    holidays: List[datetime] = []
    is_active: bool = True


class UpdateCalendarCommand(BaseCommand):
    """更新日历命令。"""
    calendar_id: UUID
    name: Optional[str] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    week_patterns: Optional[List[UUID]] = None
    holidays: Optional[List[datetime]] = None
    is_active: Optional[bool] = None


class DeleteCalendarCommand(BaseCommand):
    """删除日历命令。"""
    calendar_id: UUID


class CreateTimeslotCommand(BaseCommand):
    """创建时间段命令。"""
    week_day: str
    start_time: time
    end_time: time
    period_number: int
    is_break: bool = False
    description: Optional[str] = None


class UpdateTimeslotCommand(BaseCommand):
    """更新时间段命令。"""
    timeslot_id: UUID
    week_day: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    period_number: Optional[int] = None
    is_break: Optional[bool] = None
    description: Optional[str] = None


class DeleteTimeslotCommand(BaseCommand):
    """删除时间段命令。"""
    timeslot_id: UUID


class CreateWeekPatternCommand(BaseCommand):
    """创建周模式命令。"""
    name: str
    description: Optional[str] = None
    is_alternating: bool = False
    weeks: List[int]


class UpdateWeekPatternCommand(BaseCommand):
    """更新周模式命令。"""
    week_pattern_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    is_alternating: Optional[bool] = None
    weeks: Optional[List[int]] = None


class DeleteWeekPatternCommand(BaseCommand):
    """删除周模式命令。"""
    week_pattern_id: UUID


class CreateConstraintCommand(BaseCommand):
    """创建约束命令。"""
    name: str
    description: str
    constraint_type: str
    weight: float
    parameters: dict = {}
    is_active: bool = True


class UpdateConstraintCommand(BaseCommand):
    """更新约束命令。"""
    constraint_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    constraint_type: Optional[str] = None
    weight: Optional[float] = None
    parameters: Optional[dict] = None
    is_active: Optional[bool] = None


class DeleteConstraintCommand(BaseCommand):
    """删除约束命令。"""
    constraint_id: UUID


class CreateTimetableCommand(BaseCommand):
    """创建时间表命令。"""
    calendar_id: UUID
    name: str
    description: Optional[str] = None
    constraints: List[UUID] = []


class UpdateTimetableCommand(BaseCommand):
    """更新时间表命令。"""
    timetable_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    constraints: Optional[List[UUID]] = None


class DeleteTimetableCommand(BaseCommand):
    """删除时间表命令。"""
    timetable_id: UUID


class CreateAssignmentCommand(BaseCommand):
    """创建分配命令。"""
    timetable_id: UUID
    section_id: UUID
    timeslot_id: UUID
    room_id: UUID
    week_pattern_id: Optional[UUID] = None
    is_locked: bool = False
    notes: Optional[str] = None


class UpdateAssignmentCommand(BaseCommand):
    """更新分配命令。"""
    assignment_id: UUID
    section_id: Optional[UUID] = None
    timeslot_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    week_pattern_id: Optional[UUID] = None
    is_locked: Optional[bool] = None
    notes: Optional[str] = None


class DeleteAssignmentCommand(BaseCommand):
    """删除分配命令。"""
    assignment_id: UUID


class LockAssignmentCommand(BaseCommand):
    """锁定分配命令。"""
    assignment_id: UUID


class UnlockAssignmentCommand(BaseCommand):
    """解锁分配命令。"""
    assignment_id: UUID


class StartSchedulingCommand(BaseCommand):
    """开始调度命令。"""
    timetable_id: UUID
    max_iterations: int = 1000
    timeout_seconds: int = 300


class StopSchedulingCommand(BaseCommand):
    """停止调度命令。"""
    job_id: UUID


class PublishTimetableCommand(BaseCommand):
    """发布时间表命令。"""
    timetable_id: UUID


class UnpublishTimetableCommand(BaseCommand):
    """取消发布时间表命令。"""
    timetable_id: UUID