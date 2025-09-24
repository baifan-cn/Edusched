# 教师管理 API

## 概述

教师管理 API 提供了对教师信息的完整管理功能，包括教师的基本信息、部门分配、教学安排等。教师是调度系统中的重要资源，系统会考虑教师的时间约束和偏好进行课程安排。

### 基础信息

- **路径**: `/api/v1/teachers`
- **方法**: GET, POST, PUT, DELETE
- **认证**: 需要租户 ID (`X-Tenant-ID`)
- **数据模型**: Teacher

## 数据模型

### Teacher

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "employee_id": "T001",
  "name": "张老师",
  "email": "zhang.teacher@demo.edu.cn",
  "phone": "13800138000",
  "department": "数学系",
  "title": "教授",
  "specialization": "高等数学",
  "max_hours_per_week": 20,
  "preferred_days": ["monday", "wednesday", "friday"],
  "preferred_time_slots": ["morning", "afternoon"],
  "unavailable_periods": [],
  "notes": "教学经验丰富，擅长高等数学教学",
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
| `id` | UUID | 自动 | 教师唯一标识符 |
| `tenant_id` | string | 自动 | 租户标识符 |
| `employee_id` | string | 是 | 教师工号，在同一租户内唯一 |
| `name` | string | 是 | 教师姓名 |
| `email` | string | 否 | 教师邮箱 |
| `phone` | string | 否 | 联系电话 |
| `department` | string | 否 | 所属部门 |
| `title` | string | 否 | 职称 |
| `specialization` | string | 否 | 专业领域 |
| `max_hours_per_week` | integer | 否 | 每周最大教学课时，默认 20 |
| `preferred_days` | array | 否 | 偏好教学日期 |
| `preferred_time_slots` | array | 否 | 偏好时间段 |
| `unavailable_periods` | array | 否 | 不可用时间段 |
| `notes` | string | 否 | 备注 |
| `is_active` | boolean | 否 | 是否激活，默认 true |
| `created_at` | datetime | 自动 | 创建时间 |
| `updated_at` | datetime | 自动 | 更新时间 |
| `created_by` | string | 自动 | 创建者 |
| `updated_by` | string | 自动 | 更新者 |

### 枚举值说明

#### WeekDay (偏好教学日期)
- `monday` - 周一
- `tuesday` - 周二
- `wednesday` - 周三
- `thursday` - 周四
- `friday` - 周五
- `saturday` - 周六
- `sunday` - 周日

#### TimeSlot (偏好时间段)
- `morning` - 上午
- `afternoon` - 下午
- `evening` - 晚上

## API 端点

### 获取教师列表

**GET** `/api/v1/teachers/`

获取当前租户下的所有教师列表，支持分页和部门过滤。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `skip` | integer | 否 | 跳过的记录数，默认 0 |
| `limit` | integer | 否 | 返回的记录数，默认 100，最大 1000 |
| `department` | string | 否 | 部门过滤 |

#### 请求示例

```bash
# 获取所有教师
curl -X GET "http://localhost:8000/api/v1/teachers/" \
  -H "X-Tenant-ID: demo-school"

# 获取数学系教师
curl -X GET "http://localhost:8000/api/v1/teachers/?department=数学系" \
  -H "X-Tenant-ID: demo-school"

# 分页获取
curl -X GET "http://localhost:8000/api/v1/teachers/?skip=0&limit=20" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "demo-school",
    "employee_id": "T001",
    "name": "张老师",
    "email": "zhang.teacher@demo.edu.cn",
    "phone": "13800138000",
    "department": "数学系",
    "title": "教授",
    "specialization": "高等数学",
    "max_hours_per_week": 20,
    "preferred_days": ["monday", "wednesday", "friday"],
    "preferred_time_slots": ["morning", "afternoon"],
    "unavailable_periods": [],
    "notes": "教学经验丰富，擅长高等数学教学",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "system",
    "updated_by": "system"
  }
]
```

### 获取教师详情

**GET** `/api/v1/teachers/{teacher_id}`

