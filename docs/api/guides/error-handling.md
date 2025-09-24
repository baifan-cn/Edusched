# API 错误处理指南

## 概述

本指南详细说明了 Edusched API 的错误处理机制，包括常见错误类型、错误响应格式以及最佳实践。

## 错误响应格式

### 标准错误响应

所有 API 错误都遵循统一的响应格式：

```json
{
  "error": "错误类型",
  "message": "详细的错误信息",
  "status_code": 400,
  "path": "/api/v1/schools/",
  "timestamp": "2024-01-01T00:00:00Z",
  "details": []
}
```

### 字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `error` | string | 错误类型标识符 |
| `message` | string | 用户友好的错误信息 |
| `status_code` | integer | HTTP 状态码 |
| `path` | string | 请求路径 |
| `timestamp` | string | 错误发生时间 |
| `details` | array | 详细的错误信息（可选） |

## HTTP 状态码

### 客户端错误 (4xx)

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误或格式不正确 |
| 401 | Unauthorized | 未授权访问（待实现） |
| 403 | Forbidden | 禁止访问（待实现） |
| 404 | Not Found | 请求的资源不存在 |
| 409 | Conflict | 资源冲突或状态不允许 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 请求过于频繁 |

### 服务器错误 (5xx)

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务不可用 |
| 504 | Gateway Timeout | 网关超时 |

## 常见错误类型

### 1. 认证错误 (401)

```json
{
  "error": "AuthenticationError",
  "message": "缺少或无效的认证信息",
  "status_code": 401,
  "path": "/api/v1/schools/"
}
```

**原因**：
- 缺少 `X-Tenant-ID` 请求头
- 租户 ID 格式不正确
- 租户不存在

**解决方案**：
```python
# 正确设置请求头
headers = {
    "X-Tenant-ID": "your-tenant-id",
    "Content-Type": "application/json"
}
```

### 2. 资源不存在 (404)

```json
{
  "error": "NotFoundError",
  "message": "学校不存在",
  "status_code": 404,
  "path": "/api/v1/schools/550e8400-e29b-41d4-a716-446655440000"
}
```

**原因**：
- ID 格式错误
- 资源已被删除
- 租户数据隔离导致无法访问

**解决方案**：
```python
# 检查资源是否存在
def check_resource_exists(resource_id, resource_type):
    response = requests.get(
        f"{BASE_URL}/api/v1/{resource_type}/{resource_id}",
        headers=headers
    )
    return response.status_code == 200

# 使用前验证
if not check_resource_exists(school_id, "schools"):
    print("学校不存在")
    return
```

### 3. 数据验证错误 (422)

```json
{
  "error": "ValidationError",
  "message": "请求数据格式不正确",
  "status_code": 422,
  "path": "/api/v1/schools/",
  "details": [
    {
      "loc": ["body", "code"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "academic_year"],
      "msg": "string does not match regex",
      "type": "value_error.str.regex"
    }
  ]
}
```

**原因**：
- 缺少必需字段
- 字段格式不正确
- 数据类型错误
- 值超出范围

**解决方案**：
```python
# 验证数据格式
def validate_school_data(data):
    required_fields = ['name', 'code', 'academic_year', 'semester']

    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必需字段: {field}")

    # 验证学年格式
    if not re.match(r'^\d{4}-\d{4}$', data['academic_year']):
        raise ValueError("学年格式不正确，应为 YYYY-YYYY")

    return True

# 使用前验证
try:
    validate_school_data(school_data)
except ValueError as e:
    print(f"数据验证失败: {e}")
    return
```

### 4. 唯一性冲突 (400)

```json
{
  "error": "DuplicateError",
  "message": "学校代码已存在",
  "status_code": 400,
  "path": "/api/v1/schools/"
}
```

**原因**：
- 学校代码重复
- 教师工号重复
- 课程代码重复

**解决方案**：
```python
# 检查唯一性
def check_code_exists(code, resource_type):
    response = requests.get(
        f"{BASE_URL}/api/v1/{resource_type}/",
        headers=headers,
        params={"code": code}
    )
    data = response.json()
    return len(data) > 0

# 使用前检查
if check_code_exists(school_data['code'], "schools"):
    print("学校代码已存在")
    return
```

### 5. 状态冲突 (409)

```json
{
  "error": "StateConflictError",
  "message": "只有已优化或可行的时间表才能发布",
  "status_code": 409,
  "path": "/api/v1/timetables/550e8400-e29b-41d4-a716-446655440000/publish"
}
```

