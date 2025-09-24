# 外部服务集成模块

## 概述

Edusched 的外部服务集成模块提供了统一的接口来访问各种外部服务，包括邮件、通知、文件存储、日志和缓存服务。该模块遵循依赖倒置原则，使用抽象接口定义服务契约，支持多种服务提供商的轻松切换。

## 架构设计

### 目录结构

```
src/edusched/infrastructure/external/
├── __init__.py                    # 模块入口，导出公共接口
├── base.py                        # 基础抽象类和异常定义
├── factory.py                     # 服务工厂和管理器
├── config.py                      # 配置管理
├── email/                         # 邮件服务
│   ├── __init__.py
│   ├── interfaces.py             # 邮件服务接口
│   ├── service.py                 # 邮件服务主类
│   └── providers.py               # 邮件服务提供商实现
├── notification/                 # 通知服务
│   ├── __init__.py
│   ├── interfaces.py             # 通知服务接口
│   ├── service.py                 # 通知服务主类
│   └── providers.py               # 通知服务提供商实现
├── storage/                       # 存储服务
│   ├── __init__.py
│   ├── interfaces.py             # 存储服务接口
│   ├── service.py                 # 存储服务主类
│   └── providers.py               # 存储服务提供商实现
├── logging/                       # 日志服务
│   ├── __init__.py
│   ├── interfaces.py             # 日志服务接口
│   ├── service.py                 # 日志服务主类
│   └── providers.py               # 日志服务提供商实现
└── cache/                         # 缓存服务
    ├── __init__.py
    ├── interfaces.py             # 缓存服务接口
    ├── service.py                 # 缓存服务主类
    └── providers.py               # 缓存服务提供商实现
```

### 核心特性

1. **统一接口**：所有服务都继承自 `BaseService`，提供一致的 API
2. **提供商切换**：通过工厂模式支持不同服务提供商的动态切换
3. **错误处理**：统一的异常体系和重试机制
4. **熔断保护**：内置熔断器防止级联故障
5. **性能监控**：自动收集服务指标和健康状态
6. **配置管理**：基于环境变量的配置管理

## 使用示例

### 初始化服务

```python
from edusched.infrastructure.external import init_external_services

# 初始化所有外部服务
await init_external_services()
```

### 发送邮件

```python
from edusched.infrastructure.external import get_email_service
from edusched.infrastructure.external.email.interfaces import EmailMessage

# 获取邮件服务
email_service = get_email_service()

# 创建邮件消息
message = EmailMessage(
    to=["user@example.com"],
    subject="欢迎使用 Edusched",
    content="这是一封测试邮件",
    html_content="<h1>欢迎使用 Edusched</h1><p>这是一封测试邮件</p>"
)

# 发送邮件
result = await email_service.send_email(message)
```

### 发送通知

```python
from edusched.infrastructure.external import get_notification_service
from edusched.infrastructure.external.notification.interfaces import (
    NotificationMessage,
    NotificationTarget,
    NotificationChannel
)

# 获取通知服务
notification_service = get_notification_service()

# 创建通知消息
message = NotificationMessage(
    title="系统维护通知",
    content="系统将于今晚 22:00-24:00 进行维护",
    targets=[
        NotificationTarget(channel=NotificationChannel.EMAIL, address="user@example.com"),
        NotificationTarget(channel=NotificationChannel.SMS, address="13800138000")
    ]
)

# 发送通知
results = await notification_service.send_notification(message)
```

### 文件存储

```python
from edusched.infrastructure.external import get_storage_service

# 获取存储服务
storage_service = get_storage_service()

# 上传文件
result = await storage_service.upload_file(
    file_path="/path/to/local/file.pdf",
    key="documents/2024/report.pdf",
    content_type="application/pdf"
)

# 下载文件
success = await storage_service.download_file(
    key="documents/2024/report.pdf",
    file_path="/path/to/download/file.pdf"
)
```

### 缓存操作

```python
from edusched.infrastructure.external import get_cache_service

# 获取缓存服务
cache_service = get_cache_service()

# 设置缓存
await cache_service.set("user:123", {"name": "张三", "age": 25}, ttl=3600)

# 获取缓存
user_data = await cache_service.get("user:123")

# 使用缓存装饰器
@cache_service.cached_decorator(ttl=300)
async def get_user_data(user_id: int):
    # 模拟耗时操作
    await asyncio.sleep(1)
    return {"user_id": user_id, "data": "some data"}
```

## 配置说明

### 环境变量

所有外部服务都支持通过环境变量进行配置：

```bash
# 邮件服务配置
EDUSCHED_EMAIL_ENABLED=true
EDUSCHED_EMAIL_PROVIDER=smtp
EDUSCHED_EMAIL_SMTP_HOST=smtp.example.com
EDUSCHED_EMAIL_SMTP_PORT=587
EDUSCHED_EMAIL_SMTP_USERNAME=user@example.com
EDUSCHED_EMAIL_SMTP_PASSWORD=password

# 存储服务配置
EDUSCHED_STORAGE_ENABLED=true
EDUSCHED_STORAGE_PROVIDER=local
EDUSCHED_STORAGE_LOCAL_PATH=/tmp/storage
EDUSCHED_STORAGE_BASE_URL=http://localhost:8000/files

# 缓存服务配置
EDUSCHED_CACHE_ENABLED=true
EDUSCHED_CACHE_PROVIDER=redis
EDUSCHED_CACHE_REDIS_URL=redis://localhost:6379
EDUSCHED_CACHE_DEFAULT_TTL=3600
```

### 动态配置

```python
from edusched.infrastructure.external.config import ExternalServicesConfig

# 从环境变量加载配置
config = ExternalServicesConfig()

# 获取特定服务的配置
email_config = config.get_email_config()
storage_config = config.get_storage_config()
```

## 扩展新服务

### 添加新的服务类型

1. 在 `base.py` 中添加新的 `ServiceType`
2. 创建服务目录和接口文件
3. 实现服务类和提供商
4. 在工厂中注册服务类型

### 添加新的提供商

1. 在服务的 `interfaces.py` 中添加新的提供商枚举
2. 在 `providers.py` 中实现新的提供商类
3. 更新服务主类以支持新提供商

## 最佳实践

1. **使用依赖注入**：通过工厂获取服务实例，避免直接实例化
2. **正确处理异常**：捕获并处理 `ExternalServiceError` 及其子类
3. **合理设置超时**：根据服务特性设置合适的超时时间
4. **使用重试机制**：对于临时性故障，让系统自动重试
5. **监控服务状态**：定期检查健康状态和服务指标
6. **合理使用缓存**：避免缓存雪崩和穿透问题

## 故障排查

### 常见问题

1. **服务连接失败**
   - 检查网络连接
   - 验证认证信息
   - 查看服务日志

2. **性能问题**
   - 检查服务指标
   - 调整超时和重试配置
   - 考虑使用本地缓存

3. **配置错误**
   - 验证环境变量
   - 检查配置文件格式
   - 确认权限设置

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
from edusched.infrastructure.external import get_logging_service
logging_service = get_logging_service()
logging_service.log_config.level = LogLevel.DEBUG
```