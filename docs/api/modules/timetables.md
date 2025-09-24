# 时间表管理 API

## 概述

时间表管理 API 提供了对课程表的创建、管理和发布功能。时间表是调度系统的核心输出，包含了课程、教师、教室、时间等资源的具体分配安排。

### 基础信息

- **路径**: `/api/v1/timetables`
- **方法**: GET, POST, PUT, DELETE
- **认证**: 需要租户 ID (`X-Tenant-ID`)
- **数据模型**: Timetable

## 数据模型

### Timetable

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "name": "2024年秋季学期课程表",
  "description": "2024年秋季学期全校课程安排",
  "academic_year": "2024-2025",
  "semester": "秋季学期",
  "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
  "school_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "draft",
  "version": 1,
  "total_sections": 120,
  "scheduled_sections": 0,
  "optimization_score": 0.0,
  "published_at": null,
  "published_by": null,
  "notes": "待调度",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 字段说明

| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `id` | UUID | 自动 | 时间表唯一标识符 |
| `tenant_id` | string | 自动 | 租户标识符 |
| `name` | string | 是 | 时间表名称 |
| `description` | string | 否 | 时间表描述 |
| `academic_year` | string | 是 | 学年，格式 "YYYY-YYYY" |
| `semester` | string | 是 | 学期 |
| `calendar_id` | UUID | 是 | 日历 ID |
| `school_id` | UUID | 是 | 学校 ID |
| `status` | string | 是 | 时间表状态 |
| `version` | integer | 是 | 版本号 |
| `total_sections` | integer | 是 | 总教学段数 |
| `scheduled_sections` | integer | 是 | 已安排教学段数 |
| `optimization_score` | float | 是 | 优化得分 |
| `published_at` | datetime | 否 | 发布时间 |
| `published_by` | string | 否 | 发布者 |
| `notes` | string | 否 | 备注 |
| `is_active` | boolean | 否 | 是否激活，默认 true |
| `created_at` | datetime | 自动 | 创建时间 |
| `updated_at` | datetime | 自动 | 更新时间 |
| `created_by` | string | 自动 | 创建者 |
| `updated_by` | string | 自动 | 更新者 |

### TimetableStatus 枚举

- `draft` - 草稿
- `scheduled` - 已安排
- `feasible` - 可行
- `optimized` - 已优化
- `published` - 已发布
- `archived` - 已归档

## API 端点

### 获取时间表列表

**GET** `/api/v1/timetables/`

获取当前租户下的所有时间表列表，支持分页、日历和状态过滤。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `skip` | integer | 否 | 跳过的记录数，默认 0 |
| `limit` | integer | 否 | 返回的记录数，默认 100，最大 1000 |
| `calendar_id` | UUID | 否 | 日历 ID 过滤 |
| `status_filter` | string | 否 | 状态过滤 |

#### 请求示例

```bash
# 获取所有时间表
curl -X GET "http://localhost:8000/api/v1/timetables/" \
  -H "X-Tenant-ID: demo-school"

# 获取指定日历的时间表
curl -X GET "http://localhost:8000/api/v1/timetables/?calendar_id=550e8400-e29b-41d4-a716-446655440001" \
  -H "X-Tenant-ID: demo-school"

# 获取已发布的时间表
curl -X GET "http://localhost:8000/api/v1/timetables/?status_filter=published" \
  -H "X-Tenant-ID: demo-school"

# 分页获取
curl -X GET "http://localhost:8000/api/v1/timetables/?skip=0&limit=20" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "demo-school",
    "name": "2024年秋季学期课程表",
    "description": "2024年秋季学期全校课程安排",
    "academic_year": "2024-2025",
    "semester": "秋季学期",
    "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
    "school_id": "550e8400-e29b-41d4-a716-446655440002",
    "status": "draft",
    "version": 1,
    "total_sections": 120,
    "scheduled_sections": 0,
    "optimization_score": 0.0,
    "published_at": null,
    "published_by": null,
    "notes": "待调度",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "system",
    "updated_by": "system"
  }
]
```

### 获取时间表详情

**GET** `/api/v1/timetables/{timetable_id}`

获取指定时间表的详细信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `timetable_id` | UUID | 是 | 时间表 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/timetables/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "name": "2024年秋季学期课程表",
  "description": "2024年秋季学期全校课程安排",
  "academic_year": "2024-2025",
  "semester": "秋季学期",
  "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
  "school_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "draft",
  "version": 1,
  "total_sections": 120,
  "scheduled_sections": 0,
  "optimization_score": 0.0,
  "published_at": null,
  "published_by": null,
  "notes": "待调度",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 创建时间表

**POST** `/api/v1/timetables/`

