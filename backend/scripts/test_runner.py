#!/usr/bin/env python3
"""
Comprehensive test runner for brainsait-store backend.

This script provides various testing options:
- Run all tests
- Run tests by category (unit, integration, api, etc.)
- Run coverage analysis
- Run performance tests
- Generate test reports
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class TestRunner:
    """Comprehensive test runner for the backend application"""

    def __init__(self):
        self.backend_dir = backend_dir
        self.coverage_threshold = 80

    def run_command(self, cmd: List[str], description: str) -> bool:
        """Run a command and return success status"""
        print(f"\n🔄 {description}")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed")
            if e.stdout:
                print("STDOUT:", e.stdout)
            if e.stderr:
                print("STDERR:", e.stderr)
            return False
        except Exception as e:
            print(f"❌ {description} failed with error: {e}")
            return False

    def setup_test_environment(self) -> bool:
        """Set up the test environment"""
        print("🏗️  Setting up test environment...")
        
        # Ensure test database directory exists
        test_db_dir = self.backend_dir / "test_data"
        test_db_dir.mkdir(exist_ok=True)
        
        # Set environment variables
        os.environ.update({
            "TESTING": "true",
            "DATABASE_URL": "sqlite+aiosqlite:///./test.db",
            "SECRET_KEY": "test-secret-key-for-testing",
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "WARNING"
        })
        
        return True

    def run_unit_tests(self) -> bool:
        """Run unit tests only"""
        cmd = [
            "python", "-m", "pytest",
            "-m", "unit",
            "--tb=short",
            "-v"
        ]
        return self.run_command(cmd, "Running unit tests")

    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        cmd = [
            "python", "-m", "pytest", 
            "-m", "integration",
            "--tb=short",
            "-v"
        ]
        return self.run_command(cmd, "Running integration tests")

    def run_api_tests(self) -> bool:
        """Run API tests"""
        cmd = [
            "python", "-m", "pytest",
            "-m", "api", 
            "--tb=short",
            "-v"
        ]
        return self.run_command(cmd, "Running API tests")

    def run_database_tests(self) -> bool:
        """Run database-related tests"""
        cmd = [
            "python", "-m", "pytest",
            "-m", "db",
            "--tb=short", 
            "-v"
        ]
        return self.run_command(cmd, "Running database tests")

    def run_all_tests(self, fast: bool = False) -> bool:
        """Run all tests with coverage"""
        cmd = [
            "python", "-m", "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov", 
            "--cov-report=xml:coverage.xml",
            f"--cov-fail-under={self.coverage_threshold}",
            "--tb=short"
        ]
        
        if fast:
            cmd.extend(["-x", "--ff"])  # Stop on first failure, run failures first
        else:
            cmd.extend(["-v", "--durations=10"])  # Verbose with timing info
            
        return self.run_command(cmd, "Running all tests with coverage")

    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        cmd = [
            "python", "-m", "pytest",
            "-m", "performance",
            "--tb=short",
            "-v"
        ]
        return self.run_command(cmd, "Running performance tests")

    def run_security_tests(self) -> bool:
        """Run security tests"""
        cmd = [
            "python", "-m", "pytest", 
            "-m", "security",
            "--tb=short",
            "-v"
        ]
        return self.run_command(cmd, "Running security tests")

    def run_slow_tests(self) -> bool:
        """Run slow/comprehensive tests"""
        cmd = [
            "python", "-m", "pytest",
            "-m", "slow",
            "--tb=short",
            "-v"
        ]
        return self.run_command(cmd, "Running slow tests")

    def run_specific_test_file(self, test_file: str) -> bool:
        """Run tests from a specific file"""
        cmd = [
            "python", "-m", "pytest",
            test_file,
            "--tb=short",
            "-v"
        ]
        return self.run_command(cmd, f"Running tests from {test_file}")

    def run_coverage_report(self) -> bool:
        """Generate comprehensive coverage report"""
        cmd = [
            "python", "-m", "pytest",
            "--cov=app",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=term-missing",
            "--quiet"
        ]
        return self.run_command(cmd, "Generating coverage report")

    def check_code_quality(self) -> bool:
        """Run code quality checks"""
        success = True
        
        # Run flake8 for style checking
        if not self.run_command(
            ["python", "-m", "flake8", "app", "tests"],
            "Running flake8 style checks"
        ):
            success = False
            
        # Run mypy for type checking
        if not self.run_command(
            ["python", "-m", "mypy", "app"],
            "Running mypy type checks"
        ):
            success = False
            
        # Run black for code formatting check
        if not self.run_command(
            ["python", "-m", "black", "--check", "app", "tests"],
            "Running black format checks"
        ):
            success = False
            
        return success

    def run_comprehensive_test_suite(self) -> bool:
        """Run comprehensive test suite with all categories"""
        print("🚀 Running comprehensive test suite...")
        
        test_categories = [
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("API Tests", self.run_api_tests),
            ("Database Tests", self.run_database_tests),
            ("Security Tests", self.run_security_tests),
        ]
        
        results = []
        for category, test_func in test_categories:
            print(f"\n{'='*50}")
            print(f"Running {category}")
            print('='*50)
            
            success = test_func()
            results.append((category, success))
        
        # Generate final coverage report
        print(f"\n{'='*50}")
        print("Generating Final Coverage Report")
        print('='*50)
        coverage_success = self.run_coverage_report()
        results.append(("Coverage Report", coverage_success))
        
        # Print summary
        self.print_test_summary(results)
        
        return all(success for _, success in results)

    def print_test_summary(self, results: List[tuple]) -> None:
        """Print a summary of test results"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        
        for category, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{category:<30} {status}")
        
        total_passed = sum(1 for _, success in results if success)
        total_tests = len(results)
        
        print(f"\n{total_passed}/{total_tests} test categories passed")
        
        if total_passed == total_tests:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Please check the output above.")

    def clean_test_artifacts(self) -> bool:
        """Clean up test artifacts"""
        artifacts_to_clean = [
            "test.db",
            "test.db-shm", 
            "test.db-wal",
            ".coverage",
            "htmlcov",
            ".pytest_cache",
            "__pycache__"
        ]
        
        print("🧹 Cleaning test artifacts...")
        
        for artifact in artifacts_to_clean:
            artifact_path = self.backend_dir / artifact
            if artifact_path.exists():
                if artifact_path.is_dir():
                    subprocess.run(["rm", "-rf", str(artifact_path)])
                else:
                    artifact_path.unlink()
                print(f"  Removed {artifact}")
        
        return True


