#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API

This script provides different ways to run the test suite with common options.
"""

import subprocess
import sys
import argparse


def run_command(command, description):
    """Run a command and handle its output."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                              capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for the Activities API")
    parser.add_argument('--quick', action='store_true', 
                       help='Run tests without coverage (faster)')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage report')
    parser.add_argument('--performance', action='store_true', 
                       help='Run only performance tests')
    parser.add_argument('--api', action='store_true', 
                       help='Run only API tests')
    parser.add_argument('--validation', action='store_true', 
                       help='Run only data validation tests')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = "python -m pytest tests/"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    # Determine which tests to run
    if args.api:
        pytest_cmd = pytest_cmd.replace("tests/", "tests/test_api.py")
        description = "Running API Tests"
    elif args.validation:
        pytest_cmd = pytest_cmd.replace("tests/", "tests/test_data_validation.py")
        description = "Running Data Validation Tests"
    elif args.performance:
        pytest_cmd = pytest_cmd.replace("tests/", "tests/test_performance.py")
        description = "Running Performance Tests"
    else:
        description = "Running All Tests"
    
    # Add coverage if requested
    if args.coverage and not args.quick:
        pytest_cmd += " --cov=src --cov-report=html --cov-report=term-missing"
        description += " with Coverage"
    elif not args.quick and not (args.api or args.validation or args.performance):
        # Default to coverage for full test runs
        pytest_cmd += " --cov=src --cov-report=term"
        description += " with Coverage"
    
    # Run the tests
    success = run_command(pytest_cmd, description)
    
    if success:
        print(f"\n🎉 All tests passed successfully!")
        if "--cov=" in pytest_cmd:
            print(f"📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n💥 Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()