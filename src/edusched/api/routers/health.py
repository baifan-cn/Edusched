"""健康检查路由。"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from edusched.infrastructure.database.connection import get_db, db_manager

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """基础健康检查。"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "edusched-api",
    }


@router.get("/health/detailed")
async def detailed_health_check(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """详细健康检查。"""
    tenant_id = getattr(request.state, "tenant_id", "unknown")
    
    # 检查数据库连接
    db_status = "healthy"
    try:
        db_healthy = await db_manager.health_check()
        db_status = "healthy" if db_healthy else "unhealthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # 检查Redis连接（TODO: 实现Redis健康检查）
    redis_status = "not_implemented"
    
    # 检查租户信息
    tenant_info = {
        "id": tenant_id,
        "status": "active" if tenant_id != "unknown" else "unknown"
    }
    
    # 总体状态
    overall_status = "healthy"
    if db_status != "healthy":
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "edusched-api",
        "components": {
            "database": db_status,
            "redis": redis_status,
            "tenant": tenant_info,
        },
        "version": "0.1.0",
        "environment": "development",  # TODO: 从配置获取
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """就绪检查。"""
    # 检查所有关键服务是否就绪
    db_ready = await db_manager.health_check()
    
    ready = db_ready  # 暂时只检查数据库
    
    return {
        "ready": ready,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": db_ready,
        }
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """存活检查。"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
    }