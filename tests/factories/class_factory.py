"""班级数据工厂"""

import uuid
from typing import Any, Dict
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import ClassGroup
from .base_factory import BaseFactory, fake


class ClassFactory(BaseFactory[ClassGroup]):
    """班级数据工厂"""

    model_class = ClassGroup

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取班级默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'name': cls.generate_name('测试班级'),
            'grade_level': fake.random_int(min=1, max=6),
            'student_count': fake.random_int(min=20, max=50),
            'classroom': f"教室{fake.random_number(digits=3)}",
            'supervisor': fake.name(),
            'is_active': True,
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_elementary_class(cls, session: Session, **kwargs) -> ClassGroup:
        """创建小学班级"""
        defaults = {
            'name': cls.generate_name('小学'),
            'grade_level': fake.random_int(min=1, max=6),
            'student_count': fake.random_int(min=25, max=40),
            'classroom': f"小学教室{fake.random_number(digits=2)}"
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_middle_class(cls, session: Session, **kwargs) -> ClassGroup:
        """创建中学班级"""
        defaults = {
            'name': cls.generate_name('中学'),
            'grade_level': fake.random_int(min=7, max=9),
            'student_count': fake.random_int(min=30, max=50),
            'classroom': f"中学教室{fake.random_number(digits=2)}"
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_high_class(cls, session: Session, **kwargs) -> ClassGroup:
        """创建高中班级"""
        defaults = {
            'name': cls.generate_name('高中'),
            'grade_level': fake.random_int(min=10, max=12),
            'student_count': fake.random_int(min=35, max=55),
            'classroom': f"高中教室{fake.random_number(digits=2)}"
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_university_class(cls, session: Session, **kwargs) -> ClassGroup:
        """创建大学班级"""
        defaults = {
            'name': cls.generate_name('大学'),
            'grade_level': fake.random_int(min=13, max=16),
            'student_count': fake.random_int(min=40, max=200),
            'classroom': f"大学教室{fake.random_number(digits=3)}"
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)