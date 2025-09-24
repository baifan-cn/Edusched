# 调度引擎 API

## 概述

调度引擎 API 提供 Edusched 系统的核心智能调度功能，包括启动调度任务、监控进度、管理约束等。系统使用 Google OR-Tools CP-SAT 求解器实现高效的课程表优化算法。

### 基础信息

- **路径**: `/api/v1/scheduling`
- **方法**: GET, POST
- **认证**: 需要租户 ID (`X-Tenant-ID`)
- **异步处理**: 调度任务在后台执行

## 核心特性

- 🎯 **智能优化**: 使用 OR-Tools CP-SAT 求解器
- 📊 **实时监控**: 支持进度查询和状态跟踪
- 🔄 **异步处理**: 后台执行，不阻塞 API 响应
- ⚡ **并发控制**: 支持多个调度任务并发执行
- 🎛️ **任务管理**: 支持启动、取消、查询等操作

## 数据模型

### SchedulingJob

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "timetable_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "running",
  "progress": 0.45,
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": null,
  "error_message": null,
  "worker_id": "worker-1",
  "metrics": {
    "total_sections": 120,
    "scheduled_sections": 54,
    "constraint_violations": 0,
    "optimization_score": 0.85
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:15:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | UUID | 调度任务唯一标识符 |
| `tenant_id` | string | 租户标识符 |
| `timetable_id` | UUID | 时间表 ID |
| `status` | string | 任务状态 |
| `progress` | float | 进度百分比 (0.0-1.0) |
| `started_at` | datetime | 开始时间 |
| `completed_at` | datetime | 完成时间 |
| `error_message` | string | 错误信息 |
| `worker_id` | string | 工作进程 ID |
| `metrics` | object | 调度指标 |

### SchedulingStatus 枚举

- `draft` - 草稿
- `running` - 运行中
- `feasible` - 可行解
- `optimized` - 已优化
- `published` - 已发布
- `failed` - 失败

## API 端点

### 启动调度任务

**POST** `/api/v1/scheduling/start`

为指定时间表启动新的调度任务。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `timetable_id` | UUID | 是 | 时间表 ID |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/scheduling/start" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "timetable_id": "550e8400-e29b-41d4-a716-446655440001"
  }'
```

#### 响应示例

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "started",
  "message": "调度任务已启动",
  "timetable_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 获取调度任务列表

**GET** `/api/v1/scheduling/jobs`

获取当前租户下的所有调度任务列表，支持分页和状态过滤。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `skip` | integer | 否 | 跳过的记录数，默认 0 |
| `limit` | integer | 否 | 返回的记录数，默认 100，最大 1000 |
| `status_filter` | string | 否 | 状态过滤 |

#### 请求示例

```bash
# 获取所有任务
curl -X GET "http://localhost:8000/api/v1/scheduling/jobs" \
  -H "X-Tenant-ID: demo-school"

# 获取运行中的任务
curl -X GET "http://localhost:8000/api/v1/scheduling/jobs?status_filter=running" \
  -H "X-Tenant-ID: demo-school"

# 分页获取
curl -X GET "http://localhost:8000/api/v1/scheduling/jobs?skip=0&limit=20" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "tenant_id": "demo-school",
    "timetable_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "running",
    "progress": 0.45,
    "started_at": "2024-01-01T10:00:00Z",
    "completed_at": null,
    "error_message": null,
    "worker_id": "worker-1",
    "metrics": {
      "total_sections": 120,
      "scheduled_sections": 54,
      "constraint_violations": 0,
      "optimization_score": 0.85
    },
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:15:00Z",
    "created_by": "system",
    "updated_by": "system"
  }
]
```

### 获取调度任务详情

**GET** `/api/v1/scheduling/jobs/{job_id}`

获取指定调度任务的详细信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `job_id` | UUID | 是 | 调度任务 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/scheduling/jobs/550e8400-e29b-41d4-a716-446655440002" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "tenant_id": "demo-school",
  "timetable_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "running",
  "progress": 0.45,
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": null,
  "error_message": null,
  "worker_id": "worker-1",
  "metrics": {
    "total_sections": 120,
    "scheduled_sections": 54,
    "constraint_violations": 0,
    "optimization_score": 0.85
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:15:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 取消调度任务

**POST** `/api/v1/scheduling/jobs/{job_id}/cancel`

取消指定的调度任务。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `job_id` | UUID | 是 | 调度任务 ID |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/scheduling/jobs/550e8400-e29b-41d4-a716-446655440002/cancel" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "cancelled",
  "message": "调度任务已取消"
}
```

