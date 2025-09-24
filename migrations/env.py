"""Alembic环境配置。

这个模块配置了Alembic与SQLAlchemy 2.0的集成，支持多租户架构。
"""

import os
import sys
from logging.config import fileConfig
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import Connection, engine_from_config, pool
from sqlalchemy.engine import Engine

from alembic import context

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入您的模型的基础类和元数据
from edusched.infrastructure.database.models import Base

# 添加您的模型模块路径，以便autogenerate功能可以发现它们
import edusched.infrastructure.database.models  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config: Any = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url() -> str:
    """获取数据库URL。"""
    from dotenv import load_dotenv
    import os

    load_dotenv()

    # 优先从环境变量获取完整URL
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")

    # 否则从单个环境变量构建URL
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "edusched")
    db_user = os.getenv("DB_USER", "edusched")
    db_password = os.getenv("DB_PASSWORD", "edusched")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_engine() -> Engine:
    """获取数据库引擎。"""
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool

    url = get_url()

    # 在测试环境中使用NullPool以避免连接问题
    if os.getenv("TESTING"):
        return create_engine(url, poolclass=NullPool)

    return create_engine(url)


def run_migrations_offline() -> None:
    """在"离线"模式下运行迁移。

    这不需要实际的数据库连接，只是生成SQL脚本。
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 支持多租户的配置
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """执行实际的迁移操作。"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 支持多租户的配置
        include_schemas=True,
        # 自动检测枚举类型
        render_as_batch=True,
        # 支持比较类型
        compare_type=True,
        # 支持比较服务器默认值
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在"在线"模式下运行迁移。

    这需要实际的数据库连接。
    """
    connectable = get_engine()

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


def include_object(
    object: Any,
    name: str,
    type_: str,
    reflected: bool,
    compare_to: Optional[Any],
) -> bool:
    """控制哪些对象应该包含在迁移中。

    这个函数可以用来过滤掉某些不需要的表或索引。
    """
    # 跳过alembic_version表
    if type_ == "table" and name == "alembic_version":
        return False

    # 包含所有其他对象
    return True


def process_revision_directives(
    context: Any,
    revision: List[str],
    directives: List[Any],
) -> None:
    """处理迁移指令。

    可以用来修改自动生成的迁移脚本。
    """
    # 如果是autogenerate，可以在这里添加额外的逻辑
    if config.cmd_opts.autogenerate:
        # 获取迁移脚本
        script = directives[0]

        # 可以在这里修改脚本内容
        pass


def run_migrations_online_with_tenant(tenant_id: str) -> None:
    """为特定的租户运行迁移。

    这个函数可以用来为特定的租户运行迁移。
    """
    connectable = get_engine()

    with connectable.connect() as connection:
        # 设置租户ID
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
            # 设置租户特定的配置
            user_module_prefix="f'tenant_{tenant_id}_'",
        )

        with context.begin_transaction():
            context.run_migrations()