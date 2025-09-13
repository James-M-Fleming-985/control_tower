#!/usr/bin/env python3
"""
🧪 REQUIREMENTS MANAGEMENT SYSTEM TEST RUNNER
Runs comprehensive tests for the hierarchical requirements management system

Usage:
    python test_runner.py                    # Run all tests
    python test_runner.py --makefile        # Test only Makefile commands
    python test_runner.py --validation      # Test only validation scripts
    python test_runner.py --integration     # Test only integration workflows
    python test_runner.py --user-value      # Test only user value delivery
"""

import subprocess
import sys
import argparse
from pathlib import Path
import time

def run_test_suite(test_type="all"):
    """Run the specified test suite"""
    
    test_dir = Path(__file__).parent
    control_tower_root = test_dir.parent
    
    print(f"🧪 Running Requirements Management System Tests")
    print(f"📁 Test Directory: {test_dir}")
    print(f"🗼 Control Tower Root: {control_tower_root}")
    print(f"🎯 Test Type: {test_type}")
    print("=" * 60)
    
    start_time = time.time()
    
    if test_type in ["all", "makefile"]:
        print("\n🔧 Testing Makefile Commands...")
        result = run_makefile_tests()
        if result != 0:
            print("❌ Makefile tests failed!")
            return result
    
    if test_type in ["all", "validation"]:
        print("\n✅ Testing Validation Scripts...")
        result = run_validation_tests()
        if result != 0:
            print("❌ Validation tests failed!")
            return result
    
    if test_type in ["all", "integration"]:
        print("\n🔗 Testing Integration Workflows...")
        result = run_integration_tests()
        if result != 0:
            print("❌ Integration tests failed!")
            return result
    
    if test_type in ["all", "user-value"]:
        print("\n👤 Testing User Value Delivery...")
        result = run_user_value_tests()
        if result != 0:
            print("❌ User value tests failed!")
            return result
    
    execution_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"✅ All tests completed successfully!")
    print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
    print("🎉 Requirements Management System is working correctly!")
    
    return 0

def run_makefile_tests():
    """Run tests specifically for Makefile functionality"""
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_makefile_validation.py",
            "-v", "--tb=short", "--color=yes"
        ], cwd=Path(__file__).parent, timeout=120)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("⏰ Makefile tests timed out")
        return 1
    except Exception as e:
        print(f"❌ Error running Makefile tests: {e}")
        return 1

def run_validation_tests():
    """Run tests for validation scripts and logic"""
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_requirements_management_system.py::TestRequirementsValidation",
            "-v", "--tb=short", "--color=yes"
        ], cwd=Path(__file__).parent, timeout=120)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("⏰ Validation tests timed out")
        return 1
    except Exception as e:
        print(f"❌ Error running validation tests: {e}")
        return 1

def run_integration_tests():
    """Run tests for end-to-end integration workflows"""
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_requirements_management_system.py::TestEndToEndWorkflows",
            "-v", "--tb=short", "--color=yes"
        ], cwd=Path(__file__).parent, timeout=180)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("⏰ Integration tests timed out")
        return 1
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return 1

def run_user_value_tests():
    """Run tests that validate user value delivery"""
    
    try:
        # Run user value tests from both test files
        result1 = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_makefile_validation.py::TestUserValueDelivery",
            "-v", "--tb=short", "--color=yes"
        ], cwd=Path(__file__).parent, timeout=120)
        
        if result1.returncode != 0:
            return result1.returncode
        
        result2 = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_requirements_management_system.py::TestEndToEndWorkflows::test_user_value_delivery",
            "-v", "--tb=short", "--color=yes"
        ], cwd=Path(__file__).parent, timeout=120)
        
        return result2.returncode
        
    except subprocess.TimeoutExpired:
        print("⏰ User value tests timed out")
        return 1
    except Exception as e:
        print(f"❌ Error running user value tests: {e}")
        return 1

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Run Requirements Management System Tests")
    parser.add_argument("--makefile", action="store_true", help="Test only Makefile commands")
    parser.add_argument("--validation", action="store_true", help="Test only validation scripts")  
    parser.add_argument("--integration", action="store_true", help="Test only integration workflows")
    parser.add_argument("--user-value", action="store_true", help="Test only user value delivery")
    
    args = parser.parse_args()
    
    # Determine test type
    if args.makefile:
        test_type = "makefile"
    elif args.validation:
        test_type = "validation"
    elif args.integration:
        test_type = "integration"
    elif args.user_value:
        test_type = "user-value"
    else:
        test_type = "all"
    
    # Run tests
    result = run_test_suite(test_type)
    sys.exit(result)

if __name__ == "__main__":
    main()