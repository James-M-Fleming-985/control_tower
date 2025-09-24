#!/usr/bin/env python3
"""
Simple test runner for TDD Integration Layer tests
Simulates pytest behavior without requiring pytest installation
"""

import sys
import os
import traceback
from datetime import datetime

# Add the integration layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'integration_layer'))

class SimpleTestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def fail(self, message):
        """Simulate pytest.fail()"""
        raise AssertionError(message)
        
    def run_test_method(self, test_class, method_name):
        """Run a single test method"""
        try:
            # Create test instance
            test_instance = test_class()
            
            # Run setup if it exists
            if hasattr(test_instance, 'setup_method'):
                # Monkey patch pytest.fail for the test
                import types
                pytest_module = types.ModuleType('pytest')
                pytest_module.fail = self.fail
                sys.modules['pytest'] = pytest_module
                
                test_instance.setup_method()
            
            # Run the actual test method
            method = getattr(test_instance, method_name)
            method()
            
            print(f"✅ PASS: {method_name}")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"❌ FAIL: {method_name}")
            print(f"   Error: {str(e)}")
            self.failed += 1
            self.errors.append({
                'test': method_name,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            return False
    
    def run_all_tests(self, test_class):
        """Run all test methods in a test class"""
        print(f"\n🧪 Running tests for {test_class.__name__}")
        print("=" * 60)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        
        print(f"Found {len(test_methods)} test methods\n")
        
        # Run each test method
        for method_name in test_methods:
            self.run_test_method(test_class, method_name)
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test execution report"""
        total = self.passed + self.failed
        
        report = f"""
🧪 TEST EXECUTION REPORT
========================
Total Tests: {total}
✅ Passed: {self.passed}
❌ Failed: {self.failed}
Success Rate: {(self.passed/total*100) if total > 0 else 0:.1f}%

"""
        
        if self.errors:
            report += "DETAILED FAILURE ANALYSIS:\n"
            report += "-" * 40 + "\n"
            for i, error in enumerate(self.errors, 1):
                report += f"{i}. {error['test']}:\n"
                report += f"   {error['error']}\n\n"
        
        return report

if __name__ == "__main__":
    # Add tests directory to path and import the test class
    sys.path.append('tests')
    try:
        from test_integration_layer import TestTDDIntegrationLayer
    except ImportError as e:
        print(f"❌ Failed to import test class: {e}")
        sys.exit(1)
    
    # Run the tests
    runner = SimpleTestRunner()
    report = runner.run_all_tests(TestTDDIntegrationLayer)
    
    print(report)
    
    # Return exit code based on results
    sys.exit(0 if runner.failed == 0 else 1)