获取指定教师的详细信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `teacher_id` | UUID | 是 | 教师 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/teachers/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "employee_id": "T001",
  "name": "张老师",
  "email": "zhang.teacher@demo.edu.cn",
  "phone": "13800138000",
  "department": "数学系",
  "title": "教授",
  "specialization": "高等数学",
  "max_hours_per_week": 20,
  "preferred_days": ["monday", "wednesday", "friday"],
  "preferred_time_slots": ["morning", "afternoon"],
  "unavailable_periods": [],
  "notes": "教学经验丰富，擅长高等数学教学",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 创建教师

**POST** `/api/v1/teachers/`

创建新的教师记录。

#### 请求体

```json
{
  "employee_id": "T001",
  "name": "张老师",
  "email": "zhang.teacher@demo.edu.cn",
  "phone": "13800138000",
  "department": "数学系",
  "title": "教授",
  "specialization": "高等数学",
  "max_hours_per_week": 20,
  "preferred_days": ["monday", "wednesday", "friday"],
  "preferred_time_slots": ["morning", "afternoon"],
  "notes": "教学经验丰富，擅长高等数学教学"
}
```

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/teachers/" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "T001",
    "name": "张老师",
    "email": "zhang.teacher@demo.edu.cn",
    "phone": "13800138000",
    "department": "数学系",
    "title": "教授",
    "specialization": "高等数学",
    "max_hours_per_week": 20,
    "preferred_days": ["monday", "wednesday", "friday"],
    "preferred_time_slots": ["morning", "afternoon"],
    "notes": "教学经验丰富，擅长高等数学教学"
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "employee_id": "T001",
  "name": "张老师",
  "email": "zhang.teacher@demo.edu.cn",
  "phone": "13800138000",
  "department": "数学系",
  "title": "教授",
  "specialization": "高等数学",
  "max_hours_per_week": 20,
  "preferred_days": ["monday", "wednesday", "friday"],
  "preferred_time_slots": ["morning", "afternoon"],
  "unavailable_periods": [],
  "notes": "教学经验丰富，擅长高等数学教学",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 更新教师

**PUT** `/api/v1/teachers/{teacher_id}`

更新现有教师的信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `teacher_id` | UUID | 是 | 教师 ID |

#### 请求体

```json
{
  "name": "张老师（更新）",
  "title": "副教授",
  "department": "应用数学系",
  "preferred_days": ["tuesday", "thursday"],
  "max_hours_per_week": 16
}
```

#### 请求示例

```bash
curl -X PUT "http://localhost:8000/api/v1/teachers/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张老师（更新）",
    "title": "副教授",
    "department": "应用数学系",
    "preferred_days": ["tuesday", "thursday"],
    "max_hours_per_week": 16
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "employee_id": "T001",
  "name": "张老师（更新）",
  "email": "zhang.teacher@demo.edu.cn",
  "phone": "13800138000",
  "department": "应用数学系",
  "title": "副教授",
  "specialization": "高等数学",
  "max_hours_per_week": 16,
  "preferred_days": ["tuesday", "thursday"],
  "preferred_time_slots": ["morning", "afternoon"],
  "unavailable_periods": [],
  "notes": "教学经验丰富，擅长高等数学教学",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 删除教师

**DELETE** `/api/v1/teachers/{teacher_id}`

删除指定的教师。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `teacher_id` | UUID | 是 | 教师 ID |

#### 请求示例

```bash
curl -X DELETE "http://localhost:8000/api/v1/teachers/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应

成功删除时返回 HTTP 204 No Content。

## 错误处理

### 常见错误

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误，如工号已存在 |
| 404 | Not Found | 教师不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |

### 错误响应示例

