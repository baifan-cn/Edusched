"""
配置验证器。

负责验证配置的有效性和完整性。
"""

import ipaddress
import re
from typing import Dict, Any, List, Optional, Callable
from urllib.parse import urlparse
from pydantic import ValidationError, validator

from .base import BaseConfig


class ConfigValidator:
    """配置验证器。"""

    def __init__(self):
        """初始化配置验证器。"""
        self._validators: Dict[str, List[Callable]] = {}
        self._register_validators()

    def _register_validators(self) -> None:
        """注册内置验证器。"""
        self._validators = {
            "database": [
                self._validate_database_connection,
                self._validate_database_pool,
            ],
            "redis": [
                self._validate_redis_connection,
            ],
            "security": [
                self._validate_security_settings,
            ],
            "mail": [
                self._validate_mail_settings,
            ],
            "storage": [
                self._validate_storage_settings,
            ],
            "scheduling": [
                self._validate_scheduling_settings,
            ],
        }

    def validate(self, config: BaseConfig) -> List[str]:
        """验证配置。

        Args:
            config: 配置实例

        Returns:
            验证错误列表，如果为空则验证通过
        """
        errors: List[str] = []

        # 执行Pydantic内置验证
        try:
            config.model_validate(config.model_dump())
        except ValidationError as e:
            for error in e.errors():
                errors.append(f"{'.'.join(map(str, error['loc']))}: {error['msg']}")

        # 执行自定义验证
        for section, validators in self._validators.items():
            if hasattr(config, section):
                section_config = getattr(config, section)
                for validator_func in validators:
                    try:
                        validator_func(section_config)
                    except ValueError as e:
                        errors.append(f"{section}.{e}")

        return errors

    def validate_database_connection(self, db_config: Any) -> None:
        """验证数据库连接配置。"""
        # 验证主机地址
        try:
            ipaddress.ip_address(db_config.host)
        except ValueError:
            # 如果不是IP地址，应该是域名
            if not re.match(r"^[a-zA-Z0-9.-]+$", db_config.host):
                raise ValueError(f"无效的数据库主机: {db_config.host}")

        # 验证端口
        if not (1 <= db_config.port <= 65535):
            raise ValueError(f"无效的数据库端口: {db_config.port}")

        # 验证密码长度
        if len(db_config.password) < 8:
            raise ValueError("数据库密码长度至少8个字符")

    def validate_database_pool(self, db_config: Any) -> None:
        """验证数据库连接池配置。"""
        if db_config.pool_size < 1:
            raise ValueError("连接池大小必须大于0")

        if db_config.max_overflow < 0:
            raise ValueError("最大溢出连接数不能为负数")

        if db_config.pool_recycle < 60:
            raise ValueError("连接回收时间至少60秒")

    def validate_redis_connection(self, redis_config: Any) -> None:
        """验证Redis连接配置。"""
        # 验证主机地址
        try:
            ipaddress.ip_address(redis_config.host)
        except ValueError:
            if not re.match(r"^[a-zA-Z0-9.-]+$", redis_config.host):
                raise ValueError(f"无效的Redis主机: {redis_config.host}")

        # 验证端口
        if not (1 <= redis_config.port <= 65535):
            raise ValueError(f"无效的Redis端口: {redis_config.port}")

        # 验证数据库编号
        if not (0 <= redis_config.db <= 15):
            raise ValueError(f"无效的Redis数据库编号: {redis_config.db}")

    def validate_security_settings(self, security_config: Any) -> None:
        """验证安全配置。"""
        # 验证密钥长度
        if len(security_config.secret_key) < 32:
            raise ValueError("密钥长度必须至少32个字符")

        # 验证算法
        allowed_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if security_config.algorithm not in allowed_algorithms:
            raise ValueError(f"不支持的JWT算法: {security_config.algorithm}")

        # 验证令牌过期时间
        if security_config.access_token_expire_minutes < 1:
            raise ValueError("访问令牌过期时间至少1分钟")

        if security_config.refresh_token_expire_days < 1:
            raise ValueError("刷新令牌过期时间至少1天")

        # 验证密码长度
        if security_config.password_min_length < 8:
            raise ValueError("密码最小长度至少8个字符")

        # 验证允许的来源
        for origin in security_config.allowed_origins:
            if origin != "*" and not self._is_valid_url(origin):
                raise ValueError(f"无效的跨域来源: {origin}")

    def validate_mail_settings(self, mail_config: Any) -> None:
        """验证邮件配置。"""
        if mail_config.enabled:
            if not mail_config.host:
                raise ValueError("启用邮件时必须配置主机地址")

            if not mail_config.from_email or "@" not in mail_config.from_email:
                raise ValueError("无效的发件人邮箱")

            if mail_config.username and not mail_config.password:
                raise ValueError("配置用户名时必须配置密码")

    def validate_storage_settings(self, storage_config: Any) -> None:
        """验证存储配置。"""
        if storage_config.provider == "s3":
            if not all([
                storage_config.endpoint,
                storage_config.access_key,
                storage_config.secret_key,
                storage_config.bucket_name
            ]):
                raise ValueError("S3存储必须配置endpoint、access_key、secret_key和bucket_name")

        elif storage_config.provider == "local":
            if not storage_config.local_path:
                raise ValueError("本地存储必须配置路径")

    def validate_scheduling_settings(self, scheduling_config: Any) -> None:
        """验证调度引擎配置。"""
        if scheduling_config.worker_count < 1:
            raise ValueError("工作进程数必须大于0")

        if scheduling_config.max_iterations < 100:
            raise ValueError("最大迭代次数至少100")

        if scheduling_config.timeout_seconds < 10:
            raise ValueError("超时时间至少10秒")

        if scheduling_config.parallel_threads < 1:
            raise ValueError("并行线程数必须大于0")

    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式。"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def validate_config_dict(self, config_dict: Dict[str, Any]) -> List[str]:
        """验证配置字典。

        Args:
            config_dict: 配置字典

        Returns:
            验证错误列表
        """
        try:
            # 获取环境类型
            environment = config_dict.get("environment", "development")

            # 创建配置实例
            from .factory import ConfigFactory
            config = ConfigFactory.create_config(environment)

            # 更新配置
            for key, value in config_dict.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            # 验证配置
            return self.validate(config)
        except Exception as e:
            return [str(e)]

    def validate_environment(self, environment: str) -> bool:
        """验证环境名称。"""
        from .factory import ConfigFactory
        return environment in ConfigFactory.get_available_environments()


# 全局验证器实例
config_validator = ConfigValidator()