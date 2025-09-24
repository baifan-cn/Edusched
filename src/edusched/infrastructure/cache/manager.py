"""缓存管理模块。

提供Redis缓存功能，包括缓存策略、失效机制和性能优化。
"""

import json
import pickle
import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional, Union, List, Dict
from functools import wraps
import logging

import redis.asyncio as redis
from redis.exceptions import RedisError

from edusched.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheManager:
    """缓存管理器。"""

    def __init__(self):
        """初始化缓存管理器。"""
        self._redis: Optional[redis.Redis] = None
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self._local_cache_ttl: Dict[str, datetime] = {}

    async def initialize(self) -> None:
        """初始化Redis连接。"""
        if self._redis is not None:
            return

        try:
            # 创建Redis连接池
            self._redis = redis.ConnectionPool.from_url(
                settings.redis.url,
                max_connections=20,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )

            # 测试连接
            redis_client = redis.Redis(connection_pool=self._redis)
            await redis_client.ping()

            logger.info("Redis缓存连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败，将使用本地缓存: {e}")
            self._redis = None

    async def close(self) -> None:
        """关闭Redis连接。"""
        if self._redis:
            await self._redis.aclose()  # 修正方法名
            self._redis = None

    async def get(
        self,
        key: str,
        default: Any = None,
        use_local_cache: bool = True
    ) -> Any:
        """获取缓存值。"""
        # 先尝试本地缓存
        if use_local_cache and key in self._local_cache:
            if self._is_local_cache_valid(key):
                return self._local_cache[key]["value"]
            else:
                # 清理过期缓存
                del self._local_cache[key]
                if key in self._local_cache_ttl:
                    del self._local_cache_ttl[key]

        # 尝试Redis缓存
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                cached_data = await redis_client.get(key)

                if cached_data is not None:
                    # 反序列化数据
                    try:
                        value = pickle.loads(cached_data)

                        # 同时更新本地缓存
                        if use_local_cache:
                            self._set_local_cache(key, value, ttl=300)  # 本地缓存5分钟

                        return value
                    except (pickle.UnpicklingError, EOFError):
                        # 如果反序列化失败，尝试JSON解析
                        try:
                            value = json.loads(cached_data.decode('utf-8'))
                            if use_local_cache:
                                self._set_local_cache(key, value, ttl=300)
                            return value
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            logger.warning(f"缓存数据反序列化失败: {key}")
                            return default
            except RedisError as e:
                logger.warning(f"Redis GET操作失败: {e}")

        return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_local_cache: bool = True
    ) -> bool:
        """设置缓存值。"""
        success = False

        # 设置Redis缓存
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)

                # 序列化数据
                try:
                    serialized_data = pickle.dumps(value)
                except (pickle.PicklingError, TypeError):
                    # 如果pickle失败，使用JSON
                    try:
                        serialized_data = json.dumps(value, ensure_ascii=False).encode('utf-8')
                    except (TypeError, ValueError):
                        logger.warning(f"缓存数据序列化失败: {key}")
                        return False

                # 设置缓存
                if ttl:
                    await redis_client.setex(key, ttl, serialized_data)
                else:
                    await redis_client.set(key, serialized_data)

                success = True

                # 同时设置本地缓存
                if use_local_cache:
                    local_ttl = min(ttl or 3600, 300)  # 本地缓存最多5分钟
                    self._set_local_cache(key, value, local_ttl)

            except RedisError as e:
                logger.warning(f"Redis SET操作失败: {e}")

        # 如果Redis不可用，只设置本地缓存
        if not success and use_local_cache:
            local_ttl = ttl or 3600
            self._set_local_cache(key, value, local_ttl)
            success = True

        return success

    async def delete(self, key: str) -> bool:
        """删除缓存值。"""
        success = False

        # 删除Redis缓存
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                result = await redis_client.delete(key)
                success = result > 0
            except RedisError as e:
                logger.warning(f"Redis DELETE操作失败: {e}")

        # 删除本地缓存
        if key in self._local_cache:
            del self._local_cache[key]
        if key in self._local_cache_ttl:
            del self._local_cache_ttl[key]

        return success

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        # 检查本地缓存
        if key in self._local_cache and self._is_local_cache_valid(key):
            return True

        # 检查Redis缓存
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.exists(key) > 0
            except RedisError as e:
                logger.warning(f"Redis EXISTS操作失败: {e}")

        return False

    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存。"""
        cleared_count = 0

        # 清除本地缓存
        local_keys_to_delete = [
            key for key in self._local_cache.keys()
            if self._match_pattern(key, pattern)
        ]
        for key in local_keys_to_delete:
            del self._local_cache[key]
            if key in self._local_cache_ttl:
                del self._local_cache_ttl[key]
            cleared_count += 1

        # 清除Redis缓存
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                keys = []
                async for key in redis_client.scan_iter(match=pattern):
                    keys.append(key)

                if keys:
                    cleared_count += await redis_client.delete(*keys)
            except RedisError as e:
                logger.warning(f"Redis CLEAR_PATTERN操作失败: {e}")

        return cleared_count

    async def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """递增缓存值。"""
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.incrby(key, delta)
            except RedisError as e:
                logger.warning(f"Redis INCR操作失败: {e}")

        # Redis不可用时的本地实现
        current_value = await self.get(key, 0)
        if isinstance(current_value, int):
            new_value = current_value + delta
            await self.set(key, new_value)
            return new_value

        return None

    async def get_ttl(self, key: str) -> Optional[int]:
        """获取缓存TTL。"""
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.ttl(key)
            except RedisError as e:
                logger.warning(f"Redis TTL操作失败: {e}")

        # 本地缓存TTL
        if key in self._local_cache_ttl:
            remaining = (self._local_cache_ttl[key] - datetime.now()).total_seconds()
            return max(0, int(remaining))

        return None

    def _set_local_cache(self, key: str, value: Any, ttl: int) -> None:
        """设置本地缓存。"""
        self._local_cache[key] = {
            "value": value,
            "created_at": datetime.now()
        }

        if ttl > 0:
            self._local_cache_ttl[key] = datetime.now() + timedelta(seconds=ttl)

        # 定期清理过期缓存
        if len(self._local_cache) > 1000:  # 缓存项过多时清理
            self._cleanup_local_cache()

    def _is_local_cache_valid(self, key: str) -> bool:
        """检查本地缓存是否有效。"""
        if key not in self._local_cache_ttl:
            return True  # 没有设置TTL，永久有效

        return datetime.now() < self._local_cache_ttl[key]

    def _cleanup_local_cache(self) -> None:
        """清理过期的本地缓存。"""
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self._local_cache_ttl.items()
            if expiry < now
        ]

        for key in expired_keys:
            if key in self._local_cache:
                del self._local_cache[key]
            del self._local_cache_ttl[key]

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """检查键是否匹配模式。"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    use_local_cache: bool = True,
    ignore_args: Optional[List[int]] = None,
    ignore_kwargs: Optional[List[str]] = None
):
    """缓存装饰器。"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(
                func, key_prefix, args, kwargs, ignore_args, ignore_kwargs
            )

            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key, use_local_cache=use_local_cache)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result

            # 执行函数
            logger.debug(f"缓存未命中，执行函数: {cache_key}")
            result = await func(*args, **kwargs)

            # 存入缓存
            await cache_manager.set(cache_key, result, ttl, use_local_cache=use_local_cache)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步版本的缓存装饰器（简化实现）
            cache_key = _generate_cache_key(
                func, key_prefix, args, kwargs, ignore_args, ignore_kwargs
            )

            # 这里简化处理，实际中可能需要异步上下文
            return func(*args, **kwargs)

        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _generate_cache_key(
    func,
    key_prefix: str,
    args: tuple,
    kwargs: dict,
    ignore_args: Optional[List[int]] = None,
    ignore_kwargs: Optional[List[str]] = None
) -> str:
    """生成缓存键。"""
    # 函数名和模块名
    module_name = func.__module__
    func_name = func.__name__

    # 处理参数
    filtered_args = []
    for i, arg in enumerate(args):
        if ignore_args and i in ignore_args:
            continue
        filtered_args.append(repr(arg))

    filtered_kwargs = {}
    for k, v in kwargs.items():
        if ignore_kwargs and k in ignore_kwargs:
            continue
        filtered_kwargs[k] = repr(v)

    # 生成键
    key_parts = [key_prefix, module_name, func_name]
    if filtered_args:
        key_parts.append("args:" + ",".join(filtered_args))
    if filtered_kwargs:
        key_parts.append("kwargs:" + ",".join(f"{k}={v}" for k, v in filtered_kwargs.items()))

    return ":".join(key_parts)


async def init_cache() -> None:
    """初始化缓存。"""
    await cache_manager.initialize()


async def close_cache() -> None:
    """关闭缓存连接。"""
    await cache_manager.close()