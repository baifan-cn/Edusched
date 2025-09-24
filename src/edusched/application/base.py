"""基础抽象类定义。

定义CQRS模式的基础接口和抽象类。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")
C = TypeVar("C", bound="BaseCommand")
Q = TypeVar("Q", bound="BaseQuery")


class BaseCommand(BaseModel):
    """基础命令类。

    所有写操作命令的基类，包含执行命令所需的上下文信息。
    """
    tenant_id: str = Field(description="租户ID")
    requested_by: Optional[str] = Field(default=None, description="请求者")
    correlation_id: Optional[str] = Field(default=None, description="关联ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class BaseQuery(BaseModel):
    """基础查询类。

    所有读操作查询的基类，包含查询参数和分页信息。
    """
    tenant_id: str = Field(description="租户ID")
    skip: int = Field(default=0, ge=0, description="跳过记录数")
    limit: int = Field(default=100, ge=1, le=1000, description="限制记录数")
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: str = Field(default="asc", regex="^(asc|desc)$", description="排序方向")


class CommandResult(BaseModel, Generic[T]):
    """命令执行结果。

    封装命令执行后的结果，包括成功/失败状态、数据和错误信息。
    """
    success: bool = Field(description="是否成功")
    data: Optional[T] = Field(default=None, description="返回数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    message: Optional[str] = Field(default=None, description="提示信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    events: List["DomainEvent"] = Field(default_factory=list, description="产生的事件")

    @classmethod
    def success_result(
        cls,
        data: Optional[T] = None,
        message: Optional[str] = None,
        **metadata
    ) -> "CommandResult[T]":
        """创建成功结果。"""
        return cls(
            success=True,
            data=data,
            message=message,
            metadata=metadata
        )

    @classmethod
    def failure_result(
        cls,
        error: str,
        data: Optional[T] = None,
        **metadata
    ) -> "CommandResult[T]":
        """创建失败结果。"""
        return cls(
            success=False,
            data=data,
            error=error,
            metadata=metadata
        )


class QueryResult(BaseModel, Generic[T]):
    """查询执行结果。

    封装查询执行后的结果，包括数据和分页信息。
    """
    success: bool = Field(default=True, description="是否成功")
    data: Optional[T] = Field(default=None, description="返回数据")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    size: int = Field(default=100, description="每页大小")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    @classmethod
    def success_result(
        cls,
        data: Optional[T] = None,
        total: int = 0,
        page: int = 1,
        size: int = 100,
        **metadata
    ) -> "QueryResult[T]":
        """创建成功结果。"""
        return cls(
            success=True,
            data=data,
            total=total,
            page=page,
            size=size,
            metadata=metadata
        )


class DomainEvent(BaseModel):
    """领域事件基类。

    表示领域中发生的重要事件，可用于事件溯源和集成。
    """
    event_id: str = Field(description="事件ID")
    event_type: str = Field(description="事件类型")
    aggregate_id: Union[str, UUID] = Field(description="聚合根ID")
    tenant_id: str = Field(description="租户ID")
    timestamp: float = Field(description="时间戳")
    version: int = Field(default=1, description="版本号")
    data: Dict[str, Any] = Field(default_factory=dict, description="事件数据")


class ICommandHandler(ABC, Generic[C, T]):
    """命令处理器接口。

    定义处理命令的接口。
    """

    @abstractmethod
    async def handle(self, command: C) -> CommandResult[T]:
        """处理命令。

        Args:
            command: 要处理的命令

        Returns:
            命令执行结果
        """
        pass


class IQueryHandler(ABC, Generic[Q, T]):
    """查询处理器接口。

    定义处理查询的接口。
    """

    @abstractmethod
    async def handle(self, query: Q) -> QueryResult[T]:
        """处理查询。

        Args:
            query: 要处理的查询

        Returns:
            查询执行结果
        """
        pass


class IEventHandler(ABC):
    """事件处理器接口。

    定义处理领域事件的接口。
    """

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """处理事件。

        Args:
            event: 要处理的事件
        """
        pass


class EventBus(ABC):
    """事件总线抽象类。

    定义发布和订阅事件的接口。
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """发布事件。

        Args:
            event: 要发布的事件
        """
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler: IEventHandler) -> None:
        """订阅事件。

        Args:
            event_type: 事件类型
            handler: 事件处理器
        """
        pass