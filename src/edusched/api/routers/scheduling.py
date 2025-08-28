"""调度引擎路由。"""

from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from edusched.domain.models import SchedulingJob, SchedulingStatus
from edusched.infrastructure.database.connection import get_db
from edusched.infrastructure.database.models import SchedulingJob as SchedulingJobTable
from edusched.scheduling.engine import SchedulingEngine, ConstraintValidator

router = APIRouter()


@router.post("/start", response_model=Dict[str, Any])
async def start_scheduling(
    timetable_id: UUID,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """启动调度任务。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 验证时间表存在
    # TODO: 实现时间表验证逻辑
    
    # 创建调度任务
    job = SchedulingJob(
        tenant_id=tenant_id,
        timetable_id=timetable_id,
        status=SchedulingStatus.RUNNING,
        progress=0.0,
        started_at="2024-01-01T00:00:00Z",  # TODO: 使用当前时间
        worker_id="worker-1",  # TODO: 动态分配工作进程ID
    )
    
    # 保存到数据库
    job_data = job.model_dump()
    db_job = SchedulingJobTable(**job_data)
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    # 在后台启动调度任务
    background_tasks.add_task(
        run_scheduling_task,
        job_id=db_job.id,
        tenant_id=tenant_id,
        timetable_id=timetable_id
    )
    
    return {
        "job_id": str(db_job.id),
        "status": "started",
        "message": "调度任务已启动",
        "timetable_id": str(timetable_id)
    }


@router.get("/jobs", response_model=List[SchedulingJob])
async def list_scheduling_jobs(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[SchedulingJob]:
    """获取调度任务列表。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(SchedulingJobTable).where(SchedulingJobTable.tenant_id == tenant_id)
    
    if status_filter:
        query = query.where(SchedulingJobTable.status == status_filter)
    
    query = query.offset(skip).limit(limit).order_by(SchedulingJobTable.created_at.desc())
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [SchedulingJob.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=SchedulingJob)
async def get_scheduling_job(
    job_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> SchedulingJob:
    """获取调度任务详情。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    query = select(SchedulingJobTable).where(
        SchedulingJobTable.id == job_id,
        SchedulingJobTable.tenant_id == tenant_id
    )
    
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度任务不存在"
        )
    
    return SchedulingJob.model_validate(job)


@router.post("/jobs/{job_id}/cancel")
async def cancel_scheduling_job(
    job_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """取消调度任务。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找任务
    query = select(SchedulingJobTable).where(
        SchedulingJobTable.id == job_id,
        SchedulingJobTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_job = result.scalar_one_or_none()
    
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度任务不存在"
        )
    
    # 检查状态
    if db_job.status not in ["draft", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有草稿或运行中的任务才能取消"
        )
    
    # 更新状态
    db_job.status = "failed"
    db_job.error_message = "任务被用户取消"
    db_job.completed_at = "2024-01-01T00:00:00Z"  # TODO: 使用当前时间
    
    await db.commit()
    
    return {
        "job_id": str(job_id),
        "status": "cancelled",
        "message": "调度任务已取消"
    }


@router.get("/jobs/{job_id}/progress")
async def get_job_progress(
    job_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取调度任务进度。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # 查找任务
    query = select(SchedulingJobTable).where(
        SchedulingJobTable.id == job_id,
        SchedulingJobTable.tenant_id == tenant_id
    )
    result = await db.execute(query)
    db_job = result.scalar_one_or_none()
    
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度任务不存在"
        )
    
    return {
        "job_id": str(job_id),
        "status": db_job.status,
        "progress": float(db_job.progress),
        "started_at": db_job.started_at,
        "completed_at": db_job.completed_at,
        "error_message": db_job.error_message,
        "worker_id": db_job.worker_id,
    }


@router.post("/validate")
async def validate_constraints(
    timetable_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """验证时间表约束。"""
    tenant_id = getattr(request.state, "tenant_id", "default")
    
    # TODO: 实现约束验证逻辑
    # 1. 获取时间表的所有分配
    # 2. 获取相关的教学段、时间段等数据
    # 3. 调用约束验证器
    
    return {
        "timetable_id": str(timetable_id),
        "valid": True,
        "violations": [],
        "message": "约束验证功能待实现"
    }


async def run_scheduling_task(job_id: UUID, tenant_id: str, timetable_id: UUID):
    """在后台运行调度任务。"""
    # TODO: 实现完整的调度任务逻辑
    # 1. 获取时间表数据
    # 2. 创建调度引擎
    # 3. 构建调度问题
    # 4. 求解并更新进度
    # 5. 保存结果
    
    print(f"启动调度任务: {job_id} for timetable {timetable_id}")
    
    # 模拟调度过程
    import asyncio
    import random
    
    for i in range(10):
        await asyncio.sleep(1)  # 模拟计算时间
        progress = (i + 1) / 10
        
        # TODO: 更新数据库中的进度
        print(f"任务 {job_id} 进度: {progress:.1%}")
    
    print(f"调度任务 {job_id} 完成")