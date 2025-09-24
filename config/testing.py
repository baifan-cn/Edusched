"""
测试环境配置。

适用于自动化测试环境，使用独立的数据库和配置。
"""

from typing import List

from .base import BaseConfig


class TestingConfig(BaseConfig):
    """测试环境配置。"""

    # 应用配置
    debug: bool = True
    environment: str = "testing"
    reload: bool = False

    # 服务配置
    host: str = "127.0.0.1"
    port: int = 8001
    workers: int = 1

    # 数据库配置（使用测试数据库）
    database_name: str = "edusched_test"
    database_echo: bool = True
    database_pool_size: int = 1
    database_max_overflow: int = 5

    # Redis配置（使用测试数据库）
    redis_db: int = 1
    redis_pool_size: int = 1

    # 安全配置
    security_secret_key: str = "test-secret-key-for-testing-only"
    security_access_token_expire_minutes: int = 5
    security_refresh_token_expire_days: int = 1
    security_password_min_length: int = 1
    security_bcrypt_rounds: int = 4
    security_allowed_origins: List[str] = ["*"]

    # 调度引擎配置（快速测试）
    scheduling_worker_count: int = 1
    scheduling_timeout_seconds: int = 30
    scheduling_max_iterations: int = 100
    scheduling_solution_limit: int = 1

    # 可观测性配置
    observability_log_level: str = "DEBUG"
    observability_sentry_dsn: str = ""
    observability_tracing_enabled: bool = False
    observability_prometheus_enabled: bool = False

    # 邮件配置（使用测试邮件）
    mail_enabled: bool = False
    mail_provider: str = "console"

    # 存储配置（使用临时目录）
    storage_provider: str = "local"
    storage_local_path: str = "/tmp/edusched_test"

    # 测试特有配置
    test_mode: bool = True
    mock_external_services: bool = True
    enable_test_endpoints: bool = True
    clean_test_data: bool = True
    test_data_path: str = "./tests/fixtures"

    class Config:
        env_prefix = "TEST_"
        case_sensitive = False