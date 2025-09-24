"""日志服务接口定义。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
import traceback
import json


class LogLevel(Enum):
    """日志级别。"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogFormat(Enum):
    """日志格式。"""
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"


class LogProvider(Enum):
    """日志服务提供商。"""
    CONSOLE = "console"
    FILE = "file"
    ELASTICSEARCH = "elasticsearch"
    LOGSTASH = "logstash"
    CLOUDWATCH = "cloudwatch"
    SENTRY = "sentry"
    DATADOG = "datadog"
    LOGLY = "loggly"
    PAPERTRAIL = "papertrail"


@dataclass
class LogRecord:
    """日志记录。"""
    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    logger_name: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    exception: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    request_id: Optional[str] = None
    tags: Optional[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "logger_name": self.logger_name,
            "module": self.module,
            "function": self.function,
            "line_number": self.line_number,
            "thread_id": self.thread_id,
            "process_id": self.process_id,
            "exception": self.exception,
            "extra": self.extra,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "request_id": self.request_id,
            "tags": self.tags
        }


@dataclass
class LogQuery:
    """日志查询条件。"""
    level: Optional[LogLevel] = None
    logger_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    message_pattern: Optional[str] = None
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    request_id: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 100
    offset: int = 0
    sort: str = "timestamp:desc"


@dataclass
class LogStats:
    """日志统计信息。"""
    total_count: int
    level_counts: Dict[LogLevel, int]
    time_range: Dict[str, datetime]
    top_loggers: List[Dict[str, Any]]
    top_errors: List[Dict[str, Any]]


@dataclass
class LogConfig:
    """日志服务配置。"""
    provider: LogProvider
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.JSON
    enabled: bool = True

    # 文件配置
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    encoding: str = "utf-8"

    # Elasticsearch 配置
    elasticsearch_hosts: Optional[List[str]] = None
    elasticsearch_index: str = "edusched-logs"
    elasticsearch_index_pattern: str = "edusched-logs-%Y.%m.%d"
    elasticsearch_username: Optional[str] = None
    elasticsearch_password: Optional[str] = None

    # 云服务配置
    cloudwatch_group: Optional[str] = None
    cloudwatch_stream: Optional[str] = None
    cloudwatch_region: Optional[str] = None

    # Sentry 配置
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None
    sentry_release: Optional[str] = None

    # Datadog 配置
    datadog_api_key: Optional[str] = None
    datadog_host: Optional[str] = None
    datadog_service: Optional[str] = None

    # 缓冲配置
    buffer_size: int = 1000
    flush_interval: int = 10  # 秒
    max_batch_size: int = 100

    # 采样配置
    sample_rate: float = 1.0  # 0.0-1.0
    ignore_patterns: Optional[List[str]] = None

    # 结构化日志配置
    include_context: bool = True
    include_stacktrace: bool = True
    max_stacktrace_frames: int = 20


class LoggingServiceInterface(ABC):
    """日志服务接口。"""

    @abstractmethod
    async def log(self, record: LogRecord) -> None:
        """记录日志。"""
        pass

    @abstractmethod
    async def debug(self, message: str, **kwargs) -> None:
        """记录 DEBUG 级别日志。"""
        pass

    @abstractmethod
    async def info(self, message: str, **kwargs) -> None:
        """记录 INFO 级别日志。"""
        pass

    @abstractmethod
    async def warning(self, message: str, **kwargs) -> None:
        """记录 WARNING 级别日志。"""
        pass

    @abstractmethod
    async def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 ERROR 级别日志。"""
        pass

    @abstractmethod
    async def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 CRITICAL 级别日志。"""
        pass

    @abstractmethod
    async def query_logs(self, query: LogQuery) -> List[LogRecord]:
        """查询日志。"""
        pass

    @abstractmethod
    async def get_log_stats(self, start_time: datetime, end_time: datetime) -> LogStats:
        """获取日志统计信息。"""
        pass

    @abstractmethod
    async def create_alert(
        self,
        name: str,
        condition: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> str:
        """创建告警规则。"""
        pass

    @abstractmethod
    async def delete_alert(self, alert_id: str) -> bool:
        """删除告警规则。"""
        pass

    @abstractmethod
    async def list_alerts(self) -> List[Dict[str, Any]]:
        """列出告警规则。"""
        pass

    @abstractmethod
    async def export_logs(
        self,
        query: LogQuery,
        format: str = "json",
        compression: Optional[str] = None
    ) -> bytes:
        """导出日志。"""
        pass

    @abstractmethod
    async def flush(self) -> None:
        """刷新日志缓冲区。"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭日志服务。"""
        pass


def create_log_record(
    level: LogLevel,
    message: str,
    logger_name: Optional[str] = None,
    exception: Optional[Exception] = None,
    **kwargs
) -> LogRecord:
    """创建日志记录。"""
    import inspect
    import threading

    # 获取调用栈信息
    frame = inspect.currentframe()
    if frame:
        frame = frame.f_back
        if frame:
            module = frame.f_globals.get("__name__")
            function = frame.f_code.co_name
            line_number = frame.f_lineno
        else:
            module = function = line_number = None
    else:
        module = function = line_number = None

    # 处理异常信息
    exception_info = None
    if exception:
        exception_info = {
            "type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exc()
        }

    return LogRecord(
        level=level,
        message=message,
        logger_name=logger_name,
        module=module,
        function=function,
        line_number=line_number,
        thread_id=threading.get_ident(),
        process_id=os.getpid(),
        exception=exception_info,
        **kwargs
    )


# 需要在文件顶部添加导入
import os