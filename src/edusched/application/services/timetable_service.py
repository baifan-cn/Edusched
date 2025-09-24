"""时间表管理应用服务。

协调时间表相关的领域服务和基础设施操作。
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from ...domain.models import Timetable, Assignment, SchedulingJob
from ...domain.services import TimetableService, SchedulingDomainService
from ..base import CommandResult, QueryResult
from ..commands import (
    StartSchedulingCommand, StopSchedulingCommand,
    PublishTimetableCommand, UnpublishTimetableCommand,
    CreateTimetableCommand, UpdateTimetableCommand, DeleteTimetableCommand,
    CreateAssignmentCommand, UpdateAssignmentCommand, DeleteAssignmentCommand,
    LockAssignmentCommand, UnlockAssignmentCommand
)
from ..queries import (
    GetTimetableByIdQuery, GetTimetablesQuery, GetAssignmentsQuery,
    GetSchedulingJobsQuery, GetTimetableByClassGroupQuery,
    GetTimetableByTeacherQuery, GetTimetableByRoomQuery,
    GetConflictsQuery, GetTimetableStatsQuery, GetPublishedTimetablesQuery
)
from ..dto import (
    TimetableDTO, AssignmentDTO, SchedulingJobDTO,
    TimetableCreateDTO, TimetableUpdateDTO,
    AssignmentCreateDTO, AssignmentUpdateDTO,
    TimetableStatsDTO, ConflictDTO, ScheduleGridDTO,
    TimetablePublishDTO
)
from ..handlers.command_handlers import TimetableCommandHandlers
from ..handlers.query_handlers import TimetableQueryHandlers

logger = logging.getLogger(__name__)


class TimetableApplicationService:
    """时间表管理应用服务。"""

    def __init__(
        self,
        timetable_service: TimetableService,
        scheduling_service: SchedulingDomainService,
        command_handlers: TimetableCommandHandlers,
        query_handlers: TimetableQueryHandlers
    ):
        self.timetable_service = timetable_service
        self.scheduling_service = scheduling_service
        self.command_handlers = command_handlers
        self.query_handlers = query_handlers

    # Timetable operations
    async def create_timetable(
        self,
        dto: TimetableCreateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[TimetableDTO]:
        """创建时间表。"""
        command = CreateTimetableCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            **dto.dict()
        )
        result = await self.command_handlers.handle_create_timetable(command)

        if result.success and result.data:
            timetable_dto = TimetableDTO.from_orm(result.data)
            return CommandResult.success_result(
                timetable_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def update_timetable(
        self,
        timetable_id: UUID,
        dto: TimetableUpdateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[TimetableDTO]:
        """更新时间表。"""
        command = UpdateTimetableCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            timetable_id=timetable_id,
            **dto.dict(exclude_unset=True)
        )
        result = await self.command_handlers.handle_update_timetable(command)

        if result.success and result.data:
            timetable_dto = TimetableDTO.from_orm(result.data)
            return CommandResult.success_result(
                timetable_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def delete_timetable(
        self,
        timetable_id: UUID,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[bool]:
        """删除时间表。"""
        command = DeleteTimetableCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            timetable_id=timetable_id
        )
        return await self.command_handlers.handle_delete_timetable(command)

    async def get_timetable_by_id(
        self,
        timetable_id: UUID,
        tenant_id: str
    ) -> QueryResult[TimetableDTO]:
        """根据ID获取时间表。"""
        query = GetTimetableByIdQuery(tenant_id=tenant_id, timetable_id=timetable_id)
        result = await self.query_handlers.handle_get_timetable_by_id(query)

        if result.success and result.data:
            timetable_dto = TimetableDTO.from_orm(result.data)
            return QueryResult.success_result(timetable_dto)
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    async def get_timetables(
        self,
        tenant_id: str,
        calendar_id: Optional[UUID] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> QueryResult[List[TimetableDTO]]:
        """获取时间表列表。"""
        query = GetTimetablesQuery(
            tenant_id=tenant_id,
            calendar_id=calendar_id,
            status=status,
            skip=(page - 1) * size,
            limit=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        result = await self.query_handlers.handle_get_timetables(query)

        if result.success and result.data:
            timetables_dto = [TimetableDTO.from_orm(t) for t in result.data]
            return QueryResult.success_result(
                timetables_dto,
                total=result.total,
                page=page,
                size=size
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    # Scheduling operations
    async def start_scheduling(
        self,
        timetable_id: UUID,
        tenant_id: str,
        max_iterations: int = 1000,
        timeout_seconds: int = 300,
        requested_by: Optional[str] = None
    ) -> CommandResult[SchedulingJobDTO]:
        """开始调度。"""
        command = StartSchedulingCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            timetable_id=timetable_id,
            max_iterations=max_iterations,
            timeout_seconds=timeout_seconds
        )
        result = await self.command_handlers.handle_start_scheduling(command)

        if result.success and result.data:
            job_dto = SchedulingJobDTO.from_orm(result.data)
            return CommandResult.success_result(
                job_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def stop_scheduling(
        self,
        job_id: UUID,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[bool]:
        """停止调度。"""
        command = StopSchedulingCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            job_id=job_id
        )
        result = await self.command_handlers.handle_stop_scheduling(command)

        if result.success:
            return CommandResult.success_result(True, message=result.message)
        else:
            return CommandResult.failure_result(result.error)

    async def get_scheduling_jobs(
        self,
        tenant_id: str,
        timetable_id: Optional[UUID] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> QueryResult[List[SchedulingJobDTO]]:
        """获取调度任务列表。"""
        query = GetSchedulingJobsQuery(
            tenant_id=tenant_id,
            timetable_id=timetable_id,
            status=status,
            skip=(page - 1) * size,
            limit=size
        )
        result = await self.query_handlers.handle_get_scheduling_jobs(query)

        if result.success and result.data:
            jobs_dto = [SchedulingJobDTO.from_orm(job) for job in result.data]
            return QueryResult.success_result(
                jobs_dto,
                total=result.total,
                page=page,
                size=size
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    # Assignment operations
    async def create_assignment(
        self,
        dto: AssignmentCreateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[AssignmentDTO]:
        """创建分配。"""
        command = CreateAssignmentCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            **dto.dict()
        )
        result = await self.command_handlers.handle_create_assignment(command)

        if result.success and result.data:
            assignment_dto = AssignmentDTO.from_orm(result.data)
            return CommandResult.success_result(
                assignment_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def update_assignment(
        self,
        assignment_id: UUID,
        dto: AssignmentUpdateDTO,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[AssignmentDTO]:
        """更新分配。"""
        command = UpdateAssignmentCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            assignment_id=assignment_id,
            **dto.dict(exclude_unset=True)
        )
        result = await self.command_handlers.handle_update_assignment(command)

        if result.success and result.data:
            assignment_dto = AssignmentDTO.from_orm(result.data)
            return CommandResult.success_result(
                assignment_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def delete_assignment(
        self,
        assignment_id: UUID,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[bool]:
        """删除分配。"""
        command = DeleteAssignmentCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            assignment_id=assignment_id
        )
        result = await self.command_handlers.handle_delete_assignment(command)

        if result.success:
            return CommandResult.success_result(True, message=result.message)
        else:
            return CommandResult.failure_result(result.error)

    async def get_assignments(
        self,
        timetable_id: UUID,
        tenant_id: str,
        section_id: Optional[UUID] = None,
        teacher_id: Optional[UUID] = None,
        room_id: Optional[UUID] = None,
        timeslot_id: Optional[UUID] = None,
        is_locked: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> QueryResult[List[AssignmentDTO]]:
        """获取分配列表。"""
        query = GetAssignmentsQuery(
            tenant_id=tenant_id,
            timetable_id=timetable_id,
            section_id=section_id,
            teacher_id=teacher_id,
            room_id=room_id,
            timeslot_id=timeslot_id,
            is_locked=is_locked,
            skip=(page - 1) * size,
            limit=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        result = await self.query_handlers.handle_get_assignments(query)

        if result.success and result.data:
            assignments_dto = [AssignmentDTO.from_orm(a) for a in result.data]
            return QueryResult.success_result(
                assignments_dto,
                total=result.total,
                page=page,
                size=size
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    # Schedule view operations
    async def get_class_group_schedule(
        self,
        class_group_id: UUID,
        calendar_id: UUID,
        tenant_id: str,
        week_number: Optional[int] = None,
        week_pattern_id: Optional[UUID] = None
    ) -> QueryResult[ScheduleGridDTO]:
        """获取班级课程表。"""
        query = GetTimetableByClassGroupQuery(
            tenant_id=tenant_id,
            class_group_id=class_group_id,
            calendar_id=calendar_id,
            week_number=week_number,
            week_pattern_id=week_pattern_id
        )
        result = await self.query_handlers.handle_get_timetable_by_class_group(query)

        if result.success and result.data:
            # 转换为ScheduleGridDTO格式
            schedule_data = result.data
            return QueryResult.success_result(
                ScheduleGridDTO(
                    headers=["时间段", "周一", "周二", "周三", "周四", "周五"],
                    rows=schedule_data,
                    metadata={"week_number": week_number}
                )
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    async def get_teacher_schedule(
        self,
        teacher_id: UUID,
        calendar_id: UUID,
        tenant_id: str,
        week_number: Optional[int] = None,
        week_pattern_id: Optional[UUID] = None
    ) -> QueryResult[ScheduleGridDTO]:
        """获取教师课程表。"""
        query = GetTimetableByTeacherQuery(
            tenant_id=tenant_id,
            teacher_id=teacher_id,
            calendar_id=calendar_id,
            week_number=week_number,
            week_pattern_id=week_pattern_id
        )
        result = await self.query_handlers.handle_get_timetable_by_teacher(query)

        if result.success and result.data:
            schedule_data = result.data
            return QueryResult.success_result(
                ScheduleGridDTO(
                    headers=["时间段", "周一", "周二", "周三", "周四", "周五"],
                    rows=schedule_data,
                    metadata={"week_number": week_number}
                )
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    async def get_room_schedule(
        self,
        room_id: UUID,
        calendar_id: UUID,
        tenant_id: str,
        week_number: Optional[int] = None,
        week_pattern_id: Optional[UUID] = None
    ) -> QueryResult[ScheduleGridDTO]:
        """获取教室课程表。"""
        query = GetTimetableByRoomQuery(
            tenant_id=tenant_id,
            room_id=room_id,
            calendar_id=calendar_id,
            week_number=week_number,
            week_pattern_id=week_pattern_id
        )
        result = await self.query_handlers.handle_get_timetable_by_room(query)

        if result.success and result.data:
            schedule_data = result.data
            return QueryResult.success_result(
                ScheduleGridDTO(
                    headers=["时间段", "周一", "周二", "周三", "周四", "周五"],
                    rows=schedule_data,
                    metadata={"week_number": week_number}
                )
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    # Statistics and analysis
    async def get_timetable_stats(
        self,
        timetable_id: UUID,
        tenant_id: str
    ) -> QueryResult[TimetableStatsDTO]:
        """获取时间表统计信息。"""
        query = GetTimetableStatsQuery(tenant_id=tenant_id, timetable_id=timetable_id)
        result = await self.query_handlers.handle_get_timetable_stats(query)

        if result.success and result.data:
            stats_dto = TimetableStatsDTO(**result.data)
            return QueryResult.success_result(stats_dto)
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    async def get_conflicts(
        self,
        timetable_id: UUID,
        tenant_id: str,
        conflict_type: Optional[str] = None
    ) -> QueryResult[List[ConflictDTO]]:
        """获取冲突列表。"""
        query = GetConflictsQuery(
            tenant_id=tenant_id,
            timetable_id=timetable_id,
            conflict_type=conflict_type
        )
        result = await self.query_handlers.handle_get_conflicts(query)

        if result.success and result.data:
            conflicts_dto = [ConflictDTO(**conflict) for conflict in result.data]
            return QueryResult.success_result(conflicts_dto, total=len(conflicts_dto))
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)

    # Publish operations
    async def publish_timetable(
        self,
        timetable_id: UUID,
        tenant_id: str,
        requested_by: str,
        notes: Optional[str] = None
    ) -> CommandResult[TimetableDTO]:
        """发布时间表。"""
        command = PublishTimetableCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            timetable_id=timetable_id
        )
        result = await self.command_handlers.handle_publish_timetable(command)

        if result.success and result.data:
            timetable_dto = TimetableDTO.from_orm(result.data)
            return CommandResult.success_result(
                timetable_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def unpublish_timetable(
        self,
        timetable_id: UUID,
        tenant_id: str,
        requested_by: Optional[str] = None
    ) -> CommandResult[TimetableDTO]:
        """取消发布时间表。"""
        command = UnpublishTimetableCommand(
            tenant_id=tenant_id,
            requested_by=requested_by,
            timetable_id=timetable_id
        )
        result = await self.command_handlers.handle_unpublish_timetable(command)

        if result.success and result.data:
            timetable_dto = TimetableDTO.from_orm(result.data)
            return CommandResult.success_result(
                timetable_dto,
                message=result.message,
                **result.metadata
            )
        else:
            return CommandResult.failure_result(result.error)

    async def get_published_timetables(
        self,
        tenant_id: str,
        school_id: Optional[UUID] = None,
        calendar_id: Optional[UUID] = None,
        page: int = 1,
        size: int = 20
    ) -> QueryResult[List[TimetableDTO]]:
        """获取已发布的时间表。"""
        query = GetPublishedTimetablesQuery(
            tenant_id=tenant_id,
            school_id=school_id,
            calendar_id=calendar_id,
            skip=(page - 1) * size,
            limit=size
        )
        result = await self.query_handlers.handle_get_published_timetables(query)

        if result.success and result.data:
            timetables_dto = [TimetableDTO.from_orm(t) for t in result.data]
            return QueryResult.success_result(
                timetables_dto,
                total=result.total,
                page=page,
                size=size
            )
        else:
            return QueryResult(success=False, data=None, total=0, error=result.error)