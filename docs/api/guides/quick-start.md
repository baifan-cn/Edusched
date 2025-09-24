# API 快速入门指南

## 概述

本指南将帮助您快速开始使用 Edusched API 进行教育调度系统的开发和集成。

## 前置条件

- Python 3.12+ 或其他编程语言环境
- 能够发送 HTTP 请求的工具（curl、Postman、requests 等）
- 访问 Edusched API 服务的权限
- 基本的 REST API 概念了解

## 第一步：环境准备

### 1.1 安装依赖

#### Python 环境

```bash
# 安装 requests 库
pip install requests

# 或者使用 pipenv
pip install pipenv
pipenv install requests
```

#### JavaScript 环境

```bash
# 使用 npm
npm install axios

# 或者使用 yarn
yarn add axios
```

### 1.2 配置信息

准备好以下信息：

- **API 基础 URL**: `http://localhost:8000`
- **租户 ID**: 您的学校或组织标识符
- **认证方式**: 目前使用 `X-Tenant-ID` 头部进行认证

## 第二步：基本请求

### 2.1 健康检查

首先验证 API 服务是否正常运行：

#### Python 示例

```python
import requests

# 配置
BASE_URL = "http://localhost:8000"
TENANT_ID = "your-tenant-id"

# 健康检查
response = requests.get(f"{BASE_URL}/health")

if response.status_code == 200:
    health_data = response.json()
    print(f"系统状态: {health_data['status']}")
else:
    print(f"服务不可用: {response.status_code}")
```

#### curl 示例

```bash
curl -X GET "http://localhost:8000/health"
```

### 2.2 设置请求头

所有 API 请求都需要包含租户 ID：

#### Python 示例

```python
HEADERS = {
    "X-Tenant-ID": TENANT_ID,
    "Content-Type": "application/json"
}
```

#### curl 示例

```bash
curl -X GET "http://localhost:8000/api/v1/schools/" \
  -H "X-Tenant-ID: your-tenant-id"
```

## 第三步：核心操作

### 3.1 创建学校

```python
# 创建学校数据
school_data = {
    "name": "示范学校",
    "code": "DEMO001",
    "address": "北京市海淀区",
    "academic_year": "2024-2025",
    "semester": "秋季学期"
}

# 发送请求
response = requests.post(
    f"{BASE_URL}/api/v1/schools/",
    headers=HEADERS,
    json=school_data
)

if response.status_code == 201:
    school = response.json()
    print(f"学校创建成功: {school['name']} (ID: {school['id']})")
    school_id = school['id']
else:
    print(f"创建失败: {response.status_code}")
    print(response.text)
```

### 3.2 创建教师

```python
# 创建教师数据
teacher_data = {
    "employee_id": "T001",
    "name": "张老师",
    "email": "zhang.teacher@demo.edu.cn",
    "department": "数学系",
    "title": "教授",
    "specialization": "高等数学",
    "max_hours_per_week": 20,
    "preferred_days": ["monday", "wednesday", "friday"],
    "preferred_time_slots": ["morning", "afternoon"]
}

# 发送请求
response = requests.post(
    f"{BASE_URL}/api/v1/teachers/",
    headers=HEADERS,
    json=teacher_data
)

if response.status_code == 201:
    teacher = response.json()
    print(f"教师创建成功: {teacher['name']} (ID: {teacher['id']})")
    teacher_id = teacher['id']
else:
    print(f"创建失败: {response.status_code}")
    print(response.text)
```

### 3.3 创建课程

```python
# 创建课程数据
course_data = {
    "code": "MATH101",
    "name": "高等数学",
    "description": "大学一年级高等数学课程",
    "credits": 4,
    "hours_per_week": 4,
    "total_hours": 64,
    "is_required": True,
    "max_students": 120,
    "min_students": 30,
    "requires_lab": False
}

# 发送请求
response = requests.post(
    f"{BASE_URL}/api/v1/courses/",
    headers=HEADERS,
    json=course_data
)

if response.status_code == 201:
    course = response.json()
    print(f"课程创建成功: {course['name']} (ID: {course['id']})")
    course_id = course['id']
else:
    print(f"创建失败: {response.status_code}")
    print(response.text)
```

