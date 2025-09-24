#!/usr/bin/env python3
"""运行Alembic命令的包装脚本。"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["PYTHONPATH"] = str(project_root)

# 导入alembic并运行命令
from alembic.config import CommandLine

if __name__ == "__main__":
    # 创建Alembic命令行对象
    alembic_cli = CommandLine()

    # 设置配置文件路径
    config_file = project_root / "alembic.ini"

    # 运行命令
    alembic_cli.main(argv=["-c", str(config_file)] + sys.argv[1:])