#!/bin/bash

# Edusched 服务监控脚本
# 使用方法: ./scripts/monitor.sh

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

echo "🔍 Edusched 服务状态监控"
echo "========================="

# 检查Docker服务状态
echo ""
echo "🐳 Docker 服务状态："
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# 检查资源使用情况
echo ""
echo "💾 资源使用情况："
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# 检查日志
echo ""
echo "📋 最近的错误日志："
for service in postgres redis backend frontend; do
    echo "--- $service 最近5条错误日志 ---"
    docker-compose logs --tail=5 "$service" | grep -i "error\|exception\|failed" || echo "  无错误日志"
    echo ""
done

# 健康检查
echo ""
echo "🏥 健康检查："
services=("postgres:5432" "redis:6379" "backend:8000" "frontend:8080")

for service_port in "${services[@]}"; do
    service=$(echo "$service_port" | cut -d: -f1)
    port=$(echo "$service_port" | cut -d: -f2)

    container_name=$(docker-compose ps -q "$service")
    if [ -n "$container_name" ]; then
        if docker exec "$container_name" nc -z localhost "$port" 2>/dev/null; then
            echo "✅ $service 服务端口 $port 可访问"
        else
            echo "❌ $service 服务端口 $port 不可访问"
        fi
    else
        echo "❌ $service 服务未运行"
    fi
done

# 检查磁盘空间
echo ""
echo "💿 磁盘空间使用情况："
df -h | grep -E "(Filesystem|/dev/sda|/dev/vda)"

# 检查内存使用
echo ""
echo "🧠 内存使用情况："
free -h

echo ""
echo "📊 监控完成！"