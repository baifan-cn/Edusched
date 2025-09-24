"""课程管理领域服务。

处理课程相关的业务逻辑和领域规则。
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from ..models import Course, Section, Subject
from .base import DomainService, ServiceResult


class CourseService(DomainService[Course]):
    """课程领域服务。"""

    async def get_by_id(self, entity_id: UUID) -> ServiceResult[Course]:
        """根据ID获取课程。"""
        # TODO: 实现从存储库获取课程
        return ServiceResult.not_found_result("Course", entity_id)

    async def get_by_code(self, code: str) -> ServiceResult[Course]:
        """根据课程代码获取课程。"""
        # TODO: 实现从存储库获取
        return ServiceResult.not_found_result("Course", code)

    async def create(self, entity: Course) -> ServiceResult[Course]:
        """创建课程。"""
        # 验证业务规则
        validation_errors = await self.validate_business_rules(entity)
        if validation_errors:
            return ServiceResult.validation_error_result(validation_errors)

        # 创建前处理
        pre_result = await self.before_create(entity)
        if not pre_result.success:
            return pre_result

        # TODO: 实现保存到存储库
        # entity = await self.course_repository.create(entity)

        # 创建后处理
        return await self.after_create(entity)

    async def update(self, entity_id: UUID, entity: Course) -> ServiceResult[Course]:
        """更新课程。"""
        # 检查课程是否存在
        existing = await self.get_by_id(entity_id)
        if not existing.success:
            return existing

        # 验证业务规则
        validation_errors = await self.validate_business_rules(entity)
        if validation_errors:
            return ServiceResult.validation_error_result(validation_errors)

        # 更新前处理
        pre_result = await self.before_update(entity_id, entity)
        if not pre_result.success:
            return pre_result

        # TODO: 实现更新到存储库
        # entity = await self.course_repository.update(entity_id, entity)

        # 更新后处理
        return await self.after_update(entity)

    async def delete(self, entity_id: UUID) -> ServiceResult[bool]:
        """删除课程。"""
        # 检查课程是否存在
        existing = await self.get_by_id(entity_id)
        if not existing.success:
            return ServiceResult.failure_result("Course not found")

        # 检查是否有关联的教学段
        sections = await self.get_sections_by_course(entity_id)
        if sections:
            return ServiceResult.failure_result(
                "Cannot delete course with associated sections"
            )

        # 删除前处理
        pre_result = await self.before_delete(entity_id)
        if not pre_result.success:
            return pre_result

        # TODO: 实现从存储库删除
        # await self.course_repository.delete(entity_id)

        # 删除后处理
        return await self.after_delete(entity_id)

    async def validate_business_rules(self, entity: Course) -> List[str]:
        """验证业务规则。"""
        errors = []

        # 验证课程代码唯一性
        # TODO: 实现唯一性检查
        # existing = await self.course_repository.get_by_code(entity.code)
        # if existing and existing.id != entity.id:
        #     errors.append("Course code already exists")

        # 验证学分
        if entity.credits <= Decimal('0'):
            errors.append("Credits must be greater than 0")

        if entity.credits > Decimal('10'):
            errors.append("Credits cannot exceed 10")

        # 验证课时数
        if entity.hours_per_week <= 0:
            errors.append("Hours per week must be greater than 0")

        if entity.total_hours <= 0:
            errors.append("Total hours must be greater than 0")

        if entity.total_hours < entity.hours_per_week:
            errors.append("Total hours cannot be less than hours per week")

        return errors

    async def get_sections_by_course(self, course_id: UUID) -> List[Section]:
        """获取课程的所有教学段。"""
        # TODO: 实现从存储库获取
        return []

    async def get_courses_by_subject(self, subject_id: UUID) -> ServiceResult[List[Course]]:
        """根据学科获取课程列表。"""
        # TODO: 实现从存储库获取
        courses = []
        return ServiceResult.success_result(courses)

    async def get_active_courses(self, skip: int = 0, limit: int = 100) -> ServiceResult[List[Course]]:
        """获取所有激活的课程。"""
        # TODO: 实现从存储库获取
        courses = []
        return ServiceResult.success_result(courses)

    async def calculate_course_statistics(self, course_id: UUID) -> ServiceResult[dict]:
        """计算课程统计信息。"""
        # 获取课程信息
        course_result = await self.get_by_id(course_id)
        if not course_result.success:
            return ServiceResult.failure_result("Course not found")

        # 获取教学段
        sections = await self.get_sections_by_course(course_id)

        # 计算统计信息
        total_sections = len(sections)
        total_students = sum(section.class_group_id for section in sections)  # TODO: 需要获取实际学生数
        total_teachers = len(set(section.teacher_id for section in sections))

        return ServiceResult.success_result({
            "course_id": course_id,
            "course_name": course_result.data.name,
            "total_sections": total_sections,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "credits": float(course_result.data.credits),
            "hours_per_week": course_result.data.hours_per_week,
            "total_hours": course_result.data.total_hours
        })

    async def duplicate_course(
        self,
        course_id: UUID,
        new_name: str,
        new_code: str,
        copy_sections: bool = False
    ) -> ServiceResult[Course]:
        """复制课程。"""
        # 获取原课程
        original_result = await self.get_by_id(course_id)
        if not original_result.success:
            return original_result

        original = original_result.data

        # 创建新课程
        new_course = Course(
            subject_id=original.subject_id,
            name=new_name,
            code=new_code,
            description=original.description,
            credits=original.credits,
            hours_per_week=original.hours_per_week,
            total_hours=original.total_hours,
            is_active=False,  # 默认停用
            tenant_id=self.tenant_id
        )

        # 验证新课程
        validation_errors = await self.validate_business_rules(new_course)
        if validation_errors:
            return ServiceResult.validation_error_result(validation_errors)

        # 保存新课程
        create_result = await self.create(new_course)
        if not create_result.success:
            return create_result

        # TODO: 如果需要复制教学段，在这里实现
        if copy_sections:
            # sections = await self.get_sections_by_course(course_id)
            # for section in sections:
            #     # 创建新的教学段
            #     pass
            pass

        return create_result

    async def search_courses(
        self,
        keyword: Optional[str] = None,
        subject_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> ServiceResult[List[Course]]:
        """搜索课程。"""
        # TODO: 实现搜索逻辑
        courses = []
        return ServiceResult.success_result(courses)