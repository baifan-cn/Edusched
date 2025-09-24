"""缓存服务接口定义。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Union, List, Dict, AsyncIterator
from enum import Enum
from datetime import datetime, timedelta


class CacheProvider(Enum):
    """缓存服务提供商。"""
    REDIS = "redis"
    MEMCACHED = "memcached"
    LOCAL = "local"
    DYNAMODB = "dynamodb"


class CacheStrategy(Enum):
    """缓存策略。"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最不经常使用
    FIFO = "fifo"  # 先进先出
    TTL = "ttl"  # 基于时间


@dataclass
class CacheItem:
    """缓存项。"""
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CacheStats:
    """缓存统计信息。"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_memory: int = 0
    hit_rate: float = 0.0

    @property
    def total_requests(self) -> int:
        """总请求数。"""
        return self.hits + self.misses

    def update_hit_rate(self) -> None:
        """更新命中率。"""
        if self.total_requests > 0:
            self.hit_rate = self.hits / self.total_requests


@dataclass
class CacheConfig:
    """缓存服务配置。"""
    provider: CacheProvider
    default_ttl: int = 3600  # 默认TTL：1小时
    max_memory: Optional[int] = None  # 最大内存使用（字节）
    strategy: CacheStrategy = CacheStrategy.LRU

    # Redis 配置
    redis_url: Optional[str] = None
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_max_connections: int = 20
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5

    # Memcached 配置
    memcached_servers: Optional[List[str]] = None
    memcached_username: Optional[str] = None
    memcached_password: Optional[str] = None

    # 本地缓存配置
    local_max_size: int = 10000  # 本地缓存最大条目数
    local_cleanup_interval: int = 300  # 清理间隔（秒）

    # 序列化配置
    serializer: str = "pickle"  # pickle, json, msgpack
    compression: bool = True
    compression_threshold: int = 1024  # 压缩阈值（字节）

    # 分布式配置
    distributed_lock: bool = False
    lock_timeout: int = 30

    # 缓存穿透保护
    cache_null_values: bool = True
    null_value_ttl: int = 60  # 空值TTL（秒）

    # 缓存雪崩保护
    ttl_jitter: bool = True
    ttl_jitter_range: float = 0.1  # TTL抖动范围（0-1）


class CacheServiceInterface(ABC):
    """缓存服务接口。"""

    @abstractmethod
    async def get(
        self,
        key: str,
        default: Any = None,
        use_local_cache: bool = True
    ) -> Any:
        """获取缓存值。"""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_local_cache: bool = True
    ) -> bool:
        """设置缓存值。"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值。"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在。"""
        pass

    @abstractmethod
    async def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间。"""
        pass

    @abstractmethod
    async def ttl(self, key: str) -> Optional[int]:
        """获取剩余TTL。"""
        pass

    @abstractmethod
    async def persist(self, key: str) -> bool:
        """移除过期时间，使键永久存在。"""
        pass

    @abstractmethod
    async def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """递增数值。"""
        pass

    @abstractmethod
    async def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        """递减数值。"""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存。"""
        pass

    @abstractmethod
    async def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值。"""
        pass

    @abstractmethod
    async def set_multiple(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存值。"""
        pass

    @abstractmethod
    async def delete_multiple(self, keys: List[str]) -> int:
        """批量删除缓存值。"""
        pass

    @abstractmethod
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键。"""
        pass

    @abstractmethod
    async def scan(self, pattern: str = "*", count: int = 100) -> AsyncIterator[str]:
        """扫描匹配模式的键。"""
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """获取缓存统计信息。"""
        pass

    @abstractmethod
    async def clear_all(self) -> bool:
        """清空所有缓存。"""
        pass

    @abstractmethod
    async def info(self) -> Dict[str, Any]:
        """获取缓存服务信息。"""
        pass

    @abstractmethod
    async def pipeline(self) -> "CachePipeline":
        """创建管道对象。"""
        pass


class CachePipeline(ABC):
    """缓存管道。"""

    @abstractmethod
    async def get(self, key: str) -> "CachePipeline":
        """添加获取操作。"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> "CachePipeline":
        """添加设置操作。"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> "CachePipeline":
        """添加删除操作。"""
        pass

    @abstractmethod
    async def increment(self, key: str, delta: int = 1) -> "CachePipeline":
        """添加递增操作。"""
        pass

    @abstractmethod
    async def execute(self) -> List[Any]:
        """执行管道中的所有操作。"""
        pass


def make_cache_key(*args, **kwargs) -> str:
    """生成缓存键。"""
    parts = []
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            parts.append(str(arg))
        elif hasattr(arg, "__dict__"):
            # 对象使用其唯一标识
            parts.append(f"{arg.__class__.__name__}:{id(arg)}")
        else:
            # 其他对象使用其字符串表示
            parts.append(str(arg))

    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        for k, v in sorted_kwargs:
            parts.append(f"{k}={v}")

    return ":".join(parts)


class CacheLock:
    """缓存锁。"""

    def __init__(self, cache_service: CacheServiceInterface, key: str, timeout: int = 30):
        self.cache = cache_service
        self.key = f"lock:{key}"
        self.timeout = timeout
        self._token = None

    async def __aenter__(self):
        """进入异步上下文。"""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出异步上下文。"""
        await self.release()

    async def acquire(self) -> bool:
        """获取锁。"""
        import uuid
        self._token = str(uuid.uuid4())
        return await self.cache.set(self.key, self._token, self.timeout)

    async def release(self) -> bool:
        """释放锁。"""
        if self._token:
            # 使用 Lua 脚本确保原子性
            lua_script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
            """
            # 这里简化实现，实际应根据具体缓存服务实现
            await self.cache.delete(self.key)
            self._token = None
            return True
        return False

    async def is_locked(self) -> bool:
        """检查锁是否存在。"""
        return await self.cache.exists(self.key)