"""课程数据工厂"""

import uuid
from typing import Any, Dict
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import Course
from .base_factory import BaseFactory, fake


class CourseFactory(BaseFactory[Course]):
    """课程数据工厂"""

    model_class = Course

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取课程默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'name': cls.generate_name('测试课程'),
            'code': f"COURSE{fake.random_number(digits=3)}",
            'description': fake.text(max_nb_chars=200),
            'credit_hours': fake.random_int(min=1, max=6),
            'weekly_hours': fake.random_int(min=1, max=8),
            'semester': fake.random_element([
                '2024-春季', '2024-秋季', '2025-春季', '2025-秋季'
            ]),
            'course_type': fake.random_element([
                '必修课', '选修课', '通识课', '专业基础课'
            ]),
            'is_active': True,
            'prerequisites': [],
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_math_course(cls, session: Session, **kwargs) -> Course:
        """创建数学课程"""
        defaults = {
            'name': cls.generate_name('高等数学'),
            'code': f"MATH{fake.random_number(digits=3)}",
            'credit_hours': 4,
            'weekly_hours': 4,
            'course_type': '必修课',
            'description': '高等数学基础课程，涵盖微积分、线性代数等内容'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_language_course(cls, session: Session, **kwargs) -> Course:
        """创建语言课程"""
        defaults = {
            'name': cls.generate_name('大学英语'),
            'code': f"ENG{fake.random_number(digits=3)}",
            'credit_hours': 3,
            'weekly_hours': 3,
            'course_type': '必修课',
            'description': '大学英语课程，提高学生英语综合能力'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_science_course(cls, session: Session, **kwargs) -> Course:
        """创建科学课程"""
        defaults = {
            'name': cls.generate_name('物理学'),
            'code': f"PHY{fake.random_number(digits=3)}",
            'credit_hours': 3,
            'weekly_hours': 3,
            'course_type': '必修课',
            'description': '大学物理课程，涵盖力学、热学、电磁学等内容'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_elective_course(cls, session: Session, **kwargs) -> Course:
        """创建选修课程"""
        defaults = {
            'name': cls.generate_name('艺术欣赏'),
            'code': f"ART{fake.random_number(digits=3)}",
            'credit_hours': 2,
            'weekly_hours': 2,
            'course_type': '选修课',
            'description': '艺术欣赏课程，提高学生艺术素养'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_with_prerequisites(cls, session: Session, prerequisites: list, **kwargs) -> Course:
        """创建有先修要求的课程"""
        defaults = {'prerequisites': prerequisites}
        defaults.update(kwargs)
        return cls.create(session, **defaults)