"""调度相关数据工厂"""

import uuid
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import (
    SchedulingProblem, SchedulingSolution, SchedulingConstraint,
    SchedulingResult, SchedulingMetric
)
from .base_factory import BaseFactory, fake


class SchedulingProblemFactory(BaseFactory[SchedulingProblem]):
    """调度问题工厂"""

    model_class = SchedulingProblem

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取调度问题默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'school_id': None,  # 需要在外部设置
            'semester': fake.random_element([
                '2024-春季', '2024-秋季', '2025-春季', '2025-秋季'
            ]),
            'problem_status': 'pending',
            'input_data': {},
            'constraints': {},
            'objective_weights': {
                'teacher_conflicts': 1.0,
                'room_conflicts': 1.0,
                'class_conflicts': 1.0,
                'teacher_preferences': 0.8,
                'room_utilization': 0.6,
                'balanced_distribution': 0.7
            },
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_with_school(cls, session: Session, school_id: str, **kwargs) -> SchedulingProblem:
        """创建带有学校的调度问题"""
        defaults = {'school_id': school_id}
        defaults.update(kwargs)
        return cls.create(session, **defaults)


class SchedulingSolutionFactory(BaseFactory[SchedulingSolution]):
    """调度解决方案工厂"""

    model_class = SchedulingSolution

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取调度解决方案默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'problem_id': None,  # 需要在外部设置
            'solution_status': 'draft',
            'assignments': [],
            'metrics': {},
            'quality_score': 0.0,
            'constraint_violations': [],
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_with_problem(cls, session: Session, problem_id: str, **kwargs) -> SchedulingSolution:
        """创建带有问题的调度解决方案"""
        defaults = {'problem_id': problem_id}
        defaults.update(kwargs)
        return cls.create(session, **defaults)


class SchedulingConstraintFactory(BaseFactory[SchedulingConstraint]):
    """调度约束工厂"""

    model_class = SchedulingConstraint

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取调度约束默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'problem_id': None,  # 需要在外部设置
            'constraint_type': fake.random_element([
                'hard', 'soft', 'preference'
            ]),
            'constraint_name': fake.random_element([
                'teacher_conflict', 'room_conflict', 'class_conflict',
                'teacher_preference', 'room_capacity', 'time_preference'
            ]),
            'description': fake.text(max_nb_chars=100),
            'weight': fake.random.uniform(0.1, 1.0),
            'parameters': {},
            'is_active': True,
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_with_problem(cls, session: Session, problem_id: str, **kwargs) -> SchedulingConstraint:
        """创建带有问题的调度约束"""
        defaults = {'problem_id': problem_id}
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_hard_constraint(cls, session: Session, problem_id: str, constraint_name: str, **kwargs) -> SchedulingConstraint:
        """创建硬约束"""
        defaults = {
            'problem_id': problem_id,
            'constraint_type': 'hard',
            'constraint_name': constraint_name,
            'weight': 1.0,
            'description': f'硬约束: {constraint_name}'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_soft_constraint(cls, session: Session, problem_id: str, constraint_name: str, weight: float = 0.5, **kwargs) -> SchedulingConstraint:
        """创建软约束"""
        defaults = {
            'problem_id': problem_id,
            'constraint_type': 'soft',
            'constraint_name': constraint_name,
            'weight': weight,
            'description': f'软约束: {constraint_name}'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)


class SchedulingResultFactory(BaseFactory[SchedulingResult]):
    """调度结果工厂"""

    model_class = SchedulingResult

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取调度结果默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'solution_id': None,  # 需要在外部设置
            'execution_time': fake.random.uniform(1.0, 60.0),
            'status': fake.random_element(['success', 'partial_success', 'failed']),
            'total_assignments': fake.random_int(min=10, max=100),
            'successful_assignments': 0,
            'constraint_violations': 0,
            'quality_metrics': {},
            'created_at': cls.generate_datetime()
        }

    @classmethod
    def create_with_solution(cls, session: Session, solution_id: str, **kwargs) -> SchedulingResult:
        """创建带有解决方案的调度结果"""
        defaults = {'solution_id': solution_id}
        defaults.update(kwargs)
        return cls.create(session, **defaults)


class SchedulingMetricFactory(BaseFactory[SchedulingMetric]):
    """调度指标工厂"""

    model_class = SchedulingMetric

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取调度指标默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'result_id': None,  # 需要在外部设置
            'metric_name': fake.random_element([
                'teacher_utilization', 'room_utilization', 'class_utilization',
                'constraint_satisfaction', 'solution_quality', 'execution_time'
            ]),
            'metric_value': fake.random.uniform(0.0, 1.0),
            'metric_unit': fake.random_element(['percentage', 'count', 'seconds', 'score']),
            'metric_category': fake.random_element(['efficiency', 'quality', 'performance']),
            'created_at': cls.generate_datetime()
        }

    @classmethod
    def create_with_result(cls, session: Session, result_id: str, **kwargs) -> SchedulingMetric:
        """创建带有结果的调度指标"""
        defaults = {'result_id': result_id}
        defaults.update(kwargs)
        return cls.create(session, **defaults)