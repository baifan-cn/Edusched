# 课程管理 API

## 概述

课程管理 API 提供了对课程信息的管理功能，包括课程的基本信息、学科分类、学分设置等。课程是教育调度系统中的核心资源，与教师、教室、时间等资源紧密关联。

### 基础信息

- **路径**: `/api/v1/courses`
- **方法**: GET, POST, PUT, DELETE
- **认证**: 需要租户 ID (`X-Tenant-ID`)
- **数据模型**: Course

## 数据模型

### Course

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "code": "MATH101",
  "name": "高等数学",
  "description": "大学一年级高等数学课程，包括微积分、线性代数等内容",
  "subject_id": "550e8400-e29b-41d4-a716-446655440001",
  "credits": 4,
  "hours_per_week": 4,
  "total_hours": 64,
  "prerequisites": [],
  "is_required": true,
  "max_students": 120,
  "min_students": 30,
  "requires_lab": false,
  "lab_hours": 0,
  "notes": "重要基础课程，建议优先安排",
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
| `id` | UUID | 自动 | 课程唯一标识符 |
| `tenant_id` | string | 自动 | 租户标识符 |
| `code` | string | 是 | 课程代码，在同一租户内唯一 |
| `name` | string | 是 | 课程名称 |
| `description` | string | 否 | 课程描述 |
| `subject_id` | UUID | 是 | 所属学科 ID |
| `credits` | integer | 是 | 学分数 |
| `hours_per_week` | integer | 是 | 每周课时数 |
| `total_hours` | integer | 是 | 总课时数 |
| `prerequisites` | array | 否 | 先修课程 ID 列表 |
| `is_required` | boolean | 否 | 是否为必修课，默认 true |
| `max_students` | integer | 否 | 最大学生数 |
| `min_students` | 否 | 最小学生数 |
| `requires_lab` | boolean | 否 | 是否需要实验室，默认 false |
| `lab_hours` | integer | 否 | 实验课时数 |
| `notes` | string | 否 | 备注 |
| `is_active` | boolean | 否 | 是否激活，默认 true |
| `created_at` | datetime | 自动 | 创建时间 |
| `updated_at` | datetime | 自动 | 更新时间 |
| `created_by` | string | 自动 | 创建者 |
| `updated_by` | string | 自动 | 更新者 |

## API 端点

### 获取课程列表

**GET** `/api/v1/courses/`

获取当前租户下的所有课程列表，支持分页和学科过滤。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `skip` | integer | 否 | 跳过的记录数，默认 0 |
| `limit` | integer | 否 | 返回的记录数，默认 100，最大 1000 |
| `subject_id` | UUID | 否 | 学科 ID 过滤 |

#### 请求示例

```bash
# 获取所有课程
curl -X GET "http://localhost:8000/api/v1/courses/" \
  -H "X-Tenant-ID: demo-school"

# 获取指定学科的课程
curl -X GET "http://localhost:8000/api/v1/courses/?subject_id=550e8400-e29b-41d4-a716-446655440001" \
  -H "X-Tenant-ID: demo-school"

# 分页获取
curl -X GET "http://localhost:8000/api/v1/courses/?skip=0&limit=20" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "demo-school",
    "code": "MATH101",
    "name": "高等数学",
    "description": "大学一年级高等数学课程，包括微积分、线性代数等内容",
    "subject_id": "550e8400-e29b-41d4-a716-446655440001",
    "credits": 4,
    "hours_per_week": 4,
    "total_hours": 64,
    "prerequisites": [],
    "is_required": true,
    "max_students": 120,
    "min_students": 30,
    "requires_lab": false,
    "lab_hours": 0,
    "notes": "重要基础课程，建议优先安排",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "system",
    "updated_by": "system"
  }
]
```

### 获取课程详情

**GET** `/api/v1/courses/{course_id}`

获取指定课程的详细信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `course_id` | UUID | 是 | 课程 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/courses/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "code": "MATH101",
  "name": "高等数学",
  "description": "大学一年级高等数学课程，包括微积分、线性代数等内容",
  "subject_id": "550e8400-e29b-41d4-a716-446655440001",
  "credits": 4,
  "hours_per_week": 4,
  "total_hours": 64,
  "prerequisites": [],
  "is_required": true,
  "max_students": 120,
  "min_students": 30,
  "requires_lab": false,
  "lab_hours": 0,
  "notes": "重要基础课程，建议优先安排",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 创建课程

