"""
FEATURE-003-01-04 Integration Test Suite
Tests the integration of enhanced components with the Stage Gate Evidence Collection feature.
Builds on the validated 7 critical foundation tests.
"""
import sys
import os
from pathlib import Path

# Add workspace root to path for imports
workspace_root = Path("/workspaces/control_tower")
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

def test_compliance_reporter_feature_integration():
    """Test ComplianceReporter integration with FEATURE-003-01-04"""
    from compliance_reporter import ComplianceReporter
    
    # Initialize with configuration
    reporter = ComplianceReporter()
    
    # Test integration with stage gate evidence
    stage_gate_evidence = {
        'compliance_score': 92.5,
        'requirements_passed': 18,
        'requirements_total': 20,
        'stage_gates': {
            'red_stage': 'complete',
            'green_stage': 'complete', 
            'refactor_stage': 'in_progress'
        }
    }
    
    report = reporter.generate_compliance_report(stage_gate_evidence)
    
    assert report['overall_compliance_score'] == 92.5
    assert report['compliance_level'] == 'GOOD'
    assert 'generation_time_ms' in report
    assert report['operation_number'] > 0
    
    print("✅ ComplianceReporter integrates successfully with FEATURE-003-01-04")
    return True

def test_evidence_display_feature_integration():
    """Test EvidenceDisplayInterface integration with stage gate workflow"""
    from evidence_display_interface import EvidenceDisplayInterface
    
    interface = EvidenceDisplayInterface()
    
    # Stage gate evidence data
    stage_evidence = {
        'compliance_data': [
            {'stage': 'red', 'score': 95, 'tests': 5},
            {'stage': 'green', 'score': 88, 'tests': 5}, 
            {'stage': 'refactor', 'score': 92, 'tests': 5}
        ],
        'test_results': [f'test_result_{i}' for i in range(15)],
        'metrics': {
            'overall_score': 91.7,
            'stage_completion': '100%'
        }
    }
    
    # Test mobile optimization for stage gate
    mobile_display = interface.create_mobile_optimized_display(stage_evidence)
    
    assert mobile_display['display_config']['screen_width'] == 320
    assert len(mobile_display['compliance_data']) <= 10
    assert len(mobile_display['test_results']) <= 10
    assert mobile_display['metrics']['overall_score'] == 91.7
    
    print("✅ EvidenceDisplayInterface integrates with stage gate workflow")
    return True

def test_evidence_validator_stage_gate_integration():
    """Test EvidenceValidator integration with stage gate validation"""
    from evidence_validator import EvidenceValidator
    
    validator = EvidenceValidator()
    
    # Stage gate TDD cycle evidence
    stage_gate_cycle = [
        {
            'stage': 'red',
            'tests_failing': 3,
            'stage_gate': 'RED_PHASE_COMPLETE'
        },
        {
            'stage': 'green', 
            'tests_passing': 3,
            'implementation': 'complete',
            'stage_gate': 'GREEN_PHASE_COMPLETE'
        },
        {
            'stage': 'refactor',
            'code_quality': 'improved',
            'stage_gate': 'REFACTOR_PHASE_COMPLETE'
        }
    ]
    
    # Validate complete stage gate cycle
    validation_result = validator.validate_complete_tdd_cycle(stage_gate_cycle)
    
    assert validation_result.is_valid == True
    assert validation_result.cycle_complete == True
    assert len(validation_result.completed_phases) == 3
    assert 'RED' in validation_result.completed_phases
    assert 'GREEN' in validation_result.completed_phases
    assert 'REFACTOR' in validation_result.completed_phases
    
    print("✅ EvidenceValidator integrates with stage gate TDD validation")
    return True

def test_cross_component_stage_gate_workflow():
    """Test complete workflow using all 3 components with stage gate evidence"""
    from compliance_reporter import ComplianceReporter
    from evidence_display_interface import EvidenceDisplayInterface
    from evidence_validator import EvidenceValidator
    
    # Initialize all components
    reporter = ComplianceReporter()
    interface = EvidenceDisplayInterface()
    validator = EvidenceValidator()
    
    # Stage gate workflow data
    workflow_evidence = {
        'project': 'FEATURE-003-01-04',
        'stage_gate_evidence': [
            {'stage': 'red', 'tests_failing': 2},
            {'stage': 'green', 'tests_passing': 2, 'implementation': 'complete'},
            {'stage': 'refactor', 'code_quality': 'improved'}
        ],
        'compliance_score': 89.5,
        'requirements_passed': 17,
        'requirements_total': 19
    }
    
    # 1. Validate TDD cycle
    cycle_validation = validator.validate_complete_tdd_cycle(
        workflow_evidence['stage_gate_evidence']
    )
    assert cycle_validation.is_valid
    
    # 2. Generate compliance report
    compliance_report = reporter.generate_compliance_report(workflow_evidence)
    assert compliance_report['overall_compliance_score'] == 89.5
    
    # 3. Create mobile display
    mobile_display = interface.create_mobile_optimized_display({
        'compliance_data': [compliance_report],
        'test_results': workflow_evidence['stage_gate_evidence']
    })
    assert mobile_display['display_config']['device_type'] == 'mobile'
    
    print("✅ Complete cross-component stage gate workflow successful")
    return True

def test_performance_integration_requirements():
    """Test performance requirements for integrated components"""
    import time
    from compliance_reporter import ComplianceReporter
    from evidence_display_interface import EvidenceDisplayInterface
    
    reporter = ComplianceReporter()
    interface = EvidenceDisplayInterface()
    
    # Performance test data
    large_evidence = {
        'compliance_score': 85.0,
        'requirements_passed': 42,
        'requirements_total': 50,
        'compliance_data': [{'item': i} for i in range(100)],
        'test_results': [f'result_{i}' for i in range(200)]
    }
    
    # Test compliance reporting performance
    start_time = time.time()
    report = reporter.generate_compliance_report(large_evidence)
    report_time = (time.time() - start_time) * 1000
    
    assert report_time < 50.0  # Should complete in under 50ms
    assert 'generation_time_ms' in report
    assert report['generation_time_ms'] < 10.0  # Internal tracking under 10ms
    
    # Test mobile display performance with pagination
    start_time = time.time()
    mobile_display = interface.create_mobile_optimized_display(large_evidence)
    display_time = (time.time() - start_time) * 1000
    
    assert display_time < 25.0  # Should complete in under 25ms
    assert len(mobile_display['compliance_data']) <= 10  # Pagination working
    assert len(mobile_display['test_results']) <= 10
    
    print(f"✅ Performance requirements met: Report {report_time:.2f}ms, Display {display_time:.2f}ms")
    return True

def run_feature_integration_tests():
    """Run all FEATURE-003-01-04 integration tests"""
    print("🧪 Running FEATURE-003-01-04 Integration Tests...")
    print("📁 Building on validated 7 critical foundation tests")
    print("=" * 80)
    
    tests = [
        test_compliance_reporter_feature_integration,
        test_evidence_display_feature_integration,
        test_evidence_validator_stage_gate_integration,
        test_cross_component_stage_gate_workflow,
        test_performance_integration_requirements
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
    print(f"📊 INTEGRATION RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 FEATURE-003-01-04 INTEGRATION SUCCESSFUL")
        print("✅ All components integrate successfully with stage gate evidence collection")
        return True
    else:
        print("⚠️  INTEGRATION ISSUES DETECTED - Review failing tests")
        return False

if __name__ == "__main__":
    success = run_feature_integration_tests()
    exit(0 if success else 1)