#!/usr/bin/env python3
"""
配置使用示例。

展示如何使用新的配置管理系统。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def basic_usage():
    """基本使用示例。"""
    print("=== 基本配置使用示例 ===\n")

    # 导入配置
    from config import get_config

    # 获取配置实例
    config = get_config()

    # 访问配置项
    print(f"应用名称: {config.app_name}")
    print(f"应用版本: {config.app_version}")
    print(f"运行环境: {config.environment}")
    print(f"调试模式: {config.debug}")

    # 访问子配置
    print(f"数据库URL: {config.database.url}")
    print(f"Redis URL: {config.redis.url}")
    print(f"日志级别: {config.observability.log_level}")


def environment_switching():
    """环境切换示例。"""
    print("\n=== 环境切换示例 ===\n")

    from config.factory import ConfigFactory

    # 创建不同环境的配置
    environments = ["development", "testing", "production"]

    for env in environments:
        try:
            config = ConfigFactory.create_config(env)
            print(f"{env:12} | 调试: {config.debug:5} | 数据库: {config.database.name}")
        except Exception as e:
            print(f"{env:12} | 错误: {e}")


def configuration_validation():
    """配置验证示例。"""
    print("\n=== 配置验证示例 ===\n")

    from config import get_config
    from config.validator import config_validator

    # 获取配置
    config = get_config()

    # 验证配置
    errors = config_validator.validate(config)

    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ 配置验证通过")


def utilities_usage():
    """工具函数使用示例。"""
    print("\n=== 工具函数使用示例 ===\n")

    from config.utils import (
        get_config_value,
        is_development,
        is_production,
        get_database_url,
        get_redis_url,
        print_config_summary
    )

    # 获取嵌套配置值
    db_url = get_config_value("database.url")
    print(f"数据库URL: {db_url}")

    # 检查环境
    print(f"是开发环境: {is_development()}")
    print(f"是生产环境: {is_production()}")

    # 获取特定URL
    print(f"数据库URL: {get_database_url()}")
    print(f"Redis URL: {get_redis_url()}")

    # 打印配置摘要
    print("\n配置摘要:")
    print_config_summary()


def custom_configuration():
    """自定义配置示例。"""
    print("\n=== 自定义配置示例 ===\n")

    from pydantic import Field
    from config.base import BaseConfig

    # 创建自定义配置类
    class CustomConfig(BaseConfig):
        """自定义配置示例。"""
        custom_feature: bool = Field(
            default=False,
            description="自定义功能开关"
        )
        custom_threshold: int = Field(
            default=100,
            ge=0,
            le=1000,
            description="自定义阈值"
        )

    # 使用自定义配置
    custom_config = CustomConfig()
    print(f"自定义功能: {custom_config.custom_feature}")
    print(f"自定义阈值: {custom_config.custom_threshold}")


def configuration_inheritance():
    """配置继承示例。"""
    print("\n=== 配置继承示例 ===\n")

    from config.development import DevelopmentConfig

    # 创建基于开发环境的自定义配置
    class ExtendedDevConfig(DevelopmentConfig):
        """扩展的开发环境配置。"""
        extended_feature: bool = True
        debug_level: str = "VERBOSE"

    extended_config = ExtendedDevConfig()
    print(f"扩展功能: {extended_config.extended_feature}")
    print(f"调试级别: {extended_config.debug_level}")
    print(f"继承的调试模式: {extended_config.debug}")


def hot_reload_example():
    """热重载示例。"""
    print("\n=== 配置热重载示例 ===\n")

    from config.loader import config_loader
    from config import get_config

    # 获取当前配置
    config_before = get_config()
    print(f"当前环境: {config_before.environment}")

    # 模拟热重载
    # 注意: 实际使用时需要修改环境变量或配置文件
    print("\n尝试热重载...")
    success = config_loader.hot_reload()

    if success:
        config_after = get_config()
        print(f"✓ 热重载成功")
        print(f"新环境: {config_after.environment}")
    else:
        print("❌ 热重载失败")


def main():
    """主函数。"""
    print("Edusched 配置管理系统使用示例\n")

    try:
        basic_usage()
        environment_switching()
        configuration_validation()
        utilities_usage()
        custom_configuration()
        configuration_inheritance()
        hot_reload_example()

        print("\n=== 运行完成 ===")
        print("更多用法请参考文档: docs/configuration.md")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()