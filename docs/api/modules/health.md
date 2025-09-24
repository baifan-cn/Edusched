# 健康检查 API

## 概述

健康检查 API 提供系统状态监控和诊断功能，用于检查系统各组件的运行状态，确保服务正常运行。此 API 主要用于运维监控和故障诊断。

### 基础信息

- **路径**: `/api/v1/health`
- **方法**: GET
- **认证**: 无需认证
- **用途**: 系统健康状态检查

## API 端点

### 健康检查

**GET** `/api/v1/health`

检查系统各组件的健康状态，包括数据库连接、缓存服务等。

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

#### 响应示例

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "response_time": 0.005,
      "connection_pool": {
        "total": 10,
        "available": 8,
        "used": 2
      }
    },
    "cache": {
      "status": "healthy",
      "response_time": 0.002,
      "memory_usage": 45.2
    },
    "scheduling_engine": {
      "status": "healthy",
      "active_jobs": 0,
      "queue_size": 0,
      "last_job": null
    }
  },
  "metrics": {
    "uptime": 86400,
    "memory_usage": 256.5,
    "cpu_usage": 15.3,
    "requests_per_minute": 120
  }
}
```

### 响应字段说明

#### 主要字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `status` | string | 整体健康状态 |
| `timestamp` | string | 检查时间戳 |
| `version` | string | 系统版本 |
| `components` | object | 各组件状态详情 |
| `metrics` | object | 系统性能指标 |

#### 健康状态值

- `healthy` - 系统正常运行
- `degraded` - 系统性能下降，但仍可提供服务
- `unhealthy` - 系统存在严重问题，无法正常服务

#### 组件状态详情

**数据库状态**
```json
{
  "database": {
    "status": "healthy",
    "response_time": 0.005,
    "connection_pool": {
      "total": 10,
      "available": 8,
      "used": 2
    }
  }
}
```

**缓存状态**
```json
{
  "cache": {
    "status": "healthy",
    "response_time": 0.002,
    "memory_usage": 45.2
  }
}
```

**调度引擎状态**
```json
{
  "scheduling_engine": {
    "status": "healthy",
    "active_jobs": 0,
    "queue_size": 0,
    "last_job": null
  }
}
```

## 使用场景

### 1. 负载均衡器健康检查

```bash
# 负载均衡器定期检查
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "服务健康"
else
    echo "服务异常"
fi
```

### 2. 容器编排健康检查

```yaml
# Kubernetes 健康检查示例
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 3. 监控系统集成

```python
# Python 监控脚本示例
import requests
import time
from datetime import datetime

def monitor_health():
    url = "http://localhost:8000/api/v1/health"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        timestamp = datetime.now().isoformat()
        status = data.get('status', 'unknown')

        print(f"[{timestamp}] 系统状态: {status}")

        # 检查各组件状态
        components = data.get('components', {})
        for component, info in components.items():
            comp_status = info.get('status', 'unknown')
            if comp_status != 'healthy':
                print(f"警告: {component} 状态异常 - {comp_status}")

        # 记录性能指标
        metrics = data.get('metrics', {})
        cpu_usage = metrics.get('cpu_usage', 0)
        memory_usage = metrics.get('memory_usage', 0)

        print(f"CPU使用率: {cpu_usage}%, 内存使用: {memory_usage}MB")

    except requests.exceptions.RequestException as e:
        print(f"健康检查失败: {e}")

# 定期监控
while True:
    monitor_health()
    time.sleep(60)  # 每分钟检查一次
```

## 故障诊断

### 常见问题

#### 1. 数据库连接失败

**症状**: 组件状态中数据库显示 `unhealthy`

**可能原因**:
- 数据库服务未启动
- 网络连接问题
- 认证信息错误
- 连接池耗尽

**诊断步骤**:
```bash
# 检查数据库连接
curl -X GET "http://localhost:8000/api/v1/health"

# 查看数据库服务状态
systemctl status postgresql

# 检查网络连接
telnet localhost 5432
```

