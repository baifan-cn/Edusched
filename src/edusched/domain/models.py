"""领域模型定义。

包含Edusched系统的核心业务实体和值对象。
"""

from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class WeekDay(str, Enum):
    """星期枚举。"""
    
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class PeriodType(str, Enum):
    """课时类型枚举。"""
    
    REGULAR = "regular"  # 常规课时
    LAB = "lab"  # 实验课时
    PHYSICAL = "physical"  # 体育课时
    ART = "art"  # 艺术课时
    SPECIAL = "special"  # 特殊课时


class ConstraintType(str, Enum):
    """约束类型枚举。"""
    
    HARD = "hard"  # 硬约束
    SOFT = "soft"  # 软约束


class SchedulingStatus(str, Enum):
    """调度状态枚举。"""
    
    DRAFT = "draft"  # 草稿
    RUNNING = "running"  # 运行中
    FEASIBLE = "feasible"  # 可行
    OPTIMIZED = "optimized"  # 已优化
    PUBLISHED = "published"  # 已发布
    FAILED = "failed"  # 失败


class BaseEntity(BaseModel):
    """基础实体类。"""
    
    id: UUID = Field(default_factory=uuid4, description="实体ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class School(BaseEntity):
    """学校实体。"""
    
    name: str = Field(description="学校名称")
    code: str = Field(description="学校代码")
    address: Optional[str] = Field(default=None, description="学校地址")
    phone: Optional[str] = Field(default=None, description="联系电话")
    email: Optional[str] = Field(default=None, description="联系邮箱")
    website: Optional[str] = Field(default=None, description="学校网站")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    academic_year: str = Field(description="学年")
    semester: str = Field(description="学期")
    is_active: bool = Field(default=True, description="是否激活")


class Campus(BaseEntity):
    """校区实体。"""
    
    school_id: UUID = Field(description="所属学校ID")
    name: str = Field(description="校区名称")
    code: str = Field(description="校区代码")
    address: Optional[str] = Field(default=None, description="校区地址")
    travel_time_minutes: int = Field(default=0, description="到主校区行程时间(分钟)")
    is_main: bool = Field(default=False, description="是否为主校区")


class Building(BaseEntity):
    """建筑实体。"""
    
    campus_id: UUID = Field(description="所属校区ID")
    name: str = Field(description="建筑名称")
    code: str = Field(description="建筑代码")
    floors: int = Field(default=1, description="楼层数")
    description: Optional[str] = Field(default=None, description="建筑描述")


class Room(BaseEntity):
    """教室实体。"""
    
    building_id: UUID = Field(description="所属建筑ID")
    name: str = Field(description="教室名称")
    code: str = Field(description="教室代码")
    floor: int = Field(description="楼层")
    capacity: int = Field(description="容纳人数")
    room_type: str = Field(default="classroom", description="教室类型")
    features: Dict[str, Any] = Field(default_factory=dict, description="教室特性")
    is_active: bool = Field(default=True, description="是否可用")
    
    @field_validator("features")
    @classmethod
    def validate_features(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """验证教室特性。"""
        allowed_features = {
            "projector", "whiteboard", "computer", "lab_equipment",
            "audio_system", "air_conditioning", "wheelchair_accessible"
        }
        for key in v.keys():
            if key not in allowed_features:
                raise ValueError(f"不支持的教室特性: {key}")
        return v


class Teacher(BaseEntity):
    """教师实体。"""
    
    employee_id: str = Field(description="工号")
    name: str = Field(description="教师姓名")
    email: str = Field(description="邮箱")
    phone: Optional[str] = Field(default=None, description="电话")
    department: str = Field(description="所属部门")
    title: Optional[str] = Field(default=None, description="职称")
    max_hours_per_day: int = Field(default=8, description="每日最大课时数")
    max_hours_per_week: int = Field(default=40, description="每周最大课时数")
    preferred_time_slots: List[time] = Field(default_factory=list, description="偏好时间段")
    unavailable_time_slots: List[time] = Field(default_factory=list, description="不可用时间段")
    is_active: bool = Field(default=True, description="是否在职")


class Subject(BaseEntity):
    """学科实体。"""
    
    name: str = Field(description="学科名称")
    code: str = Field(description="学科代码")
    category: str = Field(description="学科类别")
    description: Optional[str] = Field(default=None, description="学科描述")
    is_active: bool = Field(default=True, description="是否激活")


class Course(BaseEntity):
    """课程实体。"""
    
    subject_id: UUID = Field(description="学科ID")
    name: str = Field(description="课程名称")
    code: str = Field(description="课程代码")
    description: Optional[str] = Field(default=None, description="课程描述")
    credits: Decimal = Field(description="学分")
    hours_per_week: int = Field(description="每周课时数")
    total_hours: int = Field(description="总课时数")
    is_active: bool = Field(default=True, description="是否激活")


class Grade(BaseEntity):
    """年级实体。"""
    
    name: str = Field(description="年级名称")
    code: str = Field(description="年级代码")
    level: int = Field(description="年级级别")
    description: Optional[str] = Field(default=None, description="年级描述")


class ClassGroup(BaseEntity):
    """班级实体。"""
    
    grade_id: UUID = Field(description="年级ID")
    name: str = Field(description="班级名称")
    code: str = Field(description="班级代码")
    student_count: int = Field(description="学生人数")
    homeroom_teacher_id: Optional[UUID] = Field(default=None, description="班主任ID")
    description: Optional[str] = Field(default=None, description="班级描述")


class Section(BaseEntity):
    """教学段实体。"""
    
    course_id: UUID = Field(description="课程ID")
    class_group_id: UUID = Field(description="班级ID")
    teacher_id: UUID = Field(description="教师ID")
    room_id: Optional[UUID] = Field(default=None, description="教室ID")
    name: str = Field(description="教学段名称")
    code: str = Field(description="教学段代码")
    hours_per_week: int = Field(description="每周课时数")
    period_type: PeriodType = Field(default=PeriodType.REGULAR, description="课时类型")
    is_locked: bool = Field(default=False, description="是否锁定")
    notes: Optional[str] = Field(default=None, description="备注")


class Timeslot(BaseEntity):
    """时间段实体。"""
    
    week_day: WeekDay = Field(description="星期")
    start_time: time = Field(description="开始时间")
    end_time: time = Field(description="结束时间")
    period_number: int = Field(description="课时序号")
    is_break: bool = Field(default=False, description="是否为休息时间")
    description: Optional[str] = Field(default=None, description="时间段描述")
    
    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: time, info: Any) -> time:
        """验证结束时间必须晚于开始时间。"""
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("结束时间必须晚于开始时间")
        return v


class WeekPattern(BaseEntity):
    """周模式实体。"""
    
    name: str = Field(description="周模式名称")
    description: Optional[str] = Field(default=None, description="周模式描述")
    is_alternating: bool = Field(default=False, description="是否交替周")
    weeks: List[int] = Field(description="适用的周数")


class Calendar(BaseEntity):
    """日历实体。"""
    
    school_id: UUID = Field(description="学校ID")
    name: str = Field(description="日历名称")
    academic_year: str = Field(description="学年")
    semester: str = Field(description="学期")
    start_date: datetime = Field(description="开始日期")
    end_date: datetime = Field(description="结束日期")
    week_patterns: List[UUID] = Field(default_factory=list, description="周模式ID列表")
    holidays: List[datetime] = Field(default_factory=list, description="节假日列表")
    is_active: bool = Field(default=True, description="是否激活")


class Constraint(BaseEntity):
    """约束实体。"""
    
    name: str = Field(description="约束名称")
    description: str = Field(description="约束描述")
    constraint_type: ConstraintType = Field(description="约束类型")
    weight: float = Field(description="权重")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="约束参数")
    is_active: bool = Field(default=True, description="是否激活")
    
    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """验证权重范围。"""
        if not 0 <= v <= 1:
            raise ValueError("权重必须在0到1之间")
        return v


