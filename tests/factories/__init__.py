"""测试数据工厂模块"""

from .school_factory import SchoolFactory
from .teacher_factory import TeacherFactory
from .course_factory import CourseFactory
from .class_factory import ClassFactory
from .section_factory import SectionFactory
from .timeslot_factory import TimeslotFactory
from .assignment_factory import AssignmentFactory
from .scheduling_factory import SchedulingFactory

__all__ = [
    'SchoolFactory',
    'TeacherFactory',
    'CourseFactory',
    'ClassFactory',
    'SectionFactory',
    'TimeslotFactory',
    'AssignmentFactory',
    'SchedulingFactory'
]