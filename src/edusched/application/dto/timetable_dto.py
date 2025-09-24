"""时间表管理相关数据传输对象。

包含时间表、分配、调度任务等实体的DTO定义。
"""

from datetime import datetime, time
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TimeslotBaseDTO(BaseModel):
    """时间段基础DTO。"""
    week_day: str = Field(description="星期")
    start_time: time = Field(description="开始时间")
    end_time: time = Field(description="结束时间")
    period_number: int = Field(description="课时序号")
    is_break: bool = Field(default=False, description="是否为休息时间")
    description: Optional[str] = Field(default=None, description="时间段描述")


class TimeslotCreateDTO(TimeslotBaseDTO):
    """创建时间段DTO。"""
    pass


class TimeslotUpdateDTO(BaseModel):
    """更新时间段DTO。"""
    week_day: Optional[str] = Field(default=None, description="星期")
    start_time: Optional[time] = Field(default=None, description="开始时间")
    end_time: Optional[time] = Field(default=None, description="结束时间")
    period_number: Optional[int] = Field(default=None, description="课时序号")
    is_break: Optional[bool] = Field(default=None, description="是否为休息时间")
    description: Optional[str] = Field(default=None, description="时间段描述")


class TimeslotDTO(TimeslotBaseDTO):
    """时间段详情DTO。"""
    id: UUID = Field(description="时间段ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")

    class Config:
        from_attributes = True


class WeekPatternBaseDTO(BaseModel):
    """周模式基础DTO。"""
    name: str = Field(description="周模式名称")
    description: Optional[str] = Field(default=None, description="周模式描述")
    is_alternating: bool = Field(default=False, description="是否交替周")
    weeks: List[int] = Field(description="适用的周数")


class WeekPatternCreateDTO(WeekPatternBaseDTO):
    """创建周模式DTO。"""
    pass


class WeekPatternUpdateDTO(BaseModel):
    """更新周模式DTO。"""
    name: Optional[str] = Field(default=None, description="周模式名称")
    description: Optional[str] = Field(default=None, description="周模式描述")
    is_alternating: Optional[bool] = Field(default=None, description="是否交替周")
    weeks: Optional[List[int]] = Field(default=None, description="适用的周数")


class WeekPatternDTO(WeekPatternBaseDTO):
    """周模式详情DTO。"""
    id: UUID = Field(description="周模式ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")

    class Config:
        from_attributes = True


class CalendarBaseDTO(BaseModel):
    """日历基础DTO。"""
    name: str = Field(description="日历名称")
    academic_year: str = Field(description="学年")
    semester: str = Field(description="学期")
    start_date: datetime = Field(description="开始日期")
    end_date: datetime = Field(description="结束日期")
    week_patterns: List[UUID] = Field(default_factory=list, description="周模式ID列表")
    holidays: List[datetime] = Field(default_factory=list, description="节假日列表")
    is_active: bool = Field(default=True, description="是否激活")


class CalendarCreateDTO(CalendarBaseDTO):
    """创建日历DTO。"""
    school_id: UUID = Field(description="学校ID")


class CalendarUpdateDTO(BaseModel):
    """更新日历DTO。"""
    name: Optional[str] = Field(default=None, description="日历名称")
    academic_year: Optional[str] = Field(default=None, description="学年")
    semester: Optional[str] = Field(default=None, description="学期")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    week_patterns: Optional[List[UUID]] = Field(default=None, description="周模式ID列表")
    holidays: Optional[List[datetime]] = Field(default=None, description="节假日列表")
    is_active: Optional[bool] = Field(default=None, description="是否激活")