```json
{
  "error": "HTTP错误",
  "message": "教师不存在",
  "status_code": 404,
  "path": "/api/v1/teachers/550e8400-e29b-41d4-a716-446655440000"
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

# 获取教师列表
def list_teachers(department=None):
    params = {}
    if department:
        params["department"] = department

    response = requests.get(
        f"{BASE_URL}/teachers/",
        headers=HEADERS,
        params=params
    )
    return response.json()

# 创建教师
def create_teacher(teacher_data):
    response = requests.post(
        f"{BASE_URL}/teachers/",
        headers=HEADERS,
        json=teacher_data
    )
    return response.json()

# 更新教师
def update_teacher(teacher_id, update_data):
    response = requests.put(
        f"{BASE_URL}/teachers/{teacher_id}",
        headers=HEADERS,
        json=update_data
    )
    return response.json()

# 示例用法
teacher_data = {
    "employee_id": "T002",
    "name": "李老师",
    "email": "li.teacher@demo.edu.cn",
    "phone": "13900139000",
    "department": "物理系",
    "title": "副教授",
    "specialization": "理论物理",
    "max_hours_per_week": 18,
    "preferred_days": ["monday", "wednesday", "friday"],
    "preferred_time_slots": ["morning"],
    "notes": "专注于理论物理研究"
}

try:
    # 创建教师
    new_teacher = create_teacher(teacher_data)
    print(f"创建教师成功: {new_teacher['id']}")

    # 获取数学系教师
    math_teachers = list_teachers(department="数学系")
    print(f"数学系教师数量: {len(math_teachers)}")

    # 更新教师信息
    update_data = {
        "title": "教授",
        "max_hours_per_week": 20
    }
    updated_teacher = update_teacher(new_teacher['id'], update_data)
    print(f"更新教师职称: {updated_teacher['title']}")

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

// 获取教师列表
async function listTeachers(department = null) {
    const params = new URLSearchParams();
    if (department) {
        params.append('department', department);
    }

    const response = await fetch(`${BASE_URL}/teachers/?${params}`, {
        headers: HEADERS
    });
    return await response.json();
}

// 创建教师
async function createTeacher(teacherData) {
    const response = await fetch(`${BASE_URL}/teachers/`, {
        method: 'POST',
        headers: HEADERS,
        body: JSON.stringify(teacherData)
    });
    return await response.json();
}

// 更新教师
async function updateTeacher(teacherId, updateData) {
    const response = await fetch(`${BASE_URL}/teachers/${teacherId}`, {
        method: 'PUT',
        headers: HEADERS,
        body: JSON.stringify(updateData)
    });
    return await response.json();
}

// 示例用法
(async () => {
    const teacherData = {
        employee_id: 'T003',
        name: '王老师',
        email: 'wang.teacher@demo.edu.cn',
        phone: '13700137000',
        department: '化学系',
        title: '讲师',
        specialization: '有机化学',
        max_hours_per_week: 16,
        preferred_days: ['tuesday', 'thursday'],
        preferred_time_slots: ['afternoon'],
        notes: '专注于有机化学教学'
    };

    try {
        // 创建教师
        const newTeacher = await createTeacher(teacherData);
        console.log(`创建教师成功: ${newTeacher.id}`);

        // 获取化学系教师
        const chemTeachers = await listTeachers('化学系');
        console.log(`化学系教师数量: ${chemTeachers.length}`);

        // 更新教师信息
        const updateData = {
            title: '副教授',
            max_hours_per_week: 18
        };
        const updatedTeacher = await updateTeacher(newTeacher.id, updateData);
        console.log(`更新教师职称: ${updatedTeacher.title}`);

    } catch (error) {
        console.error('请求失败:', error);
    }
})();
```

## 调度约束

教师信息在调度系统中扮演重要角色，系统会考虑以下约束：

### 硬约束
1. **时间冲突**: 同一教师不能在同一时间教授多门课程
2. **课时限制**: 教师的周课时不能超过 `max_hours_per_week`
3. **不可用时间**: 教师在 `unavailable_periods` 指定的时间不能安排课程

### 软约束
1. **偏好日期**: 尽量安排在 `preferred_days` 指定的日期
2. **偏好时间段**: 尽量安排在 `preferred_time_slots` 指定的时间段
3. **部门分配**: 考虑教师的专业领域和部门归属

## 注意事项

1. **工号唯一性**: 教师工号在同一租户内必须唯一
2. **数据完整性**: 删除教师前需要检查是否有相关的教学分配
3. **调度影响**: 修改教师信息可能影响已生成的课程表
4. **性能优化**: 大量教师数据查询时建议使用分页
5. **实时同步**: 教师信息变更后，调度引擎会自动重新计算约束