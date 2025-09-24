"""数据库测试工具"""

import os
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager, contextmanager

from edusched.infrastructure.database.models import Base


class DatabaseUtils:
    """数据库测试工具类"""

    @staticmethod
    def create_test_database_url() -> str:
        """创建测试数据库URL"""
        return os.getenv(
            "TEST_DATABASE_URL",
            "sqlite:///:memory:"
        )

    @staticmethod
    def create_test_async_database_url() -> str:
        """创建异步测试数据库URL"""
        return os.getenv(
            "TEST_ASYNC_DATABASE_URL",
            "sqlite+aiosqlite:///:memory:"
        )

    @staticmethod
    def create_test_engine():
        """创建测试数据库引擎"""
        return create_engine(
            DatabaseUtils.create_test_database_url(),
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    @staticmethod
    def create_test_async_engine():
        """创建异步测试数据库引擎"""
        return create_async_engine(
            DatabaseUtils.create_test_async_database_url(),
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    @staticmethod
    def create_tables(engine):
        """创建所有表"""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def drop_tables(engine):
        """删除所有表"""
        Base.metadata.drop_all(bind=engine)

    @staticmethod
    def create_session_factory(engine):
        """创建会话工厂"""
        return sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )

    @staticmethod
    def create_async_session_factory(engine):
        """创建异步会话工厂"""
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @staticmethod
    @contextmanager
    def get_test_session() -> Generator[Session, None, None]:
        """获取测试数据库会话"""
        engine = DatabaseUtils.create_test_engine()
        DatabaseUtils.create_tables(engine)

        session_factory = DatabaseUtils.create_session_factory(engine)
        session = session_factory()

        try:
            yield session
        finally:
            session.close()
            DatabaseUtils.drop_tables(engine)

    @staticmethod
    @asynccontextmanager
    async def get_test_async_session() -> AsyncGenerator[AsyncSession, None]:
        """获取异步测试数据库会话"""
        engine = DatabaseUtils.create_test_async_engine()
        DatabaseUtils.create_tables(engine)

        session_factory = DatabaseUtils.create_async_session_factory(engine)
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()
                await engine.dispose()

    @staticmethod
    def clear_table(session, model_class):
        """清空表数据"""
        session.query(model_class).delete()
        session.commit()

    @staticmethod
    def count_records(session, model_class):
        """统计记录数量"""
        return session.query(model_class).count()

    @staticmethod
    def get_all_records(session, model_class):
        """获取所有记录"""
        return session.query(model_class).all()

    @staticmethod
    def find_record_by_id(session, model_class, record_id):
        """根据ID查找记录"""
        return session.query(model_class).filter(model_class.id == record_id).first()

    @staticmethod
    def find_records_by_field(session, model_class, field_name, field_value):
        """根据字段查找记录"""
        field = getattr(model_class, field_name)
        return session.query(model_class).filter(field == field_value).all()

    @staticmethod
    def assert_record_exists(session, model_class, record_id):
        """断言记录存在"""
        record = DatabaseUtils.find_record_by_id(session, model_class, record_id)
        assert record is not None, f"Record with id {record_id} does not exist"

    @staticmethod
    def assert_record_not_exists(session, model_class, record_id):
        """断言记录不存在"""
        record = DatabaseUtils.find_record_by_id(session, model_class, record_id)
        assert record is None, f"Record with id {record_id} exists"

    @staticmethod
    def assert_field_value(session, model_class, record_id, field_name, expected_value):
        """断言字段值"""
        record = DatabaseUtils.find_record_by_id(session, model_class, record_id)
        assert record is not None, f"Record with id {record_id} does not exist"

        actual_value = getattr(record, field_name)
        assert actual_value == expected_value, \
            f"Field {field_name} value mismatch. Expected: {expected_value}, Actual: {actual_value}"

    @staticmethod
    def assert_tenant_isolation(session, model_class, tenant_id):
        """断言租户数据隔离"""
        records = session.query(model_class).filter(model_class.tenant_id == tenant_id).all()

        # 检查所有记录都属于指定租户
        for record in records:
            assert record.tenant_id == tenant_id, \
                f"Record {record.id} belongs to tenant {record.tenant_id}, not {tenant_id}"

        return records

    @staticmethod
    def seed_test_data(session, factory_class, count: int = 10):
        """批量生成测试数据"""
        instances = []
        for _ in range(count):
            instance = factory_class.create(session)
            instances.append(instance)
        return instances

    @staticmethod
    def setup_test_database():
        """设置测试数据库"""
        engine = DatabaseUtils.create_test_engine()
        DatabaseUtils.create_tables(engine)
        return engine

    @staticmethod
    def teardown_test_database(engine):
        """清理测试数据库"""
        DatabaseUtils.drop_tables(engine)
        engine.dispose()