# Docker Compose 问题解决方案

## 问题描述

在尝试使用 `docker compose` 启动服务时遇到以下问题：

1. **Docker守护进程问题**: Docker守护进程无法正常启动或连接
2. **权限问题**: 用户无法访问Docker socket
3. **网络配置问题**: 容器网络配置异常

## 解决方案

### 方案1: 使用Podman + Python混合方案 (推荐)

由于Docker环境存在根本性问题，我们采用混合方案：
- 使用Podman运行数据库服务（PostgreSQL + Redis）
- 直接运行Python FastAPI应用

#### 快速启动

```bash
# 启动所有服务
./start_services.sh start

# 检查服务状态
./start_services.sh status

# 停止所有服务
./start_services.sh stop

# 重启所有服务
./start_services.sh restart

# 清理所有资源
./start_services.sh cleanup
```

#### 服务详情

- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379  
- **FastAPI应用**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 方案2: 修复Docker环境

如果坚持要使用Docker，需要解决以下问题：

#### 1. 检查Docker服务状态

```bash
sudo service docker status
sudo systemctl status docker
```

#### 2. 重新启动Docker服务

```bash
sudo service docker stop
sudo pkill -9 -f docker
sudo rm -f /var/run/docker-ssd.pid /var/run/docker.sock
sudo service docker start
```

#### 3. 检查用户权限

```bash
# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录或重新加载组权限
newgrp docker
```

#### 4. 测试Docker

```bash
docker run hello-world
```

### 方案3: 使用Docker Desktop

如果系统支持，可以安装Docker Desktop：

```bash
# 下载并安装Docker Desktop
# 参考: https://docs.docker.com/desktop/install/ubuntu/
```

## 当前状态

✅ **服务已成功启动并运行**
- PostgreSQL数据库容器运行正常
- Redis缓存容器运行正常  
- FastAPI应用运行正常
- 所有服务健康检查通过

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo netstat -tlnp | grep :5432
   sudo netstat -tlnp | grep :6379
   ```

2. **容器启动失败**
   ```bash
   podman logs edusched-postgres
   podman logs edusched-redis
   ```

3. **应用启动失败**
   ```bash
   # 检查进程
   ps aux | grep start_app
   
   # 检查端口
   netstat -tlnp | grep :8000
   ```

4. **数据库连接失败**
   ```bash
   # 测试PostgreSQL
   podman exec edusched-postgres pg_isready -U edusched -d edusched
   
   # 测试Redis
   podman exec edusched-redis redis-cli -a edusched123 ping
   ```

### 重置环境

```bash
# 完全清理
./start_services.sh cleanup

# 重新启动
./start_services.sh start
```

## 文件说明

- `start_services.sh` - 主要的服务管理脚本
- `start_app.py` - Python应用启动脚本
- `podman-compose.yml` - Podman compose配置（备用）
- `docker-compose.yml` - Docker compose配置（有问题）

## 建议

1. **开发环境**: 使用 `./start_services.sh` 脚本
2. **生产环境**: 考虑使用Docker Desktop或修复Docker环境
3. **CI/CD**: 使用Podman作为Docker的替代品

## 技术支持

如果遇到问题：

1. 检查服务状态: `./start_services.sh status`
2. 查看容器日志: `podman logs <container_name>`
3. 检查系统资源: `top`, `df`, `free`
4. 检查网络连接: `curl -v http://localhost:8000/health`

---

**注意**: 当前推荐使用方案1（Podman + Python混合方案），因为它更稳定且已经验证可用。