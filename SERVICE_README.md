# Edusched 服务管理指南

## 概述

本项目使用 Podman 作为容器引擎来运行数据库服务，并使用 Python 虚拟环境运行 FastAPI 应用。

## 系统要求

- Ubuntu 25.04 或更高版本
- Python 3.13+
- Podman 5.4+

## 快速开始

### 1. 启动所有服务

```bash
./manage_services.sh start
```

这将启动：
- PostgreSQL 数据库容器
- Redis 缓存容器  
- Python FastAPI 应用

### 2. 检查服务状态

```bash
./manage_services.sh status
```

### 3. 停止所有服务

```bash
./manage_services.sh stop
```

### 4. 重启所有服务

```bash
./manage_services.sh restart
```

### 5. 清理所有资源

```bash
./manage_services.sh cleanup
```

## 服务详情

### 数据库服务

- **PostgreSQL**: 端口 5432
  - 数据库名: `edusched`
  - 用户名: `edusched`
  - 密码: `edusched123`

- **Redis**: 端口 6379
  - 密码: `edusched123`

### 应用服务

- **FastAPI 应用**: 端口 8000
  - 主应用: http://localhost:8000
  - API 文档: http://localhost:8000/docs
  - 健康检查: http://localhost:8000/health

## 手动管理

### 启动数据库容器

```bash
# PostgreSQL
podman run -d --name edusched-postgres --network host \
  -e POSTGRES_DB=edusched \
  -e POSTGRES_USER=edusched \
  -e POSTGRES_PASSWORD=edusched123 \
  docker.io/library/postgres:16-alpine

# Redis
podman run -d --name edusched-redis --network host \
  docker.io/library/redis:7-alpine \
  redis-server --appendonly yes --requirepass edusched123
```

### 启动 Python 应用

```bash
# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=edusched
export DB_USER=edusched
export DB_PASSWORD=edusched123
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=edusched123
export SECURITY_SECRET_KEY=your-super-secret-key-here-make-it-long-enough
export OIDC_ISSUER=http://localhost:8080/auth/realms/edusched
export OIDC_CLIENT_ID=edusched-client
export OIDC_CLIENT_SECRET=edusched-secret

# 启动应用
python start_app.py
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口使用情况
   sudo netstat -tlnp | grep :8000
   sudo netstat -tlnp | grep :5432
   sudo netstat -tlnp | grep :6379
   ```

2. **容器启动失败**
   ```bash
   # 查看容器日志
   podman logs edusched-postgres
   podman logs edusched-redis
   ```

3. **应用启动失败**
   ```bash
   # 查看应用日志
   tail -f app.log
   ```

4. **数据库连接失败**
   ```bash
   # 测试数据库连接
   podman exec edusched-postgres pg_isready -U edusched -d edusched
   podman exec edusched-redis redis-cli -a edusched123 ping
   ```

### 重置环境

如果需要完全重置环境：

```bash
# 停止并删除所有容器
./manage_services.sh cleanup

# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 重新启动服务
./manage_services.sh start
```

## 开发模式

在开发模式下，应用会自动重载代码更改：

```bash
# 启动开发模式（已包含在 start_app.py 中）
python start_app.py
```

## 生产部署

对于生产环境，建议：

1. 使用环境变量文件 (.env) 管理配置
2. 配置反向代理 (Nginx)
3. 使用进程管理器 (systemd, supervisor)
4. 配置日志轮转
5. 设置监控和告警

## 支持

如果遇到问题，请检查：

1. 系统日志
2. 容器日志
3. 应用日志
4. 网络连接状态
5. 资源使用情况

## 更新日志

- **v1.0.0**: 初始版本，支持基本的服务管理功能