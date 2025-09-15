#!/usr/bin/env python3
"""
TDD Workflow Enforcer - Complete Stage Gate Validation

Simple script to run all four TDD stage gates with clean terminal output.
This demonstrates the complete RED phase validation with immutable evidence.
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_access.requirements_parser import RequirementsParser
from data_access.test_generator import TestGenerator
from data_access.tdd_workflow_enforcer import TDDWorkflowEnforcer

def main():
    """Run complete TDD workflow enforcer with all four stage gates"""
    
    print("\033[95m🔧 TDD Workflow Enforcer - Complete Stage Gate Validation\033[0m")
    print("=" * 70)
    
    # Create shared enforcer instance
    enforcer = TDDWorkflowEnforcer()
    
    # Create parser and test generator with shared enforcer
    parser = RequirementsParser(enforcer)
    test_generator = TestGenerator('pytest', enforcer)
    
    # Requirements file path
    requirements_file = "requirements/layers/LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001.md"
    
    try:
        # Stage Gate 1: Requirements file validation
        print("\n\033[95m🔍 Stage Gate 1: Requirements File Validation\033[0m")
        stage_1_result = enforcer.stage_gate_1_requirements_file_validation(requirements_file)
        
        if stage_1_result.success:
            # Stage Gate 2: Requirements parsing
            print("\n\033[95m📝 Stage Gate 2: Requirements Parsing & Verification\033[0m")
            parsed_requirement = parser.parse_requirements_file(requirements_file)
            stage_2_result = enforcer.stage_gate_2_parsing_completion_verification(parsed_requirement)
            
            if stage_2_result.success:
                # Stage Gate 3: Test generation
                print("\n\033[95m🧪 Stage Gate 3: Test Generation & File Creation\033[0m")
                generated_tests = test_generator.generate_tests_from_requirement(parsed_requirement)
                # Stage Gate 3 validation happens inside generate_tests_from_requirement
                
                if "stage_gate_3" in enforcer.gates_passed:
                    # Stage Gate 4: RED phase validation
                    print("\n\033[95m🔴 Stage Gate 4: RED Phase Validation\033[0m")
                    import subprocess
                    
                    # Run pytest on our REAL failing test files
                    result = subprocess.run([
                        'python', '-m', 'pytest',
                        'control_tower_failing_tests/',
                        '-v', '--tb=short'
                    ], capture_output=True, text=True, cwd=os.getcwd())
                    
                    stage_4_result = enforcer.stage_gate_4_red_phase_validation(result.stdout + result.stderr)
                    
                    # Final summary
                    print("\n\033[95m🎯 TDD Workflow Summary\033[0m")
                    print("=" * 50)
                    
                    gates_status = [
                        ("Stage Gate 1", "stage_gate_1" in enforcer.gates_passed),
                        ("Stage Gate 2", "stage_gate_2" in enforcer.gates_passed), 
                        ("Stage Gate 3", "stage_gate_3" in enforcer.gates_passed),
                        ("Stage Gate 4", "stage_gate_4" in enforcer.gates_passed)
                    ]
                    
                    for gate_name, passed in gates_status:
                        status = "\033[92m✅ PASSED\033[0m" if passed else "\033[91m❌ FAILED\033[0m"
                        print(f"{gate_name}: {status}")
                    
                    if enforcer.can_proceed_to_green_phase():
                        print(f"\n\033[92m🎉 RED PHASE COMPLETE - Ready for GREEN phase implementation!\033[0m")
                        print(f"\033[96mBaseline saved: {enforcer.red_phase_baseline}\033[0m")
                    else:
                        print(f"\n\033[91m❌ RED PHASE INCOMPLETE - Check stage gate failures\033[0m")
                        
                else:
                    print(f"\n\033[91m❌ Stage Gate 3 failed - Cannot proceed to RED phase validation\033[0m")
            else:
                print(f"\n\033[91m❌ Stage Gate 2 failed - Cannot proceed to test generation\033[0m")
        else:
            print(f"\n\033[91m❌ Stage Gate 1 failed - Cannot proceed to parsing\033[0m")
            
    except Exception as e:
        print(f"\n\033[91m💥 TDD Workflow Error: {e}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()