"""API路由模块。"""

from . import health, schools, teachers, courses, timetables, scheduling

__all__ = [
    "health",
    "schools", 
    "teachers",
    "courses",
    "timetables",
    "scheduling",
]