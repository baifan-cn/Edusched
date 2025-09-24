#!/usr/bin/env python3
"""
调度引擎API测试脚本

用于测试调度引擎相关的所有API端点。
"""

import requests
import json
import uuid
import time
import sys
from typing import Dict, Any, Optional

class SchedulingAPITester:
    """调度API测试类"""

    def __init__(self, base_url: str = "http://localhost:8000", tenant_id: str = "demo-school"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.tenant_id = tenant_id
        self.headers = {
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }
        self.test_job_id = None
        self.test_timetable_id = str(uuid.uuid4())

    def test_health_check(self) -> bool:
        """测试健康检查"""
        print("🏥 测试系统健康检查...")

        try:
            response = requests.get(f"{self.base_url}/health")

            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ 系统健康状态: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_start_scheduling(self) -> bool:
        """测试启动调度任务"""
        print("🚀 测试启动调度任务...")

        data = {
            "timetable_id": self.test_timetable_id
        }

        try:
            response = requests.post(
                f"{self.api_url}/scheduling/start",
                headers=self.headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                self.test_job_id = result["job_id"]
                print(f"✅ 调度任务启动成功: {result['job_id']}")
                return True
            else:
                print(f"❌ 启动调度任务失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_list_jobs(self) -> bool:
        """测试获取任务列表"""
        print("📋 测试获取调度任务列表...")

        try:
            response = requests.get(
                f"{self.api_url}/scheduling/jobs",
                headers=self.headers
            )

            if response.status_code == 200:
                jobs = response.json()
                print(f"✅ 获取任务列表成功，共 {len(jobs)} 个任务")

                # 打印任务状态
                for job in jobs:
                    print(f"   - 任务 {job['id']}: {job['status']} ({job['progress']:.1%})")

                return True
            else:
                print(f"❌ 获取任务列表失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_list_jobs_by_status(self) -> bool:
        """测试按状态过滤任务"""
        print("🔍 测试按状态过滤任务...")

        try:
            response = requests.get(
                f"{self.api_url}/scheduling/jobs",
                headers=self.headers,
                params={"status_filter": "running"}
            )

            if response.status_code == 200:
                jobs = response.json()
                print(f"✅ 按状态过滤成功，运行中任务共 {len(jobs)} 个")
                return True
            else:
                print(f"❌ 按状态过滤失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_get_job(self) -> bool:
        """测试获取任务详情"""
        if not self.test_job_id:
            print("❌ 没有可用的任务ID，跳过测试")
            return False

        print(f"📄 测试获取任务详情 (ID: {self.test_job_id})...")

        try:
            response = requests.get(
                f"{self.api_url}/scheduling/jobs/{self.test_job_id}",
                headers=self.headers
            )

            if response.status_code == 200:
                job = response.json()
                print(f"✅ 获取任务详情成功:")
                print(f"   状态: {job['status']}")
                print(f"   进度: {job['progress']:.1%}")
                print(f"   开始时间: {job['started_at']}")
                print(f"   工作进程: {job['worker_id']}")
                return True
            else:
                print(f"❌ 获取任务详情失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_get_job_progress(self) -> bool:
        """测试获取任务进度"""
        if not self.test_job_id:
            print("❌ 没有可用的任务ID，跳过测试")
            return False

        print(f"📊 测试获取任务进度 (ID: {self.test_job_id})...")

        try:
            response = requests.get(
                f"{self.api_url}/scheduling/jobs/{self.test_job_id}/progress",
                headers=self.headers
            )

            if response.status_code == 200:
                progress = response.json()
                print(f"✅ 获取任务进度成功:")
                print(f"   状态: {progress['status']}")
                print(f"   进度: {progress['progress']:.1%}")
                print(f"   工作进程: {progress['worker_id']}")
                return True
            else:
                print(f"❌ 获取任务进度失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_cancel_job(self) -> bool:
        """测试取消任务"""
        if not self.test_job_id:
            print("❌ 没有可用的任务ID，跳过测试")
            return False

        print(f"🛑 测试取消任务 (ID: {self.test_job_id})...")

        try:
            response = requests.post(
                f"{self.api_url}/scheduling/jobs/{self.test_job_id}/cancel",
                headers=self.headers
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 取消任务成功: {result['message']}")
                return True
            else:
                print(f"❌ 取消任务失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_validate_constraints(self) -> bool:
        """测试约束验证"""
        print("✅ 测试约束验证...")

        data = {
            "timetable_id": self.test_timetable_id
        }

        try:
            response = requests.post(
                f"{self.api_url}/scheduling/validate",
                headers=self.headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 约束验证成功: {result['message']}")
                print(f"   验证结果: {'通过' if result['valid'] else '失败'}")
                print(f"   违反约束数: {len(result['violations'])}")
                return True
            else:
                print(f"❌ 约束验证失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_nonexistent_job(self) -> bool:
        """测试不存在的任务"""
        print("👻 测试不存在的任务...")

        fake_id = str(uuid.uuid4())

        try:
            response = requests.get(
                f"{self.api_url}/scheduling/jobs/{fake_id}",
                headers=self.headers
            )

            if response.status_code == 404:
                print("✅ 不存在任务的错误处理正确")
                return True
            else:
                print(f"❌ 错误处理不正确: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_job_lifecycle(self) -> bool:
        """测试完整的任务生命周期"""
        print("🔄 测试任务生命周期...")

        # 创建新任务
        timetable_id = str(uuid.uuid4())

        try:
            # 启动任务
            response = requests.post(
                f"{self.api_url}/scheduling/start",
                headers=self.headers,
                json={"timetable_id": timetable_id}
            )

            if response.status_code != 200:
                print(f"❌ 启动任务失败: {response.status_code} - {response.text}")
                return False

            job_data = response.json()
            job_id = job_data["job_id"]

            # 等待任务开始
            time.sleep(2)

            # 检查进度
            progress_response = requests.get(
                f"{self.api_url}/scheduling/jobs/{job_id}/progress",
                headers=self.headers
            )

            if progress_response.status_code == 200:
                progress = progress_response.json()
                print(f"✅ 任务进度: {progress['status']} ({progress['progress']:.1%})")

            # 取消任务
            cancel_response = requests.post(
                f"{self.api_url}/scheduling/jobs/{job_id}/cancel",
                headers=self.headers
            )

            if cancel_response.status_code == 200:
                print("✅ 任务生命周期测试完成")
                return True
            else:
                print(f"❌ 取消任务失败: {cancel_response.status_code} - {cancel_response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_concurrent_jobs(self) -> bool:
        """测试并发任务"""
        print("⚡ 测试并发任务...")

        job_ids = []

        try:
            # 启动多个并发任务
            for i in range(3):
                timetable_id = str(uuid.uuid4())
                response = requests.post(
                    f"{self.api_url}/scheduling/start",
                    headers=self.headers,
                    json={"timetable_id": timetable_id}
                )

                if response.status_code == 200:
                    job_data = response.json()
                    job_ids.append(job_data["job_id"])
                    print(f"✅ 启动任务 {i+1}: {job_data['job_id']}")
                else:
                    print(f"❌ 启动任务 {i+1} 失败")

            # 等待一下
            time.sleep(2)

            # 检查任务列表
            response = requests.get(
                f"{self.api_url}/scheduling/jobs",
                headers=self.headers
            )

            if response.status_code == 200:
                jobs = response.json()
                active_jobs = [job for job in jobs if job["status"] in ["running", "draft"]]
                print(f"✅ 当前活跃任务数: {len(active_jobs)}")

            # 取消所有任务
            for job_id in job_ids:
                requests.post(
                    f"{self.api_url}/scheduling/jobs/{job_id}/cancel",
                    headers=self.headers
                )

            print("✅ 并发任务测试完成")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始调度引擎API测试...")
        print("=" * 50)

        tests = [
            self.test_health_check,
            self.test_start_scheduling,
            self.test_list_jobs,
            self.test_list_jobs_by_status,
            self.test_get_job,
            self.test_get_job_progress,
            self.test_validate_constraints,
            self.test_job_lifecycle,
            self.test_concurrent_jobs,
            self.test_nonexistent_job,
            self.test_cancel_job
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

    parser = argparse.ArgumentParser(description="调度引擎API测试")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--tenant", default="demo-school", help="租户ID")

    args = parser.parse_args()

    tester = SchedulingAPITester(base_url=args.url, tenant_id=args.tenant)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()