class CalendarDTO(CalendarBaseDTO):
    """日历详情DTO。"""
    id: UUID = Field(description="日历ID")
    school_id: UUID = Field(description="学校ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    school_name: Optional[str] = Field(default=None, description="学校名称")

    class Config:
        from_attributes = True


class ConstraintBaseDTO(BaseModel):
    """约束基础DTO。"""
    name: str = Field(description="约束名称")
    description: str = Field(description="约束描述")
    constraint_type: str = Field(description="约束类型")
    weight: float = Field(description="权重")
    parameters: Dict = Field(default_factory=dict, description="约束参数")
    is_active: bool = Field(default=True, description="是否激活")


class ConstraintCreateDTO(ConstraintBaseDTO):
    """创建约束DTO。"""
    pass


class ConstraintUpdateDTO(BaseModel):
    """更新约束DTO。"""
    name: Optional[str] = Field(default=None, description="约束名称")
    description: Optional[str] = Field(default=None, description="约束描述")
    constraint_type: Optional[str] = Field(default=None, description="约束类型")
    weight: Optional[float] = Field(default=None, description="权重")
    parameters: Optional[Dict] = Field(default=None, description="约束参数")
    is_active: Optional[bool] = Field(default=None, description="是否激活")


class ConstraintDTO(ConstraintBaseDTO):
    """约束详情DTO。"""
    id: UUID = Field(description="约束ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")

    class Config:
        from_attributes = True


class TimetableBaseDTO(BaseModel):
    """时间表基础DTO。"""
    name: str = Field(description="时间表名称")
    description: Optional[str] = Field(default=None, description="时间表描述")
    status: str = Field(default="draft", description="调度状态")
    constraints: List[UUID] = Field(default_factory=list, description="约束ID列表")
    metadata: Dict = Field(default_factory=dict, description="元数据")


class TimetableCreateDTO(TimetableBaseDTO):
    """创建时间表DTO。"""
    calendar_id: UUID = Field(description="日历ID")


class TimetableUpdateDTO(BaseModel):
    """更新时间表DTO。"""
    name: Optional[str] = Field(default=None, description="时间表名称")
    description: Optional[str] = Field(default=None, description="时间表描述")
    constraints: Optional[List[UUID]] = Field(default=None, description="约束ID列表")


class TimetableDTO(TimetableBaseDTO):
    """时间表详情DTO。"""
    id: UUID = Field(description="时间表ID")
    calendar_id: UUID = Field(description="日历ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    published_at: Optional[datetime] = Field(default=None, description="发布时间")
    published_by: Optional[str] = Field(default=None, description="发布者")
    calendar_name: Optional[str] = Field(default=None, description="日历名称")
    assignment_count: int = Field(default=0, description="分配数量")
    latest_job: Optional[Dict] = Field(default=None, description="最新调度任务")

    class Config:
        from_attributes = True


class AssignmentBaseDTO(BaseModel):
    """分配基础DTO。"""
    section_id: UUID = Field(description="教学段ID")
    timeslot_id: UUID = Field(description="时间段ID")
    room_id: UUID = Field(description="教室ID")
    week_pattern_id: Optional[UUID] = Field(default=None, description="周模式ID")
    is_locked: bool = Field(default=False, description="是否锁定")
    notes: Optional[str] = Field(default=None, description="备注")


class AssignmentCreateDTO(AssignmentBaseDTO):
    """创建分配DTO。"""
    timetable_id: UUID = Field(description="时间表ID")


class AssignmentUpdateDTO(BaseModel):
    """更新分配DTO。"""
    section_id: Optional[UUID] = Field(default=None, description="教学段ID")
    timeslot_id: Optional[UUID] = Field(default=None, description="时间段ID")
    room_id: Optional[UUID] = Field(default=None, description="教室ID")
    week_pattern_id: Optional[UUID] = Field(default=None, description="周模式ID")
    is_locked: Optional[bool] = Field(default=None, description="是否锁定")
    notes: Optional[str] = Field(default=None, description="备注")


class AssignmentDTO(AssignmentBaseDTO):
    """分配详情DTO。"""
    id: UUID = Field(description="分配ID")
    timetable_id: UUID = Field(description="时间表ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    section_name: Optional[str] = Field(default=None, description="教学段名称")
    teacher_name: Optional[str] = Field(default=None, description="教师姓名")
    room_name: Optional[str] = Field(default=None, description="教室名称")
    timeslot_info: Optional[Dict] = Field(default=None, description="时间段信息")

    class Config:
        from_attributes = True


class SchedulingJobDTO(BaseModel):
    """调度任务DTO。"""
    id: UUID = Field(description="任务ID")
    timetable_id: UUID = Field(description="时间表ID")
    status: str = Field(description="任务状态")
    progress: float = Field(description="进度(0-1)")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    result_metadata: Dict = Field(default_factory=dict, description="结果元数据")
    worker_id: Optional[str] = Field(default=None, description="工作进程ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class TimetableStatsDTO(BaseModel):
    """时间表统计DTO。"""
    timetable_id: UUID = Field(description="时间表ID")
    total_sections: int = Field(description="总教学段数")
    assigned_sections: int = Field(description="已分配教学段数")
    unassigned_sections: int = Field(description="未分配教学段数")
    locked_assignments: int = Field(description="锁定分配数")
    teacher_conflicts: int = Field(description="教师冲突数")
    room_conflicts: int = Field(description="教室冲突数")
    class_conflicts: int = Field(description="班级冲突数")
    constraint_violations: int = Field(description="约束违反数")
    satisfaction_score: float = Field(description="满足度分数")


class ConflictDTO(BaseModel):
    """冲突DTO。"""
    conflict_id: str = Field(description="冲突ID")
    conflict_type: str = Field(description="冲突类型")
    description: str = Field(description="冲突描述")
    severity: str = Field(description="严重程度")
    entities: List[Dict] = Field(description="相关实体")
    suggestions: List[str] = Field(default_factory=list, description="解决建议")


class ScheduleGridDTO(BaseModel):
    """课程表网格DTO。"""
    headers: List[str] = Field(description="表头")
    rows: List[Dict] = Field(description="行数据")
    metadata: Dict = Field(default_factory=dict, description="元数据")


class TimetablePublishDTO(BaseModel):
    """时间表发布DTO。"""
    timetable_id: UUID = Field(description="时间表ID")
    publish_date: datetime = Field(description="发布日期")
    published_by: str = Field(description="发布者")
    notes: Optional[str] = Field(default=None, description="备注")