### 3.4 创建时间表

```python
# 创建时间表数据
timetable_data = {
    "name": "2024年秋季学期课程表",
    "description": "2024年秋季学期全校课程安排",
    "academic_year": "2024-2025",
    "semester": "秋季学期",
    "calendar_id": "550e8400-e29b-41d4-a716-446655440001",  # 需要实际的日历ID
    "school_id": school_id,  # 使用前面创建的学校ID
    "total_sections": 100
}

# 发送请求
response = requests.post(
    f"{BASE_URL}/api/v1/timetables/",
    headers=HEADERS,
    json=timetable_data
)

if response.status_code == 201:
    timetable = response.json()
    print(f"时间表创建成功: {timetable['name']} (ID: {timetable['id']})")
    timetable_id = timetable['id']
else:
    print(f"创建失败: {response.status_code}")
    print(response.text)
```

## 第四步：启动调度

### 4.1 启动调度任务

```python
# 启动调度
response = requests.post(
    f"{BASE_URL}/api/v1/scheduling/start",
    headers=HEADERS,
    json={"timetable_id": timetable_id}
)

if response.status_code == 200:
    job_data = response.json()
    print(f"调度任务启动成功: {job_data['job_id']}")
    job_id = job_data['job_id']
else:
    print(f"启动失败: {response.status_code}")
    print(response.text)
```

### 4.2 监控调度进度

```python
import time

def monitor_job(job_id):
    """监控调度任务进度"""
    while True:
        response = requests.get(
            f"{BASE_URL}/api/v1/scheduling/jobs/{job_id}/progress",
            headers=HEADERS
        )

        if response.status_code == 200:
            progress = response.json()
            status = progress['status']
            progress_pct = progress['progress'] * 100

            print(f"任务状态: {status}, 进度: {progress_pct:.1f}%")

            if status in ['completed', 'failed']:
                if status == 'completed':
                    print("🎉 调度完成!")
                else:
                    print(f"❌ 调度失败: {progress.get('error_message', '未知错误')}")
                break
        else:
            print(f"获取进度失败: {response.status_code}")
            break

        time.sleep(5)  # 每5秒检查一次

# 开始监控
monitor_job(job_id)
```

## 第五步：查询结果

### 5.1 获取调度结果

```python
# 获取任务详情
response = requests.get(
    f"{BASE_URL}/api/v1/scheduling/jobs/{job_id}",
    headers=HEADERS
)

if response.status_code == 200:
    job = response.json()
    print(f"任务详情:")
    print(f"  状态: {job['status']}")
    print(f"  进度: {job['progress']:.1%}")
    print(f"  开始时间: {job['started_at']}")
    print(f"  完成时间: {job['completed_at']}")

    if job['metrics']:
        metrics = job['metrics']
        print(f"  优化得分: {metrics.get('optimization_score', 0):.2f}")
        print(f"  已安排教学段: {metrics.get('scheduled_sections', 0)}/{metrics.get('total_sections', 0)}")
```

### 5.2 获取时间表分配

```python
# 获取时间表分配（当前版本为待实现）
response = requests.get(
    f"{BASE_URL}/api/v1/timetables/{timetable_id}/assignments",
    headers=HEADERS
)

print("时间表分配信息:")
print(response.json())
```

## 完整示例

### complete_workflow.py

