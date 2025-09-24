"""
配置工厂类。

负责根据环境创建和返回相应的配置实例。
"""

import os
from typing import Dict, Type, Any

from .base import BaseConfig
from .development import DevelopmentConfig
from .testing import TestingConfig
from .production import ProductionConfig
from .staging import StagingConfig


class ConfigFactory:
    """配置工厂类。"""

    # 环境配置映射
    _config_classes: Dict[str, Type[BaseConfig]] = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
        "staging": StagingConfig,
    }

    @classmethod
    def create_config(cls, environment: str = None) -> BaseConfig:
        """创建配置实例。

        Args:
            environment: 环境名称，如果为None则从环境变量读取

        Returns:
            配置实例

        Raises:
            ValueError: 当环境名称无效时
        """
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development")

        config_class = cls._config_classes.get(environment.lower())
        if config_class is None:
            raise ValueError(f"无效的环境: {environment}. 可用环境: {list(cls._config_classes.keys())}")

        return config_class()

    @classmethod
    def get_available_environments(cls) -> list[str]:
        """获取所有可用环境列表。"""
        return list(cls._config_classes.keys())

    @classmethod
    def register_config(cls, environment: str, config_class: Type[BaseConfig]) -> None:
        """注册新的配置类。

        Args:
            environment: 环境名称
            config_class: 配置类
        """
        cls._config_classes[environment.lower()] = config_class


# 全局配置实例
_config_instance: BaseConfig = None


def get_config() -> BaseConfig:
    """获取全局配置实例。

    Returns:
        全局配置实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigFactory.create_config()
    return _config_instance


def set_config(config: BaseConfig) -> None:
    """设置全局配置实例。

    Args:
        config: 配置实例
    """
    global _config_instance
    _config_instance = config


def reload_config() -> BaseConfig:
    """重新加载配置。

    Returns:
        新的配置实例
    """
    global _config_instance
    _config_instance = ConfigFactory.create_config()
    return _config_instance