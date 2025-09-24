# API 使用最佳实践

## 概述

本文档提供了使用 Edusched API 的最佳实践建议，帮助开发者构建高质量、高性能的应用程序。

## 1. 认证和安全

### 1.1 租户管理

```python
# 推荐：使用环境变量管理租户ID
import os
from typing import Optional

class EduschedClient:
    def __init__(self, base_url: str, tenant_id: Optional[str] = None):
        self.base_url = base_url
        self.tenant_id = tenant_id or os.getenv('EDUSCHED_TENANT_ID')

        if not self.tenant_id:
            raise ValueError("必须提供租户ID")

        self.headers = {
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }

# 使用示例
client = EduschedClient(
    base_url="http://localhost:8000",
    tenant_id=os.getenv('EDUSCHED_TENANT_ID')
)
```

### 1.2 安全配置

```python
# 推荐：在生产环境中使用HTTPS
import ssl

def create_secure_session():
    """创建安全的HTTP会话"""
    session = requests.Session()

    # 强制HTTPS
    session.verify = True
    # 设置合理的超时
    session.timeout = 30

    return session

# 避免硬编码敏感信息
CONFIG = {
    "base_url": os.getenv('EDUSCHED_API_URL', 'https://api.edusched.com'),
    "tenant_id": os.getenv('EDUSCHED_TENANT_ID'),
    "timeout": int(os.getenv('EDUSCHED_TIMEOUT', '30'))
}
```

## 2. 错误处理

### 2.1 统一错误处理

```python
import requests
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class EduschedAPIException(Exception):
    """自定义API异常"""

    def __init__(self, message: str, status_code: int, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

def handle_api_response(response: requests.Response) -> Any:
    """统一处理API响应"""
    try:
        if response.status_code == 200:
            return response.json()

        error_data = response.json()
        raise EduschedAPIException(
            message=error_data.get('message', 'Unknown error'),
            status_code=response.status_code,
            details=error_data
        )

    except requests.exceptions.JSONDecodeError:
        raise EduschedAPIException(
            message='Invalid response format',
            status_code=response.status_code
        )

def safe_api_call(func, *args, **kwargs):
    """安全的API调用包装器"""
    try:
        return func(*args, **kwargs)
    except EduschedAPIException as e:
        logger.error(f"API error [{e.status_code}]: {e.message}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

### 2.2 重试机制

```python
import time
from functools import wraps
from typing import Callable

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    retryable_errors: tuple = (requests.exceptions.RequestException,)
):
    """重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_error = None

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except retryable_errors as e:
                    last_error = e
                    retries += 1

                    if retries == max_retries:
                        break

                    wait_time = delay * (backoff ** (retries - 1))
                    logger.warning(f"Retry {retries}/{max_retries} after {wait_time}s: {e}")
                    time.sleep(wait_time)
                except Exception as e:
                    # 不重试非预期异常
                    raise

            raise last_error if last_error else Exception("Max retries exceeded")

        return wrapper
    return decorator

# 使用示例
@retry_on_failure(max_retries=3, delay=1, backoff=2)
def create_school_with_retry(data: Dict):
    response = requests.post(
        f"{CONFIG['base_url']}/api/v1/schools/",
        headers=client.headers,
        json=data,
        timeout=CONFIG['timeout']
    )
    return handle_api_response(response)
```

## 3. 性能优化

### 3.1 连接池管理

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_optimized_session():
    """创建优化的HTTP会话"""
    session = requests.Session()

    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
    )

    # 配置适配器
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

# 全局会话
session = create_optimized_session()
```

### 3.2 批量操作

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

def create_schools_batch(schools_data: List[Dict], max_workers: int = 5) -> List[Dict]:
    """批量创建学校"""
    results = []
    failed_items = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_data = {
            executor.submit(create_single_school, data): data
            for data in schools_data
        }

        # 收集结果
        for future in as_completed(future_to_data):
            original_data = future_to_data[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to create school: {e}")
                failed_items.append({
                    'data': original_data,
                    'error': str(e)
                })

    logger.info(f"Created {len(results)} schools, {len(failed_items)} failed")
    return results, failed_items

def create_single_school(school_data: Dict) -> Dict:
    """创建单个学校"""
    response = session.post(
        f"{CONFIG['base_url']}/api/v1/schools/",
        headers=client.headers,
        json=school_data,
        timeout=CONFIG['timeout']
    )
    return handle_api_response(response)
```

### 3.3 缓存策略

```python
import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Optional

class SimpleCache:
    """简单的文件缓存"""

    def __init__(self, cache_dir: str = "cache", ttl: int = 3600):
        self.cache_dir = cache_dir
        self.ttl = ttl
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_key}.json")

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        cache_path = self._get_cache_path(key)

        if not os.path.exists(cache_path):
            return None

        # 检查是否过期
        mtime = os.path.getmtime(cache_path)
        if datetime.now().timestamp() - mtime > self.ttl:
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, key: str, value: Any):
        """设置缓存数据"""
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")

# 使用示例
cache = SimpleCache()

def get_schools_with_cache() -> List[Dict]:
    """带缓存获取学校列表"""
    cache_key = f"schools_{client.tenant_id}"

    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info("Returning cached schools data")
        return cached_data

    # 从API获取
    response = session.get(
        f"{CONFIG['base_url']}/api/v1/schools/",
        headers=client.headers,
        timeout=CONFIG['timeout']
    )
    schools = handle_api_response(response)

    # 缓存结果
    cache.set(cache_key, schools)

    return schools
```

## 4. 数据验证

### 4.1 输入验证

```python
from typing import Dict, List, Optional
import re
from pydantic import BaseModel, Field, validator

class SchoolModel(BaseModel):
    """学校数据模型"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    address: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    academic_year: str = Field(..., regex=r'^\d{4}-\d{4}$')
    semester: str = Field(..., regex=r'^(春季|秋季|夏季|冬季)学期$')

    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^[\d\s\-\+\(\)]+$', v):
            raise ValueError('Invalid phone format')
        return v

