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
        """添加软约束。"""
        # 这里实现软约束的惩罚机制
        # 例如：教师偏好时间段、课程分布等
        pass
    
    def _add_objective(self) -> None:
        """添加目标函数。"""
        # 简化版本：最小化总惩罚值
        # 实际应该考虑多个目标的加权组合
        pass
    
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