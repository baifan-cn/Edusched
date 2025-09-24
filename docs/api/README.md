# Edusched API 文档

## 概述

Edusched 是一个智能教育调度平台，提供完整的 REST API 用于管理学校、教师、课程、时间表以及智能调度功能。API 基于 FastAPI 框架构建，遵循 OpenAPI 3.0 规范。

### 核心特性

- 🎯 **智能调度算法**: 使用 OR-Tools CP-SAT 求解器实现高效的课程表生成
- 🔒 **多租户支持**: 支持多所学校独立使用，数据完全隔离
- 🏫 **多校区管理**: 支持跨校区约束和资源管理
- 📊 **实时进度监控**: 调度过程可视化，支持暂停、恢复和取消
- 🎨 **现代化API**: 基于 FastAPI，自动生成交互式文档

### 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **API版本**: v1
- **数据格式**: JSON
- **认证方式**: Bearer Token (待实现)
- **多租户**: 通过 `X-Tenant-ID` 请求头指定

### 快速开始

#### 1. 设置环境

```bash
# 克隆项目
git clone <repository-url>
cd Edusched

# 安装依赖
pip install uv
uv pip install -e .

# 启动开发服务器
uvicorn edusched.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 基本请求示例

```bash
# 设置租户ID (必需)
export TENANT_ID="demo-school"

# 获取学校列表
curl -X GET "http://localhost:8000/api/v1/schools/" \
  -H "X-Tenant-ID: $TENANT_ID"

# 创建学校
curl -X POST "http://localhost:8000/api/v1/schools/" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示范学校",
    "code": "DEMO001",
    "address": "北京市海淀区",
    "academic_year": "2024-2025",
    "semester": "秋季学期"
  }'
```

#### 3. 访问交互式文档

启动服务后，您可以访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### 认证和授权

当前版本中，API 使用多租户架构进行数据隔离。每个请求都需要包含 `X-Tenant-ID` 请求头来指定租户。

```http
X-Tenant-ID: your-tenant-id
```

**注意**: 完整的用户认证和授权系统正在开发中。

### 错误处理

API 使用标准的 HTTP 状态码，并返回统一的错误格式：

```json
{
  "error": "错误类型",
  "message": "详细的错误信息",
  "status_code": 400,
  "path": "/api/v1/schools/"
}
```

常见状态码：

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权（待实现）
- `403 Forbidden`: 禁止访问（待实现）
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

### 分页和过滤

列表接口支持分页和过滤：

```http
GET /api/v1/schools/?skip=0&limit=20&sort=name:asc
```

#### 分页参数

- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的记录数 (默认: 100, 最大: 1000)
- `sort`: 排序字段，格式 `field:direction` (例如: `name:asc`)

#### 过滤参数

根据不同的资源，支持特定的过滤参数，例如：

- `/api/v1/teachers/?department=数学系`
- `/api/v1/scheduling/jobs/?status_filter=running`

### 数据模型

所有 API 响应都遵循统一的模型结构：

#### 基础字段

- `id`: 资源唯一标识符 (UUID)
- `tenant_id`: 租户标识符
- `created_at`: 创建时间 (ISO 8601 格式)
- `updated_at`: 更新时间 (ISO 8601 格式)
- `created_by`: 创建者用户标识
- `updated_by`: 更新者用户标识

### API 模块

API 按功能模块组织：

#### 🏫 学校管理 (`/api/v1/schools`)
管理学校基本信息和校区

#### 👨‍🏫 教师管理 (`/api/v1/teachers`)
管理教师信息和教学安排

#### 📚 课程管理 (`/api/v1/courses`)
管理课程信息、教学段和教室资源

#### 📅 时间表管理 (`/api/v1/timetables`)
管理课程表和时间安排

#### 🤖 调度引擎 (`/api/v1/scheduling`)
智能调度算法和任务管理

#### 💚 健康检查 (`/api/v1/health`)
系统健康状态检查

### 最佳实践

1. **租户隔离**: 始终在请求中包含正确的 `X-Tenant-ID`
2. **错误处理**: 检查 HTTP 状态码，不要只依赖响应内容
3. **分页使用**: 对大数据集使用分页，避免一次性获取过多数据
4. **资源清理**: 删除资源前检查是否有依赖关系
5. **并发控制**: 调度任务支持并发执行，但需要合理管理资源

### 开发指南

#### 本地开发

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/
```

#### API 扩展

添加新的 API 端点时，请遵循以下规范：

1. 在 `src/edusched/api/routers/` 目录下创建路由文件
2. 使用 Pydantic 模型定义请求和响应
3. 添加适当的错误处理和验证
4. 包含完整的 docstring 文档
5. 在 `main.py` 中注册路由

#### 文档更新

API 文档应该与代码保持同步：

- 使用 FastAPI 的自动文档生成功能
- 为每个端点添加详细的描述和示例
- 更新本文档时保持结构清晰

### 常见问题

#### Q: 如何处理跨校区调度？
A: 系统自动考虑校区间的行程时间，确保教师有足够的时间在不同校区间移动。

#### Q: 调度算法支持哪些约束？
A: 支持硬约束（教师时间冲突、教室占用等）和软约束（教师偏好、课程分布等）。

#### Q: 如何监控调度进度？
A: 使用 `/api/v1/scheduling/jobs/{job_id}/progress` 端点实时获取任务进度。

#### Q: API 是否支持批量操作？
A: 当前版本主要支持单个资源的 CRUD 操作，批量操作功能正在规划中。

### 更新日志

#### v1.0.0 (当前版本)
- 基础 CRUD API
- 多租户架构
- 智能调度引擎
- 实时进度监控

### 技术支持

如有问题或建议，请通过以下方式联系：

- 创建 GitHub Issue
- 发送邮件至开发团队
- 查看项目 Wiki 和文档