**POST** `/api/v1/courses/`

创建新的课程记录。

#### 请求体

```json
{
  "code": "PHYS101",
  "name": "大学物理",
  "description": "大学一年级物理课程，包括力学、热学、电磁学等内容",
  "subject_id": "550e8400-e29b-41d4-a716-446655440002",
  "credits": 3,
  "hours_per_week": 3,
  "total_hours": 48,
  "is_required": true,
  "max_students": 100,
  "min_students": 25,
  "requires_lab": true,
  "lab_hours": 1,
  "notes": "包含实验课程"
}
```

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/courses/" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PHYS101",
    "name": "大学物理",
    "description": "大学一年级物理课程，包括力学、热学、电磁学等内容",
    "subject_id": "550e8400-e29b-41d4-a716-446655440002",
    "credits": 3,
    "hours_per_week": 3,
    "total_hours": 48,
    "is_required": true,
    "max_students": 100,
    "min_students": 25,
    "requires_lab": true,
    "lab_hours": 1,
    "notes": "包含实验课程"
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "tenant_id": "demo-school",
  "code": "PHYS101",
  "name": "大学物理",
  "description": "大学一年级物理课程，包括力学、热学、电磁学等内容",
  "subject_id": "550e8400-e29b-41d4-a716-446655440002",
  "credits": 3,
  "hours_per_week": 3,
  "total_hours": 48,
  "prerequisites": [],
  "is_required": true,
  "max_students": 100,
  "min_students": 25,
  "requires_lab": true,
  "lab_hours": 1,
  "notes": "包含实验课程",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 更新课程

**PUT** `/api/v1/courses/{course_id}`

更新现有课程的信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `course_id` | UUID | 是 | 课程 ID |

#### 请求体

```json
{
  "name": "大学物理（更新）",
  "description": "大学一年级物理课程，包括力学、热学、电磁学、光学等内容",
  "credits": 4,
  "max_students": 120,
  "requires_lab": false
}
```

#### 请求示例

```bash
curl -X PUT "http://localhost:8000/api/v1/courses/550e8400-e29b-41d4-a716-446655440003" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "大学物理（更新）",
    "description": "大学一年级物理课程，包括力学、热学、电磁学、光学等内容",
    "credits": 4,
    "max_students": 120,
    "requires_lab": false
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "tenant_id": "demo-school",
  "code": "PHYS101",
  "name": "大学物理（更新）",
  "description": "大学一年级物理课程，包括力学、热学、电磁学、光学等内容",
  "subject_id": "550e8400-e29b-41d4-a716-446655440002",
  "credits": 4,
  "hours_per_week": 3,
  "total_hours": 48,
  "prerequisites": [],
  "is_required": true,
  "max_students": 120,
  "min_students": 25,
  "requires_lab": false,
  "lab_hours": 0,
  "notes": "包含实验课程",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 删除课程

**DELETE** `/api/v1/courses/{course_id}`

删除指定的课程。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `course_id` | UUID | 是 | 课程 ID |

#### 请求示例

```bash
curl -X DELETE "http://localhost:8000/api/v1/courses/550e8400-e29b-41d4-a716-446655440003" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应

成功删除时返回 HTTP 204 No Content。

## 错误处理

### 常见错误

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误，如课程代码已存在 |
| 404 | Not Found | 课程不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |

### 错误响应示例

