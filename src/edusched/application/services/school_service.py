"""学校管理应用服务。

协调学校相关的领域服务和基础设施操作。
"""

import logging
from typing import List, Optional

from ...domain.models import School, Campus, Building, Room
from ...domain.services import SchoolService
from ..base import CommandResult, QueryResult
from ..commands import (
    CreateSchoolCommand, UpdateSchoolCommand, DeleteSchoolCommand,
    ActivateSchoolCommand, DeactivateSchoolCommand,
    CreateCampusCommand, UpdateCampusCommand, DeleteCampusCommand,
    CreateBuildingCommand, UpdateBuildingCommand, DeleteBuildingCommand,
    CreateRoomCommand, UpdateRoomCommand, DeleteRoomCommand
)
from ..queries import (
    GetSchoolByIdQuery, GetSchoolsQuery, GetCampusesBySchoolQuery,
    GetCampusByIdQuery, GetBuildingsByCampusQuery, GetBuildingByIdQuery,
    GetRoomsByBuildingQuery, GetRoomByIdQuery, SearchRoomsQuery,
    GetAvailableRoomsQuery
)
from ..dto import (
    SchoolDTO, CampusDTO, BuildingDTO, RoomDTO,
    SchoolCreateDTO, SchoolUpdateDTO,
    CampusCreateDTO, CampusUpdateDTO,
    BuildingCreateDTO, BuildingUpdateDTO,
    RoomCreateDTO, RoomUpdateDTO,
    SchoolSummaryDTO, SchoolWithDetailsDTO
)
from ..handlers.command_handlers import SchoolCommandHandlers
from ..handlers.query_handlers import SchoolQueryHandlers

logger = logging.getLogger(__name__)


