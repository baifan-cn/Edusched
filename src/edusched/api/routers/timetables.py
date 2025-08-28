"""时间表管理路由。"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from edusched.domain.models import Timetable, Assignment
from edusched.infrastructure.database.connection import get_db
from edusched.infrastructure.database.models import Timetable as TimetableTable

router = APIRouter()


@router.get("/", response_model=List[Timetable])
async def list_timetables(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    calendar_id: UUID = None,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Timetable]:
    """获取时间表列表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(TimetableTable).where(TimetableTable.tenant_id == tenant_id)
    
    if calendar_id:
        query = query.where(TimetableTable.calendar_id == calendar_id)
    
    if status_filter:
        query = query.where(TimetableTable.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    timetables = result.scalars().all()
    
    return [Timetable.model_validate(timetable) for timetable in timetables]


@router.get("/{timetable_id}", response_model=Timetable)
async def get_timetable(
    timetable_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Timetable:
    """获取时间表详情。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(TimetableTable).where(
        TimetableTable.id == timetable_id,
        TimetableTable.tenant_id == tenant_id
    )
    
    result = await db.execute(query)
    timetable = result.scalar_one_or_none()
    
    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间表不存在"
        )
    
    return Timetable.model_validate(timetable)


@router.post("/", response_model=Timetable, status_code=status.HTTP_201_CREATED)
async def create_timetable(
    timetable: Timetable,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Timetable:
    """创建时间表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 检查时间表名称是否已存在
    existing_query = select(TimetableTable).where(
        TimetableTable.tenant_id == tenant_id,
        TimetableTable.name == timetable.name
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="时间表名称已存在"
        )
    
    # 创建时间表记录
    timetable_data = timetable.model_dump()
    timetable_data["tenant_id"] = tenant_id
    timetable_data["created_by"] = "system"
    
    db_timetable = TimetableTable(**timetable_data)
    db.add(db_timetable)
    await db.commit()
    await db.refresh(db_timetable)
    
    return Timetable.model_validate(db_timetable)


@router.put("/{timetable_id}", response_model=Timetable)
async def update_timetable(
    timetable_id: UUID,
    timetable_update: Timetable,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Timetable:
    """更新时间表信息。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找现有时间表
    query = select(TimetableTable).where(
        TimetableTable.id == timetable_id,
        TimetableTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_timetable = result.scalar_one_or_none()
    
    if not db_timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间表不存在"
        )
    
    # 检查名称冲突
    if timetable_update.name != db_timetable.name:
        existing_query = select(TimetableTable).where(
            TimetableTable.tenant_id == tenant_id,
            TimetableTable.name == timetable_update.name,
            TimetableTable.id != timetable_id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="时间表名称已存在"
            )
    
    # 更新字段
    update_data = timetable_update.model_dump(exclude_unset=True)
    update_data["updated_by"] = "system"
    
    for field, value in update_data.items():
        if hasattr(db_timetable, field):
            setattr(db_timetable, field, value)
    
    await db.commit()
    await db.refresh(db_timetable)
    
    return Timetable.model_validate(db_timetable)


@router.delete("/{timetable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timetable(
    timetable_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> None:
    """删除时间表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找时间表
    query = select(TimetableTable).where(
        TimetableTable.id == timetable_id,
        TimetableTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_timetable = result.scalar_one_or_none()
    
    if not db_timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间表不存在"
        )
    
    # TODO: 检查是否有依赖数据（分配等）
    
    await db.delete(db_timetable)
    await db.commit()


@router.post("/{timetable_id}/publish", response_model=Timetable)
async def publish_timetable(
    timetable_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Timetable:
    """发布时间表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找时间表
    query = select(TimetableTable).where(
        TimetableTable.id == timetable_id,
        TimetableTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_timetable = result.scalar_one_or_none()
    
    if not db_timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间表不存在"
        )
    
    # 检查状态
    if db_timetable.status not in ["optimized", "feasible"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有已优化或可行的时间表才能发布"
        )
    
    # 更新状态
    db_timetable.status = "published"
    db_timetable.published_at = "2024-01-01T00:00:00Z"  # TODO: 使用当前时间
    db_timetable.published_by = "system"
    
    await db.commit()
    await db.refresh(db_timetable)
    
    return Timetable.model_validate(db_timetable)


@router.get("/{timetable_id}/assignments")
async def get_timetable_assignments(
    timetable_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取时间表的分配列表。"""
    # TODO: 实现分配查询逻辑
    return {"message": "分配查询功能待实现"}