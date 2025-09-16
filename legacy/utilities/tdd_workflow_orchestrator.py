#!/usr/bin/env python3
"""
TDD Workflow Runner - Uses existing FR-002 enforcer

Simple runner to execute complete TDD workflow using the existing enforcer.
Usage: python run-tdd-workflow.py
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from shared.common.requirements_parser import RequirementsParser
from shared.common.test_generator import TestGenerator
from shared.common.tdd_workflow_enforcer import TDDWorkflowEnforcer

def main():
    """Run complete TDD workflow using existing enforcer"""
    
    # Create shared enforcer instance
    enforcer = TDDWorkflowEnforcer()
    
    # Create parser and test generator with shared enforcer
    parser = RequirementsParser()
    test_generator = TestGenerator('pytest', enforcer)
    
    # Requirements file path
    requirements_file = "requirements/layers/LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001.md"
    
    # Stage Gate 1: Requirements file validation
    stage_1_result = enforcer.stage_gate_1_requirements_file_validation(requirements_file)
    
    if stage_1_result.can_proceed:
        # Stage Gate 2: Requirements parsing
        parsed_requirement = parser.parse_file(requirements_file)
        stage_2_result = enforcer.stage_gate_2_parsing_completion_verification(parsed_requirement)
        
        if stage_2_result.can_proceed:
            # Stage Gate 3: Test generation (includes validation)
            generated_tests = test_generator.generate_tests_from_requirement(parsed_requirement)
            
            if "stage_gate_3" in enforcer.gates_passed:
                # Stage Gate 4: RED phase validation
                import subprocess
                
                result = subprocess.run([
                    'python', '-m', 'pytest',
                    'control_tower_failing_tests/',
                    '-v', '--tb=short'
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                stage_4_result = enforcer.stage_gate_4_red_phase_validation(result.stdout + result.stderr)

if __name__ == "__main__":
    main()