# 学校管理 API

## 概述

学校管理 API 提供了对学校及其校区的基本管理功能。每个学校可以包含多个校区，支持跨校区资源管理和调度。

### 基础信息

- **路径**: `/api/v1/schools`
- **方法**: GET, POST, PUT, DELETE
- **认证**: 需要租户 ID (`X-Tenant-ID`)
- **数据模型**: School

## 数据模型

### School

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "name": "示范学校",
  "code": "DEMO001",
  "address": "北京市海淀区中关村大街1号",
  "phone": "010-12345678",
  "email": "info@demo.edu.cn",
  "website": "https://www.demo.edu.cn",
  "timezone": "Asia/Shanghai",
  "academic_year": "2024-2025",
  "semester": "秋季学期",
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
| `id` | UUID | 自动 | 学校唯一标识符 |
| `tenant_id` | string | 自动 | 租户标识符 |
| `name` | string | 是 | 学校名称 |
| `code` | string | 是 | 学校代码，在同一租户内唯一 |
| `address` | string | 否 | 学校地址 |
| `phone` | string | 否 | 联系电话 |
| `email` | string | 否 | 联系邮箱 |
| `website` | string | 否 | 学校网站 |
| `timezone` | string | 否 | 时区，默认 "Asia/Shanghai" |
| `academic_year` | string | 是 | 学年，格式 "YYYY-YYYY" |
| `semester` | string | 是 | 学期，如 "春季学期"、"秋季学期" |
| `is_active` | boolean | 否 | 是否激活，默认 true |
| `created_at` | datetime | 自动 | 创建时间 |
| `updated_at` | datetime | 自动 | 更新时间 |
| `created_by` | string | 自动 | 创建者 |
| `updated_by` | string | 自动 | 更新者 |

## API 端点

### 获取学校列表

**GET** `/api/v1/schools/`

获取当前租户下的所有学校列表，支持分页。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `skip` | integer | 否 | 跳过的记录数，默认 0 |
| `limit` | integer | 否 | 返回的记录数，默认 100，最大 1000 |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/schools/?skip=0&limit=20" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "demo-school",
    "name": "示范学校",
    "code": "DEMO001",
    "address": "北京市海淀区中关村大街1号",
    "phone": "010-12345678",
    "email": "info@demo.edu.cn",
    "website": "https://www.demo.edu.cn",
    "timezone": "Asia/Shanghai",
    "academic_year": "2024-2025",
    "semester": "秋季学期",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "system",
    "updated_by": "system"
  }
]
```

### 获取学校详情

**GET** `/api/v1/schools/{school_id}`

获取指定学校的详细信息，包括校区信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `school_id` | UUID | 是 | 学校 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "name": "示范学校",
  "code": "DEMO001",
  "address": "北京市海淀区中关村大街1号",
  "phone": "010-12345678",
  "email": "info@demo.edu.cn",
  "website": "https://www.demo.edu.cn",
  "timezone": "Asia/Shanghai",
  "academic_year": "2024-2025",
  "semester": "秋季学期",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 创建学校

**POST** `/api/v1/schools/`

创建新的学校记录。

#### 请求体

```json
{
  "name": "示范学校",
  "code": "DEMO001",
  "address": "北京市海淀区中关村大街1号",
  "phone": "010-12345678",
  "email": "info@demo.edu.cn",
  "website": "https://www.demo.edu.cn",
  "academic_year": "2024-2025",
  "semester": "秋季学期"
}
```

#### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/schools/" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示范学校",
    "code": "DEMO001",
    "address": "北京市海淀区中关村大街1号",
    "phone": "010-12345678",
    "email": "info@demo.edu.cn",
    "website": "https://www.demo.edu.cn",
    "academic_year": "2024-2025",
    "semester": "秋季学期"
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "name": "示范学校",
  "code": "DEMO001",
  "address": "北京市海淀区中关村大街1号",
  "phone": "010-12345678",
  "email": "info@demo.edu.cn",
  "website": "https://www.demo.edu.cn",
  "timezone": "Asia/Shanghai",
  "academic_year": "2024-2025",
  "semester": "秋季学期",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 更新学校

**PUT** `/api/v1/schools/{school_id}`

更新现有学校的信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `school_id` | UUID | 是 | 学校 ID |

#### 请求体

```json
{
  "name": "示范学校（更新）",
  "phone": "010-87654321",
  "semester": "春季学期"
}
```

#### 请求示例

```bash
curl -X PUT "http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示范学校（更新）",
    "phone": "010-87654321",
    "semester": "春季学期"
  }'