创建新的时间表记录。

#### 请求体

```json
{
  "name": "2024年春季学期课程表",
  "description": "2024年春季学期全校课程安排",
  "academic_year": "2024-2025",
  "semester": "春季学期",
  "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
  "school_id": "550e8400-e29b-41d4-a716-446655440002",
  "total_sections": 100,
  "notes": "待调度"
}
```

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/timetables/" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2024年春季学期课程表",
    "description": "2024年春季学期全校课程安排",
    "academic_year": "2024-2025",
    "semester": "春季学期",
    "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
    "school_id": "550e8400-e29b-41d4-a716-446655440002",
    "total_sections": 100,
    "notes": "待调度"
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "tenant_id": "demo-school",
  "name": "2024年春季学期课程表",
  "description": "2024年春季学期全校课程安排",
  "academic_year": "2024-2025",
  "semester": "春季学期",
  "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
  "school_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "draft",
  "version": 1,
  "total_sections": 100,
  "scheduled_sections": 0,
  "optimization_score": 0.0,
  "published_at": null,
  "published_by": null,
  "notes": "待调度",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 更新时间表

**PUT** `/api/v1/timetables/{timetable_id}`

更新现有时间表的信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `timetable_id` | UUID | 是 | 时间表 ID |

#### 请求体

```json
{
  "name": "2024年春季学期课程表（更新）",
  "description": "2024年春季学期全校课程安排（包含调整）",
  "total_sections": 110
}
```

#### 请求示例

```bash
curl -X PUT "http://localhost:8000/api/v1/timetables/550e8400-e29b-41d4-a716-446655440003" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2024年春季学期课程表（更新）",
    "description": "2024年春季学期全校课程安排（包含调整）",
    "total_sections": 110
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "tenant_id": "demo-school",
  "name": "2024年春季学期课程表（更新）",
  "description": "2024年春季学期全校课程安排（包含调整）",
  "academic_year": "2024-2025",
  "semester": "春季学期",
  "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
  "school_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "draft",
  "version": 1,
  "total_sections": 110,
  "scheduled_sections": 0,
  "optimization_score": 0.0,
  "published_at": null,
  "published_by": null,
  "notes": "待调度",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 删除时间表

**DELETE** `/api/v1/timetables/{timetable_id}`

删除指定的时间表。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `timetable_id` | UUID | 是 | 时间表 ID |

#### 请求示例

```bash
curl -X DELETE "http://localhost:8000/api/v1/timetables/550e8400-e29b-41d4-a716-446655440003" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应

成功删除时返回 HTTP 204 No Content。

### 发布时间表

**POST** `/api/v1/timetables/{timetable_id}/publish`

发布指定的时间表，使其对用户可见。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `timetable_id` | UUID | 是 | 时间表 ID |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/timetables/550e8400-e29b-41d4-a716-446655440000/publish" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "name": "2024年秋季学期课程表",
  "description": "2024年秋季学期全校课程安排",
  "academic_year": "2024-2025",
  "semester": "秋季学期",
  "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
  "school_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "published",
  "version": 1,
  "total_sections": 120,
  "scheduled_sections": 120,
  "optimization_score": 0.85,
  "published_at": "2024-01-01T12:00:00Z",
  "published_by": "system",
  "notes": "已发布",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 获取时间表分配

**GET** `/api/v1/timetables/{timetable_id}/assignments`

获取指定时间表的所有课程分配详情。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `timetable_id` | UUID | 是 | 时间表 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/timetables/550e8400-e29b-41d4-a716-446655440000/assignments" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "message": "分配查询功能待实现"
}
```

## 错误处理

### 常见错误

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误，如时间表名称已存在 |
| 404 | Not Found | 时间表不存在 |
| 409 | Conflict | 时间表状态不允许操作 |
| 422 | Unprocessable Entity | 数据验证失败 |

### 错误响应示例

```json
{
  "error": "HTTP错误",
  "message": "时间表不存在",
  "status_code": 404,
  "path": "/api/v1/timetables/550e8400-e29b-41d4-a716-446655440000"
}
```

## 使用示例

### Python 示例

```python
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TENANT_ID = "demo-school"
HEADERS = {
    "X-Tenant-ID": TENANT_ID,
    "Content-Type": "application/json"
}

# 获取时间表列表
def list_timetables(calendar_id=None, status_filter=None):
    params = {}
    if calendar_id:
        params["calendar_id"] = calendar_id
    if status_filter:
        params["status_filter"] = status_filter

    response = requests.get(
        f"{BASE_URL}/timetables/",
        headers=HEADERS,
        params=params
    )
    return response.json()

