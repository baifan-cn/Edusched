"""教学段数据工厂"""

import uuid
from typing import Any, Dict
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import Section
from .base_factory import BaseFactory, fake


class SectionFactory(BaseFactory[Section]):
    """教学段数据工厂"""

    model_class = Section

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取教学段默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'course_id': None,  # 需要在外部设置
            'teacher_id': None,  # 需要在外部设置
            'class_group_id': None,  # 需要在外部设置
            'section_number': f"SEC{fake.random_number(digits=3)}",
            'max_students': fake.random_int(min=20, max=50),
            'current_students': 0,
            'weekly_hours': fake.random_int(min=1, max=6),
            'semester': fake.random_element([
                '2024-春季', '2024-秋季', '2025-春季', '2025-秋季'
            ]),
            'classroom': f"教室{fake.random_number(digits=3)}",
            'schedule_requirements': {},
            'is_active': True,
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_with_relationships(cls, session: Session, course_id: str, teacher_id: str, class_group_id: str, **kwargs) -> Section:
        """创建带有关系的教学段"""
        defaults = {
            'course_id': course_id,
            'teacher_id': teacher_id,
            'class_group_id': class_group_id,
            'section_number': f"{course_id[-3:]}-{fake.random_number(digits=2)}"
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_math_section(cls, session: Session, course_id: str, teacher_id: str, class_group_id: str, **kwargs) -> Section:
        """创建数学教学段"""
        defaults = {
            'course_id': course_id,
            'teacher_id': teacher_id,
            'class_group_id': class_group_id,
            'section_number': f"MATH-{fake.random_number(digits=2)}",
            'weekly_hours': 4,
            'max_students': 40,
            'classroom': f"数学教室{fake.random_number(digits=2)}",
            'schedule_requirements': {
                'requires_blackboard': True,
                'requires_projector': True
            }
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_language_section(cls, session: Session, course_id: str, teacher_id: str, class_group_id: str, **kwargs) -> Section:
        """创建语言教学段"""
        defaults = {
            'course_id': course_id,
            'teacher_id': teacher_id,
            'class_group_id': class_group_id,
            'section_number': f"LANG-{fake.random_number(digits=2)}",
            'weekly_hours': 3,
            'max_students': 35,
            'classroom': f"语言教室{fake.random_number(digits=2)}",
            'schedule_requirements': {
                'requires_audio_equipment': True,
                'requires_projector': True
            }
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_science_section(cls, session: Session, course_id: str, teacher_id: str, class_group_id: str, **kwargs) -> Section:
        """创建科学教学段"""
        defaults = {
            'course_id': course_id,
            'teacher_id': teacher_id,
            'class_group_id': class_group_id,
            'section_number': f"SCI-{fake.random_number(digits=2)}",
            'weekly_hours': 3,
            'max_students': 30,
            'classroom': f"实验室{fake.random_number(digits=2)}",
            'schedule_requirements': {
                'requires_lab_equipment': True,
                'requires_safety_gear': True
            }
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_with_students(cls, session: Session, course_id: str, teacher_id: str, class_group_id: str, student_count: int, **kwargs) -> Section:
        """创建有固定学生数量的教学段"""
        defaults = {
            'course_id': course_id,
            'teacher_id': teacher_id,
            'class_group_id': class_group_id,
            'current_students': student_count,
            'max_students': max(student_count + 5, 20)
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)