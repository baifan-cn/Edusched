#!/usr/bin/env python3
"""数据库迁移管理脚本。

这个脚本提供了管理数据库迁移的便捷命令。
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(project_root / ".env")


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(description="数据库迁移管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 升级命令
    upgrade_parser = subparsers.add_parser("upgrade", help="升级数据库到最新版本")
    upgrade_parser.add_argument("--revision", "-r", help="指定要升级到的版本")
    upgrade_parser.add_argument("--sql", action="store_true", help="生成SQL脚本而不是执行")

    # 降级命令
    downgrade_parser = subparsers.add_parser("downgrade", help="降级数据库到指定版本")
    downgrade_parser.add_argument("revision", help="要降级到的版本")
    downgrade_parser.add_argument("--sql", action="store_true", help="生成SQL脚本而不是执行")

    # 创建迁移命令
    revision_parser = subparsers.add_parser("revision", help="创建新的迁移文件")
    revision_parser.add_argument("-m", "--message", required=True, help="迁移消息")
    revision_parser.add_argument("--autogenerate", action="store_true", help="自动生成迁移")

    # 历史命令
    history_parser = subparsers.add_parser("history", help="显示迁移历史")
    history_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")

    # 当前版本命令
    subparsers.add_parser("current", help="显示当前数据库版本")

    # 检查命令
    subparsers.add_parser("check", help="检查迁移状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        from alembic.config import Config
        from alembic import command
        from alembic.script import ScriptDirectory

        # 配置Alembic
        alembic_cfg = Config(project_root / "alembic.ini")

        # 设置数据库URL
        if not os.getenv("DATABASE_URL"):
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "edusched")
            db_user = os.getenv("DB_USER", "edusched")
            db_password = os.getenv("DB_PASSWORD", "edusched")
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            alembic_cfg.set_main_option("sqlalchemy.url", database_url)

        if args.command == "upgrade":
            revision = args.revision or "head"
            if args.sql:
                command.upgrade(alembic_cfg, revision, sql=True)
            else:
                print(f"正在升级数据库到版本: {revision}")
                command.upgrade(alembic_cfg, revision)
                print("数据库升级完成")

        elif args.command == "downgrade":
            if args.sql:
                command.downgrade(alembic_cfg, args.revision, sql=True)
            else:
                print(f"正在降级数据库到版本: {args.revision}")
                command.downgrade(alembic_cfg, args.revision)
                print("数据库降级完成")

        elif args.command == "revision":
            kwargs = {"message": args.message}
            if args.autogenerate:
                kwargs["autogenerate"] = True

            print(f"正在创建迁移: {args.message}")
            command.revision(alembic_cfg, **kwargs)
            print("迁移文件创建完成")

        elif args.command == "history":
            script = ScriptDirectory.from_config(alembic_cfg)
            for rev in script.walk_revisions():
                if args.verbose:
                    print(f"{rev.revision} -> {rev.down_revision} ({rev.doc})")
                else:
                    print(f"{rev.revision} -> {rev.down_revision}")

        elif args.command == "current":
            print(f"当前数据库版本: {command.current(alembic_cfg)}")

        elif args.command == "check":
            print("正在检查迁移状态...")
            command.check(alembic_cfg)
            print("迁移状态正常")

    except ImportError as e:
        print(f"错误: 缺少依赖包 - {e}")
        print("请安装项目依赖: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()