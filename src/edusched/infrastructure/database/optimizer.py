"""数据库查询优化模块。

提供查询性能监控、索引建议、查询优化等功能。
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from functools import wraps

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query

from edusched.infrastructure.cache.manager import cache_manager

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """查询性能指标。"""
    query: str
    execution_time: float
    timestamp: datetime
    row_count: int
    cache_hit: bool = False
    error: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndexSuggestion:
    """索引建议。"""
    table_name: str
    column_name: str
    index_type: str
    estimated_improvement: float
    current_selectivity: float
    suggestion: str


class QueryOptimizer:
    """查询优化器。"""

    def __init__(self):
        """初始化查询优化器。"""
        self.query_history: List[QueryMetrics] = []
        self.slow_query_threshold = 1.0  # 秒
        self.max_history_size = 1000

    @asynccontextmanager
    async def monitor_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        cache_key: Optional[str] = None,
        cache_ttl: int = 300
    ):
        """监控查询执行。"""
        start_time = time.time()
        error = None
        row_count = 0
        cache_hit = False

        try:
            # 尝试从缓存获取结果
            if cache_key:
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    cache_hit = True
                    execution_time = time.time() - start_time
                    metrics = QueryMetrics(
                        query=query,
                        execution_time=execution_time,
                        timestamp=datetime.now(),
                        row_count=len(cached_result) if isinstance(cached_result, list) else 1,
                        cache_hit=True,
                        parameters=parameters or {}
                    )
                    self._record_query(metrics)
                    yield cached_result
                    return

            # 执行查询
            yield None  # 实际查询执行在外部

        except Exception as e:
            error = str(e)
            raise
        finally:
            execution_time = time.time() - start_time
            metrics = QueryMetrics(
                query=query,
                execution_time=execution_time,
                timestamp=datetime.now(),
                row_count=row_count,
                cache_hit=cache_hit,
                error=error,
                parameters=parameters or {}
            )
            self._record_query(metrics)

            if not cache_hit and execution_time > self.slow_query_threshold:
                logger.warning(f"慢查询检测: {query[:100]}... 执行时间: {execution_time:.3f}s")

    def _record_query(self, metrics: QueryMetrics) -> None:
        """记录查询指标。"""
        self.query_history.append(metrics)

        # 限制历史记录大小
        if len(self.query_history) > self.max_history_size:
            self.query_history = self.query_history[-self.max_history_size:]

    def get_slow_queries(self, limit: int = 10) -> List[QueryMetrics]:
        """获取慢查询列表。"""
        return sorted(
            [q for q in self.query_history if q.execution_time > self.slow_query_threshold],
            key=lambda x: x.execution_time,
            reverse=True
        )[:limit]

    def get_query_statistics(self) -> Dict[str, Any]:
        """获取查询统计信息。"""
        if not self.query_history:
            return {}

        total_queries = len(self.query_history)
        cached_queries = sum(1 for q in self.query_history if q.cache_hit)
        error_queries = sum(1 for q in self.query_history if q.error)

        execution_times = [q.execution_time for q in self.query_history]
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        min_execution_time = min(execution_times)

        return {
            'total_queries': total_queries,
            'cached_queries': cached_queries,
            'cache_hit_rate': (cached_queries / total_queries * 100) if total_queries > 0 else 0,
            'error_queries': error_queries,
            'error_rate': (error_queries / total_queries * 100) if total_queries > 0 else 0,
            'avg_execution_time': avg_execution_time,
            'max_execution_time': max_execution_time,
            'min_execution_time': min_execution_time,
            'slow_queries': len(self.get_slow_queries())
        }

    def get_index_suggestions(self, session: AsyncSession) -> List[IndexSuggestion]:
        """获取索引建议。"""
        suggestions = []

        # 分析查询历史中的常见模式
        query_patterns = self._analyze_query_patterns()

        # 获取数据库统计信息
        stats = self._get_database_stats(session)

        # 生成索引建议
        for pattern, count in query_patterns.items():
            if count > 10:  # 频繁查询的表
                table_name = pattern.get('table')
                columns = pattern.get('columns', [])

                if table_name and columns:
                    suggestion = self._create_index_suggestion(table_name, columns, stats)
                    if suggestion:
                        suggestions.append(suggestion)

        return suggestions

    def _analyze_query_patterns(self) -> Dict[str, Dict[str, Any]]:
        """分析查询模式。"""
        patterns = {}

        for metrics in self.query_history:
            if metrics.error or metrics.cache_hit:
                continue

            # 简化的查询模式分析
            query_lower = metrics.query.lower()

            # 提取表名
            if 'from' in query_lower:
                parts = query_lower.split('from')
                if len(parts) > 1:
                    table_part = parts[1].strip().split()[0]
                    table_name = table_part.strip('"').strip("'")

                    if table_name not in patterns:
                        patterns[table_name] = {
                            'table': table_name,
                            'columns': [],
                            'count': 0,
                            'avg_time': 0
                        }

                    patterns[table_name]['count'] += 1

        return patterns

    async def _get_database_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """获取数据库统计信息。"""
        try:
            # PostgreSQL 统计查询
            result = await session.execute(text("""
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins,
                    n_tup_upd,
                    n_tup_del,
                    n_live_tup,
                    n_dead_tup,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
            """))

            stats = {}
            for row in result:
                stats[row.tablename] = dict(row)

            return stats
        except Exception as e:
            logger.warning(f"获取数据库统计信息失败: {e}")
            return {}

    def _create_index_suggestion(
        self,
        table_name: str,
        columns: List[str],
        stats: Dict[str, Any]
    ) -> Optional[IndexSuggestion]:
        """创建索引建议。"""
        table_stats = stats.get(table_name, {})
        live_tuples = table_stats.get('n_live_tup', 0)
        dead_tuples = table_stats.get('n_dead_tup', 0)

        # 如果表数据量很小，不需要索引
        if live_tuples < 1000:
            return None

        # 死元组比例过高，建议清理
        if live_tuples > 0 and dead_tuples / live_tuples > 0.2:
            return IndexSuggestion(
                table_name=table_name,
                column_name="VACUUM",
                index_type="maintenance",
                estimated_improvement=15.0,
                current_selectivity=0.0,
                suggestion=f"表 {table_name} 需要执行 VACUUM，死元组比例: {dead_tuples/live_tuples:.2%}"
            )

        return None


class QueryBuilder:
    """查询构建器，提供优化的查询构建方法。"""

    @staticmethod
    def optimized_select(
        session: AsyncSession,
        table_name: str,
        columns: List[str] = None,
        where_conditions: List[str] = None,
        order_by: List[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        join_tables: List[str] = None
    ) -> str:
        """构建优化的SELECT查询。"""
        if columns is None:
            columns = ["*"]

        # 构建SELECT子句
        select_clause = ", ".join(columns)

        # 构建FROM子句
        from_clause = table_name

        # 构建JOIN子句
        join_clause = ""
        if join_tables:
            for join_table in join_tables:
                join_clause += f" JOIN {join_table} ON {table_name}.id = {join_table}.{table_name}_id"

        # 构建WHERE子句
        where_clause = ""
        if where_conditions:
            where_clause = " WHERE " + " AND ".join(where_conditions)

        # 构建ORDER BY子句
        order_clause = ""
        if order_by:
            order_clause = " ORDER BY " + ", ".join(order_by)

        # 构建LIMIT和OFFSET子句
        limit_clause = ""
        if limit is not None:
            limit_clause = f" LIMIT {limit}"
            if offset is not None:
                limit_clause += f" OFFSET {offset}"

        return f"SELECT {select_clause} FROM {from_clause}{join_clause}{where_clause}{order_clause}{limit_clause}"

    @staticmethod
    def add_query_hints(query: str, hints: List[str]) -> str:
        """为查询添加优化提示。"""
        if not hints:
            return query

        # 在SELECT后添加提示
        if query.lower().startswith('select'):
            select_pos = query.find('select') + 6
            hints_str = "/*+ " + " ".join(hints) + " */"
            return query[:select_pos] + " " + hints_str + query[select_pos:]

        return query


# 全局查询优化器实例
query_optimizer = QueryOptimizer()


def optimized_query(
    cache_key_prefix: str = "",
    cache_ttl: int = 300,
    slow_query_threshold: float = 1.0
):
    """优化查询装饰器。"""
    def decorator(func):
        @wraps(func)
        async def wrapper(session: AsyncSession, *args, **kwargs):
            # 生成缓存键
            cache_key = f"{cache_key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 监控查询执行
            async with query_optimizer.monitor_query(
                query=func.__name__,
                parameters={'args': args, 'kwargs': kwargs},
                cache_key=cache_key,
                cache_ttl=cache_ttl
            ) as cached_result:
                if cached_result is not None:
                    return cached_result

                # 执行原始查询
                start_time = time.time()
                result = await func(session, *args, **kwargs)
                execution_time = time.time() - start_time

                # 如果查询缓慢，记录警告
                if execution_time > slow_query_threshold:
                    logger.warning(f"慢查询: {func.__name__} 执行时间: {execution_time:.3f}s")

                # 缓存结果
                if cache_key:
                    await cache_manager.set(cache_key, result, cache_ttl)

                return result

        return wrapper
    return decorator


async def get_query_performance_report() -> Dict[str, Any]:
    """获取查询性能报告。"""
    stats = query_optimizer.get_query_statistics()
    slow_queries = query_optimizer.get_slow_queries()

    return {
        'statistics': stats,
        'slow_queries': [
            {
                'query': q.query[:100] + '...' if len(q.query) > 100 else q.query,
                'execution_time': q.execution_time,
                'timestamp': q.timestamp.isoformat(),
                'row_count': q.row_count
            }
            for q in slow_queries
        ],
        'recommendations': _generate_performance_recommendations(stats)
    }


def _generate_performance_recommendations(stats: Dict[str, Any]) -> List[str]:
    """生成性能优化建议。"""
    recommendations = []

    if stats.get('cache_hit_rate', 0) < 50:
        recommendations.append("建议增加缓存使用率，当前缓存命中率较低")

    if stats.get('error_rate', 0) > 5:
        recommendations.append("查询错误率较高，建议检查数据库连接和SQL语法")

    if stats.get('avg_execution_time', 0) > 0.5:
        recommendations.append("平均查询执行时间较长，建议优化SQL语句或添加索引")

    if stats.get('slow_queries', 0) > 10:
        recommendations.append("存在大量慢查询，建议分析查询模式并添加适当的索引")

    return recommendations