"""查询处理器实现。

实现各种查询的处理逻辑。
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from ...domain.models import (
    School, Campus, Building, Room, Teacher, Subject, Course,
    Grade, ClassGroup, Section, Timeslot, WeekPattern, Calendar,
    Constraint, Timetable, Assignment, SchedulingJob
)
from ...infrastructure.database.repository import (
    SchoolRepository, CampusRepository, BuildingRepository, RoomRepository,
    TeacherRepository, SubjectRepository, CourseRepository, GradeRepository,
    ClassGroupRepository, SectionRepository, TimeslotRepository, WeekPatternRepository,
    CalendarRepository, ConstraintRepository, TimetableRepository,
    AssignmentRepository, SchedulingJobRepository
)
from ..base import QueryResult, IQueryHandler
from ..queries import (
    # School Queries
    GetSchoolByIdQuery, GetSchoolsQuery, GetCampusesBySchoolQuery,
    GetCampusByIdQuery, GetBuildingsByCampusQuery, GetBuildingByIdQuery,
    GetRoomsByBuildingQuery, GetRoomByIdQuery, SearchRoomsQuery,
    GetAvailableRoomsQuery,
    # Teacher Queries
    GetTeacherByIdQuery, GetTeachersQuery, GetTeacherWorkloadQuery,
    GetTeacherAvailabilityQuery, GetAvailableTeachersQuery, GetTeacherScheduleQuery,
    GetTeachersByDepartmentQuery, GetTeacherStatsQuery, CheckTeacherAvailabilityQuery,
    # Course Queries
    GetSubjectByIdQuery, GetSubjectsQuery, GetCourseByIdQuery, GetCoursesQuery,
    GetGradeByIdQuery, GetGradesQuery, GetClassGroupByIdQuery, GetClassGroupsQuery,
    GetSectionByIdQuery, GetSectionsQuery, GetSectionsByTeacherQuery,
    GetSectionsByClassGroupQuery, GetSectionsByCourseQuery, GetUnassignedSectionsQuery,
    # Timetable Queries
    GetCalendarByIdQuery, GetCalendarsQuery, GetTimeslotByIdQuery, GetTimeslotsQuery,
    GetWeekPatternByIdQuery, GetWeekPatternsQuery, GetConstraintByIdQuery,
    GetConstraintsQuery, GetTimetableByIdQuery, GetTimetablesQuery,
    GetAssignmentByIdQuery, GetAssignmentsQuery, GetSchedulingJobByIdQuery,
    GetSchedulingJobsQuery, GetTimetableByClassGroupQuery, GetTimetableByTeacherQuery,
    GetTimetableByRoomQuery, GetConflictsQuery, GetTimetableStatsQuery,
    GetPublishedTimetablesQuery, CheckTimeslotAvailabilityQuery
)

logger = logging.getLogger(__name__)


class SchoolQueryHandlers:
    """学校相关查询处理器。"""

    def __init__(
        self,
        school_repository: SchoolRepository,
        campus_repository: CampusRepository,
        building_repository: BuildingRepository,
        room_repository: RoomRepository
    ):
        self.school_repository = school_repository
        self.campus_repository = campus_repository
        self.building_repository = building_repository
        self.room_repository = room_repository

    async def handle_get_school_by_id(self, query: GetSchoolByIdQuery) -> QueryResult[School]:
        """处理根据ID获取学校查询。"""
        try:
            school = await self.school_repository.get_by_id(
                entity_id=query.school_id,
                tenant_id=query.tenant_id
            )

            if school:
                return QueryResult.success_result(school)
            else:
                return QueryResult.success_result(None, total=0)

        except Exception as e:
            logger.error(f"Error getting school by ID: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_schools(self, query: GetSchoolsQuery) -> QueryResult[List[School]]:
        """处理获取学校列表查询。"""
        try:
            filters = {}
            if query.keyword:
                filters["keyword"] = query.keyword
            if query.is_active is not None:
                filters["is_active"] = query.is_active

            schools, total = await self.school_repository.get_list(
                tenant_id=query.tenant_id,
                skip=query.skip,
                limit=query.limit,
                filters=filters,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )

            return QueryResult.success_result(
                schools,
                total=total,
                page=query.skip // query.limit + 1,
                size=query.limit
            )

        except Exception as e:
            logger.error(f"Error getting schools: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_campuses_by_school(self, query: GetCampusesBySchoolQuery) -> QueryResult[List[Campus]]:
        """处理获取学校的校区列表查询。"""
        try:
            campuses = await self.campus_repository.get_by_school(
                school_id=query.school_id,
                tenant_id=query.tenant_id
            )

            return QueryResult.success_result(campuses, total=len(campuses))

        except Exception as e:
            logger.error(f"Error getting campuses: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_rooms_by_building(self, query: GetRoomsByBuildingQuery) -> QueryResult[List[Room]]:
        """处理获取建筑的教室列表查询。"""
        try:
            filters = {"building_id": query.building_id}
            if query.room_type:
                filters["room_type"] = query.room_type
            if query.min_capacity:
                filters["capacity__gte"] = query.min_capacity
            if query.is_active is not None:
                filters["is_active"] = query.is_active

            rooms, total = await self.room_repository.get_list(
                tenant_id=query.tenant_id,
                filters=filters,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )

            return QueryResult.success_result(rooms, total=total)

        except Exception as e:
            logger.error(f"Error getting rooms: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_search_rooms(self, query: SearchRoomsQuery) -> QueryResult[List[Room]]:
        """处理搜索教室查询。"""
        try:
            filters = {}
            if query.keyword:
                filters["keyword"] = query.keyword
            if query.room_type:
                filters["room_type"] = query.room_type
            if query.min_capacity:
                filters["capacity__gte"] = query.min_capacity
            if query.features:
                filters["features__contains"] = query.features
            if query.building_id:
                filters["building_id"] = query.building_id
            if query.campus_id:
                filters["campus_id"] = query.campus_id
            if query.school_id:
                filters["school_id"] = query.school_id

            rooms, total = await self.room_repository.search(
                tenant_id=query.tenant_id,
                filters=filters,
                skip=query.skip,
                limit=query.limit,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )

            return QueryResult.success_result(
                rooms,
                total=total,
                page=query.skip // query.limit + 1,
                size=query.limit
            )

        except Exception as e:
            logger.error(f"Error searching rooms: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))


class TeacherQueryHandlers:
    """教师相关查询处理器。"""

    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository

    async def handle_get_teacher_by_id(self, query: GetTeacherByIdQuery) -> QueryResult[Teacher]:
        """处理根据ID获取教师查询。"""
        try:
            teacher = await self.teacher_repository.get_by_id(
                entity_id=query.teacher_id,
                tenant_id=query.tenant_id
            )

            if teacher:
                return QueryResult.success_result(teacher)
            else:
                return QueryResult.success_result(None, total=0)

        except Exception as e:
            logger.error(f"Error getting teacher by ID: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_teachers(self, query: GetTeachersQuery) -> QueryResult[List[Teacher]]:
        """处理获取教师列表查询。"""
        try:
            filters = {}
            if query.keyword:
                filters["keyword"] = query.keyword
            if query.department:
                filters["department"] = query.department
            if query.is_active is not None:
                filters["is_active"] = query.is_active

            teachers, total = await self.teacher_repository.get_list(
                tenant_id=query.tenant_id,
                skip=query.skip,
                limit=query.limit,
                filters=filters,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )

            return QueryResult.success_result(
                teachers,
                total=total,
                page=query.skip // query.limit + 1,
                size=query.limit
            )

        except Exception as e:
            logger.error(f"Error getting teachers: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_teacher_workload(self, query: GetTeacherWorkloadQuery) -> QueryResult[Dict[str, Any]]:
        """处理获取教师工作量查询。"""
        try:
            workload = await self.teacher_repository.get_workload(
                teacher_id=query.teacher_id,
                start_date=query.start_date,
                end_date=query.end_date
            )

            return QueryResult.success_result(workload)

        except Exception as e:
            logger.error(f"Error getting teacher workload: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_teacher_schedule(self, query: GetTeacherScheduleQuery) -> QueryResult[List[Assignment]]:
        """处理获取教师课程表查询。"""
        try:
            assignments = await self.teacher_repository.get_schedule(
                teacher_id=query.teacher_id,
                calendar_id=query.calendar_id,
                week_number=query.week_number,
                week_pattern_id=query.week_pattern_id
            )

            return QueryResult.success_result(assignments, total=len(assignments))

        except Exception as e:
            logger.error(f"Error getting teacher schedule: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))


class TimetableQueryHandlers:
    """时间表相关查询处理器。"""

    def __init__(
        self,
        timetable_repository: TimetableRepository,
        assignment_repository: AssignmentRepository,
        scheduling_job_repository: SchedulingJobRepository
    ):
        self.timetable_repository = timetable_repository
        self.assignment_repository = assignment_repository
        self.scheduling_job_repository = scheduling_job_repository

    async def handle_get_timetable_by_id(self, query: GetTimetableByIdQuery) -> QueryResult[Timetable]:
        """处理根据ID获取时间表查询。"""
        try:
            timetable = await self.timetable_repository.get_by_id(
                entity_id=query.timetable_id,
                tenant_id=query.tenant_id
            )

            if timetable:
                return QueryResult.success_result(timetable)
            else:
                return QueryResult.success_result(None, total=0)

        except Exception as e:
            logger.error(f"Error getting timetable by ID: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_assignments(self, query: GetAssignmentsQuery) -> QueryResult[List[Assignment]]:
        """处理获取分配列表查询。"""
        try:
            filters = {"timetable_id": query.timetable_id}
            if query.section_id:
                filters["section_id"] = query.section_id
            if query.teacher_id:
                filters["teacher_id"] = query.teacher_id
            if query.room_id:
                filters["room_id"] = query.room_id
            if query.timeslot_id:
                filters["timeslot_id"] = query.timeslot_id
            if query.is_locked is not None:
                filters["is_locked"] = query.is_locked

            assignments, total = await self.assignment_repository.get_list(
                tenant_id=query.tenant_id,
                filters=filters,
                skip=query.skip,
                limit=query.limit,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )

            return QueryResult.success_result(
                assignments,
                total=total,
                page=query.skip // query.limit + 1,
                size=query.limit
            )

        except Exception as e:
            logger.error(f"Error getting assignments: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_timetable_by_class_group(self, query: GetTimetableByClassGroupQuery) -> QueryResult[List[Dict[str, Any]]]:
        """处理获取班级的时间表查询。"""
        try:
            schedule = await self.timetable_repository.get_class_group_schedule(
                class_group_id=query.class_group_id,
                calendar_id=query.calendar_id,
                week_number=query.week_number,
                week_pattern_id=query.week_pattern_id
            )

            return QueryResult.success_result(schedule, total=len(schedule))

        except Exception as e:
            logger.error(f"Error getting class group schedule: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))

    async def handle_get_scheduling_jobs(self, query: GetSchedulingJobsQuery) -> QueryResult[List[SchedulingJob]]:
        """处理获取调度任务列表查询。"""
        try:
            filters = {}
            if query.timetable_id:
                filters["timetable_id"] = query.timetable_id
            if query.status:
                filters["status"] = query.status

            jobs, total = await self.scheduling_job_repository.get_list(
                tenant_id=query.tenant_id,
                filters=filters,
                skip=query.skip,
                limit=query.limit,
                sort_by="created_at",
                sort_order="desc"
            )

            return QueryResult.success_result(
                jobs,
                total=total,
                page=query.skip // query.limit + 1,
                size=query.limit
            )

        except Exception as e:
            logger.error(f"Error getting scheduling jobs: {e}", exc_info=True)
            return QueryResult(success=False, data=None, total=0, error=str(e))


# 查询处理器映射
QUERY_HANDLERS = {
    # School Queries
    GetSchoolByIdQuery: SchoolQueryHandlers.handle_get_school_by_id,
    GetSchoolsQuery: SchoolQueryHandlers.handle_get_schools,
    GetCampusesBySchoolQuery: SchoolQueryHandlers.handle_get_campuses_by_school,
    GetRoomsByBuildingQuery: SchoolQueryHandlers.handle_get_rooms_by_building,
    SearchRoomsQuery: SchoolQueryHandlers.handle_search_rooms,

    # Teacher Queries
    GetTeacherByIdQuery: TeacherQueryHandlers.handle_get_teacher_by_id,
    GetTeachersQuery: TeacherQueryHandlers.handle_get_teachers,
    GetTeacherWorkloadQuery: TeacherQueryHandlers.handle_get_teacher_workload,
    GetTeacherScheduleQuery: TeacherQueryHandlers.handle_get_teacher_schedule,

    # Timetable Queries
    GetTimetableByIdQuery: TimetableQueryHandlers.handle_get_timetable_by_id,
    GetAssignmentsQuery: TimetableQueryHandlers.handle_get_assignments,
    GetTimetableByClassGroupQuery: TimetableQueryHandlers.handle_get_timetable_by_class_group,
    GetSchedulingJobsQuery: TimetableQueryHandlers.handle_get_scheduling_jobs,
}