# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Edusched是一个智能教育调度平台，旨在为学校生成可行且优化的课程表。系统使用先进的约束满足和优化算法，确保生成的课程表满足所有硬约束，并尽可能优化软约束。

### 技术栈
- **后端**: FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis + OR-Tools
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia + Vue Router
- **数据库**: PostgreSQL 16+ (多租户架构)
- **缓存**: Redis 7+ (会话存储和队列)
- **优化引擎**: Google OR-Tools CP-SAT求解器
- **容器化**: Docker + Docker Compose

### 核心特性
- 🎯 **智能调度算法**: 使用OR-Tools CP-SAT求解器实现高效的课程表生成
- 🔒 **多租户支持**: 支持多所学校独立使用，数据完全隔离
- 🏫 **多校区管理**: 支持跨校区约束和资源管理
- 📊 **实时进度监控**: 调度过程可视化，支持暂停、恢复和取消
- 🎨 **现代化UI**: 基于Vue 3 + Element Plus的响应式界面

## 开发环境设置

### 环境要求
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

### 常用开发命令

#### 后端开发
```bash
# 安装依赖
pip install uv
uv pip install -e .

# 启动开发服务器
uvicorn edusched.api.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest

# 代码质量检查
black src/
isort src/
mypy src/

# 数据库迁移
alembic upgrade head
alembic revision --autogenerate -m "描述"
```

#### 前端开发
```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器 (端口3000)
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test

# 代码质量检查
npm run lint
npm run format
npm run type-check
```

#### Docker开发环境
```bash
# 启动完整环境
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止服务
docker-compose down
```

## 项目架构

### 后端架构 (洋葱架构)
```
src/edusched/
├── api/                    # API层 - HTTP接口和DTO
│   ├── main.py            # FastAPI应用入口
│   └── routers/           # 路由模块
├── domain/                # 领域层 - 业务逻辑和实体
│   ├── models.py          # 领域模型 (Pydantic)
│   └── services/          # 领域服务
├── infrastructure/        # 基础设施层 - 技术实现
│   ├── database/          # 数据库相关
│   │   ├── models.py      # SQLAlchemy模型
│   │   └── connection.py  # 数据库连接
│   └── external/          # 外部服务集成
└── scheduling/           # 调度引擎
    └── engine.py         # OR-Tools求解器核心
```

### 前端架构 (Vue 3)
```
frontend/src/
├── components/            # 公共组件
├── pages/                # 页面组件
├── stores/               # Pinia状态管理
├── router/               # 路由配置
├── api/                  # API调用
├── utils/                # 工具函数
└── styles/               # 样式文件
```

### 核心模块说明

#### 调度引擎 (`src/edusched/scheduling/engine.py`)
- 使用OR-Tools CP-SAT求解器实现课程表优化
- 支持硬约束（必须满足）和软约束（尽量满足）
- 包含约束验证器和解的质量评估
- 核心类：`SchedulingProblem`、`SchedulingEngine`、`ConstraintValidator`

#### 数据模型 (`src/edusched/domain/models.py`)
- 定义所有领域实体：School、Teacher、Course、Section、Timetable等
- 使用Pydantic进行数据验证和序列化
- 包含业务逻辑验证和字段约束

#### API路由 (`src/edusched/api/routers/`)
- 模块化路由设计：schools、teachers、courses、timetables、scheduling
- 统一的错误处理和响应格式
- 支持分页、过滤和排序

#### 数据库模型 (`src/edusched/infrastructure/database/models.py`)
- SQLAlchemy 2.0风格的数据模型
- 支持多租户数据隔离（tenant_id）
- 完整的关联关系和索引设计
- 审计字段：created_at、updated_at、created_by、updated_by

## 开发注意事项

### 多租户架构
- 所有数据库查询必须包含`tenant_id`过滤
- 租户ID通过请求头`X-Tenant-ID`传递
- 每个API请求都会自动注入租户上下文

### 约束系统
- **硬约束**: 教师时间冲突、教室占用冲突、班级时间冲突
- **软约束**: 教师偏好、课程分布均匀性、教室利用率
- 约束权重范围：0.0-1.0

### 数据库设计原则
- 使用UUID主键，支持分布式系统
- 所有表继承`BaseTable`，包含审计字段
- 合理的索引设计，优化查询性能
- 外键约束确保数据完整性

### API设计规范
- RESTful风格，使用标准HTTP方法
- 统一的响应格式和错误处理
- 支持分页：`?page=1&size=20`
- 支持排序：`?sort=name:asc`

### 代码质量要求
- **类型安全**: 使用Python类型提示和TypeScript
- **测试覆盖**: 单元测试、集成测试、API测试
- **代码规范**: 遵循PEP 8、ESLint、Prettier
- **文档**: 重要函数和类需要docstring

### 环境配置
- 使用`.env`文件管理环境变量
- 敏感信息通过环境变量注入，不硬编码
- 不同环境使用不同配置：development、testing、production

## 部署和运维

### 部署
- 使用uv工具给当前项目创建python虚拟环境，并安装相关依赖

### Docker部署
- 后端：`Dockerfile.backend`，基于Python 3.12-slim
- 前端：`frontend/Dockerfile`，多阶段构建，Nginx服务
- 数据库：PostgreSQL 16官方镜像
- 缓存：Redis 7官方镜像

### 健康检查
- 后端：`/health`端点，检查数据库连接
- 前端：Nginx服务状态检查
- 数据库：PostgreSQL健康检查
- Redis：Redis服务状态检查

### 监控和日志
- 结构化日志输出，支持JSON格式
- 集成Sentry错误监控
- 性能监控：处理时间、内存使用、数据库查询
- 支持OpenTelemetry追踪

## 常见问题

### 数据库连接问题
- 检查PostgreSQL服务是否启动
- 验证连接字符串和认证信息
- 确保数据库端口5432可访问

### 调度算法问题
- 检查约束配置是否正确
- 验证输入数据的完整性
- 查看求解器日志和状态信息

### 前端构建问题
- 确保Node.js版本≥18.0.0
- 清理node_modules并重新安装
- 检查TypeScript类型错误
- 前端使用 ant design组件

### 多租户问题
- 确保所有API请求包含正确的tenant_id
- 验证数据隔离是否正确
- 检查租户权限配置
