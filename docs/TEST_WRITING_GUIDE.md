# Edusched 测试编写指南

## 目录
- [测试概述](#测试概述)
- [测试架构](#测试架构)
- [后端测试指南](#后端测试指南)
- [前端测试指南](#前端测试指南)
- [测试最佳实践](#测试最佳实践)
- [测试数据管理](#测试数据管理)
- [Mock和Stub使用](#mock和stub使用)
- [测试覆盖率](#测试覆盖率)
- [CI/CD集成](#cicd集成)
- [常见问题](#常见问题)

## 测试概述

### 测试金字塔原则
Edusched项目遵循测试金字塔原则，确保测试的合理分布：
- **70% 单元测试**：快速测试单个组件的功能
- **25% 集成测试**：测试组件间的交互
- **5% E2E测试**：测试完整的用户流程

### 测试分类
```
tests/
├── unit/           # 单元测试 - 测试单个函数/类
├── integration/    # 集成测试 - 测试组件间交互
├── e2e/           # 端到端测试 - 测试完整用户流程
├── performance/    # 性能测试 - 测试系统性能
├── api/           # API测试 - 测试HTTP接口
├── database/      # 数据库测试 - 测试数据访问层
├── tenant/        # 多租户测试 - 测试租户隔离
└── scheduling/    # 调度测试 - 测试核心算法
```

## 测试架构

### 后端测试框架
- **测试运行器**: pytest
- **Mock工具**: pytest-mock
- **覆盖率**: pytest-cov
- **数据库测试**: SQLAlchemy + SQLite/PostgreSQL
- **API测试**: FastAPI TestClient

### 前端测试框架
- **测试运行器**: Vitest
- **组件测试**: @vue/test-utils
- **Mock工具**: vi (Vitest Mock)
- **覆盖率**: @vitest/coverage
- **API测试**: axios-mock-adapter

## 后端测试指南

### 1. 基本测试结构

```python
# tests/unit/test_example.py
import pytest
from unittest.mock import Mock, patch
from edusched.domain.services import ExampleService

class TestExampleService:
    """示例服务测试"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return ExampleService()

    @pytest.fixture
    def mock_repository(self):
        """Mock仓库"""
        return Mock()

    def test_service_method(self, service, mock_repository):
        """测试服务方法"""
        # Arrange
        mock_repository.get_by_id.return_value = {"id": 1, "name": "test"}

        # Act
        result = service.get_example(1, mock_repository)

        # Assert
        assert result["name"] == "test"
        mock_repository.get_by_id.assert_called_once_with(1)
```

### 2. 使用数据工厂

```python
# tests/unit/test_school_service.py
import pytest
from tests.factories import SchoolFactory, TeacherFactory

class TestSchoolService:
    """学校服务测试"""

    def test_create_school_with_teachers(self, test_db_session, test_tenant_id):
        """测试创建学校及教师"""
        # Arrange
        school_data = SchoolFactory.build_dict(tenant_id=test_tenant_id)
        teacher_data = TeacherFactory.build_dict(tenant_id=test_tenant_id)

        # Act
        school = SchoolFactory.create(test_db_session, **school_data)
        teachers = TeacherFactory.create_batch(test_db_session, 3, tenant_id=test_tenant_id)

        # Assert
        assert school.id is not None
        assert len(teachers) == 3
        assert all(teacher.tenant_id == test_tenant_id for teacher in teachers)
```

### 3. 数据库测试

```python
# tests/database/test_school_repository.py
import pytest
from tests.factories import SchoolFactory
from tests.utils.database_utils import DatabaseUtils

class TestSchoolRepository:
    """学校仓库测试"""

    def test_create_school(self, test_db_session, test_tenant_id):
        """测试创建学校"""
        # Arrange
        school_data = {
            "name": "Test School",
            "code": "TST001",
            "tenant_id": test_tenant_id
        }

        # Act
        school = SchoolFactory.create(test_db_session, **school_data)

        # Assert
        assert school.id is not None
        assert school.name == "Test School"
        assert school.tenant_id == test_tenant_id

    def test_get_school_by_id(self, test_db_session, test_tenant_id):
        """测试根据ID获取学校"""
        # Arrange
        school = SchoolFactory.create(test_db_session, tenant_id=test_tenant_id)

        # Act
        result = test_db_session.query(School).filter(School.id == school.id).first()

        # Assert
        assert result is not None
        assert result.id == school.id
```

### 4. API测试

```python
# tests/api/test_school_api.py
import pytest
from fastapi.testclient import TestClient
from tests.factories import SchoolFactory

class TestSchoolAPI:
    """学校API测试"""

    def test_create_school(self, api_client, test_tenant_id):
        """测试创建学校API"""
        # Arrange
        school_data = {
            "name": "Test School",
            "code": "TST001",
            "type": "elementary",
            "address": "123 Test St"
        }

        headers = {"X-Tenant-ID": test_tenant_id}

        # Act
        response = api_client.post("/api/v1/schools/", json=school_data, headers=headers)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test School"
        assert data["tenant_id"] == test_tenant_id

    def test_get_schools(self, api_client, test_db_session, test_tenant_id):
        """测试获取学校列表"""
        # Arrange
        SchoolFactory.create_batch(test_db_session, 3, tenant_id=test_tenant_id)
        headers = {"X-Tenant-ID": test_tenant_id}

        # Act
        response = api_client.get("/api/v1/schools/", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
```

### 5. 多租户测试

```python
# tests/tenant/test_tenant_isolation.py
import pytest
from tests.factories import SchoolFactory
from tests.utils.tenant_test_utils import TenantTestUtils

class TestTenantIsolation:
    """租户隔离测试"""

    def test_tenant_data_isolation(self, test_db_session, test_tenant_ids):
        """测试租户数据隔离"""
        # Arrange
        tenant1, tenant2, tenant3 = test_tenant_ids

        # 为每个租户创建数据
        school1 = SchoolFactory.create(test_db_session, tenant_id=tenant1, name="School 1")
        school2 = SchoolFactory.create(test_db_session, tenant_id=tenant2, name="School 2")
        school3 = SchoolFactory.create(test_db_session, tenant_id=tenant3, name="School 3")

        # Act & Assert - 验证租户1只能看到自己的数据
        result1 = TenantTestUtils.get_tenant_schools(test_db_session, tenant1)
        assert len(result1) == 1
        assert result1[0].name == "School 1"

        # 验证租户2只能看到自己的数据
        result2 = TenantTestUtils.get_tenant_schools(test_db_session, tenant2)
        assert len(result2) == 1
        assert result2[0].name == "School 2"
```

### 6. 集成测试

```python
# tests/integration/test_scheduling_integration.py
import pytest
from tests.factories import (
    SchoolFactory, TeacherFactory, CourseFactory,
    ClassFactory, SectionFactory, TimeslotFactory
)

class TestSchedulingIntegration:
    """调度集成测试"""

    def test_complete_scheduling_workflow(self, test_db_session, test_tenant_id):
        """测试完整的调度工作流"""
        # Arrange - 创建完整的测试数据
        school = SchoolFactory.create(test_db_session, tenant_id=test_tenant_id)
        teachers = TeacherFactory.create_batch(test_db_session, 5, tenant_id=test_tenant_id)
        courses = CourseFactory.create_batch(test_db_session, 10, tenant_id=test_tenant_id)
        classes = ClassFactory.create_batch(test_db_session, 8, tenant_id=test_tenant_id)
        timeslots = TimeslotFactory.create_batch(test_db_session, 20, tenant_id=test_tenant_id)

        # Act - 创建教学段
        sections = []
        for course in courses[:5]:
            section = SectionFactory.create_with_relationships(
                test_db_session,
                course.id,
                teachers[0].id,
                classes[0].id,
                tenant_id=test_tenant_id
            )
            sections.append(section)

        # Assert - 验证数据完整性
        assert len(sections) == 5
        for section in sections:
            assert section.course_id is not None
            assert section.teacher_id is not None
            assert section.class_id is not None
            assert section.tenant_id == test_tenant_id
```

## 前端测试指南

### 1. 组件测试

```typescript
// frontend/src/tests/unit/components/Common/ButtonTest.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/Common/Button.vue'

describe('Button', () => {
  it('renders correctly with default props', () => {
    const wrapper = mount(Button, {
      props: {
        text: 'Click me'
      }
    })

    expect(wrapper.text()).toBe('Click me')
    expect(wrapper.classes()).toContain('el-button')
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(Button, {
      props: {
        text: 'Click me'
      }
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('shows loading state', () => {
    const wrapper = mount(Button, {
      props: {
        text: 'Loading',
        loading: true
      }
    })

    expect(wrapper.find('.el-icon-loading').exists()).toBe(true)
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })
})
```

### 2. Store测试

```typescript
// frontend/src/tests/unit/stores/schoolStore.spec.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useSchoolStore } from '@/stores/schoolStore'
import { mockSchoolApi } from '@/test/utils/api-utils'

describe('SchoolStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetches schools successfully', async () => {
    const store = useSchoolStore()
    const mockSchools = [
      { id: 1, name: 'School 1', code: 'SCH001' },
      { id: 2, name: 'School 2', code: 'SCH002' }
    ]

    // Mock API call
    vi.spyOn(mockSchoolApi, 'getSchools').mockResolvedValue(mockSchools)

    await store.fetchSchools()

    expect(store.schools).toEqual(mockSchools)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('handles API errors', async () => {
    const store = useSchoolStore()

    vi.spyOn(mockSchoolApi, 'getSchools').mockRejectedValue(new Error('API Error'))

    await store.fetchSchools()

    expect(store.schools).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe('API Error')
  })
})
```

### 3. API测试

```typescript
// frontend/src/tests/unit/api/schoolApi.spec.ts
import { describe, it, expect, vi, afterEach } from 'vitest'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { schoolApi } from '@/api/schoolApi'

describe('SchoolApi', () => {
  let mock: MockAdapter

  afterEach(() => {
    mock.restore()
  })

  it('creates school successfully', async () => {
    mock = new MockAdapter(axios)
    const schoolData = {
      name: 'Test School',
      code: 'TST001',
      type: 'elementary'
    }
    const responseData = { id: 1, ...schoolData }

    mock.onPost('/api/v1/schools/').reply(201, responseData)

    const result = await schoolApi.createSchool(schoolData)

    expect(result).toEqual(responseData)
  })

  it('handles validation errors', async () => {
    mock = new MockAdapter(axios)
    const errorData = {
      detail: [
        {
          loc: ['body', 'name'],
          msg: 'Field required',
          type: 'value_error.missing'
        }
      ]
    }

    mock.onPost('/api/v1/schools/').reply(422, errorData)

    await expect(schoolApi.createSchool({})).rejects.toThrow()
  })
})
```

### 4. 路由测试

```typescript
// frontend/src/tests/unit/router/router.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory, Router } from 'vue-router'
import SchoolsView from '@/views/SchoolsView.vue'

describe('Router', () => {
  let router: Router

  beforeEach(() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/schools', component: SchoolsView },
        { path: '/', redirect: '/schools' }
      ]
    })
  })

  it('navigates to schools view', async () => {
    await router.push('/schools')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/schools')
  })

  it('redirects to schools from root', async () => {
    await router.push('/')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/schools')
  })
})
```

### 5. 表单测试

```typescript
// frontend/src/tests/unit/components/Forms/SchoolFormTest.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import SchoolForm from '@/components/Forms/SchoolForm.vue'

vi.mock('element-plus', async () => ({
  ...await vi.importActual('element-plus'),
  ElMessage: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

describe('SchoolForm', () => {
  it('validates required fields', async () => {
    const wrapper = mount(SchoolForm)

    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.text()).toContain('学校名称不能为空')
    expect(wrapper.text()).toContain('学校代码不能为空')
  })

  it('submits form successfully', async () => {
    const wrapper = mount(SchoolForm)

    await wrapper.find('#name').setValue('Test School')
    await wrapper.find('#code').setValue('TST001')
    await wrapper.find('#type').setValue('elementary')
    await wrapper.find('form').trigger('submit.prevent')

    expect(ElMessage.success).toHaveBeenCalledWith('学校创建成功')
  })
})
```

## 测试最佳实践

### 1. 命名规范

#### 测试文件命名
- 后端：`test_*.py` 或 `*_test.py`
- 前端：`*.spec.ts`

#### 测试函数命名
- 使用描述性的测试名称
- 格式：`test_场景_预期结果`
- 示例：
  ```python
  def test_create_school_with_valid_data_succeeds():
      pass

  def test_create_school_with_duplicate_code_fails():
      pass
  ```

### 2. 测试结构（AAA模式）

```python
def test_user_service_create_user():
    # Arrange - 准备测试数据
    user_data = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    mock_repository = Mock()

    # Act - 执行测试操作
    service = UserService(mock_repository)
    result = service.create_user(user_data)

    # Assert - 验证结果
    assert result["name"] == "John Doe"
    mock_repository.create.assert_called_once_with(user_data)
```

### 3. 测试隔离

```python
@pytest.fixture(autouse=True)
def setup_test_environment(test_db_session):
    """每个测试的设置和清理"""
    # Arrange - 准备测试数据
    test_data = TestDataFactory.create(test_db_session)

    yield test_data

    # Cleanup - 清理测试数据
    test_db_session.rollback()
```

### 4. 断言最佳实践

```python
# 好的断言
def test_school_creation(test_db_session):
    school = SchoolFactory.create(test_db_session, name="Test School")

    # 明确的断言
    assert school.id is not None
    assert school.name == "Test School"
    assert school.created_at is not None
    assert school.tenant_id is not None

# 避免的断言
def test_school_creation_bad(test_db_session):
    school = SchoolFactory.create(test_db_session)

    # 不明确的断言
    assert school  # 这个断言太模糊
```

## 测试数据管理

### 1. 使用工厂模式

```python
# 推荐方式 - 使用工厂
def test_with_factory(test_db_session):
    school = SchoolFactory.create(
        test_db_session,
        name="Test School",
        code="TST001"
    )
    assert school.name == "Test School"

# 不推荐 - 手动创建
def test_manual_creation(test_db_session):
    school = School(
        name="Test School",
        code="TST001",
        tenant_id="test_tenant",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db_session.add(school)
    test_db_session.commit()
    assert school.name == "Test School"
```

### 2. 批量数据创建

```python
def test_batch_operations(test_db_session):
    # 创建批量数据
    schools = SchoolFactory.create_batch(
        test_db_session,
        size=10,
        tenant_id="test_tenant"
    )

    assert len(schools) == 10
    assert all(school.tenant_id == "test_tenant" for school in schools)
```

### 3. 使用Traits

```python
# 在工厂中定义traits
class SchoolFactory(BaseFactory):
    class Meta:
        model = School

    # 基本属性
    name = Faker("company")
    code = Faker("bothify", text="SCH###")

    # Traits
    class Params:
        elementary = {
            "type": "elementary",
            "grades": "1-6"
        }
        high_school = {
            "type": "high_school",
            "grades": "9-12"
        }

# 使用traits
def test_school_types(test_db_session):
    elementary_school = SchoolFactory.create(
        test_db_session,
        elementary=True
    )
    high_school = SchoolFactory.create(
        test_db_session,
        high_school=True
    )

    assert elementary_school.type == "elementary"
    assert high_school.type == "high_school"
```

## Mock和Stub使用

### 1. Mock外部服务

```python
# 使用pytest-mock
def test_email_service(mocker):
    # Mock email服务
    mock_email = mocker.patch('edusched.infrastructure.email.EmailService')
    mock_email.send_email.return_value = True

    service = NotificationService(mock_email)
    result = service.send_notification("test@example.com", "Test message")

    assert result is True
    mock_email.send_email.assert_called_once_with(
        "test@example.com",
        "Test message"
    )
```

### 2. 使用patch装饰器

```python
from unittest.mock import patch

class TestExternalAPI:
    @patch('requests.get')
    def test_fetch_data_from_api(self, mock_get):
        # 配置mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        # 执行测试
        result = fetch_external_data()

        # 验证结果
        assert result == {"data": "test"}
        mock_get.assert_called_once_with("https://api.example.com/data")
```

### 3. Mock数据库查询

```python
def test_repository_with_mock(mocker):
    # Mock数据库会话
    mock_session = mocker.Mock()
    mock_query = mocker.Mock()
    mock_session.query.return_value = mock_query

    # 配置查询结果
    mock_result = Mock()
    mock_result.id = 1
    mock_result.name = "Test School"
    mock_query.filter.return_value.first.return_value = mock_result

    # 执行测试
    repository = SchoolRepository()
    result = repository.get_by_id(mock_session, 1)

    # 验证结果
    assert result.id == 1
    assert result.name == "Test School"
```

## 测试覆盖率

### 1. 覆盖率目标

```python
# pytest.ini配置
[tool:pytest]
addopts =
    --cov=src/edusched
    --cov-report=term-missing
    --cov-report=html:reports/coverage/html
    --cov-report=xml:reports/coverage/coverage.xml
    --cov-fail-under=80  # 覆盖率至少80%
```

### 2. 覆盖率排除

```python
# coverage.py配置
[coverage:run]
omit =
    */tests/*
    */test_*
    */__pycache__/*
    */migrations/*
    */venv/*
    */.venv/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
```

### 3. 生成覆盖率报告

```bash
# 运行测试并生成覆盖率报告
pytest --cov=src/edusched --cov-report=html

# 查看HTML报告
open reports/coverage/html/index.html
```

## CI/CD集成

### 1. GitHub Actions工作流

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12]
        node-version: [18.x, 20.x]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install uv
        uv pip install -e .[dev,test]

    - name: Run tests
      run: |
        python tests/scripts/run_tests.py --all --coverage
      env:
        DATABASE_URL: postgresql://postgres:testpass@localhost:5432/edusched_test
        REDIS_URL: redis://localhost:6379/1
        TESTING: true

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./reports/coverage/coverage.xml
```

### 2. 本地测试脚本

```bash
#!/bin/bash
# scripts/test.sh

echo "运行完整测试套件..."

# 清理之前的测试产物
make clean

# 运行代码检查
make lint

# 运行所有测试
make test-all

# 生成覆盖率报告
make coverage

echo "测试完成！查看报告："
echo "- HTML覆盖率报告: reports/coverage/html/index.html"
echo "- 测试报告: reports/test-report.html"
```

## 常见问题

### 1. 数据库连接问题

```python
# 问题：测试无法连接数据库
# 解决：使用测试数据库配置

@pytest.fixture(scope="session")
def test_db_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        "sqlite:///:memory:",  # 使用内存数据库
        poolclass=StaticPool
    )
    yield engine
    engine.dispose()
```

### 2. 测试数据隔离

```python
# 问题：测试之间数据干扰
# 解决：使用事务回滚

@pytest.fixture
def test_db_session(test_db_engine):
    """创建测试会话"""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### 3. 异步测试

```python
# 问题：异步函数测试
# 解决：使用pytest-asyncio

import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == "expected"
```

### 4. 前端组件依赖

```typescript
// 问题：组件依赖Pinia store
// 解决：Mock store依赖

import { createTestingPinia } from '@pinia/testing'

const wrapper = mount(MyComponent, {
  global: {
    plugins: [
      createTestingPinia({
        createSpy: vi.fn,
        initialState: {
          counter: { count: 10 }
        }
      })
    ]
  }
})
```

### 5. 性能测试

```python
# 问题：需要测试性能
# 解决：使用性能基准测试

def test_performance_with_benchmark(benchmark):
    def create_many_schools():
        return SchoolFactory.create_batch(test_db_session, 100)

    result = benchmark(create_many_schools)
    assert len(result) == 100
```

## 测试工具快速参考

### 常用pytest命令

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_school.py

# 运行特定测试函数
pytest tests/unit/test_school.py::test_create_school

# 运行标记的测试
pytest -m "unit"
pytest -m "integration"
pytest -m "api"

# 生成覆盖率报告
pytest --cov=src/edusched --cov-report=html

# 运行慢速测试
pytest --runslow

# 并行运行测试
pytest -n auto
```

### 常用Vitest命令

```bash
# 运行所有测试
npm test

# 运行特定测试文件
npm test -- schools.spec.ts

# 监听模式
npm run test:watch

# 运行覆盖率测试
npm run test:coverage

# 运行UI测试
npm run test:ui
```

### Makefile命令

```bash
# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 运行所有测试
make test-all

# 运行代码检查
make lint

# 格式化代码
make format

# 生成覆盖率报告
make coverage

# 清理测试产物
make clean
```

这个测试编写指南提供了Edusched项目测试开发的完整参考。按照这些指南，开发者可以编写高质量、可维护的测试代码，确保项目的稳定性和可靠性。