```json
{
  "error": "HTTP错误",
  "message": "课程不存在",
  "status_code": 404,
  "path": "/api/v1/courses/550e8400-e29b-41d4-a716-446655440003"
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

# 获取课程列表
def list_courses(subject_id=None):
    params = {}
    if subject_id:
        params["subject_id"] = subject_id

    response = requests.get(
        f"{BASE_URL}/courses/",
        headers=HEADERS,
        params=params
    )
    return response.json()

# 创建课程
def create_course(course_data):
    response = requests.post(
        f"{BASE_URL}/courses/",
        headers=HEADERS,
        json=course_data
    )
    return response.json()

# 更新课程
def update_course(course_id, update_data):
    response = requests.put(
        f"{BASE_URL}/courses/{course_id}",
        headers=HEADERS,
        json=update_data
    )
    return response.json()

# 示例用法
course_data = {
    "code": "CHEM101",
    "name": "大学化学",
    "description": "大学一年级化学课程，包括无机化学、有机化学基础",
    "subject_id": "550e8400-e29b-41d4-a716-446655440003",
    "credits": 3,
    "hours_per_week": 3,
    "total_hours": 48,
    "is_required": true,
    "max_students": 80,
    "min_students": 20,
    "requires_lab": true,
    "lab_hours": 2,
    "notes": "包含实验课程，需要注意安全"
}

try:
    # 创建课程
    new_course = create_course(course_data)
    print(f"创建课程成功: {new_course['id']}")

    # 获取指定学科的课程
    subject_courses = list_courses(subject_id="550e8400-e29b-41d4-a716-446655440003")
    print(f"指定学科课程数量: {len(subject_courses)}")

    # 更新课程信息
    update_data = {
        "credits": 4,
        "max_students": 100
    }
    updated_course = update_course(new_course['id'], update_data)
    print(f"更新课程学分: {updated_course['credits']}")

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

// 获取课程列表
async function listCourses(subjectId = null) {
    const params = new URLSearchParams();
    if (subjectId) {
        params.append('subject_id', subjectId);
    }

    const response = await fetch(`${BASE_URL}/courses/?${params}`, {
        headers: HEADERS
    });
    return await response.json();
}

// 创建课程
async function createCourse(courseData) {
    const response = await fetch(`${BASE_URL}/courses/`, {
        method: 'POST',
        headers: HEADERS,
        body: JSON.stringify(courseData)
    });
    return await response.json();
}

// 更新课程
async function updateCourse(courseId, updateData) {
    const response = await fetch(`${BASE_URL}/courses/${courseId}`, {
        method: 'PUT',
        headers: HEADERS,
        body: JSON.stringify(updateData)
    });
    return await response.json();
}

// 示例用法
(async () => {
    const courseData = {
        code: 'COMP101',
        name: '计算机科学导论',
        description: '计算机科学基础课程，包括编程基础、数据结构等',
        subject_id: '550e8400-e29b-41d4-a716-446655440004',
        credits: 3,
        hours_per_week: 3,
        total_hours: 48,
        is_required: true,
        max_students: 60,
        min_students: 15,
        requires_lab: true,
        lab_hours: 2,
        notes: '需要计算机实验室'
    };

    try {
        // 创建课程
        const newCourse = await createCourse(courseData);
        console.log(`创建课程成功: ${newCourse.id}`);

        // 获取指定学科的课程
        const subjectCourses = await listCourses('550e8400-e29b-41d4-a716-446655440004');
        console.log(`指定学科课程数量: ${subjectCourses.length}`);

        // 更新课程信息
        const updateData = {
            name: '计算机科学导论（更新）',
            max_students: 80
        };
        const updatedCourse = await updateCourse(newCourse.id, updateData);
        console.log(`更新课程名称: ${updatedCourse.name}`);

    } catch (error) {
        console.error('请求失败:', error);
    }
})();
```

## 课程类型说明

### 按课程性质分类

1. **必修课** (`is_required: true`)
   - 专业必修课
   - 公共必修课
   - 学生必须完成才能毕业

2. **选修课** (`is_required: false`)
   - 专业选修课
   - 公共选修课
   - 学生可根据兴趣选择

### 按教学方式分类

1. **理论课** (`requires_lab: false`)
   - 课堂教学
   - 理论讲授为主

2. **实验课** (`requires_lab: true`)
   - 实验教学
   - 需要实验室设备
   - 包含 `lab_hours` 实验课时

## 调度约束

课程信息在调度系统中用于以下约束：

### 容量约束
- **最大学生数**: 课程安排的教室容量必须 >= `max_students`
- **最小学生数**: 选课人数必须 >= `min_students` 才开课

### 时间约束
- **周课时**: 每周安排 `hours_per_week` 课时
- **总课时**: 整学期安排 `total_hours` 课时
- **实验课时**: 如果 `requires_lab` 为 true，需要额外安排 `lab_hours`

### 教师约束
- **专业匹配**: 教师专业背景必须与课程匹配
- **工作量**: 考虑教师在多门课程上的总课时

### 教室约束
- **实验室需求**: 实验课程必须安排在实验室
- **设备要求**: 特殊课程需要特定设备

## 注意事项

1. **代码唯一性**: 课程代码在同一租户内必须唯一
2. **数据完整性**: 删除课程前需要检查是否有相关的教学安排
3. **先修课程**: 确保先修课程的逻辑关系正确
4. **容量管理**: 合理设置最大最小学生数，避免资源浪费
5. **实验课程**: 实验课程需要特殊的教学资源安排