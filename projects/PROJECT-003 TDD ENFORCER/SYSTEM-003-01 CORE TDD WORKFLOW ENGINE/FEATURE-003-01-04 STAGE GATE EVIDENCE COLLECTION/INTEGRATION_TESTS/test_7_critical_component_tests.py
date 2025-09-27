"""
7 Critical Component Tests for FEATURE-003-01-04 Integration
These tests validate the foundation components before full feature integration.
All 7 tests must pass for successful FEATURE-003-01-04 integration.
"""
import sys
import os
from pathlib import Path

# Add workspace root to path for imports
workspace_root = Path("/workspaces/control_tower")
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

def test_1_mobile_display_configuration():
    """✅ Test 1: Mobile Display Configuration includes screen_width"""
    from evidence_display_interface import EvidenceDisplayInterface
    
    interface = EvidenceDisplayInterface()
    mobile_config = interface.create_mobile_optimized_display({'test': 'data'})
    
    assert 'screen_width' in mobile_config['display_config']
    assert mobile_config['display_config']['screen_width'] == 320
    assert mobile_config['display_config']['device_type'] == 'mobile'
    print("✅ Test 1 PASSED: Mobile Display Configuration includes screen_width")
    return True

def test_2_mobile_css_ios_compliance():
    """✅ Test 2: Mobile CSS uses 16px font size for iOS compliance"""
    from evidence_display_interface import EvidenceDisplayInterface
    
    interface = EvidenceDisplayInterface()
    mobile_css = interface.generate_mobile_css()
    
    assert 'font-size: 16px' in mobile_css
    assert '.compliance-dashboard' in mobile_css
    assert '.touch-target' in mobile_css
    print("✅ Test 2 PASSED: Mobile CSS uses 16px font size for iOS compliance")
    return True

def test_3_responsive_css_grid_layout():
    """✅ Test 3: Responsive CSS includes single-column mobile grid"""
    from evidence_display_interface import EvidenceDisplayInterface
    
    interface = EvidenceDisplayInterface()
    responsive_css = interface.generate_responsive_css()
    
    assert 'grid-template-columns: 1fr' in responsive_css
    assert '@media (max-width: 767px)' in responsive_css
    print("✅ Test 3 PASSED: Responsive CSS includes single-column mobile grid")
    return True

def test_4_mobile_data_pagination():
    """✅ Test 4: Mobile data pagination limits to 10 items"""
    from evidence_display_interface import EvidenceDisplayInterface
    
    interface = EvidenceDisplayInterface()
    large_dataset = {
        'compliance_data': list(range(50)),  # 50 items
        'test_results': list(range(30))      # 30 items
    }
    
    mobile_config = interface.create_mobile_optimized_display(large_dataset)
    
    assert len(mobile_config['compliance_data']) <= 10
    assert len(mobile_config['test_results']) <= 10
    assert mobile_config['display_config']['max_items'] == 10
    print("✅ Test 4 PASSED: Mobile data pagination limits to 10 items")
    return True

def test_5_mobile_workflow_object_to_dict():
    """✅ Test 5: Mobile workflow object has working to_dict() method"""
    from evidence_display_interface import EvidenceDisplayInterface
    
    interface = EvidenceDisplayInterface()
    workflow_data = {
        'stage': 'green_phase',
        'progress': 75,
        'mobile_optimized': True
    }
    
    mobile_package = interface.create_mobile_workflow_package(workflow_data)
    
    assert hasattr(mobile_package, 'to_dict')
    assert callable(getattr(mobile_package, 'to_dict'))
    result_dict = mobile_package.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict['stage'] == 'green_phase'
    assert result_dict['progress'] == 75
    print("✅ Test 5 PASSED: Mobile workflow object has working to_dict() method")
    return True

def test_6_red_stage_validation_criteria():
    """✅ Test 6: RED stage validation accepts proper failing test scenarios"""
    from evidence_validator import EvidenceValidator
    
    validator = EvidenceValidator()
    red_test_data = {
        'tests_failing': 3,
        'tests_written': True,
        'implementation_exists': False
    }
    
    result = validator.validate_red_stage_acceptance(red_test_data)
    
    assert result == True
    print("✅ Test 6 PASSED: RED stage validation accepts proper failing test scenarios")
    return True

def test_7_complete_tdd_cycle_validation():
    """✅ Test 7: Complete TDD cycle validation recognizes RED→GREEN→REFACTOR sequence"""
    from evidence_validator import EvidenceValidator
    
    validator = EvidenceValidator()
    
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
    return True

def run_all_7_critical_tests():
    """Run all 7 critical tests for FEATURE-003-01-04 integration validation"""
    print("🧪 Running 7 Critical Component Tests for FEATURE-003-01-04 Integration...")
    print("📁 Location: FEATURE-003-01-04 STAGE GATE EVIDENCE COLLECTION/INTEGRATION_TESTS/")
    print("=" * 80)
    
    tests = [
        test_1_mobile_display_configuration,
        test_2_mobile_css_ios_compliance,
        test_3_responsive_css_grid_layout,
        test_4_mobile_data_pagination,
        test_5_mobile_workflow_object_to_dict,
        test_6_red_stage_validation_criteria,
        test_7_complete_tdd_cycle_validation
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED: {e}")
    
    print("=" * 80)
    print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL 7 CRITICAL TESTS PASSED - FEATURE-003-01-04 INTEGRATION READY")
        print("✅ Foundation validated - proceeding with feature integration is safe")
        return True
    else:
        print("⚠️  FOUNDATION VALIDATION FAILED - Fix failing tests before integration")
        return False

if __name__ == "__main__":
    success = run_all_7_critical_tests()
    exit(0 if success else 1)