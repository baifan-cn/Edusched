"""应用配置管理模块。

已迁移到新的配置管理系统，保留此文件用于向后兼容。
"""

import warnings
from typing import Optional

# 弃用警告
warnings.warn(
    "edusched.core.config 已弃用，请使用 config 模块",
    DeprecationWarning,
    stacklevel=2
)

# 从新的配置系统导入
try:
    from config import get_config

    # 获取配置实例
    _config = get_config()

    # 创建兼容的Settings类
    class Settings:
        """兼容旧的配置接口。"""

        def __init__(self):
            self.app_name = _config.app_name
            self.app_version = _config.app_version
            self.debug = _config.debug
            self.environment = _config.environment
            self.host = _config.host
            self.port = _config.port
            self.workers = _config.workers
            self.multi_tenant = _config.multi_tenant
            self.default_tenant = _config.default_tenant

            # 子配置
            self.database = _config.database
            self.redis = _config.redis
            self.security = _config.security
            self.oidc = _config.oidc
            self.scheduling = _config.scheduling
            self.observability = _config.observability

        @property
        def is_production(self) -> bool:
            """是否为生产环境。"""
            return _config.is_production

        @property
        def is_development(self) -> bool:
            """是否为开发环境。"""
            return _config.is_development

        def get_database_url(self, tenant_id: Optional[str] = None) -> str:
            """获取指定租户的数据库URL。"""
            return _config.get_database_url(tenant_id)

    # 全局配置实例
    settings = Settings()

    def get_settings() -> Settings:
        """获取配置实例。"""
        return settings

except ImportError:
    # 如果新配置系统未安装，使用旧的配置
    warnings.warn(
        "无法导入新的配置系统，使用旧配置",
        ImportWarning,
        stacklevel=2
    )

    from typing import Any, Dict, List
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class DatabaseSettings(BaseSettings):
        """数据库配置。"""

        model_config = SettingsConfigDict(env_prefix="DB_")

        host: str = Field(default="localhost", description="数据库主机")
        port: int = Field(default=5432, description="数据库端口")
        name: str = Field(default="edusched", description="数据库名称")
        user: str = Field(default="edusched", description="数据库用户名")
        password: str = Field(default="", description="数据库密码")
        pool_size: int = Field(default=20, description="连接池大小")
        max_overflow: int = Field(default=30, description="最大溢出连接数")
        echo: bool = Field(default=False, description="是否输出SQL语句")

        @property
        def url(self) -> str:
            """构建数据库连接URL。"""
            return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    class RedisSettings(BaseSettings):
        """Redis配置。"""

        model_config = SettingsConfigDict(env_prefix="REDIS_")

        host: str = Field(default="localhost", description="Redis主机")
        port: int = Field(default=6379, description="Redis端口")
        password: Optional[str] = Field(default=None, description="Redis密码")
        db: int = Field(default=0, description="Redis数据库编号")
        pool_size: int = Field(default=10, description="连接池大小")

        @property
        def url(self) -> str:
            """构建Redis连接URL。"""
            if self.password:
                return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
            return f"redis://{self.host}:{self.port}/{self.db}"

    class SecuritySettings(BaseSettings):
        """安全配置。"""

        model_config = SettingsConfigDict(env_prefix="SECURITY_")

        secret_key: str = Field(description="JWT签名密钥")
        algorithm: str = Field(default="HS256", description="JWT算法")
        access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
        refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间(天)")

        @field_validator("secret_key")
        @classmethod
        def validate_secret_key(cls, v: str) -> str:
            """验证密钥长度。"""
            if len(v) < 32:
                raise ValueError("密钥长度必须至少32字符")
            return v

    class OIDCSettings(BaseSettings):
        """OIDC配置。"""

        model_config = SettingsConfigDict(env_prefix="OIDC_")

        issuer: str = Field(description="OIDC发行者URL")
        client_id: str = Field(description="客户端ID")
        client_secret: str = Field(description="客户端密钥")
        audience: Optional[str] = Field(default=None, description="受众")
        scopes: List[str] = Field(default=["openid", "profile", "email"], description="请求的作用域")

    class SchedulingSettings(BaseSettings):
        """调度引擎配置。"""

        model_config = SettingsConfigDict(env_prefix="SCHEDULING_")

        worker_count: int = Field(default=2, description="调度工作进程数")
        max_iterations: int = Field(default=1000, description="最大迭代次数")
        timeout_seconds: int = Field(default=300, description="调度超时时间(秒)")
        checkpoint_interval: int = Field(default=50, description="检查点间隔")

    class ObservabilitySettings(BaseSettings):
        """可观测性配置。"""

        model_config = SettingsConfigDict(env_prefix="OBSERVABILITY_")

        log_level: str = Field(default="INFO", description="日志级别")
        sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
        prometheus_enabled: bool = Field(default=True, description="是否启用Prometheus指标")
        tracing_enabled: bool = Field(default=True, description="是否启用分布式追踪")
        otlp_endpoint: Optional[str] = Field(default=None, description="OTLP端点")

    class Settings(BaseSettings):
        """主配置类。"""

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )

        # 应用基础配置
        app_name: str = Field(default="Edusched", description="应用名称")
        app_version: str = Field(default="0.1.0", description="应用版本")
        debug: bool = Field(default=False, description="调试模式")
        environment: str = Field(default="development", description="运行环境")

        # 服务配置
        host: str = Field(default="0.0.0.0", description="服务监听地址")
        port: int = Field(default=8000, description="服务监听端口")
        workers: int = Field(default=1, description="工作进程数")

        # 多租户配置
        multi_tenant: bool = Field(default=True, description="是否启用多租户")
        default_tenant: str = Field(default="default", description="默认租户")

        # 子配置
        database: DatabaseSettings = Field(default_factory=DatabaseSettings)
        redis: RedisSettings = Field(default_factory=RedisSettings)
        security: SecuritySettings = Field(default_factory=SecuritySettings)
        oidc: OIDCSettings = Field(default_factory=OIDCSettings)
        scheduling: SchedulingSettings = Field(default_factory=SchedulingSettings)
        observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)

        @field_validator("environment")
        @classmethod
        def validate_environment(cls, v: str) -> str:
            """验证环境值。"""
            allowed = {"development", "staging", "production", "testing"}
            if v not in allowed:
                raise ValueError(f"环境必须是以下之一: {allowed}")
            return v

        @property
        def is_production(self) -> bool:
            """是否为生产环境。"""
            return self.environment == "production"

        @property
        def is_development(self) -> bool:
            """是否为开发环境。"""
            return self.environment == "development"

        def get_database_url(self, tenant_id: Optional[str] = None) -> str:
            """获取指定租户的数据库URL。"""
            if tenant_id and self.multi_tenant:
                return self.database.url.replace("/edusched", f"/edusched_{tenant_id}")
            return self.database.url

    # 全局配置实例
    settings = Settings()

    def get_settings() -> Settings:
        """获取配置实例。"""
        return settings