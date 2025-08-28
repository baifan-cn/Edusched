# EduSched 容器化部署指南

## 概述

EduSched是一个智能教育调度平台，使用容器化技术进行部署。本指南将帮助您使用Podman和Docker Compose成功部署整个系统。

## 系统要求

- Ubuntu 20.04+ 或其他支持Podman的Linux发行版
- 至少4GB RAM
- 至少10GB可用磁盘空间
- 网络连接（用于下载镜像）

## 安装依赖

### 1. 安装Podman和Podman Compose

```bash
# 更新包列表
sudo apt update

# 安装Podman和Podman Compose
sudo apt install -y podman podman-compose

# 验证安装
podman --version
podman-compose --version
```

### 2. 配置网络（如果需要）

如果遇到网络问题，可能需要创建网络设备：

```bash
sudo mkdir -p /dev/net
sudo mknod /dev/net/tun c 10 200
sudo chmod 666 /dev/net/tun
```

## 快速启动

### 方法1：使用启动脚本（推荐）

```bash
# 给脚本添加执行权限
chmod +x start-edusched.sh

# 运行启动脚本
./start-edusched.sh
```

### 方法2：手动启动

```bash
# 启动所有服务
podman-compose -f docker-compose-final.yml up -d

# 查看服务状态
podman ps

# 查看日志
podman-compose -f docker-compose-final.yml logs -f
```

## 服务架构

系统包含以下服务：

| 服务 | 端口 | 描述 |
|------|------|------|
| PostgreSQL | 5432 | 主数据库 |
| Redis | 6379 | 缓存和队列 |
| Backend API | 8000 | FastAPI后端服务 |
| Frontend | 3000 | React前端应用 |
| Nginx | 80/443 | 反向代理和负载均衡 |

## 配置说明

### 环境变量

主要配置通过环境变量设置：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=edusched
DB_USER=edusched
DB_PASSWORD=edusched123

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=edusched123

# 安全配置
SECURITY_SECRET_KEY=your-super-secret-key-here-make-it-long-enough-for-validation

# OIDC配置
OIDC_ISSUER=http://localhost:8080/auth/realms/edusched
OIDC_CLIENT_ID=edusched-client
OIDC_CLIENT_SECRET=edusched-secret
```

### 网络配置

使用`network_mode: host`避免网络配置问题，所有服务通过localhost通信。

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看容器日志
   podman logs <container-name>
   
   # 重新构建镜像
   podman build --network=host -t edusched-backend -f Dockerfile.backend .
   ```

2. **网络连接问题**
   ```bash
   # 检查网络设备
   ls -la /dev/net/
   
   # 重新创建网络设备
   sudo mkdir -p /dev/net && sudo mknod /dev/net/tun c 10 200
   ```

3. **权限问题**
   ```bash
   # 检查Podman权限
   podman ps
   
   # 如果失败，使用sudo
   sudo podman ps
   ```

### 日志查看

```bash
# 查看所有服务日志
podman-compose -f docker-compose-final.yml logs -f

# 查看特定服务日志
podman-compose -f docker-compose-final.yml logs -f backend
podman-compose -f docker-compose-final.yml logs -f frontend
```

## 维护操作

### 更新服务

```bash
# 停止服务
podman-compose -f docker-compose-final.yml down

# 重新构建镜像
podman build --network=host -t edusched-backend -f Dockerfile.backend .
podman build --network=host -t edusched-frontend -f frontend/Dockerfile ./frontend

# 重新启动服务
podman-compose -f docker-compose-final.yml up -d
```

### 备份数据

```bash
# 备份PostgreSQL数据
podman exec edusched-postgres pg_dump -U edusched edusched > backup.sql

# 备份Redis数据
podman exec edusched-redis redis-cli -a edusched123 SAVE
```

### 清理资源

```bash
# 停止所有服务
podman-compose -f docker-compose-final.yml down

# 清理容器
podman container prune -f

# 清理镜像
podman image prune -f

# 清理卷
podman volume prune -f
```

## 性能优化

### 资源限制

可以在docker-compose文件中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### 数据库优化

```bash
# 调整PostgreSQL配置
podman exec -it edusched-postgres psql -U edusched -d edusched

# 在PostgreSQL中执行
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
```

## 监控和健康检查

### 健康检查端点

- 后端健康检查：`http://localhost:8000/health`
- 前端健康检查：`http://localhost:3000/health`
- 数据库健康检查：通过PostgreSQL连接测试

### 监控命令

```bash
# 查看容器状态
podman ps

# 查看资源使用
podman stats

# 查看网络连接
podman network ls
```

## 安全建议

1. **更改默认密码**：修改数据库和Redis的默认密码
2. **限制网络访问**：在生产环境中限制端口访问
3. **使用HTTPS**：配置SSL证书启用HTTPS
4. **定期更新**：保持容器镜像和依赖包的最新版本

## 支持

如果遇到问题，请：

1. 查看容器日志
2. 检查系统资源使用情况
3. 验证网络配置
4. 参考故障排除部分

## 许可证

本项目采用MIT许可证。详见LICENSE文件。