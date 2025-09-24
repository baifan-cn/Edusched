"""教师数据工厂"""

import uuid
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import Teacher
from .base_factory import BaseFactory, fake


class TeacherFactory(BaseFactory[Teacher]):
    """教师数据工厂"""

    model_class = Teacher

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取教师默认字段值"""
        first_name = fake.first_name()
        last_name = fake.last_name()

        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'first_name': first_name,
            'last_name': last_name,
            'email': cls.generate_email(f"{first_name}.{last_name}"),
            'phone': cls.generate_phone(),
            'department': fake.random_element([
                '数学系', '语文系', '英语系', '物理系',
                '化学系', '生物系', '历史系', '地理系'
            ]),
            'title': fake.random_element([
                '教授', '副教授', '讲师', '助教'
            ]),
            'max_hours_per_week': fake.random_int(min=10, max=30),
            'preferred_time_slots': cls._generate_preferred_time_slots(),
            'unavailable_time_slots': [],
            'subject_specialties': [],
            'is_active': True,
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def _generate_preferred_time_slots(cls) -> List[str]:
        """生成偏好时间段"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        times = ['09:00', '10:00', '14:00', '15:00', '16:00']

        preferred = []
        num_slots = fake.random_int(min=3, max=8)

        for _ in range(num_slots):
            day = fake.random_element(days)
            time = fake.random_element(times)
            slot = f"{day}_{time}"
            if slot not in preferred:
                preferred.append(slot)

        return preferred

    @classmethod
    def create_math_teacher(cls, session: Session, **kwargs) -> Teacher:
        """创建数学教师"""
        defaults = {
            'department': '数学系',
            'subject_specialties': ['数学', '高等数学', '线性代数'],
            'title': '教授'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_chinese_teacher(cls, session: Session, **kwargs) -> Teacher:
        """创建语文教师"""
        defaults = {
            'department': '语文系',
            'subject_specialties': ['语文', '文学', '写作'],
            'title': '副教授'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_english_teacher(cls, session: Session, **kwargs) -> Teacher:
        """创建英语教师"""
        defaults = {
            'department': '英语系',
            'subject_specialties': ['英语', '口语', '写作'],
            'title': '讲师'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_with_unavailable_slots(cls, session: Session, unavailable_slots: List[str], **kwargs) -> Teacher:
        """创建有不可用时间段的教师"""
        defaults = {'unavailable_time_slots': unavailable_slots}
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_part_time_teacher(cls, session: Session, **kwargs) -> Teacher:
        """创建兼职教师"""
        defaults = {
            'max_hours_per_week': fake.random_int(min=5, max=15),
            'title': '兼职讲师'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)