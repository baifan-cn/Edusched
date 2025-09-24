"""学校管理相关命令。

包含创建、更新、删除学校等操作的命令定义。
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from ..base import BaseCommand


class CreateSchoolCommand(BaseCommand):
    """创建学校命令。"""
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    timezone: str = "Asia/Shanghai"
    academic_year: str
    semester: str
    is_active: bool = True


class UpdateSchoolCommand(BaseCommand):
    """更新学校命令。"""
    school_id: UUID
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    timezone: Optional[str] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    is_active: Optional[bool] = None


class DeleteSchoolCommand(BaseCommand):
    """删除学校命令。"""
    school_id: UUID


class ActivateSchoolCommand(BaseCommand):
    """激活学校命令。"""
    school_id: UUID


class DeactivateSchoolCommand(BaseCommand):
    """停用学校命令。"""
    school_id: UUID


class CreateCampusCommand(BaseCommand):
    """创建校区命令。"""
    school_id: UUID
    name: str
    code: str
    address: Optional[str] = None
    travel_time_minutes: int = 0
    is_main: bool = False


class UpdateCampusCommand(BaseCommand):
    """更新校区命令。"""
    campus_id: UUID
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    travel_time_minutes: Optional[int] = None
    is_main: Optional[bool] = None


class DeleteCampusCommand(BaseCommand):
    """删除校区命令。"""
    campus_id: UUID


class CreateBuildingCommand(BaseCommand):
    """创建建筑命令。"""
    campus_id: UUID
    name: str
    code: str
    floors: int = 1
    description: Optional[str] = None


class UpdateBuildingCommand(BaseCommand):
    """更新建筑命令。"""
    building_id: UUID
    name: Optional[str] = None
    code: Optional[str] = None
    floors: Optional[int] = None
    description: Optional[str] = None


class DeleteBuildingCommand(BaseCommand):
    """删除建筑命令。"""
    building_id: UUID


class CreateRoomCommand(BaseCommand):
    """创建教室命令。"""
    building_id: UUID
    name: str
    code: str
    floor: int
    capacity: int
    room_type: str = "classroom"
    features: dict = {}


class UpdateRoomCommand(BaseCommand):
    """更新教室命令。"""
    room_id: UUID
    name: Optional[str] = None
    code: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    room_type: Optional[str] = None
    features: Optional[dict] = None
    is_active: Optional[bool] = None


class DeleteRoomCommand(BaseCommand):
    """删除教室命令。"""
    room_id: UUID