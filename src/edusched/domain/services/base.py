"""领域服务基础类。

定义领域服务的通用接口和基础实现。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")


class ServiceResult(BaseModel, Generic[T]):
    """服务执行结果。"""

    success: bool = Field(description="是否成功")
    data: Optional[T] = Field(default=None, description="返回数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    message: Optional[str] = Field(default=None, description="提示信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    @classmethod
    def success_result(cls, data: Optional[T] = None, message: Optional[str] = None, **metadata) -> "ServiceResult[T]":
        """创建成功结果。"""
        return cls(
            success=True,
            data=data,
            message=message,
            metadata=metadata
        )

    @classmethod
    def failure_result(cls, error: str, data: Optional[T] = None, **metadata) -> "ServiceResult[T]":
        """创建失败结果。"""
        return cls(
            success=False,
            data=data,
            error=error,
            metadata=metadata
        )

    @classmethod
    def not_found_result(cls, entity_type: str, entity_id: Union[UUID, str]) -> "ServiceResult[T]":
        """创建未找到结果。"""
        return cls(
            success=False,
            error=f"{entity_type} not found: {entity_id}"
        )

    @classmethod
    def validation_error_result(cls, errors: List[str]) -> "ServiceResult[T]":
        """创建验证错误结果。"""
        return cls(
            success=False,
            error="Validation failed",
            metadata={"validation_errors": errors}
        )


class BaseService(ABC):
    """基础服务类。"""

    def __init__(self, tenant_id: str):
        """初始化服务。

        Args:
            tenant_id: 租户ID
        """
        self.tenant_id = tenant_id

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> ServiceResult[T]:
        """根据ID获取实体。"""
        pass

    @abstractmethod
    async def create(self, entity: T) -> ServiceResult[T]:
        """创建实体。"""
        pass

    @abstractmethod
    async def update(self, entity_id: UUID, entity: T) -> ServiceResult[T]:
        """更新实体。"""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> ServiceResult[bool]:
        """删除实体。"""
        pass


class DomainService(BaseService[T]):
    """领域服务基类。

    封装核心业务逻辑和领域规则。
    """

    async def validate_business_rules(self, entity: T) -> List[str]:
        """验证业务规则。

        Args:
            entity: 要验证的实体

        Returns:
            验证错误列表，空列表表示验证通过
        """
        return []

    async def before_create(self, entity: T) -> ServiceResult[T]:
        """创建前的预处理。"""
        return ServiceResult.success_result(entity)

    async def after_create(self, entity: T) -> ServiceResult[T]:
        """创建后的后处理。"""
        return ServiceResult.success_result(entity)

    async def before_update(self, entity_id: UUID, entity: T) -> ServiceResult[T]:
        """更新前的预处理。"""
        return ServiceResult.success_result(entity)

    async def after_update(self, entity: T) -> ServiceResult[T]:
        """更新后的后处理。"""
        return ServiceResult.success_result(entity)

    async def before_delete(self, entity_id: UUID) -> ServiceResult[bool]:
        """删除前的预处理。"""
        return ServiceResult.success_result(True)

    async def after_delete(self, entity_id: UUID) -> ServiceResult[bool]:
        """删除后的后处理。"""
        return ServiceResult.success_result(True)