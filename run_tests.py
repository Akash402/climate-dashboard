#!/usr/bin/env python3
"""
Test runner script for Climate Dashboard.

This script provides an easy way to run all tests with different configurations.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ Command failed with return code {result.returncode}")
        return False
    else:
        print("✅ Command completed successfully")
        return True


def main():
    """Main test runner function."""
    print("🧪 Climate Dashboard Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("build.py").exists():
        print("❌ Error: Please run this script from the climate-dashboard root directory")
        sys.exit(1)
    
    # Test commands
    commands = [
        (["python", "-m", "pytest", "tests/", "-v"], "All tests with verbose output"),
        (["python", "-m", "pytest", "tests/test_utils.py", "-v"], "Utils module tests only"),
        (["python", "-m", "pytest", "tests/test_data_fetchers.py", "-v"], "Data fetchers tests only"),
        (["python", "-m", "pytest", "tests/test_html_builder.py", "-v"], "HTML builder tests only"),
        (["python", "-m", "pytest", "tests/test_main.py", "-v"], "Main integration tests only"),
        (["python", "-m", "pytest", "tests/ui/", "-v"], "UI tests only"),
        (["python", "-m", "pytest", "tests/ui/test_dashboard_ui.py", "-v"], "Dashboard UI tests only"),
        (["python", "-m", "pytest", "tests/ui/test_animations.py", "-v"], "Animation tests only"),
        (["python", "-m", "pytest", "tests/ui/test_performance.py", "-v"], "Performance tests only"),
        (["python", "-m", "pytest", "tests/", "--cov=.", "--cov-report=html"], "All tests with coverage report"),
        (["python", "-m", "pytest", "tests/", "-k", "not slow", "-v"], "Fast tests only (excluding slow tests)"),
        (["python", "-m", "pytest", "tests/", "-m", "ui", "-v"], "UI tests only (using markers)"),
        (["python", "-m", "pytest", "tests/", "-m", "performance", "-v"], "Performance tests only (using markers)"),
    ]
    
    success_count = 0
    total_count = len(commands)
    
    for cmd, description in commands:
        if run_command(cmd, description):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Test Summary: {success_count}/{total_count} test suites passed")
    print('='*60)
    
    if success_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
