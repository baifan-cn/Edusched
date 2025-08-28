"""应用配置管理模块。

使用Pydantic Settings管理环境变量和配置，支持多环境配置。
"""

from typing import Any, Dict, List, Optional

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
            # 多租户模式下，可以为不同租户使用不同的数据库
            return self.database.url.replace("/edusched", f"/edusched_{tenant_id}")
        return self.database.url


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例。"""
    return settings