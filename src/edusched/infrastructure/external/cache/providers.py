"""缓存服务提供商实现。"""

import asyncio
import json
import pickle
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, AsyncIterator
import threading
from collections import OrderedDict
import zlib
import fnmatch

import redis.asyncio as redis
from redis.exceptions import RedisError

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


class RedisCacheService(BaseService, CacheServiceInterface):
    """Redis 缓存服务。"""

    def __init__(self, config: ServiceConfig, cache_config: CacheConfig):
        super().__init__("redis_cache", config)
        self.cache_config = cache_config
        self._redis: Optional[redis.Redis] = None
        self._local_cache: OrderedDict = OrderedDict()
        self._stats = CacheStats()
        self._lock = threading.Lock()

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.CACHE

    async def initialize(self) -> None:
        """初始化 Redis 缓存服务。"""
        try:
            # 创建 Redis 连接池
            if self.cache_config.redis_url:
                self._redis = redis.ConnectionPool.from_url(
                    self.cache_config.redis_url,
                    max_connections=self.cache_config.redis_max_connections,
                    retry_on_timeout=True,
                    socket_timeout=self.cache_config.redis_socket_timeout,
                    socket_connect_timeout=self.cache_config.redis_socket_connect_timeout
                )
            else:
                raise ExternalServiceError("Redis URL 未配置", self.service_name)

            # 测试连接
            redis_client = redis.Redis(connection_pool=self._redis)
            await redis_client.ping()

            self.logger.info("Redis 缓存服务初始化成功")

        except Exception as e:
            raise ExternalServiceError(
                f"Redis 缓存服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        try:
            start_time = datetime.now()

            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                await redis_client.ping()

            response_time = (datetime.now() - start_time).total_seconds()

            self._health.status = ServiceStatus.HEALTHY
            self._health.message = "Redis 缓存服务正常"
            self._health.response_time = response_time
            self._health.last_check = datetime.now()

            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"Redis 缓存服务异常: {str(e)}"
            self._health.last_check = datetime.now()

            return self._health

    def _serialize(self, value: Any) -> bytes:
        """序列化值。"""
        try:
            if self.cache_config.serializer == "pickle":
                data = pickle.dumps(value)
            elif self.cache_config.serializer == "json":
                data = json.dumps(value, ensure_ascii=False).encode("utf-8")
            elif self.cache_config.serializer == "msgpack":
                import msgpack
                data = msgpack.packb(value)
            else:
                data = str(value).encode("utf-8")

            # 压缩
            if self.cache_config.compression and len(data) > self.cache_config.compression_threshold:
                data = zlib.compress(data)

            return data

        except Exception as e:
            raise ExternalServiceError(f"序列化失败: {str(e)}", self.service_name)

    def _deserialize(self, data: bytes) -> Any:
        """反序列化值。"""
        try:
            # 解压缩
            if self.cache_config.compression:
                try:
                    data = zlib.decompress(data)
                except:
                    pass  # 可能不是压缩的数据

            if self.cache_config.serializer == "pickle":
                return pickle.loads(data)
            elif self.cache_config.serializer == "json":
                return json.loads(data.decode("utf-8"))
            elif self.cache_config.serializer == "msgpack":
                import msgpack
                return msgpack.unpackb(data)
            else:
                return data.decode("utf-8")

        except Exception as e:
            raise ExternalServiceError(f"反序列化失败: {str(e)}", self.service_name)

    def _add_ttl_jitter(self, ttl: Optional[int]) -> Optional[int]:
        """添加 TTL 抖动。"""
        if ttl and self.cache_config.ttl_jitter:
            jitter = int(ttl * self.cache_config.ttl_jitter_range * (time.random() * 2 - 1))
            return max(1, ttl + jitter)
        return ttl

    async def get(
        self,
        key: str,
        default: Any = None,
        use_local_cache: bool = True
    ) -> Any:
        """获取缓存值。"""
        try:
            # 先尝试本地缓存
            if use_local_cache and key in self._local_cache:
                item = self._local_cache[key]
                if not item.ttl or (datetime.now() - item.created_at).total_seconds() < item.ttl:
                    # 更新访问记录
                    item.access_count += 1
                    # LRU 策略：移到末尾
                    with self._lock:
                        self._local_cache.move_to_end(key)
                    self._stats.hits += 1
                    return item.value
                else:
                    # 过期，删除
                    with self._lock:
                        del self._local_cache[key]

            # 从 Redis 获取
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                data = await redis_client.get(key)

                if data is not None:
                    # 处理空值缓存
                    if data == b"__NULL__" and self.cache_config.cache_null_values:
                        self._stats.hits += 1
                        return None

                    value = self._deserialize(data)

                    # 更新本地缓存
                    if use_local_cache:
                        ttl = await redis_client.ttl(key)
                        if ttl > 0:
                            with self._lock:
                                self._local_cache[key] = CacheItem(
                                    key=key,
                                    value=value,
                                    ttl=ttl,
                                    created_at=datetime.now()
                                )
                                # LRU 策略
                                self._local_cache.move_to_end(key)

                                # 限制本地缓存大小
                                if len(self._local_cache) > self.cache_config.local_max_size:
                                    self._local_cache.popitem(last=False)

                    self._stats.hits += 1
                    return value

            self._stats.misses += 1
            return default

        except Exception as e:
            self.logger.error(f"获取缓存失败 {key}: {e}")
            self._stats.misses += 1
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_local_cache: bool = True
    ) -> bool:
        """设置缓存值。"""
        try:
            # 处理空值缓存
            if value is None and self.cache_config.cache_null_values:
                data = b"__NULL__"
            else:
                data = self._serialize(value)

            # 添加 TTL 抖动
            ttl = self._add_ttl_jitter(ttl or self.cache_config.default_ttl)

            # 设置到 Redis
            success = True
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                if ttl:
                    await redis_client.setex(key, ttl, data)
                else:
                    await redis_client.set(key, data)

            # 更新本地缓存
            if use_local_cache:
                with self._lock:
                    self._local_cache[key] = CacheItem(
                        key=key,
                        value=value,
                        ttl=ttl,
                        created_at=datetime.now()
                    )
                    # LRU 策略
                    self._local_cache.move_to_end(key)

                    # 限制本地缓存大小
                    if len(self._local_cache) > self.cache_config.local_max_size:
                        self._local_cache.popitem(last=False)

            self._stats.sets += 1
            return success

        except Exception as e:
            self.logger.error(f"设置缓存失败 {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值。"""
        try:
            # 从 Redis 删除
            success = True
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                result = await redis_client.delete(key)
                success = result > 0

            # 从本地缓存删除
            with self._lock:
                if key in self._local_cache:
                    del self._local_cache[key]

            self._stats.deletes += 1
            return success

        except Exception as e:
            self.logger.error(f"删除缓存失败 {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        try:
            # 先检查本地缓存
            if key in self._local_cache:
                item = self._local_cache[key]
                if not item.ttl or (datetime.now() - item.created_at).total_seconds() < item.ttl:
                    return True
                else:
                    # 过期，删除
                    with self._lock:
                        del self._local_cache[key]

            # 检查 Redis
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.exists(key) > 0

            return False

        except Exception as e:
            self.logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间。"""
        try:
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                ttl = self._add_ttl_jitter(ttl)
                return await redis_client.expire(key, ttl)
            return False
        except Exception as e:
            self.logger.error(f"设置过期时间失败 {key}: {e}")
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """获取剩余TTL。"""
        try:
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.ttl(key)
            return None
        except Exception as e:
            self.logger.error(f"获取TTL失败 {key}: {e}")
            return None

    async def persist(self, key: str) -> bool:
        """移除过期时间。"""
        try:
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.persist(key)
            return False
        except Exception as e:
            self.logger.error(f"移除过期时间失败 {key}: {e}")
            return False

    async def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """递增数值。"""
        try:
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.incrby(key, delta)
            return None
        except Exception as e:
            self.logger.error(f"递增失败 {key}: {e}")
            return None

    async def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        """递减数值。"""
        try:
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                return await redis_client.decrby(key, delta)
            return None
        except Exception as e:
            self.logger.error(f"递减失败 {key}: {e}")
            return None

    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存。"""
        try:
            cleared_count = 0

            # 清除本地缓存
            with self._lock:
                keys_to_delete = [
                    key for key in self._local_cache.keys()
                    if fnmatch.fnmatch(key, pattern)
                ]
                for key in keys_to_delete:
                    del self._local_cache[key]
                cleared_count += len(keys_to_delete)

            # 清除 Redis 缓存
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                keys = []
                async for key in redis_client.scan_iter(match=pattern):
                    keys.append(key)

                if keys:
                    cleared_count += await redis_client.delete(*keys)

            return cleared_count

        except Exception as e:
            self.logger.error(f"清除模式缓存失败 {pattern}: {e}")
            return 0

    async def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值。"""
        result = {}
        for key in keys:
            value = await self.get(key)
            result[key] = value
        return result

    async def set_multiple(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存值。"""
        success = True
        for key, value in mapping.items():
            if not await self.set(key, value, ttl):
                success = False
        return success

    async def delete_multiple(self, keys: List[str]) -> int:
        """批量删除缓存值。"""
        deleted_count = 0
        for key in keys:
            if await self.delete(key):
                deleted_count += 1
        return deleted_count

    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键。"""
        try:
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                return [key.decode() for key in await redis_client.keys(pattern)]
            return []
        except Exception as e:
            self.logger.error(f"获取键失败 {pattern}: {e}")
            return []

    async def scan(self, pattern: str = "*", count: int = 100) -> AsyncIterator[str]:
        """扫描匹配模式的键。"""
        if self._redis:
            redis_client = redis.Redis(connection_pool=self._redis)
            async for key in redis_client.scan_iter(match=pattern, count=count):
                yield key.decode()

    async def get_stats(self) -> CacheStats:
        """获取缓存统计信息。"""
        # 更新命中率
        self._stats.update_hit_rate()

        # 获取 Redis 统计信息
        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                info = await redis_client.info()
                self._stats.total_memory = info.get("used_memory", 0)
                self._stats.evictions = info.get("evicted_keys", 0)
            except:
                pass

        return self._stats

    async def clear_all(self) -> bool:
        """清空所有缓存。"""
        try:
            # 清空本地缓存
            with self._lock:
                self._local_cache.clear()

            # 清空 Redis
            if self._redis:
                redis_client = redis.Redis(connection_pool=self._redis)
                await redis_client.flushdb()

            return True

        except Exception as e:
            self.logger.error(f"清空缓存失败: {e}")
            return False

    async def info(self) -> Dict[str, Any]:
        """获取缓存服务信息。"""
        info = {
            "provider": "redis",
            "local_cache_size": len(self._local_cache),
            "local_cache_max_size": self.cache_config.local_max_size,
            "config": {
                "default_ttl": self.cache_config.default_ttl,
                "strategy": self.cache_config.strategy.value,
                "serializer": self.cache_config.serializer,
                "compression": self.cache_config.compression
            }
        }

        if self._redis:
            try:
                redis_client = redis.Redis(connection_pool=self._redis)
                redis_info = await redis_client.info()
                info.update({
                    "redis_version": redis_info.get("redis_version"),
                    "connected_clients": redis_info.get("connected_clients"),
                    "used_memory": redis_info.get("used_memory"),
                    "keyspace_hits": redis_info.get("keyspace_hits"),
                    "keyspace_misses": redis_info.get("keyspace_misses")
                })
            except:
                pass

        return info

    async def pipeline(self) -> "CachePipeline":
        """创建管道对象。"""
        return RedisCachePipeline(self)


class RedisCachePipeline(CachePipeline):
    """Redis 缓存管道。"""

    def __init__(self, cache_service: RedisCacheService):
        self.cache = cache_service
        self._commands: List[tuple] = []
        self._redis = cache_service._redis

    async def get(self, key: str) -> "CachePipeline":
        """添加获取操作。"""
        self._commands.append(("get", key))
        return self

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> "CachePipeline":
        """添加设置操作。"""
        data = self.cache._serialize(value)
        self._commands.append(("set", key, data, ttl))
        return self

    async def delete(self, key: str) -> "CachePipeline":
        """添加删除操作。"""
        self._commands.append(("delete", key))
        return self

    async def increment(self, key: str, delta: int = 1) -> "CachePipeline":
        """添加递增操作。"""
        self._commands.append(("increment", key, delta))
        return self

    async def execute(self) -> List[Any]:
        """执行管道中的所有操作。"""
        if not self._redis:
            return []

        redis_client = redis.Redis(connection_pool=self._redis)
        pipe = redis_client.pipeline()

        for cmd in self._commands:
            if cmd[0] == "get":
                pipe.get(cmd[1])
            elif cmd[0] == "set":
                if cmd[3]:  # ttl
                    pipe.setex(cmd[1], cmd[3], cmd[2])
                else:
                    pipe.set(cmd[1], cmd[2])
            elif cmd[0] == "delete":
                pipe.delete(cmd[1])
            elif cmd[0] == "increment":
                pipe.incrby(cmd[1], cmd[2])

        results = await pipe.execute()

        # 反序列化结果
        final_results = []
        for i, (cmd, result) in enumerate(zip(self._commands, results)):
            if cmd[0] == "get" and result is not None:
                try:
                    final_results.append(self.cache._deserialize(result))
                except:
                    final_results.append(None)
            else:
                final_results.append(result)

        return final_results


# 需要在文件顶部添加导入
import time
from ..base import ServiceStatus