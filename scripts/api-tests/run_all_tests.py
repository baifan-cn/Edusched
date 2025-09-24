#!/usr/bin/env python3
"""
API测试总脚本

运行所有API模块的测试。
"""

import subprocess
import sys
import time
from pathlib import Path

def run_test(script_path: str, name: str) -> bool:
    """运行单个测试脚本"""
    print(f"\n🚀 运行 {name} 测试...")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        print(result.stdout)

        if result.stderr:
            print("错误信息:")
            print(result.stderr)

        success = result.returncode == 0
        if success:
            print(f"✅ {name} 测试通过")
        else:
            print(f"❌ {name} 测试失败")

        return success

    except subprocess.TimeoutExpired:
        print(f"❌ {name} 测试超时")
        return False
    except Exception as e:
        print(f"❌ {name} 测试异常: {e}")
        return False

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="运行所有API测试")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--tenant", default="demo-school", help="租户ID")

    args = parser.parse_args()

    # 获取脚本目录
    script_dir = Path(__file__).parent

    # 定义测试脚本
    test_scripts = [
        ("test_schools.py", "学校管理"),
        ("test_teachers.py", "教师管理"),
        ("test_scheduling.py", "调度引擎")
    ]

    # 检查API服务是否可用
    print("🔍 检查API服务可用性...")
    try:
        import requests
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API服务状态异常: {response.status_code}")
            sys.exit(1)
        print("✅ API服务正常运行")
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        print("请确保API服务正在运行并且可以访问")
        sys.exit(1)

    # 运行所有测试
    print("\n🎯 开始运行所有API测试...")
    print("=" * 60)

    passed = 0
    failed = 0

    for script_name, display_name in test_scripts:
        script_path = script_dir / script_name

        if not script_path.exists():
            print(f"❌ 测试脚本不存在: {script_path}")
            failed += 1
            continue

        if run_test(str(script_path), display_name):
            passed += 1
        else:
            failed += 1

        print("-" * 60)

    # 输出总结
    print("\n📊 测试总结")
    print("=" * 60)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()