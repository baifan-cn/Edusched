# Edusched API 文档 (中文版)

## 📋 目录

- [快速开始](#快速开始)
- [API 概览](#api-概览)
- [认证方式](#认证方式)
- [错误处理](#错误处理)
- [模块文档](#模块文档)
- [使用指南](#使用指南)
- [测试工具](#测试工具)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd Edusched

# 安装依赖
pip install requests
```

### 2. 基本请求

```python
import requests

# 配置
BASE_URL = "http://localhost:8000"
TENANT_ID = "your-tenant-id"
HEADERS = {
    "X-Tenant-ID": TENANT_ID,
    "Content-Type": "application/json"
}

# 健康检查
response = requests.get(f"{BASE_URL}/health")
print(f"系统状态: {response.json()['status']}")

# 获取学校列表
response = requests.get(f"{BASE_URL}/api/v1/schools/", headers=HEADERS)
schools = response.json()
print(f"共 {len(schools)} 所学校")
```

### 3. 交互式文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API 概览

Edusched API 提供智能教育调度平台的完整功能，包括：

### 核心模块

| 模块 | 路径 | 功能 |
|------|------|------|
| 🏫 学校管理 | `/api/v1/schools` | 学校和校区管理 |
| 👨‍🏫 教师管理 | `/api/v1/teachers` | 教师信息和偏好设置 |
| 📚 课程管理 | `/api/v1/courses` | 课程和学科管理 |
| 📅 时间表管理 | `/api/v1/timetables` | 课程表创建和管理 |
| 🤖 调度引擎 | `/api/v1/scheduling` | 智能调度算法 |
| 💚 健康检查 | `/api/v1/health` | 系统状态监控 |

### 技术特性

- **多租户架构**: 数据完全隔离
- **智能调度**: OR-Tools CP-SAT 求解器
- **实时监控**: 调度进度跟踪
- **异步处理**: 后台任务执行
- **RESTful设计**: 标准化接口

## 🔐 认证方式

当前版本使用多租户认证：

```python
# 设置租户ID
HEADERS = {
    "X-Tenant-ID": "your-tenant-id"
}
```

**注意**: 完整的用户认证系统正在开发中。

## ❌ 错误处理

API 使用标准 HTTP 状态码：

```python
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()

except requests.exceptions.HTTPError as e:
    print(f"HTTP错误 [{e.response.status_code}]: {e.response.text}")

except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")
```

### 常见状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

## 📚 模块文档

### 🏫 学校管理 API

[详细文档](modules/schools.md)

- 创建、查询、更新、删除学校
- 校区管理（开发中）
- 多租户数据隔离

### 👨‍🏫 教师管理 API

[详细文档](modules/teachers.md)

- 教师信息管理
- 部门和职称设置
- 教学偏好配置
- 工作量管理

### 📚 课程管理 API

[详细文档](modules/courses.md)

- 课程信息管理
- 学科分类
- 学分和课时设置
- 实验室需求

### 📅 时间表管理 API

[详细文档](modules/timetables.md)

- 时间表创建和管理
- 状态流转控制
- 版本管理
- 发布管理

### 🤖 调度引擎 API

[详细文档](modules/scheduling.md)

- 启动调度任务
- 进度监控
- 任务管理
- 约束验证

### 💚 健康检查 API

[详细文档](modules/health.md)

- 系统状态监控
- 组件健康检查
- 性能指标
- 故障诊断

## 📖 使用指南

### 快速入门指南

[快速入门](guides/quick-start.md)

- 环境准备
- 基本请求
- 完整工作流
- 代码示例

### 错误处理指南

[错误处理](guides/error-handling.md)

- 错误类型说明
- 错误恢复策略
- 重试机制
- 日志记录

### 最佳实践

[最佳实践](guides/best-practices.md)

- 认证和安全
- 性能优化
- 错误处理
- 监控和日志
- 配置管理

## 🧪 测试工具

### 自动化测试

我们提供了完整的测试脚本：

```bash
# 运行所有测试
python scripts/api-tests/run_all_tests.py

# 测试单个模块
python scripts/api-tests/test_schools.py
python scripts/api-tests/test_teachers.py
python scripts/api-tests/test_scheduling.py
```

### 测试示例

```python
# 学校管理测试
python scripts/api-tests/test_schools.py --url http://localhost:8000 --tenant demo-school

# 教师管理测试
python scripts/api-tests/test_teachers.py --url http://localhost:8000 --tenant demo-school

# 调度引擎测试
python scripts/api-tests/test_scheduling.py --url http://localhost:8000 --tenant demo-school
```

## 💡 最佳实践

### 1. 连接管理

```python
# 使用连接池
session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

### 2. 错误处理

```python
# 统一错误处理
def safe_api_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except EduschedAPIException as e:
        logger.error(f"API错误: {e}")
        return None
```

### 3. 性能优化

```python
# 使用缓存
cache = SimpleCache(ttl=3600)

def get_schools_cached():
    cache_key = f"schools_{TENANT_ID}"
    schools = cache.get(cache_key)
    if not schools:
        schools = get_schools_from_api()
        cache.set(cache_key, schools)
    return schools
```

### 4. 监控和日志

```python
# 结构化日志
logger.info(json.dumps({
    'type': 'api_request',
    'method': 'GET',
    'endpoint': '/schools/',
    'duration_ms': 150,
    'status_code': 200
}))
```

## ❓ 常见问题

### Q: 如何处理多租户？

**A**: 每个请求都需要包含 `X-Tenant-ID` 请求头：

```python
headers = {
    "X-Tenant-ID": "your-tenant-id",
    "Content-Type": "application/json"
}
```

### Q: 调度任务需要多长时间？

**A**: 取决于问题规模：

- **小规模** (50个教学段): 1-5秒
- **中规模** (50-200个教学段): 5-30秒
- **大规模** (200+个教学段): 1-5分钟

### Q: 如何监控调度进度？

**A**: 使用进度查询接口：

```python
def monitor_job(job_id):
    while True:
        progress = get_job_progress(job_id)
        print(f"进度: {progress['progress']:.1%}")

        if progress['status'] in ['completed', 'failed']:
            break

        time.sleep(5)
```

### Q: API 有速率限制吗？

**A**: 当前版本没有严格的速率限制，但建议：

- 避免过于频繁的请求
- 使用批量操作
- 实现合理的重试机制

### Q: 如何处理调度失败？

**A**: 调度失败时：

1. 检查错误信息了解失败原因
2. 验证输入数据的完整性
3. 检查约束条件设置
4. 考虑简化问题规模
5. 重新启动调度任务

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- **GitHub Issues**: 创建问题报告
- **邮件**: 开发团队邮箱
- **文档**: 查看详细文档
- **社区**: 参与讨论和贡献

## 📋 更新日志

### v1.0.0 (当前版本)
- ✅ 基础 CRUD API
- ✅ 多租户架构
- ✅ 智能调度引擎
- ✅ 实时进度监控
- ✅ 完整测试套件
- ✅ 详细文档

### 计划中的功能
- 🔄 用户认证和授权
- 🔄 批量操作 API
- 🔄 Webhook 支持
- 🔄 更多的调度算法选项
- 🔄 性能优化

---

**注意**: 本文档基于 Edusched v1.0.0 版本。如有更新，请查看最新版本的文档。