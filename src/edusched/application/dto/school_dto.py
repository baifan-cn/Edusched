"""学校管理相关数据传输对象。

包含学校、校区、建筑、教室等实体的DTO定义。
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SchoolBaseDTO(BaseModel):
    """学校基础DTO。"""
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


class SchoolCreateDTO(SchoolBaseDTO):
    """创建学校DTO。"""
    pass


class SchoolUpdateDTO(BaseModel):
    """更新学校DTO。"""
    name: Optional[str] = Field(default=None, description="学校名称")
    code: Optional[str] = Field(default=None, description="学校代码")
    address: Optional[str] = Field(default=None, description="学校地址")
    phone: Optional[str] = Field(default=None, description="联系电话")
    email: Optional[str] = Field(default=None, description="联系邮箱")
    website: Optional[str] = Field(default=None, description="学校网站")
    timezone: Optional[str] = Field(default=None, description="时区")
    academic_year: Optional[str] = Field(default=None, description="学年")
    semester: Optional[str] = Field(default=None, description="学期")
    is_active: Optional[bool] = Field(default=None, description="是否激活")


class SchoolDTO(SchoolBaseDTO):
    """学校详情DTO。"""
    id: UUID = Field(description="学校ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    campus_count: int = Field(default=0, description="校区数量")

    class Config:
        from_attributes = True


class CampusBaseDTO(BaseModel):
    """校区基础DTO。"""
    name: str = Field(description="校区名称")
    code: str = Field(description="校区代码")
    address: Optional[str] = Field(default=None, description="校区地址")
    travel_time_minutes: int = Field(default=0, description="到主校区行程时间(分钟)")
    is_main: bool = Field(default=False, description="是否为主校区")


class CampusCreateDTO(CampusBaseDTO):
    """创建校区DTO。"""
    school_id: UUID = Field(description="所属学校ID")


class CampusUpdateDTO(BaseModel):
    """更新校区DTO。"""
    name: Optional[str] = Field(default=None, description="校区名称")
    code: Optional[str] = Field(default=None, description="校区代码")
    address: Optional[str] = Field(default=None, description="校区地址")
    travel_time_minutes: Optional[int] = Field(default=None, description="到主校区行程时间(分钟)")
    is_main: Optional[bool] = Field(default=None, description="是否为主校区")


class CampusDTO(CampusBaseDTO):
    """校区详情DTO。"""
    id: UUID = Field(description="校区ID")
    school_id: UUID = Field(description="所属学校ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    school_name: Optional[str] = Field(default=None, description="学校名称")
    building_count: int = Field(default=0, description="建筑数量")

    class Config:
        from_attributes = True


class BuildingBaseDTO(BaseModel):
    """建筑基础DTO。"""
    name: str = Field(description="建筑名称")
    code: str = Field(description="建筑代码")
    floors: int = Field(default=1, description="楼层数")
    description: Optional[str] = Field(default=None, description="建筑描述")


class BuildingCreateDTO(BuildingBaseDTO):
    """创建建筑DTO。"""
    campus_id: UUID = Field(description="所属校区ID")


class BuildingUpdateDTO(BaseModel):
    """更新建筑DTO。"""
    name: Optional[str] = Field(default=None, description="建筑名称")
    code: Optional[str] = Field(default=None, description="建筑代码")
    floors: Optional[int] = Field(default=None, description="楼层数")
    description: Optional[str] = Field(default=None, description="建筑描述")


class BuildingDTO(BuildingBaseDTO):
    """建筑详情DTO。"""
    id: UUID = Field(description="建筑ID")
    campus_id: UUID = Field(description="所属校区ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    campus_name: Optional[str] = Field(default=None, description="校区名称")
    room_count: int = Field(default=0, description="教室数量")

    class Config:
        from_attributes = True


class RoomBaseDTO(BaseModel):
    """教室基础DTO。"""
    name: str = Field(description="教室名称")
    code: str = Field(description="教室代码")
    floor: int = Field(description="楼层")
    capacity: int = Field(description="容纳人数")
    room_type: str = Field(default="classroom", description="教室类型")
    features: Dict[str, bool] = Field(default_factory=dict, description="教室特性")
    is_active: bool = Field(default=True, description="是否可用")


class RoomCreateDTO(RoomBaseDTO):
    """创建教室DTO。"""
    building_id: UUID = Field(description="所属建筑ID")


class RoomUpdateDTO(BaseModel):
    """更新教室DTO。"""
    name: Optional[str] = Field(default=None, description="教室名称")
    code: Optional[str] = Field(default=None, description="教室代码")
    floor: Optional[int] = Field(default=None, description="楼层")
    capacity: Optional[int] = Field(default=None, description="容纳人数")
    room_type: Optional[str] = Field(default=None, description="教室类型")
    features: Optional[Dict[str, bool]] = Field(default=None, description="教室特性")
    is_active: Optional[bool] = Field(default=None, description="是否可用")


class RoomDTO(RoomBaseDTO):
    """教室详情DTO。"""
    id: UUID = Field(description="教室ID")
    building_id: UUID = Field(description="所属建筑ID")
    tenant_id: str = Field(description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    created_by: Optional[str] = Field(default=None, description="创建者")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    building_name: Optional[str] = Field(default=None, description="建筑名称")
    campus_name: Optional[str] = Field(default=None, description="校区名称")
    school_name: Optional[str] = Field(default=None, description="学校名称")
    utilization_rate: float = Field(default=0.0, description="利用率")

    class Config:
        from_attributes = True


class RoomAvailabilityDTO(BaseModel):
    """教室可用性DTO。"""
    room_id: UUID = Field(description="教室ID")
    room_name: str = Field(description="教室名称")
    available_timeslots: List[UUID] = Field(description="可用时间段ID列表")
    utilization_rate: float = Field(description="利用率")


class SchoolSummaryDTO(BaseModel):
    """学校汇总DTO。"""
    total_schools: int = Field(description="总学校数")
    active_schools: int = Field(description="激活学校数")
    total_campuses: int = Field(description="总校区数")
    total_buildings: int = Field(description="总建筑数")
    total_rooms: int = Field(description="总教室数")
    active_rooms: int = Field(description="可用教室数")
    total_capacity: int = Field(description="总容纳人数")
    average_utilization: float = Field(description="平均利用率")


class SchoolWithDetailsDTO(SchoolDTO):
    """带详情的学校DTO。"""
    campuses: List[CampusDTO] = Field(default_factory=list, description="校区列表")
    buildings: List[BuildingDTO] = Field(default_factory=list, description="建筑列表")
    rooms: List[RoomDTO] = Field(default_factory=list, description="教室列表")


class CampusWithDetailsDTO(CampusDTO):
    """带详情的校区DTO。"""
    school: Optional[SchoolDTO] = Field(default=None, description="学校信息")
    buildings: List[BuildingDTO] = Field(default_factory=list, description="建筑列表")
    rooms: List[RoomDTO] = Field(default_factory=list, description="教室列表")


class BuildingWithDetailsDTO(BuildingDTO):
    """带详情的建筑DTO。"""
    campus: Optional[CampusDTO] = Field(default=None, description="校区信息")
    rooms: List[RoomDTO] = Field(default_factory=list, description="教室列表")