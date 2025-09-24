"""外部服务集成模块基础抽象。

提供外部服务的统一接口和基础实现。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging


class ServiceStatus(Enum):
    """服务状态枚举。"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"


class ServiceType(Enum):
    """服务类型枚举。"""
    EMAIL = "email"
    NOTIFICATION = "notification"
    STORAGE = "storage"
    LOGGING = "logging"
    CACHE = "cache"


@dataclass
class ServiceConfig:
    """服务配置基类。"""
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    extra_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """服务健康状态。"""
    status: ServiceStatus
    message: str = ""
    last_check: datetime = field(default_factory=datetime.now)
    response_time: Optional[float] = None
    error_count: int = 0
    consecutive_errors: int = 0


@dataclass
class ServiceMetrics:
    """服务指标。"""
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    last_request_time: Optional[datetime] = None


class ExternalServiceError(Exception):
    """外部服务异常基类。"""

    def __init__(
        self,
        message: str,
        service_name: str,
        error_code: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        self.service_name = service_name
        self.error_code = error_code
        self.original_error = original_error
        super().__init__(f"[{service_name}] {message}")


class ServiceTimeoutError(ExternalServiceError):
    """服务超时异常。"""
    pass


class ServiceRateLimitError(ExternalServiceError):
    """服务限流异常。"""
    pass


class ServiceAuthenticationError(ExternalServiceError):
    """服务认证异常。"""
    pass


class BaseService(ABC):
    """外部服务基类。"""

    def __init__(self, service_name: str, config: ServiceConfig):
        self.service_name = service_name
        self.config = config
        self.logger = logging.getLogger(f"edusched.external.{service_name}")
        self._health = ServiceHealth(status=ServiceStatus.HEALTHY)
        self._metrics = ServiceMetrics()
        self._circuit_breaker_errors = 0
        self._circuit_breaker_until = None

    @property
    @abstractmethod
    def service_type(self) -> ServiceType:
        """服务类型。"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """初始化服务。"""
        pass

    @abstractmethod
    async def health_check(self) -> ServiceHealth:
        """健康检查。"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭服务连接。"""
        pass

    def _check_circuit_breaker(self) -> bool:
        """检查熔断器状态。"""
        if self._circuit_breaker_until and datetime.now() < self._circuit_breaker_until:
            self.logger.warning(f"服务 {self.service_name} 处于熔断状态")
            return False

        if self._circuit_breaker_errors >= self.config.circuit_breaker_threshold:
            self._circuit_breaker_until = datetime.now() + timedelta(
                seconds=self.config.circuit_breaker_timeout
            )
            self._circuit_breaker_errors = 0
            self.logger.warning(
                f"服务 {self.service_name} 触发熔断器，将在 {self.config.circuit_breaker_timeout} 秒后恢复"
            )
            return False

        return True

    def _record_success(self, response_time: float) -> None:
        """记录成功请求。"""
        self._metrics.request_count += 1
        self._metrics.success_count += 1
        self._metrics.total_response_time += response_time
        self._metrics.last_request_time = datetime.now()
        self._health.consecutive_errors = 0

    def _record_error(self, error: Exception, response_time: float) -> None:
        """记录错误请求。"""
        self._metrics.request_count += 1
        self._metrics.error_count += 1
        self._metrics.total_response_time += response_time
        self._metrics.last_request_time = datetime.now()
        self._health.error_count += 1
        self._health.consecutive_errors += 1

        # 更新熔断器计数
        if isinstance(error, (ServiceTimeoutError, ServiceRateLimitError)):
            self._circuit_breaker_errors += 1

        # 更新健康状态
        if self._health.consecutive_errors >= 3:
            self._health.status = ServiceStatus.DEGRADED
        if self._health.consecutive_errors >= 5:
            self._health.status = ServiceStatus.UNAVAILABLE

    async def _execute_with_retry(
        self,
        operation,
        *args,
        **kwargs
    ) -> Any:
        """带重试和熔断的执行包装器。"""
        if not self._check_circuit_breaker():
            raise ServiceTimeoutError(
                f"服务 {self.service_name} 暂时不可用（熔断器开启）",
                self.service_name
            )

        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = datetime.now()
                result = await operation(*args, **kwargs)
                response_time = (datetime.now() - start_time).total_seconds()

                self._record_success(response_time)
                return result

            except ExternalServiceError as e:
                response_time = (datetime.now() - start_time).total_seconds()
                self._record_error(e, response_time)

                if attempt == self.config.max_retries:
                    raise e

                self.logger.warning(
                    f"服务 {self.service_name} 操作失败（尝试 {attempt + 1}/{self.config.max_retries + 1}）: {e}"
                )
                last_error = e

                if not isinstance(e, (ServiceTimeoutError, ServiceRateLimitError)):
                    # 只有超时和限流错误才重试
                    break

                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds()
                wrapped_error = ExternalServiceError(
                    f"未知错误: {str(e)}",
                    self.service_name,
                    original_error=e
                )
                self._record_error(wrapped_error, response_time)
                raise wrapped_error

        if last_error:
            raise last_error

    def get_metrics(self) -> ServiceMetrics:
        """获取服务指标。"""
        return self._metrics

    def get_health(self) -> ServiceHealth:
        """获取服务健康状态。"""
        return self._health


# 需要在文件顶部添加导入
import asyncio
from datetime import timedelta