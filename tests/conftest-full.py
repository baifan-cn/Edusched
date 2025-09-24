"""完整的pytest配置文件"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from tests.utils.database_utils import DatabaseUtils
from tests.utils.mock_utils import MockUtils
from tests.utils.tenant_test_utils import TenantTestUtils
from tests.factories import *

# 测试配置
pytest_plugins = [
    'pytest_asyncio',
    'pytest_mock',
    'pytest_cov',
    'pytest_html',
    'pytest_metadata'
]


def pytest_configure(config):
    """pytest配置"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "e2e: 标记端到端测试"
    )
    config.addinivalue_line(
        "markers", "performance: 标记性能测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )
    config.addinivalue_line(
        "markers", "tenant: 标记多租户测试"
    )
    config.addinivalue_line(
        "markers", "api: 标记API测试"
    )
    config.addinivalue_line(
        "markers", "database: 标记数据库测试"
    )
    config.addinivalue_line(
        "markers", "scheduling: 标记调度测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    # 添加默认标记
    for item in items:
        # 根据文件路径添加标记
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        # 根据测试名称添加标记
        if "tenant" in item.name.lower():
            item.add_marker(pytest.mark.tenant)
        elif "api" in item.name.lower():
            item.add_marker(pytest.mark.api)
        elif "database" in item.name.lower():
            item.add_marker(pytest.mark.database)
        elif "scheduling" in item.name.lower():
            item.add_marker(pytest.mark.scheduling)

        # 标记慢速测试
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_engine():
    """创建测试数据库引擎"""
    engine = DatabaseUtils.create_test_engine()
    DatabaseUtils.create_tables(engine)
    yield engine
    DatabaseUtils.drop_tables(engine)
    engine.dispose()


@pytest.fixture(scope="session")
def test_db_session_factory(test_db_engine):
    """创建测试数据库会话工厂"""
    return DatabaseUtils.create_session_factory(test_db_engine)


@pytest.fixture
def test_db_session(test_db_session_factory):
    """创建测试数据库会话"""
    session = test_db_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_async_db_session():
    """创建异步测试数据库会话"""
    return DatabaseUtils.get_test_async_session()


@pytest.fixture
def mock_redis():
    """创建模拟Redis客户端"""
    return MockUtils.create_mock_redis()


@pytest.fixture
def mock_http_client():
    """创建模拟HTTP客户端"""
    return MockUtils.create_mock_http_client()


@pytest.fixture
def mock_async_http_client():
    """创建模拟异步HTTP客户端"""
    return MockUtils.create_mock_async_http_client()


@pytest.fixture
def mock_email_service():
    """创建模拟邮件服务"""
    return MockUtils.create_mock_email_service()


@pytest.fixture
def mock_file_storage():
    """创建模拟文件存储"""
    return MockUtils.create_mock_file_storage()


@pytest.fixture
def mock_logger():
    """创建模拟日志器"""
    return MockUtils.create_mock_logger()


@pytest.fixture
def mock_scheduler():
    """创建模拟调度器"""
    return MockUtils.create_mock_scheduler()


@pytest.fixture
def mock_cache():
    """创建模拟缓存"""
    return MockUtils.create_mock_cache()


@pytest.fixture
def test_tenant_id():
    """创建测试租户ID"""
    return TenantTestUtils.generate_tenant_id()


@pytest.fixture
def test_tenant_ids():
    """创建多个测试租户ID"""
    return TenantTestUtils.generate_tenant_ids(3)


@pytest.fixture
def sample_school(test_db_session, test_tenant_id):
    """创建示例学校"""
    return SchoolFactory.create(test_db_session, tenant_id=test_tenant_id)


@pytest.fixture
def sample_teacher(test_db_session, test_tenant_id):
    """创建示例教师"""
    return TeacherFactory.create(test_db_session, tenant_id=test_tenant_id)


@pytest.fixture
def sample_course(test_db_session, test_tenant_id):
    """创建示例课程"""
    return CourseFactory.create(test_db_session, tenant_id=test_tenant_id)


@pytest.fixture
def sample_class(test_db_session, test_tenant_id):
    """创建示例班级"""
    return ClassFactory.create(test_db_session, tenant_id=test_tenant_id)


@pytest.fixture
def sample_timeslot(test_db_session, test_tenant_id):
    """创建示例时间段"""
    return TimeslotFactory.create(test_db_session, tenant_id=test_tenant_id)


@pytest.fixture
def sample_section(test_db_session, test_tenant_id, sample_course, sample_teacher, sample_class):
    """创建示例教学段"""
    return SectionFactory.create_with_relationships(
        test_db_session,
        sample_course.id,
        sample_teacher.id,
        sample_class.id,
        tenant_id=test_tenant_id
    )


@pytest.fixture
def sample_assignment(test_db_session, test_tenant_id, sample_section, sample_timeslot):
    """创建示例课程安排"""
    return AssignmentFactory.create_with_relationships(
        test_db_session,
        sample_section.id,
        sample_timeslot.id,
        tenant_id=test_tenant_id
    )


@pytest.fixture
def test_data_set(test_db_session, test_tenant_id):
    """创建完整测试数据集"""
    return TenantTestUtils.create_tenant_data_set(test_db_session, test_tenant_id)


@pytest.fixture
def multi_tenant_data_set(test_db_session, test_tenant_ids):
    """创建多租户测试数据集"""
    return TenantTestUtils.create_multiple_tenant_data_sets(test_db_session, len(test_tenant_ids))


@pytest.fixture
def api_client():
    """创建API测试客户端"""
    from fastapi.testclient import TestClient
    from edusched.api.main import app

    return TestClient(app)


@pytest.fixture
def async_api_client():
    """创建异步API测试客户端"""
    from httpx import AsyncClient
    from edusched.api.main import app

    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def auth_headers():
    """创建认证头"""
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def tenant_headers(test_tenant_id):
    """创建租户头"""
    return {"X-Tenant-ID": test_tenant_id}


@pytest.fixture
def full_headers(test_tenant_id):
    """创建完整请求头"""
    return {
        "Authorization": "Bearer test_token",
        "X-Tenant-ID": test_tenant_id,
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_file():
    """创建测试文件"""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test file content")
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def test_files():
    """创建多个测试文件"""
    import tempfile
    import os

    files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{i}.txt') as f:
            f.write(f"Test file content {i}")
            f.flush()
            files.append(f.name)

    yield files

    for file_path in files:
        os.unlink(file_path)


@pytest.fixture
def benchmark_data():
    """创建基准测试数据"""
    return {
        "schools": [{"name": f"School {i}", "code": f"SCH{i:03d}"} for i in range(100)],
        "teachers": [{"name": f"Teacher {i}", "email": f"teacher{i}@test.edu"} for i in range(500)],
        "courses": [{"name": f"Course {i}", "code": f"CRS{i:03d}"} for i in range(200)],
        "classes": [{"name": f"Class {i}", "grade": i % 12 + 1} for i in range(100)],
    }


@pytest.fixture
def performance_thresholds():
    """性能阈值配置"""
    return {
        "api_response_time": 1000,  # 1秒
        "database_query_time": 100,  # 100毫秒
        "memory_usage": 100 * 1024 * 1024,  # 100MB
        "cpu_usage": 0.8,  # 80%
    }


@pytest.fixture
def test_config():
    """测试配置"""
    return {
        "database": {
            "url": "sqlite:///:memory:",
            "echo": False,
        },
        "redis": {
            "url": "redis://localhost:6379/1",
        },
        "api": {
            "base_url": "http://localhost:8000",
            "timeout": 30,
        },
        "tenant": {
            "default_tenant_id": "test_tenant",
        },
    }


# 清理fixture
@pytest.fixture(autouse=True)
def cleanup_test_data(test_db_session):
    """清理测试数据"""
    yield
    # 清理所有测试数据
    test_db_session.rollback()


# 标记慢速测试
def pytest_runtest_setup(item):
    """测试设置"""
    if 'slow' in item.keywords:
        # 慢速测试设置
        item.add_marker(pytest.mark.slow)


def pytest_runtest_teardown(item, nextitem):
    """测试清理"""
    # 清理测试相关资源
    pass


def pytest_sessionfinish(session, exitstatus):
    """会话结束时的处理"""
    print(f"\n测试完成，退出状态: {exitstatus}")

    # 输出测试统计
    if hasattr(session, 'testscollected'):
        print(f"收集到的测试数量: {session.testscollected}")

    if hasattr(session, 'items'):
        print(f"执行的测试数量: {len(session.items)}")


# 自定义命令行选项
def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="运行慢速测试"
    )
    parser.addoption(
        "--runintegration", action="store_true", default=False, help="运行集成测试"
    )
    parser.addoption(
        "--rune2e", action="store_true", default=False, help="运行E2E测试"
    )
    parser.addoption(
        "--runperformance", action="store_true", default=False, help="运行性能测试"
    )
    parser.addoption(
        "--tenant", action="store", default="test_tenant", help="指定租户ID"
    )
    parser.addoption(
        "--api-url", action="store", default="http://localhost:8000", help="API URL"
    )
    parser.addoption(
        "--db-url", action="store", default="sqlite:///:memory:", help="数据库URL"
    )


def pytest_collection_finish(session):
    """收集完成后的处理"""
    print(f"\n测试收集完成，共收集到 {len(session.items)} 个测试用例")


# 钩子函数
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子"""
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call':
        # 添加测试结果到报告
        pass


# 生成HTML报告
@pytest.fixture(scope='session', autouse=True)
def configure_html_report():
    """配置HTML报告"""
    pass


# 生成XML报告
@pytest.fixture(scope='session', autouse=True)
def configure_xml_report():
    """配置XML报告"""
    pass


# 生成覆盖率报告
@pytest.fixture(scope='session', autouse=True)
def configure_coverage_report():
    """配置覆盖率报告"""
    pass


# 测试数据验证
@pytest.fixture
def validate_test_data():
    """验证测试数据的fixture"""
    def _validate(data, schema):
        # 简单的数据验证
        for key, expected_type in schema.items():
            if key in data:
                assert isinstance(data[key], expected_type), \
                    f"Field {key} should be {expected_type}, got {type(data[key])}"
    return _validate


# 环境变量设置
@pytest.fixture(autouse=True)
def set_test_environment():
    """设置测试环境变量"""
    original_env = os.environ.copy()

    # 设置测试环境变量
    os.environ['TESTING'] = 'true'
    os.environ['DEBUG'] = 'false'
    os.environ['LOG_LEVEL'] = 'ERROR'

    yield

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)


# 错误处理
@pytest.fixture
def error_handler():
    """错误处理fixture"""
    def _handle_error(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            raise
    return _handle_error


# 性能监控
@pytest.fixture
def performance_monitor():
    """性能监控fixture"""
    import time
    import psutil
    import tracemalloc

    def _monitor(func, *args, **kwargs):
        # 开始监控
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        tracemalloc.start()

        try:
            result = func(*args, **kwargs)
        finally:
            # 结束监控
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # 输出性能数据
            print(f"Function {func.__name__}:")
            print(f"  Time: {end_time - start_time:.3f}s")
            print(f"  Memory: {end_memory - start_memory} bytes")
            print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")

        return result

    return _monitor