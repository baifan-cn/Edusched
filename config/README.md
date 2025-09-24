# 配置管理系统

Edusched使用分层的配置管理系统，支持多环境配置和动态加载。

## 目录结构

```
config/
├── __init__.py          # 配置模块导出
├── base.py              # 基础配置类
├── development.py       # 开发环境配置
├── testing.py           # 测试环境配置
├── production.py        # 生产环境配置
├── staging.py          # 预发布环境配置
├── factory.py           # 配置工厂
├── loader.py            # 配置加载器
├── validator.py         # 配置验证器
├── utils.py             # 配置工具函数
└── envs/                # 环境变量文件
    ├── .env.development
    ├── .env.testing
    ├── .env.production
    └── .env.staging
```

## 使用方法

### 1. 基本使用

```python
from config import get_config

# 获取当前配置
config = get_config()
print(config.app_name)
print(config.database.url)
```

### 2. 环境切换

```python
from config.factory import ConfigFactory

# 创建特定环境的配置
config = ConfigFactory.create_config("production")
```

使用脚本切换环境：
```bash
# 切换到开发环境
python scripts/switch-env.py development

# 切换到生产环境
python scripts/switch-env.py production
```

### 3. 配置验证

```python
from config.validator import config_validator
from config import get_config

config = get_config()
errors = config_validator.validate(config)

if errors:
    print("配置验证失败:")
    for error in errors:
        print(f"  - {error}")
```

## 环境变量优先级

配置加载的优先级从高到低：

1. 环境变量（覆盖其他配置）
2. `.env` 文件
3. 环境特定的配置类
4. 基础配置类默认值

## 配置项说明

### 应用配置
- `APP_NAME`: 应用名称
- `APP_VERSION`: 应用版本
- `DEBUG`: 调试模式
- `ENVIRONMENT`: 运行环境

### 数据库配置
- `DB_*`: 数据库相关配置
- 支持 PostgreSQL 连接池配置

### Redis配置
- `REDIS_*`: Redis 相关配置
- 支持连接池和超时设置

### 安全配置
- `SECURITY_*`: JWT 和安全相关配置
- 密钥长度至少32字符

### 调度引擎配置
- `SCHEDULING_*`: OR-Tools 调度引擎配置

### 可观测性配置
- `OBSERVABILITY_*`: 日志、监控、追踪配置

## 自定义配置

### 添加新的配置项

1. 在 `base.py` 的相应配置类中添加字段
2. 在环境配置类中覆盖默认值
3. 添加验证逻辑（如需要）

```python
# 在 base.py 中
class MyConfig(BaseSettings):
    my_setting: str = Field(default="default_value")
```

### 添加新的环境

1. 创建新的环境配置类
2. 注册到 ConfigFactory

```python
# custom.py
from .base import BaseConfig

class CustomConfig(BaseConfig):
    # 自定义配置
    pass

# 注册
ConfigFactory.register_config("custom", CustomConfig)
```

## 配置最佳实践

1. **敏感信息**: 使用环境变量存储密码、密钥等敏感信息
2. **环境隔离**: 不同环境使用不同的配置文件
3. **配置验证**: 启动时验证配置的有效性
4. **文档化**: 为所有配置项添加清晰的描述
5. **默认值**: 为非敏感配置提供合理的默认值

## 开发工具

### 配置查看

```python
from config.utils import print_config_summary
print_config_summary()
```

### 配置验证

```python
from config.utils import validate_environment
validate_environment()
```

### 获取配置值

```python
from config.utils import get_config_value

# 获取嵌套配置
db_url = get_config_value("database.url")
```

## 故障排除

### 常见问题

1. **配置不生效**
   - 检查环境变量是否正确设置
   - 确认 `.env` 文件位置正确

2. **验证失败**
   - 查看错误日志了解具体原因
   - 检查配置值类型和格式

3. **密钥错误**
   - 确保密钥长度符合要求
   - 生产环境使用强密钥

### 调试技巧

启用调试模式查看详细配置信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from config import get_config
config = get_config()
```

## 相关文档

- [环境变量配置](./envs/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI 配置](https://fastapi.tiangolo.com/advanced/settings/)