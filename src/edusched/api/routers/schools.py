"""学校管理路由。"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from edusched.domain.models import School
from edusched.infrastructure.database.connection import get_db
from edusched.infrastructure.database.models import School as SchoolTable

router = APIRouter()


@router.get("/", response_model=List[School])
async def list_schools(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[School]:
    """获取学校列表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = (
        select(SchoolTable)
        .where(SchoolTable.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    schools = result.scalars().all()
    
    return [School.model_validate(school) for school in schools]


@router.get("/{school_id}", response_model=School)
async def get_school(
    school_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> School:
    """获取学校详情。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = (
        select(SchoolTable)
        .where(SchoolTable.id == school_id, SchoolTable.tenant_id == tenant_id)
        .options(selectinload(SchoolTable.campuses))
    )
    
    result = await db.execute(query)
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    return School.model_validate(school)


@router.post("/", response_model=School, status_code=status.HTTP_201_CREATED)
async def create_school(
    school: School,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> School:
    """创建学校。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 检查学校代码是否已存在
    existing_query = select(SchoolTable).where(
        SchoolTable.tenant_id == tenant_id,
        SchoolTable.code == school.code
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="学校代码已存在"
        )
    
    # 创建学校记录
    school_data = school.model_dump()
    school_data["tenant_id"] = tenant_id
    school_data["created_by"] = "system"  # TODO: 从认证获取用户ID
    
    db_school = SchoolTable(**school_data)
    db.add(db_school)
    await db.commit()
    await db.refresh(db_school)
    
    return School.model_validate(db_school)


@router.put("/{school_id}", response_model=School)
async def update_school(
    school_id: UUID,
    school_update: School,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> School:
    """更新学校信息。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找现有学校
    query = select(SchoolTable).where(
        SchoolTable.id == school_id,
        SchoolTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_school = result.scalar_one_or_none()
    
    if not db_school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    # 检查代码冲突（排除自身）
    if school_update.code != db_school.code:
        existing_query = select(SchoolTable).where(
            SchoolTable.tenant_id == tenant_id,
            SchoolTable.code == school_update.code,
            SchoolTable.id != school_id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学校代码已存在"
            )
    
    # 更新字段
    update_data = school_update.model_dump(exclude_unset=True)
    update_data["updated_by"] = "system"  # TODO: 从认证获取用户ID
    
    for field, value in update_data.items():
        if hasattr(db_school, field):
            setattr(db_school, field, value)
    
    await db.commit()
    await db.refresh(db_school)
    
    return School.model_validate(db_school)


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> None:
    """删除学校。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找学校
    query = select(SchoolTable).where(
        SchoolTable.id == school_id,
        SchoolTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_school = result.scalar_one_or_none()
    
    if not db_school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    # TODO: 检查是否有依赖数据（校区、日历等）
    
    await db.delete(db_school)
    await db.commit()


@router.get("/{school_id}/campuses")
async def get_school_campuses(
    school_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取学校的校区列表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 验证学校存在
    school_query = select(SchoolTable).where(
        SchoolTable.id == school_id,
        SchoolTable.tenant_id == tenant_id
    )
    school_result = await db.execute(school_query)
    if not school_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    # TODO: 实现校区查询逻辑
    return {"message": "校区查询功能待实现"}