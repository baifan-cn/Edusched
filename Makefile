# Edusched Makefile
# 提供便捷的测试和开发命令

.PHONY: help test test-unit test-integration test-e2e test-performance test-api test-database test-tenant test-scheduling test-frontend test-all coverage clean lint format setup install-deps dev-build docker-test ci-test migrate-up migrate-down migrate-new migrate-history migrate-current migrate-check db-init db-up db-down

# 默认目标
help:
	@echo "Edusched 开发和测试命令"
	@echo ""
	@echo "测试命令:"
	@echo "  test-unit              运行单元测试"
	@echo "  test-integration       运行集成测试"
	@echo "  test-e2e               运行E2E测试"
	@echo "  test-performance       运行性能测试"
	@echo "  test-api               运行API测试"
	@echo "  test-database          运行数据库测试"
	@echo "  test-tenant            运行多租户测试"
	@echo "  test-scheduling        运行调度测试"
	@echo "  test-frontend          运行前端测试"
	@echo "  test-all               运行所有测试"
	@echo "  coverage               生成覆盖率报告"
	@echo ""
	@echo "数据库迁移:"
	@echo "  migrate-up          升级数据库到最新版本"
	@echo "  migrate-down REV    降级数据库到指定版本"
	@echo "  migrate-new MSG     创建新的迁移文件"
	@echo "  migrate-history     显示迁移历史"
	@echo "  migrate-current     显示当前数据库版本"
	@echo "  migrate-check       检查迁移状态"
	@echo ""
	@echo "数据库管理:"
	@echo "  db-init             初始化数据库（创建数据库）"
	@echo "  db-up               启动数据库服务"
	@echo "  db-down             停止数据库服务"
	@echo ""
	@echo "开发环境:"
	@echo "  setup                  设置开发环境"
	@echo "  install-deps           安装依赖"
	@echo "  dev-build              开发构建"
	@echo "  lint                   运行代码检查"
	@echo "  format                 格式化代码"
	@echo "  clean                  清理测试产物"
	@echo ""
	@echo "Docker:"
	@echo "  docker-test            Docker中运行测试"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci-test                CI测试流程"
	@echo ""
	@echo "使用示例:"
	@echo "  make test-unit"
	@echo "  make test-all coverage"
	@echo "  make clean test-all"
	@echo "  make migrate-new MSG='添加用户表'"
	@echo "  make migrate-down REV=abc123"

# 数据库迁移命令
migrate-up:
	python3 scripts/migrate.py upgrade

migrate-down:
ifndef REV
	$(error REV参数是必需的。用法: make migrate-down REV=<revision>)
endif
	python3 scripts/migrate.py downgrade $(REV)

migrate-new:
ifndef MSG
	$(error MSG参数是必需的。用法: make migrate-new MSG='<迁移描述>')
endif
	python3 scripts/migrate.py revision --message "$(MSG)" --autogenerate

migrate-history:
	python3 scripts/migrate.py history --verbose

migrate-current:
	python3 scripts/migrate.py current

migrate-check:
	python3 scripts/migrate.py check

# 数据库管理命令
db-init:
	@echo "创建数据库 edusched..."
	createdb -U edusched -h localhost -p 5432 edusched || echo "数据库可能已存在"

db-up:
	docker-compose up -d postgres redis

db-down:
	docker-compose stop postgres redis

# 测试命令
test-unit:
	python tests/scripts/run_tests.py --unit --coverage

test-integration:
	python tests/scripts/run_tests.py --integration --coverage

test-e2e:
	python tests/scripts/run_tests.py --e2e

test-performance:
	python tests/scripts/run_tests.py --performance

test-api:
	python tests/scripts/run_tests.py --api --coverage

test-database:
	python tests/scripts/run_tests.py --database --coverage

test-tenant:
	python tests/scripts/run_tests.py --tenant --coverage

test-scheduling:
	python tests/scripts/run_tests.py --scheduling --coverage

test-frontend:
	python tests/scripts/run_tests.py --frontend --coverage

test-all:
	python tests/scripts/run_tests.py --all --coverage

coverage:
	python tests/scripts/run_tests.py --coverage

# 代码质量
lint:
	python tests/scripts/run_tests.py --lint

format:
	python tests/scripts/run_tests.py --format

clean:
	python tests/scripts/run_tests.py --clean

# 开发环境
setup:
	@echo "设置开发环境..."
	python -m pip install --upgrade pip
	python -m pip install -e .[dev,test]
	cd frontend && npm install

install-deps:
	@echo "安装Python依赖..."
	python -m pip install -e .[dev,test]
	@echo "安装前端依赖..."
	cd frontend && npm install

dev-build:
	@echo "开发构建..."
	cd frontend && npm run build

# Docker测试
docker-test:
	@echo "在Docker中运行测试..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# CI/CD
ci-test:
	@echo "CI测试流程..."
	make clean
	make lint
	make test-unit
	make test-integration
	make test-frontend
	make coverage

# 快速测试
quick-test:
	python -m pytest tests/unit/ -v

# 完整测试
full-test:
	make clean
	make lint
	make test-all
	make coverage

# 数据库迁移命令
migrate-up:
	python3 scripts/migrate.py upgrade

migrate-down:
ifndef REV
	$(error REV参数是必需的。用法: make migrate-down REV=<revision>)
endif
	python3 scripts/migrate.py downgrade $(REV)

migrate-new:
ifndef MSG
	$(error MSG参数是必需的。用法: make migrate-new MSG='<迁移描述>')
endif
	python3 scripts/migrate.py revision --message "$(MSG)" --autogenerate

migrate-history:
	python3 scripts/migrate.py history --verbose

migrate-current:
	python3 scripts/migrate.py current

migrate-check:
	python3 scripts/migrate.py check

# 数据库管理命令
db-init:
	@echo "创建数据库 edusched..."
	createdb -U edusched -h localhost -p 5432 edusched || echo "数据库可能已存在"

db-up:
	docker-compose up -d postgres redis

db-down:
	docker-compose stop postgres redis

# Docker命令
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# 清理命令
clean-all:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	python tests/scripts/run_tests.py --clean

# 初始化项目（首次设置）
init: install-deps db-init migrate-up
	@echo "项目初始化完成！"