class Timetable(BaseEntity):
    """时间表实体。"""
    
    calendar_id: UUID = Field(description="日历ID")
    name: str = Field(description="时间表名称")
    description: Optional[str] = Field(default=None, description="时间表描述")
    status: SchedulingStatus = Field(default=SchedulingStatus.DRAFT, description="调度状态")
    assignments: List["Assignment"] = Field(default_factory=list, description="分配列表")
    constraints: List[UUID] = Field(default_factory=list, description="约束ID列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    published_at: Optional[datetime] = Field(default=None, description="发布时间")
    published_by: Optional[str] = Field(default=None, description="发布者")


class Assignment(BaseEntity):
    """分配实体。"""
    
    timetable_id: UUID = Field(description="时间表ID")
    section_id: UUID = Field(description="教学段ID")
    timeslot_id: UUID = Field(description="时间段ID")
    room_id: UUID = Field(description="教室ID")
    week_pattern_id: Optional[UUID] = Field(default=None, description="周模式ID")
    is_locked: bool = Field(default=False, description="是否锁定")
    notes: Optional[str] = Field(default=None, description="备注")


class SchedulingJob(BaseEntity):
    """调度任务实体。"""
    
    timetable_id: UUID = Field(description="时间表ID")
    status: SchedulingStatus = Field(description="任务状态")
    progress: float = Field(default=0.0, description="进度(0-1)")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    result_metadata: Dict[str, Any] = Field(default_factory=dict, description="结果元数据")
    worker_id: Optional[str] = Field(default=None, description="工作进程ID")


# 解决循环引用
Assignment.model_rebuild()
Timetable.model_rebuild()