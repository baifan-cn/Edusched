# Edusched测试架构规划

## 测试架构总览

Edusched项目采用分层测试架构，遵循测试金字塔原则，确保代码质量和系统稳定性。

```
                    ┌─────────────────┐
                    │   E2E Tests     │
                    │   (5%)          │
                    └─────────────────┘
                   ┌───────────────────┐
                   │  Integration Tests│
                   │  (25%)            │
                   └───────────────────┘
              ┌─────────────────────────┐
              │      Unit Tests        │
              │      (70%)             │
              └─────────────────────────┘
```

## 测试层次结构

### 1. 单元测试 (Unit Tests) - 70%
**目的**：验证单个组件/函数的正确性
**范围**：独立的函数、类、组件
**执行速度**：快速（毫秒级）
**依赖**：无外部依赖，使用mock

#### 后端单元测试
```
tests/
├── unit/
│   ├── api/              # API层测试
│   │   ├── test_schools.py
│   │   ├── test_teachers.py
│   │   ├── test_courses.py
│   │   └── test_timetables.py
│   ├── domain/           # 领域层测试
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_validators.py
│   ├── infrastructure/   # 基础设施层测试
│   │   ├── test_database.py
│   │   ├── test_cache.py
│   │   └── test_external.py
│   └── scheduling/       # 调度引擎测试
│       ├── test_engine.py
│       ├── test_constraints.py
│       └── test_optimizer.py
```

#### 前端单元测试
```
frontend/src/tests/unit/
├── components/          # 组件测试
│   ├── Common/
│   ├── Forms/
│   └── Layout/
├── stores/             # 状态管理测试
├── utils/              # 工具函数测试
├── api/                # API调用测试
└── composables/        # 组合式函数测试
```

### 2. 集成测试 (Integration Tests) - 25%
**目的**：验证多个组件协作的正确性
**范围**：模块间交互、API集成、数据库交互
**执行速度**：中等（秒级）
**依赖**：需要真实的外部服务（数据库、Redis等）

#### 后端集成测试
```
tests/
├── integration/
│   ├── api/             # API集成测试
│   ├── database/        # 数据库集成测试
│   ├── cache/           # 缓存集成测试
│   ├── auth/            # 认证集成测试
│   └── scheduling/      # 调度集成测试
```

#### 前端集成测试
```
frontend/src/tests/integration/
├── api/                # API集成测试
├── router/             # 路由集成测试
├── stores/             # 状态管理集成测试
└── workflows/          # 工作流测试
```

### 3. 端到端测试 (E2E Tests) - 5%
**目的**：验证完整用户流程
**范围**：完整的应用功能流程
**执行速度**：慢（分钟级）
**依赖**：完整的测试环境

#### E2E测试
```
tests/
├── e2e/
│   ├── auth/           # 认证流程
│   ├── schools/        # 学校管理
│   ├── teachers/       # 教师管理
│   ├── courses/        # 课程管理
│   └── scheduling/     # 调度流程

frontend/src/tests/e2e/
├── auth/               # 认证流程
├── dashboard/          # 仪表板
├── schools/            # 学校管理
└── scheduling/         # 调度流程
```

### 4. 性能测试 (Performance Tests)
**目的**：验证系统性能和负载能力
**范围**：API响应时间、并发处理、资源使用
**执行环境**：类生产环境

#### 性能测试
```
tests/
├── performance/
│   ├── api/            # API性能测试
│   ├── database/       # 数据库性能测试
│   ├── scheduling/     # 调度性能测试
│   └── load/           # 负载测试
```

## 测试工具和框架

### 后端测试工具
- **测试框架**: pytest
- **异步测试**: pytest-asyncio
- **覆盖率**: pytest-cov
- **Mock工具**: pytest-mock
- **数据工厂**: factory-boy
- **假数据**: faker
- **HTTP测试**: httpx
- **数据库测试**: pytest-postgresql, pytest-redis

### 前端测试工具
- **测试框架**: vitest
- **Vue测试**: @vue/test-utils
- **覆盖率**: @vitest/coverage-v8
- **E2E测试**: playwright 或 cypress
- **Mock工具**: vi (vitest内置)
- **UI测试**: @testing-library/vue

### 性能测试工具
- **负载测试**: locust 或 k6
- **性能分析**: pytest-benchmark
- **监控**: prometheus, grafana

## 测试数据管理

### 测试数据工厂
```
tests/
├── factories/          # 数据工厂
│   ├── __init__.py
│   ├── school_factory.py
│   ├── teacher_factory.py
│   ├── course_factory.py
│   └── scheduling_factory.py
```

### 测试固件
```
tests/
├── fixtures/           # 测试固件
│   ├── __init__.py
│   ├── database_fixtures.py
│   ├── api_fixtures.py
│   └── scheduling_fixtures.py
```

## 测试环境配置

### 测试数据库
- 使用PostgreSQL测试数据库
- 支持事务回滚
- 数据隔离

### 测试Redis
- 使用Redis测试实例
- 数据隔离

### Mock外部服务
- 邮件服务
- 文件存储服务
- 第三方API

## 测试运行策略

### 本地开发
```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 运行E2E测试
make test-e2e

# 运行性能测试
make test-performance
```

### CI/CD流水线
```yaml
stages:
  - test-unit        # 单元测试
  - test-integration # 集成测试
  - test-e2e         # E2E测试
  - test-performance # 性能测试
  - coverage         # 覆盖率报告
```

## 测试覆盖率目标

- **单元测试**: 80%+
- **集成测试**: 60%+
- **总体覆盖率**: 70%+
- **关键模块**: 90%+

## 测试报告和监控

### 覆盖率报告
- HTML格式报告
- XML格式CI集成
- 趋势分析

### 测试结果报告
- 测试执行结果
- 失败用例详情
- 性能指标

### 持续监控
- 测试执行时间趋势
- 覆盖率变化
- 失败率统计

## 多租户测试策略

### 租户数据隔离
- 每个测试使用独立的租户ID
- 验证数据隔离
- 测试租户间权限

### 租户配置测试
- 不同租户配置
- 租户特定功能
- 租户级别限制

## 测试最佳实践

### 命名规范
- 测试文件：`test_*.py` 或 `*_test.py`
- 测试类：`Test*`
- 测试方法：`test_*`
- 测试描述：`should_` 或 `test_` 前缀

### 测试结构
```python
def test_feature_name():
    # Arrange - 准备测试数据
    # Act - 执行测试操作
    # Assert - 验证结果
    pass
```

### Mock策略
- 外部依赖使用mock
- 数据库使用测试数据库
- 缓存使用测试Redis实例
- 文件系统使用内存文件系统

### 异步测试
- 使用pytest-asyncio
- 正确处理异步操作
- 避免异步泄露

## 测试文档和指南

### 测试编写指南
- 测试原则和最佳实践
- 常见测试模式
- 测试工具使用方法

### 测试案例模板
- 单元测试模板
- 集成测试模板
- E2E测试模板

### 故障排除指南
- 常见测试问题
- 调试技巧
- 性能优化建议