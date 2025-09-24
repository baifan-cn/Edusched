"""缓存服务主类。"""

from typing import Optional, Dict, Any, List, AsyncIterator
import logging

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .interfaces import (
    CacheServiceInterface,
    CacheConfig,
    CacheItem,
    CacheStats,
    CacheProvider,
    CacheStrategy,
    CachePipeline,
    CacheLock
)
from .providers import RedisCacheService

logger = logging.getLogger(__name__)


class CacheService(BaseService, CacheServiceInterface):
    """缓存服务。"""

    def __init__(self, config: ServiceConfig, cache_config: CacheConfig):
        super().__init__("cache", config)
        self.cache_config = cache_config
        self._provider: Optional[CacheServiceInterface] = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.CACHE

    async def initialize(self) -> None:
        """初始化缓存服务。"""
        try:
            # 根据配置创建提供商实例
            if self.cache_config.provider == CacheProvider.REDIS:
                self._provider = RedisCacheService(self.config, self.cache_config)
            elif self.cache_config.provider == CacheProvider.LOCAL:
                # TODO: 实现本地缓存服务
                raise ExternalServiceError("本地缓存服务尚未实现", self.service_name)
            elif self.cache_config.provider == CacheProvider.MEMCACHED:
                # TODO: 实现 Memcached 缓存服务
                raise ExternalServiceError("Memcached 缓存服务尚未实现", self.service_name)
            else:
                raise ExternalServiceError(
                    f"不支持的缓存服务提供商: {self.cache_config.provider}",
                    self.service_name
                )

            await self._provider.initialize()
            self.logger.info(f"缓存服务初始化成功，提供商: {self.cache_config.provider.value}")

        except Exception as e:
            raise ExternalServiceError(
                f"缓存服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        if not self._provider:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = "缓存服务未初始化"
            self._health.last_check = datetime.now()
            return self._health

        try:
            provider_health = await self._provider.health_check()
            self._health = provider_health
            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"缓存服务异常: {str(e)}"
            self._health.last_check = datetime.now()
            return self._health

    async def get(
        self,
        key: str,
        default: Any = None,
        use_local_cache: bool = True
    ) -> Any:
        """获取缓存值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.get,
            key,
            default,
            use_local_cache
        )

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_local_cache: bool = True
    ) -> bool:
        """设置缓存值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.set,
            key,
            value,
            ttl,
            use_local_cache
        )

    async def delete(self, key: str) -> bool:
        """删除缓存值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.delete, key)

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.exists, key)

    async def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.expire, key, ttl)

    async def ttl(self, key: str) -> Optional[int]:
        """获取剩余TTL。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.ttl, key)

    async def persist(self, key: str) -> bool:
        """移除过期时间。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.persist, key)

    async def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """递增数值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.increment, key, delta)

    async def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        """递减数值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.decrement, key, delta)

    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.clear_pattern, pattern)

    async def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.get_multiple, keys)

    async def set_multiple(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.set_multiple, mapping, ttl)

    async def delete_multiple(self, keys: List[str]) -> int:
        """批量删除缓存值。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.delete_multiple, keys)

    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.keys, pattern)

    async def scan(self, pattern: str = "*", count: int = 100) -> AsyncIterator[str]:
        """扫描匹配模式的键。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        # 对于扫描操作，直接调用提供商方法
        return self._provider.scan(pattern, count)

    async def get_stats(self) -> CacheStats:
        """获取缓存统计信息。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.get_stats)

    async def clear_all(self) -> bool:
        """清空所有缓存。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.clear_all)

    async def info(self) -> Dict[str, Any]:
        """获取缓存服务信息。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.info)

    async def pipeline(self) -> CachePipeline:
        """创建管道对象。"""
        if not self._provider:
            raise ExternalServiceError("缓存服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.pipeline)

    async def close(self) -> None:
        """关闭缓存服务。"""
        if self._provider:
            try:
                await self._provider.close()
            except Exception as e:
                self.logger.error(f"关闭缓存服务提供商时出错: {e}")
            self._provider = None

    def get_provider(self) -> Optional[CacheServiceInterface]:
        """获取当前缓存服务提供商。"""
        return self._provider

    def change_provider(self, new_config: CacheConfig) -> None:
        """切换缓存服务提供商。"""
        if self._provider:
            raise ExternalServiceError(
                "请先关闭当前提供商再切换",
                self.service_name
            )

        self.cache_config = new_config
        self.logger.info(f"已切换缓存服务提供商配置: {new_config.provider.value}")

    def create_lock(self, key: str, timeout: int = 30) -> CacheLock:
        """创建缓存锁。"""
        return CacheLock(self, key, timeout)

    async def cached_decorator(
        self,
        ttl: Optional[int] = None,
        key_prefix: str = "",
        ignore_args: Optional[List[int]] = None,
        ignore_kwargs: Optional[List[str]] = None
    ):
        """缓存装饰器工厂方法。"""
        from .interfaces import make_cache_key

        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = make_cache_key(
                    func.__module__,
                    func.__name__,
                    key_prefix,
                    args,
                    kwargs,
                    ignore_args,
                    ignore_kwargs
                )

                # 尝试从缓存获取
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # 执行函数
                result = await func(*args, **kwargs)

                # 存入缓存
                await self.set(cache_key, result, ttl)

                return result

            def sync_wrapper(*args, **kwargs):
                # 同步版本简化实现
                return func(*args, **kwargs)

            # 根据函数类型返回相应的包装器
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator


# 需要在文件顶部添加导入
import asyncio
from datetime import datetime
from ..base import ServiceStatus