#### 2. 缓存服务异常

**症状**: 组件状态中缓存显示 `degraded` 或 `unhealthy`

**可能原因**:
- Redis 服务未启动
- 内存不足
- 网络延迟

**诊断步骤**:
```bash
# 检查Redis服务
redis-cli ping

# 检查Redis内存使用
redis-cli info memory
```

#### 3. 调度引擎异常

**症状**: 组件状态中调度引擎显示 `unhealthy`

**可能原因**:
- 调度任务堆积
- 资源耗尽
- 算法异常

**诊断步骤**:
```bash
# 检查调度任务状态
curl -X GET "http://localhost:8000/api/v1/scheduling/jobs"

# 查看系统资源使用
top
```

## 监控指标

### 关键指标

#### 1. 响应时间
- 数据库响应时间: < 100ms
- 缓存响应时间: < 10ms
- API 响应时间: < 500ms

#### 2. 资源使用
- CPU 使用率: < 80%
- 内存使用率: < 85%
- 磁盘使用率: < 90%

#### 3. 连接池状态
- 可用连接数: > 0
- 连接使用率: < 80%
- 等待连接数: < 5

#### 4. 调度状态
- 活跃任务数: < 10
- 队列长度: < 50
- 任务失败率: < 5%

### 告警规则

#### 高优先级告警
- 系统状态为 `unhealthy`
- 数据库连接失败
- 缓存服务不可用
- 内存使用率 > 90%

#### 中优先级告警
- 系统状态为 `degraded`
- 响应时间 > 1s
- CPU 使用率 > 80%
- 调度任务失败

#### 低优先级告警
- 连接池使用率 > 80%
- 磁盘使用率 > 80%
- 缓存命中率 < 90%

## 配置选项

### 健康检查配置

```python
# 在 FastAPI 应用中配置健康检查
from fastapi import FastAPI
import asyncio
import asyncpg
import redis

app = FastAPI()

@app.get("/api/v1/health")
async def health_check():
    """健康检查端点"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {},
        "metrics": {}
    }

    # 检查数据库
    try:
        start_time = time.time()
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.close()
        db_response_time = time.time() - start_time
        health_status["components"]["database"] = {
            "status": "healthy",
            "response_time": db_response_time
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # 检查缓存
    try:
        start_time = time.time()
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        cache_response_time = time.time() - start_time
        health_status["components"]["cache"] = {
            "status": "healthy",
            "response_time": cache_response_time
        }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # 检查调度引擎
    try:
        # 检查活跃任务数等
        health_status["components"]["scheduling_engine"] = {
            "status": "healthy",
            "active_jobs": 0,
            "queue_size": 0
        }
    except Exception as e:
        health_status["components"]["scheduling_engine"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    return health_status
```

### 性能监控配置

```python
import psutil

def get_system_metrics():
    """获取系统性能指标"""
    return {
        "uptime": time.time() - psutil.boot_time(),
        "memory_usage": psutil.virtual_memory().used / 1024 / 1024,  # MB
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent,
        "network_io": psutil.net_io_counters()._asdict()
    }
```

## 最佳实践

### 1. 定期检查

- 设置合适的检查间隔（建议 30-60 秒）
- 避免过于频繁的检查造成系统负担
- 在业务低峰期进行深度检查

### 2. 错误处理

- 实现优雅降级机制
- 设置合理的超时时间
- 记录详细的错误日志

### 3. 监控集成

- 与现有监控系统集成
- 支持多种告警方式
- 提供可视化监控面板

### 4. 安全考虑

- 健康检查端点无需认证，但要限制访问
- 避免在健康检查中返回敏感信息
- 监控日志和访问模式

## 注意事项

1. **性能影响**: 健康检查会增加系统负载，需要合理设置检查频率
2. **网络分区**: 考虑网络分区情况下的健康检查策略
3. **级联故障**: 避免健康检查本身成为故障点
4. **监控覆盖**: 确保所有关键组件都被监控
5. **告警疲劳**: 合理设置告警阈值，避免误报