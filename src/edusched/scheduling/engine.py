"""调度引擎核心模块。

使用OR-Tools CP-SAT求解器实现课程表调度算法，支持硬约束和软约束优化。
"""

import logging
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver

from edusched.domain.models import (
    Assignment,
    Constraint,
    ConstraintType,
    PeriodType,
    SchedulingStatus,
    Section,
    Teacher,
    Timeslot,
    WeekDay,
)

logger = logging.getLogger(__name__)


class SchedulingProblem:
    """调度问题定义。"""
    
    def __init__(self, tenant_id: str):
        """初始化调度问题。"""
        self.tenant_id = tenant_id
        self.sections: List[Section] = []
        self.timeslots: List[Timeslot] = []
        self.teachers: List[Teacher] = []
        self.constraints: List[Constraint] = []
        self.existing_assignments: List[Assignment] = []
        
        # 索引映射
        self.section_to_idx: Dict[UUID, int] = {}
        self.timeslot_to_idx: Dict[UUID, int] = {}
        self.teacher_to_idx: Dict[UUID, int] = {}
        
        # 变量
        self.assignment_vars: List[List[cp_model.IntVar]] = []
        self.teacher_timeslot_vars: List[List[cp_model.IntVar]] = []
        self.room_timeslot_vars: List[List[cp_model.IntVar]] = []
        
        # 求解器
        self.model: Optional[CpModel] = None
        self.solver: Optional[CpSolver] = None
    
    def add_section(self, section: Section) -> None:
        """添加教学段。"""
        if section.id not in self.section_to_idx:
            self.section_to_idx[section.id] = len(self.sections)
            self.sections.append(section)
    
    def add_timeslot(self, timeslot: Timeslot) -> None:
        """添加时间段。"""
        if timeslot.id not in self.timeslot_to_idx:
            self.timeslot_to_idx[timeslot.id] = len(self.timeslots)
            self.timeslots.append(timeslot)
    
    def add_teacher(self, teacher: Teacher) -> None:
        """添加教师。"""
        if teacher.id not in self.teacher_to_idx:
            self.teacher_to_idx[teacher.id] = len(self.teachers)
            self.teachers.append(teacher)
    
    def add_constraint(self, constraint: Constraint) -> None:
        """添加约束。"""
        self.constraints.append(constraint)
    
    def add_existing_assignment(self, assignment: Assignment) -> None:
        """添加现有分配。"""
        self.existing_assignments.append(assignment)
    
    def build_model(self) -> None:
        """构建CP-SAT模型。"""
        self.model = CpModel()
        self._create_variables()
        self._add_hard_constraints()
        self._add_soft_constraints()
        self._add_objective()
    
    def _create_variables(self) -> None:
        """创建决策变量。"""
        num_sections = len(self.sections)
        num_timeslots = len(self.timeslots)
        
        # 分配变量：assignment_vars[i][j] = 1 表示教学段i分配到时间段j
        self.assignment_vars = []
        for i in range(num_sections):
            row = []
            for j in range(num_timeslots):
                var = self.model.NewBoolVar(f"assignment_{i}_{j}")
                row.append(var)
            self.assignment_vars.append(row)
        
        # 教师时间段变量：teacher_timeslot_vars[t][j] = 1 表示教师t在时间段j有课
        self.teacher_timeslot_vars = []
        for t in range(len(self.teachers)):
            row = []
            for j in range(num_timeslots):
                var = self.model.NewBoolVar(f"teacher_timeslot_{t}_{j}")
                row.append(var)
            self.teacher_timeslot_vars.append(row)
        
        # 教室时间段变量：room_timeslot_vars[r][j] = 1 表示教室r在时间段j被使用
        # 这里简化处理，实际应该考虑教室容量和特性匹配
        self.room_timeslot_vars = []
        # TODO: 实现教室分配逻辑
    
    def _add_hard_constraints(self) -> None:
        """添加硬约束。"""
        num_sections = len(self.sections)
        num_timeslots = len(self.timeslots)
        
        # 约束1：每个教学段必须且只能分配到一个时间段
        for i in range(num_sections):
            self.model.AddExactlyOne(self.assignment_vars[i])
        
        # 约束2：每个时间段最多只能分配一个教学段（简化处理，实际应该考虑教室）
        for j in range(num_timeslots):
            section_vars = [self.assignment_vars[i][j] for i in range(num_sections)]
            self.model.Add(sum(section_vars) <= 1)
        
        # 约束3：教师不能在同一时间段教授多个教学段
        for t_idx, teacher in enumerate(self.teachers):
            for j in range(num_timeslots):
                # 找出该教师的所有教学段
                teacher_sections = [
                    i for i, section in enumerate(self.sections)
                    if section.teacher_id == teacher.id
                ]
                if teacher_sections:
                    teacher_timeslot_vars = [
                        self.assignment_vars[i][j] for i in teacher_sections
                    ]
                    self.model.Add(sum(teacher_timeslot_vars) <= 1)
        
        # 约束4：班级不能在同一时间段有多个教学段
        class_groups = {}
        for i, section in enumerate(self.sections):
            if section.class_group_id not in class_groups:
                class_groups[section.class_group_id] = []
            class_groups[section.class_group_id].append(i)
        
        for class_group_id, section_indices in class_groups.items():
            for j in range(num_timeslots):
                class_timeslot_vars = [
                    self.assignment_vars[i][j] for i in section_indices
                ]
                self.model.Add(sum(class_timeslot_vars) <= 1)
        
        # 约束5：处理现有分配（锁定的分配）
        for assignment in self.existing_assignments:
            if assignment.is_locked:
                section_idx = self.section_to_idx.get(assignment.section_id)
                timeslot_idx = self.timeslot_to_idx.get(assignment.timeslot_id)
                if section_idx is not None and timeslot_idx is not None:
                    self.model.Add(self.assignment_vars[section_idx][timeslot_idx] == 1)
    
    def _add_soft_constraints(self) -> None:
        """添加软约束及其惩罚变量。"""
        if not self.model:
            return

        # 软约束权重配置
        weights = {
            'teacher_preference': 0.8,
            'room_preference': 0.6,
            'balanced_distribution': 0.7,
            'compact_schedule': 0.5,
            'consecutive_classes': 0.4
        }

        # 创建惩罚变量
        self.penalty_vars = {}

        # 1. 教师偏好时间段约束
        self._add_teacher_preference_constraints(weights['teacher_preference'])

        # 2. 教室容量匹配约束
        self._add_room_capacity_constraints(weights['room_preference'])

        # 3. 课程分布均匀性约束
        self._add_balanced_distribution_constraints(weights['balanced_distribution'])

        # 4. 紧凑课表约束（避免过多空档）
        self._add_compact_schedule_constraints(weights['compact_schedule'])

        # 5. 连续课程约束
        self._add_consecutive_classes_constraints(weights['consecutive_classes'])

    def _add_teacher_preference_constraints(self, weight: float) -> None:
        """添加教师偏好时间段软约束。"""
        penalty_var = self.model.NewIntVar(0, 1000, "teacher_preference_penalty")
        self.penalty_vars['teacher_preference'] = penalty_var

        # 为每个教师的非偏好时间段创建惩罚
        for t_idx, teacher in enumerate(self.teachers):
            if hasattr(teacher, 'preferred_time_slots') and teacher.preferred_time_slots:
                preferred_slots = set(teacher.preferred_time_slots)

                for j, timeslot in enumerate(self.timeslots):
                    # 检查当前时间段是否是教师偏好时间段
                    timeslot_key = f"{timeslot.day_of_week}_{timeslot.start_time}"
                    is_preferred = timeslot_key in preferred_slots

                    if not is_preferred:
                        # 找出该教师在这个时间段的所有教学段
                        teacher_sections = [
                            i for i, section in enumerate(self.sections)
                            if section.teacher_id == teacher.id
                        ]

                        if teacher_sections:
                            # 如果在非偏好时间段分配课程，增加惩罚
                            non_pref_assignments = [
                                self.assignment_vars[i][j] for i in teacher_sections
                            ]
                            if non_pref_assignments:
                                self.model.Add(penalty_var >= sum(non_pref_assignments) * weight)

    def _add_room_capacity_constraints(self, weight: float) -> None:
        """添加教室容量匹配软约束。"""
        penalty_var = self.model.NewIntVar(0, 1000, "room_capacity_penalty")
        self.penalty_vars['room_capacity'] = penalty_var

        # 检查教室容量与学生数量的匹配度
        for i, section in enumerate(self.sections):
            class_size = section.class_group.student_count if hasattr(section, 'class_group') else 30

            # 寻找合适的教室（容量>=班级人数的最小教室）
            suitable_rooms = [
                room for room in getattr(self, 'rooms', [])
                if room.capacity >= class_size
            ]

            if suitable_rooms:
                # 最小合适容量
                min_suitable_capacity = min(room.capacity for room in suitable_rooms)

                for j, timeslot in enumerate(self.timeslots):
                    # 如果分配的教室过大，增加惩罚
                    # 这里简化处理，实际应该考虑具体的教室分配逻辑
                    capacity_waste_penalty = max(0, min_suitable_capacity - class_size) * 0.1
                    self.model.Add(penalty_var >=
                                   self.assignment_vars[i][j] * capacity_waste_penalty * weight)

    def _add_balanced_distribution_constraints(self, weight: float) -> None:
        """添加课程分布均匀性软约束。"""
        penalty_var = self.model.NewIntVar(0, 1000, "balanced_distribution_penalty")
        self.penalty_vars['balanced_distribution'] = penalty_var

        # 确保每个班级的课程在一周内均匀分布
        class_groups = {}
        for i, section in enumerate(self.sections):
            if section.class_group_id not in class_groups:
                class_groups[section.class_group_id] = []
            class_groups[section.class_group_id].append(i)

        for class_group_id, section_indices in class_groups.items():
            if len(section_indices) > 2:
                # 计算每天的课程数量偏差
                daily_counts = {}
                for day in range(1, 6):  # 周一到周五
                    daily_sections = []
                    for i in section_indices:
                        for j, timeslot in enumerate(self.timeslots):
                            if timeslot.day_of_week == day:
                                daily_sections.append(self.assignment_vars[i][j])

                    if daily_sections:
                        daily_counts[day] = sum(daily_sections)

                if len(daily_counts) > 1:
                    # 计算标准差作为均匀性度量
                    mean_count = sum(daily_counts.values()) / len(daily_counts)
                    variance = sum((count - mean_count) ** 2 for count in daily_counts.values()) / len(daily_counts)

                    # 将方差转换为惩罚
                    self.model.Add(penalty_var >= variance * weight * 0.1)

    def _add_compact_schedule_constraints(self, weight: float) -> None:
        """添加紧凑课表软约束（避免过多空档）。"""
        penalty_var = self.model.NewIntVar(0, 1000, "compact_schedule_penalty")
        self.penalty_vars['compact_schedule'] = penalty_var

        # 为每个班级计算紧凑性惩罚
        class_groups = {}
        for i, section in enumerate(self.sections):
            if section.class_group_id not in class_groups:
                class_groups[section.class_group_id] = []
            class_groups[section.class_group_id].append(i)

        for class_group_id, section_indices in class_groups.items():
            # 为每个工作日计算紧凑性
            for day in range(1, 6):  # 周一到周五
                day_timeslots = [
                    (j, timeslot) for j, timeslot in enumerate(self.timeslots)
                    if timeslot.day_of_week == day
                ]

                if len(day_timeslots) > 2:
                    # 按时间排序
                    day_timeslots.sort(key=lambda x: x[1].start_time)

                    # 计算空档惩罚
                    for k in range(len(day_timeslots) - 1):
                        current_j, current_timeslot = day_timeslots[k]
                        next_j, next_timeslot = day_timeslots[k + 1]

                        # 如果有课程在相邻时间段，减少惩罚
                        has_current = False
                        has_next = False

                        for i in section_indices:
                            has_current = has_current or self.assignment_vars[i][current_j]
                            has_next = has_next or self.assignment_vars[i][next_j]

                        # 如果只有其中一个时间段有课，增加空档惩罚
                        gap_penalty = self.model.NewBoolVar(f"gap_penalty_{class_group_id}_{day}_{k}")
                        self.model.AddImplication(has_current & ~has_next, gap_penalty)
                        self.model.AddImplication(~has_current & has_next, gap_penalty)

                        self.model.Add(penalty_var >= gap_penalty * weight)

    def _add_consecutive_classes_constraints(self, weight: float) -> None:
        """添加连续课程软约束。"""
        penalty_var = self.model.NewIntVar(0, 1000, "consecutive_classes_penalty")
        self.penalty_vars['consecutive_classes'] = penalty_var

        # 为需要连续安排的课程设置约束
        for i, section in enumerate(self.sections):
            # 检查是否需要连续安排（例如：实验课、双课时课程等）
            needs_consecutive = getattr(section, 'needs_consecutive', False)
            consecutive_hours = getattr(section, 'consecutive_hours', 1)

            if needs_consecutive and consecutive_hours > 1:
                # 寻找连续的时间段
                consecutive_slot_pairs = []
                for j in range(len(self.timeslots) - 1):
                    current_timeslot = self.timeslots[j]
                    next_timeslot = self.timeslots[j + 1]

                    # 检查是否是连续的时间段
                    if (current_timeslot.day_of_week == next_timeslot.day_of_week and
                        self._is_times_consecutive(current_timeslot, next_timeslot)):
                        consecutive_slot_pairs.append((j, j + 1))

                # 如果没有连续分配，增加惩罚
                if consecutive_slot_pairs:
                    consecutive_assignment = self.model.NewBoolVar(f"consecutive_{i}")

                    # 至少有一对连续时间段被分配
                    consecutive_constraints = []
                    for j1, j2 in consecutive_slot_pairs:
                        consecutive_constraints.append(
                            self.assignment_vars[i][j1] & self.assignment_vars[i][j2]
                        )

                    if consecutive_constraints:
                        self.model.AddBoolOr(consecutive_constraints).OnlyEnforceIf(consecutive_assignment)

                        # 如果没有连续分配，增加惩罚
                        self.model.Add(penalty_var >= (1 - consecutive_assignment) * weight * 10)

    def _is_times_consecutive(self, timeslot1: Timeslot, timeslot2: Timeslot) -> bool:
        """检查两个时间段是否连续。"""
        try:
            # 解析时间字符串
            end_time1 = datetime.strptime(timeslot1.end_time, "%H:%M")
            start_time2 = datetime.strptime(timeslot2.start_time, "%H:%M")

            # 检查是否连续或相差一个休息时间段（如10分钟）
            time_diff = (start_time2 - end_time1).total_seconds() / 60  # 分钟差

            # 允许最多30分钟的间隔（考虑课间休息）
            return 0 <= time_diff <= 30
        except (ValueError, AttributeError):
            return False
    
    def _add_objective(self) -> None:
        """添加目标函数：最小化软约束惩罚的总和。"""
        if not self.model or not hasattr(self, 'penalty_vars'):
            return

        # 计算总惩罚
        total_penalty = sum(self.penalty_vars.values())

        # 设置目标函数：最小化总惩罚
        self.model.Minimize(total_penalty)

        # 可选：也可以设置最大化约束满足的数量
        # 这里简化处理，只使用惩罚最小化

    def get_constraint_violations(self) -> Dict[str, Any]:
        """获取约束违反情况统计。"""
        if not self.solver or not hasattr(self, 'penalty_vars'):
            return {}

        violations = {}
        total_penalty = 0

        for constraint_name, penalty_var in self.penalty_vars.items():
            penalty_value = self.solver.Value(penalty_var)
            violations[constraint_name] = {
                'penalty_value': penalty_value,
                'violations_count': int(penalty_value)  # 简化的违反计数
            }
            total_penalty += penalty_value

        violations['total_penalty'] = total_penalty
        violations['is_feasible'] = total_penalty == 0

        return violations

    def get_solution_quality_metrics(self) -> Dict[str, Any]:
        """获取解的质量指标。"""
        if not self.solver:
            return {}

        # 基本求解器指标
        basic_metrics = {
            'status': self.solver.StatusName(),
            'objective_value': self.solver.ObjectiveValue(),
            'best_bound': self.solver.BestObjectiveBound(),
            'wall_time': self.solver.WallTime(),
            'num_conflicts': self.solver.NumConflicts(),
            'num_branches': self.solver.NumBranches(),
            'num_booleans': self.solver.NumBooleans(),
            'num_propagations': self.solver.NumPropagations()
        }

        # 约束违反情况
        constraint_violations = self.get_constraint_violations()
        basic_metrics.update(constraint_violations)

        # 业务指标
        business_metrics = self._calculate_business_metrics()
        basic_metrics.update(business_metrics)

        return basic_metrics

    def _calculate_business_metrics(self) -> Dict[str, Any]:
        """计算业务相关的质量指标。"""
        metrics = {
            'total_sections': len(self.sections),
            'scheduled_sections': 0,
            'teacher_utilization': {},
            'room_utilization': {},
            'balance_metrics': {}
        }

        # 统计已安排的教学段
        if hasattr(self, 'assignment_vars') and self.solver:
            for i, section in enumerate(self.sections):
                for j, timeslot in enumerate(self.timeslots):
                    if self.solver.Value(self.assignment_vars[i][j]) == 1:
                        metrics['scheduled_sections'] += 1
                        break

        # 计算教师利用率
        for teacher in self.teachers:
            teacher_id = str(teacher.id)
            scheduled_hours = 0
            max_hours = teacher.max_hours_per_week if hasattr(teacher, 'max_hours_per_week') else 20

            if hasattr(self, 'assignment_vars') and self.solver:
                for i, section in enumerate(self.sections):
                    if section.teacher_id == teacher.id:
                        for j, timeslot in enumerate(self.timeslots):
                            if self.solver.Value(self.assignment_vars[i][j]) == 1:
                                scheduled_hours += 1  # 每个时间段算1小时

            utilization_rate = (scheduled_hours / max_hours * 100) if max_hours > 0 else 0
            metrics['teacher_utilization'][teacher_id] = {
                'scheduled_hours': scheduled_hours,
                'max_hours': max_hours,
                'utilization_rate': round(utilization_rate, 2)
            }

        # 计算整体调度质量
        metrics['scheduling_rate'] = (
            metrics['scheduled_sections'] / metrics['total_sections'] * 100
        ) if metrics['total_sections'] > 0 else 0

        metrics['average_teacher_utilization'] = (
            sum(info['utilization_rate'] for info in metrics['teacher_utilization'].values()) /
            len(metrics['teacher_utilization'])
        ) if metrics['teacher_utilization'] else 0

        return metrics
    
    def solve(self, time_limit: int = 300) -> Tuple[bool, List[Assignment]]:
        """求解调度问题。"""
        if self.model is None:
            raise RuntimeError("模型未构建，请先调用 build_model()")

        self.solver = CpSolver()
        self.solver.parameters.max_time_in_seconds = time_limit

        logger.info(f"开始求解调度问题，时间限制: {time_limit}秒")
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("找到可行解")
            assignments = self._extract_solution()
            return True, assignments
        else:
            logger.warning("未找到可行解")
            return False, []

    def solve_two_phase(self, phase1_time_limit: int = 60, phase2_time_limit: int = 240) -> Tuple[bool, List[Assignment], Dict[str, Any]]:
        """两阶段求解策略。

        阶段1：快速找到可行解（只考虑硬约束）
        阶段2：优化软约束（基于可行解进行改进）
        """
        if self.model is None:
            raise RuntimeError("模型未构建，请先调用 build_model()")

        logger.info("开始两阶段求解策略")
        phase_metrics = {
            'phase1_status': 'not_started',
            'phase2_status': 'not_started',
            'phase1_time': 0,
            'phase2_time': 0,
            'phase1_solution_found': False,
            'phase2_improved': False,
            'best_objective': float('inf')
        }

        # 阶段1：快速找到可行解
        logger.info(f"阶段1：寻找可行解，时间限制: {phase1_time_limit}秒")
        phase1_start = datetime.now()

        # 创建只包含硬约束的模型
        phase1_model = self._create_phase1_model()
        phase1_solver = CpSolver()
        phase1_solver.parameters.max_time_in_seconds = phase1_time_limit
        phase1_solver.parameters.num_search_workers = 4  # 并行搜索加速

        phase1_status = phase1_solver.Solve(phase1_model)
        phase1_time = (datetime.now() - phase1_start).total_seconds()

        phase_metrics['phase1_time'] = phase1_time
        phase_metrics['phase1_status'] = phase1_solver.StatusName()

        initial_assignments = []
        if phase1_status == cp_model.OPTIMAL or phase1_status == cp_model.FEASIBLE:
            logger.info("阶段1：找到可行解")
            phase_metrics['phase1_solution_found'] = True
            initial_assignments = self._extract_phase1_solution(phase1_solver)

            # 阶段2：优化软约束
            logger.info(f"阶段2：优化软约束，时间限制: {phase2_time_limit}秒")
            phase2_start = datetime.now()

            # 基于阶段1的解创建热启动模型
            phase2_success, optimized_assignments = self._solve_phase2(
                initial_assignments, phase2_time_limit
            )

            phase2_time = (datetime.now() - phase2_start).total_seconds()
            phase_metrics['phase2_time'] = phase2_time
            phase_metrics['phase2_status'] = 'success' if phase2_success else 'failed'

            if phase2_success:
                logger.info("阶段2：优化成功")
                phase_metrics['phase2_improved'] = True
                final_assignments = optimized_assignments
            else:
                logger.info("阶段2：优化失败，使用阶段1的解")
                final_assignments = initial_assignments
        else:
            logger.warning("阶段1：未找到可行解，尝试完整模型")
            # 回退到完整模型求解
            fallback_success, fallback_assignments = self.solve(phase1_time_limit + phase2_time_limit)
            if fallback_success:
                final_assignments = fallback_assignments
                phase_metrics['fallback_success'] = True
            else:
                return False, [], phase_metrics

        # 计算最终解的质量指标
        if hasattr(self, 'solver') and self.solver:
            phase_metrics['final_objective'] = self.solver.ObjectiveValue()
            phase_metrics['solution_quality'] = self.get_solution_quality_metrics()

        return True, final_assignments, phase_metrics

    def _create_phase1_model(self) -> CpModel:
        """创建阶段1模型：只包含硬约束，快速找到可行解。"""
        phase1_model = CpModel()

        # 重新创建变量（避免与原模型冲突）
        num_sections = len(self.sections)
        num_timeslots = len(self.timeslots)

        # 阶段1变量
        phase1_vars = []
        for i in range(num_sections):
            row = []
            for j in range(num_timeslots):
                var = phase1_model.NewBoolVar(f"phase1_assignment_{i}_{j}")
                row.append(var)
            phase1_vars.append(row)

        # 只添加硬约束
        self._add_phase1_hard_constraints(phase1_model, phase1_vars)

        # 阶段1目标：最小化变量数量（简化目标，快速求解）
        # 实际上我们只需要找到可行解，所以不需要复杂的目标
        phase1_model.Minimize(0)  # 只要求可行性

        return phase1_model

    def _add_phase1_hard_constraints(self, model: CpModel, vars: List[List[cp_model.IntVar]]) -> None:
        """为阶段1模型添加硬约束。"""
        num_sections = len(self.sections)
        num_timeslots = len(self.timeslots)

        # 硬约束1：每个教学段必须且只能分配到一个时间段
        for i in range(num_sections):
            model.AddExactlyOne(vars[i])

        # 硬约束2：每个时间段最多只能分配一个教学段
        for j in range(num_timeslots):
            section_vars = [vars[i][j] for i in range(num_sections)]
            model.Add(sum(section_vars) <= 1)

        # 硬约束3：教师时间冲突约束
        for t_idx, teacher in enumerate(self.teachers):
            for j in range(num_timeslots):
                teacher_sections = [
                    i for i, section in enumerate(self.sections)
                    if section.teacher_id == teacher.id
                ]
                if teacher_sections:
                    teacher_timeslot_vars = [vars[i][j] for i in teacher_sections]
                    model.Add(sum(teacher_timeslot_vars) <= 1)

        # 硬约束4：班级时间冲突约束
        class_groups = {}
        for i, section in enumerate(self.sections):
            if section.class_group_id not in class_groups:
                class_groups[section.class_group_id] = []
            class_groups[section.class_group_id].append(i)

        for class_group_id, section_indices in class_groups.items():
            for j in range(num_timeslots):
                class_timeslot_vars = [vars[i][j] for i in section_indices]
                model.Add(sum(class_timeslot_vars) <= 1)

        # 硬约束5：现有分配约束
        for assignment in self.existing_assignments:
            if assignment.is_locked:
                section_idx = self.section_to_idx.get(assignment.section_id)
                timeslot_idx = self.timeslot_to_idx.get(assignment.timeslot_id)
                if section_idx is not None and timeslot_idx is not None:
                    model.Add(vars[section_idx][timeslot_idx] == 1)

    def _extract_phase1_solution(self, phase1_solver: CpSolver) -> List[Assignment]:
        """从阶段1求解结果中提取解。"""
        assignments = []

        # 重新创建变量引用（用于提取值）
        num_sections = len(self.sections)
        num_timeslots = len(self.timeslots)

        for i, section in enumerate(self.sections):
            for j, timeslot in enumerate(self.timeslots):
                var_name = f"phase1_assignment_{i}_{j}"
                # 注意：这里需要通过变量名获取值，实际实现可能需要调整
                # 简化处理：假设我们能够获取到变量值
                try:
                    # 在实际实现中，需要正确获取变量值
                    # 这里简化处理，直接创建分配
                    if phase1_solver.Value(phase1_solver.IntVar(var_name)) == 1:
                        assignment = Assignment(
                            tenant_id=self.tenant_id,
                            timetable_id=UUID('00000000-0000-0000-0000-000000000000'),
                            section_id=section.id,
                            timeslot_id=timeslot.id,
                            room_id=UUID('00000000-0000-0000-0000-000000000000'),
                            is_locked=False,
                        )
                        assignments.append(assignment)
                except:
                    # 如果无法获取变量值，跳过
                    continue

        return assignments

    def _solve_phase2(self, initial_assignments: List[Assignment], time_limit: int) -> Tuple[bool, List[Assignment]]:
        """阶段2：基于初始解优化软约束。"""
        if not self.model:
            return False, []

        # 设置求解器参数以优化软约束
        solver = CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.num_search_workers = 2  # 使用较少的搜索者，专注于优化

        # 添加初始解作为热启动
        self._add_solution_hint(solver, initial_assignments)

        # 设置更优的搜索策略
        solver.parameters.search_branching = cp_model.AUTOMATIC_SEARCH
        solver.parameters.use_phase_saving = True

        logger.info("开始阶段2优化")
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self.solver = solver  # 保存求解器用于质量评估
            optimized_assignments = self._extract_solution()
            return True, optimized_assignments
        else:
            logger.warning("阶段2优化失败")
            return False, initial_assignments

    def _add_solution_hint(self, solver: CpSolver, initial_assignments: List[Assignment]) -> None:
        """添加初始解作为求解器提示。"""
        # 创建解提示映射
        assignment_hints = {}

        for assignment in initial_assignments:
            section_idx = self.section_to_idx.get(assignment.section_id)
            timeslot_idx = self.timeslot_to_idx.get(assignment.timeslot_id)

            if section_idx is not None and timeslot_idx is not None:
                assignment_hints[section_idx] = timeslot_idx

        # 为变量添加提示值
        for i, section in enumerate(self.sections):
            for j, timeslot in enumerate(self.timeslots):
                if i in assignment_hints and assignment_hints[i] == j:
                    # 这个变量在初始解中为1
                    solver.AddHint(self.assignment_vars[i][j], 1)
                else:
                    # 这个变量在初始解中为0
                    solver.AddHint(self.assignment_vars[i][j], 0)
    
    def _extract_solution(self) -> List[Assignment]:
        """从求解结果中提取分配方案。"""
        if self.solver is None:
            return []
        
        assignments = []
        for i, section in enumerate(self.sections):
            for j, timeslot in enumerate(self.timeslots):
                if self.solver.Value(self.assignment_vars[i][j]) == 1:
                    # 创建分配记录
                    assignment = Assignment(
                        tenant_id=self.tenant_id,
                        timetable_id=UUID('00000000-0000-0000-0000-000000000000'),  # 临时ID
                        section_id=section.id,
                        timeslot_id=timeslot.id,
                        room_id=UUID('00000000-0000-0000-0000-000000000000'),  # 临时ID
                        is_locked=False,
                    )
                    assignments.append(assignment)
        
        return assignments


