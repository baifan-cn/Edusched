"""学校管理相关查询。

包含获取学校、校区、建筑、教室等信息的查询定义。
"""

from typing import Optional
from uuid import UUID

from ..base import BaseQuery


class GetSchoolByIdQuery(BaseQuery):
    """根据ID获取学校查询。"""
    school_id: UUID


class GetSchoolsQuery(BaseQuery):
    """获取学校列表查询。"""
    keyword: Optional[str] = None
    is_active: Optional[bool] = None


class GetCampusesBySchoolQuery(BaseQuery):
    """获取学校的校区列表查询。"""
    school_id: UUID


class GetCampusByIdQuery(BaseQuery):
    """根据ID获取校区查询。"""
    campus_id: UUID


class GetBuildingsByCampusQuery(BaseQuery):
    """获取校区的建筑列表查询。"""
    campus_id: UUID


class GetBuildingByIdQuery(BaseQuery):
    """根据ID获取建筑查询。"""
    building_id: UUID


class GetRoomsByBuildingQuery(BaseQuery):
    """获取建筑的教室列表查询。"""
    building_id: UUID
    room_type: Optional[str] = None
    min_capacity: Optional[int] = None
    is_active: Optional[bool] = None


class GetRoomByIdQuery(BaseQuery):
    """根据ID获取教室查询。"""
    room_id: UUID


class SearchRoomsQuery(BaseQuery):
    """搜索教室查询。"""
    keyword: Optional[str] = None
    room_type: Optional[str] = None
    min_capacity: Optional[int] = None
    features: Optional[list] = None
    building_id: Optional[UUID] = None
    campus_id: Optional[UUID] = None
    school_id: Optional[UUID] = None


class GetAvailableRoomsQuery(BaseQuery):
    """获取可用教室查询。"""
    timeslot_id: UUID
    week_pattern_id: Optional[UUID] = None
    week_number: Optional[int] = None
    min_capacity: Optional[int] = None
    room_type: Optional[str] = None
    required_features: Optional[list] = None