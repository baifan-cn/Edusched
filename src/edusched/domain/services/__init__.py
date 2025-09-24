"""领域服务层模块。

包含Edusched系统的核心业务逻辑服务。
"""

from .base import BaseService, DomainService, ServiceResult
from .school_service import SchoolService
from .teacher_service import TeacherService
from .course_service import CourseService
from .timetable_service import TimetableService
from .scheduling_domain_service import SchedulingDomainService

__all__ = [
    "BaseService",
    "DomainService",
    "ServiceResult",
    "SchoolService",
    "TeacherService",
    "CourseService",
    "TimetableService",
    "SchedulingDomainService",
]