```

#### 响应示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "demo-school",
  "name": "示范学校（更新）",
  "code": "DEMO001",
  "address": "北京市海淀区中关村大街1号",
  "phone": "010-87654321",
  "email": "info@demo.edu.cn",
  "website": "https://www.demo.edu.cn",
  "timezone": "Asia/Shanghai",
  "academic_year": "2024-2025",
  "semester": "春季学期",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "created_by": "system",
  "updated_by": "system"
}
```

### 删除学校

**DELETE** `/api/v1/schools/{school_id}`

删除指定的学校。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `school_id` | UUID | 是 | 学校 ID |

#### 请求示例

```bash
curl -X DELETE "http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应

成功删除时返回 HTTP 204 No Content。

### 获取学校校区列表

**GET** `/api/v1/schools/{school_id}/campuses`

获取指定学校的所有校区信息。

#### 参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `school_id` | UUID | 是 | 学校 ID |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000/campuses" \
  -H "X-Tenant-ID: demo-school"
```

#### 响应示例

```json
{
  "message": "校区查询功能待实现"
}
```

## 错误处理

### 常见错误

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 学校不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |

### 错误响应示例

```json
{
  "error": "HTTP错误",
  "message": "学校不存在",
  "status_code": 404,
  "path": "/api/v1/schools/550e8400-e29b-41d4-a716-446655440000"
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

# 获取学校列表
def list_schools():
    response = requests.get(
        f"{BASE_URL}/schools/",
        headers=HEADERS
    )
    return response.json()

# 创建学校
def create_school(school_data):
    response = requests.post(
        f"{BASE_URL}/schools/",
        headers=HEADERS,
        json=school_data
    )
    return response.json()

# 示例用法
school_data = {
    "name": "示例学校",
    "code": "EXAMPLE001",
    "address": "北京市朝阳区",
    "academic_year": "2024-2025",
    "semester": "秋季学期"
}

try:
    # 创建学校
    new_school = create_school(school_data)
    print(f"创建学校成功: {new_school['id']}")

    # 获取学校列表
    schools = list_schools()
    print(f"学校总数: {len(schools)}")

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

// 获取学校列表
async function listSchools() {
    const response = await fetch(`${BASE_URL}/schools/`, {
        headers: HEADERS
    });
    return await response.json();
}

// 创建学校
async function createSchool(schoolData) {
    const response = await fetch(`${BASE_URL}/schools/`, {
        method: 'POST',
        headers: HEADERS,
        body: JSON.stringify(schoolData)
    });
    return await response.json();
}

// 示例用法
(async () => {
    const schoolData = {
        name: '示例学校',
        code: 'EXAMPLE001',
        address: '北京市朝阳区',
        academic_year: '2024-2025',
        semester: '秋季学期'
    };

    try {
        // 创建学校
        const newSchool = await createSchool(schoolData);
        console.log(`创建学校成功: ${newSchool.id}`);

        // 获取学校列表
        const schools = await listSchools();
        console.log(`学校总数: ${schools.length}`);

    } catch (error) {
        console.error('请求失败:', error);
    }
})();
```

## 注意事项

1. **代码唯一性**: 学校代码在同一租户内必须唯一
2. **数据完整性**: 删除学校前需要检查是否有依赖的校区、课程等数据
3. **并发控制**: 多个用户同时操作同一学校时，系统会自动处理并发
4. **软删除**: 当前使用硬删除，未来可能支持软删除功能
5. **校区管理**: 校区相关功能正在开发中