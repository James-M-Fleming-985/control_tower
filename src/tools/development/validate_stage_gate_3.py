#!/usr/bin/env python3
"""
Validation Script for Stage Gate 3 Requirements Coverage

This script validates that Stage Gate 3 now shows:
- Number of tests generated
- Number of requirements covered
- Coverage details by requirement type (FR, BR, AC, PR, QR)
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from shared.common.requirements_parser import RequirementsParser
from shared.common.test_generator import TestGenerator
from shared.common.tdd_workflow_enforcer import TDDWorkflowEnforcer

def main():
    print("🔍 Validating Stage Gate 3 Requirements Coverage Output...")
    print("=" * 60)
    
    # Create shared enforcer instance
    enforcer = TDDWorkflowEnforcer()
    
    # Create parser and test generator with shared enforcer
    parser = RequirementsParser(enforcer)
    test_generator = TestGenerator(enforcer)
    
    # Parse requirements
    item_id = 'LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001'
    print(f'📋 Parsing requirements for {item_id}...')
    parsed_requirement = parser.parse_work_item_requirements(item_id)
    
    print(f'\n📊 Requirements Summary:')
    print(f'  FR: {len(parsed_requirement.functional_requirements)}')
    print(f'  BR: {len(parsed_requirement.business_requirements)}')
    print(f'  AC: {len(parsed_requirement.acceptance_criteria)}')
    print(f'  PR: {len(parsed_requirement.performance_requirements)}')
    print(f'  QR: {len(parsed_requirement.quality_requirements)}')
    
    total_requirements = (
        len(parsed_requirement.functional_requirements) +
        len(parsed_requirement.business_requirements) +
        len(parsed_requirement.acceptance_criteria) +
        len(parsed_requirement.performance_requirements) +
        len(parsed_requirement.quality_requirements)
    )
    print(f'  Total: {total_requirements} requirements')
    
    # Generate tests (this will trigger Stage Gate 3 with coverage output)
    print(f'\n🧪 Generating tests...')
    print("=" * 60)
    generated_tests = test_generator.generate_failing_tests(parsed_requirement)
    print("=" * 60)
    
    print(f'\n✅ Validation completed!')
    print(f'Generated {len(generated_tests)} tests')
    
    # Check if Stage Gate 3 passed and show summary
    if "stage_gate_3" in enforcer.gates_passed:
        print(f'✅ Stage Gate 3 PASSED with requirements coverage output')
        
        # Get verification data
        stage_3_result = enforcer.stage_gate_results.get("stage_gate_3")
        if stage_3_result:
            verification_data = stage_3_result.verification_data
            print(f'\n📈 Verification Data:')
            print(f'  Tests generated: {verification_data.get("generated_tests_count", 0)}')
            print(f'  Requirements covered: {verification_data.get("requirements_covered", 0)}')
            print(f'  Total requirements: {verification_data.get("total_requirements", 0)}')
            print(f'  Coverage percentage: {verification_data.get("coverage_percentage", 0)}%')
            print(f'  Coverage details: {verification_data.get("coverage_details", {})}')
    else:
        print(f'❌ Stage Gate 3 FAILED')

if __name__ == "__main__":
    main()