"""Pytest配置和共享fixtures。"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from edusched.infrastructure.database.models import Base
from edusched.infrastructure.database.connection import get_db
from edusched.domain.models import School, Teacher, Course, ClassGroup, Section, Timeslot, Assignment
from edusched.scheduling.engine import SchedulingEngine


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环。"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db() -> Generator:
    """创建测试数据库。"""
    # 使用内存SQLite数据库
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 创建测试会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal

    # 清理
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """创建数据库会话。"""
    db = test_db()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_school() -> School:
    """创建示例学校。"""
    return School(
        name="测试学校",
        code="TEST_SCHOOL",
        address="测试地址123号",
        phone="010-12345678",
        email="test@school.edu",
        is_active=True,
        settings={"max_students_per_class": 40, "school_hours": "08:00-17:00"}
    )


@pytest.fixture
def sample_teacher() -> Teacher:
    """创建示例教师。"""
    return Teacher(
        first_name="张",
        last_name="老师",
        email="zhang@school.edu",
        phone="13800138000",
        department="数学系",
        title="教授",
        max_hours_per_week=20,
        preferred_time_slots=["monday_09:00", "tuesday_09:00", "wednesday_09:00"],
        is_active=True
    )


@pytest.fixture
def sample_course() -> Course:
    """创建示例课程。"""
    return Course(
        name="高等数学",
        code="MATH101",
        description="高等数学基础课程",
        credit_hours=4,
        is_active=True
    )


@pytest.fixture
def sample_class_group() -> ClassGroup:
    """创建示例班级。"""
    return ClassGroup(
        name="计算机科学1班",
        grade_level=1,
        student_count=30,
        is_active=True
    )


@pytest.fixture
def sample_timeslot() -> Timeslot:
    """创建示例时间段。"""
    return Timeslot(
        day_of_week=1,  # 周一
        start_time="09:00",
        end_time="10:00",
        period_type="class",
        is_active=True
    )


@pytest.fixture
def sample_section(sample_teacher, sample_course, sample_class_group) -> Section:
    """创建示例教学段。"""
    return Section(
        course_id=sample_course.id,
        teacher_id=sample_teacher.id,
        class_group_id=sample_class_group.id,
        section_number="MATH101-01",
        max_students=30,
        weekly_hours=3,
        semester="2024-春季",
        is_active=True
    )


@pytest.fixture
def scheduling_engine() -> SchedulingEngine:
    """创建调度引擎。"""
    return SchedulingEngine("test_tenant")


@pytest.fixture
def mock_http_client():
    """创建模拟HTTP客户端。"""
    return MagicMock()


@pytest.fixture
def mock_redis():
    """创建模拟Redis客户端。"""
    return MagicMock()


# 覆盖数据库依赖
@pytest.fixture
def override_get_db(db_session):
    """覆盖数据库依赖。"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    return _override_get_db