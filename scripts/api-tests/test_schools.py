#!/usr/bin/env python3
"""
学校管理API测试脚本

用于测试学校管理相关的所有API端点。
"""

import requests
import json
import uuid
import sys
from typing import Dict, Any, Optional

class SchoolsAPITester:
    """学校API测试类"""

    def __init__(self, base_url: str = "http://localhost:8000", tenant_id: str = "demo-school"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.tenant_id = tenant_id
        self.headers = {
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }
        self.test_school_id = None

    def test_create_school(self) -> bool:
        """测试创建学校"""
        print("🏫 测试创建学校...")

        school_data = {
            "name": "测试学校",
            "code": "TEST001",
            "address": "北京市海淀区测试路1号",
            "phone": "010-12345678",
            "email": "test@school.edu.cn",
            "website": "https://test.school.edu.cn",
            "academic_year": "2024-2025",
            "semester": "秋季学期"
        }

        try:
            response = requests.post(
                f"{self.api_url}/schools/",
                headers=self.headers,
                json=school_data
            )

            if response.status_code == 201:
                result = response.json()
                self.test_school_id = result["id"]
                print(f"✅ 创建学校成功: {result['name']} (ID: {result['id']})")
                return True
            else:
                print(f"❌ 创建学校失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_list_schools(self) -> bool:
        """测试获取学校列表"""
        print("📋 测试获取学校列表...")

        try:
            response = requests.get(
                f"{self.api_url}/schools/",
                headers=self.headers
            )

            if response.status_code == 200:
                schools = response.json()
                print(f"✅ 获取学校列表成功，共 {len(schools)} 所学校")

                # 打印前3所学校
                for school in schools[:3]:
                    print(f"   - {school['name']} ({school['code']})")

                return True
            else:
                print(f"❌ 获取学校列表失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_get_school(self) -> bool:
        """测试获取学校详情"""
        if not self.test_school_id:
            print("❌ 没有可用的学校ID，跳过测试")
            return False

        print(f"🔍 测试获取学校详情 (ID: {self.test_school_id})...")

        try:
            response = requests.get(
                f"{self.api_url}/schools/{self.test_school_id}",
                headers=self.headers
            )

            if response.status_code == 200:
                school = response.json()
                print(f"✅ 获取学校详情成功: {school['name']}")
                return True
            else:
                print(f"❌ 获取学校详情失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_update_school(self) -> bool:
        """测试更新学校"""
        if not self.test_school_id:
            print("❌ 没有可用的学校ID，跳过测试")
            return False

        print(f"✏️ 测试更新学校 (ID: {self.test_school_id})...")

        update_data = {
            "name": "测试学校（已更新）",
            "phone": "010-87654321",
            "semester": "春季学期"
        }

        try:
            response = requests.put(
                f"{self.api_url}/schools/{self.test_school_id}",
                headers=self.headers,
                json=update_data
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 更新学校成功: {result['name']}")
                return True
            else:
                print(f"❌ 更新学校失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_delete_school(self) -> bool:
        """测试删除学校"""
        if not self.test_school_id:
            print("❌ 没有可用的学校ID，跳过测试")
            return False

        print(f"🗑️ 测试删除学校 (ID: {self.test_school_id})...")

        try:
            response = requests.delete(
                f"{self.api_url}/schools/{self.test_school_id}",
                headers=self.headers
            )

            if response.status_code == 204:
                print(f"✅ 删除学校成功")
                self.test_school_id = None
                return True
            else:
                print(f"❌ 删除学校失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_get_campuses(self) -> bool:
        """测试获取学校校区"""
        if not self.test_school_id:
            print("❌ 没有可用的学校ID，跳过测试")
            return False

        print(f"🏢 测试获取学校校区 (ID: {self.test_school_id})...")

        try:
            response = requests.get(
                f"{self.api_url}/schools/{self.test_school_id}/campuses",
                headers=self.headers
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取校区信息成功")
                return True
            else:
                print(f"❌ 获取校区信息失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_error_handling(self) -> bool:
        """测试错误处理"""
        print("🚨 测试错误处理...")

        # 测试获取不存在的学校
        fake_id = str(uuid.uuid4())

        try:
            response = requests.get(
                f"{self.api_url}/schools/{fake_id}",
                headers=self.headers
            )

            if response.status_code == 404:
                print("✅ 不存在学校的错误处理正确")
                return True
            else:
                print(f"❌ 错误处理不正确: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始学校管理API测试...")
        print("=" * 50)

        tests = [
            self.test_create_school,
            self.test_list_schools,
            self.test_get_school,
            self.test_update_school,
            self.test_get_campuses,
            self.test_error_handling,
            self.test_delete_school
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

    parser = argparse.ArgumentParser(description="学校管理API测试")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--tenant", default="demo-school", help="租户ID")

    args = parser.parse_args()

    tester = SchoolsAPITester(base_url=args.url, tenant_id=args.tenant)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()