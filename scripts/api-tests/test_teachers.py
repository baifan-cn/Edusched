#!/usr/bin/env python3
"""
教师管理API测试脚本

用于测试教师管理相关的所有API端点。
"""

import requests
import json
import uuid
import sys
from typing import Dict, Any, Optional

class TeachersAPITester:
    """教师API测试类"""

    def __init__(self, base_url: str = "http://localhost:8000", tenant_id: str = "demo-school"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.tenant_id = tenant_id
        self.headers = {
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }
        self.test_teacher_id = None

    def test_create_teacher(self) -> bool:
        """测试创建教师"""
        print("👨‍🏫 测试创建教师...")

        teacher_data = {
            "employee_id": "T001",
            "name": "张老师",
            "email": "zhang.teacher@demo.edu.cn",
            "phone": "13800138000",
            "department": "数学系",
            "title": "教授",
            "specialization": "高等数学",
            "max_hours_per_week": 20,
            "preferred_days": ["monday", "wednesday", "friday"],
            "preferred_time_slots": ["morning", "afternoon"],
            "notes": "教学经验丰富，擅长高等数学教学"
        }

        try:
            response = requests.post(
                f"{self.api_url}/teachers/",
                headers=self.headers,
                json=teacher_data
            )

            if response.status_code == 201:
                result = response.json()
                self.test_teacher_id = result["id"]
                print(f"✅ 创建教师成功: {result['name']} (ID: {result['id']})")
                return True
            else:
                print(f"❌ 创建教师失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_list_teachers(self) -> bool:
        """测试获取教师列表"""
        print("📋 测试获取教师列表...")

        try:
            response = requests.get(
                f"{self.api_url}/teachers/",
                headers=self.headers
            )

            if response.status_code == 200:
                teachers = response.json()
                print(f"✅ 获取教师列表成功，共 {len(teachers)} 位教师")

                # 打印前3位教师
                for teacher in teachers[:3]:
                    print(f"   - {teacher['name']} ({teacher['employee_id']}) - {teacher['department']}")

                return True
            else:
                print(f"❌ 获取教师列表失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_list_teachers_by_department(self) -> bool:
        """测试按部门过滤教师"""
        print("🏛️ 测试按部门过滤教师...")

        try:
            response = requests.get(
                f"{self.api_url}/teachers/",
                headers=self.headers,
                params={"department": "数学系"}
            )

            if response.status_code == 200:
                teachers = response.json()
                print(f"✅ 按部门过滤成功，数学系共 {len(teachers)} 位教师")
                return True
            else:
                print(f"❌ 按部门过滤失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_get_teacher(self) -> bool:
        """测试获取教师详情"""
        if not self.test_teacher_id:
            print("❌ 没有可用的教师ID，跳过测试")
            return False

        print(f"🔍 测试获取教师详情 (ID: {self.test_teacher_id})...")

        try:
            response = requests.get(
                f"{self.api_url}/teachers/{self.test_teacher_id}",
                headers=self.headers
            )

            if response.status_code == 200:
                teacher = response.json()
                print(f"✅ 获取教师详情成功: {teacher['name']} ({teacher['title']})")
                print(f"   部门: {teacher['department']}")
                print(f"   专业: {teacher['specialization']}")
                print(f"   最大课时: {teacher['max_hours_per_week']}/周")
                return True
            else:
                print(f"❌ 获取教师详情失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_update_teacher(self) -> bool:
        """测试更新教师"""
        if not self.test_teacher_id:
            print("❌ 没有可用的教师ID，跳过测试")
            return False

        print(f"✏️ 测试更新教师 (ID: {self.test_teacher_id})...")

        update_data = {
            "name": "张老师（更新）",
            "title": "副教授",
            "department": "应用数学系",
            "preferred_days": ["tuesday", "thursday"],
            "max_hours_per_week": 18
        }

        try:
            response = requests.put(
                f"{self.api_url}/teachers/{self.test_teacher_id}",
                headers=self.headers,
                json=update_data
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 更新教师成功: {result['name']} ({result['title']})")
                return True
            else:
                print(f"❌ 更新教师失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_delete_teacher(self) -> bool:
        """测试删除教师"""
        if not self.test_teacher_id:
            print("❌ 没有可用的教师ID，跳过测试")
            return False

        print(f"🗑️ 测试删除教师 (ID: {self.test_teacher_id})...")

        try:
            response = requests.delete(
                f"{self.api_url}/teachers/{self.test_teacher_id}",
                headers=self.headers
            )

            if response.status_code == 204:
                print(f"✅ 删除教师成功")
                self.test_teacher_id = None
                return True
            else:
                print(f"❌ 删除教师失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_duplicate_employee_id(self) -> bool:
        """测试重复工号处理"""
        print("🔄 测试重复工号处理...")

        # 创建第一个教师
        teacher_data = {
            "employee_id": "T002",
            "name": "李老师",
            "department": "物理系"
        }

        try:
            response = requests.post(
                f"{self.api_url}/teachers/",
                headers=self.headers,
                json=teacher_data
            )

            if response.status_code != 201:
                print(f"❌ 创建第一个教师失败: {response.status_code} - {response.text}")
                return False

            # 尝试创建相同工号的教师
            response2 = requests.post(
                f"{self.api_url}/teachers/",
                headers=self.headers,
                json=teacher_data
            )

            if response2.status_code == 400:
                print("✅ 重复工号检测正确")
                # 清理测试数据
                result = response.json()
                requests.delete(
                    f"{self.api_url}/teachers/{result['id']}",
                    headers=self.headers
                )
                return True
            else:
                print(f"❌ 重复工号检测失败: {response2.status_code} - {response2.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_pagination(self) -> bool:
        """测试分页功能"""
        print("📄 测试分页功能...")

        try:
            # 获取第一页
            response1 = requests.get(
                f"{self.api_url}/teachers/",
                headers=self.headers,
                params={"skip": 0, "limit": 5}
            )

            if response1.status_code != 200:
                print(f"❌ 分页请求失败: {response1.status_code} - {response1.text}")
                return False

            page1 = response1.json()
            print(f"✅ 第一页获取成功，共 {len(page1)} 位教师")

            # 获取第二页
            response2 = requests.get(
                f"{self.api_url}/teachers/",
                headers=self.headers,
                params={"skip": 5, "limit": 5}
            )

            if response2.status_code == 200:
                page2 = response2.json()
                print(f"✅ 第二页获取成功，共 {len(page2)} 位教师")
                return True
            else:
                print(f"❌ 第二页获取失败: {response2.status_code} - {response2.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始教师管理API测试...")
        print("=" * 50)

        tests = [
            self.test_create_teacher,
            self.test_list_teachers,
            self.test_list_teachers_by_department,
            self.test_get_teacher,
            self.test_update_teacher,
            self.test_pagination,
            self.test_duplicate_employee_id,
            self.test_delete_teacher
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                failed += 1

            print("-" * 30)

        print("=" * 50)
        print(f"📊 测试结果: {passed} 通过, {failed} 失败")

        if failed == 0:
            print("🎉 所有测试通过!")
            return True
        else:
            print("⚠️ 存在失败的测试")
            return False

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="教师管理API测试")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--tenant", default="demo-school", help="租户ID")

    args = parser.parse_args()

    tester = TeachersAPITester(base_url=args.url, tenant_id=args.tenant)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()