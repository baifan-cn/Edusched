"""教师管理相关查询。

包含获取教师信息、工作量、可用性等查询定义。
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, time

from ..base import BaseQuery


class GetTeacherByIdQuery(BaseQuery):
    """根据ID获取教师查询。"""
    teacher_id: UUID


class GetTeachersQuery(BaseQuery):
    """获取教师列表查询。"""
    keyword: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    has_availability: Optional[bool] = None


class GetTeacherWorkloadQuery(BaseQuery):
    """获取教师工作量查询。"""
    teacher_id: UUID
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class GetTeacherAvailabilityQuery(BaseQuery):
    """获取教师可用性查询。"""
    teacher_id: UUID
    week_day: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class GetAvailableTeachersQuery(BaseQuery):
    """获取可用教师查询。"""
    timeslot_id: UUID
    subject_id: Optional[UUID] = None
    week_pattern_id: Optional[UUID] = None
    week_number: Optional[int] = None
    department: Optional[str] = None


class GetTeacherScheduleQuery(BaseQuery):
    """获取教师课程表查询。"""
    teacher_id: UUID
    calendar_id: Optional[UUID] = None
    week_number: Optional[int] = None
    week_pattern_id: Optional[UUID] = None


class GetTeachersByDepartmentQuery(BaseQuery):
    """按部门获取教师查询。"""
    department: str
    is_active: Optional[bool] = None


class GetTeacherStatsQuery(BaseQuery):
    """获取教师统计信息查询。"""
    department: Optional[str] = None
    is_active: Optional[bool] = None


class CheckTeacherAvailabilityQuery(BaseQuery):
    """检查教师可用性查询。"""
    teacher_id: UUID
    timeslot_ids: List[UUID]
    week_pattern_id: Optional[UUID] = None
    exclude_assignment_id: Optional[UUID] = None