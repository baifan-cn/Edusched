"""调度服务示例模块。

演示如何使用两阶段求解策略进行课程表调度。
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from edusched.domain.models import (
    Assignment,
    Section,
    Teacher,
    Timeslot,
    WeekDay,
    SchedulingStatus,
    Timetable,
    ClassGroup,
    Course,
    Room,
    Campus
)
from edusched.scheduling.engine import SchedulingEngine, SchedulingProblem

logger = logging.getLogger(__name__)


class SchedulingService:
    """调度服务类，提供高级调度功能。"""

    def __init__(self, tenant_id: str):
        """初始化调度服务。"""
        self.tenant_id = tenant_id
        self.engine = SchedulingEngine(tenant_id)

    def create_sample_problem(self) -> SchedulingProblem:
        """创建示例调度问题。"""
        problem = self.engine.create_problem()

        # 创建示例教师
        teachers = [
            Teacher(
                id=UUID('11111111-1111-1111-1111-111111111111'),
                tenant_id=self.tenant_id,
                first_name="张",
                last_name="老师",
                email="zhang@school.edu",
                max_hours_per_week=20,
                preferred_time_slots=["monday_09:00", "tuesday_09:00", "wednesday_09:00"],
                is_active=True
            ),
            Teacher(
                id=UUID('22222222-2222-2222-2222-222222222222'),
                tenant_id=self.tenant_id,
                first_name="李",
                last_name="老师",
                email="li@school.edu",
                max_hours_per_week=18,
                preferred_time_slots=["tuesday_14:00", "thursday_14:00", "friday_14:00"],
                is_active=True
            ),
            Teacher(
                id=UUID('33333333-3333-3333-3333-333333333333'),
                tenant_id=self.tenant_id,
                first_name="王",
                last_name="老师",
                email="wang@school.edu",
                max_hours_per_week=16,
                preferred_time_slots=["monday_14:00", "wednesday_14:00", "friday_09:00"],
                is_active=True
            )
        ]

        # 创建示例时间段
        timeslots = []
        for day in [WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY]:
            for hour in ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]:
                timeslot = Timeslot(
                    id=UUID(f'{day.value}_{hour.replace(":", "")}'),
                    tenant_id=self.tenant_id,
                    day_of_week=day,
                    start_time=hour,
                    end_time=f"{int(hour.split(':')[0]) + 1}:00",
                    period_type=PeriodType.CLASS,
                    is_active=True
                )
                timeslots.append(timeslot)

        # 创建示例班级
        class_groups = [
            ClassGroup(
                id=UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                tenant_id=self.tenant_id,
                name="一年级A班",
                grade_level=1,
                student_count=30,
                is_active=True
            ),
            ClassGroup(
                id=UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                tenant_id=self.tenant_id,
                name="一年级B班",
                grade_level=1,
                student_count=28,
                is_active=True
            )
        ]

        # 创建示例课程
        courses = [
            Course(
                id=UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
                tenant_id=self.tenant_id,
                name="数学",
                code="MATH101",
                credit_hours=3,
                is_active=True
            ),
            Course(
                id=UUID('dddddddd-dddd-dddd-dddd-dddddddddddd'),
                tenant_id=self.tenant_id,
                name="语文",
                code="CHIN101",
                credit_hours=3,
                is_active=True
            ),
            Course(
                id=UUID('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'),
                tenant_id=self.tenant_id,
                name="英语",
                code="ENG101",
                credit_hours=2,
                is_active=True
            )
        ]

        # 创建示例教学段
        sections = []
        section_id_counter = 1

        for class_group in class_groups:
            for course in courses:
                # 每个班级每门课程每周2-3课时
                weekly_hours = 2 if course.code in ["ENG101"] else 3

                for i in range(weekly_hours):
                    section = Section(
                        id=UUID(f'section_{section_id_counter:08d}'),
                        tenant_id=self.tenant_id,
                        course_id=course.id,
                        teacher_id=teachers[(section_id_counter - 1) % len(teachers)].id,
                        class_group_id=class_group.id,
                        section_number=f"{course.code}-{class_group.name[-1]}{i+1}",
                        max_students=class_group.student_count,
                        weekly_hours=1,
                        semester="2024-秋季",
                        is_active=True
                    )
                    sections.append(section)
                    section_id_counter += 1

        # 添加所有数据到问题
        for teacher in teachers:
            problem.add_teacher(teacher)

        for timeslot in timeslots:
            problem.add_timeslot(timeslot)

        for section in sections:
            problem.add_section(section)

        logger.info(f"创建示例问题：{len(teachers)}位教师，{len(sections)}个教学段，{len(timeslots)}个时间段")

        return problem

    def solve_with_two_phase_strategy(self) -> Dict[str, Any]:
        """使用两阶段策略求解调度问题。"""
        logger.info("开始两阶段调度求解")

        # 创建问题
        problem = self.create_sample_problem()

        # 执行两阶段求解
        success, assignments, phase_metrics = self.engine.solve_two_phase(
            phase1_time_limit=30,  # 阶段1：30秒
            phase2_time_limit=120  # 阶段2：120秒
        )

        result = {
            'success': success,
            'assignments_count': len(assignments),
            'phase_metrics': phase_metrics,
            'solution_quality': {}
        }

        if success:
            # 获取详细的质量指标
            result['solution_quality'] = self.engine.get_detailed_solution_quality()

            # 验证约束
            violations = self._validate_solution(assignments)
            result['constraint_violations'] = violations

            logger.info(f"调度成功：生成{len(assignments)}个分配")
            logger.info(f"阶段1状态：{phase_metrics.get('phase1_status')}")
            logger.info(f"阶段2状态：{phase_metrics.get('phase2_status')}")
            logger.info(f"总求解时间：{phase_metrics.get('phase1_time', 0) + phase_metrics.get('phase2_time', 0):.2f}秒")
        else:
            logger.warning("调度失败：未找到可行解")

        return result

    def solve_with_basic_strategy(self, time_limit: int = 150) -> Dict[str, Any]:
        """使用基础策略求解调度问题。"""
        logger.info("开始基础调度求解")

        # 创建问题
        problem = self.create_sample_problem()

        # 执行基础求解
        success, assignments = self.engine.solve(time_limit)

        result = {
            'success': success,
            'assignments_count': len(assignments),
            'solution_quality': {}
        }

        if success:
            # 获取质量指标
            result['solution_quality'] = self.engine.get_solution_quality()

            # 验证约束
            violations = self._validate_solution(assignments)
            result['constraint_violations'] = violations

            logger.info(f"基础调度成功：生成{len(assignments)}个分配")
        else:
            logger.warning("基础调度失败：未找到可行解")

        return result

    def compare_strategies(self) -> Dict[str, Any]:
        """比较两阶段策略和基础策略的性能。"""
        logger.info("开始策略比较测试")

        # 使用两阶段策略
        two_phase_result = self.solve_with_two_phase_strategy()

        # 使用基础策略
        basic_result = self.solve_with_basic_strategy()

        comparison = {
            'two_phase_strategy': two_phase_result,
            'basic_strategy': basic_result,
            'analysis': {
                'two_phase_faster': False,
                'two_phase_better_quality': False,
                'recommendation': ''
            }
        }

        # 分析结果
        if two_phase_result['success'] and basic_result['success']:
            two_phase_time = (
                two_phase_result['phase_metrics'].get('phase1_time', 0) +
                two_phase_result['phase_metrics'].get('phase2_time', 0)
            )
            basic_time = basic_result['solution_quality'].get('wall_time', float('inf'))

            comparison['analysis']['two_phase_faster'] = two_phase_time < basic_time

            # 比较解的质量（目标函数值）
            two_phase_objective = two_phase_result['solution_quality'].get('objective_value', float('inf'))
            basic_objective = basic_result['solution_quality'].get('objective_value', float('inf'))

            comparison['analysis']['two_phase_better_quality'] = two_phase_objective < basic_objective

            # 生成建议
            if comparison['analysis']['two_phase_faster'] and comparison['analysis']['two_phase_better_quality']:
                comparison['analysis']['recommendation'] = "推荐使用两阶段策略：更快且质量更好"
            elif comparison['analysis']['two_phase_faster']:
                comparison['analysis']['recommendation'] = "推荐使用两阶段策略：速度更快"
            elif comparison['analysis']['two_phase_better_quality']:
                comparison['analysis']['recommendation'] = "推荐使用两阶段策略：质量更好"
            else:
                comparison['analysis']['recommendation'] = "两种策略性能相近，可根据需求选择"

        logger.info(f"策略比较完成：{comparison['analysis']['recommendation']}")
        return comparison

    def _validate_solution(self, assignments: List[Assignment]) -> List[str]:
        """验证解决方案的约束违反情况。"""
        if not hasattr(self.engine, 'problem') or not self.engine.problem:
            return []

        problem = self.engine.problem
        violations = []

        # 检查教师冲突
        teacher_schedule = {}
        for assignment in assignments:
            # 找到对应的教师
            teacher_id = None
            for section in problem.sections:
                if section.id == assignment.section_id:
                    teacher_id = section.teacher_id
                    break

            if teacher_id:
                if teacher_id not in teacher_schedule:
                    teacher_schedule[teacher_id] = []

                if assignment.timeslot_id in teacher_schedule[teacher_id]:
                    violations.append(f"教师{teacher_id}在时间段{assignment.timeslot_id}有冲突")
                else:
                    teacher_schedule[teacher_id].append(assignment.timeslot_id)

        # 检查班级冲突
        class_schedule = {}
        for assignment in assignments:
            # 找到对应的班级
            class_group_id = None
            for section in problem.sections:
                if section.id == assignment.section_id:
                    class_group_id = section.class_group_id
                    break

            if class_group_id:
                if class_group_id not in class_schedule:
                    class_schedule[class_group_id] = []

                if assignment.timeslot_id in class_schedule[class_group_id]:
                    violations.append(f"班级{class_group_id}在时间段{assignment.timeslot_id}有冲突")
                else:
                    class_schedule[class_group_id].append(assignment.timeslot_id)

        return violations


def demo_scheduling_strategies():
    """演示调度策略的比较。"""
    print("=== Edusched 调度引擎演示 ===")
    print("演示两阶段求解策略 vs 基础求解策略")
    print()

    # 创建调度服务
    service = SchedulingService("demo_tenant")

    # 执行策略比较
    comparison = service.compare_strategies()

    # 打印结果
    print("📊 策略比较结果：")
    print()

    # 两阶段策略结果
    two_phase = comparison['two_phase_strategy']
    print("🔄 两阶段策略：")
    if two_phase['success']:
        print(f"  ✅ 成功生成 {two_phase['assignments_count']} 个分配")
        phase_metrics = two_phase['phase_metrics']
        print(f"  ⏱️  阶段1时间: {phase_metrics.get('phase1_time', 0):.2f}秒")
        print(f"  ⏱️  阶段2时间: {phase_metrics.get('phase2_time', 0):.2f}秒")
        print(f"  📈 总时间: {phase_metrics.get('phase1_time', 0) + phase_metrics.get('phase2_time', 0):.2f}秒")
        print(f"  🎯 阶段1状态: {phase_metrics.get('phase1_status', 'N/A')}")
        print(f"  🎯 阶段2状态: {phase_metrics.get('phase2_status', 'N/A')}")

        quality = two_phase.get('solution_quality', {})
        if quality:
            print(f"  📊 目标函数值: {quality.get('objective_value', 'N/A')}")
            print(f"  📊 调度率: {quality.get('scheduling_rate', 0):.1f}%")
    else:
        print("  ❌ 求解失败")
    print()

    # 基础策略结果
    basic = comparison['basic_strategy']
    print("🎯 基础策略：")
    if basic['success']:
        print(f"  ✅ 成功生成 {basic['assignments_count']} 个分配")
        quality = basic.get('solution_quality', {})
        if quality:
            print(f"  ⏱️  求解时间: {quality.get('wall_time', 0):.2f}秒")
            print(f"  📊 目标函数值: {quality.get('objective_value', 'N/A')}")
    else:
        print("  ❌ 求解失败")
    print()

    # 分析结果
    analysis = comparison['analysis']
    print("🔍 分析结果：")
    print(f"  🚀 两阶段更快: {'是' if analysis['two_phase_faster'] else '否'}")
    print(f"  🎯 两阶段质量更好: {'是' if analysis['two_phase_better_quality'] else '否'}")
    print(f"  💡 推荐: {analysis['recommendation']}")
    print()

    print("=== 演示完成 ===")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 运行演示
    demo_scheduling_strategies()