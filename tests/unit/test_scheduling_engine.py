"""调度引擎单元测试。"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from edusched.scheduling.engine import SchedulingEngine, SchedulingProblem, ConstraintValidator
from edusched.domain.models import (
    Teacher,
    Section,
    Timeslot,
    Assignment,
    WeekDay,
    PeriodType,
    ClassGroup,
    Course
)


class TestSchedulingEngine:
    """调度引擎测试类。"""

    def test_create_scheduling_engine(self):
        """测试创建调度引擎。"""
        engine = SchedulingEngine("test_tenant")
        assert engine.tenant_id == "test_tenant"
        assert engine.problem is None

    def test_create_problem(self):
        """测试创建调度问题。"""
        engine = SchedulingEngine("test_tenant")
        problem = engine.create_problem()

        assert problem.tenant_id == "test_tenant"
        assert isinstance(problem, SchedulingProblem)
        assert engine.problem is problem

    def test_solve_without_problem(self):
        """测试在未创建问题的情况下求解。"""
        engine = SchedulingEngine("test_tenant")

        with pytest.raises(RuntimeError, match="调度问题未创建"):
            engine.solve()

    def test_solve_two_phase_without_problem(self):
        """测试在未创建问题的情况下进行两阶段求解。"""
        engine = SchedulingEngine("test_tenant")

        with pytest.raises(RuntimeError, match="调度问题未创建"):
            engine.solve_two_phase()

    def test_get_solution_quality_without_problem(self):
        """测试在未创建问题的情况下获取解质量。"""
        engine = SchedulingEngine("test_tenant")

        quality = engine.get_solution_quality()
        assert quality == {}

    def test_get_detailed_solution_quality_without_problem(self):
        """测试在未创建问题的情况下获取详细解质量。"""
        engine = SchedulingEngine("test_tenant")

        quality = engine.get_detailed_solution_quality()
        assert quality == {}


class TestSchedulingProblem:
    """调度问题测试类。"""

    @pytest.fixture
    def problem(self):
        """创建调度问题fixture。"""
        return SchedulingProblem("test_tenant")

    def test_create_scheduling_problem(self, problem):
        """测试创建调度问题。"""
        assert problem.tenant_id == "test_tenant"
        assert len(problem.sections) == 0
        assert len(problem.timeslots) == 0
        assert len(problem.teachers) == 0
        assert len(problem.constraints) == 0
        assert problem.model is None

    def test_add_section(self, problem):
        """测试添加教学段。"""
        section = Mock()
        section.id = uuid4()

        problem.add_section(section)

        assert len(problem.sections) == 1
        assert problem.sections[0] == section
        assert problem.section_to_idx[section.id] == 0

    def test_add_duplicate_section(self, problem):
        """测试添加重复教学段。"""
        section = Mock()
        section.id = uuid4()

        problem.add_section(section)
        problem.add_section(section)

        assert len(problem.sections) == 1  # 不应该重复添加

    def test_add_teacher(self, problem):
        """测试添加教师。"""
        teacher = Mock()
        teacher.id = uuid4()

        problem.add_teacher(teacher)

        assert len(problem.teachers) == 1
        assert problem.teachers[0] == teacher
        assert problem.teacher_to_idx[teacher.id] == 0

    def test_add_timeslot(self, problem):
        """测试添加时间段。"""
        timeslot = Mock()
        timeslot.id = uuid4()

        problem.add_timeslot(timeslot)

        assert len(problem.timeslots) == 1
        assert problem.timeslots[0] == timeslot
        assert problem.timeslot_to_idx[timeslot.id] == 0

    def test_add_constraint(self, problem):
        """测试添加约束。"""
        constraint = Mock()

        problem.add_constraint(constraint)

        assert len(problem.constraints) == 1
        assert problem.constraints[0] == constraint

    def test_add_existing_assignment(self, problem):
        """测试添加现有分配。"""
        assignment = Mock()

        problem.add_existing_assignment(assignment)

        assert len(problem.existing_assignments) == 1
        assert problem.existing_assignments[0] == assignment

    def test_build_model_without_data(self, problem):
        """测试在没有数据的情况下构建模型。"""
        problem.build_model()

        assert problem.model is not None
        assert len(problem.assignment_vars) == 0  # 没有教学段，所以没有变量

    def test_solve_without_model(self, problem):
        """测试在未构建模型的情况下求解。"""
        with pytest.raises(RuntimeError, match="模型未构建"):
            problem.solve()

    @patch('edusched.scheduling.engine.CpSolver')
    def test_solve_with_feasible_solution(self, mock_solver_class, problem):
        """测试求解并找到可行解。"""
        # 模拟求解器
        mock_solver = Mock()
        mock_solver.Solve.return_value = 1  # FEASIBLE
        mock_solver_class.return_value = mock_solver

        # 添加一些测试数据
        section = Mock()
        section.id = uuid4()
        timeslot = Mock()
        timeslot.id = uuid4()

        problem.add_section(section)
        problem.add_timeslot(timeslot)
        problem.build_model()

        success, assignments = problem.solve()

        assert success is True
        assert isinstance(assignments, list)

    def test_extract_solution_without_solver(self, problem):
        """测试在没有求解器的情况下提取解。"""
        assignments = problem._extract_solution()
        assert assignments == []

    def test_get_constraint_violations_without_solver(self, problem):
        """测试在没有求解器的情况下获取约束违反情况。"""
        violations = problem.get_constraint_violations()
        assert violations == {}

    def test_get_solution_quality_metrics_without_solver(self, problem):
        """测试在没有求解器的情况下获取解质量指标。"""
        metrics = problem.get_solution_quality_metrics()
        assert metrics == {}

    def test_calculate_business_metrics_without_sections(self, problem):
        """测试在没有教学段的情况下计算业务指标。"""
        metrics = problem._calculate_business_metrics()

        assert metrics['total_sections'] == 0
        assert metrics['scheduled_sections'] == 0
        assert metrics['scheduling_rate'] == 0

    def test_create_sample_problem_with_real_data(self):
        """测试使用真实数据创建示例问题。"""
        problem = SchedulingProblem("test_tenant")

        # 创建真实教师
        teacher = Teacher(
            id=uuid4(),
            tenant_id="test_tenant",
            first_name="张",
            last_name="老师",
            email="zhang@school.edu",
            max_hours_per_week=20,
            is_active=True
        )

        # 创建真实时间段
        timeslot = Timeslot(
            id=uuid4(),
            tenant_id="test_tenant",
            day_of_week=WeekDay.MONDAY,
            start_time="09:00",
            end_time="10:00",
            period_type=PeriodType.CLASS,
            is_active=True
        )

        # 添加到问题
        problem.add_teacher(teacher)
        problem.add_timeslot(timeslot)

        assert len(problem.teachers) == 1
        assert len(problem.timeslots) == 1
        assert problem.teachers[0].first_name == "张"
        assert problem.timeslots[0].day_of_week == WeekDay.MONDAY

    def test_solve_two_phase_without_model(self, problem):
        """测试在未构建模型的情况下进行两阶段求解。"""
        with pytest.raises(RuntimeError, match="模型未构建"):
            problem.solve_two_phase()

    def test_create_phase1_model(self, problem):
        """测试创建阶段1模型。"""
        # 添加测试数据
        section = Mock()
        section.id = uuid4()
        timeslot = Mock()
        timeslot.id = uuid4()

        problem.add_section(section)
        problem.add_timeslot(timeslot)

        phase1_model = problem._create_phase1_model()

        assert phase1_model is not None
        assert hasattr(phase1_model, 'NewBoolVar')

    def test_add_phase1_hard_constraints(self, problem):
        """测试为阶段1模型添加硬约束。"""
        # 创建测试模型和变量
        from ortools.sat.python import cp_model

        model = cp_model.CpModel()
        vars = [[model.NewBoolVar(f"test_{i}_{j}") for j in range(3)] for i in range(2)]

        # 添加测试数据
        teacher = Mock()
        teacher.id = uuid4()
        problem.add_teacher(teacher)

        section = Mock()
        section.id = uuid4()
        section.teacher_id = teacher.id
        section.class_group_id = uuid4()
        problem.add_section(section)

        # 应该不抛出异常
        problem._add_phase1_hard_constraints(model, vars)


class TestConstraintValidator:
    """约束验证器测试类。"""

    def test_validate_hard_constraints_empty_list(self):
        """测试验证空的分配列表。"""
        violations = ConstraintValidator.validate_hard_constraints([], [], [])
        assert violations == []

    def test_check_teacher_conflicts_empty_list(self):
        """�试检查空的教师冲突列表。"""
        violations = ConstraintValidator._check_teacher_conflicts([], [], [])
        assert violations == []

    def test_check_class_conflicts_empty_list(self):
        """测试检查空的班级冲突列表。"""
        violations = ConstraintValidator._check_class_conflicts([], [], [])
        assert violations == []

    def test_check_timeslot_conflicts_empty_list(self):
        """测试检查空的时间段冲突列表。"""
        violations = ConstraintValidator._check_timeslot_conflicts([])
        assert violations == []

    def test_check_timeslot_conflicts_with_multiple_assignments(self):
        """测试检查时间段冲突（多个分配到同一时间段）。"""
        timeslot_id = uuid4()
        assignment1 = Mock(timeslot_id=timeslot_id)
        assignment2 = Mock(timeslot_id=timeslot_id)
        assignment3 = Mock(timeslot_id=uuid4())  # 不同的时间段

        assignments = [assignment1, assignment2, assignment3]
        violations = ConstraintValidator._check_timeslot_conflicts(assignments)

        assert len(violations) == 1
        assert "时间段" in violations[0]
        assert "被多个教学段占用" in violations[0]

    def test_check_timeslot_conflicts_no_conflicts(self):
        """测试检查时间段冲突（无冲突）。"""
        assignment1 = Mock(timeslot_id=uuid4())
        assignment2 = Mock(timeslot_id=uuid4())

        assignments = [assignment1, assignment2]
        violations = ConstraintValidator._check_timeslot_conflicts(assignments)

        assert len(violations) == 0

    def test_check_teacher_conflicts_with_conflicts(self):
        """测试检查教师冲突。"""
        teacher_id = uuid4()
        timeslot_id = uuid4()
        section_id = uuid4()

        # 创建冲突的分配
        assignment1 = Mock(timeslot_id=timeslot_id, section_id=section_id)
        assignment2 = Mock(timeslot_id=timeslot_id, section_id=uuid4())

        # 创建对应的section
        section1 = Mock(id=section_id, teacher_id=teacher_id)
        section2 = Mock(id=uuid4(), teacher_id=teacher_id)

        violations = ConstraintValidator._check_teacher_conflicts(
            [assignment1, assignment2],
            [section1, section2],
            [Mock(id=timeslot_id)]
        )

        assert len(violations) == 1
        assert "教师" in violations[0]
        assert "在时间段" in violations[0]
        assert "有冲突" in violations[0]