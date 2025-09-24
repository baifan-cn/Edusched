"""教师管理相关数据传输对象。

包含教师相关实体的DTO定义。
"""

from datetime import datetime, time
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TeacherBaseDTO(BaseModel):
    """教师基础DTO。"""
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


class TeacherCreateDTO(TeacherBaseDTO):
    """创建教师DTO。"""
    pass


class TeacherUpdateDTO(BaseModel):
    """更新教师DTO。"""
    employee_id: Optional[str] = Field(default=None, description="工号")
    name: Optional[str] = Field(default=None, description="教师姓名")
    email: Optional[str] = Field(default=None, description="邮箱")
    phone: Optional[str] = Field(default=None, description="电话")
    department: Optional[str] = Field(default=None, description="所属部门")
    title: Optional[str] = Field(default=None, description="职称")
    max_hours_per_day: Optional[int] = Field(default=None, description="每日最大课时数")
    max_hours_per_week: Optional[int] = Field(default=None, description="每周最大课时数")
    preferred_time_slots: Optional[List[time]] = Field(default=None, description="偏好时间段")
    unavailable_time_slots: Optional[List[time]] = Field(default=None, description="不可用时间段")
    is_active: Optional[bool] = Field(default=None, description="是否在职")


class TeacherDTO(TeacherBaseDTO):
    """教师详情DTO。"""
    id: UUID = Field(description="教师ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")

    class Config:
        from_attributes = True


class TeacherWorkloadDTO(BaseModel):
    """教师工作量DTO。"""
    teacher_id: UUID = Field(description="教师ID")
    teacher_name: str = Field(description="教师姓名")
    department: str = Field(description="部门")
    assigned_hours: int = Field(description="已分配课时")
    max_hours_per_week: int = Field(description="每周最大课时")
    utilization_rate: float = Field(description="利用率")
    courses: List[Dict] = Field(default_factory=list, description="课程列表")


class TeacherAvailabilityDTO(BaseModel):
    """教师可用性DTO。"""
    teacher_id: UUID = Field(description="教师ID")
    teacher_name: str = Field(description="教师姓名")
    preferred_time_slots: List[time] = Field(description="偏好时间段")
    unavailable_time_slots: List[time] = Field(description="不可用时间段")
    available_days: List[str] = Field(description="可用星期")


class TeacherScheduleDTO(BaseModel):
    """教师课程表DTO。"""
    teacher_id: UUID = Field(description="教师ID")
    teacher_name: str = Field(description="教师姓名")
    week_number: int = Field(description="周数")
    schedule: List[Dict] = Field(description="课程表详情")


class TeacherSummaryDTO(BaseModel):
    """教师汇总DTO。"""
    total_teachers: int = Field(description="总教师数")
    active_teachers: int = Field(description="在职教师数")
    department_stats: Dict[str, int] = Field(default_factory=dict, description="部门统计")
    average_workload: float = Field(description="平均工作量")
    max_workload_teachers: List[Dict] = Field(default_factory=list, description="工作量最大教师")


class TeacherWithDetailsDTO(TeacherDTO):
    """带详情的教师DTO。"""
    workload: Optional[TeacherWorkloadDTO] = Field(default=None, description="工作量")
    availability: Optional[TeacherAvailabilityDTO] = Field(default=None, description="可用性")
    schedule: Optional[TeacherScheduleDTO] = Field(default=None, description="课程表")
    sections: List[Dict] = Field(default_factory=list, description="教学段")


class SetTeacherAvailabilityDTO(BaseModel):
    """设置教师可用性DTO。"""
    preferred_time_slots: List[time] = Field(description="偏好时间段")
    unavailable_time_slots: List[time] = Field(description="不可用时间段")


class UpdateTeacherWorkloadDTO(BaseModel):
    """更新教师工作量限制DTO。"""
    max_hours_per_day: int = Field(description="每日最大课时数")
    max_hours_per_week: int = Field(description="每周最大课时数")


class TeacherFilterDTO(BaseModel):
    """教师过滤DTO。"""
    keyword: Optional[str] = Field(default=None, description="关键词")
    department: Optional[str] = Field(default=None, description="部门")
    title: Optional[str] = Field(default=None, description="职称")
    is_active: Optional[bool] = Field(default=None, description="是否在职")
    has_availability: Optional[bool] = Field(default=None, description="是否有可用时间")
    min_workload: Optional[float] = Field(default=None, description="最小工作量")
    max_workload: Optional[float] = Field(default=None, description="最大工作量")