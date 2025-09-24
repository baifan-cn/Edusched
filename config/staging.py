"""
预发布环境配置。

介于开发和生产之间，用于最终测试。
"""

from typing import List

from .base import BaseConfig


class StagingConfig(BaseConfig):
    """预发布环境配置。"""

    # 应用配置
    debug: bool = False
    environment: str = "staging"
    reload: bool = False

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2

    # 数据库配置（接近生产）
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_recycle: int = 1800
    database_ssl_mode: str = "require"

    # Redis配置
    redis_db: int = 1
    redis_pool_size: int = 15
    redis_timeout: int = 3

    # 安全配置
    security_access_token_expire_minutes: int = 30
    security_refresh_token_expire_days: int = 7
    security_password_min_length: int = 8
    security_bcrypt_rounds: int = 10
    security_allowed_origins: List[str] = ["*"]  # 预发布可以宽松一些

    # 调度引擎配置
    scheduling_worker_count: int = 2
    scheduling_timeout_seconds: int = 300
    scheduling_max_iterations: int = 1000
    scheduling_parallel_threads: int = 4

    # 可观测性配置
    observability_log_level: str = "INFO"
    observability_log_format: str = "json"
    observability_sentry_dsn: str = ""
    observability_tracing_enabled: bool = True
    observability_otlp_endpoint: str = ""

    # 邮件配置
    mail_enabled: bool = True
    mail_use_tls: bool = True
    mail_host: str = ""
    mail_port: int = 587
    mail_username: str = ""
    mail_password: str = ""

    # 存储配置
    storage_provider: str = "s3"
    storage_endpoint: str = ""
    storage_access_key: str = ""
    storage_secret_key: str = ""
    storage_bucket_name: str = ""
    storage_region: str = ""

    # 预发布特有配置
    enable_cors: bool = True
    enable_docs: bool = True  # 预发布可以保留文档
    rate_limiting: bool = True
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    graceful_timeout: int = 30
    max_request_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_prefix = "STAGING_"
        case_sensitive = False