### 获取任务进度

**GET** `/api/v1/scheduling/jobs/{job_id}/progress`

获取调度任务的实时进度信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `job_id` | UUID | 是 | 调度任务 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/scheduling/jobs/550e8400-e29b-41d4-a716-446655440002/progress" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "running",
  "progress": 0.67,
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": null,
  "error_message": null,
  "worker_id": "worker-1"
}
```

### 验证约束

**POST** `/api/v1/scheduling/validate`

验证指定时间表的约束条件。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `timetable_id` | UUID | 是 | 时间表 ID |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/scheduling/validate" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "timetable_id": "550e8400-e29b-41d4-a716-446655440001"
  }'
```

#### 响应示例

```json
{
  "timetable_id": "550e8400-e29b-41d4-a716-446655440001",
  "valid": true,
  "violations": [],
  "message": "约束验证通过"
}
```

## 调度算法

### 约束类型

#### 硬约束 (Hard Constraints)
必须满足的约束条件，违反时调度失败：

1. **教师时间冲突**: 同一教师不能在同一时间教授多门课程
2. **教室占用冲突**: 同一教室不能在同一时间安排多门课程
3. **班级时间冲突**: 同一个班级不能在同一时间上多门课程
4. **教师课时限制**: 教师周课时不能超过最大限制
5. **教室容量**: 学生人数不能超过教室容量
6. **教师专业匹配**: 课程必须由专业对口的教师教授

#### 软约束 (Soft Constraints)
尽量满足的约束条件，影响优化质量：

1. **教师偏好**: 尽量安排在教师偏好的日期和时间段
2. **课程分布**: 同一课程尽量分散在一周的不同日期
3. **教室利用率**: 优先使用利用率高的教室
4. **连续课时**: 同一课程尽量安排连续的时间段
5. **跨校区时间**: 考虑教师在不同校区间的行程时间

### 优化目标

1. **可行性**: 首先确保所有硬约束得到满足
2. **质量**: 在可行解的基础上优化软约束
3. **效率**: 使用高效的算法快速找到优质解
4. **稳定性**: 小范围数据变化不应导致大幅度的排课调整

## 错误处理

### 常见错误

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 调度任务不存在 |
| 409 | Conflict | 任务状态不允许操作 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 调度引擎内部错误 |

### 错误响应示例

```json
{
  "error": "HTTP错误",
  "message": "调度任务不存在",
  "status_code": 404,
  "path": "/api/v1/scheduling/jobs/550e8400-e29b-41d4-a716-446655440002"
}
```

## 使用示例

### Python 示例

```python
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TENANT_ID = "demo-school"
HEADERS = {
    "X-Tenant-ID": TENANT_ID,
    "Content-Type": "application/json"
}

def start_scheduling(timetable_id):
    """启动调度任务"""
    response = requests.post(
        f"{BASE_URL}/scheduling/start",
        headers=HEADERS,
        json={"timetable_id": timetable_id}
    )
    return response.json()

def get_job_progress(job_id):
    """获取任务进度"""
    response = requests.get(
        f"{BASE_URL}/scheduling/jobs/{job_id}/progress",
        headers=HEADERS
    )
    return response.json()

def wait_for_completion(job_id, timeout=300):
    """等待任务完成"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        progress = get_job_progress(job_id)

        if progress["status"] == "completed":
            print("调度完成!")
            return True
        elif progress["status"] == "failed":
            print(f"调度失败: {progress.get('error_message', '未知错误')}")
            return False
        else:
            print(f"调度进度: {progress['progress']:.1%}")
            time.sleep(5)

    print("调度超时")
    return False

# 示例用法
if __name__ == "__main__":
    timetable_id = "550e8400-e29b-41d4-a716-446655440001"

    try:
        # 启动调度任务
        result = start_scheduling(timetable_id)
        job_id = result["job_id"]
        print(f"调度任务已启动: {job_id}")

        # 等待完成
        wait_for_completion(job_id)

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
```

