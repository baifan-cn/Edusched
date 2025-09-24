"""学校管理领域服务。

处理学校相关的业务逻辑和领域规则。
"""

from typing import List, Optional, Union
from uuid import UUID

from ..models import School, Campus
from .base import DomainService, ServiceResult


class SchoolService(DomainService[School]):
    """学校领域服务。"""

    async def get_by_id(self, entity_id: UUID) -> ServiceResult[School]:
        """根据ID获取学校。"""
        # TODO: 实现从存储库获取学校
        return ServiceResult.not_found_result("School", entity_id)

    async def create(self, entity: School) -> ServiceResult[School]:
        """创建学校。"""
        # 验证业务规则
        validation_errors = await self.validate_business_rules(entity)
        if validation_errors:
            return ServiceResult.validation_error_result(validation_errors)

        # 创建前处理
        pre_result = await self.before_create(entity)
        if not pre_result.success:
            return pre_result

        # TODO: 实现保存到存储库
        # entity = await self.school_repository.create(entity)

        # 创建后处理
        return await self.after_create(entity)

    async def update(self, entity_id: UUID, entity: School) -> ServiceResult[School]:
        """更新学校。"""
        # 检查学校是否存在
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
        # entity = await self.school_repository.update(entity_id, entity)

        # 更新后处理
        return await self.after_update(entity)

    async def delete(self, entity_id: UUID) -> ServiceResult[bool]:
        """删除学校。"""
        # 检查学校是否存在
        existing = await self.get_by_id(entity_id)
        if not existing.success:
            return ServiceResult.failure_result("School not found")

        # 检查是否有关联的校区
        campuses = await self.get_campuses_by_school(entity_id)
        if campuses:
            return ServiceResult.failure_result(
                "Cannot delete school with associated campuses"
            )

        # 删除前处理
        pre_result = await self.before_delete(entity_id)
        if not pre_result.success:
            return pre_result

        # TODO: 实现从存储库删除
        # await self.school_repository.delete(entity_id)

        # 删除后处理
        return await self.after_delete(entity_id)

    async def validate_business_rules(self, entity: School) -> List[str]:
        """验证业务规则。"""
        errors = []

        # 验证学校代码唯一性
        # TODO: 实现唯一性检查
        # existing = await self.school_repository.get_by_code(entity.code)
        # if existing and existing.id != entity.id:
        #     errors.append("School code already exists")

        # 验证学年格式
        if not entity.academic_year or len(entity.academic_year) != 9:
            errors.append("Academic year must be in format YYYY-YYYY")

        # 验证学期
        valid_semesters = ["spring", "fall", "summer", "winter"]
        if entity.semester.lower() not in valid_semesters:
            errors.append(f"Semester must be one of: {', '.join(valid_semesters)}")

        return errors

    async def get_campuses_by_school(self, school_id: UUID) -> List[Campus]:
        """获取学校的所有校区。"""
        # TODO: 实现从存储库获取校区
        return []

    async def activate_school(self, school_id: UUID) -> ServiceResult[School]:
        """激活学校。"""
        result = await self.get_by_id(school_id)
        if not result.success:
            return result

        school = result.data
        if school.is_active:
            return ServiceResult.success_result(school, "School is already active")

        school.is_active = True
        return await self.update(school_id, school)

    async def deactivate_school(self, school_id: UUID) -> ServiceResult[School]:
        """停用学校。"""
        result = await self.get_by_id(school_id)
        if not result.success:
            return result

        school = result.data
        if not school.is_active:
            return ServiceResult.success_result(school, "School is already inactive")

        school.is_active = False
        return await self.update(school_id, school)

    async def get_active_schools(self, skip: int = 0, limit: int = 100) -> ServiceResult[List[School]]:
        """获取所有激活的学校。"""
        # TODO: 实现从存储库获取
        schools = []
        return ServiceResult.success_result(schools)

    async def search_schools(
        self,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> ServiceResult[List[School]]:
        """搜索学校。"""
        # TODO: 实现搜索逻辑
        schools = []
        return ServiceResult.success_result(schools)