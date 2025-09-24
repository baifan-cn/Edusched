"""日志服务主类。"""

from typing import Optional, Dict, Any, List
import logging

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .interfaces import (
    LoggingServiceInterface,
    LogConfig,
    LogRecord,
    LogQuery,
    LogStats,
    LogLevel,
    LogProvider
)
from .providers import ConsoleLoggingService, FileLoggingService

logger = logging.getLogger(__name__)


class LoggingService(BaseService, LoggingServiceInterface):
    """日志服务。"""

    def __init__(self, config: ServiceConfig, log_config: LogConfig):
        super().__init__("logging", config)
        self.log_config = log_config
        self._provider: Optional[LoggingServiceInterface] = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.LOGGING

    async def initialize(self) -> None:
        """初始化日志服务。"""
        try:
            # 根据配置创建提供商实例
            if self.log_config.provider == LogProvider.CONSOLE:
                self._provider = ConsoleLoggingService(self.config, self.log_config)
            elif self.log_config.provider == LogProvider.FILE:
                self._provider = FileLoggingService(self.config, self.log_config)
            elif self.log_config.provider == LogProvider.ELASTICSEARCH:
                # TODO: 实现 Elasticsearch 日志服务
                raise ExternalServiceError("Elasticsearch 日志服务尚未实现", self.service_name)
            elif self.log_config.provider == LogProvider.SENTRY:
                # TODO: 实现 Sentry 日志服务
                raise ExternalServiceError("Sentry 日志服务尚未实现", self.service_name)
            else:
                raise ExternalServiceError(
                    f"不支持的日志服务提供商: {self.log_config.provider}",
                    self.service_name
                )

            await self._provider.initialize()
            self.logger.info(f"日志服务初始化成功，提供商: {self.log_config.provider.value}")

        except Exception as e:
            raise ExternalServiceError(
                f"日志服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        if not self._provider:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = "日志服务未初始化"
            self._health.last_check = datetime.now()
            return self._health

        try:
            provider_health = await self._provider.health_check()
            self._health = provider_health
            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"日志服务异常: {str(e)}"
            self._health.last_check = datetime.now()
            return self._health

    async def log(self, record: LogRecord) -> None:
        """记录日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.log, record)

    async def debug(self, message: str, **kwargs) -> None:
        """记录 DEBUG 级别日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.debug, message, **kwargs)

    async def info(self, message: str, **kwargs) -> None:
        """记录 INFO 级别日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.info, message, **kwargs)

    async def warning(self, message: str, **kwargs) -> None:
        """记录 WARNING 级别日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.warning, message, **kwargs)

    async def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 ERROR 级别日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.error,
            message,
            exception,
            **kwargs
        )

    async def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 CRITICAL 级别日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.critical,
            message,
            exception,
            **kwargs
        )

    async def query_logs(self, query: LogQuery) -> List[LogRecord]:
        """查询日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.query_logs, query)

    async def get_log_stats(self, start_time: datetime, end_time: datetime) -> LogStats:
        """获取日志统计信息。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.get_log_stats,
            start_time,
            end_time
        )

    async def create_alert(
        self,
        name: str,
        condition: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> str:
        """创建告警规则。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.create_alert,
            name,
            condition,
            actions
        )

    async def delete_alert(self, alert_id: str) -> bool:
        """删除告警规则。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.delete_alert, alert_id)

    async def list_alerts(self) -> List[Dict[str, Any]]:
        """列出告警规则。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.list_alerts)

    async def export_logs(
        self,
        query: LogQuery,
        format: str = "json",
        compression: Optional[str] = None
    ) -> bytes:
        """导出日志。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.export_logs,
            query,
            format,
            compression
        )

    async def flush(self) -> None:
        """刷新日志缓冲区。"""
        if not self._provider:
            raise ExternalServiceError("日志服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.flush)

    async def close(self) -> None:
        """关闭日志服务。"""
        if self._provider:
            try:
                await self._provider.close()
            except Exception as e:
                self.logger.error(f"关闭日志服务提供商时出错: {e}")
            self._provider = None

    def get_provider(self) -> Optional[LoggingServiceInterface]:
        """获取当前日志服务提供商。"""
        return self._provider

    def change_provider(self, new_config: LogConfig) -> None:
        """切换日志服务提供商。"""
        if self._provider:
            raise ExternalServiceError(
                "请先关闭当前提供商再切换",
                self.service_name
            )

        self.log_config = new_config
        self.logger.info(f"已切换日志服务提供商配置: {new_config.provider.value}")

    def create_child_logger(self, name: str) -> "LoggingService":
        """创建子日志记录器。"""
        child_config = LogConfig(
            provider=self.log_config.provider,
            level=self.log_config.level,
            format=self.log_config.format,
            enabled=self.log_config.enabled,
            file_path=self.log_config.file_path,
            max_file_size=self.log_config.max_file_size,
            backup_count=self.log_config.backup_count,
            encoding=self.log_config.encoding
        )
        return LoggingService(self.config, child_config)


# 需要在文件顶部添加导入
from datetime import datetime
from ..base import ServiceStatus