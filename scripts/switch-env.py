#!/usr/bin/env python3
"""
环境切换脚本。

用于在不同的环境配置之间切换。
"""

import os
import sys
import shutil
from pathlib import Path

from config.utils import get_config, validate_environment


def main():
    """主函数。"""
    if len(sys.argv) != 2:
        print("用法: python switch-env.py <environment>")
        print("可用环境: development, testing, staging, production")
        sys.exit(1)

    environment = sys.argv[1].lower()

    # 验证环境
    config = get_config()
    if environment not in config._config_classes:
        print(f"错误: 无效的环境 '{environment}'")
        print(f"可用环境: {list(config._config_classes.keys())}")
        sys.exit(1)

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 源文件和目标文件路径
    source_env_file = project_root / "config" / "envs" / f".env.{environment}"
    target_env_file = project_root / ".env"

    # 检查源文件是否存在
    if not source_env_file.exists():
        print(f"错误: 配置文件不存在 {source_env_file}")
        sys.exit(1)

    # 备份现有的.env文件
    if target_env_file.exists():
        backup_file = project_root / ".env.backup"
        shutil.copy2(target_env_file, backup_file)
        print(f"已备份现有配置到 {backup_file}")

    # 复制新的配置文件
    shutil.copy2(source_env_file, target_env_file)
    print(f"已切换到 {environment} 环境")

    # 验证配置
    try:
        from config.factory import ConfigFactory
        new_config = ConfigFactory.create_config(environment)
        print(f"配置验证通过: {new_config.app_name} v{new_config.app_version}")

        # 打印配置摘要
        print("\n配置摘要:")
        print(f"  环境: {new_config.environment}")
        print(f"  调试模式: {new_config.debug}")
        print(f"  数据库: {new_config.database.host}:{new_config.database.port}/{new_config.database.name}")
        print(f"  Redis: {new_config.redis.host}:{new_config.redis.port}/{new_config.redis.db}")

    except Exception as e:
        print(f"警告: 配置验证失败 - {e}")

    print("\n注意: 请重新启动应用使配置生效")


if __name__ == "__main__":
    main()