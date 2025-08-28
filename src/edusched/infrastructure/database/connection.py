"""数据库连接管理模块。

提供数据库连接池、会话工厂和事务管理功能。
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from edusched.core.config import get_settings

settings = get_settings()


class DatabaseManager:
    """数据库管理器。"""
    
    def __init__(self) -> None:
        """初始化数据库管理器。"""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._sync_engine = None
    
    async def initialize(self) -> None:
        """初始化数据库连接。"""
        if self._engine is not None:
            return
        
        # 创建异步引擎
        self._engine = create_async_engine(
            settings.database.url,
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # 创建会话工厂
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        
        # 创建同步引擎（用于Alembic迁移）
        self._sync_engine = create_engine(
            settings.database.url.replace("+asyncpg", ""),
            echo=settings.database.echo,
            poolclass=NullPool,  # 迁移时不需要连接池
        )
        
        # 测试连接
        await self._test_connection()
    
    async def _test_connection(self) -> None:
        """测试数据库连接。"""
        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception as e:
            raise RuntimeError(f"数据库连接测试失败: {e}")
    
    async def close(self) -> None:
        """关闭数据库连接。"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
        
        self._session_factory = None
    
    @property
    def engine(self) -> AsyncEngine:
        """获取异步引擎。"""
        if self._engine is None:
            raise RuntimeError("数据库未初始化，请先调用 initialize()")
        return self._engine
    
    @property
    def sync_engine(self):
        """获取同步引擎。"""
        if self._sync_engine is None:
            raise RuntimeError("数据库未初始化，请先调用 initialize()")
        return self._sync_engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """获取会话工厂。"""
        if self._session_factory is None:
            raise RuntimeError("数据库未初始化，请先调用 initialize()")
        return self._session_factory
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话。"""
        if self._session_factory is None:
            raise RuntimeError("数据库未初始化，请先调用 initialize()")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话上下文管理器。"""
        if self._session_factory is None:
            raise RuntimeError("数据库未初始化，请先调用 initialize()")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def execute_in_transaction(self, func, *args, **kwargs):
        """在事务中执行函数。"""
        async with self.get_session_context() as session:
            async with session.begin():
                return await func(session, *args, **kwargs)
    
    async def health_check(self) -> bool:
        """健康检查。"""
        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数。"""
    async for session in db_manager.get_session():
        yield session


async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话上下文的依赖函数。"""
    async with db_manager.get_session_context() as session:
        yield session


def get_sync_engine():
    """获取同步引擎（用于Alembic）。"""
    return db_manager.sync_engine


async def init_db() -> None:
    """初始化数据库。"""
    await db_manager.initialize()


async def close_db() -> None:
    """关闭数据库连接。"""
    await db_manager.close()