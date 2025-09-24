# Edusched Docker 部署指南

## 🚀 快速开始

### 开发环境一键启动

```bash
# 启动所有服务（包括前端）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service]
```

### 生产环境部署

```bash
# 1. 复制环境变量模板
cp .env.prod.template .env.production

# 2. 编辑环境变量
vim .env.production

# 3. 部署到生产环境
./scripts/deploy.sh prod
```

## 📋 服务说明

| 服务 | 端口 | 说明 | 健康检查 |
|------|------|------|----------|
| postgres | 5432 | PostgreSQL数据库 | ✅ |
| redis | 6380 | Redis缓存 | ✅ |
| backend | 8000 | 后端API服务 | ✅ |
| frontend | 3000 | 前端Vue应用 | ✅ |

## 🔗 访问地址

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: localhost:5432

## 🛠️ 管理命令

### 基本操作
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启指定服务
docker-compose restart [service]

# 查看实时日志
docker-compose logs -f [service]

# 进入容器
docker-compose exec [service] bash
```

### 监控和健康检查
```bash
# 查看所有服务状态
docker-compose ps

# 执行健康检查
./scripts/monitor.sh

# 查看资源使用情况
docker stats
```

### 开发环境
```bash
# 重新构建并启动
docker-compose up -d --build

# 仅启动后端服务
docker-compose up -d backend postgres redis

# 仅启动前端服务
docker-compose up -d frontend
```

## 🔧 配置说明

### 环境变量

#### 后端环境变量
- `DB_HOST`: 数据库主机名
- `DB_PASSWORD`: 数据库密码
- `REDIS_PASSWORD`: Redis密码
- `SECURITY_SECRET_KEY`: 安全密钥

#### 前端环境变量
- `VITE_API_BASE_URL`: API基础URL
- `VITE_APP_TITLE`: 应用标题
- `VITE_APP_VERSION`: 应用版本

### Docker Compose 配置

#### 开发环境 (docker-compose.yml)
- 适用于开发调试
- 包含完整的开发工具链
- 支持热重载

#### 生产环境 (docker-compose.prod.yml)
- 适用于生产部署
- 包含Nginx反向代理
- 支持HTTPS和负载均衡
- 包含资源限制和监控

## 🐛 故障排除

### 常见问题

1. **前端无法访问后端API**
   ```bash
   # 检查后端服务状态
   docker-compose logs backend

   # 检查网络连接
   docker-compose exec frontend curl http://backend:8000/health
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose logs postgres

   # 检查数据库连接
   docker-compose exec backend python -c "from edusched.infrastructure.database.connection import get_db; print('Database connected')"
   ```

3. **前端构建失败**
   ```bash
   # 查看构建日志
   docker-compose logs frontend

   # 重新构建前端
   docker-compose build --no-cache frontend
   ```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs [service]

# 查看最近100行日志
docker-compose logs --tail=100 [service]

# 实时查看日志
docker-compose logs -f [service]
```

## 📊 监控和维护

### 资源监控
```bash
# 查看容器资源使用情况
docker stats

# 查看磁盘使用情况
df -h

# 查看内存使用情况
free -h
```

### 备份和恢复
```bash
# 备份数据库
docker-compose exec postgres pg_dump -U edusched edusched > backup.sql

# 恢复数据库
docker-compose exec -i postgres psql -U edusched edusched < backup.sql

# 备份Redis数据
docker-compose exec redis redis-cli --rdb backup.rdb
```

## 🔄 更新和升级

### 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重新构建和启动
docker-compose up -d --build

# 清理旧镜像
docker image prune -f
```

### 更新依赖
```bash
# 更新后端依赖
docker-compose exec backend pip install -r requirements.txt

# 更新前端依赖
docker-compose build --no-cache frontend
```

## 🔒 安全建议

1. **生产环境安全**
   - 使用强密码和密钥
   - 启用HTTPS
   - 配置防火墙规则
   - 定期更新依赖

2. **环境变量管理**
   - 不要在代码中硬编码敏感信息
   - 使用环境变量文件
   - 定期轮换密钥

3. **网络安全**
   - 使用私有网络
   - 限制端口暴露
   - 配置访问控制

## 📝 开发指南

### 本地开发
```bash
# 启动开发环境
docker-compose up -d

# 前端开发（热重载）
cd frontend && npm run dev

# 后端开发
uvicorn edusched.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 测试
```bash
# 运行后端测试
docker-compose exec backend pytest

# 运行前端测试
docker-compose exec frontend npm test

# 运行集成测试
docker-compose exec backend pytest tests/integration/
```

## 📞 支持

如果遇到问题，请：

1. 查看日志文件
2. 检查服务状态
3. 参考故障排除部分
4. 联系技术支持

---

*最后更新时间: 2024-01-24*