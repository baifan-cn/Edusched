"""命令处理器实现。

实现各种命令的处理逻辑。
"""

import logging
from typing import List, Optional
from uuid import UUID

from ...domain.models import (
    School, Campus, Building, Room, Teacher, Subject, Course,
    Grade, ClassGroup, Section, Timeslot, WeekPattern, Calendar,
    Constraint, Timetable, Assignment, SchedulingJob
)
from ...domain.services import (
    SchoolService, TeacherService, CourseService, TimetableService,
    SchedulingDomainService
)
from ..base import CommandResult, ICommandHandler
from ..commands import (
    # School Commands
    CreateSchoolCommand, UpdateSchoolCommand, DeleteSchoolCommand,
    ActivateSchoolCommand, DeactivateSchoolCommand,
    CreateCampusCommand, UpdateCampusCommand, DeleteCampusCommand,
    CreateBuildingCommand, UpdateBuildingCommand, DeleteBuildingCommand,
    CreateRoomCommand, UpdateRoomCommand, DeleteRoomCommand,
    # Teacher Commands
    CreateTeacherCommand, UpdateTeacherCommand, DeleteTeacherCommand,
    SetTeacherAvailabilityCommand, UpdateTeacherWorkloadCommand,
    # Course Commands
    CreateSubjectCommand, UpdateSubjectCommand, DeleteSubjectCommand,
    CreateCourseCommand, UpdateCourseCommand, DeleteCourseCommand,
    CreateGradeCommand, UpdateGradeCommand, DeleteGradeCommand,
    CreateClassGroupCommand, UpdateClassGroupCommand, DeleteClassGroupCommand,
    CreateSectionCommand, UpdateSectionCommand, DeleteSectionCommand,
    LockSectionCommand, UnlockSectionCommand,
    # Timetable Commands
    CreateCalendarCommand, UpdateCalendarCommand, DeleteCalendarCommand,
    CreateTimeslotCommand, UpdateTimeslotCommand, DeleteTimeslotCommand,
    CreateWeekPatternCommand, UpdateWeekPatternCommand, DeleteWeekPatternCommand,
    CreateConstraintCommand, UpdateConstraintCommand, DeleteConstraintCommand,
    CreateTimetableCommand, UpdateTimetableCommand, DeleteTimetableCommand,
    CreateAssignmentCommand, UpdateAssignmentCommand, DeleteAssignmentCommand,
    LockAssignmentCommand, UnlockAssignmentCommand,
    StartSchedulingCommand, StopSchedulingCommand,
    PublishTimetableCommand, UnpublishTimetableCommand
)

logger = logging.getLogger(__name__)


class SchoolCommandHandlers:
    """学校相关命令处理器。"""

    def __init__(self, school_service: SchoolService):
        self.school_service = school_service

    async def handle_create_school(self, command: CreateSchoolCommand) -> CommandResult[School]:
        """处理创建学校命令。"""
        try:
            school = School(
                tenant_id=command.tenant_id,
                name=command.name,
                code=command.code,
                address=command.address,
                phone=command.phone,
                email=command.email,
                website=command.website,
                timezone=command.timezone,
                academic_year=command.academic_year,
                semester=command.semester,
                is_active=command.is_active,
                created_by=command.requested_by
            )

            result = await self.school_service.create(school)
            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="School created successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error creating school: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_update_school(self, command: UpdateSchoolCommand) -> CommandResult[School]:
        """处理更新学校命令。"""
        try:
            # 获取现有学校
            existing_result = await self.school_service.get_by_id(command.school_id)
            if not existing_result.success:
                return CommandResult.failure_result(existing_result.error)

            school = existing_result.data

            # 更新字段
            update_data = command.dict(exclude_unset=True, exclude={"school_id"})
            for field, value in update_data.items():
                if hasattr(school, field):
                    setattr(school, field, value)

            school.updated_by = command.requested_by

            result = await self.school_service.update(command.school_id, school)
            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="School updated successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error updating school: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_delete_school(self, command: DeleteSchoolCommand) -> CommandResult[bool]:
        """处理删除学校命令。"""
        try:
            result = await self.school_service.delete(command.school_id)
            if result.success:
                return CommandResult.success_result(
                    True,
                    message="School deleted successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error deleting school: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_activate_school(self, command: ActivateSchoolCommand) -> CommandResult[School]:
        """处理激活学校命令。"""
        try:
            result = await self.school_service.activate_school(command.school_id)
            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="School activated successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error activating school: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_deactivate_school(self, command: DeactivateSchoolCommand) -> CommandResult[School]:
        """处理停用学校命令。"""
        try:
            result = await self.school_service.deactivate_school(command.school_id)
            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="School deactivated successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error deactivating school: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")


