#!/usr/bin/env python3
"""
Demo: TDD Workflow Enforcer with TRUE RED Phase

This demonstrates the TDD workflow enforcer working correctly
when tests are actually failing (true RED phase).
"""

import subprocess
import tempfile
import os
from pathlib import Path

# Create a temporary test file that will actually fail
test_content = '''
import pytest

def test_this_will_fail():
    """This test will fail as required for RED phase"""
    assert False, "RED phase - test designed to fail"

def test_another_failing_test():
    """Another failing test for RED phase"""
    result = 1 + 1
    assert result == 3, "RED phase - intentionally incorrect assertion"

def test_third_failing_test():
    """Third failing test"""
    assert "hello" == "world", "RED phase - strings don't match"
'''

# Write to temporary test file
with tempfile.NamedTemporaryFile(mode='w', suffix='_red_phase.py', delete=False) as f:
    f.write(test_content)
    temp_test_file = f.name

try:
    print("🧪 Testing TRUE RED Phase with TDD Workflow Enforcer...")
    
    # Run the failing tests
    print(f"\n🔴 Running TRUE RED phase tests from {temp_test_file}...")
    result = subprocess.run([
        'python', '-m', 'pytest', temp_test_file, '--tb=short', '-v'
    ], capture_output=True, text=True, cwd='/workspaces/control_tower')
    
    test_output = result.stdout + result.stderr
    print(f"Test exit code: {result.returncode}")
    print("Test output sample:")
    print(test_output[:500] + "..." if len(test_output) > 500 else test_output)
    
    # Test with TDD enforcer
    from shared.common.tdd_workflow_enforcer import TDDWorkflowEnforcer
    
    enforcer = TDDWorkflowEnforcer()
    
    # Simulate passing the first 3 gates
    enforcer.gates_passed.add('stage_gate_1')
    enforcer.gates_passed.add('stage_gate_2')
    enforcer.gates_passed.add('stage_gate_3')
    
    # Test Stage Gate 4 with real failing tests
    stage_gate_4_result = enforcer.stage_gate_4_red_phase_validation(test_output)
    
    print(f"\n📊 Stage Gate 4 Result:")
    print(f"Status: {stage_gate_4_result.status.value}")
    print(f"Output: {stage_gate_4_result.terminal_output}")
    print(f"Can proceed: {stage_gate_4_result.can_proceed}")
    
    # Check overall workflow integrity
    print(f"\n🔍 TDD Workflow Integrity Check:")
    integrity_valid = enforcer.validate_tdd_workflow_integrity()
    print(f"Workflow integrity: {integrity_valid}")
    
    # Show verification data
    verification_data = stage_gate_4_result.verification_data
    print(f"\n📈 Verification Data:")
    print(f"  Passed tests: {verification_data.get('passed_tests', 0)}")
    print(f"  Failed tests: {verification_data.get('failed_tests', 0)}")
    print(f"  Total tests: {verification_data.get('total_tests', 0)}")
    print(f"  RED phase valid: {verification_data.get('red_phase_valid', False)}")

finally:
    # Clean up temporary file
    os.unlink(temp_test_file)
    print(f"\n🧹 Cleaned up temporary test file")