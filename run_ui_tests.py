#!/usr/bin/env python3
"""
UI Test runner script for Climate Dashboard.

This script provides an easy way to run UI tests with different configurations
and browsers.
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
    """Main UI test runner function."""
    print("🎭 Climate Dashboard UI Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("build.py").exists():
        print("❌ Error: Please run this script from the climate-dashboard root directory")
        sys.exit(1)
    
    # Build the dashboard first
    print("🏗️ Building dashboard...")
    build_result = subprocess.run(["python", "build.py"], capture_output=True, text=True)
    if build_result.returncode != 0:
        print("❌ Failed to build dashboard")
        print(build_result.stderr)
        sys.exit(1)
    print("✅ Dashboard built successfully")
    
    # UI Test commands
    commands = [
        (["python", "-m", "pytest", "tests/ui/", "-v"], "All UI tests with verbose output"),
        (["python", "-m", "pytest", "tests/ui/test_dashboard_ui.py", "-v"], "Dashboard UI tests only"),
        (["python", "-m", "pytest", "tests/ui/test_animations.py", "-v"], "Animation tests only"),
        (["python", "-m", "pytest", "tests/ui/test_performance.py", "-v"], "Performance tests only"),
        (["python", "-m", "pytest", "tests/ui/", "--headed"], "UI tests with browser visible"),
        (["python", "-m", "pytest", "tests/ui/", "--browser", "chromium"], "UI tests in Chromium only"),
        (["python", "-m", "pytest", "tests/ui/", "--browser", "firefox"], "UI tests in Firefox only"),
        (["python", "-m", "pytest", "tests/ui/", "--browser", "webkit"], "UI tests in WebKit only"),
        (["python", "-m", "pytest", "tests/ui/", "--slowmo", "1000"], "UI tests with slow motion"),
        (["python", "-m", "pytest", "tests/ui/", "--video", "on"], "UI tests with video recording"),
        (["python", "-m", "pytest", "tests/ui/", "--screenshot", "on"], "UI tests with screenshots"),
        (["python", "-m", "pytest", "tests/ui/", "-k", "not slow", "-v"], "Fast UI tests only"),
        (["python", "-m", "pytest", "tests/ui/", "-m", "performance", "-v"], "Performance tests only"),
    ]
    
    success_count = 0
    total_count = len(commands)
    
    for cmd, description in commands:
        if run_command(cmd, description):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"UI Test Summary: {success_count}/{total_count} test suites passed")
    print('='*60)
    
    if success_count == total_count:
        print("🎉 All UI tests passed!")
        return 0
    else:
        print("❌ Some UI tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
