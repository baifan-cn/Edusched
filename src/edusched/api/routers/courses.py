"""课程管理路由。"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from edusched.domain.models import Course
from edusched.infrastructure.database.connection import get_db
from edusched.infrastructure.database.models import Course as CourseTable

router = APIRouter()


@router.get("/", response_model=List[Course])
async def list_courses(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    subject_id: UUID = None,
    db: AsyncSession = Depends(get_db)
) -> List[Course]:
    """获取课程列表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(CourseTable).where(CourseTable.tenant_id == tenant_id)
    
    if subject_id:
        query = query.where(CourseTable.subject_id == subject_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    courses = result.scalars().all()
    
    return [Course.model_validate(course) for course in courses]


@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Course:
    """获取课程详情。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(CourseTable).where(
        CourseTable.id == course_id,
        CourseTable.tenant_id == tenant_id
    )
    
    result = await db.execute(query)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    return Course.model_validate(course)


@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: Course,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Course:
    """创建课程。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 检查课程代码是否已存在
    existing_query = select(CourseTable).where(
        CourseTable.tenant_id == tenant_id,
        CourseTable.code == course.code
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="课程代码已存在"
        )
    
    # 创建课程记录
    course_data = course.model_dump()
    course_data["tenant_id"] = tenant_id
    course_data["created_by"] = "system"
    
    db_course = CourseTable(**course_data)
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    
    return Course.model_validate(db_course)


@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: UUID,
    course_update: Course,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Course:
    """更新课程信息。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找现有课程
    query = select(CourseTable).where(
        CourseTable.id == course_id,
        CourseTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_course = result.scalar_one_or_none()
    
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 检查代码冲突
    if course_update.code != db_course.code:
        existing_query = select(CourseTable).where(
            CourseTable.tenant_id == tenant_id,
            CourseTable.code == course_update.code,
            CourseTable.id != course_id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="课程代码已存在"
            )
    
    # 更新字段
    update_data = course_update.model_dump(exclude_unset=True)
    update_data["updated_by"] = "system"
    
    for field, value in update_data.items():
        if hasattr(db_course, field):
            setattr(db_course, field, value)
    
    await db.commit()
    await db.refresh(db_course)
    
    return Course.model_validate(db_course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> None:
    """删除课程。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找课程
    query = select(CourseTable).where(
        CourseTable.id == course_id,
        CourseTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_course = result.scalar_one_or_none()
    
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # TODO: 检查是否有依赖数据（教学段等）
    
    await db.delete(db_course)
    await db.commit()