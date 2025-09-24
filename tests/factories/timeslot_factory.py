"""时间段数据工厂"""

import uuid
from typing import Any, Dict
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import Timeslot
from .base_factory import BaseFactory, fake


class TimeslotFactory(BaseFactory[Timeslot]):
    """时间段数据工厂"""

    model_class = Timeslot

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取时间段默认字段值"""
        return {
            'id': cls.generate_id(),
            'tenant_id': 'test_tenant',
            'day_of_week': fake.random_int(min=1, max=7),
            'start_time': '09:00',
            'end_time': '10:00',
            'period_type': fake.random_element(['class', 'break', 'lunch']),
            'is_active': True,
            'created_at': cls.generate_datetime(),
            'updated_at': cls.generate_datetime()
        }

    @classmethod
    def create_morning_class(cls, session: Session, **kwargs) -> Timeslot:
        """创建上午课程时间段"""
        defaults = {
            'day_of_week': fake.random_int(min=1, max=5),
            'start_time': fake.random_element(['08:00', '09:00', '10:00']),
            'end_time': fake.random_element(['08:45', '09:45', '10:45']),
            'period_type': 'class'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_afternoon_class(cls, session: Session, **kwargs) -> Timeslot:
        """创建下午课程时间段"""
        defaults = {
            'day_of_week': fake.random_int(min=1, max=5),
            'start_time': fake.random_element(['14:00', '15:00', '16:00']),
            'end_time': fake.random_element(['14:45', '15:45', '16:45']),
            'period_type': 'class'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_lunch_break(cls, session: Session, **kwargs) -> Timeslot:
        """创建午休时间段"""
        defaults = {
            'day_of_week': fake.random_int(min=1, max=5),
            'start_time': '12:00',
            'end_time': '13:00',
            'period_type': 'lunch'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_break_time(cls, session: Session, **kwargs) -> Timeslot:
        """创建课间休息时间段"""
        defaults = {
            'day_of_week': fake.random_int(min=1, max=5),
            'start_time': fake.random_element(['10:00', '15:00']),
            'end_time': fake.random_element(['10:15', '15:15']),
            'period_type': 'break'
        }
        defaults.update(kwargs)
        return cls.create(session, **defaults)

    @classmethod
    def create_weekly_schedule(cls, session: Session) -> list[Timeslot]:
        """创建一周的时间段"""
        timeslots = []

        # 上午课程
        for day in range(1, 6):  # 周一到周五
            for hour in ['08:00', '09:00', '10:00']:
                timeslot = cls.create(
                    session,
                    day_of_week=day,
                    start_time=hour,
                    end_time=f"{int(hour[:2]) + 1}:00",
                    period_type='class'
                )
                timeslots.append(timeslot)

        # 下午课程
        for day in range(1, 6):
            for hour in ['14:00', '15:00', '16:00']:
                timeslot = cls.create(
                    session,
                    day_of_week=day,
                    start_time=hour,
                    end_time=f"{int(hour[:2]) + 1}:00",
                    period_type='class'
                )
                timeslots.append(timeslot)

        # 午休
        for day in range(1, 6):
            timeslot = cls.create_lunch_break(session, day_of_week=day)
            timeslots.append(timeslot)

        return timeslots