"""外部服务配置管理。"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field, validator

from .base import ServiceConfig
from .email.interfaces import EmailConfig, EmailProvider
from .notification.interfaces import NotificationConfig, NotificationChannel
from .storage.interfaces import StorageConfig, StorageProvider
from .logging.interfaces import LogConfig, LogProvider
from .cache.interfaces import CacheConfig, CacheProvider


class ExternalServicesConfig(BaseSettings):
    """外部服务配置。"""

    # 邮件服务配置
    email_enabled: bool = Field(default=True, env="EMAIL_ENABLED")
    email_provider: str = Field(default="smtp", env="EMAIL_PROVIDER")
    email_api_key: Optional[str] = Field(default=None, env="EMAIL_API_KEY")
    email_smtp_host: Optional[str] = Field(default=None, env="EMAIL_SMTP_HOST")
    email_smtp_port: int = Field(default=587, env="EMAIL_SMTP_PORT")
    email_smtp_username: Optional[str] = Field(default=None, env="EMAIL_SMTP_USERNAME")
    email_smtp_password: Optional[str] = Field(default=None, env="EMAIL_SMTP_PASSWORD")
    email_default_from: Optional[str] = Field(default=None, env="EMAIL_DEFAULT_FROM")
    email_default_from_name: Optional[str] = Field(default=None, env="EMAIL_DEFAULT_FROM_NAME")

    # 通知服务配置
    notification_enabled: bool = Field(default=True, env="NOTIFICATION_ENABLED")
    notification_default_channel: str = Field(default="email", env="NOTIFICATION_DEFAULT_CHANNEL")
    notification_queue_enabled: bool = Field(default=True, env="NOTIFICATION_QUEUE_ENABLED")
    notification_queue_name: str = Field(default="notifications", env="NOTIFICATION_QUEUE_NAME")
    notification_retry_attempts: int = Field(default=3, env="NOTIFICATION_RETRY_ATTEMPTS")

    # 存储服务配置
    storage_enabled: bool = Field(default=True, env="STORAGE_ENABLED")
    storage_provider: str = Field(default="local", env="STORAGE_PROVIDER")
    storage_bucket_name: str = Field(default="edusched", env="STORAGE_BUCKET_NAME")
    storage_region: Optional[str] = Field(default=None, env="STORAGE_REGION")
    storage_access_key_id: Optional[str] = Field(default=None, env="STORAGE_ACCESS_KEY_ID")
    storage_access_key_secret: Optional[str] = Field(default=None, env="STORAGE_ACCESS_KEY_SECRET")
    storage_local_path: str = Field(default="/tmp/storage", env="STORAGE_LOCAL_PATH")
    storage_base_url: Optional[str] = Field(default=None, env="STORAGE_BASE_URL")

    # 日志服务配置
    logging_enabled: bool = Field(default=True, env="LOGGING_ENABLED")
    logging_provider: str = Field(default="console", env="LOGGING_PROVIDER")
    logging_level: str = Field(default="info", env="LOGGING_LEVEL")
    logging_format: str = Field(default="json", env="LOGGING_FORMAT")
    logging_file_path: Optional[str] = Field(default=None, env="LOGGING_FILE_PATH")
    logging_max_file_size: int = Field(default=10485760, env="LOGGING_MAX_FILE_SIZE")  # 10MB
    logging_backup_count: int = Field(default=5, env="LOGGING_BACKUP_COUNT")

    # 缓存服务配置
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_provider: str = Field(default="redis", env="CACHE_PROVIDER")
    cache_redis_url: str = Field(default="redis://localhost:6379", env="CACHE_REDIS_URL")
    cache_default_ttl: int = Field(default=3600, env="CACHE_DEFAULT_TTL")
    cache_local_max_size: int = Field(default=10000, env="CACHE_LOCAL_MAX_SIZE")

    # 通用服务配置
    service_timeout: int = Field(default=30, env="SERVICE_TIMEOUT")
    service_max_retries: int = Field(default=3, env="SERVICE_MAX_RETRIES")
    service_retry_delay: float = Field(default=1.0, env="SERVICE_RETRY_DELAY")

    class Config:
        env_prefix = "EDUSCHED_"
        env_file = ".env"
        case_sensitive = False

    @validator("email_provider")
    def validate_email_provider(cls, v):
        """验证邮件服务提供商。"""
        providers = [p.value for p in EmailProvider]
        if v not in providers:
            raise ValueError(f"不支持的邮件服务提供商: {v}. 支持的提供商: {providers}")
        return v

    @validator("notification_default_channel")
    def validate_notification_channel(cls, v):
        """验证通知渠道。"""
        channels = [c.value for c in NotificationChannel]
        if v not in channels:
            raise ValueError(f"不支持的通知渠道: {v}. 支持的渠道: {channels}")
        return v

    @validator("storage_provider")
    def validate_storage_provider(cls, v):
        """验证存储服务提供商。"""
        providers = [p.value for p in StorageProvider]
        if v not in providers:
            raise ValueError(f"不支持的存储服务提供商: {v}. 支持的提供商: {providers}")
        return v

    @validator("logging_provider")
    def validate_logging_provider(cls, v):
        """验证日志服务提供商。"""
        providers = [p.value for p in LogProvider]
        if v not in providers:
            raise ValueError(f"不支持的日志服务提供商: {v}. 支持的提供商: {providers}")
        return v

    @validator("cache_provider")
    def validate_cache_provider(cls, v):
        """验证缓存服务提供商。"""
        providers = [p.value for p in CacheProvider]
        if v not in providers:
            raise ValueError(f"不支持的缓存服务提供商: {v}. 支持的提供商: {providers}")
        return v

    def get_email_config(self) -> EmailConfig:
        """获取邮件服务配置。"""
        return EmailConfig(
            provider=EmailProvider(self.email_provider),
            api_key=self.email_api_key,
            smtp_host=self.email_smtp_host,
            smtp_port=self.email_smtp_port,
            smtp_username=self.email_smtp_username,
            smtp_password=self.email_smtp_password,
            default_from_email=self.email_default_from,
            default_from_name=self.email_default_from_name
        )

    def get_notification_config(self) -> NotificationConfig:
        """获取通知服务配置。"""
        return NotificationConfig(
            default_channel=NotificationChannel(self.notification_default_channel),
            queue_enabled=self.notification_queue_enabled,
            queue_name=self.notification_queue_name,
            retry_attempts=self.notification_retry_attempts,
            email_config={
                "provider": self.email_provider,
                "api_key": self.email_api_key,
                "smtp_host": self.email_smtp_host,
                "smtp_port": self.email_smtp_port,
                "smtp_username": self.email_smtp_username,
                "smtp_password": self.email_smtp_password,
                "default_from_email": self.email_default_from,
                "default_from_name": self.email_default_from_name
            } if self.email_enabled else None
        )

    def get_storage_config(self) -> StorageConfig:
        """获取存储服务配置。"""
        return StorageConfig(
            provider=StorageProvider(self.storage_provider),
            bucket_name=self.storage_bucket_name,
            region=self.storage_region,
            access_key_id=self.storage_access_key_id,
            access_key_secret=self.storage_access_key_secret,
            local_path=self.storage_local_path,
            base_url=self.storage_base_url
        )

    def get_logging_config(self) -> LogConfig:
        """获取日志服务配置。"""
        from .logging.interfaces import LogLevel, LogFormat
        return LogConfig(
            provider=LogProvider(self.logging_provider),
            level=LogLevel(self.logging_level.lower()),
            format=LogFormat(self.logging_format.lower()),
            file_path=self.logging_file_path,
            max_file_size=self.logging_max_file_size,
            backup_count=self.logging_backup_count
        )

    def get_cache_config(self) -> CacheConfig:
        """获取缓存服务配置。"""
        return CacheConfig(
            provider=CacheProvider(self.cache_provider),
            default_ttl=self.cache_default_ttl,
            redis_url=self.cache_redis_url,
            local_max_size=self.cache_local_max_size
        )

    def get_service_config(self) -> ServiceConfig:
        """获取通用服务配置。"""
        return ServiceConfig(
            enabled=True,
            timeout=self.service_timeout,
            max_retries=self.service_max_retries,
            retry_delay=self.service_retry_delay
        )


class ExternalServicesManager:
    """外部服务管理器。"""

    def __init__(self, config: ExternalServicesConfig):
        self.config = config
        self._services = {}

    async def initialize_services(self) -> None:
        """初始化所有启用的服务。"""
        from .factory import ServiceFactory, ServiceType

        # 初始化邮件服务
        if self.config.email_enabled:
            email_service = await ServiceFactory.create_service(
                ServiceType.EMAIL,
                self.config.get_service_config(),
                "default",
                email_config=self.config.get_email_config()
            )
            await email_service.initialize()

        # 初始化通知服务
        if self.config.notification_enabled:
            notification_service = await ServiceFactory.create_service(
                ServiceType.NOTIFICATION,
                self.config.get_service_config(),
                "default",
                notification_config=self.config.get_notification_config()
            )
            await notification_service.initialize()

        # 初始化存储服务
        if self.config.storage_enabled:
            storage_service = await ServiceFactory.create_service(
                ServiceType.STORAGE,
                self.config.get_service_config(),
                "default",
                storage_config=self.config.get_storage_config()
            )
            await storage_service.initialize()

        # 初始化日志服务
        if self.config.logging_enabled:
            logging_service = await ServiceFactory.create_service(
                ServiceType.LOGGING,
                self.config.get_service_config(),
                "default",
                log_config=self.config.get_logging_config()
            )
            await logging_service.initialize()

        # 初始化缓存服务
        if self.config.cache_enabled:
            cache_service = await ServiceFactory.create_service(
                ServiceType.CACHE,
                self.config.get_service_config(),
                "default",
                cache_config=self.config.get_cache_config()
            )
            await cache_service.initialize()

    async def close_services(self) -> None:
        """关闭所有服务。"""
        from .factory import ServiceFactory
        await ServiceFactory.close_all()

    def get_email_service(self):
        """获取邮件服务。"""
        from .factory import ServiceFactory, ServiceType
        return ServiceFactory.get_service(ServiceType.EMAIL, "default")

    def get_notification_service(self):
        """获取通知服务。"""
        from .factory import ServiceFactory, ServiceType
        return ServiceFactory.get_service(ServiceType.NOTIFICATION, "default")

    def get_storage_service(self):
        """获取存储服务。"""
        from .factory import ServiceFactory, ServiceType
        return ServiceFactory.get_service(ServiceType.STORAGE, "default")

    def get_logging_service(self):
        """获取日志服务。"""
        from .factory import ServiceFactory, ServiceType
        return ServiceFactory.get_service(ServiceType.LOGGING, "default")

    def get_cache_service(self):
        """获取缓存服务。"""
        from .factory import ServiceFactory, ServiceType
        return ServiceFactory.get_service(ServiceType.CACHE, "default")


# 全局配置实例
external_services_config = ExternalServicesConfig()

# 全局服务管理器实例
external_services_manager = ExternalServicesManager(external_services_config)