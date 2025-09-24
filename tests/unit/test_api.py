"""API层单元测试。"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from edusched.api.main import app
from edusched.domain.models import School as DomainSchool, Teacher, Course, ClassGroup
from edusched.infrastructure.database.models import School as SchoolModel


class TestSchoolAPI:
    """学校API测试类。"""

    @pytest.fixture
    def client(self):
        """创建测试客户端。"""
        return TestClient(app)

    @pytest.fixture
    def sample_school_data(self):
        """示例学校数据。"""
        return {
            "name": "测试学校",
            "code": "TEST001",
            "address": "测试地址123号",
            "phone": "010-12345678",
            "email": "test@school.edu",
            "is_active": True,
            "settings": {"max_students_per_class": 40}
        }

    def test_create_school_success(self, client, sample_school_data):
        """测试成功创建学校。"""
        response = client.post("/api/v1/schools/", json=sample_school_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_school_data["name"]
        assert data["code"] == sample_school_data["code"]
        assert "id" in data

    def test_create_school_missing_required_field(self, client):
        """测试创建学校时缺少必填字段。"""
        incomplete_data = {
            "name": "测试学校"
            # 缺少code等必填字段
        }

        response = client.post("/api/v1/schools/", json=incomplete_data)

        assert response.status_code == 422  # Validation error

    def test_create_school_duplicate_code(self, client, sample_school_data):
        """测试创建重复代码的学校。"""
        # 先创建一个学校
        client.post("/api/v1/schools/", json=sample_school_data)

        # 尝试创建相同代码的学校
        response = client.post("/api/v1/schools/", json=sample_school_data)

        assert response.status_code == 400  # Bad request

    def test_get_schools_list(self, client, sample_school_data):
        """测试获取学校列表。"""
        # 创建几个学校
        for i in range(3):
            school_data = sample_school_data.copy()
            school_data["code"] = f"TEST{i:03d}"
            school_data["name"] = f"测试学校{i}"
            client.post("/api/v1/schools/", json=school_data)

        response = client.get("/api/v1/schools/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3
        assert "page" in data
        assert "size" in data

    def test_get_schools_with_pagination(self, client, sample_school_data):
        """测试分页获取学校列表。"""
        # 创建多个学校
        for i in range(15):
            school_data = sample_school_data.copy()
            school_data["code"] = f"TEST{i:03d}"
            school_data["name"] = f"测试学校{i}"
            client.post("/api/v1/schools/", json=school_data)

        # 获取第一页
        response = client.get("/api/v1/schools/?page=1&size=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["size"] == 10

        # 获取第二页
        response = client.get("/api/v1/schools/?page=2&size=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    def test_get_school_by_id(self, client, sample_school_data):
        """测试根据ID获取学校。"""
        # 创建学校
        create_response = client.post("/api/v1/schools/", json=sample_school_data)
        school_id = create_response.json()["id"]

        # 获取学校
        response = client.get(f"/api/v1/schools/{school_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == school_id
        assert data["name"] == sample_school_data["name"]

    def test_get_school_not_found(self, client):
        """测试获取不存在的学校。"""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/schools/{non_existent_id}")

        assert response.status_code == 404

    def test_update_school(self, client, sample_school_data):
        """测试更新学校信息。"""
        # 创建学校
        create_response = client.post("/api/v1/schools/", json=sample_school_data)
        school_id = create_response.json()["id"]

        # 更新学校
        update_data = {
            "name": "更新后的学校名称",
            "address": "更新后的地址",
            "phone": "010-87654321"
        }

        response = client.put(f"/api/v1/schools/{school_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的学校名称"
        assert data["address"] == "更新后的地址"

    def test_update_school_not_found(self, client):
        """测试更新不存在的学校。"""
        non_existent_id = str(uuid4())
        update_data = {"name": "更新后的学校名称"}

        response = client.put(f"/api/v1/schools/{non_existent_id}", json=update_data)

        assert response.status_code == 404

    def test_delete_school(self, client, sample_school_data):
        """测试删除学校。"""
        # 创建学校
        create_response = client.post("/api/v1/schools/", json=sample_school_data)
        school_id = create_response.json()["id"]

        # 删除学校
        response = client.delete(f"/api/v1/schools/{school_id}")

        assert response.status_code == 204

        # 验证学校已被删除
        get_response = client.get(f"/api/v1/schools/{school_id}")
        assert get_response.status_code == 404

    def test_delete_school_not_found(self, client):
        """测试删除不存在的学校。"""
        non_existent_id = str(uuid4())
        response = client.delete(f"/api/v1/schools/{non_existent_id}")

        assert response.status_code == 404

    def test_get_schools_with_filtering(self, client, sample_school_data):
        """测试带过滤条件的学校查询。"""
        # 创建不同状态的学校
        active_school = sample_school_data.copy()
        active_school["code"] = "ACTIVE"
        active_school["name"] = "活跃学校"
        client.post("/api/v1/schools/", json=active_school)

        inactive_school = sample_school_data.copy()
        inactive_school["code"] = "INACTIVE"
        inactive_school["name"] = "非活跃学校"
        inactive_school["is_active"] = False
        client.post("/api/v1/schools/", json=inactive_school)

        # 只查询活跃学校
        response = client.get("/api/v1/schools/?is_active=true")

        assert response.status_code == 200
        data = response.json()
        assert all(school["is_active"] for school in data["items"])

        # 按名称搜索
        response = client.get("/api/v1/schools/?search=活跃")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "活跃学校"

    def test_get_schools_with_sorting(self, client, sample_school_data):
        """测试带排序的学校查询。"""
        # 创建多个学校
        school_names = ["C学校", "A学校", "B学校"]
        for i, name in enumerate(school_names):
            school_data = sample_school_data.copy()
            school_data["code"] = f"CODE{i:03d}"
            school_data["name"] = name
            client.post("/api/v1/schools/", json=school_data)

        # 按名称升序排序
        response = client.get("/api/v1/schools/?sort=name:asc")

        assert response.status_code == 200
        data = response.json()
        names = [school["name"] for school in data["items"]]
        assert names == sorted(names)

        # 按名称降序排序
        response = client.get("/api/v1/schools/?sort=name:desc")

        assert response.status_code == 200
        data = response.json()
        names = [school["name"] for school in data["items"]]
        assert names == sorted(names, reverse=True)


class TestTeacherAPI:
    """教师API测试类。"""

    @pytest.fixture
    def client(self):
        """创建测试客户端。"""
        return TestClient(app)

    @pytest.fixture
    def sample_teacher_data(self):
        """示例教师数据。"""
        return {
            "first_name": "张",
            "last_name": "老师",
            "email": "zhang@school.edu",
            "phone": "13800138000",
            "department": "数学系",
            "title": "教授",
            "max_hours_per_week": 20,
            "is_active": True
        }

    def test_create_teacher_success(self, client, sample_teacher_data):
        """测试成功创建教师。"""
        response = client.post("/api/v1/teachers/", json=sample_teacher_data)

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == sample_teacher_data["first_name"]
        assert data["last_name"] == sample_teacher_data["last_name"]
        assert data["email"] == sample_teacher_data["email"]
        assert "id" in data

    def test_create_teacher_invalid_email(self, client, sample_teacher_data):
        """测试创建教师时使用无效邮箱。"""
        invalid_data = sample_teacher_data.copy()
        invalid_data["email"] = "invalid-email"

        response = client.post("/api/v1/teachers/", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_get_teachers_list(self, client, sample_teacher_data):
        """测试获取教师列表。"""
        # 创建几个教师
        for i in range(3):
            teacher_data = sample_teacher_data.copy()
            teacher_data["email"] = f"teacher{i}@school.edu"
            teacher_data["first_name"] = f"老师{i}"
            client.post("/api/v1/teachers/", json=teacher_data)

        response = client.get("/api/v1/teachers/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_get_teacher_by_id(self, client, sample_teacher_data):
        """测试根据ID获取教师。"""
        # 创建教师
        create_response = client.post("/api/v1/teachers/", json=sample_teacher_data)
        teacher_id = create_response.json()["id"]

        # 获取教师
        response = client.get(f"/api/v1/teachers/{teacher_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == teacher_id
        assert data["first_name"] == sample_teacher_data["first_name"]

    def test_update_teacher(self, client, sample_teacher_data):
        """测试更新教师信息。"""
        # 创建教师
        create_response = client.post("/api/v1/teachers/", json=sample_teacher_data)
        teacher_id = create_response.json()["id"]

        # 更新教师
        update_data = {
            "title": "副教授",
            "department": "物理系",
            "max_hours_per_week": 18
        }

        response = client.put(f"/api/v1/teachers/{teacher_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "副教授"
        assert data["department"] == "物理系"
        assert data["max_hours_per_week"] == 18

    def test_delete_teacher(self, client, sample_teacher_data):
        """测试删除教师。"""
        # 创建教师
        create_response = client.post("/api/v1/teachers/", json=sample_teacher_data)
        teacher_id = create_response.json()["id"]

        # 删除教师
        response = client.delete(f"/api/v1/teachers/{teacher_id}")

        assert response.status_code == 204

        # 验证教师已被删除
        get_response = client.get(f"/api/v1/teachers/{teacher_id}")
        assert get_response.status_code == 404


class TestHealthAPI:
    """健康检查API测试类。"""

    @pytest.fixture
    def client(self):
        """创建测试客户端。"""
        return TestClient(app)

    def test_health_check(self, client):
        """测试健康检查端点。"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

    def test_health_check_with_database(self, client):
        """测试包含数据库状态的健康检查。"""
        with patch('edusched.api.main.get_db') as mock_db:
            # 模拟数据库连接正常
            mock_session = Mock()
            mock_db.return_value.__enter__.return_value = mock_session
            mock_session.execute.return_value.scalar.return_value = 1

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "database" in data
            assert data["database"]["status"] == "healthy"

    def test_health_check_database_failure(self, client):
        """测试数据库连接失败时的健康检查。"""
        with patch('edusched.api.main.get_db') as mock_db:
            # 模拟数据库连接失败
            mock_db.side_effect = Exception("Database connection failed")

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert "database" in data
            assert data["database"]["status"] == "unhealthy"