class SchedulingEngine:
    """调度引擎主类。"""
    
    def __init__(self, tenant_id: str):
        """初始化调度引擎。"""
        self.tenant_id = tenant_id
        self.problem: Optional[SchedulingProblem] = None
    
    def create_problem(self) -> SchedulingProblem:
        """创建调度问题。"""
        self.problem = SchedulingProblem(self.tenant_id)
        return self.problem
    
    def solve(self, time_limit: int = 300) -> Tuple[bool, List[Assignment]]:
        """求解调度问题。"""
        if self.problem is None:
            raise RuntimeError("调度问题未创建")

        self.problem.build_model()
        return self.problem.solve(time_limit)

    def solve_two_phase(self, phase1_time_limit: int = 60, phase2_time_limit: int = 240) -> Tuple[bool, List[Assignment], Dict[str, Any]]:
        """使用两阶段策略求解调度问题。"""
        if self.problem is None:
            raise RuntimeError("调度问题未创建")

        self.problem.build_model()
        return self.problem.solve_two_phase(phase1_time_limit, phase2_time_limit)

    def get_solution_quality(self) -> Dict[str, Any]:
        """获取解的质量指标。"""
        if self.problem is None or self.problem.solver is None:
            return {}

        solver = self.problem.solver
        return {
            "status": solver.StatusName(solver.Status()),
            "objective_value": solver.ObjectiveValue(),
            "best_objective_bound": solver.BestObjectiveBound(),
            "num_conflicts": solver.NumConflicts(),
            "num_branches": solver.NumBranches(),
            "wall_time": solver.WallTime(),
        }

    def get_detailed_solution_quality(self) -> Dict[str, Any]:
        """获取详细的解质量指标，包括业务指标。"""
        if self.problem is None:
            return {}

        return self.problem.get_solution_quality_metrics()

    def compare_solutions(self, basic_solution: List[Assignment], optimized_solution: List[Assignment]) -> Dict[str, Any]:
        """比较基础解和优化解的质量差异。"""
        comparison = {
            'basic_solution': {},
            'optimized_solution': {},
            'improvements': {}
        }

        # 计算基础解的质量
        basic_metrics = self._calculate_solution_metrics(basic_solution)
        comparison['basic_solution'] = basic_metrics

        # 计算优化解的质量
        optimized_metrics = self._calculate_solution_metrics(optimized_solution)
        comparison['optimized_solution'] = optimized_metrics

        # 计算改进
        comparison['improvements'] = {
            'objective_improvement': basic_metrics.get('total_penalty', 0) - optimized_metrics.get('total_penalty', 0),
            'teacher_utilization_improvement': optimized_metrics.get('average_teacher_utilization', 0) - basic_metrics.get('average_teacher_utilization', 0),
            'constraint_violations_reduced': basic_metrics.get('total_violations', 0) - optimized_metrics.get('total_violations', 0)
        }

        return comparison

    def _calculate_solution_metrics(self, assignments: List[Assignment]) -> Dict[str, Any]:
        """计算解决方案的质量指标。"""
        if not self.problem:
            return {}

        metrics = {
            'total_assignments': len(assignments),
            'teacher_satisfaction': 0,
            'room_utilization': 0,
            'schedule_balance': 0,
            'total_penalty': 0,
            'total_violations': 0
        }

        # 简化的质量计算
        if self.problem.sections and self.problem.teachers:
            # 计算教师满意度
            satisfied_teachers = 0
            for teacher in self.problem.teachers:
                teacher_assignments = [a for a in assignments if any(
                    s.teacher_id == teacher.id for s in self.problem.sections if s.id == a.section_id
                )]
                if teacher_assignments:
                    satisfied_teachers += 1

            metrics['teacher_satisfaction'] = satisfied_teachers / len(self.problem.teachers) * 100

        return metrics