def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for brainsait-store backend"
    )
    
    parser.add_argument(
        "--category", 
        choices=["unit", "integration", "api", "db", "performance", "security", "slow", "all"],
        default="all",
        help="Category of tests to run"
    )
    
    parser.add_argument(
        "--file", 
        type=str,
        help="Run tests from specific file"
    )
    
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report only"
    )
    
    parser.add_argument(
        "--quality", 
        action="store_true", 
        help="Run code quality checks"
    )
    
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run comprehensive test suite with all categories"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run tests in fast mode (stop on first failure)"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true", 
        help="Clean test artifacts"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner()
    
    # Setup test environment
    if not runner.setup_test_environment():
        print("❌ Failed to setup test environment")
        sys.exit(1)
    
    success = True
    
    # Handle specific operations
    if args.clean:
        success = runner.clean_test_artifacts()
    elif args.coverage:
        success = runner.run_coverage_report()
    elif args.quality:
        success = runner.check_code_quality()
    elif args.comprehensive:
        success = runner.run_comprehensive_test_suite()
    elif args.file:
        success = runner.run_specific_test_file(args.file)
    else:
        # Run tests by category
        category_runners = {
            "unit": runner.run_unit_tests,
            "integration": runner.run_integration_tests,
            "api": runner.run_api_tests,
            "db": runner.run_database_tests,
            "performance": runner.run_performance_tests,
            "security": runner.run_security_tests,
            "slow": runner.run_slow_tests,
            "all": lambda: runner.run_all_tests(args.fast)
        }
        
        runner_func = category_runners.get(args.category)
        if runner_func:
            success = runner_func()
        else:
            print(f"❌ Unknown category: {args.category}")
            success = False
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()