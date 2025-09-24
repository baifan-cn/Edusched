"""课程安排数据工厂"""

import uuid
from typing import Any, Dict
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import Assignment
from .base_factory import BaseFactory, fake


class AssignmentFactory(BaseFactory[Assignment]):
    """课程安排数据工厂"""

    model_class = Assignment

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取课程安排默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'section_id': None,  # 需要在外部设置
            'timeslot_id': None,  # 需要在外部设置
            'classroom_id': f"教室{fake.random_number(digits=3)}",
            'assigned_by': 'system',
            'assignment_status': fake.random_element([
                'scheduled', 'in_progress', 'completed', 'cancelled'
            ]),
            'conflict_status': 'no_conflict',
            'priority_score': fake.random_int(min=1, max=10),
            'is_active': True,
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_with_relationships(cls, session: Session, section_id: str, timeslot_id: str, **kwargs) -> Assignment:
        """创建带有关系的课程安排"""
        defaults = {
            'section_id': section_id,
            'timeslot_id': timeslot_id
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_scheduled_assignment(cls, session: Session, section_id: str, timeslot_id: str, **kwargs) -> Assignment:
        """创建已安排的课程"""
        defaults = {
            'section_id': section_id,
            'timeslot_id': timeslot_id,
            'assignment_status': 'scheduled',
            'conflict_status': 'no_conflict',
            'priority_score': fake.random_int(min=5, max=10)
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_conflict_assignment(cls, session: Session, section_id: str, timeslot_id: str, **kwargs) -> Assignment:
        """创建有冲突的课程安排"""
        defaults = {
            'section_id': section_id,
            'timeslot_id': timeslot_id,
            'assignment_status': 'scheduled',
            'conflict_status': 'teacher_conflict',
            'priority_score': fake.random_int(min=1, max=5)
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_high_priority_assignment(cls, session: Session, section_id: str, timeslot_id: str, **kwargs) -> Assignment:
        """创建高优先级课程安排"""
        defaults = {
            'section_id': section_id,
            'timeslot_id': timeslot_id,
            'assignment_status': 'scheduled',
            'conflict_status': 'no_conflict',
            'priority_score': fake.random_int(min=8, max=10)
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)