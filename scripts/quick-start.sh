#!/bin/bash

# Edusched 快速启动脚本
# 使用方法: ./scripts/quick-start.sh

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

echo "🚀 Edusched 快速启动"
echo "=================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "❌ Docker 未运行，请启动 Docker"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down --remove-orphans

# 构建和启动服务
echo "🏗️  构建和启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "🎉 启动完成！"
echo "============="
echo ""
echo "🌐 访问地址："
echo "  前端应用: http://localhost:3000"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "🛠️  管理命令："
echo "  查看日志: docker-compose logs -f [service]"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart [service]"
echo ""
echo "📊 监控命令："
echo "  服务状态: docker-compose ps"
echo "  资源使用: docker stats"
echo "  健康检查: ./scripts/monitor.sh"
echo ""
echo "🔧 如果遇到问题，请查看日志："
echo "  docker-compose logs --tail=100 -f"