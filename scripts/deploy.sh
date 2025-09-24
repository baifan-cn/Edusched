#!/bin/bash

# Edusched 生产环境部署脚本
# 使用方法: ./scripts/deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

echo "🚀 开始部署 Edusched 到 $ENVIRONMENT 环境..."

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 进入项目目录
cd "$PROJECT_ROOT"

# 清理旧容器和镜像
echo "🧹 清理旧的容器和镜像..."
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml down --remove-orphans
else
    docker-compose down --remove-orphans
fi

# 构建镜像
echo "🏗️  构建 Docker 镜像..."
if [ "$ENVIRONMENT" = "prod" ]; then
    # 生产环境需要环境变量文件
    if [ ! -f .env.production ]; then
        echo "❌ 生产环境需要 .env.production 文件"
        echo "请复制 .env.prod.template 为 .env.production 并填写实际值"
        exit 1
    fi

    docker-compose -f docker-compose.prod.yml build --no-cache
else
    docker-compose build --no-cache
fi

# 启动服务
echo "🎯 启动服务..."
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    docker-compose up -d
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml ps
else
    docker-compose ps
fi

# 健康检查
echo "🏥 执行健康检查..."
for service in postgres redis backend frontend; do
    if [ "$ENVIRONMENT" = "prod" ]; then
        container_name="edusched-${service}-prod"
    else
        container_name="edusched-${service}"
    fi

    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name.*Up"; then
        echo "✅ $service 服务运行正常"
    else
        echo "❌ $service 服务启动失败"
        docker-compose logs "$service"
        exit 1
    fi
done

# 显示访问地址
echo ""
echo "🎉 部署完成！"
echo ""
echo "访问地址："
echo "  - 前端: http://localhost:3000"
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/docs"
echo ""
echo "管理命令："
echo "  - 查看日志: docker-compose logs -f [service]"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart [service]"
echo ""
echo "🔧 如果遇到问题，请检查日志："
echo "  docker-compose logs --tail=100 -f"