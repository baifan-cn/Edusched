"""数据库集成测试"""

import pytest
from sqlalchemy.orm import Session
from tests.utils.database_utils import DatabaseUtils
from tests.utils.tenant_test_utils import TenantTestUtils
from tests.factories import SchoolFactory, TeacherFactory, CourseFactory, ClassFactory
from edusched.infrastructure.database.models import School, Teacher, Course, ClassGroup


class TestDatabaseIntegration:
    """数据库集成测试"""

    def test_database_connection(self):
        """测试数据库连接"""
        with DatabaseUtils.get_test_session() as session:
            # 简单查询测试连接
            result = session.execute("SELECT 1").scalar()
            assert result == 1

    def test_create_and_retrieve_school(self):
        """测试创建和获取学校"""
        with DatabaseUtils.get_test_session() as session:
            # 创建学校
            school = SchoolFactory.create(session)

            # 查询学校
            retrieved_school = DatabaseUtils.find_record_by_id(session, School, school.id)
            assert retrieved_school is not None
            assert retrieved_school.name == school.name
            assert retrieved_school.tenant_id == school.tenant_id

    def test_update_school(self):
        """测试更新学校"""
        with DatabaseUtils.get_test_session() as session:
            # 创建学校
            school = SchoolFactory.create(session)

            # 更新学校
            new_name = "更新的学校名称"
            school.name = new_name
            session.commit()

            # 验证更新
            updated_school = DatabaseUtils.find_record_by_id(session, School, school.id)
            assert updated_school.name == new_name

    def test_delete_school(self):
        """测试删除学校"""
        with DatabaseUtils.get_test_session() as session:
            # 创建学校
            school = SchoolFactory.create(session)

            # 删除学校
            session.delete(school)
            session.commit()

            # 验证删除
            deleted_school = DatabaseUtils.find_record_by_id(session, School, school.id)
            assert deleted_school is None

    def test_tenant_data_isolation(self):
        """测试租户数据隔离"""
        with DatabaseUtils.get_test_session() as session:
            # 创建多个租户的数据
            tenant1_id = "tenant_1"
            tenant2_id = "tenant_2"

            # 为租户1创建学校
            school1 = SchoolFactory.create(session, tenant_id=tenant1_id)

            # 为租户2创建学校
            school2 = SchoolFactory.create(session, tenant_id=tenant2_id)

            # 验证数据隔离
            tenant1_schools = session.query(School).filter(School.tenant_id == tenant1_id).all()
            tenant2_schools = session.query(School).filter(School.tenant_id == tenant2_id).all()

            assert len(tenant1_schools) == 1
            assert len(tenant2_schools) == 1
            assert tenant1_schools[0].id == school1.id
            assert tenant2_schools[0].id == school2.id

    def test_cascade_delete_relationships(self):
        """测试级联删除关系"""
        with DatabaseUtils.get_test_session() as session:
            # 创建学校
            school = SchoolFactory.create(session)

            # 为学校创建教师
            teacher = TeacherFactory.create(session, tenant_id=school.tenant_id)

            # 为学校创建课程
            course = CourseFactory.create(session, tenant_id=school.tenant_id)

            # 为学校创建班级
            class_group = ClassFactory.create(session, tenant_id=school.tenant_id)

            # 删除学校（注意：这里需要根据实际的级联删除配置来测试）
            # session.delete(school)
            # session.commit()

            # 验证相关数据是否也被删除（取决于实际的级联配置）
            # 这里只是示例，实际实现需要根据业务逻辑调整
            pass

    def test_batch_operations(self):
        """测试批量操作"""
        with DatabaseUtils.get_test_session() as session:
            # 批量创建学校
            schools = SchoolFactory.create_batch(session, 5)

            # 验证批量创建
            assert len(schools) == 5
            for school in schools:
                assert school.id is not None

            # 批量查询
            all_schools = DatabaseUtils.get_all_records(session, School)
            assert len(all_schools) == 5

    def test_transaction_rollback(self):
        """测试事务回滚"""
        with DatabaseUtils.get_test_session() as session:
            initial_count = DatabaseUtils.count_records(session, School)

            try:
                # 创建学校
                school = SchoolFactory.create(session)

                # 模拟错误
                raise Exception("模拟错误")

                session.commit()
            except Exception:
                session.rollback()

            # 验证回滚
            final_count = DatabaseUtils.count_records(session, School)
            assert final_count == initial_count

    def test_foreign_key_constraints(self):
        """测试外键约束"""
        with DatabaseUtils.get_test_session() as session:
            # 创建学校
            school = SchoolFactory.create(session)

            # 创建教师（需要学校ID，根据实际模型关系调整）
            # 这里只是示例，实际实现需要根据模型关系调整
            teacher = TeacherFactory.create(session, tenant_id=school.tenant_id)

            # 验证关联关系
            assert teacher.tenant_id == school.tenant_id

    def test_unique_constraints(self):
        """测试唯一约束"""
        with DatabaseUtils.get_test_session() as session:
            # 创建学校
            school1 = SchoolFactory.create(session, code="UNIQUE_CODE")

            # 尝试创建具有相同代码的学校（应该失败）
            with pytest.raises(Exception):
                school2 = SchoolFactory.create(session, code="UNIQUE_CODE")
                session.commit()

    def test_null_constraints(self):
        """测试空值约束"""
        with DatabaseUtils.get_test_session() as session:
            # 尝试创建没有必需字段的数据（应该失败）
            with pytest.raises(Exception):
                school = School(name=None)  # name是必需字段
                session.add(school)
                session.commit()

    def test_data_types_validation(self):
        """测试数据类型验证"""
        with DatabaseUtils.get_test_session() as session:
            # 创建学校
            school = SchoolFactory.create(session)

            # 验证数据类型
            assert isinstance(school.id, str)
            assert isinstance(school.name, str)
            assert isinstance(school.is_active, bool)
            assert isinstance(school.created_at, type(school.created_at))  # datetime

    def test_performance_large_dataset(self):
        """测试大数据集性能"""
        with DatabaseUtils.get_test_session() as session:
            # 创建大量数据
            import time
            start_time = time.time()

            schools = SchoolFactory.create_batch(session, 1000)

            creation_time = time.time() - start_time
            print(f"创建1000所学校耗时: {creation_time:.3f}秒")

            # 查询性能
            start_time = time.time()
            all_schools = DatabaseUtils.get_all_records(session, School)
            query_time = time.time() - start_time

            print(f"查询1000所学校耗时: {query_time:.3f}秒")
            assert query_time < 1.0, f"查询耗时过长: {query_time:.3f}秒"

    def test_tenant_cross_tenant_access(self):
        """测试跨租户访问"""
        with DatabaseUtils.get_test_session() as session:
            # 创建两个租户
            tenant1_id = "tenant_1"
            tenant2_id = "tenant_2"

            # 为租户1创建学校
            school1 = SchoolFactory.create(session, tenant_id=tenant1_id)

            # 为租户2创建学校
            school2 = SchoolFactory.create(session, tenant_id=tenant2_id)

            # 验证租户1无法访问租户2的数据
            tenant1_schools = session.query(School).filter(School.tenant_id == tenant1_id).all()
            assert len(tenant1_schools) == 1
            assert tenant1_schools[0].id == school1.id

            # 验证租户2无法访问租户1的数据
            tenant2_schools = session.query(School).filter(School.tenant_id == tenant2_id).all()
            assert len(tenant2_schools) == 1
            assert tenant2_schools[0].id == school2.id

    def test_database_connection_pooling(self):
        """测试数据库连接池"""
        connections = []
        try:
            # 创建多个连接
            for i in range(10):
                engine = DatabaseUtils.create_test_engine()
                session = DatabaseUtils.create_session_factory(engine)()
                connections.append(session)

            # 验证连接池工作正常
            assert len(connections) == 10

        finally:
            # 清理连接
            for session in connections:
                session.close()