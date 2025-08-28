#!/bin/bash

echo "🚀 启动EduSched智能教育调度平台..."

# 检查Podman是否可用
if ! command -v podman &> /dev/null; then
    echo "❌ Podman未安装，请先安装Podman"
    exit 1
fi

if ! command -v podman-compose &> /dev/null; then
    echo "❌ Podman Compose未安装，请先安装Podman Compose"
    exit 1
fi

echo "✅ Podman和Podman Compose已就绪"

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p nginx/ssl
mkdir -p scripts

# 检查并创建数据库初始化脚本
if [ ! -f "scripts/init-db.sql" ]; then
    echo "📝 创建数据库初始化脚本..."
    cat > scripts/init-db.sql << 'EOF'
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建课程表
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    credits INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建时间表
CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
EOF
fi

# 检查并创建nginx配置
if [ ! -f "nginx/nginx.conf" ]; then
    echo "📝 创建nginx主配置..."
    cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_size "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    include /etc/nginx/conf.d/*.conf;
}
EOF
fi

if [ ! -f "nginx/conf.d/default.conf" ]; then
    echo "📝 创建nginx站点配置..."
    cat > nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # 健康检查
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
    }

    # 错误页面
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF
fi

# 停止现有服务
echo "🛑 停止现有服务..."
podman-compose -f docker-compose-final.yml down 2>/dev/null || true

# 启动服务
echo "🚀 启动服务..."
podman-compose -f docker-compose-final.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
podman ps

echo ""
echo "📊 服务状态检查:"
echo "  PostgreSQL: $(curl -s http://localhost:5432 >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"
echo "  Redis: $(redis-cli -h localhost -p 6379 -a edusched123 ping 2>/dev/null | grep -q PONG && echo '✅ 运行中' || echo '❌ 未运行')"
echo "  Backend: $(curl -s http://localhost:8000/health >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"
echo "  Frontend: $(curl -s http://localhost:3000 >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"
echo "  Nginx: $(curl -s http://localhost:80 >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"

echo ""
echo "🎉 EduSched启动完成！"
echo "  📱 前端: http://localhost:3000"
echo "  🔧 后端API: http://localhost:8000"
echo "  📚 API文档: http://localhost:8000/docs"
echo "  🌐 Nginx代理: http://localhost:80"
echo ""
echo "💡 使用以下命令查看日志:"
echo "  podman-compose -f docker-compose-final.yml logs -f"
echo ""
echo "🛑 使用以下命令停止服务:"
echo "  podman-compose -f docker-compose-final.yml down"