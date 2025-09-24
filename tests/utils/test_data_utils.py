"""测试数据工具"""

import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date, time
from faker import Faker
import json

fake = Faker('zh_CN')


class TestDataUtils:
    """测试数据工具类"""

    @staticmethod
    def generate_uuid() -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    @staticmethod
    def generate_tenant_id() -> str:
        """生成租户ID"""
        return f"tenant_{fake.random_number(digits=6)}"

    @staticmethod
    def generate_school_id() -> str:
        """生成学校ID"""
        return f"school_{fake.random_number(digits=6)}"

    @staticmethod
    def generate_teacher_id() -> str:
        """生成教师ID"""
        return f"teacher_{fake.random_number(digits=6)}"

    @staticmethod
    def generate_course_id() -> str:
        """生成课程ID"""
        return f"course_{fake.random_number(digits=6)}"

    @staticmethod
    def generate_class_id() -> str:
        """生成班级ID"""
        return f"class_{fake.random_number(digits=6)}"

    @staticmethod
    def generate_name(prefix: str = "测试") -> str:
        """生成测试名称"""
        return f"{prefix}{fake.random_number(digits=4)}"

    @staticmethod
    def generate_email(name: str = None) -> str:
        """生成测试邮箱"""
        if name:
            return f"{name.lower().replace(' ', '.')}@test.edu"
        return fake.email()

    @staticmethod
    def generate_phone() -> str:
        """生成测试电话号码"""
        return fake.phone_number()

    @staticmethod
    def generate_address() -> str:
        """生成测试地址"""
        return fake.address()

    @staticmethod
    def generate_date(start_date: str = "-1y", end_date: str = "today") -> date:
        """生成测试日期"""
        return fake.date_between(start_date=start_date, end_date=end_date)

    @staticmethod
    def generate_datetime(start_date: str = "-1y", end_date: str = "now") -> datetime:
        """生成测试日期时间"""
        return fake.date_time_between(start_date=start_date, end_date=end_date)

    @staticmethod
    def generate_time() -> time:
        """生成测试时间"""
        return fake.time_object()

    @staticmethod
    def generate_semester() -> str:
        """生成学期"""
        year = fake.random_int(min=2024, max=2026)
        semester = fake.random_element(['春季', '秋季'])
        return f"{year}-{semester}"

    @staticmethod
    def generate_department() -> str:
        """生成院系"""
        return fake.random_element([
            '数学系', '语文系', '英语系', '物理系',
            '化学系', '生物系', '历史系', '地理系',
            '计算机系', '艺术系', '体育系'
        ])

    @staticmethod
    def generate_title() -> str:
        """生成职称"""
        return fake.random_element(['教授', '副教授', '讲师', '助教', '兼职讲师'])

    @staticmethod
    def generate_student_id() -> str:
        """生成学生ID"""
        return f"student_{fake.random_number(digits=8)}"

    @staticmethod
    def generate_classroom() -> str:
        """生成教室"""
        building = fake.random_element(['A', 'B', 'C', 'D'])
        floor = fake.random_int(min=1, max=5)
        room = fake.random_int(min=1, max=20)
        return f"{building}{floor:02d}{room:02d}"

    @staticmethod
    def generate_course_code() -> str:
        """生成课程代码"""
        subject = fake.random_element(['MATH', 'ENG', 'PHY', 'CHEM', 'BIO', 'HIST', 'GEO'])
        number = fake.random_int(min=100, max=999)
        return f"{subject}{number}"

    @staticmethod
    def generate_section_number() -> str:
        """生成教学段编号"""
        return f"SEC{fake.random_number(digits=3)}"

    @staticmethod
    def generate_timeslot_key() -> str:
        """生成时间段键"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        times = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
        day = fake.random_element(days)
        time = fake.random_element(times)
        return f"{day}_{time}"

    @staticmethod
    def generate_constraint_type() -> str:
        """生成约束类型"""
        return fake.random_element(['hard', 'soft', 'preference'])

    @staticmethod
    def generate_constraint_name() -> str:
        """生成约束名称"""
        return fake.random_element([
            'teacher_conflict', 'room_conflict', 'class_conflict',
            'teacher_preference', 'room_capacity', 'time_preference',
            'subject_balance', 'workload_balance'
        ])

    @staticmethod
    def generate_assignment_status() -> str:
        """生成分配状态"""
        return fake.random_element(['scheduled', 'in_progress', 'completed', 'cancelled'])

    @staticmethod
    def generate_conflict_status() -> str:
        """生成冲突状态"""
        return fake.random_element(['no_conflict', 'teacher_conflict', 'room_conflict', 'class_conflict'])

    @staticmethod
    def generate_problem_status() -> str:
        """生成问题状态"""
        return fake.random_element(['pending', 'in_progress', 'completed', 'failed'])

    @staticmethod
    def generate_solution_status() -> str:
        """生成解决方案状态"""
        return fake.random_element(['draft', 'optimizing', 'completed', 'failed'])

    @staticmethod
    def generate_school_data(**kwargs) -> Dict[str, Any]:
        """生成学校数据"""
        data = {
            'name': TestDataUtils.generate_name('测试学校'),
            'code': f"SCHOOL{fake.random_number(digits=4)}",
            'address': TestDataUtils.generate_address(),
            'phone': TestDataUtils.generate_phone(),
            'email': TestDataUtils.generate_email('school'),
            'is_active': True,
            'settings': {
                'max_students_per_class': 40,
                'school_hours': '08:00-17:00',
                'lunch_break': '12:00-13:00',
                'class_duration': 45,
                'break_duration': 10
            }
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_teacher_data(**kwargs) -> Dict[str, Any]:
        """生成教师数据"""
        first_name = fake.first_name()
        last_name = fake.last_name()

        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': TestDataUtils.generate_email(f"{first_name}.{last_name}"),
            'phone': TestDataUtils.generate_phone(),
            'department': TestDataUtils.generate_department(),
            'title': TestDataUtils.generate_title(),
            'max_hours_per_week': fake.random_int(min=10, max=30),
            'preferred_time_slots': [TestDataUtils.generate_timeslot_key() for _ in range(3)],
            'unavailable_time_slots': [],
            'subject_specialties': [],
            'is_active': True
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_course_data(**kwargs) -> Dict[str, Any]:
        """生成课程数据"""
        data = {
            'name': TestDataUtils.generate_name('测试课程'),
            'code': TestDataUtils.generate_course_code(),
            'description': fake.text(max_nb_chars=200),
            'credit_hours': fake.random_int(min=1, max=6),
            'weekly_hours': fake.random_int(min=1, max=8),
            'semester': TestDataUtils.generate_semester(),
            'course_type': fake.random_element(['必修课', '选修课', '通识课']),
            'is_active': True,
            'prerequisites': []
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_class_data(**kwargs) -> Dict[str, Any]:
        """生成班级数据"""
        data = {
            'name': TestDataUtils.generate_name('测试班级'),
            'grade_level': fake.random_int(min=1, max=12),
            'student_count': fake.random_int(min=20, max=50),
            'classroom': TestDataUtils.generate_classroom(),
            'supervisor': fake.name(),
            'is_active': True
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_timeslot_data(**kwargs) -> Dict[str, Any]:
        """生成时间段数据"""
        data = {
            'day_of_week': fake.random_int(min=1, max=7),
            'start_time': fake.random_element(['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']),
            'end_time': fake.random_element(['10:00', '11:00', '12:00', '15:00', '16:00', '17:00']),
            'period_type': fake.random_element(['class', 'break', 'lunch']),
            'is_active': True
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_section_data(**kwargs) -> Dict[str, Any]:
        """生成教学段数据"""
        data = {
            'section_number': TestDataUtils.generate_section_number(),
            'max_students': fake.random_int(min=20, max=50),
            'current_students': 0,
            'weekly_hours': fake.random_int(min=1, max=6),
            'semester': TestDataUtils.generate_semester(),
            'classroom': TestDataUtils.generate_classroom(),
            'schedule_requirements': {},
            'is_active': True
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_assignment_data(**kwargs) -> Dict[str, Any]:
        """生成分配数据"""
        data = {
            'classroom_id': TestDataUtils.generate_classroom(),
            'assigned_by': 'system',
            'assignment_status': TestDataUtils.generate_assignment_status(),
            'conflict_status': TestDataUtils.generate_conflict_status(),
            'priority_score': fake.random_int(min=1, max=10),
            'is_active': True
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_scheduling_problem_data(**kwargs) -> Dict[str, Any]:
        """生成调度问题数据"""
        data = {
            'semester': TestDataUtils.generate_semester(),
            'problem_status': TestDataUtils.generate_problem_status(),
            'input_data': {},
            'constraints': {},
            'objective_weights': {
                'teacher_conflicts': 1.0,
                'room_conflicts': 1.0,
                'class_conflicts': 1.0,
                'teacher_preferences': 0.8,
                'room_utilization': 0.6,
                'balanced_distribution': 0.7
            }
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_scheduling_solution_data(**kwargs) -> Dict[str, Any]:
        """生成调度解决方案数据"""
        data = {
            'solution_status': TestDataUtils.generate_solution_status(),
            'assignments': [],
            'metrics': {},
            'quality_score': 0.0,
            'constraint_violations': []
        }
        data.update(kwargs)
        return data

    @staticmethod
    def generate_batch_data(generator_func, count: int, **kwargs) -> List[Dict[str, Any]]:
        """批量生成测试数据"""
        return [generator_func(**kwargs) for _ in range(count)]

    @staticmethod
    def generate_test_data_set():
        """生成完整的测试数据集"""
        return {
            'school': TestDataUtils.generate_school_data(),
            'teachers': TestDataUtils.generate_batch_data(
                TestDataUtils.generate_teacher_data, 5
            ),
            'courses': TestDataUtils.generate_batch_data(
                TestDataUtils.generate_course_data, 10
            ),
            'classes': TestDataUtils.generate_batch_data(
                TestDataUtils.generate_class_data, 8
            ),
            'timeslots': TestDataUtils.generate_batch_data(
                TestDataUtils.generate_timeslot_data, 30
            )
        }

    @staticmethod
    def generate_json_test_data(data: Dict[str, Any]) -> str:
        """生成JSON测试数据"""
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def load_json_test_data(json_str: str) -> Dict[str, Any]:
        """加载JSON测试数据"""
        return json.loads(json_str)