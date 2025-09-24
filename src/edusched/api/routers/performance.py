"""性能监控API路由。"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from edusched.api.deps import get_db, get_current_active_user
from edusched.infrastructure.cache.manager import cache_manager
from edusched.infrastructure.database.optimizer import get_query_performance_report
from edusched.domain.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """获取缓存统计信息。"""
    try:
        # 这里简化处理，实际中需要连接Redis获取统计信息
        stats = {
            "status": "healthy",
            "cache_type": "redis" if cache_manager._redis else "local",
            "local_cache_size": len(cache_manager._local_cache),
            "timestamp": datetime.now().isoformat()
        }

        # 如果Redis可用，获取更多统计信息
        if cache_manager._redis:
            try:
                redis_client = cache_manager._redis
                # 获取Redis信息
                info = await redis_client.info("memory")
                stats.update({
                    "redis_used_memory": info.get("used_memory_human", "N/A"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_total_commands_processed": info.get("total_commands_processed", 0)
                })
            except Exception as e:
                logger.warning(f"获取Redis统计信息失败: {e}")
                stats["redis_status"] = "error"

        return stats
    except Exception as e:
        logger.error(f"获取缓存统计信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取缓存统计信息失败")


@router.get("/cache/clear")
async def clear_cache(
    pattern: str = Query("*", description="要清除的缓存模式"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """清除缓存。"""
    try:
        cleared_count = await cache_manager.clear_pattern(pattern)

        return {
            "success": True,
            "cleared_count": cleared_count,
            "pattern": pattern,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清除缓存失败")


@router.get("/queries/performance")
async def get_query_performance(
    hours: int = Query(24, description="查询历史时间范围（小时）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """获取查询性能报告。"""
    try:
        report = await get_query_performance_report()

        # 过滤指定时间范围内的数据
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # 过滤慢查询
        filtered_slow_queries = [
            q for q in report.get("slow_queries", [])
            if datetime.fromisoformat(q["timestamp"]) > cutoff_time
        ]

        return {
            "statistics": report.get("statistics", {}),
            "slow_queries": filtered_slow_queries,
            "recommendations": report.get("recommendations", []),
            "time_range_hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取查询性能报告失败: {e}")
        raise HTTPException(status_code=500, detail="获取查询性能报告失败")


@router.get("/queries/slow")
async def get_slow_queries(
    limit: int = Query(10, description="返回的慢查询数量"),
    min_time: float = Query(1.0, description="最小执行时间（秒）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """获取慢查询列表。"""
    try:
        from edusched.infrastructure.database.optimizer import query_optimizer

        slow_queries = query_optimizer.get_slow_queries(limit)

        # 过滤满足最小执行时间要求的查询
        filtered_queries = [
            {
                "query": q.query[:200] + "..." if len(q.query) > 200 else q.query,
                "execution_time": q.execution_time,
                "timestamp": q.timestamp.isoformat(),
                "row_count": q.row_count,
                "cache_hit": q.cache_hit,
                "error": q.error
            }
            for q in slow_queries
            if q.execution_time >= min_time
        ]

        return {
            "slow_queries": filtered_queries,
            "total_count": len(filtered_queries),
            "min_time": min_time,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取慢查询列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取慢查询列表失败")


@router.get("/database/stats")
async def get_database_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """获取数据库统计信息。"""
    try:
        # 获取表统计信息
        result = await db.execute("""
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
            ORDER BY n_live_tup DESC
        """)

        tables_stats = []
        for row in result:
            tables_stats.append({
                "schema": row.schemaname,
                "table": row.tablename,
                "live_tuples": row.n_live_tup,
                "dead_tuples": row.n_dead_tup,
                "inserts": row.n_tup_ins,
                "updates": row.n_tup_upd,
                "deletes": row.n_tup_del,
                "last_vacuum": row.last_vacuum.isoformat() if row.last_vacuum else None,
                "last_autovacuum": row.last_autovacuum.isoformat() if row.last_autovacuum else None,
                "dead_tuple_ratio": round(row.n_dead_tup / row.n_live_tup, 4) if row.n_live_tup > 0 else 0
            })

        # 获取索引统计信息
        index_result = await db.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
        """)

        indexes_stats = []
        for row in index_result:
            indexes_stats.append({
                "schema": row.schemaname,
                "table": row.tablename,
                "index": row.indexname,
                "scans": row.idx_scan,
                "tuples_read": row.idx_tup_read,
                "tuples_fetched": row.idx_tup_fetch
            })

        # 获取连接统计信息
        connection_result = await db.execute("""
            SELECT
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction_connections
            FROM pg_stat_activity
            WHERE datname = current_database()
        """)

        connection_stats = dict(connection_result.first())

        return {
            "tables": tables_stats,
            "indexes": indexes_stats,
            "connections": connection_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取数据库统计信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据库统计信息失败")


@router.post("/cache/warmup")
async def cache_warmup(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """缓存预热。"""
    try:
        # 预热常用数据缓存
        warmed_up_count = 0

        # 预热学校列表
        from edusched.infrastructure.database.repository import BaseRepository
        from edusched.infrastructure.database.models import SchoolModel

        school_repo = BaseRepository(SchoolModel, "schools")
        schools = await school_repo.get_multi(db, limit=100, use_cache=False)
        warmed_up_count += len(schools)

        # 预热教师列表
        from edusched.infrastructure.database.models import TeacherModel

        teacher_repo = BaseRepository(TeacherModel, "teachers")
        teachers = await teacher_repo.get_multi(db, limit=500, use_cache=False)
        warmed_up_count += len(teachers)

        # 预热课程列表
        from edusched.infrastructure.database.models import CourseModel

        course_repo = BaseRepository(CourseModel, "courses")
        courses = await course_repo.get_multi(db, limit=200, use_cache=False)
        warmed_up_count += len(courses)

        return {
            "success": True,
            "warmed_up_count": warmed_up_count,
            "schools_count": len(schools),
            "teachers_count": len(teachers),
            "courses_count": len(courses),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"缓存预热失败: {e}")
        raise HTTPException(status_code=500, detail="缓存预热失败")


@router.get("/health/detailed")
async def get_detailed_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """获取详细的健康状态信息。"""
    try:
        # 数据库健康检查
        try:
            await db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        # 缓存健康检查
        cache_status = "healthy"
        if cache_manager._redis:
            try:
                redis_client = cache_manager._redis
                await redis_client.ping()
            except Exception as e:
                cache_status = f"unhealthy: {str(e)}"
        else:
            cache_status = "using local cache"

        # 查询性能健康检查
        query_stats = query_optimizer.get_query_statistics()
        query_status = "healthy"
        if query_stats.get("error_rate", 0) > 5:
            query_status = "warning: high error rate"
        elif query_stats.get("avg_execution_time", 0) > 1.0:
            query_status = "warning: slow queries"

        return {
            "status": "healthy" if all([
                "unhealthy" not in db_status,
                "unhealthy" not in cache_status,
                "warning" not in query_status
            ]) else "degraded",
            "components": {
                "database": {"status": db_status},
                "cache": {"status": cache_status},
                "queries": {"status": query_status}
            },
            "statistics": query_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取详细健康状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取详细健康状态失败")