class TeacherCommandHandlers:
    """教师相关命令处理器。"""

    def __init__(self, teacher_service: TeacherService):
        self.teacher_service = teacher_service

    async def handle_create_teacher(self, command: CreateTeacherCommand) -> CommandResult[Teacher]:
        """处理创建教师命令。"""
        try:
            teacher = Teacher(
                tenant_id=command.tenant_id,
                employee_id=command.employee_id,
                name=command.name,
                email=command.email,
                phone=command.phone,
                department=command.department,
                title=command.title,
                max_hours_per_day=command.max_hours_per_day,
                max_hours_per_week=command.max_hours_per_week,
                preferred_time_slots=command.preferred_time_slots,
                unavailable_time_slots=command.unavailable_time_slots,
                is_active=command.is_active,
                created_by=command.requested_by
            )

            result = await self.teacher_service.create(teacher)
            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="Teacher created successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error creating teacher: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_update_teacher(self, command: UpdateTeacherCommand) -> CommandResult[Teacher]:
        """处理更新教师命令。"""
        try:
            # 获取现有教师
            existing_result = await self.teacher_service.get_by_id(command.teacher_id)
            if not existing_result.success:
                return CommandResult.failure_result(existing_result.error)

            teacher = existing_result.data

            # 更新字段
            update_data = command.dict(exclude_unset=True, exclude={"teacher_id"})
            for field, value in update_data.items():
                if hasattr(teacher, field):
                    setattr(teacher, field, value)

            teacher.updated_by = command.requested_by

            result = await self.teacher_service.update(command.teacher_id, teacher)
            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="Teacher updated successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error updating teacher: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_delete_teacher(self, command: DeleteTeacherCommand) -> CommandResult[bool]:
        """处理删除教师命令。"""
        try:
            result = await self.teacher_service.delete(command.teacher_id)
            if result.success:
                return CommandResult.success_result(
                    True,
                    message="Teacher deleted successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error deleting teacher: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")


class TimetableCommandHandlers:
    """时间表相关命令处理器。"""

    def __init__(
        self,
        timetable_service: TimetableService,
        scheduling_service: SchedulingDomainService
    ):
        self.timetable_service = timetable_service
        self.scheduling_service = scheduling_service

    async def handle_start_scheduling(self, command: StartSchedulingCommand) -> CommandResult[SchedulingJob]:
        """处理开始调度命令。"""
        try:
            result = await self.scheduling_service.start_scheduling(
                timetable_id=command.timetable_id,
                max_iterations=command.max_iterations,
                timeout_seconds=command.timeout_seconds
            )

            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="Scheduling started successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error starting scheduling: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_stop_scheduling(self, command: StopSchedulingCommand) -> CommandResult[bool]:
        """处理停止调度命令。"""
        try:
            result = await self.scheduling_service.stop_scheduling(command.job_id)
            if result.success:
                return CommandResult.success_result(
                    True,
                    message="Scheduling stopped successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error stopping scheduling: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_publish_timetable(self, command: PublishTimetableCommand) -> CommandResult[Timetable]:
        """处理发布时间表命令。"""
        try:
            result = await self.timetable_service.publish_timetable(
                command.timetable_id,
                command.requested_by
            )

            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="Timetable published successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error publishing timetable: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")

    async def handle_unpublish_timetable(self, command: UnpublishTimetableCommand) -> CommandResult[Timetable]:
        """处理取消发布时间表命令。"""
        try:
            result = await self.timetable_service.unpublish_timetable(command.timetable_id)
            if result.success:
                return CommandResult.success_result(
                    result.data,
                    message="Timetable unpublished successfully"
                )
            else:
                return CommandResult.failure_result(result.error)

        except Exception as e:
            logger.error(f"Error unpublishing timetable: {e}", exc_info=True)
            return CommandResult.failure_result(f"Internal server error: {str(e)}")


# 命令处理器映射
COMMAND_HANDLERS = {
    # School Commands
    CreateSchoolCommand: SchoolCommandHandlers.handle_create_school,
    UpdateSchoolCommand: SchoolCommandHandlers.handle_update_school,
    DeleteSchoolCommand: SchoolCommandHandlers.handle_delete_school,
    ActivateSchoolCommand: SchoolCommandHandlers.handle_activate_school,
    DeactivateSchoolCommand: SchoolCommandHandlers.handle_deactivate_school,

    # Teacher Commands
    CreateTeacherCommand: TeacherCommandHandlers.handle_create_teacher,
    UpdateTeacherCommand: TeacherCommandHandlers.handle_update_teacher,
    DeleteTeacherCommand: TeacherCommandHandlers.handle_delete_teacher,

    # Timetable Commands
    StartSchedulingCommand: TimetableCommandHandlers.handle_start_scheduling,
    StopSchedulingCommand: TimetableCommandHandlers.handle_stop_scheduling,
    PublishTimetableCommand: TimetableCommandHandlers.handle_publish_timetable,
    UnpublishTimetableCommand: TimetableCommandHandlers.handle_unpublish_timetable,
}