class TeacherModel(BaseModel):
    """教师数据模型"""
    employee_id: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=50)
    max_hours_per_week: int = Field(..., ge=1, le=40)

    @validator('max_hours_per_week')
    def validate_hours(cls, v):
        if v > 40:
            raise ValueError('Max hours per week cannot exceed 40')
        return v

def validate_and_create_school(data: Dict) -> Dict:
    """验证并创建学校"""
    try:
        validated_data = SchoolModel(**data)
        return create_school(validated_data.dict())
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise ValueError(f"数据验证失败: {e}")
```

### 4.2 响应验证

```python
from typing import TypeVar, Type, get_type_hints

T = TypeVar('T')

def validate_response(response_data: Dict, model_class: Type[T]) -> T:
    """验证API响应数据"""
    try:
        return model_class(**response_data)
    except Exception as e:
        logger.error(f"Response validation failed: {e}")
        raise ValueError(f"响应数据格式错误: {e}")

# 使用示例
def get_and_validate_school(school_id: str) -> SchoolModel:
    """获取并验证学校数据"""
    response = session.get(
        f"{CONFIG['base_url']}/api/v1/schools/{school_id}",
        headers=client.headers,
        timeout=CONFIG['timeout']
    )
    data = handle_api_response(response)
    return validate_response(data, SchoolModel)
```

## 5. 监控和日志

### 5.1 请求监控

```python
import time
from contextlib import contextmanager
from typing import Dict, Any

class APIMonitor:
    """API监控器"""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_time = 0.0
        self.endpoints = {}

    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """记录请求统计"""
        self.request_count += 1
        self.total_time += duration

        if status_code >= 400:
            self.error_count += 1

        key = f"{method} {endpoint}"
        if key not in self.endpoints:
            self.endpoints[key] = {
                'count': 0,
                'errors': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }

        stats = self.endpoints[key]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']

        if status_code >= 400:
            stats['errors'] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_requests': self.request_count,
            'error_rate': self.error_count / max(self.request_count, 1),
            'avg_response_time': self.total_time / max(self.request_count, 1),
            'endpoints': self.endpoints
        }

# 全局监控器
monitor = APIMonitor()

@contextmanager
def monitor_request(endpoint: str, method: str = 'GET'):
    """请求监控上下文管理器"""
    start_time = time.time()
    status_code = 200

    try:
        yield
    except Exception as e:
        if hasattr(e, 'status_code'):
            status_code = e.status_code
        else:
            status_code = 500
        raise
    finally:
        duration = time.time() - start_time
        monitor.record_request(endpoint, method, status_code, duration)
```

### 5.2 结构化日志

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_request(self, method: str, url: str, status_code: int, duration: float, **kwargs):
        """记录请求日志"""
        log_data = {
            'type': 'api_request',
            'method': method,
            'url': url,
            'status_code': status_code,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))

    def log_error(self, error: Exception, context: Dict = None):
        """记录错误日志"""
        log_data = {
            'type': 'api_error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        self.logger.error(json.dumps(log_data, ensure_ascii=False))

# 使用示例
logger = StructuredLogger('edusched_client')
```

## 6. 配置管理

### 6.1 环境配置

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class EduschedConfig:
    """Edusched配置类"""
    base_url: str
    tenant_id: str
    timeout: int = 30
    max_retries: int = 3
    cache_ttl: int = 3600
    log_level: str = 'INFO'

    @classmethod
    def from_env(cls) -> 'EduschedConfig':
        """从环境变量创建配置"""
        return cls(
            base_url=os.getenv('EDUSCHED_API_URL', 'http://localhost:8000'),
            tenant_id=os.getenv('EDUSCHED_TENANT_ID'),
            timeout=int(os.getenv('EDUSCHED_TIMEOUT', '30')),
            max_retries=int(os.getenv('EDUSCHED_MAX_RETRIES', '3')),
            cache_ttl=int(os.getenv('EDUSCHED_CACHE_TTL', '3600')),
            log_level=os.getenv('EDUSCHED_LOG_LEVEL', 'INFO')
        )

