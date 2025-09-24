"""学校数据工厂"""

import uuid
from typing import Any, Dict
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import School
from .base_factory import BaseFactory, fake


class SchoolFactory(BaseFactory[School]):
    """学校数据工厂"""

    model_class = School

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取学校默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'name': cls.generate_name('测试学校'),
            'code': f"SCHOOL{fake.random_number(digits=4)}",
            'address': fake.address(),
            'phone': cls.generate_phone(),
            'email': cls.generate_email('school'),
            'is_active': True,
            'settings': {
                'max_students_per_class': 40,
                'school_hours': '08:00-17:00',
                'lunch_break': '12:00-13:00',
                'class_duration': 45,
                'break_duration': 10,
                'max_teaching_hours_per_day': 6,
                'min_rest_hours_between_classes': 1
            },
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_elementary_school(cls, session: Session, **kwargs) -> School:
        """创建小学"""
        defaults = {
            'name': cls.generate_name('测试小学'),
            'settings': {
                'max_students_per_class': 35,
                'school_hours': '08:30-16:30',
                'class_duration': 40,
                'break_duration': 10
            }
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_middle_school(cls, session: Session, **kwargs) -> School:
        """创建中学"""
        defaults = {
            'name': cls.generate_name('测试中学'),
            'settings': {
                'max_students_per_class': 45,
                'school_hours': '08:00-17:00',
                'class_duration': 45,
                'break_duration': 10
            }
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_high_school(cls, session: Session, **kwargs) -> School:
        """创建高中"""
        defaults = {
            'name': cls.generate_name('测试高中'),
            'settings': {
                'max_students_per_class': 50,
                'school_hours': '08:00-17:30',
                'class_duration': 45,
                'break_duration': 10
            }
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_university(cls, session: Session, **kwargs) -> School:
        """创建大学"""
        defaults = {
            'name': cls.generate_name('测试大学'),
            'settings': {
                'max_students_per_class': 200,
                'school_hours': '08:00-18:00',
                'class_duration': 90,
                'break_duration': 15
            }
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)