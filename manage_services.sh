#!/bin/bash

# Edusched服务管理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务配置
POSTGRES_CONTAINER="edusched-postgres"
REDIS_CONTAINER="edusched-redis"
APP_PORT=8000

# 打印带颜色的消息
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Podman是否安装
check_podman() {
    if ! command -v podman &> /dev/null; then
        print_error "Podman未安装，请先安装Podman"
        exit 1
    fi
    print_success "Podman已安装: $(podman --version)"
}

# 启动数据库服务
start_database_services() {
    print_status "启动数据库服务..."
    
    # 启动PostgreSQL
    if ! podman ps --format "{{.Names}}" | grep -q "^${POSTGRES_CONTAINER}$"; then
        print_status "启动PostgreSQL容器..."
        podman run -d --name ${POSTGRES_CONTAINER} --network host \
            -e POSTGRES_DB=edusched \
            -e POSTGRES_USER=edusched \
            -e POSTGRES_PASSWORD=edusched123 \
            docker.io/library/postgres:16-alpine
        print_success "PostgreSQL容器已启动"
    else
        print_warning "PostgreSQL容器已在运行"
    fi
    
    # 启动Redis
    if ! podman ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER}$"; then
        print_status "启动Redis容器..."
        podman run -d --name ${REDIS_CONTAINER} --network host \
            docker.io/library/redis:7-alpine \
            redis-server --appendonly yes --requirepass edusched123
        print_success "Redis容器已启动"
    else
        print_warning "Redis容器已在运行"
    fi
    
    # 等待服务启动
    print_status "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    check_database_services
}

# 检查数据库服务状态
check_database_services() {
    print_status "检查数据库服务状态..."
    
    # 检查PostgreSQL
    if podman exec ${POSTGRES_CONTAINER} pg_isready -U edusched -d edusched &> /dev/null; then
        print_success "PostgreSQL服务正常"
    else
        print_error "PostgreSQL服务异常"
        return 1
    fi
    
    # 检查Redis
    if podman exec ${REDIS_CONTAINER} redis-cli -a edusched123 --raw incr ping &> /dev/null; then
        print_success "Redis服务正常"
    else
        print_error "Redis服务异常"
        return 1
    fi
}

# 启动Python应用
start_python_app() {
    print_status "启动Python应用..."
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        print_error "虚拟环境不存在，请先创建虚拟环境"
        return 1
    fi
    
    # 检查应用是否已在运行
    if pgrep -f "start_app.py" > /dev/null; then
        print_warning "Python应用已在运行"
        return 0
    fi
    
    # 启动应用
    cd /workspace
    source venv/bin/activate
    nohup python start_app.py > app.log 2>&1 &
    
    # 等待应用启动
    print_status "等待应用启动..."
    sleep 15
    
    # 检查应用状态
    if curl -f http://localhost:${APP_PORT}/health &> /dev/null; then
        print_success "Python应用启动成功"
        print_success "应用地址: http://localhost:${APP_PORT}"
        print_success "API文档: http://localhost:${APP_PORT}/docs"
    else
        print_error "Python应用启动失败"
        return 1
    fi
}

# 停止所有服务
stop_all_services() {
    print_status "停止所有服务..."
    
    # 停止Python应用
    if pgrep -f "start_app.py" > /dev/null; then
        print_status "停止Python应用..."
        pkill -f "start_app.py"
        print_success "Python应用已停止"
    fi
    
    # 停止容器
    if podman ps --format "{{.Names}}" | grep -q "^${POSTGRES_CONTAINER}$"; then
        print_status "停止PostgreSQL容器..."
        podman stop ${POSTGRES_CONTAINER}
        print_success "PostgreSQL容器已停止"
    fi
    
    if podman ps --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER}$"; then
        print_status "停止Redis容器..."
        podman stop ${REDIS_CONTAINER}
        print_success "Redis容器已停止"
    fi
}

# 显示服务状态
show_status() {
    print_status "服务状态:"
    echo "----------------------------------------"
    
    # 检查Python应用
    if pgrep -f "start_app.py" > /dev/null; then
        print_success "Python应用: 运行中"
        echo "  地址: http://localhost:${APP_PORT}"
        echo "  文档: http://localhost:${APP_PORT}/docs"
    else
        print_error "Python应用: 未运行"
    fi
    
    echo ""
    
    # 检查容器状态
    print_status "容器状态:"
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    
    # 检查网络连接
    print_status "网络连接:"
    if curl -f http://localhost:${APP_PORT}/health &> /dev/null; then
        print_success "应用健康检查: 正常"
    else
        print_error "应用健康检查: 失败"
    fi
}

# 清理所有资源
cleanup() {
    print_status "清理所有资源..."
    
    # 停止服务
    stop_all_services
    
    # 删除容器
    if podman ps -a --format "{{.Names}}" | grep -q "^${POSTGRES_CONTAINER}$"; then
        podman rm ${POSTGRES_CONTAINER}
        print_success "PostgreSQL容器已删除"
    fi
    
    if podman ps -a --format "{{.Names}}" | grep -q "^${REDIS_CONTAINER}$"; then
        podman rm ${REDIS_CONTAINER}
        print_success "Redis容器已删除"
    fi
    
    # 清理日志
    if [ -f "app.log" ]; then
        rm app.log
        print_success "应用日志已清理"
    fi
}

# 显示帮助信息
show_help() {
    echo "Edusched服务管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动所有服务"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  status    显示服务状态"
    echo "  cleanup   清理所有资源"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start    # 启动所有服务"
    echo "  $0 status   # 查看服务状态"
    echo "  $0 stop     # 停止所有服务"
}

# 主函数
main() {
    check_podman
    
    case "${1:-help}" in
        start)
            start_database_services
            start_python_app
            print_success "所有服务启动完成！"
            show_status
            ;;
        stop)
            stop_all_services
            print_success "所有服务已停止"
            ;;
        restart)
            print_status "重启所有服务..."
            stop_all_services
            sleep 5
            start_database_services
            start_python_app
            print_success "所有服务重启完成！"
            show_status
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            print_success "清理完成"
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@"