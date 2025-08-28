"""教师管理路由。"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from edusched.domain.models import Teacher
from edusched.infrastructure.database.connection import get_db
from edusched.infrastructure.database.models import Teacher as TeacherTable

router = APIRouter()


@router.get("/", response_model=List[Teacher])
async def list_teachers(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    department: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Teacher]:
    """获取教师列表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(TeacherTable).where(TeacherTable.tenant_id == tenant_id)
    
    if department:
        query = query.where(TeacherTable.department == department)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    teachers = result.scalars().all()
    
    return [Teacher.model_validate(teacher) for teacher in teachers]


@router.get("/{teacher_id}", response_model=Teacher)
async def get_teacher(
    teacher_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Teacher:
    """获取教师详情。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(TeacherTable).where(
        TeacherTable.id == teacher_id,
        TeacherTable.tenant_id == tenant_id
    )
    
    result = await db.execute(query)
    teacher = result.scalar_one_or_none()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师不存在"
        )
    
    return Teacher.model_validate(teacher)


@router.post("/", response_model=Teacher, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher: Teacher,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Teacher:
    """创建教师。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 检查工号是否已存在
    existing_query = select(TeacherTable).where(
        TeacherTable.tenant_id == tenant_id,
        TeacherTable.employee_id == teacher.employee_id
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工号已存在"
        )
    
    # 创建教师记录
    teacher_data = teacher.model_dump()
    teacher_data["tenant_id"] = tenant_id
    teacher_data["created_by"] = "system"
    
    db_teacher = TeacherTable(**teacher_data)
    db.add(db_teacher)
    await db.commit()
    await db.refresh(db_teacher)
    
    return Teacher.model_validate(db_teacher)


@router.put("/{teacher_id}", response_model=Teacher)
async def update_teacher(
    teacher_id: UUID,
    teacher_update: Teacher,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Teacher:
    """更新教师信息。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找现有教师
    query = select(TeacherTable).where(
        TeacherTable.id == teacher_id,
        TeacherTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_teacher = result.scalar_one_or_none()
    
    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师不存在"
        )
    
    # 检查工号冲突
    if teacher_update.employee_id != db_teacher.employee_id:
        existing_query = select(TeacherTable).where(
            TeacherTable.tenant_id == tenant_id,
            TeacherTable.employee_id == teacher_update.employee_id,
            TeacherTable.id != teacher_id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工号已存在"
            )
    
    # 更新字段
    update_data = teacher_update.model_dump(exclude_unset=True)
    update_data["updated_by"] = "system"
    
    for field, value in update_data.items():
        if hasattr(db_teacher, field):
            setattr(db_teacher, field, value)
    
    await db.commit()
    await db.refresh(db_teacher)
    
    return Teacher.model_validate(db_teacher)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> None:
    """删除教师。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找教师
    query = select(TeacherTable).where(
        TeacherTable.id == teacher_id,
        TeacherTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_teacher = result.scalar_one_or_none()
    
    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师不存在"
        )
    
    # TODO: 检查是否有依赖数据（教学段等）
    
    await db.delete(db_teacher)
    await db.commit()