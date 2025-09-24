"""应用服务工厂。

负责创建和配置应用服务层组件。
"""

from typing import Dict, Type

from .base import ICommandHandler, IQueryHandler, IEventHandler
from .commands import *
from .queries import *
from .dto import *
from .services.dispatcher import ApplicationServiceDispatcher
from .services.school_service import SchoolApplicationService
from .services.timetable_service import TimetableApplicationService
from .events.domain_event_handlers import EVENT_HANDLERS
from ..infrastructure.cache import CacheService
from ..infrastructure.external import NotificationService
from ..domain.services import *


class ApplicationServiceFactory:
    """应用服务工厂类。"""

    def __init__(
        self,
        school_service: SchoolService,
        teacher_service: TeacherService,
        course_service: CourseService,
        timetable_service: TimetableService,
        scheduling_service: SchedulingDomainService,
        cache_service: CacheService,
        notification_service: NotificationService
    ):
        self.school_service = school_service
        self.teacher_service = teacher_service
        self.course_service = course_service
        self.timetable_service = timetable_service
        self.scheduling_service = scheduling_service
        self.cache_service = cache_service
        self.notification_service = notification_service

        # 创建分发器
        self.dispatcher = ApplicationServiceDispatcher()

        # 创建应用服务
        self._school_app_service = None
        self._timetable_app_service = None

        # 注册处理器
        self._register_handlers()

    def _register_handlers(self) -> None:
        """注册所有命令和查询处理器。"""
        # 导入处理器
        from .handlers.command_handlers import (
            SchoolCommandHandlers, TeacherCommandHandlers, TimetableCommandHandlers
        )
        from .handlers.query_handlers import (
            SchoolQueryHandlers, TeacherQueryHandlers, TimetableQueryHandlers
        )

        # 创建处理器实例
        school_cmd_handlers = SchoolCommandHandlers(self.school_service)
        teacher_cmd_handlers = TeacherCommandHandlers(self.teacher_service)
        timetable_cmd_handlers = TimetableCommandHandlers(
            self.timetable_service, self.scheduling_service
        )

        school_query_handlers = SchoolQueryHandlers(
            # 需要注入仓储实例
            # school_repository, campus_repository, building_repository, room_repository
        )
        teacher_query_handlers = TeacherQueryHandlers(
            # 需要注入仓储实例
            # teacher_repository
        )
        timetable_query_handlers = TimetableQueryHandlers(
            # 需要注入仓储实例
            # timetable_repository, assignment_repository, scheduling_job_repository
        )

        # 注册命令处理器
        command_mappings = {
            # School commands
            CreateSchoolCommand: school_cmd_handlers.handle_create_school,
            UpdateSchoolCommand: school_cmd_handlers.handle_update_school,
            DeleteSchoolCommand: school_cmd_handlers.handle_delete_school,
            ActivateSchoolCommand: school_cmd_handlers.handle_activate_school,
            DeactivateSchoolCommand: school_cmd_handlers.handle_deactivate_school,
            CreateCampusCommand: school_cmd_handlers.handle_create_campus,
            UpdateCampusCommand: school_cmd_handlers.handle_update_campus,
            DeleteCampusCommand: school_cmd_handlers.handle_delete_campus,
            CreateBuildingCommand: school_cmd_handlers.handle_create_building,
            UpdateBuildingCommand: school_cmd_handlers.handle_update_building,
            DeleteBuildingCommand: school_cmd_handlers.handle_delete_building,
            CreateRoomCommand: school_cmd_handlers.handle_create_room,
            UpdateRoomCommand: school_cmd_handlers.handle_update_room,
            DeleteRoomCommand: school_cmd_handlers.handle_delete_room,

            # Teacher commands
            CreateTeacherCommand: teacher_cmd_handlers.handle_create_teacher,
            UpdateTeacherCommand: teacher_cmd_handlers.handle_update_teacher,
            DeleteTeacherCommand: teacher_cmd_handlers.handle_delete_teacher,
            SetTeacherAvailabilityCommand: teacher_cmd_handlers.handle_set_teacher_availability,
            UpdateTeacherWorkloadCommand: teacher_cmd_handlers.handle_update_teacher_workload,

            # Timetable commands
            StartSchedulingCommand: timetable_cmd_handlers.handle_start_scheduling,
            StopSchedulingCommand: timetable_cmd_handlers.handle_stop_scheduling,
            PublishTimetableCommand: timetable_cmd_handlers.handle_publish_timetable,
            UnpublishTimetableCommand: timetable_cmd_handlers.handle_unpublish_timetable,
        }

        # 注册查询处理器
        query_mappings = {
            # School queries
            GetSchoolByIdQuery: school_query_handlers.handle_get_school_by_id,
            GetSchoolsQuery: school_query_handlers.handle_get_schools,
            GetCampusesBySchoolQuery: school_query_handlers.handle_get_campuses_by_school,
            GetRoomsByBuildingQuery: school_query_handlers.handle_get_rooms_by_building,
            SearchRoomsQuery: school_query_handlers.handle_search_rooms,

            # Teacher queries
            GetTeacherByIdQuery: teacher_query_handlers.handle_get_teacher_by_id,
            GetTeachersQuery: teacher_query_handlers.handle_get_teachers,
            GetTeacherWorkloadQuery: teacher_query_handlers.handle_get_teacher_workload,
            GetTeacherScheduleQuery: teacher_query_handlers.handle_get_teacher_schedule,

            # Timetable queries
            GetTimetableByIdQuery: timetable_query_handlers.handle_get_timetable_by_id,
            GetAssignmentsQuery: timetable_query_handlers.handle_get_assignments,
            GetTimetableByClassGroupQuery: timetable_query_handlers.handle_get_timetable_by_class_group,
            GetSchedulingJobsQuery: timetable_query_handlers.handle_get_scheduling_jobs,
        }

        # 注册到分发器
        for command_type, handler in command_mappings.items():
            self.dispatcher.register_command_handler(command_type, handler)

        for query_type, handler in query_mappings.items():
            self.dispatcher.register_query_handler(query_type, handler)

    @property
    def school_service(self) -> SchoolApplicationService:
        """获取学校应用服务。"""
        if self._school_app_service is None:
            from .handlers.command_handlers import SchoolCommandHandlers
            from .handlers.query_handlers import SchoolQueryHandlers

            cmd_handlers = SchoolCommandHandlers(self.school_service)
            query_handlers = SchoolQueryHandlers(
                # 需要注入仓储实例
            )
            self._school_app_service = SchoolApplicationService(
                self.school_service, cmd_handlers, query_handlers
            )

        return self._school_app_service

    @property
    def timetable_service(self) -> TimetableApplicationService:
        """获取时间表应用服务。"""
        if self._timetable_app_service is None:
            from .handlers.command_handlers import TimetableCommandHandlers
            from .handlers.query_handlers import TimetableQueryHandlers

            cmd_handlers = TimetableCommandHandlers(
                self.timetable_service, self.scheduling_service
            )
            query_handlers = TimetableQueryHandlers(
                # 需要注入仓储实例
            )
            self._timetable_app_service = TimetableApplicationService(
                self.timetable_service, self.scheduling_service,
                cmd_handlers, query_handlers
            )

        return self._timetable_app_service

    def create_event_handlers(self) -> Dict[str, IEventHandler]:
        """创建事件处理器。"""
        event_handlers = {}

        for event_type, handler_class in EVENT_HANDLERS.items():
            handler = handler_class(self.cache_service, self.notification_service)
            event_handlers[event_type] = handler

        return event_handlers

    async def send_command(self, command: BaseCommand) -> CommandResult:
        """发送命令。"""
        return await self.dispatcher.send_command(command)

    async def send_query(self, query: BaseQuery) -> QueryResult:
        """发送查询。"""
        return await self.dispatcher.send_query(query)