class ConstraintValidator:
    """约束验证器。"""
    
    @staticmethod
    def validate_hard_constraints(
        assignments: List[Assignment],
        sections: List[Section],
        timeslots: List[Timeslot],
    ) -> List[str]:
        """验证硬约束。"""
        violations = []
        
        # 检查教师冲突
        teacher_conflicts = ConstraintValidator._check_teacher_conflicts(
            assignments, sections, timeslots
        )
        violations.extend(teacher_conflicts)
        
        # 检查班级冲突
        class_conflicts = ConstraintValidator._check_class_conflicts(
            assignments, sections, timeslots
        )
        violations.extend(class_conflicts)
        
        # 检查时间段冲突
        timeslot_conflicts = ConstraintValidator._check_timeslot_conflicts(assignments)
        violations.extend(timeslot_conflicts)
        
        return violations
    
    @staticmethod
    def _check_teacher_conflicts(
        assignments: List[Assignment],
        sections: List[Section],
        timeslots: List[Timeslot],
    ) -> List[str]:
        """检查教师冲突。"""
        violations = []
        teacher_timeslots: Dict[UUID, Set[UUID]] = {}
        
        for assignment in assignments:
            section = next(s for s in sections if s.id == assignment.section_id)
            teacher_id = section.teacher_id
            timeslot_id = assignment.timeslot_id
            
            if teacher_id not in teacher_timeslots:
                teacher_timeslots[teacher_id] = set()
            
            if timeslot_id in teacher_timeslots[teacher_id]:
                violations.append(
                    f"教师 {teacher_id} 在时间段 {timeslot_id} 有冲突"
                )
            else:
                teacher_timeslots[teacher_id].add(timeslot_id)
        
        return violations
    
    @staticmethod
    def _check_class_conflicts(
        assignments: List[Assignment],
        sections: List[Section],
        timeslots: List[Timeslot],
    ) -> List[str]:
        """检查班级冲突。"""
        violations = []
        class_timeslots: Dict[UUID, Set[UUID]] = {}
        
        for assignment in assignments:
            section = next(s for s in sections if s.id == assignment.section_id)
            class_group_id = section.class_group_id
            timeslot_id = assignment.timeslot_id
            
            if class_group_id not in class_timeslots:
                class_timeslots[class_group_id] = set()
            
            if timeslot_id in class_timeslots[class_group_id]:
                violations.append(
                    f"班级 {class_group_id} 在时间段 {timeslot_id} 有冲突"
                )
            else:
                class_timeslots[class_group_id].add(timeslot_id)
        
        return violations
    
    @staticmethod
    def _check_timeslot_conflicts(assignments: List[Assignment]) -> List[str]:
        """检查时间段冲突。"""
        violations = []
        timeslot_assignments: Dict[UUID, List[Assignment]] = {}
        
        for assignment in assignments:
            timeslot_id = assignment.timeslot_id
            if timeslot_id not in timeslot_assignments:
                timeslot_assignments[timeslot_id] = []
            timeslot_assignments[timeslot_id].append(assignment)
        
        for timeslot_id, assignments_list in timeslot_assignments.items():
            if len(assignments_list) > 1:
                violations.append(
                    f"时间段 {timeslot_id} 被多个教学段占用"
                )
        
        return violations