# 使用示例
config = EduschedConfig.from_env()
```

### 6.2 客户端工厂

```python
class EduschedClientFactory:
    """Edusched客户端工厂"""

    @staticmethod
    def create_client(config: EduschedConfig) -> 'EduschedClient':
        """创建配置好的客户端"""
        session = create_optimized_session()
        cache = SimpleCache(ttl=config.cache_ttl)

        return EduschedClient(
            base_url=config.base_url,
            tenant_id=config.tenant_id,
            session=session,
            cache=cache,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

# 使用示例
config = EduschedConfig.from_env()
client = EduschedClientFactory.create_client(config)
```

## 7. 完整示例

### 7.1 高级客户端实现

```python
class AdvancedEduschedClient:
    """高级Edusched客户端"""

    def __init__(self, config: EduschedConfig):
        self.config = config
        self.session = create_optimized_session()
        self.cache = SimpleCache(ttl=config.cache_ttl)
        self.monitor = APIMonitor()
        self.logger = StructuredLogger('edusched_client')

        self.headers = {
            "X-Tenant-ID": config.tenant_id,
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """发送请求并处理响应"""
        url = f"{self.config.base_url}/api/v1{endpoint}"

        # 添加默认参数
        kwargs.setdefault('timeout', self.config.timeout)
        kwargs.setdefault('headers', self.headers)

        start_time = time.time()

        try:
            with monitor_request(endpoint, method):
                response = self.session.request(method, url, **kwargs)
                return handle_api_response(response)

        except Exception as e:
            self.logger.log_error(e, {
                'method': method,
                'endpoint': endpoint,
                'kwargs': kwargs
            })
            raise

    def create_school(self, data: Dict) -> Dict:
        """创建学校"""
        validated_data = SchoolModel(**data).dict()
        return self._make_request('POST', '/schools/', json=validated_data)

    def get_schools(self, use_cache: bool = True) -> List[Dict]:
        """获取学校列表"""
        if use_cache:
            cache_key = f"schools_{self.config.tenant_id}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

        schools = self._make_request('GET', '/schools/')

        if use_cache:
            self.cache.set(cache_key, schools)

        return schools

    def create_teacher_batch(self, teachers_data: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """批量创建教师"""
        return create_schools_batch(teachers_data, max_workers=3)

    def get_stats(self) -> Dict:
        """获取客户端统计信息"""
        return self.monitor.get_stats()
```

### 7.2 使用示例

```python
# 初始化
config = EduschedConfig.from_env()
client = AdvancedEduschedClient(config)

# 创建学校
school_data = {
    "name": "示例学校",
    "code": "EXAMPLE001",
    "address": "北京市海淀区",
    "academic_year": "2024-2025",
    "semester": "秋季学期"
}

try:
    school = client.create_school(school_data)
    print(f"学校创建成功: {school['name']}")

    # 获取学校列表
    schools = client.get_schools()
    print(f"共 {len(schools)} 所学校")

    # 批量创建教师
    teachers_data = [
        {
            "employee_id": "T001",
            "name": "张老师",
            "department": "数学系",
            "max_hours_per_week": 20
        },
        {
            "employee_id": "T002",
            "name": "李老师",
            "department": "物理系",
            "max_hours_per_week": 18
        }
    ]

    created_teachers, failed_teachers = client.create_teacher_batch(teachers_data)
    print(f"成功创建 {len(created_teachers)} 位教师")
    if failed_teachers:
        print(f"失败 {len(failed_teachers)} 位教师")

    # 获取统计信息
    stats = client.get_stats()
    print(f"API统计: {stats}")

except Exception as e:
    print(f"操作失败: {e}")
```

## 8. 部署建议

### 8.1 容器化部署

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY . .

# 设置环境变量
ENV EDUSCHED_API_URL=https://api.edusched.com
ENV EDUSCHED_TENANT_ID=your-tenant-id
ENV EDUSCHED_LOG_LEVEL=INFO

# 运行应用
CMD ["python", "your_app.py"]
```

### 8.2 Kubernetes 配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edusched-client
spec:
  replicas: 3
  selector:
    matchLabels:
      app: edusched-client
  template:
    metadata:
      labels:
        app: edusched-client
    spec:
      containers:
      - name: client
        image: edusched-client:latest
        env:
        - name: EDUSCHED_API_URL
          value: "https://api.edusched.com"
        - name: EDUSCHED_TENANT_ID
          valueFrom:
            secretKeyRef:
              name: edusched-secrets
              key: tenant-id
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 总结

遵循这些最佳实践可以帮助您：

1. **提高代码质量**: 使用类型提示、数据验证和错误处理
2. **增强性能**: 使用连接池、缓存和批量操作
3. **改善可维护性**: 使用配置管理和结构化日志
4. **提升可靠性**: 实现重试机制和监控
5. **便于部署**: 使用容器化和环境配置

记住根据您的具体需求调整这些建议，并在实践中持续优化您的实现。