# 创建时间表
def create_timetable(timetable_data):
    response = requests.post(
        f"{BASE_URL}/timetables/",
        headers=HEADERS,
        json=timetable_data
    )
    return response.json()

# 发布时间表
def publish_timetable(timetable_id):
    response = requests.post(
        f"{BASE_URL}/timetables/{timetable_id}/publish",
        headers=HEADERS
    )
    return response.json()

# 示例用法
timetable_data = {
    "name": "2024年夏季学期课程表",
    "description": "2024年夏季学期全校课程安排",
    "academic_year": "2024-2025",
    "semester": "夏季学期",
    "calendar_id": "550e8400-e29b-41d4-a716-446655440001",
    "school_id": "550e8400-e29b-41d4-a716-446655440002",
    "total_sections": 80,
    "notes": "待调度"
}

try:
    # 创建时间表
    new_timetable = create_timetable(timetable_data)
    print(f"创建时间表成功: {new_timetable['id']}")

    # 获取已发布的时间表
    published_timetables = list_timetables(status_filter="published")
    print(f"已发布时间表数量: {len(published_timetables)}")

    # 发布时间表
    # publish_timetable(new_timetable['id'])
    # print(f"时间表已发布: {new_timetable['name']}")

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

// 获取时间表列表
async function listTimetables(calendarId = null, statusFilter = null) {
    const params = new URLSearchParams();
    if (calendarId) {
        params.append('calendar_id', calendarId);
    }
    if (statusFilter) {
        params.append('status_filter', statusFilter);
    }

    const response = await fetch(`${BASE_URL}/timetables/?${params}`, {
        headers: HEADERS
    });
    return await response.json();
}

// 创建时间表
async function createTimetable(timetableData) {
    const response = await fetch(`${BASE_URL}/timetables/`, {
        method: 'POST',
        headers: HEADERS,
        body: JSON.stringify(timetableData)
    });
    return await response.json();
}

// 发布时间表
async function publishTimetable(timetableId) {
    const response = await fetch(`${BASE_URL}/timetables/${timetableId}/publish`, {
        method: 'POST',
        headers: HEADERS
    });
    return await response.json();
}

// 示例用法
(async () => {
    const timetableData = {
        name: '2024年冬季学期课程表',
        description: '2024年冬季学期全校课程安排',
        academic_year: '2024-2025',
        semester: '冬季学期',
        calendar_id: '550e8400-e29b-41d4-a716-446655440001',
        school_id: '550e8400-e29b-41d4-a716-446655440002',
        total_sections: 60,
        notes: '待调度'
    };

    try {
        // 创建时间表
        const newTimetable = await createTimetable(timetableData);
        console.log(`创建时间表成功: ${newTimetable.id}`);

        // 获取草稿状态的时间表
        const draftTimetables = await listTimetables(null, 'draft');
        console.log(`草稿时间表数量: ${draftTimetables.length}`);

        // 发布时间表
        // const publishedTimetable = await publishTimetable(newTimetable.id);
        // console.log(`时间表已发布: ${publishedTimetable.name}`);

    } catch (error) {
        console.error('请求失败:', error);
    }
})();
```

## 时间表生命周期

### 状态流转

```
draft → scheduled → feasible → optimized → published
                                      ↓
                                 archived
```

### 状态说明

1. **draft** - 草稿
   - 新创建的时间表
   - 可以编辑基本信息
   - 可以进行调度

2. **scheduled** - 已安排
   - 完成基本调度
   - 所有课程都有时间安排
   - 可能存在约束冲突

3. **feasible** - 可行
   - 解决了所有硬约束冲突
   - 基础可行解
   - 可以进一步优化

4. **optimized** - 已优化
   - 在可行解基础上优化软约束
   - 达到较高的优化分数
   - 准备发布

5. **published** - 已发布
   - 对用户可见
   - 只读状态
   - 可以归档

6. **archived** - 已归档
   - 历史记录
   - 不可修改
   - 用于参考

## 调度集成

时间表与调度引擎紧密集成：

### 调度输入
- 时间表基本信息
- 教学段定义
- 约束条件
- 优化目标

### 调度输出
- 具体的时间安排
- 教师-课程分配
- 教室-课程分配
- 优化指标

### 进度跟踪
- 实时更新调度进度
- 显示约束违反情况
- 优化分数变化

## 注意事项

1. **名称唯一性**: 时间表名称在同一租户内必须唯一
2. **状态管理**: 遵循时间表生命周期状态流转
3. **发布控制**: 只有优化完成的时间表才能发布
4. **版本管理**: 修改已发布的时间表会创建新版本
5. **性能考虑**: 大规模时间表调度可能需要较长时间