**原因**：
- 资源状态不允许执行操作
- 业务流程不符合要求

**解决方案**：
```python
# 检查资源状态
def get_timetable_status(timetable_id):
    response = requests.get(
        f"{BASE_URL}/api/v1/timetables/{timetable_id}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()['status']
    return None

# 检查是否可以发布
status = get_timetable_status(timetable_id)
if status not in ['optimized', 'feasible']:
    print(f"时间表状态 {status} 不允许发布")
    return
```

### 6. 调度错误 (500)

```json
{
  "error": "SchedulingError",
  "message": "调度算法内部错误",
  "status_code": 500,
  "path": "/api/v1/scheduling/start"
}
```

**原因**：
- 算法参数错误
- 约束冲突
- 系统资源不足

**解决方案**：
```python
# 验证调度参数
def validate_scheduling_params(timetable_id):
    # 检查时间表是否存在
    response = requests.get(
        f"{BASE_URL}/api/v1/timetables/{timetable_id}",
        headers=headers
    )
    if response.status_code != 200:
        return False, "时间表不存在"

    # 检查是否有教学段
    timetable = response.json()
    if timetable['total_sections'] == 0:
        return False, "没有教学段需要调度"

    return True, "验证通过"
```

## 错误处理最佳实践

### 1. 统一错误处理

```python
import requests
from typing import Dict, Any, Tuple

class EduschedAPIError(Exception):
    """自定义API错误类"""

    def __init__(self, message: str, status_code: int, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

def handle_api_response(response: requests.Response) -> Tuple[bool, Any]:
    """统一处理API响应"""
    try:
        if response.status_code == 200:
            return True, response.json()

        error_data = response.json()
        raise EduschedAPIError(
            message=error_data.get('message', '未知错误'),
            status_code=response.status_code,
            details=error_data
        )

    except json.JSONDecodeError:
        raise EduschedAPIError(
            message="响应格式错误",
            status_code=response.status_code
        )

def safe_api_call(func, *args, **kwargs):
    """安全的API调用包装器"""
    try:
        return func(*args, **kwargs)
    except EduschedAPIError as e:
        print(f"API错误 [{e.status_code}]: {e.message}")
        if e.details:
            print(f"详细信息: {e.details}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"网络请求异常: {e}")
        return None
    except Exception as e:
        print(f"未知异常: {e}")
        return None
```

### 2. 重试机制

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, EduschedAPIError) as e:
                    retries += 1
                    if retries == max_retries:
                        raise

                    wait_time = delay * (backoff ** (retries - 1))
                    print(f"请求失败，{wait_time}秒后重试 ({retries}/{max_retries})")
                    time.sleep(wait_time)

            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@retry_on_failure(max_retries=3, delay=1)
def create_school_with_retry(school_data):
    response = requests.post(
        f"{BASE_URL}/api/v1/schools/",
        headers=headers,
        json=school_data
    )
    return handle_api_response(response)
```

### 3. 错误日志记录

```python
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('edusched_api')

def log_api_error(error: EduschedAPIError, request_data: Dict = None):
    """记录API错误日志"""
    error_info = {
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__,
        'message': error.message,
        'status_code': error.status_code,
        'details': error.details,
        'request_data': request_data
    }

    logger.error(f"API错误: {error_info}")

    # 可以发送到监控系统
    # send_to_monitoring(error_info)

# 使用示例
try:
    response = requests.post(url, headers=headers, json=data)
    success, result = handle_api_response(response)
except EduschedAPIError as e:
    log_api_error(e, request_data=data)
    # 处理错误
```

### 4. 用户友好的错误提示

```python
def get_user_friendly_error(error: EduschedAPIError) -> str:
    """获取用户友好的错误信息"""
    error_messages = {
        400: "请求参数有误，请检查输入数据",
        401: "请先登录后再试",
        403: "您没有权限执行此操作",
        404: "请求的资源不存在",
        409: "当前状态下无法执行此操作",
        422: "数据格式不正确，请检查输入",
        429: "请求过于频繁，请稍后再试",
        500: "服务器内部错误，请稍后再试",
        502: "网关错误，请稍后再试",
        503: "服务暂时不可用，请稍后再试",
        504: "请求超时，请稍后再试"
    }

    return error_messages.get(error.status_code, "未知错误，请联系技术支持")

# 使用示例
try:
    # API 调用
    pass
except EduschedAPIError as e:
    user_message = get_user_friendly_error(e)
    print(f"错误: {user_message}")
