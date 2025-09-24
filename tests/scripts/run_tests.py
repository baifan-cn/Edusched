#!/usr/bin/env python3
"""
测试运行脚本
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """测试运行器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / "reports"
        self.coverage_dir = self.reports_dir / "coverage"
        self.ensure_directories()

    def ensure_directories(self):
        """确保目录存在"""
        self.reports_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)

    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """运行命令"""
        print(f"运行命令: {' '.join(command)}")
        result = subprocess.run(
            command,
            cwd=cwd or self.project_root,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result

    def run_unit_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行单元测试"""
        print("=" * 60)
        print("运行单元测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "tests/unit/"]

        if verbose:
            command.append("-v")

        if coverage:
            command.extend([
                "--cov=src/edusched",
                "--cov-report=term-missing",
                "--cov-report=html:reports/coverage/html",
                "--cov-report=xml:reports/coverage/coverage.xml"
            ])

        result = self.run_command(command)
        return result.returncode == 0

    def run_integration_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行集成测试"""
        print("=" * 60)
        print("运行集成测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "tests/integration/"]

        if verbose:
            command.append("-v")

        if coverage:
            command.extend([
                "--cov=src/edusched",
                "--cov-report=term-missing",
                "--cov-report=html:reports/coverage/html",
                "--cov-report=xml:reports/coverage/coverage.xml"
            ])

        result = self.run_command(command)
        return result.returncode == 0

    def run_e2e_tests(self, verbose: bool = False) -> bool:
        """运行E2E测试"""
        print("=" * 60)
        print("运行E2E测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "tests/e2e/"]

        if verbose:
            command.append("-v")

        result = self.run_command(command)
        return result.returncode == 0

    def run_performance_tests(self, verbose: bool = False) -> bool:
        """运行性能测试"""
        print("=" * 60)
        print("运行性能测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "tests/performance/"]

        if verbose:
            command.append("-v")

        result = self.run_command(command)
        return result.returncode == 0

    def run_api_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行API测试"""
        print("=" * 60)
        print("运行API测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "-m", "api"]

        if verbose:
            command.append("-v")

        if coverage:
            command.extend([
                "--cov=src/edusched",
                "--cov-report=term-missing",
                "--cov-report=html:reports/coverage/html",
                "--cov-report=xml:reports/coverage/coverage.xml"
            ])

        result = self.run_command(command)
        return result.returncode == 0

    def run_database_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行数据库测试"""
        print("=" * 60)
        print("运行数据库测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "-m", "database"]

        if verbose:
            command.append("-v")

        if coverage:
            command.extend([
                "--cov=src/edusched",
                "--cov-report=term-missing",
                "--cov-report=html:reports/coverage/html",
                "--cov-report=xml:reports/coverage/coverage.xml"
            ])

        result = self.run_command(command)
        return result.returncode == 0

    def run_tenant_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行多租户测试"""
        print("=" * 60)
        print("运行多租户测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "-m", "tenant"]

        if verbose:
            command.append("-v")

        if coverage:
            command.extend([
                "--cov=src/edusched",
                "--cov-report=term-missing",
                "--cov-report=html:reports/coverage/html",
                "--cov-report=xml:reports/coverage/coverage.xml"
            ])

        result = self.run_command(command)
        return result.returncode == 0

    def run_scheduling_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行调度测试"""
        print("=" * 60)
        print("运行调度测试...")
        print("=" * 60)

        command = ["python", "-m", "pytest", "-m", "scheduling"]

        if verbose:
            command.append("-v")

        if coverage:
            command.extend([
                "--cov=src/edusched",
                "--cov-report=term-missing",
                "--cov-report=html:reports/coverage/html",
                "--cov-report=xml:reports/coverage/coverage.xml"
            ])

        result = self.run_command(command)
        return result.returncode == 0

    def run_all_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行所有测试"""
        print("=" * 60)
        print("运行所有测试...")
        print("=" * 60)

        success = True

        # 运行单元测试
        if not self.run_unit_tests(verbose, coverage):
            success = False

        # 运行集成测试
        if not self.run_integration_tests(verbose, coverage):
            success = False

        # 运行E2E测试
        if not self.run_e2e_tests(verbose):
            success = False

        # 运行性能测试
        if not self.run_performance_tests(verbose):
            success = False

        return success

    def run_frontend_tests(self, verbose: bool = False, coverage: bool = True) -> bool:
        """运行前端测试"""
        print("=" * 60)
        print("运行前端测试...")
        print("=" * 60)

        frontend_dir = self.project_root / "frontend"

        command = ["npm", "run", "test"]

        if verbose:
            command.append("--")
            command.append("--verbose")

        if coverage:
            command.append("--coverage")

        result = self.run_command(command, cwd=frontend_dir)
        return result.returncode == 0

    def generate_coverage_report(self) -> bool:
        """生成覆盖率报告"""
        print("=" * 60)
        print("生成覆盖率报告...")
        print("=" * 60)

        command = ["python", "-m", "coverage", "report"]
        result = self.run_command(command)
        return result.returncode == 0

    def clean_test_artifacts(self):
        """清理测试产物"""
        print("=" * 60)
        print("清理测试产物...")
        print("=" * 60)

        # 清理pytest缓存
        cache_dirs = [
            self.project_root / ".pytest_cache",
            self.project_root / "__pycache__",
            self.project_root / ".coverage",
            self.project_root / "htmlcov"
        ]

        for cache_dir in cache_dirs:
            if cache_dir.exists():
                print(f"删除: {cache_dir}")
                import shutil
                shutil.rmtree(cache_dir)

        # 清理报告目录
        if self.reports_dir.exists():
            print(f"清空: {self.reports_dir}")
            import shutil
            shutil.rmtree(self.reports_dir)
            self.ensure_directories()

        print("清理完成")

    def lint_code(self) -> bool:
        """代码检查"""
        print("=" * 60)
        print("运行代码检查...")
        print("=" * 60)

        # 运行black
        print("运行 black...")
        result = self.run_command(["python", "-m", "black", "--check", "src/"])
        if result.returncode != 0:
            print("代码格式不符合black规范")
            return False

        # 运行isort
        print("运行 isort...")
        result = self.run_command(["python", "-m", "isort", "--check-only", "src/"])
        if result.returncode != 0:
            print("导入排序不符合isort规范")
            return False

        # 运行flake8
        print("运行 flake8...")
        result = self.run_command(["python", "-m", "flake8", "src/"])
        if result.returncode != 0:
            print("代码存在flake8问题")
            return False

        # 运行mypy
        print("运行 mypy...")
        result = self.run_command(["python", "-m", "mypy", "src/"])
        if result.returncode != 0:
            print("类型检查存在问题")
            return False

        print("代码检查通过")
        return True

    def format_code(self) -> bool:
        """格式化代码"""
        print("=" * 60)
        print("格式化代码...")
        print("=" * 60)

        # 运行black
        print("运行 black...")
        result = self.run_command(["python", "-m", "black", "src/"])

        # 运行isort
        print("运行 isort...")
        result = self.run_command(["python", "-m", "isort", "src/"])

        print("代码格式化完成")
        return True

    def show_help(self):
        """显示帮助信息"""
        help_text = """
Edusched 测试运行器

用法:
    python tests/scripts/run_tests.py [选项]

选项:
    --unit              运行单元测试
    --integration       运行集成测试
    --e2e               运行E2E测试
    --performance       运行性能测试
    --api               运行API测试
    --database          运行数据库测试
    --tenant            运行多租户测试
    --scheduling        运行调度测试
    --frontend          运行前端测试
    --all               运行所有测试 (默认)
    --coverage          生成覆盖率报告
    --clean             清理测试产物
    --lint              运行代码检查
    --format            格式化代码
    --verbose           详细输出
    --help              显示帮助信息

示例:
    python tests/scripts/run_tests.py --unit --coverage
    python tests/scripts/run_tests.py --all --verbose
    python tests/scripts/run_tests.py --clean --all
        """
        print(help_text)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Edusched 测试运行器")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--e2e", action="store_true", help="运行E2E测试")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--api", action="store_true", help="运行API测试")
    parser.add_argument("--database", action="store_true", help="运行数据库测试")
    parser.add_argument("--tenant", action="store_true", help="运行多租户测试")
    parser.add_argument("--scheduling", action="store_true", help="运行调度测试")
    parser.add_argument("--frontend", action="store_true", help="运行前端测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--clean", action="store_true", help="清理测试产物")
    parser.add_argument("--lint", action="store_true", help="运行代码检查")
    parser.add_argument("--format", action="store_true", help="格式化代码")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--help", action="store_true", help="显示帮助信息")

    args = parser.parse_args()

    if args.help:
        runner = TestRunner(Path(__file__).parent.parent.parent)
        runner.show_help()
        return

    project_root = Path(__file__).parent.parent.parent
    runner = TestRunner(project_root)

    # 清理测试产物
    if args.clean:
        runner.clean_test_artifacts()

    # 格式化代码
    if args.format:
        runner.format_code()

    # 代码检查
    if args.lint:
        if not runner.lint_code():
            sys.exit(1)

    # 运行测试
    success = True

    if args.unit:
        if not runner.run_unit_tests(args.verbose, args.coverage):
            success = False

    if args.integration:
        if not runner.run_integration_tests(args.verbose, args.coverage):
            success = False

    if args.e2e:
        if not runner.run_e2e_tests(args.verbose):
            success = False

    if args.performance:
        if not runner.run_performance_tests(args.verbose):
            success = False

    if args.api:
        if not runner.run_api_tests(args.verbose, args.coverage):
            success = False

    if args.database:
        if not runner.run_database_tests(args.verbose, args.coverage):
            success = False

    if args.tenant:
        if not runner.run_tenant_tests(args.verbose, args.coverage):
            success = False

    if args.scheduling:
        if not runner.run_scheduling_tests(args.verbose, args.coverage):
            success = False

    if args.frontend:
        if not runner.run_frontend_tests(args.verbose, args.coverage):
            success = False

    if args.all or not any([
        args.unit, args.integration, args.e2e, args.performance,
        args.api, args.database, args.tenant, args.scheduling, args.frontend
    ]):
        if not runner.run_all_tests(args.verbose, args.coverage):
            success = False

    # 生成覆盖率报告
    if args.coverage:
        runner.generate_coverage_report()

    # 输出结果
    print("=" * 60)
    if success:
        print("所有测试通过! ✓")
        sys.exit(0)
    else:
        print("测试失败! ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()