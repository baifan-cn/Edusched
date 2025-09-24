"""日志服务提供商实现。"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiofiles
from logging.handlers import RotatingFileHandler
import aiohttp

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .interfaces import (
    LoggingServiceInterface,
    LogConfig,
    LogRecord,
    LogQuery,
    LogStats,
    LogLevel,
    LogFormat,
    LogProvider,
    create_log_record
)

logger = logging.getLogger(__name__)


class ConsoleLoggingService(BaseService, LoggingServiceInterface):
    """控制台日志服务。"""

    def __init__(self, config: ServiceConfig, log_config: LogConfig):
        super().__init__("console_logging", config)
        self.log_config = log_config
        self._buffer: List[LogRecord] = []
        self._flush_task: Optional[asyncio.Task] = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.LOGGING

    async def initialize(self) -> None:
        """初始化控制台日志服务。"""
        try:
            # 配置标准日志记录器
            handler = logging.StreamHandler(sys.stdout)
            formatter = self._get_formatter()
            handler.setFormatter(formatter)

            self._logger = logging.getLogger("edusched")
            self._logger.addHandler(handler)
            self._logger.setLevel(self._get_python_level(self.log_config.level))

            # 启动刷新任务
            self._flush_task = asyncio.create_task(self._flush_loop())

            self.logger.info("控制台日志服务初始化成功")

        except Exception as e:
            raise ExternalServiceError(
                f"控制台日志服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    def _get_formatter(self):
        """获取日志格式化器。"""
        if self.log_config.format == LogFormat.JSON:
            return logging.Formatter(
                '%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

    def _get_python_level(self, level: LogLevel):
        """转换日志级别。"""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        return level_map.get(level, logging.INFO)

    async def health_check(self):
        """健康检查。"""
        try:
            start_time = datetime.now()

            # 测试日志记录
            self._logger.debug("健康检查测试日志")

            response_time = (datetime.now() - start_time).total_seconds()

            self._health.status = ServiceStatus.HEALTHY
            self._health.message = "控制台日志服务正常"
            self._health.response_time = response_time
            self._health.last_check = datetime.now()

            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"控制台日志服务异常: {str(e)}"
            self._health.last_check = datetime.now()

            return self._health

    async def log(self, record: LogRecord) -> None:
        """记录日志。"""
        if not self.log_config.enabled:
            return

        # 采样
        if random.random() > self.log_config.sample_rate:
            return

        # 检查忽略模式
        if self._should_ignore(record.message):
            return

        # 添加到缓冲区
        self._buffer.append(record)

        # 如果缓冲区满了，立即刷新
        if len(self._buffer) >= self.log_config.max_batch_size:
            await self.flush()

    def _should_ignore(self, message: str) -> bool:
        """检查是否应该忽略该日志。"""
        if not self.log_config.ignore_patterns:
            return False

        for pattern in self.log_config.ignore_patterns:
            if pattern in message:
                return True
        return False

    async def _flush_loop(self) -> None:
        """刷新循环。"""
        while True:
            try:
                await asyncio.sleep(self.log_config.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"刷新日志缓冲区时出错: {e}")

    async def flush(self) -> None:
        """刷新日志缓冲区。"""
        if not self._buffer:
            return

        records = self._buffer.copy()
        self._buffer.clear()

        for record in records:
            try:
                if self.log_config.format == LogFormat.JSON:
                    message = json.dumps(record.to_dict(), ensure_ascii=False)
                else:
                    message = f"{record.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {record.level.value.upper()} - {record.message}"

                level = self._get_python_level(record.level)
                self._logger.log(level, message)

            except Exception as e:
                self.logger.error(f"写入日志失败: {e}")

    async def debug(self, message: str, **kwargs) -> None:
        """记录 DEBUG 级别日志。"""
        record = create_log_record(LogLevel.DEBUG, message, **kwargs)
        await self.log(record)

    async def info(self, message: str, **kwargs) -> None:
        """记录 INFO 级别日志。"""
        record = create_log_record(LogLevel.INFO, message, **kwargs)
        await self.log(record)

    async def warning(self, message: str, **kwargs) -> None:
        """记录 WARNING 级别日志。"""
        record = create_log_record(LogLevel.WARNING, message, **kwargs)
        await self.log(record)

    async def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 ERROR 级别日志。"""
        record = create_log_record(LogLevel.ERROR, message, exception=exception, **kwargs)
        await self.log(record)

    async def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 CRITICAL 级别日志。"""
        record = create_log_record(LogLevel.CRITICAL, message, exception=exception, **kwargs)
        await self.log(record)

    async def query_logs(self, query: LogQuery) -> List[LogRecord]:
        """查询日志（控制台不支持）。"""
        raise ExternalServiceError("控制台日志服务不支持查询功能", self.service_name)

    async def get_log_stats(self, start_time: datetime, end_time: datetime) -> LogStats:
        """获取日志统计信息（控制台不支持）。"""
        raise ExternalServiceError("控制台日志服务不支持统计功能", self.service_name)

    async def create_alert(
        self,
        name: str,
        condition: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> str:
        """创建告警规则（控制台不支持）。"""
        raise ExternalServiceError("控制台日志服务不支持告警功能", self.service_name)

    async def delete_alert(self, alert_id: str) -> bool:
        """删除告警规则（控制台不支持）。"""
        raise ExternalServiceError("控制台日志服务不支持告警功能", self.service_name)

    async def list_alerts(self) -> List[Dict[str, Any]]:
        """列出告警规则（控制台不支持）。"""
        raise ExternalServiceError("控制台日志服务不支持告警功能", self.service_name)

    async def export_logs(
        self,
        query: LogQuery,
        format: str = "json",
        compression: Optional[str] = None
    ) -> bytes:
        """导出日志（控制台不支持）。"""
        raise ExternalServiceError("控制台日志服务不支持导出功能", self.service_name)

    async def close(self) -> None:
        """关闭日志服务。"""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        await self.flush()

        if hasattr(self, '_logger'):
            for handler in self._logger.handlers[:]:
                handler.close()
                self._logger.removeHandler(handler)


class FileLoggingService(BaseService, LoggingServiceInterface):
    """文件日志服务。"""

    def __init__(self, config: ServiceConfig, log_config: LogConfig):
        super().__init__("file_logging", config)
        self.log_config = log_config
        self._buffer: List[LogRecord] = []
        self._flush_task: Optional[asyncio.Task] = None
        self._file_handler: Optional[RotatingFileHandler] = None
        self._logger: Optional[logging.Logger] = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.LOGGING

    async def initialize(self) -> None:
        """初始化文件日志服务。"""
        try:
            if not self.log_config.file_path:
                raise ExternalServiceError("日志文件路径未配置", self.service_name)

            # 创建日志目录
            log_file = Path(self.log_config.file_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # 配置文件处理器
            self._file_handler = RotatingFileHandler(
                self.log_config.file_path,
                maxBytes=self.log_config.max_file_size,
                backupCount=self.log_config.backup_count,
                encoding=self.log_config.encoding
            )
            formatter = self._get_formatter()
            self._file_handler.setFormatter(formatter)

            # 配置日志记录器
            self._logger = logging.getLogger(f"edusched.file.{id(self)}")
            self._logger.addHandler(self._file_handler)
            self._logger.setLevel(self._get_python_level(self.log_config.level))

            # 启动刷新任务
            self._flush_task = asyncio.create_task(self._flush_loop())

            self.logger.info(f"文件日志服务初始化成功，日志文件: {self.log_config.file_path}")

        except Exception as e:
            raise ExternalServiceError(
                f"文件日志服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    def _get_formatter(self):
        """获取日志格式化器。"""
        if self.log_config.format == LogFormat.JSON:
            return logging.Formatter('%(message)s')
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

    def _get_python_level(self, level: LogLevel):
        """转换日志级别。"""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        return level_map.get(level, logging.INFO)

    async def health_check(self):
        """健康检查。"""
        try:
            start_time = datetime.now()

            # 测试日志写入
            if self._file_handler:
                self._file_handler.stream.write("健康检查测试日志\n")
                self._file_handler.stream.flush()

            response_time = (datetime.now() - start_time).total_seconds()

            self._health.status = ServiceStatus.HEALTHY
            self._health.message = "文件日志服务正常"
            self._health.response_time = response_time
            self._health.last_check = datetime.now()

            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"文件日志服务异常: {str(e)}"
            self._health.last_check = datetime.now()

            return self._health

    async def log(self, record: LogRecord) -> None:
        """记录日志。"""
        if not self.log_config.enabled:
            return

        # 采样
        if random.random() > self.log_config.sample_rate:
            return

        # 检查忽略模式
        if self._should_ignore(record.message):
            return

        # 添加到缓冲区
        self._buffer.append(record)

        # 如果缓冲区满了，立即刷新
        if len(self._buffer) >= self.log_config.max_batch_size:
            await self.flush()

    def _should_ignore(self, message: str) -> bool:
        """检查是否应该忽略该日志。"""
        if not self.log_config.ignore_patterns:
            return False

        for pattern in self.log_config.ignore_patterns:
            if pattern in message:
                return True
        return False

    async def _flush_loop(self) -> None:
        """刷新循环。"""
        while True:
            try:
                await asyncio.sleep(self.log_config.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"刷新日志缓冲区时出错: {e}")

    async def flush(self) -> None:
        """刷新日志缓冲区。"""
        if not self._buffer or not self._logger:
            return

        records = self._buffer.copy()
        self._buffer.clear()

        for record in records:
            try:
                if self.log_config.format == LogFormat.JSON:
                    message = json.dumps(record.to_dict(), ensure_ascii=False)
                else:
                    message = f"{record.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {record.level.value.upper()} - {record.message}"

                level = self._get_python_level(record.level)
                self._logger.log(level, message)

            except Exception as e:
                self.logger.error(f"写入日志失败: {e}")

    async def debug(self, message: str, **kwargs) -> None:
        """记录 DEBUG 级别日志。"""
        record = create_log_record(LogLevel.DEBUG, message, **kwargs)
        await self.log(record)

    async def info(self, message: str, **kwargs) -> None:
        """记录 INFO 级别日志。"""
        record = create_log_record(LogLevel.INFO, message, **kwargs)
        await self.log(record)

    async def warning(self, message: str, **kwargs) -> None:
        """记录 WARNING 级别日志。"""
        record = create_log_record(LogLevel.WARNING, message, **kwargs)
        await self.log(record)

    async def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 ERROR 级别日志。"""
        record = create_log_record(LogLevel.ERROR, message, exception=exception, **kwargs)
        await self.log(record)

    async def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """记录 CRITICAL 级别日志。"""
        record = create_log_record(LogLevel.CRITICAL, message, exception=exception, **kwargs)
        await self.log(record)

    async def query_logs(self, query: LogQuery) -> List[LogRecord]:
        """查询日志。"""
        if not self.log_config.file_path:
            return []

        records = []
        log_file = Path(self.log_config.file_path)

        # 检查主日志文件
        if log_file.exists():
            records.extend(await self._parse_log_file(log_file, query))

        # 检查轮转的日志文件
        for i in range(1, self.log_config.backup_count + 1):
            backup_file = Path(f"{self.log_config.file_path}.{i}")
            if backup_file.exists():
                records.extend(await self._parse_log_file(backup_file, query))

        # 排序和分页
        records.sort(key=lambda r: r.timestamp, reverse=True)
        if query.offset:
            records = records[query.offset:]
        if query.limit:
            records = records[:query.limit]

        return records

    async def _parse_log_file(self, file_path: Path, query: LogQuery) -> List[LogRecord]:
        """解析日志文件。"""
        records = []

        try:
            async with aiofiles.open(file_path, "r", encoding=self.log_config.encoding) as f:
                async for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        if self.log_config.format == LogFormat.JSON:
                            data = json.loads(line)
                            record = LogRecord(
                                level=LogLevel(data.get("level", "info")),
                                message=data.get("message", ""),
                                timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
                                logger_name=data.get("logger_name"),
                                module=data.get("module"),
                                function=data.get("function"),
                                line_number=data.get("line_number"),
                                user_id=data.get("user_id"),
                                tenant_id=data.get("tenant_id"),
                                request_id=data.get("request_id"),
                                tags=data.get("tags", [])
                            )
                        else:
                            # 解析文本格式
                            parts = line.split(" - ", 3)
                            if len(parts) >= 4:
                                record = LogRecord(
                                    level=LogLevel(parts[2].lower()),
                                    message=parts[3],
                                    timestamp=datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"),
                                    logger_name=parts[1]
                                )
                            else:
                                continue

                        # 应用查询条件
                        if self._match_query(record, query):
                            records.append(record)

                    except Exception as e:
                        self.logger.error(f"解析日志行失败: {e}")
                        continue

        except Exception as e:
            self.logger.error(f"读取日志文件失败 {file_path}: {e}")

        return records

    def _match_query(self, record: LogRecord, query: LogQuery) -> bool:
        """检查记录是否匹配查询条件。"""
        if query.level and record.level != query.level:
            return False

        if query.logger_name and query.logger_name not in (record.logger_name or ""):
            return False

        if query.start_time and record.timestamp < query.start_time:
            return False

        if query.end_time and record.timestamp > query.end_time:
            return False

        if query.message_pattern and query.message_pattern not in record.message:
            return False

        if query.trace_id and record.trace_id != query.trace_id:
            return False

        if query.user_id and record.user_id != query.user_id:
            return False

        if query.tenant_id and record.tenant_id != query.tenant_id:
            return False

        if query.request_id and record.request_id != query.request_id:
            return False

        if query.tags and not all(tag in (record.tags or []) for tag in query.tags):
            return False

        return True

    async def get_log_stats(self, start_time: datetime, end_time: datetime) -> LogStats:
        """获取日志统计信息。"""
        query = LogQuery(
            start_time=start_time,
            end_time=end_time,
            limit=10000  # 限制数量以提高性能
        )

        records = await self.query_logs(query)

        # 统计各级别数量
        level_counts = {}
        for level in LogLevel:
            level_counts[level] = 0

        for record in records:
            level_counts[record.level] += 1

        # 统计最活跃的日志记录器
        logger_counts = {}
        for record in records:
            logger_name = record.logger_name or "unknown"
            logger_counts[logger_name] = logger_counts.get(logger_name, 0) + 1

        top_loggers = [
            {"name": name, "count": count}
            for name, count in sorted(logger_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        # 统计最常见的错误
        error_counts = {}
        for record in records:
            if record.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                error_counts[record.message] = error_counts.get(record.message, 0) + 1

        top_errors = [
            {"message": msg, "count": count}
            for msg, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        return LogStats(
            total_count=len(records),
            level_counts=level_counts,
            time_range={"start": start_time, "end": end_time},
            top_loggers=top_loggers,
            top_errors=top_errors
        )

    async def create_alert(
        self,
        name: str,
        condition: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> str:
        """创建告警规则（文件日志不支持）。"""
        raise ExternalServiceError("文件日志服务不支持告警功能", self.service_name)

    async def delete_alert(self, alert_id: str) -> bool:
        """删除告警规则（文件日志不支持）。"""
        raise ExternalServiceError("文件日志服务不支持告警功能", self.service_name)

    async def list_alerts(self) -> List[Dict[str, Any]]:
        """列出告警规则（文件日志不支持）。"""
        raise ExternalServiceError("文件日志服务不支持告警功能", self.service_name)

    async def export_logs(
        self,
        query: LogQuery,
        format: str = "json",
        compression: Optional[str] = None
    ) -> bytes:
        """导出日志。"""
        records = await self.query_logs(query)

        if format == "json":
            data = [record.to_dict() for record in records]
            output = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "timestamp", "level", "message", "logger_name", "module",
                "function", "line_number", "user_id", "tenant_id", "request_id"
            ])
            writer.writeheader()
            for record in records:
                writer.writerow({
                    "timestamp": record.timestamp.isoformat(),
                    "level": record.level.value,
                    "message": record.message,
                    "logger_name": record.logger_name,
                    "module": record.module,
                    "function": record.function,
                    "line_number": record.line_number,
                    "user_id": record.user_id,
                    "tenant_id": record.tenant_id,
                    "request_id": record.request_id
                })
            output = output.getvalue().encode("utf-8")
        else:
            raise ExternalServiceError(f"不支持的导出格式: {format}", self.service_name)

        if compression == "gzip":
            import gzip
            output = gzip.compress(output)

        return output

    async def close(self) -> None:
        """关闭日志服务。"""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        await self.flush()

        if self._file_handler:
            self._file_handler.close()
            if self._logger:
                self._logger.removeHandler(self._file_handler)


# 需要在文件顶部添加导入
import random
from ..base import ServiceStatus