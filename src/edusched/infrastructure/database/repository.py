"""优化的数据库仓库基类。

提供通用的CRUD操作、缓存支持和性能监控功能。
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Generic
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import DeclarativeBase, selectinload

from edusched.infrastructure.cache.manager import cache_manager, cached
from edusched.infrastructure.database.optimizer import query_optimizer, optimized_query

logger = logging.getLogger(__name__)

# 泛型类型变量
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """优化的仓库基类。"""

    def __init__(self, model: Type[ModelType], cache_prefix: str = ""):
        """初始化仓库。

        Args:
            model: SQLAlchemy模型类
            cache_prefix: 缓存键前缀
        """
        self.model = model
        self.cache_prefix = cache_prefix or model.__name__.lower()

    @optimized_query(cache_ttl=300)
    async def get(
        self,
        session: AsyncSession,
        id: UUID,
        use_cache: bool = True
    ) -> Optional[ModelType]:
        """根据ID获取记录。

        Args:
            session: 数据库会话
            id: 记录ID
            use_cache: 是否使用缓存

        Returns:
            模型实例或None
        """
        cache_key = f"{self.cache_prefix}:{id}" if use_cache else None

        if use_cache:
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached

        query = select(self.model).where(self.model.id == id)
        result = await session.execute(query)
        entity = result.scalar_one_or_none()

        if entity and use_cache:
            await cache_manager.set(cache_key, entity, ttl=300)

        return entity

    @optimized_query(cache_ttl=60)
    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        use_cache: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """获取多条记录。

        Args:
            session: 数据库会话
            skip: 跳过的记录数
            limit: 返回的记录数限制
            use_cache: 是否使用缓存
            filters: 过滤条件
            order_by: 排序字段

        Returns:
            模型实例列表
        """
        # 生成缓存键
        cache_key = None
        if use_cache:
            cache_key = f"{self.cache_prefix}:multi:{skip}:{limit}:{hash(str(filters))}:{order_by}"

            cached = await cache_manager.get(cache_key)
            if cached:
                return cached

        # 构建查询
        query = select(self.model)

        # 添加过滤条件
        if filters:
            for column_name, value in filters.items():
                if hasattr(self.model, column_name):
                    query = query.where(getattr(self.model, column_name) == value)

        # 添加排序
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))

        # 添加分页
        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        entities = result.scalars().all()

        if use_cache:
            await cache_manager.set(cache_key, list(entities), ttl=60)

        return entities

    @optimized_query(cache_ttl=300)
    async def get_by_field(
        self,
        session: AsyncSession,
        field_name: str,
        field_value: Any,
        use_cache: bool = True
    ) -> Optional[ModelType]:
        """根据字段值获取记录。

        Args:
            session: 数据库会话
            field_name: 字段名
            field_value: 字段值
            use_cache: 是否使用缓存

        Returns:
            模型实例或None
        """
        if not hasattr(self.model, field_name):
            raise AttributeError(f"模型 {self.model.__name__} 没有字段 {field_name}")

        cache_key = f"{self.cache_prefix}:field:{field_name}:{field_value}" if use_cache else None

        if use_cache:
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached

        query = select(self.model).where(getattr(self.model, field_name) == field_value)
        result = await session.execute(query)
        entity = result.scalar_one_or_none()

        if entity and use_cache:
            await cache_manager.set(cache_key, entity, ttl=300)

        return entity

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType,
        auto_commit: bool = True,
        clear_cache: bool = True
    ) -> ModelType:
        """创建新记录。

        Args:
            session: 数据库会话
            obj_in: 创建数据
            auto_commit: 是否自动提交
            clear_cache: 是否清除相关缓存

        Returns:
            创建的模型实例
        """
        obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in
        db_obj = self.model(**obj_data)

        session.add(db_obj)

        if auto_commit:
            await session.commit()
            await session.refresh(db_obj)

        # 清除相关缓存
        if clear_cache:
            await self._clear_related_cache(db_obj)

        return db_obj

    async def create_multi(
        self,
        session: AsyncSession,
        *,
        objs_in: List[CreateSchemaType],
        auto_commit: bool = True,
        clear_cache: bool = True
    ) -> List[ModelType]:
        """批量创建记录。

        Args:
            session: 数据库会话
            objs_in: 创建数据列表
            auto_commit: 是否自动提交
            clear_cache: 是否清除相关缓存

        Returns:
            创建的模型实例列表
        """
        db_objs = []
        for obj_in in objs_in:
            obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in
            db_obj = self.model(**obj_data)
            db_objs.append(db_obj)
            session.add(db_obj)

        if auto_commit:
            await session.commit()
            for db_obj in db_objs:
                await session.refresh(db_obj)

        # 清除相关缓存
        if clear_cache:
            for db_obj in db_objs:
                await self._clear_related_cache(db_obj)

        return db_objs

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        auto_commit: bool = True,
        clear_cache: bool = True
    ) -> ModelType:
        """更新记录。

        Args:
            session: 数据库会话
            db_obj: 数据库对象
            obj_in: 更新数据
            auto_commit: 是否自动提交
            clear_cache: 是否清除相关缓存

        Returns:
            更新后的模型实例
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)

        if auto_commit:
            await session.commit()
            await session.refresh(db_obj)

        # 清除相关缓存
        if clear_cache:
            await self._clear_related_cache(db_obj)

        return db_obj

    async def delete(
        self,
        session: AsyncSession,
        *,
        id: UUID,
        auto_commit: bool = True,
        clear_cache: bool = True
    ) -> Optional[ModelType]:
        """删除记录。

        Args:
            session: 数据库会话
            id: 记录ID
            auto_commit: 是否自动提交
            clear_cache: 是否清除相关缓存

        Returns:
            删除的模型实例或None
        """
        db_obj = await self.get(session, id=id, use_cache=False)
        if db_obj:
            await session.delete(db_obj)

            if auto_commit:
                await session.commit()

            # 清除相关缓存
            if clear_cache:
                await self._clear_related_cache(db_obj)

        return db_obj

    async def count(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> int:
        """计算记录数量。

        Args:
            session: 数据库会话
            filters: 过滤条件
            use_cache: 是否使用缓存

        Returns:
            记录数量
        """
        cache_key = f"{self.cache_prefix}:count:{hash(str(filters))}" if use_cache else None

        if use_cache:
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                return cached

        query = select(func.count(self.model.id))

        if filters:
            for column_name, value in filters.items():
                if hasattr(self.model, column_name):
                    query = query.where(getattr(self.model, column_name) == value)

        result = await session.execute(query)
        count = result.scalar()

        if use_cache:
            await cache_manager.set(cache_key, count, ttl=120)

        return count

    async def exists(
        self,
        session: AsyncSession,
        id: UUID,
        use_cache: bool = True
    ) -> bool:
        """检查记录是否存在。

        Args:
            session: 数据库会话
            id: 记录ID
            use_cache: 是否使用缓存

        Returns:
            是否存在
        """
        cache_key = f"{self.cache_prefix}:exists:{id}" if use_cache else None

        if use_cache:
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                return cached

        count = await self.count(session, filters={"id": id}, use_cache=False)

        if use_cache:
            await cache_manager.set(cache_key, count > 0, ttl=300)

        return count > 0

    async def _clear_related_cache(self, db_obj: ModelType) -> None:
        """清除相关缓存。

        Args:
            db_obj: 数据库对象
        """
        # 清除单个对象缓存
        await cache_manager.delete(f"{self.cache_prefix}:{db_obj.id}")

        # 清除exists缓存
        await cache_manager.delete(f"{self.cache_prefix}:exists:{db_obj.id}")

        # 清除字段缓存
        for field_name in ['code', 'email', 'name']:  # 常见字段
            if hasattr(db_obj, field_name):
                field_value = getattr(db_obj, field_name)
                if field_value:
                    await cache_manager.delete(f"{self.cache_prefix}:field:{field_name}:{field_value}")

        # 清除列表缓存（使用模式匹配）
        await cache_manager.clear_pattern(f"{self.cache_prefix}:multi:*")
        await cache_manager.clear_pattern(f"{self.cache_prefix}:count:*")

    async def bulk_update(
        self,
        session: AsyncSession,
        *,
        updates: List[Tuple[UUID, Dict[str, Any]]],
        auto_commit: bool = True
    ) -> int:
        """批量更新记录。

        Args:
            session: 数据库会话
            updates: 更新列表，包含(ID, 更新数据)的元组
            auto_commit: 是否自动提交

        Returns:
            更新的记录数
        """
        if not updates:
            return 0

        # 批量更新
        for obj_id, update_data in updates:
            query = (
                update(self.model)
                .where(self.model.id == obj_id)
                .values(**update_data)
            )
            await session.execute(query)

        if auto_commit:
            await session.commit()

        # 清除所有相关缓存
        await cache_manager.clear_pattern(f"{self.cache_prefix}:*")

        return len(updates)

    async def get_with_relations(
        self,
        session: AsyncSession,
        id: UUID,
        relations: List[str],
        use_cache: bool = False
    ) -> Optional[ModelType]:
        """获取记录及其关联数据。

        Args:
            session: 数据库会话
            id: 记录ID
            relations: 关联关系列表
            use_cache: 是否使用缓存

        Returns:
            模型实例或None
        """
        cache_key = f"{self.cache_prefix}:{id}:relations:{'+'.join(relations)}" if use_cache else None

        if use_cache:
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached

        query = select(self.model).where(self.model.id == id)

        # 预加载关联关系
        for relation in relations:
            if hasattr(self.model, relation):
                query = query.options(selectinload(getattr(self.model, relation)))

        result = await session.execute(query)
        entity = result.scalar_one_or_none()

        if entity and use_cache:
            await cache_manager.set(cache_key, entity, ttl=180)  # 关联数据缓存时间较短

        return entity

    async def health_check(self, session: AsyncSession) -> Dict[str, Any]:
        """仓库健康检查。

        Args:
            session: 数据库会话

        Returns:
            健康检查结果
        """
        try:
            # 测试基本查询
            count = await self.count(session, use_cache=False)

            # 测试缓存
            cache_status = await cache_manager.exists(f"{self.cache_prefix}:health")

            return {
                'status': 'healthy',
                'model': self.model.__name__,
                'record_count': count,
                'cache_available': cache_status is not None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"仓库健康检查失败: {e}")
            return {
                'status': 'unhealthy',
                'model': self.model.__name__,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }