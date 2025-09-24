"""领域服务使用示例。

演示如何使用领域服务层进行业务操作。
"""

from uuid import uuid4
from datetime import datetime

from ..models import School, Teacher, Course, Timetable, SchedulingStatus
from .school_service import SchoolService
from .teacher_service import TeacherService
from .course_service import CourseService
from .timetable_service import TimetableService
from .scheduling_domain_service import SchedulingDomainService


async def school_management_example():
    """学校管理示例。"""
    # 创建服务实例
    tenant_id = "demo_school_001"
    school_service = SchoolService(tenant_id)

    # 创建学校
    school = School(
        name="示范中学",
        code="DEMO001",
        address="北京市朝阳区示范路1号",
        phone="010-12345678",
        email="info@demo.edu.cn",
        academic_year="2024-2025",
        semester="fall",
        timezone="Asia/Shanghai",
        tenant_id=tenant_id
    )

    # 保存学校
    result = await school_service.create(school)
    if result.success:
        print(f"学校创建成功: {result.data.name} (ID: {result.data.id})")
        school_id = result.data.id

        # 激活学校
        activate_result = await school_service.activate_school(school_id)
        if activate_result.success:
            print("学校已激活")
    else:
        print(f"创建失败: {result.error}")


async def teacher_management_example():
    """教师管理示例。"""
    tenant_id = "demo_school_001"
    teacher_service = TeacherService(tenant_id)

    # 创建教师
    teacher = Teacher(
        employee_id="T2024001",
        name="李老师",
        email="li@demo.edu.cn",
        phone="13800138000",
        department="数学系",
        title="高级教师",
        max_hours_per_day=6,
        max_hours_per_week=30,
        is_active=True,
        tenant_id=tenant_id
    )

    # 保存教师
    result = await teacher_service.create(teacher)
    if result.success:
        print(f"教师创建成功: {result.data.name}")
        teacher_id = result.data.id

        # 计算工作负荷
        workload = await teacher_service.calculate_teacher_workload(teacher_id)
        if workload.success:
            print(f"工作负荷: {workload.data}")
    else:
        print(f"创建失败: {result.error}")


async def course_management_example():
    """课程管理示例。"""
    tenant_id = "demo_school_001"
    course_service = CourseService(tenant_id)

    # 创建课程
    course = Course(
        subject_id=uuid4(),  # 需要先创建学科
        name="高等数学",
        code="MATH101",
        description="高等数学基础课程",
        credits=4.0,
        hours_per_week=4,
        total_hours=64,
        is_active=True,
        tenant_id=tenant_id
    )

    # 保存课程
    result = await course_service.create(course)
    if result.success:
        print(f"课程创建成功: {result.data.name}")

        # 复制课程
        duplicate_result = await course_service.duplicate_course(
            result.data.id,
            "高等数学（下学期）",
            "MATH102",
            copy_sections=False
        )
        if duplicate_result.success:
            print(f"课程复制成功: {duplicate_result.data.name}")
    else:
        print(f"创建失败: {result.error}")


async def timetable_management_example():
    """时间表管理示例。"""
    tenant_id = "demo_school_001"
    timetable_service = TimetableService(tenant_id)
    scheduling_service = SchedulingDomainService(tenant_id)

    # 创建时间表
    timetable = Timetable(
        calendar_id=uuid4(),  # 需要先创建日历
        name="2024秋季学期课表",
        description="示范中学2024年秋季学期课程表",
        status=SchedulingStatus.DRAFT,
        constraints=[],  # 需要先创建约束
        tenant_id=tenant_id
    )

    # 保存时间表
    result = await timetable_service.create(timetable)
    if result.success:
        print(f"时间表创建成功: {result.data.name}")
        timetable_id = result.data.id

        # 开始调度
        job_result = await scheduling_service.start_scheduling(timetable_id)
        if job_result.success:
            print(f"调度任务已启动: {job_result.data.id}")

            # 检查调度状态
            status_result = await scheduling_service.get_scheduling_status(timetable_id)
            if status_result.success:
                print(f"调度进度: {status_result.data['progress']*100:.1f}%")

        # 验证约束
        validation_result = await scheduling_service.validate_constraints(timetable_id)
        if validation_result.success:
            summary = validation_result.data["summary"]
            print(f"约束验证结果:")
            print(f"  硬约束: {summary['satisfied_hard_constraints']}/{summary['total_hard_constraints']}")
            print(f"  软约束: {summary['satisfied_soft_constraints']}/{summary['total_soft_constraints']}")
            print(f"  总体得分: {summary['overall_score']:.2f}")
    else:
        print(f"创建失败: {result.error}")


async def main():
    """运行所有示例。"""
    print("=== 领域服务使用示例 ===\n")

    print("1. 学校管理示例:")
    await school_management_example()
    print("\n" + "="*50 + "\n")

    print("2. 教师管理示例:")
    await teacher_management_example()
    print("\n" + "="*50 + "\n")

    print("3. 课程管理示例:")
    await course_management_example()
    print("\n" + "="*50 + "\n")

    print("4. 时间表管理示例:")
    await timetable_management_example()
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())