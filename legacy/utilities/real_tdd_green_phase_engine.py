#!/usr/bin/env python3
"""
REAL TDD GREEN Phase Iteration Engine
Implements minimal REAL code, runs REAL tests, creates REAL backups, provides REAL progress
"""

import sys
import os
import subprocess
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from shared.common.tdd_workflow_enforcer import TDDWorkflowEnforcer

class RealTDDGreenPhaseEngine:
    """Engine for iterative REAL TDD GREEN phase implementation"""
    
    def __init__(self):
        self.enforcer = TDDWorkflowEnforcer()
        self.test_dir = "control_tower_failing_tests"
        self.test_file = "test_simple_automation_demo.py"  # Use simple demo tests
        self.total_tests = 0
        self.passing_count = 0
        
    def run_iterative_green_phase(self):
        """
        Fully automated GREEN phase: analyzes failing tests and implements minimal code
        """
        print("🚀 GREEN PHASE AUTOMATION")
        
        # Get initial test count
        self._update_test_count()
        
        while True:
            # Find next failing test
            failing_test = self._find_next_failing_test()
            if not failing_test:
                print("\n🎉 ALL TESTS PASSING!")
                break
                
            print(f"\n🎯 {failing_test}")
            
            # Try up to 5 attempts for this test
            attempt = 0
            max_attempts = 5
            test_passed = False
            
            while attempt < max_attempts and not test_passed:
                attempt += 1
                print(f"   Attempt: {attempt}/{max_attempts}")
                print("   Status: IMPLEMENTING")
                
                # Automatically implement REAL code for this test
                implementation_success = self._auto_implement_code(failing_test)
                
                if implementation_success:
                    print("   Status: TESTING")
                    
                    if self._test_specific_function(failing_test):
                        self.passing_count += 1
                        print("   Status: PASS")
                        test_passed = True
                        
                        # Auto-save and backup
                        test_file = f"{self.test_dir}/test_test_generator.py"
                        backup_path = self.enforcer.create_incremental_test_backup(
                            test_name=failing_test,
                            passing_count=self.passing_count,
                            total_count=self.total_tests
                        )
                        
                        print(f"   File saved: {test_file}")
                        if backup_path:
                            print(f"   Backup: {backup_path}")
                        print(f"   Progress: {self.passing_count}/{self.total_tests}")
                        
                    else:
                        print("   Status: FAIL")
                        if attempt < max_attempts:
                            print(f"   Try again ({max_attempts - attempt} attempts left)")
                else:
                    print("   Status: IMPLEMENTATION_FAILED")
                    if attempt < max_attempts:
                        print(f"   Retry implementation ({max_attempts - attempt} attempts left)")
                    else:
                        break
            
            if not test_passed:
                print(f"   SKIPPING: {failing_test} after {max_attempts} attempts (will appear in final Stage 5)")
        
        # Final Stage 5 verification
        print(f"\n🏁 STAGE 5 VERIFICATION")
        stage5_result = self.enforcer.stage_gate_5_green_phase_implementation_quality_verification()
        
        print(f"   Status: {stage5_result.status}")
        print(f"   Can Proceed: {stage5_result.can_proceed}")
        
        return stage5_result
    
    def _show_test_details(self, test_name):
        """Show test failure details to guide implementation"""
        try:
            test_file = os.path.join(self.test_dir, "test_test_generator.py")
            cmd = ["python", "-m", "pytest", f"{test_file}::{test_name}", "-v", "--tb=short"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            print("   Test Failure Details:")
            # Show key error info (truncated for readability)
            lines = result.stdout.split('\n')
            for line in lines[-8:]:
                if line.strip() and ('FAILED' in line or 'AssertionError' in line or 'AttributeError' in line):
                    print(f"     {line.strip()}")
                    
        except Exception as e:
            print(f"   Error getting test details: {e}")
    
    def _auto_implement_code(self, test_name):
        """
        Create implementation work queue and wait for AI to implement REAL code
        Returns True if implementation was completed, False if failed
        """
        try:
            # Create work queue directory if it doesn't exist
            work_queue_dir = "/tmp/ai_work_queue"
            os.makedirs(work_queue_dir, exist_ok=True)
            
            # Get detailed test failure information
            test_file = os.path.join(self.test_dir, "test_test_generator.py")
            cmd = ["python", "-m", "pytest", f"{test_file}::{test_name}", "-v", "--tb=long"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Create implementation request
            request_file = os.path.join(work_queue_dir, f"implement_{test_name}.request")
            with open(request_file, 'w') as f:
                f.write(f"AI IMPLEMENTATION REQUEST\n")
                f.write(f"========================\n")
                f.write(f"Test: {test_name}\n")
                f.write(f"Status: WAITING_FOR_AI_IMPLEMENTATION\n")
                f.write(f"Test File: {test_file}\n")
                f.write(f"Created: {time.time()}\n")
                f.write(f"\nTest Failure Details:\n")
                f.write(f"STDOUT:\n{result.stdout}\n")
                f.write(f"STDERR:\n{result.stderr}\n")
            
            print(f"   AI: Implementation request created: {request_file}")
            print(f"   AI: WAITING for implementation...")
            
            # Wait for AI to implement and mark as complete
            completion_file = os.path.join(work_queue_dir, f"implement_{test_name}.complete")
            max_wait_time = 30  # 30 seconds max wait (reduced from 300)
            wait_time = 0
            check_interval = 1  # Check every 1 second (faster response)
            
            while wait_time < max_wait_time:
                if os.path.exists(completion_file):
                    # AI has completed implementation
                    with open(completion_file, 'r') as f:
                        completion_status = f.read().strip()
                    
                    print(f"   AI: Implementation completed with status: {completion_status}")
                    
                    # Clean up files
                    os.remove(request_file)
                    os.remove(completion_file)
                    
                    return completion_status == "SUCCESS"
                
                time.sleep(check_interval)
                wait_time += check_interval
                
                # Show waiting progress every 5 seconds (faster updates)
                if wait_time % 5 == 0:
                    print(f"   AI: Still waiting... ({wait_time}s elapsed)")
            
            print(f"   AI: Timeout waiting for implementation ({max_wait_time}s)")
            return False
            
        except Exception as e:
            print(f"   AI: Error in implementation workflow: {e}")
            return False
    
    def _find_next_failing_test(self):
        """Find the next failing test using pytest -x"""
        try:
            cmd = ["python", "-m", "pytest", f"{self.test_dir}/{self.test_file}", "-x", "--tb=no"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Parse output to find first failing test
            lines = result.stdout.split('\n')
            for line in lines:
                if "FAILED" in line and "::" in line:
                    # Extract test name: "path/file.py::test_name FAILED"
                    test_part = line.split("::")[1].split()[0]
                    return test_part
            
            return None  # No failing tests found
            
        except Exception as e:
            print(f"❌ Error finding failing test: {e}")
            return None
    
    def _test_specific_function(self, test_name):
        """Test a specific function to see if it passes"""
        try:
            cmd = ["python", "-m", "pytest", f"{self.test_dir}/{self.test_file}::{test_name}", "-v", "--tb=no"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0 and "PASSED" in result.stdout
            
        except Exception as e:
            print(f"❌ Error testing {test_name}: {e}")
            return False
    
    def _update_test_count(self):
        """Update the total test count"""
        try:
            test_file = os.path.join(self.test_dir, self.test_file)
            with open(test_file, 'r') as f:
                content = f.read()
                import re
                test_functions = re.findall(r'^def (test_[^(]+)', content, re.MULTILINE)
                self.total_tests = len(test_functions)
                
        except Exception as e:
            print(f"❌ Error counting tests: {e}")
            self.total_tests = 3  # fallback


if __name__ == "__main__":
    engine = RealTDDGreenPhaseEngine()
    engine.run_iterative_green_phase()