```

## 错误恢复策略

### 1. 客户端恢复

```python
def handle_create_school_error(error: EduschedAPIError, school_data: Dict):
    """处理创建学校错误的恢复策略"""
    if error.status_code == 400 and "学校代码已存在" in error.message:
        # 生成新的代码
        original_code = school_data['code']
        school_data['code'] = f"{original_code}_{int(time.time())}"

        print(f"代码已存在，使用新代码: {school_data['code']}")
        return create_school(school_data)

    elif error.status_code == 422:
        # 验证数据格式
        try:
            validate_school_data(school_data)
        except ValueError as e:
            print(f"数据验证失败: {e}")
            return None

    return None
```

### 2. 调度任务恢复

```python
def recover_scheduling_job(job_id: str):
    """恢复失败的调度任务"""
    try:
        # 获取任务详情
        response = requests.get(
            f"{BASE_URL}/api/v1/scheduling/jobs/{job_id}",
            headers=headers
        )

        if response.status_code == 200:
            job = response.json()

            if job['status'] == 'failed':
                print(f"任务失败原因: {job.get('error_message', '未知')}")

                # 分析失败原因
                if "约束冲突" in job.get('error_message', ''):
                    print("建议：检查约束条件设置")
                elif "超时" in job.get('error_message', ''):
                    print("建议：减少问题规模或增加超时时间")

                # 询问是否重试
                retry = input("是否重试任务？(y/n): ")
                if retry.lower() == 'y':
                    return restart_scheduling_job(job['timetable_id'])

    except Exception as e:
        print(f"恢复任务失败: {e}")

    return None
```

## 监控和告警

### 1. 错误率监控

```python
class ErrorMonitor:
    """错误监控器"""

    def __init__(self):
        self.error_counts = {}
        self.total_requests = 0

    def record_error(self, error: EduschedAPIError):
        """记录错误"""
        self.total_requests += 1

        error_key = f"{error.status_code}_{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

    def get_error_rate(self) -> float:
        """获取错误率"""
        if self.total_requests == 0:
            return 0.0
        total_errors = sum(self.error_counts.values())
        return total_errors / self.total_requests

    def check_alerts(self):
        """检查告警条件"""
        error_rate = self.get_error_rate()

        if error_rate > 0.1:  # 10%错误率
            print(f"⚠️ 错误率过高: {error_rate:.2%}")

        # 检查特定错误
        for error_key, count in self.error_counts.items():
            if count > 10:  # 单个错误类型超过10次
                print(f"⚠️ 错误 {error_key} 频繁发生: {count} 次")

# 使用示例
error_monitor = ErrorMonitor()
```

### 2. 性能监控

```python
import time
from contextlib import contextmanager

@contextmanager
def monitor_performance(operation_name: str):
    """性能监控上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        if duration > 5.0:  # 超过5秒
            print(f"⚠️ 操作 {operation_name} 耗时过长: {duration:.2f}秒")

# 使用示例
with monitor_performance("create_school"):
    response = requests.post(url, headers=headers, json=data)
```

## 测试错误处理

### 1. 单元测试

```python
import pytest
from unittest.mock import Mock, patch

def test_create_school_duplicate_error():
    """测试重复学校代码错误"""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": "DuplicateError",
        "message": "学校代码已存在",
        "status_code": 400
    }

    with patch('requests.post', return_value=mock_response):
        with pytest.raises(EduschedAPIError) as exc_info:
            create_school({"code": "TEST", "name": "Test School"})

        assert exc_info.value.status_code == 400
        assert "已存在" in exc_info.value.message
```

### 2. 集成测试

```python
def test_error_handling_workflow():
    """测试错误处理工作流"""
    # 测试不存在的资源
    fake_id = "550e8400-e29b-41d4-a716-446655440000"

    with pytest.raises(EduschedAPIError) as exc_info:
        get_school(fake_id)

    assert exc_info.value.status_code == 404

    # 测试数据验证
    with pytest.raises(EduschedAPIError) as exc_info:
        create_school({"name": "Test"})  # 缺少必需字段

    assert exc_info.value.status_code == 422
```

## 最佳实践总结

1. **统一错误处理**: 使用统一的错误处理机制和格式
2. **详细日志**: 记录足够的错误信息用于调试
3. **用户友好**: 提供用户友好的错误提示
4. **重试机制**: 对临时性错误实现自动重试
5. **监控告警**: 监控错误率和性能指标
6. **恢复策略**: 为常见错误提供恢复方案
7. **测试覆盖**: 充分测试各种错误场景
8. **文档完善**: 为错误代码提供详细文档