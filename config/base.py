"""
基础配置类。

定义所有环境共享的配置项和默认值。
"""

from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """数据库配置。"""

    model_config = SettingsConfigDict(env_prefix="DB_", case_sensitive=False)

    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    name: str = Field(default="edusched", description="数据库名称")
    user: str = Field(default="edusched", description="数据库用户名")
    password: str = Field(default="", description="数据库密码")
    pool_size: int = Field(default=20, description="连接池大小")
    max_overflow: int = Field(default=30, description="最大溢出连接数")
    echo: bool = Field(default=False, description="是否输出SQL语句")
    ssl_mode: Optional[str] = Field(default=None, description="SSL模式")
    pool_recycle: int = Field(default=3600, description="连接回收时间(秒)")

    @property
    def url(self) -> str:
        """构建数据库连接URL。"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseSettings):
    """Redis配置。"""

    model_config = SettingsConfigDict(env_prefix="REDIS_", case_sensitive=False)

    host: str = Field(default="localhost", description="Redis主机")
    port: int = Field(default=6379, description="Redis端口")
    password: Optional[str] = Field(default=None, description="Redis密码")
    db: int = Field(default=0, description="Redis数据库编号")
    pool_size: int = Field(default=10, description="连接池大小")
    timeout: int = Field(default=5, description="连接超时时间(秒)")
    retry_on_timeout: bool = Field(default=True, description="是否在超时时重试")

    @property
    def url(self) -> str:
        """构建Redis连接URL。"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class SecurityConfig(BaseSettings):
    """安全配置。"""

    model_config = SettingsConfigDict(env_prefix="SECURITY_", case_sensitive=False)

    secret_key: str = Field(description="JWT签名密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间(天)")
    password_min_length: int = Field(default=8, description="密码最小长度")
    password_max_length: int = Field(default=128, description="密码最大长度")
    bcrypt_rounds: int = Field(default=12, description="bcrypt加密轮数")
    allowed_origins: List[str] = Field(default=["http://localhost:3000"], description="允许的跨域来源")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """验证密钥长度。"""
        if len(v) < 32:
            raise ValueError("密钥长度必须至少32字符")
        return v


class OIDCConfig(BaseSettings):
    """OIDC配置。"""

    model_config = SettingsConfigDict(env_prefix="OIDC_", case_sensitive=False)

    issuer: str = Field(description="OIDC发行者URL")
    client_id: str = Field(description="客户端ID")
    client_secret: str = Field(description="客户端密钥")
    audience: Optional[str] = Field(default=None, description="受众")
    scopes: List[str] = Field(default=["openid", "profile", "email"], description="请求的作用域")
    token_endpoint: Optional[str] = Field(default=None, description="令牌端点")
    userinfo_endpoint: Optional[str] = Field(default=None, description="用户信息端点")


class SchedulingConfig(BaseSettings):
    """调度引擎配置。"""

    model_config = SettingsConfigDict(env_prefix="SCHEDULING_", case_sensitive=False)

    worker_count: int = Field(default=2, description="调度工作进程数")
    max_iterations: int = Field(default=1000, description="最大迭代次数")
    timeout_seconds: int = Field(default=300, description="调度超时时间(秒)")
    checkpoint_interval: int = Field(default=50, description="检查点间隔")
    solution_limit: int = Field(default=10, description="解的数量限制")
    time_limit_minutes: int = Field(default=30, description="时间限制(分钟)")
    parallel_threads: int = Field(default=4, description="并行线程数")


class ObservabilityConfig(BaseSettings):
    """可观测性配置。"""

    model_config = SettingsConfigDict(env_prefix="OBSERVABILITY_", case_sensitive=False)

    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    prometheus_enabled: bool = Field(default=True, description="是否启用Prometheus指标")
    prometheus_path: str = Field(default="/metrics", description="Prometheus指标路径")
    tracing_enabled: bool = Field(default=True, description="是否启用分布式追踪")
    otlp_endpoint: Optional[str] = Field(default=None, description="OTLP端点")
    service_name: str = Field(default="edusched-api", description="服务名称")


class MailConfig(BaseSettings):
    """邮件配置。"""

    model_config = SettingsConfigDict(env_prefix="MAIL_", case_sensitive=False)

    enabled: bool = Field(default=False, description="是否启用邮件功能")
    provider: str = Field(default="smtp", description="邮件提供商")
    host: str = Field(default="localhost", description="SMTP主机")
    port: int = Field(default=587, description="SMTP端口")
    username: Optional[str] = Field(default=None, description="SMTP用户名")
    password: Optional[str] = Field(default=None, description="SMTP密码")
    use_tls: bool = Field(default=True, description="是否使用TLS")
    from_email: str = Field(default="noreply@edusched.com", description="发件人邮箱")


class StorageConfig(BaseSettings):
    """存储配置。"""

    model_config = SettingsConfigDict(env_prefix="STORAGE_", case_sensitive=False)

    provider: str = Field(default="local", description="存储提供商")
    local_path: str = Field(default="./storage", description="本地存储路径")
    endpoint: Optional[str] = Field(default=None, description="对象存储端点")
    access_key: Optional[str] = Field(default=None, description="访问密钥")
    secret_key: Optional[str] = Field(default=None, description="密钥")
    bucket_name: Optional[str] = Field(default=None, description="存储桶名称")
    region: Optional[str] = Field(default=None, description="区域")


class BaseConfig(BaseSettings):
    """基础配置类。

    定义所有环境共享的配置项，作为其他环境配置的基类。
    """

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
    reload: bool = Field(default=False, description="是否自动重载")

    # 多租户配置
    multi_tenant: bool = Field(default=True, description="是否启用多租户")
    default_tenant: str = Field(default="default", description="默认租户")
    tenant_id_header: str = Field(default="X-Tenant-ID", description="租户ID请求头")

    # API配置
    api_prefix: str = Field(default="/api/v1", description="API前缀")
    docs_url: str = Field(default="/docs", description="API文档URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI URL")

    # 子配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    oidc: OIDCConfig = Field(default_factory=OIDCConfig)
    scheduling: SchedulingConfig = Field(default_factory=SchedulingConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    mail: MailConfig = Field(default_factory=MailConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)

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

    @property
    def is_testing(self) -> bool:
        """是否为测试环境。"""
        return self.environment == "testing"

    def get_database_url(self, tenant_id: Optional[str] = None) -> str:
        """获取指定租户的数据库URL。"""
        if tenant_id and self.multi_tenant:
            return self.database.url.replace("/edusched", f"/edusched_{tenant_id}")
        return self.database.url

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return self.model_dump()

    def filter_sensitive_data(self) -> Dict[str, Any]:
        """过滤敏感数据。"""
        config_dict = self.to_dict()
        sensitive_keys = {
            "password", "secret_key", "client_secret", "dsn",
            "access_key", "secret_key", "token"
        }

        def _filter_dict(data: Dict[str, Any]) -> Dict[str, Any]:
            filtered = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    filtered[key] = "***"
                elif isinstance(value, dict):
                    filtered[key] = _filter_dict(value)
                else:
                    filtered[key] = value
            return filtered

        return _filter_dict(config_dict)