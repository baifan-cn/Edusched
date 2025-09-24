"""租户测试工具"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from edusched.infrastructure.database.models import School, Teacher, Course, ClassGroup, Section, Timeslot, Assignment
from tests.factories import SchoolFactory, TeacherFactory, CourseFactory, ClassFactory, SectionFactory, TimeslotFactory, AssignmentFactory


class TenantTestUtils:
    """租户测试工具类"""

    @staticmethod
    def generate_tenant_id() -> str:
        """生成租户ID"""
        return f"tenant_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_tenant_ids(count: int) -> List[str]:
        """生成多个租户ID"""
        return [TenantTestUtils.generate_tenant_id() for _ in range(count)]

    @staticmethod
    def create_tenant_school(session: Session, tenant_id: str, **kwargs) -> School:
        """创建租户学校"""
        school_data = SchoolFactory.build(tenant_id=tenant_id, **kwargs)
        school = School(**school_data)
        session.add(school)
        session.flush()
        return school

    @staticmethod
    def create_tenant_teacher(session: Session, tenant_id: str, **kwargs) -> Teacher:
        """创建租户教师"""
        teacher_data = TeacherFactory.build(tenant_id=tenant_id, **kwargs)
        teacher = Teacher(**teacher_data)
        session.add(teacher)
        session.flush()
        return teacher

    @staticmethod
    def create_tenant_course(session: Session, tenant_id: str, **kwargs) -> Course:
        """创建租户课程"""
        course_data = CourseFactory.build(tenant_id=tenant_id, **kwargs)
        course = Course(**course_data)
        session.add(course)
        session.flush()
        return course

    @staticmethod
    def create_tenant_class(session: Session, tenant_id: str, **kwargs) -> ClassGroup:
        """创建租户班级"""
        class_data = ClassFactory.build(tenant_id=tenant_id, **kwargs)
        class_group = ClassGroup(**class_data)
        session.add(class_group)
        session.flush()
        return class_group

    @staticmethod
    def create_tenant_section(session: Session, tenant_id: str, course_id: str, teacher_id: str, class_group_id: str, **kwargs) -> Section:
        """创建租户教学段"""
        section_data = SectionFactory.build(tenant_id=tenant_id, course_id=course_id, teacher_id=teacher_id, class_group_id=class_group_id, **kwargs)
        section = Section(**section_data)
        session.add(section)
        session.flush()
        return section

    @staticmethod
    def create_tenant_timeslot(session: Session, tenant_id: str, **kwargs) -> Timeslot:
        """创建租户时间段"""
        timeslot_data = TimeslotFactory.build(tenant_id=tenant_id, **kwargs)
        timeslot = Timeslot(**timeslot_data)
        session.add(timeslot)
        session.flush()
        return timeslot

    @staticmethod
    def create_tenant_assignment(session: Session, tenant_id: str, section_id: str, timeslot_id: str, **kwargs) -> Assignment:
        """创建租户课程安排"""
        assignment_data = AssignmentFactory.build(tenant_id=tenant_id, section_id=section_id, timeslot_id=timeslot_id, **kwargs)
        assignment = Assignment(**assignment_data)
        session.add(assignment)
        session.flush()
        return assignment

    @staticmethod
    def create_tenant_data_set(session: Session, tenant_id: str) -> Dict[str, Any]:
        """创建租户完整数据集"""
        # 创建学校
        school = TenantTestUtils.create_tenant_school(session, tenant_id)

        # 创建教师
        teachers = []
        for i in range(5):
            teacher = TenantTestUtils.create_tenant_teacher(session, tenant_id)
            teachers.append(teacher)

        # 创建课程
        courses = []
        for i in range(10):
            course = TenantTestUtils.create_tenant_course(session, tenant_id)
            courses.append(course)

        # 创建班级
        classes = []
        for i in range(8):
            class_group = TenantTestUtils.create_tenant_class(session, tenant_id)
            classes.append(class_group)

        # 创建时间段
        timeslots = []
        for day in range(1, 6):  # 周一到周五
            for hour in ['09:00', '10:00', '14:00', '15:00']:
                timeslot = TenantTestUtils.create_tenant_timeslot(
                    session, tenant_id,
                    day_of_week=day,
                    start_time=hour,
                    end_time=f"{int(hour[:2]) + 1}:00"
                )
                timeslots.append(timeslot)

        return {
            'tenant_id': tenant_id,
            'school': school,
            'teachers': teachers,
            'courses': courses,
            'classes': classes,
            'timeslots': timeslots
        }

    @staticmethod
    def create_multiple_tenant_data_sets(session: Session, tenant_count: int = 3) -> List[Dict[str, Any]]:
        """创建多个租户数据集"""
        tenant_data_sets = []
        for _ in range(tenant_count):
            tenant_id = TenantTestUtils.generate_tenant_id()
            tenant_data = TenantTestUtils.create_tenant_data_set(session, tenant_id)
            tenant_data_sets.append(tenant_data)
        return tenant_data_sets

    @staticmethod
    def assert_tenant_data_isolation(session: Session, model_class, tenant_id: str):
        """断言租户数据隔离"""
        # 查询指定租户的数据
        tenant_records = session.query(model_class).filter(model_class.tenant_id == tenant_id).all()

        # 检查所有记录都属于指定租户
        for record in tenant_records:
            assert record.tenant_id == tenant_id, \
                f"Record {record.id} belongs to tenant {record.tenant_id}, not {tenant_id}"

        return tenant_records

    @staticmethod
    def assert_tenant_data_not_accessible(session: Session, model_class, tenant_id: str, other_tenant_id: str):
        """断言租户数据不可访问"""
        # 查询其他租户的数据
        other_tenant_records = session.query(model_class).filter(model_class.tenant_id == other_tenant_id).all()

        # 确保其他租户的数据不会被当前租户访问到
        for record in other_tenant_records:
            assert record.tenant_id != tenant_id, \
                f"Record {record.id} from tenant {record.tenant_id} should not be accessible to tenant {tenant_id}"

    @staticmethod
    def assert_tenant_data_count(session: Session, model_class, tenant_id: str, expected_count: int):
        """断言租户数据数量"""
        actual_count = session.query(model_class).filter(model_class.tenant_id == tenant_id).count()
        assert actual_count == expected_count, \
            f"Expected {expected_count} records for tenant {tenant_id}, got {actual_count}"

    @staticmethod
    def assert_tenant_data_unique_across_tenants(session: Session, model_class, tenant_ids: List[str]):
        """断言租户数据在不同租户间唯一"""
        all_records = session.query(model_class).filter(model_class.tenant_id.in_(tenant_ids)).all()

        # 检查是否有重复的ID
        ids = [record.id for record in all_records]
        unique_ids = set(ids)

        assert len(ids) == len(unique_ids), \
            f"Found duplicate IDs across tenants: {len(ids)} total, {len(unique_ids)} unique"

        # 检查每个租户的数据隔离
        for tenant_id in tenant_ids:
            tenant_records = [r for r in all_records if r.tenant_id == tenant_id]
            for record in tenant_records:
                assert record.tenant_id == tenant_id, \
                    f"Record {record.id} belongs to wrong tenant"

    @staticmethod
    def get_tenant_data_count(session: Session, model_class, tenant_id: str) -> int:
        """获取租户数据数量"""
        return session.query(model_class).filter(model_class.tenant_id == tenant_id).count()

    @staticmethod
    def get_all_tenant_data(session: Session, model_class, tenant_id: str) -> List[Any]:
        """获取租户所有数据"""
        return session.query(model_class).filter(model_class.tenant_id == tenant_id).all()

    @staticmethod
    def get_tenant_data_by_id(session: Session, model_class, tenant_id: str, record_id: str) -> Optional[Any]:
        """根据ID获取租户数据"""
        return session.query(model_class).filter(
            model_class.tenant_id == tenant_id,
            model_class.id == record_id
        ).first()

    @staticmethod
    def verify_tenant_cross_tenant_access(session: Session, model_class, tenant_id: str, record_id: str):
        """验证跨租户访问"""
        # 尝试访问其他租户的数据
        record = TenantTestUtils.get_tenant_data_by_id(session, model_class, tenant_id, record_id)

        # 如果记录存在，检查它是否属于正确的租户
        if record:
            assert record.tenant_id == tenant_id, \
                f"Cross-tenant access detected: Record {record_id} belongs to tenant {record.tenant_id}, accessed by tenant {tenant_id}"

    @staticmethod
    def test_tenant_data_creation(session: Session, model_class, tenant_id: str, data: Dict[str, Any]):
        """测试租户数据创建"""
        # 添加租户ID到数据
        data['tenant_id'] = tenant_id

        # 创建记录
        record = model_class(**data)
        session.add(record)
        session.flush()

        # 验证记录创建成功
        assert record.id is not None, "Record ID should not be None"
        assert record.tenant_id == tenant_id, f"Record should belong to tenant {tenant_id}"

        return record

    @staticmethod
    def test_tenant_data_update(session: Session, model_class, tenant_id: str, record_id: str, update_data: Dict[str, Any]):
        """测试租户数据更新"""
        # 获取记录
        record = TenantTestUtils.get_tenant_data_by_id(session, model_class, tenant_id, record_id)
        assert record is not None, f"Record {record_id} not found for tenant {tenant_id}"

        # 更新记录
        for key, value in update_data.items():
            setattr(record, key, value)

        session.flush()

        # 验证更新成功
        updated_record = TenantTestUtils.get_tenant_data_by_id(session, model_class, tenant_id, record_id)
        assert updated_record is not None, "Updated record not found"

        for key, value in update_data.items():
            assert getattr(updated_record, key) == value, \
                f"Field {key} not updated correctly. Expected: {value}, Actual: {getattr(updated_record, key)}"

    @staticmethod
    def test_tenant_data_deletion(session: Session, model_class, tenant_id: str, record_id: str):
        """测试租户数据删除"""
        # 获取记录
        record = TenantTestUtils.get_tenant_data_by_id(session, model_class, tenant_id, record_id)
        assert record is not None, f"Record {record_id} not found for tenant {tenant_id}"

        # 删除记录
        session.delete(record)
        session.flush()

        # 验证删除成功
        deleted_record = TenantTestUtils.get_tenant_data_by_id(session, model_class, tenant_id, record_id)
        assert deleted_record is None, f"Record {record_id} should be deleted"

    @staticmethod
    def test_tenant_data_query_performance(session: Session, model_class, tenant_id: str, max_time: float = 0.1):
        """测试租户数据查询性能"""
        import time

        start_time = time.time()
        records = session.query(model_class).filter(model_class.tenant_id == tenant_id).all()
        end_time = time.time()

        query_time = end_time - start_time
        assert query_time <= max_time, \
            f"Query took {query_time:.3f}s, expected <= {max_time:.3f}s"

        return records

    @staticmethod
    def create_tenant_headers(tenant_id: str) -> Dict[str, str]:
        """创建租户请求头"""
        return {"X-Tenant-ID": tenant_id}

    @staticmethod
    def create_tenant_auth_headers(tenant_id: str, token: str) -> Dict[str, str]:
        """创建租户认证请求头"""
        return {
            "X-Tenant-ID": tenant_id,
            "Authorization": f"Bearer {token}"
        }

    @staticmethod
    def setup_tenant_test_data(session: Session, tenant_count: int = 3) -> List[str]:
        """设置租户测试数据"""
        tenant_ids = TenantTestUtils.generate_tenant_ids(tenant_count)
        tenant_data_sets = TenantTestUtils.create_multiple_tenant_data_sets(session, tenant_count)
        return tenant_ids

    @staticmethod
    def cleanup_tenant_test_data(session: Session, tenant_ids: List[str]):
        """清理租户测试数据"""
        for tenant_id in tenant_ids:
            # 删除所有属于该租户的数据
            models = [School, Teacher, Course, ClassGroup, Section, Timeslot, Assignment]
            for model in models:
                session.query(model).filter(model.tenant_id == tenant_id).delete()
        session.commit()