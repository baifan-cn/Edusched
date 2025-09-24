"""
配置加载器。

负责从各种来源加载配置，支持动态配置和热重载。
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, ValidationError

from .factory import get_config, set_config


class ConfigLoader:
    """配置加载器。"""

    def __init__(self, base_path: Optional[Path] = None):
        """初始化配置加载器。

        Args:
            base_path: 配置文件基础路径，默认为项目根目录
        """
        self.base_path = base_path or Path(__file__).parent.parent
        self.config_dir = self.base_path / "config"
        self._cache: Dict[str, Any] = {}

    def load_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置。

        Returns:
            配置字典
        """
        config = {}

        # 遍历所有环境变量
        for key, value in os.environ.items():
            # 只加载相关的环境变量
            if any(prefix in key.upper() for prefix in [
                "APP_", "DB_", "REDIS_", "SECURITY_", "OIDC_",
                "SCHEDULING_", "OBSERVABILITY_", "MAIL_", "STORAGE_",
                "DEV_", "TEST_", "PROD_", "STAGING_"
            ]):
                # 尝试解析JSON值
                if value.startswith(("[", "{", '"')):
                    try:
                        config[key] = json.loads(value)
                    except json.JSONDecodeError:
                        config[key] = value
                # 尝试转换为布尔值
                elif value.lower() in ("true", "false"):
                    config[key] = value.lower() == "true"
                # 尝试转换为数字
                elif value.isdigit():
                    config[key] = int(value)
                elif value.replace(".", "", 1).isdigit():
                    config[key] = float(value)
                else:
                    config[key] = value

        return config

    def load_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """从文件加载配置。

        Args:
            file_path: 配置文件路径，支持JSON、YAML格式

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 根据扩展名解析
        if file_path.suffix.lower() in (".json",):
            return json.loads(content)
        elif file_path.suffix.lower() in (".yaml", ".yml"):
            return yaml.safe_load(content)
        else:
            raise ValueError(f"不支持的配置文件格式: {file_path.suffix}")

    def load_from_directory(self, directory: Union[str, Path] = None) -> Dict[str, Any]:
        """从目录加载所有配置文件。

        Args:
            directory: 配置目录路径，默认为config目录

        Returns:
            合并后的配置字典
        """
        if directory is None:
            directory = self.config_dir

        directory = Path(directory)
        if not directory.exists():
            return {}

        config = {}

        # 加载所有配置文件
        for file_path in directory.glob("*"):
            if file_path.is_file() and file_path.suffix in (".json", ".yaml", ".yml"):
                try:
                    file_config = self.load_from_file(file_path)
                    config[file_path.stem] = file_config
                except Exception as e:
                    print(f"加载配置文件失败 {file_path}: {e}")

        return config

    def load_overrides(self, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """加载覆盖配置。

        Args:
            overrides: 覆盖配置字典

        Returns:
            合并后的配置字典
        """
        return overrides

    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """合并多个配置字典。

        Args:
            *configs: 多个配置字典

        Returns:
            合并后的配置字典
        """
        merged = {}
        for config in configs:
            if config:
                self._deep_update(merged, config)
        return merged

    def _deep_update(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """深度更新字典。

        Args:
            base: 基础字典
            update: 更新字典
        """
        for key, value in update.items():
            if (
                key in base
                and isinstance(base[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def load_config(self) -> Dict[str, Any]:
        """加载完整的配置。

        Returns:
            完整的配置字典
        """
        # 加载顺序：环境变量 < 配置文件 < 覆盖配置
        env_config = self.load_from_env()
        file_config = self.load_from_directory()

        # 合并配置
        config = self.merge_configs(env_config, file_config)

        # 缓存配置
        self._cache = config

        return config

    def hot_reload(self) -> bool:
        """热重载配置。

        Returns:
            是否成功重载
        """
        try:
            # 重新加载配置
            new_config = self.load_config()

            # 更新全局配置
            from .factory import ConfigFactory
            environment = new_config.get("environment", "development")
            new_config_instance = ConfigFactory.create_config(environment)
            set_config(new_config_instance)

            return True
        except Exception as e:
            print(f"热重载配置失败: {e}")
            return False

    def validate_config(self, config_dict: Dict[str, Any]) -> bool:
        """验证配置。

        Args:
            config_dict: 配置字典

        Returns:
            是否验证通过
        """
        try:
            # 尝试创建配置实例进行验证
            environment = config_dict.get("environment", "development")
            from .factory import ConfigFactory
            config_class = ConfigFactory._config_classes.get(environment)
            if config_class:
                config_class(**config_dict)
            return True
        except ValidationError as e:
            print(f"配置验证失败: {e}")
            return False
        except Exception as e:
            print(f"配置验证错误: {e}")
            return False

    def get_cached_config(self) -> Dict[str, Any]:
        """获取缓存的配置。

        Returns:
            缓存的配置字典
        """
        return self._cache.copy()


# 全局配置加载器实例
config_loader = ConfigLoader()