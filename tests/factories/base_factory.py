"""基础工厂类"""

import uuid
from typing import Any, Dict, Generic, Type, TypeVar
from datetime import datetime, date
from faker import Faker
from sqlalchemy.orm import Session

T = TypeVar('T')

fake = Faker('zh_CN')


class BaseFactory(Generic[T]):
    """基础数据工厂类"""

    model_class: Type[T]

    @classmethod
    def create(cls, session: Session, **kwargs) -> T:
        """创建并保存模型实例"""
        data = cls.build(**kwargs)
        instance = cls.model_class(**data)
        session.add(instance)
        session.flush()
        return instance

    @classmethod
    def build(cls, **kwargs) -> Dict[str, Any]:
        """构建模型数据字典"""
        data = cls.get_defaults()
        data.update(kwargs)
        return data

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """获取默认字段值"""
        return {}

    @classmethod
    def create_batch(cls, session: Session, count: int, **kwargs) -> list[T]:
        """批量创建模型实例"""
        instances = []
        for _ in range(count):
            instance = cls.create(session, **kwargs)
            instances.append(instance)
        return instances

    @classmethod
    def generate_id(cls) -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    @classmethod
    def generate_name(cls, prefix: str = "测试") -> str:
        """生成测试名称"""
        return f"{prefix}{fake.random_number(digits=4)}"

    @classmethod
    def generate_email(cls, name: str = None) -> str:
        """生成测试邮箱"""
        if name:
            return f"{name.lower().replace(' ', '.')}@test.edu"
        return fake.email()

    @classmethod
    def generate_phone(cls) -> str:
        """生成测试电话号码"""
        return fake.phone_number()

    @classmethod
    def generate_date(cls) -> date:
        """生成测试日期"""
        return fake.date_between(start_date='-1y', end_date='today')

    @classmethod
    def generate_datetime(cls) -> datetime:
        """生成测试日期时间"""
        return fake.date_time_between(start_date='-1y', end_date='now')