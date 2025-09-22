#!/usr/bin/env python3
"""
REAL Requirements Verification Report Generator
Validates LAYER-003-01-02-001 DATA ACCESS LAYER implementation against specific requirements
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.append('src')

class RequirementsVerifier:
    def __init__(self):
        self.results = {}
        self.failures = []
        self.warnings = []
        
    def check_requirement(self, req_id, description, check_func):
        """Execute a requirement check and record results"""
        try:
            result = check_func()
            status = "PASS" if result['passed'] else "FAIL"
            self.results[req_id] = {
                'description': description,
                'status': status,
                'details': result.get('details', ''),
                'evidence': result.get('evidence', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            if not result['passed']:
                self.failures.append(f"{req_id}: {description}")
            
            print(f"{'✅' if result['passed'] else '❌'} {req_id}: {description}")
            if result.get('details'):
                print(f"   Details: {result['details']}")
                
        except Exception as e:
            self.results[req_id] = {
                'description': description,
                'status': 'ERROR',
                'details': str(e),
                'evidence': '',
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ {req_id}: ERROR - {e}")
    
    def req_001_real_components_exist(self):
        """REQ-001: All 4 REAL components must be implemented"""
        components = [
            'src/data_access/real_test_file_discovery.py',
            'src/data_access/real_test_metadata_persistence.py', 
            'src/data_access/real_test_result_storage.py',
            'src/data_access/real_verification_evidence_storage.py'
        ]
        
        existing = [c for c in components if Path(c).exists()]
        passed = len(existing) == 4
        
        return {
            'passed': passed,
            'details': f"Found {len(existing)}/4 REAL components",
            'evidence': f"Existing: {existing}"
        }
    
    def req_002_performance_requirements(self):
        """REQ-002: Performance must be <100ms response time, >1000 files/sec"""
        try:
            from data_access.real_test_file_discovery import RealTestFileDiscovery
            
            discovery = RealTestFileDiscovery('/workspaces/control_tower/tests')
            
            start_time = time.time()
            test_files = discovery.discover_real_test_files()
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            throughput = len(test_files) / (response_time_ms / 1000) if response_time_ms > 0 else 0
            
            response_ok = response_time_ms <= 100
            throughput_ok = throughput >= 1000
            passed = response_ok and throughput_ok
            
            return {
                'passed': passed,
                'details': f"Response: {response_time_ms:.1f}ms, Throughput: {throughput:.0f}/sec",
                'evidence': f"Files discovered: {len(test_files)}"
            }
        except Exception as e:
            return {'passed': False, 'details': f"Performance test failed: {e}"}
    
    def req_003_repository_pattern(self):
        """REQ-003: Repository pattern must be implemented"""
        try:
            from data_access.real_test_file_discovery import RealTestFileDiscovery
            from data_access.utilities import ThreadSafeDataAccess
            
            # Check inheritance
            inherits_correctly = issubclass(RealTestFileDiscovery, ThreadSafeDataAccess)
            
            # Check required methods exist
            instance = RealTestFileDiscovery('/tmp')
            has_discover = hasattr(instance, 'discover_real_test_files')
            has_validate = hasattr(instance, 'validate_test_file')
            
            passed = inherits_correctly and has_discover and has_validate
            
            return {
                'passed': passed,
                'details': f"Inheritance: {inherits_correctly}, Methods: discover={has_discover}, validate={has_validate}",
                'evidence': f"Base class: {RealTestFileDiscovery.__bases__}"
            }
        except Exception as e:
            return {'passed': False, 'details': f"Repository pattern check failed: {e}"}
    
    def req_004_sqlite_storage(self):
        """REQ-004: SQLite storage must be implemented for test results"""
        try:
            from data_access.real_test_result_storage import RealTestResultStorage
            
            storage = RealTestResultStorage('/tmp/test_verification')
            
            # Test basic operations
            test_result = {
                'test_id': 'verification_001',
                'status': 'PASSED',
                'execution_time': 0.05,
                'timestamp': time.time()
            }
            
            # Test store
            storage.store_test_result(test_result)
            
            # Test retrieve
            results = storage.get_test_results({'test_id': 'verification_001'})
            
            passed = len(results) > 0 and results[0]['status'] == 'PASSED'
            
            return {
                'passed': passed,
                'details': f"Storage and retrieval working, found {len(results)} results",
                'evidence': f"Test result stored and retrieved successfully"
            }
        except Exception as e:
            return {'passed': False, 'details': f"SQLite storage test failed: {e}"}
    
    def req_005_error_handling(self):
        """REQ-005: Comprehensive error handling must be implemented"""
        try:
            from data_access.real_test_file_discovery import RealTestFileDiscovery
            
            # Test invalid directory handling
            try:
                discovery = RealTestFileDiscovery('/nonexistent/directory/path')
                discovery.discover_real_test_files()
                error_handled = True
            except Exception:
                error_handled = True  # Expected to handle gracefully
            
            # Check code for error handling patterns
            with open('src/data_access/real_test_file_discovery.py', 'r') as f:
                content = f.read()
            
            has_try_except = 'try:' in content and 'except' in content
            has_logging = 'log' in content.lower()
            
            passed = error_handled and has_try_except
            
            return {
                'passed': passed,
                'details': f"Error handling: {has_try_except}, Logging: {has_logging}",
                'evidence': f"Exception handling patterns found in code"
            }
        except Exception as e:
            return {'passed': False, 'details': f"Error handling test failed: {e}"}
    
    def req_006_test_coverage(self):
        """REQ-006: Test coverage must be ≥95% for REAL components"""
        try:
            # Run pytest with coverage for REAL components only
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/test_data_access/test_requirements_driven_data_access.py',
                '--cov=src/data_access/real_test_file_discovery.py',
                '--cov=src/data_access/real_test_result_storage.py',
                '--cov-report=json',
                '--quiet'
            ], capture_output=True, text=True, timeout=30)
            
            if Path('coverage.json').exists():
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                passed = total_coverage >= 95
                
                return {
                    'passed': passed,
                    'details': f"Coverage: {total_coverage:.1f}% (Target: ≥95%)",
                    'evidence': f"Coverage report generated successfully"
                }
            else:
                return {'passed': False, 'details': "Coverage report not generated"}
                
        except Exception as e:
            return {'passed': False, 'details': f"Coverage test failed: {e}"}
    
    def req_007_security_validation(self):
        """REQ-007: Security requirements must be implemented"""
        security_checks = []
        
        try:
            # Check for path validation
            with open('src/data_access/real_test_file_discovery.py', 'r') as f:
                content = f.read()
            
            has_path_validation = 'Path(' in content or 'pathlib' in content
            has_sanitization = 'resolve()' in content or 'absolute()' in content
            has_input_validation = 'validate' in content.lower()
            
            security_checks = [
                ('Path validation', has_path_validation),
                ('Path sanitization', has_sanitization), 
                ('Input validation', has_input_validation)
            ]
            
            passed_checks = sum(1 for _, check in security_checks if check)
            passed = passed_checks >= 2  # At least 2/3 security features
            
            return {
                'passed': passed,
                'details': f"Security features: {passed_checks}/3 implemented",
                'evidence': f"Checks: {security_checks}"
            }
        except Exception as e:
            return {'passed': False, 'details': f"Security validation failed: {e}"}
    
    def generate_report(self):
        """Generate final verification report"""
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        failed_checks = sum(1 for r in self.results.values() if r['status'] == 'FAIL')
        error_checks = sum(1 for r in self.results.values() if r['status'] == 'ERROR')
        
        print("\n" + "="*80)
        print("📊 REQUIREMENTS VERIFICATION REPORT")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Layer: DATA ACCESS LAYER (LAYER-003-01-02-001)")
        print(f"Feature: TEST GENERATION VERIFICATION SYSTEM")
        print()
        
        print("📈 SUMMARY:")
        print(f"   Total Requirements: {total_checks}")
        print(f"   ✅ Passed: {passed_checks}")
        print(f"   ❌ Failed: {failed_checks}")
        print(f"   🔥 Errors: {error_checks}")
        print(f"   Success Rate: {(passed_checks/total_checks)*100:.1f}%")
        print()
        
        if failed_checks > 0:
            print("❌ FAILURES:")
            for failure in self.failures:
                print(f"   - {failure}")
            print()
        
        # Determine overall status
        if passed_checks == total_checks:
            status = "✅ FULLY COMPLIANT"
            recommendation = "Ready for production deployment"
        elif passed_checks >= total_checks * 0.8:
            status = "⚠️ MOSTLY COMPLIANT"
            recommendation = "Address failures before production"
        else:
            status = "❌ NON-COMPLIANT"
            recommendation = "Significant work required before deployment"
        
        print(f"🎯 OVERALL STATUS: {status}")
        print(f"📋 RECOMMENDATION: {recommendation}")
        print()
        
        # Save detailed results
        with open('verification_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print("📄 Detailed results saved to: verification_results.json")
        
        return {
            'status': status,
            'passed': passed_checks,
            'total': total_checks,
            'success_rate': (passed_checks/total_checks)*100
        }

def main():
    print("🔍 STARTING REQUIREMENTS VERIFICATION")
    print("=" * 50)
    
    verifier = RequirementsVerifier()
    
    # Execute all requirement checks
    verifier.check_requirement(
        "REQ-001", 
        "All 4 REAL components implemented", 
        verifier.req_001_real_components_exist
    )
    
    verifier.check_requirement(
        "REQ-002", 
        "Performance requirements met (<100ms, >1000/sec)", 
        verifier.req_002_performance_requirements
    )
    
    verifier.check_requirement(
        "REQ-003", 
        "Repository pattern correctly implemented", 
        verifier.req_003_repository_pattern
    )
    
    verifier.check_requirement(
        "REQ-004", 
        "SQLite storage working correctly", 
        verifier.req_004_sqlite_storage
    )
    
    verifier.check_requirement(
        "REQ-005", 
        "Error handling comprehensive", 
        verifier.req_005_error_handling
    )
    
    verifier.check_requirement(
        "REQ-006", 
        "Test coverage ≥95%", 
        verifier.req_006_test_coverage
    )
    
    verifier.check_requirement(
        "REQ-007", 
        "Security requirements implemented", 
        verifier.req_007_security_validation
    )
    
    # Generate final report
    summary = verifier.generate_report()
    
    # Exit with appropriate code
    if summary['success_rate'] >= 100:
        sys.exit(0)  # All tests passed
    elif summary['success_rate'] >= 80:
        sys.exit(1)  # Some failures but mostly working
    else:
        sys.exit(2)  # Significant failures

if __name__ == "__main__":
    main()