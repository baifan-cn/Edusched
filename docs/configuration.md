# 配置管理指南

## 概述

Edusched使用分层的配置管理系统，支持多环境配置、动态加载和验证。配置系统基于Pydantic Settings构建，提供类型安全的配置管理。

## 快速开始

### 1. 环境切换

```bash
# 切换到开发环境
python scripts/switch-env.py development

# 切换到测试环境
python scripts/switch-env.py testing

# 切换到生产环境
python scripts/switch-env.py production
```

### 2. 配置验证

```bash
# 验证当前配置
python scripts/validate-config.py
```

### 3. 基本使用

```python
from config import get_config

# 获取配置
config = get_config()

# 访问配置项
print(config.app_name)
print(config.database.url)
print(config.is_development)
```

## 配置结构

### 基础配置类

所有环境配置都继承自`BaseConfig`，包含以下主要部分：

- **应用配置**: 应用名称、版本、环境等
- **服务配置**: 监听地址、端口、工作进程等
- **数据库配置**: PostgreSQL连接和池化配置
- **Redis配置**: Redis连接和缓存配置
- **安全配置**: JWT、密码策略等
- **调度引擎配置**: OR-Tools相关配置
- **可观测性配置**: 日志、监控、追踪配置

### 环境特定配置

每个环境都有特定的配置类：

- `DevelopmentConfig`: 开发环境配置
- `TestingConfig`: 测试环境配置
- `StagingConfig`: 预发布环境配置
- `ProductionConfig`: 生产环境配置

## 环境变量

### 环境变量优先级

1. 系统环境变量（最高优先级）
2. `.env` 文件
3. 环境配置类
4. 基础配置默认值

### 关键环境变量

```bash
# 应用配置
APP_NAME=Edusched
ENVIRONMENT=development
DEBUG=true

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=edusched
DB_USER=edusched
DB_PASSWORD=your_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 安全配置
SECURITY_SECRET_KEY=your-super-secret-key
SECURITY_ALGORITHM=HS256
```

## 配置文件

### 环境配置文件

配置文件位于`config/envs/`目录：

- `.env.development`: 开发环境
- `.env.testing`: 测试环境
- `.env.staging`: 预发布环境
- `.env.production`: 生产环境

### YAML配置文件

支持YAML格式的配置文件，位于`config/`目录：

```yaml
# config/development.yaml
app:
  name: "Edusched"
  debug: true

database:
  host: "localhost"
  port: 5432
  name: "edusched_dev"
```

## 最佳实践

### 1. 敏感信息管理

- **不要**将密码、密钥等敏感信息提交到版本控制
- 使用环境变量存储敏感信息
- 生产环境使用密钥管理服务

### 2. 环境隔离

- 不同环境使用不同的数据库
- 测试环境使用独立的数据存储
- 生产环境禁用调试功能

### 3. 配置验证

- 启动时验证配置有效性
- 检查必需的配置项
- 验证配置值格式和范围

### 4. 配置文档

- 为所有配置项添加描述
- 提供配置示例
- 记录配置变更历史

## 开发指南

### 添加新的配置项

1. 在`base.py`中添加到相应的配置类
2. 设置合适的默认值和验证规则
3. 在环境配置中覆盖默认值（如果需要）
4. 更新文档和示例

```python
# config/base.py
class ObservabilityConfig(BaseSettings):
    new_metric_enabled: bool = Field(
        default=True,
        description="是否启用新指标"
    )
```

### 添加新的环境

1. 创建新的环境配置类
2. 注册到配置工厂
3. 创建环境变量文件
4. 添加验证规则

```python
# config/custom.py
from .base import BaseConfig

class CustomConfig(BaseConfig):
    """自定义环境配置。"""
    environment: str = "custom"
    # 其他自定义配置
```

### 配置热重载

```python
from config.loader import config_loader

# 热重载配置
success = config_loader.hot_reload()
if success:
    print("配置重载成功")
```

## 故障排除

### 常见问题

1. **配置不生效**
   - 检查环境变量设置
   - 确认`.env`文件位置
   - 验证配置语法

2. **验证失败**
   - 查看详细错误信息
   - 检查配置值类型
   - 确认必需的配置项

3. **导入错误**
   - 确认配置模块路径
   - 检查Python环境
   - 验证依赖安装

### 调试技巧

启用调试日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from config import get_config
config = get_config()
```

查看配置摘要：

```python
from config.utils import print_config_summary
print_config_summary()
```

## 配置参考

### 数据库配置

| 配置项 | 默认值 | 描述 |
|--------|--------|------|
| DB_HOST | localhost | 数据库主机 |
| DB_PORT | 5432 | 数据库端口 |
| DB_NAME | edusched | 数据库名称 |
| DB_POOL_SIZE | 20 | 连接池大小 |
| DB_MAX_OVERFLOW | 30 | 最大溢出连接数 |

### Redis配置

| 配置项 | 默认值 | 描述 |
|--------|--------|------|
| REDIS_HOST | localhost | Redis主机 |
| REDIS_PORT | 6379 | Redis端口 |
| REDIS_DB | 0 | Redis数据库编号 |
| REDIS_POOL_SIZE | 10 | 连接池大小 |

### 安全配置

| 配置项 | 要求 | 描述 |
|--------|------|------|
| SECURITY_SECRET_KEY | ≥32字符 | JWT签名密钥 |
| SECURITY_ALGORITHM | HS256/RS256 | 签名算法 |
| SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES | ≥1 | 访问令牌过期时间 |

## 相关资源

- [Pydantic Settings文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI配置指南](https://fastapi.tiangolo.com/advanced/settings/)
- [12-Factor App配置原则](https://12factor.net/config)