### JavaScript 示例

```javascript
// 配置
const BASE_URL = 'http://localhost:8000/api/v1';
const TENANT_ID = 'demo-school';
const HEADERS = {
    'X-Tenant-ID': TENANT_ID,
    'Content-Type': 'application/json'
};

async function startScheduling(timetableId) {
    const response = await fetch(`${BASE_URL}/scheduling/start`, {
        method: 'POST',
        headers: HEADERS,
        body: JSON.stringify({ timetable_id: timetableId })
    });
    return await response.json();
}

async function getJobProgress(jobId) {
    const response = await fetch(`${BASE_URL}/scheduling/jobs/${jobId}/progress`, {
        headers: HEADERS
    });
    return await response.json();
}

async function waitForCompletion(jobId, timeout = 300000) {
    const startTime = Date.now();

    return new Promise((resolve, reject) => {
        const checkProgress = async () => {
            try {
                const progress = await getJobProgress(jobId);

                if (progress.status === 'completed') {
                    console.log('调度完成!');
                    resolve(true);
                } else if (progress.status === 'failed') {
                    console.log(`调度失败: ${progress.error_message || '未知错误'}`);
                    resolve(false);
                } else {
                    console.log(`调度进度: ${(progress.progress * 100).toFixed(1)}%`);

                    if (Date.now() - startTime < timeout) {
                        setTimeout(checkProgress, 5000);
                    } else {
                        console.log('调度超时');
                        resolve(false);
                    }
                }
            } catch (error) {
                reject(error);
            }
        };

        checkProgress();
    });
}

// 示例用法
(async () => {
    const timetableId = '550e8400-e29b-41d4-a716-446655440001';

    try {
        // 启动调度任务
        const result = await startScheduling(timetableId);
        const jobId = result.job_id;
        console.log(`调度任务已启动: ${jobId}`);

        // 等待完成
        await waitForCompletion(jobId);

    } catch (error) {
        console.error('请求失败:', error);
    }
})();
```

## 性能优化

### 调度性能

- **小规模** (50个教学段以内): 通常在 1-5 秒内完成
- **中规模** (50-200个教学段): 通常在 5-30 秒内完成
- **大规模** (200个教学段以上): 可能需要 1-5 分钟或更长时间

### 优化建议

1. **数据预处理**: 确保输入数据质量，减少无效数据
2. **约束设置**: 合理设置软约束权重，避免过度优化
3. **并行处理**: 对于大规模问题，考虑分批处理
4. **缓存机制**: 重复调度相同数据时使用缓存
5. **监控指标**: 密切关注调度指标，及时发现问题

## 监控和调试

### 关键指标

- **进度百分比**: 实时显示调度进度
- **约束违反数**: 监控硬约束违反情况
- **优化得分**: 评估解的质量
- **处理时间**: 统计调度耗时

### 调试工具

1. **任务详情**: 查看任务的详细状态和指标
2. **约束验证**: 手动验证约束条件
3. **日志分析**: 查看调度过程的详细日志
4. **性能分析**: 分析算法性能瓶颈

## 注意事项

1. **资源消耗**: 调度过程会消耗较多 CPU 和内存资源
2. **并发限制**: 同时运行的调度任务数量有限制
3. **数据一致性**: 调度期间避免修改相关数据
4. **错误恢复**: 调度失败后需要分析原因并重试
5. **版本兼容**: 不同版本的调度引擎可能产生不同结果