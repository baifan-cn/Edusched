#!/bin/bash

echo "启动EduSched服务..."

# 检查并安装PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "安装PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
else
    echo "PostgreSQL已安装"
    sudo systemctl start postgresql
fi

# 检查并安装Redis
if ! command -v redis-server &> /dev/null; then
    echo "安装Redis..."
    sudo apt install -y redis-server
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
else
    echo "Redis已安装"
    sudo systemctl start redis-server
fi

# 创建数据库和用户
echo "配置数据库..."
sudo -u postgres psql -c "CREATE DATABASE edusched;" 2>/dev/null || echo "数据库已存在"
sudo -u postgres psql -c "CREATE USER edusched WITH PASSWORD 'edusched123';" 2>/dev/null || echo "用户已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE edusched TO edusched;" 2>/dev/null || echo "权限已设置"

# 运行数据库初始化脚本
echo "初始化数据库..."
psql -h localhost -U edusched -d edusched -f scripts/init-db.sql

# 配置Redis密码
echo "配置Redis..."
sudo sed -i 's/# requirepass foobared/requirepass edusched123/' /etc/redis/redis.conf
sudo systemctl restart redis-server

echo "服务启动完成！"
echo "PostgreSQL: localhost:5432"
echo "Redis: localhost:6379"
echo ""
echo "现在可以启动后端和前端服务了"