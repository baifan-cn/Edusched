"""
配置工具函数。

提供配置相关的实用工具。
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import lru_cache

from .factory import get_config


def get_env_variable(key: str, default: Any = None, required: bool = False) -> Any:
    """获取环境变量。

    Args:
        key: 环境变量名
        default: 默认值
        required: 是否必需

    Returns:
        环境变量值

    Raises:
        ValueError: 当必需的环境变量不存在时
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"必需的环境变量 {key} 未设置")
    return value


def get_bool_env(key: str, default: bool = False) -> bool:
    """获取布尔类型环境变量。

    Args:
        key: 环境变量名
        default: 默认值

    Returns:
        布尔值
    """
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def get_int_env(key: str, default: int = 0) -> int:
    """获取整数类型环境变量。

    Args:
        key: 环境变量名
        default: 默认值

    Returns:
        整数值
    """
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_list_env(key: str, delimiter: str = ",", default: Optional[list] = None) -> list:
    """获取列表类型环境变量。

    Args:
        key: 环境变量名
        delimiter: 分隔符
        default: 默认值

    Returns:
        列表值
    """
    if default is None:
        default = []
    value = os.getenv(key)
    if value is None:
        return default
    return [item.strip() for item in value.split(delimiter) if item.strip()]


def get_path_env(key: str, default: Optional[Union[str, Path]] = None) -> Path:
    """获取路径类型环境变量。

    Args:
        key: 环境变量名
        default: 默认值

    Returns:
        路径对象
    """
    value = os.getenv(key, str(default) if default else None)
    if value is None:
        raise ValueError(f"路径环境变量 {key} 未设置")
    return Path(value).expanduser().absolute()


@lru_cache(maxsize=128)
def get_cached_config() -> Dict[str, Any]:
    """获取缓存的配置字典。

    Returns:
        配置字典
    """
    config = get_config()
    return config.to_dict()


def get_database_url(tenant_id: Optional[str] = None) -> str:
    """获取数据库URL。

    Args:
        tenant_id: 租户ID

    Returns:
        数据库URL
    """
    config = get_config()
    return config.get_database_url(tenant_id)


def get_redis_url() -> str:
    """获取Redis URL。

    Returns:
        Redis URL
    """
    config = get_config()
    return config.redis.url


def is_development() -> bool:
    """是否为开发环境。"""
    return get_config().is_development


def is_production() -> bool:
    """是否为生产环境。"""
    return get_config().is_production


def is_testing() -> bool:
    """是否为测试环境。"""
    return get_config().is_testing


def get_log_level() -> str:
    """获取日志级别。"""
    config = get_config()
    return config.observability.log_level


def get_version() -> str:
    """获取应用版本。"""
    config = get_config()
    return config.app_version


def get_app_name() -> str:
    """获取应用名称。"""
    config = get_config()
    return config.app_name


def create_directory(path: Union[str, Path]) -> Path:
    """创建目录。

    Args:
        path: 目录路径

    Returns:
        创建的目录路径
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_directories() -> None:
    """确保必要的目录存在。"""
    config = get_config()

    # 创建存储目录
    if config.storage.provider == "local":
        create_directory(config.storage.local_path)

    # 创建日志目录
    if config.observability.log_file:
        log_dir = Path(config.observability.log_file).parent
        create_directory(log_dir)

    # 创建临时目录
    create_directory("tmp")
    create_directory("logs")


def print_config_summary() -> None:
    """打印配置摘要。"""
    config = get_config()
    filtered = config.filter_sensitive_data()

    print(f"\n=== {config.app_name} 配置摘要 ===")
    print(f"环境: {config.environment}")
    print(f"调试模式: {config.debug}")
    print(f"监听地址: {config.host}:{config.port}")
    print(f"工作进程: {config.workers}")
    print(f"多租户: {config.multi_tenant}")
    print(f"数据库: {config.database.host}:{config.database.port}/{config.database.name}")
    print(f"Redis: {config.redis.host}:{config.redis.port}/{config.redis.db}")
    print(f"日志级别: {config.observability.log_level}")
    print("=" * 40)


def validate_environment() -> None:
    """验证运行环境。"""
    # 检查Python版本
    if sys.version_info < (3, 12):
        print("警告: 建议使用Python 3.12或更高版本")

    # 检查必需的环境变量
    required_vars = ["SECURITY_SECRET_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            print(f"警告: 环境变量 {var} 未设置")

    # 检查配置文件
    config_files = [
        ".env",
        "config/development.yaml",
        "config/production.yaml",
    ]
    for file in config_files:
        if Path(file).exists():
            print(f"找到配置文件: {file}")


def get_config_value(key: str, default: Any = None) -> Any:
    """获取配置值。

    Args:
        key: 配置键，支持点号分隔的嵌套键
        default: 默认值

    Returns:
        配置值
    """
    config = get_config()
    keys = key.split(".")
    value = config

    for k in keys:
        if hasattr(value, k):
            value = getattr(value, k)
        else:
            return default

    return value


def set_config_value(key: str, value: Any) -> None:
    """设置配置值。

    Args:
        key: 配置键，支持点号分隔的嵌套键
        value: 配置值
    """
    config = get_config()
    keys = key.split(".")
    obj = config

    for k in keys[:-1]:
        if hasattr(obj, k):
            obj = getattr(obj, k)
        else:
            setattr(obj, k, {})
            obj = getattr(obj, k)

    setattr(obj, keys[-1], value)