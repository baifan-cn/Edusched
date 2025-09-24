"""课程管理相关查询。

包含获取学科、课程、年级、班级、教学段等信息的查询定义。
"""

from typing import Optional, List
from uuid import UUID

from ..base import BaseQuery


class GetSubjectByIdQuery(BaseQuery):
    """根据ID获取学科查询。"""
    subject_id: UUID


class GetSubjectsQuery(BaseQuery):
    """获取学科列表查询。"""
    keyword: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class GetCourseByIdQuery(BaseQuery):
    """根据ID获取课程查询。"""
    course_id: UUID


class GetCoursesQuery(BaseQuery):
    """获取课程列表查询。"""
    keyword: Optional[str] = None
    subject_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class GetGradeByIdQuery(BaseQuery):
    """根据ID获取年级查询。"""
    grade_id: UUID


class GetGradesQuery(BaseQuery):
    """获取年级列表查询。"""
    keyword: Optional[str] = None
    level: Optional[int] = None


class GetClassGroupByIdQuery(BaseQuery):
    """根据ID获取班级查询。"""
    class_group_id: UUID


class GetClassGroupsQuery(BaseQuery):
    """获取班级列表查询。"""
    keyword: Optional[str] = None
    grade_id: Optional[UUID] = None
    homeroom_teacher_id: Optional[UUID] = None


class GetSectionByIdQuery(BaseQuery):
    """根据ID获取教学段查询。"""
    section_id: UUID


class GetSectionsQuery(BaseQuery):
    """获取教学段列表查询。"""
    keyword: Optional[str] = None
    course_id: Optional[UUID] = None
    class_group_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    is_locked: Optional[bool] = None


class GetSectionsByTeacherQuery(BaseQuery):
    """获取教师的教学段列表查询。"""
    teacher_id: UUID
    is_active: Optional[bool] = None


class GetSectionsByClassGroupQuery(BaseQuery):
    """获取班级的教学段列表查询。"""
    class_group_id: UUID
    is_active: Optional[bool] = None


class GetSectionsByCourseQuery(BaseQuery):
    """获取课程的教学段列表查询。"""
    course_id: UUID
    is_active: Optional[bool] = None


class GetUnassignedSectionsQuery(BaseQuery):
    """获取未分配时间的教学段查询。"""
    course_id: Optional[UUID] = None
    class_group_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None