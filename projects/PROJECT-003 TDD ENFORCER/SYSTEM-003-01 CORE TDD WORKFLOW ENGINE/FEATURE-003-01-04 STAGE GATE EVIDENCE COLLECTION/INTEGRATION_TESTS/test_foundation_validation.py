#!/usr/bin/env python3
"""
Foundation Test Validation for FEATURE-003-01-04 Integration
Validates the 7 critical tests before proceeding with feature integration.

This file ensures our refactored components are working correctly before
integrating with the broader FEATURE-003-01-04 Stage Gate Evidence Collection system.
"""

import sys
import os
sys.path.insert(0, '/workspaces/control_tower')

def test_foundation_components():
    """Execute all 7 foundation tests that must pass before integration"""
    
    print("🔧 Executing 7 Critical Foundation Tests...")
    
    try:
        # Import our validated components
        from evidence_display_interface import EvidenceDisplayInterface
        from evidence_validator import EvidenceValidator
        
        interface = EvidenceDisplayInterface()
        validator = EvidenceValidator()
        
        # Test 1: Mobile Display Configuration
        mobile_config = interface.create_mobile_optimized_display({'test': 'data'})
        assert 'screen_width' in mobile_config['display_config']
        assert mobile_config['display_config']['screen_width'] == 320
        print("✅ Test 1 PASSED: Mobile Display Configuration includes screen_width")
        
        # Test 2: Mobile CSS (16px font)
        mobile_css = interface.generate_mobile_css()
        assert 'font-size: 16px' in mobile_css
        print("✅ Test 2 PASSED: Mobile CSS uses 16px font size for iOS compliance")
        
        # Test 3: Responsive CSS Grid
        responsive_css = interface.generate_responsive_css()
        assert 'grid-template-columns: 1fr' in responsive_css
        print("✅ Test 3 PASSED: Responsive CSS includes single-column mobile grid")
        
        # Test 4: Mobile Data Pagination
        mobile_config = interface.create_mobile_optimized_display({
            'compliance_data': list(range(50)),
            'test_results': list(range(30))
        })
        assert len(mobile_config['compliance_data']) <= 10
        assert len(mobile_config['test_results']) <= 10
        print("✅ Test 4 PASSED: Mobile data pagination limits to 10 items")
        
        # Test 5: Mobile Workflow Objects
        workflow_data = {
            'stage': 'green_phase',
            'progress': 75,
            'mobile_optimized': True
        }
        mobile_package = interface.create_mobile_workflow_package(workflow_data)
        assert hasattr(mobile_package, 'to_dict')
        assert callable(getattr(mobile_package, 'to_dict'))
        assert isinstance(mobile_package.to_dict(), dict)
        print("✅ Test 5 PASSED: Mobile workflow object has working to_dict() method")
        
        # Test 6: RED Stage Validation
        red_test_data = {
            'tests_failing': 3,
            'tests_written': True,
            'implementation_exists': False
        }
        result = validator.validate_red_stage_acceptance(red_test_data)
        assert result == True
        print("✅ Test 6 PASSED: RED stage validation accepts proper failing test scenarios")
        
        # Test 7: Complete TDD Cycle Validation
        red_evidence = {'stage': 'red', 'tests_failing': 3}
        green_evidence = {'stage': 'green', 'tests_passing': 3, 'implementation': 'complete'}
        refactor_evidence = {'stage': 'refactor', 'code_quality': 'improved'}
        
        cycle_evidence = [red_evidence, green_evidence, refactor_evidence]
        cycle_result = validator.validate_complete_tdd_cycle(cycle_evidence)
        
        assert cycle_result.is_valid == True
        assert cycle_result.cycle_complete == True
        assert 'RED' in cycle_result.completed_phases
        assert 'GREEN' in cycle_result.completed_phases
        assert 'REFACTOR' in cycle_result.completed_phases
        print("✅ Test 7 PASSED: Complete TDD cycle validation recognizes RED→GREEN→REFACTOR sequence")
        
        print("\n🎉 ALL 7 FOUNDATION TESTS PASSED - READY FOR FEATURE INTEGRATION")
        return True
        
    except Exception as e:
        print(f"❌ FOUNDATION TEST FAILED: {e}")
        print("🚨 Cannot proceed with FEATURE-003-01-04 integration until foundation tests pass")
        return False

if __name__ == "__main__":
    success = test_foundation_components()
    sys.exit(0 if success else 1)