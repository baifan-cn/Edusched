"""通用数据传输对象。

包含分页、排序、过滤等通用DTO定义。
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """分页参数DTO。"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页大小")

    @property
    def skip(self) -> int:
        """跳过记录数。"""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """限制记录数。"""
        return self.size


class SortParams(BaseModel):
    """排序参数DTO。"""
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: str = Field(default="asc", regex="^(asc|desc)$", description="排序方向")


class FilterParams(BaseModel):
    """过滤参数DTO。"""
    keyword: Optional[str] = Field(default=None, description="关键词搜索")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应DTO。"""
    items: List[T] = Field(description="数据列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页大小")
    pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ) -> "PaginatedResponse[T]":
        """创建分页响应。"""
        pages = (total + size - 1) // size
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class ApiResponse(BaseModel, Generic[T]):
    """API响应DTO。"""
    success: bool = Field(description="是否成功")
    data: Optional[T] = Field(default=None, description="响应数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    message: Optional[str] = Field(default=None, description="提示信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    @classmethod
    def success(
        cls,
        data: Optional[T] = None,
        message: Optional[str] = None,
        **metadata
    ) -> "ApiResponse[T]":
        """创建成功响应。"""
        return cls(
            success=True,
            data=data,
            message=message,
            metadata=metadata
        )

    @classmethod
    def failure(
        cls,
        error: str,
        data: Optional[T] = None,
        **metadata
    ) -> "ApiResponse[T]":
        """创建失败响应。"""
        return cls(
            success=False,
            data=data,
            error=error,
            metadata=metadata
        )


class ValidationErrorDetail(BaseModel):
    """验证错误详情DTO。"""
    field: str = Field(description="字段名")
    message: str = Field(description="错误消息")
    value: Any = Field(description="错误值")


class ValidationErrorResponse(BaseModel):
    """验证错误响应DTO。"""
    error: str = Field(default="Validation failed", description="错误类型")
    details: List[ValidationErrorDetail] = Field(description="错误详情")


class BulkOperationResult(BaseModel):
    """批量操作结果DTO。"""
    success_count: int = Field(description="成功数量")
    failure_count: int = Field(description="失败数量")
    total_count: int = Field(description="总数量")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="结果列表")


class BulkCreateRequest(BaseModel, Generic[T]):
    """批量创建请求DTO。"""
    items: List[T] = Field(description="创建项列表")


class BulkUpdateRequest(BaseModel, Generic[T]):
    """批量更新请求DTO。"""
    items: List[T] = Field(description="更新项列表")


class BulkDeleteRequest(BaseModel):
    """批量删除请求DTO。"""
    ids: List[UUID] = Field(description="要删除的ID列表")


class ExportRequest(BaseModel):
    """导出请求DTO。"""
    format: str = Field(default="csv", regex="^(csv|excel|pdf|json)$", description="导出格式")
    include_headers: bool = Field(default=True, description="是否包含表头")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")
    columns: Optional[List[str]] = Field(default=None, description="导出列")


class ExportResponse(BaseModel):
    """导出响应DTO。"""
    file_id: str = Field(description="文件ID")
    file_name: str = Field(description="文件名")
    file_size: int = Field(description="文件大小")
    download_url: str = Field(description="下载链接")
    expires_at: str = Field(description="过期时间")


class ImportRequest(BaseModel):
    """导入请求DTO。"""
    file_id: str = Field(description="文件ID")
    mapping: Dict[str, str] = Field(description="字段映射")
    skip_errors: bool = Field(default=False, description="是否跳过错误")
    update_existing: bool = Field(default=False, description="是否更新已存在")


class ImportResponse(BaseModel):
    """导入响应DTO。"""
    success_count: int = Field(description="成功数量")
    failure_count: int = Field(description="失败数量")
    total_count: int = Field(description="总数量")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误详情")


class SearchQuery(BaseModel):
    """搜索查询DTO。"""
    keyword: Optional[str] = Field(default=None, description="关键词")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")
    pagination: PaginationParams = Field(default_factory=PaginationParams, description="分页参数")
    sort: SortParams = Field(default_factory=SortParams, description="排序参数")


class SearchResult(BaseModel, Generic[T]):
    """搜索结果DTO。"""
    items: List[T] = Field(description="搜索结果")
    total: int = Field(description="总结果数")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页大小")
    suggestions: List[str] = Field(default_factory=list, description="搜索建议")
    facets: Dict[str, Any] = Field(default_factory=dict, description="分面信息")


class HealthCheckResponse(BaseModel):
    """健康检查响应DTO。"""
    status: str = Field(description="服务状态")
    timestamp: str = Field(description="检查时间")
    version: str = Field(description="版本号")
    services: Dict[str, Any] = Field(description="服务状态详情")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ErrorResponse(BaseModel):
    """错误响应DTO。"""
    error: str = Field(description="错误类型")
    message: str = Field(description="错误消息")
    code: int = Field(description="错误代码")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    stack_trace: Optional[str] = Field(default=None, description="堆栈跟踪")
    request_id: Optional[str] = Field(default=None, description="请求ID")