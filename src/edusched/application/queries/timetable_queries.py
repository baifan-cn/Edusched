"""时间表管理相关查询。

包含获取时间表、分配、调度任务等信息的查询定义。
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, date

from ..base import BaseQuery


class GetCalendarByIdQuery(BaseQuery):
    """根据ID获取日历查询。"""
    calendar_id: UUID


class GetCalendarsQuery(BaseQuery):
    """获取日历列表查询。"""
    school_id: Optional[UUID] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    is_active: Optional[bool] = None


class GetTimeslotByIdQuery(BaseQuery):
    """根据ID获取时间段查询。"""
    timeslot_id: UUID


class GetTimeslotsQuery(BaseQuery):
    """获取时间段列表查询。"""
    week_day: Optional[str] = None
    is_break: Optional[bool] = None


class GetWeekPatternByIdQuery(BaseQuery):
    """根据ID获取周模式查询。"""
    week_pattern_id: UUID


class GetWeekPatternsQuery(BaseQuery):
    """获取周模式列表查询。"""
    is_alternating: Optional[bool] = None


class GetConstraintByIdQuery(BaseQuery):
    """根据ID获取约束查询。"""
    constraint_id: UUID


class GetConstraintsQuery(BaseQuery):
    """获取约束列表查询。"""
    constraint_type: Optional[str] = None
    is_active: Optional[bool] = None


class GetTimetableByIdQuery(BaseQuery):
    """根据ID获取时间表查询。"""
    timetable_id: UUID


class GetTimetablesQuery(BaseQuery):
    """获取时间表列表查询。"""
    calendar_id: Optional[UUID] = None
    status: Optional[str] = None


class GetAssignmentByIdQuery(BaseQuery):
    """根据ID获取分配查询。"""
    assignment_id: UUID


class GetAssignmentsQuery(BaseQuery):
    """获取分配列表查询。"""
    timetable_id: UUID
    section_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    timeslot_id: Optional[UUID] = None
    is_locked: Optional[bool] = None


class GetSchedulingJobByIdQuery(BaseQuery):
    """根据ID获取调度任务查询。"""
    job_id: UUID


class GetSchedulingJobsQuery(BaseQuery):
    """获取调度任务列表查询。"""
    timetable_id: Optional[UUID] = None
    status: Optional[str] = None


class GetTimetableByClassGroupQuery(BaseQuery):
    """获取班级的时间表查询。"""
    class_group_id: UUID
    calendar_id: UUID
    week_number: Optional[int] = None
    week_pattern_id: Optional[UUID] = None


class GetTimetableByTeacherQuery(BaseQuery):
    """获取教师的时间表查询。"""
    teacher_id: UUID
    calendar_id: UUID
    week_number: Optional[int] = None
    week_pattern_id: Optional[UUID] = None


class GetTimetableByRoomQuery(BaseQuery):
    """获取教室的时间表查询。"""
    room_id: UUID
    calendar_id: UUID
    week_number: Optional[int] = None
    week_pattern_id: Optional[UUID] = None


class GetConflictsQuery(BaseQuery):
    """获取冲突查询。"""
    timetable_id: UUID
    conflict_type: Optional[str] = None


class GetTimetableStatsQuery(BaseQuery):
    """获取时间表统计信息查询。"""
    timetable_id: UUID


class GetPublishedTimetablesQuery(BaseQuery):
    """获取已发布的时间表查询。"""
    school_id: Optional[UUID] = None
    calendar_id: Optional[UUID] = None
    publish_date: Optional[datetime] = None


class CheckTimeslotAvailabilityQuery(BaseQuery):
    """检查时间段可用性查询。"""
    timeslot_id: UUID
    week_pattern_id: Optional[UUID] = None
    week_number: Optional[int] = None
    exclude_assignment_id: Optional[UUID] = None