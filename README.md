# Edusched - 智能教育调度平台

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-4fc08d.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Edusched是一个智能教育调度平台，旨在为学校生成可行且优化的课程表。系统使用先进的约束满足和优化算法，确保生成的课程表满足所有硬约束，并尽可能优化软约束。

## ✨ 特性

- 🎯 **智能调度算法**: 使用OR-Tools CP-SAT求解器实现高效的课程表生成
- 🔒 **多租户支持**: 支持多所学校独立使用，数据完全隔离
- 🏫 **多校区管理**: 支持跨校区约束和资源管理
- 📊 **实时进度监控**: 调度过程可视化，支持暂停、恢复和取消
- 🎨 **现代化UI**: 基于Vue 3 + Element Plus的响应式界面
- 🚀 **高性能**: 异步架构，支持大规模数据和高并发访问
- 🔐 **安全可靠**: 支持OIDC认证，完整的RBAC权限控制

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue 3)   │    │   后端 (FastAPI) │    │   数据库 (PG)   │
│                 │◄──►│                 │◄──►│                 │
│  Element Plus   │    │  SQLAlchemy     │    │   PostgreSQL    │
│  ECharts       │    │  OR-Tools       │    │   Redis         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   调度引擎      │
                    │                 │
                    │  CP-SAT + LS    │
                    │  约束验证       │
                    └─────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

### 使用Docker Compose（推荐）

1. **克隆项目**
```bash
git clone https://github.com/your-org/edusched.git
cd edusched
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **访问应用**
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 本地开发

1. **后端设置**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install uv
uv pip install -e .

# 设置环境变量
cp .env.example .env
# 编辑.env文件配置数据库等

# 启动后端
uvicorn edusched.api.main:app --reload
```

2. **前端设置**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📚 使用指南

### 1. 学校管理
- 创建学校基本信息
- 配置校区和建筑
- 设置学年和学期

### 2. 基础数据管理
- 添加教师信息
- 创建课程和教学段
- 配置教室和时段

### 3. 时间表生成
- 创建时间表项目
- 配置约束条件
- 启动调度算法
- 监控生成进度

### 4. 结果优化
- 查看约束违反情况
- 调整约束权重
- 重新优化时间表

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DB_HOST` | 数据库主机 | localhost |
| `DB_PORT` | 数据库端口 | 5432 |
| `DB_NAME` | 数据库名称 | edusched |
| `REDIS_HOST` | Redis主机 | localhost |
| `SECURITY_SECRET_KEY` | JWT密钥 | 必须设置 |
| `OIDC_ISSUER` | OIDC发行者 | 必须设置 |

### 约束配置

系统支持以下类型的约束：

**硬约束（必须满足）**
- 教师时间冲突
- 教室占用冲突
- 班级时间冲突
- 教师可用性

**软约束（尽量满足）**
- 教师偏好时间段
- 课程分布均匀性
- 教室利用率
- 教师工作负荷平衡

## 🧪 测试

```bash
# 后端测试
pytest

# 前端测试
cd frontend
npm run test

# 端到端测试
npm run test:e2e
```

## 📊 性能基准

- **小规模**: 100个教学段，50个时段 → 生成时间 < 30秒
- **中规模**: 500个教学段，100个时段 → 生成时间 < 2分钟
- **大规模**: 1000个教学段，200个时段 → 生成时间 < 5分钟

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OR-Tools](https://developers.google.com/optimization) - 约束优化求解器
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库

## 📞 联系我们

- 项目主页: https://github.com/your-org/edusched
- 问题反馈: https://github.com/your-org/edusched/issues
- 邮箱: team@edusched.com

---

如果这个项目对你有帮助，请给我们一个 ⭐️ ！