```python
#!/usr/bin/env python3
"""
完整的API工作流示例
"""

import requests
import time
import json

class EduschedAPI:
    """Edusched API 客户端"""

    def __init__(self, base_url, tenant_id):
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.headers = {
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }

    def health_check(self):
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def create_school(self, data):
        """创建学校"""
        response = requests.post(
            f"{self.base_url}/api/v1/schools/",
            headers=self.headers,
            json=data
        )
        return response.json()

    def create_teacher(self, data):
        """创建教师"""
        response = requests.post(
            f"{self.base_url}/api/v1/teachers/",
            headers=self.headers,
            json=data
        )
        return response.json()

    def create_course(self, data):
        """创建课程"""
        response = requests.post(
            f"{self.base_url}/api/v1/courses/",
            headers=self.headers,
            json=data
        )
        return response.json()

    def create_timetable(self, data):
        """创建时间表"""
        response = requests.post(
            f"{self.base_url}/api/v1/timetables/",
            headers=self.headers,
            json=data
        )
        return response.json()

    def start_scheduling(self, timetable_id):
        """启动调度"""
        response = requests.post(
            f"{self.base_url}/api/v1/scheduling/start",
            headers=self.headers,
            json={"timetable_id": timetable_id}
        )
        return response.json()

    def get_job_progress(self, job_id):
        """获取任务进度"""
        response = requests.get(
            f"{self.base_url}/api/v1/scheduling/jobs/{job_id}/progress",
            headers=self.headers
        )
        return response.json()

def main():
    """主函数"""
    # 初始化 API 客户端
    api = EduschedAPI(
        base_url="http://localhost:8000",
        tenant_id="demo-school"
    )

    print("🚀 Edusched API 完整工作流示例")
    print("=" * 50)

    # 1. 健康检查
    print("1. 健康检查...")
    health = api.health_check()
    print(f"   系统状态: {health['status']}")

    # 2. 创建学校
    print("\n2. 创建学校...")
    school = api.create_school({
        "name": "API测试学校",
        "code": "API001",
        "address": "北京市海淀区",
        "academic_year": "2024-2025",
        "semester": "秋季学期"
    })
    print(f"   学校创建成功: {school['name']}")

    # 3. 创建教师
    print("\n3. 创建教师...")
    teacher = api.create_teacher({
        "employee_id": "API001",
        "name": "API测试老师",
        "email": "api.teacher@demo.edu.cn",
        "department": "计算机系",
        "title": "讲师",
        "max_hours_per_week": 16
    })
    print(f"   教师创建成功: {teacher['name']}")

    # 4. 创建课程
    print("\n4. 创建课程...")
    course = api.create_course({
        "code": "API101",
        "name": "API编程基础",
        "credits": 3,
        "hours_per_week": 3,
        "total_hours": 48,
        "max_students": 60,
        "requires_lab": True
    })
    print(f"   课程创建成功: {course['name']}")

    # 5. 创建时间表
    print("\n5. 创建时间表...")
    timetable = api.create_timetable({
        "name": "API测试课程表",
        "description": "API测试用课程表",
        "academic_year": "2024-2025",
        "semester": "秋季学期",
        "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
        "school_id": school['id'],
        "total_sections": 10
    })
    print(f"   时间表创建成功: {timetable['name']}")

    # 6. 启动调度
    print("\n6. 启动调度...")
    job = api.start_scheduling(timetable['id'])
    print(f"   调度任务启动: {job['job_id']}")

    # 7. 监控进度
    print("\n7. 监控调度进度...")
    job_id = job['job_id']
    while True:
        progress = api.get_job_progress(job_id)
        status = progress['status']
        progress_pct = progress['progress'] * 100

        print(f"   进度: {progress_pct:.1f}% ({status})")

        if status in ['completed', 'failed']:
            break

        time.sleep(2)

    print("\n🎉 工作流完成!")

if __name__ == "__main__":
    main()
```

## 常见问题

### Q1: 如何处理错误？

API 返回标准的 HTTP 状态码和错误信息：

```python
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # 检查 HTTP 错误
    result = response.json()

except requests.exceptions.HTTPError as e:
    print(f"HTTP 错误: {e.response.status_code}")
    print(f"错误信息: {e.response.text}")

except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")

except json.JSONDecodeError as e:
    print(f"JSON 解析错误: {e}")
```

### Q2: 如何处理分页？

列表接口支持分页参数：

```python
# 获取分页数据
params = {
    "skip": 0,
    "limit": 20,
    "sort": "name:asc"
}

response = requests.get(
    f"{BASE_URL}/api/v1/schools/",
    headers=HEADERS,
    params=params
)
```

### Q3: 如何优化调度性能？

- 合理设置约束条件
- 避免过度优化
- 使用合适的超时时间
- 监控系统资源使用

## 下一步

- 阅读详细的 API 文档
- 了解各个模块的高级功能
- 集成到您的应用中
- 参与社区讨论和贡献

## 资源链接

- [完整 API 文档](../README.md)
- [错误处理指南](error-handling.md)
- [最佳实践](best-practices.md)
- [示例代码](../examples/)