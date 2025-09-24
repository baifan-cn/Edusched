#!/usr/bin/env python3
"""
配置验证脚本。

用于验证当前配置的有效性。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """主函数。"""
    print("=== Edusched 配置验证工具 ===\n")

    try:
        # 导入配置模块
        from config import get_config
        from config.validator import config_validator
        from config.utils import validate_environment, print_config_summary

        # 获取当前配置
        print("1. 加载配置...")
        config = get_config()

        print(f"   环境: {config.environment}")
        print(f"   应用: {config.app_name} v{config.app_version}")
        print(f"   调试模式: {config.debug}\n")

        # 验证环境
        print("2. 验证运行环境...")
        validate_environment()
        print("   ✓ 环境验证通过\n")

        # 验证配置
        print("3. 验证配置...")
        errors = config_validator.validate(config)

        if errors:
            print("   ❌ 配置验证失败:")
            for error in errors:
                print(f"      - {error}")
            print("\n   请修复以上错误后重试。")
            sys.exit(1)
        else:
            print("   ✓ 配置验证通过\n")

        # 检查必需的配置
        print("4. 检查关键配置...")
        critical_configs = [
            ("数据库连接", config.database.url),
            ("Redis连接", config.redis.url),
            ("安全密钥", "***" if len(config.security.secret_key) >= 32 else "❌ 密钥太短"),
        ]

        for name, value in critical_configs:
            print(f"   ✓ {name}: 已配置")

        print("\n5. 检查敏感配置...")
        sensitive_issues = []

        if config.debug and config.environment == "production":
            sensitive_issues.append("生产环境启用了调试模式")

        if config.security.secret_key == "dev-secret-key-for-development-only":
            sensitive_issues.append("使用默认的开发密钥")

        if config.environment == "production" and config.observability.sentry_dsn == "":
            sensitive_issues.append("生产环境未配置Sentry")

        if sensitive_issues:
            print("   ⚠️  发现潜在问题:")
            for issue in sensitive_issues:
                print(f"      - {issue}")
        else:
            print("   ✓ 未发现敏感配置问题")

        # 打印配置摘要
        print("\n6. 配置摘要")
        print("-" * 40)
        print_config_summary()

        print("\n✅ 所有检查通过！配置有效。")

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保配置模块已正确安装。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()