class SchoolApplicationService:
    """学校管理应用服务。"""

    def __init__(
        self,
        school_service: SchoolService,
        command_handlers: SchoolCommandHandlers,
        query_handlers: SchoolQueryHandlers
    ):
        self.school_service = school_service
        self.command_handlers = command_handlers
        self.query_handlers = query_handlers

    # School operations
    async def create_school(
        self,
        dto: SchoolCreateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[SchoolDTO]:
        """创建学校。"""
        command = CreateSchoolCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            **dto.dict()
        )
        result = await self.command_handlers.handle_create_school(command)

        if result.success and result.data:
            school_dto = SchoolDTO.from_orm(result.data)
            return CommandResult.success_result(
                school_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def update_school(
        self,
        school_id: str,
        dto: SchoolUpdateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[SchoolDTO]:
        """更新学校。"""
        command = UpdateSchoolCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            school_id=school_id,
            **dto.dict(exclude_unset=True)
        )
        result = await self.command_handlers.handle_update_school(command)

        if result.success and result.data:
            school_dto = SchoolDTO.from_orm(result.data)
            return CommandResult.success_result(
                school_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def delete_school(
        self,
        school_id: str,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[bool]:
        """删除学校。"""
        command = DeleteSchoolCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            school_id=school_id
        )
        return await self.command_handlers.handle_delete_school(command)

    async def get_school_by_id(self, school_id: str, tenant_id: str) -> QueryResult[SchoolDTO]:
        """根据ID获取学校。"""
        query = GetSchoolByIdQuery(tenant_id=tenant_id, school_id=school_id)
        result = await self.query_handlers.handle_get_school_by_id(query)

        if result.success and result.data:
            school_dto = SchoolDTO.from_orm(result.data)
            return QueryResult.success_result(school_dto)
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    async def get_schools(
        self,
        tenant_id: str,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> QueryResult[List[SchoolDTO]]:
        """获取学校列表。"""
        query = GetSchoolsQuery(
            tenant_id=tenant_id,
            keyword=keyword,
            is_active=is_active,
            skip=(page - 1) * size,
            limit=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        result = await self.query_handlers.handle_get_schools(query)

        if result.success and result.data:
            schools_dto = [SchoolDTO.from_orm(school) for school in result.data]
            return QueryResult.success_result(
                schools_dto,
                total=result.total,
                page=page,
                size=size
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    async def get_school_summary(self, tenant_id: str) -> SchoolSummaryDTO:
        """获取学校汇总信息。"""
        # 获取所有激活的学校
        result = await self.get_schools(tenant_id, is_active=True, size=1000)

        if result.success and result.data:
            schools = result.data
            total_campuses = sum(s.campus_count for s in schools)
            total_buildings = sum(
                sum(b.building_count for b in s.campuses)
                for s in schools
            )
            total_rooms = sum(
                sum(r.room_count for r in s.rooms)
                for s in schools
            )
            active_rooms = sum(
                sum(1 for r in s.rooms if r.is_active)
                for s in schools
            )
            total_capacity = sum(r.capacity for s in schools for r in s.rooms)
            avg_utilization = (
                sum(r.utilization_rate for s in schools for r in s.rooms) /
                total_rooms if total_rooms > 0 else 0.0
            )

            return SchoolSummaryDTO(
                total_schools=len(schools),
                active_schools=len([s for s in schools if s.is_active]),
                total_campuses=total_campuses,
                total_buildings=total_buildings,
                total_rooms=total_rooms,
                active_rooms=active_rooms,
                total_capacity=total_capacity,
                average_utilization=round(avg_utilization, 2)
            )
        else:
            return SchoolSummaryDTO()

    async def get_school_with_details(self, school_id: str, tenant_id: str) -> QueryResult[SchoolWithDetailsDTO]:
        """获取带详情的学校信息。"""
        school_result = await self.get_school_by_id(school_id, tenant_id)

        if not school_result.success:
            return QueryResult(success=False, data=None, total=0, error=school_result.error)

        # 获取校区列表
        campuses_query = GetCampusesBySchoolQuery(tenant_id=tenant_id, school_id=school_id)
        campuses_result = await self.query_handlers.handle_get_campuses_by_school(campuses_query)

        school_dto = school_result.data
        school_with_details = SchoolWithDetailsDTO(**school_dto.dict())

        if campuses_result.success and campuses_result.data:
            school_with_details.campuses = [
                CampusDTO.from_orm(campus) for campus in campuses_result.data
            ]

        return QueryResult.success_result(school_with_details)

    # Campus operations
    async def create_campus(
        self,
        dto: CampusCreateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[CampusDTO]:
        """创建校区。"""
        command = CreateCampusCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            **dto.dict()
        )
        result = await self.command_handlers.handle_create_campus(command)

        if result.success and result.data:
            campus_dto = CampusDTO.from_orm(result.data)
            return CommandResult.success_result(campus_dto, message=result.message)
        else:
            return CommandResult.failure_result(result.error)

    # Building operations
    async def create_building(
        self,
        dto: BuildingCreateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[BuildingDTO]:
        """创建建筑。"""
        command = CreateBuildingCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            **dto.dict()
        )
        result = await self.command_handlers.handle_create_building(command)

        if result.success and result.data:
            building_dto = BuildingDTO.from_orm(result.data)
            return CommandResult.success_result(building_dto, message=result.message)
        else:
            return CommandResult.failure_result(result.error)

    # Room operations
    async def create_room(
        self,
        dto: RoomCreateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[RoomDTO]:
        """创建教室。"""
        command = CreateRoomCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            **dto.dict()
        )
        result = await self.command_handlers.handle_create_room(command)

        if result.success and result.data:
            room_dto = RoomDTO.from_orm(result.data)
            return CommandResult.success_result(room_dto, message=result.message)
        else:
            return CommandResult.failure_result(result.error)

    async def search_rooms(
        self,
        tenant_id: str,
        keyword: Optional[str] = None,
        room_type: Optional[str] = None,
        min_capacity: Optional[int] = None,
        features: Optional[List[str]] = None,
        building_id: Optional[str] = None,
        campus_id: Optional[str] = None,
        school_id: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> QueryResult[List[RoomDTO]]:
        """搜索教室。"""
        query = SearchRoomsQuery(
            tenant_id=tenant_id,
            keyword=keyword,
            room_type=room_type,
            min_capacity=min_capacity,
            features=features,
            building_id=building_id,
            campus_id=campus_id,
            school_id=school_id,
            skip=(page - 1) * size,
            limit=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        result = await self.query_handlers.handle_search_rooms(query)

        if result.success and result.data:
            rooms_dto = [RoomDTO.from_orm(room) for room in result.data]
            return QueryResult.success_result(
                rooms_dto,
                total=result.total,
                page=page,
                size=size
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)