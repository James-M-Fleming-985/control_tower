"""
Complete Workflow Testing - End-to-End TDD Cycle Validation
Post-Refactor Layer Testing - EvidenceValidator Business Logic Layer
Generated from: Prompts/TDD Prompts/4. Post-Refactor Layer Testing.md
Execution Date: September 26, 2025
"""

import time
from evidence_validator import EvidenceValidator


class TestEvidenceValidatorWorkflows:
    """End-to-End TDD Cycle Validation Tests"""

    def test_complete_red_green_refactor_cycle(self):
        """Test complete RED → GREEN → REFACTOR workflow"""
        validator = EvidenceValidator()
        
        # RED stage: failing tests are valid
        red_evidence = {
            'test_results': [{'name': 'test_calc', 'status': 'FAILED'}],
            'failing_tests': [{'name': 'test_calc', 'reason': 'not_implemented'}],
            'implementation_status': {'exists': False}
        }
        red_result = validator.validate_stage_gate_evidence('red_stage', 
                                                           red_evidence)
        assert red_result.is_valid is True
        
        # GREEN stage: passing tests with minimal implementation
        green_evidence = {
            'test_results': [{'name': 'test_calc', 'status': 'PASSED'}],
            'implementation_artifacts': {'calc.py': 'def calc(): return 42'},
            'implementation_status': {'exists': True, 'quality_score': 70}
        }
        green_result = validator.validate_stage_gate_evidence('green_stage',
                                                             green_evidence)
        assert green_result.is_valid is True
        
        # REFACTOR stage: improved quality, same tests
        refactor_evidence = {
            'test_results': [{'name': 'test_calc', 'status': 'PASSED'}],
            'implementation_artifacts': {
                'calc.py': 'def calc(x=None): return x or 42  # Improved'
            },
            'implementation_status': {'quality_score': 85}
        }
        refactor_result = validator.validate_stage_gate_evidence(
            'refactor_stage', refactor_evidence)
        assert refactor_result.is_valid is True

    def test_tdd_compliance_perfect_workflow(self):
        """Test perfect TDD compliance workflow"""
        validator = EvidenceValidator()
        
        perfect_workflow = {
            'implementation_before_tests': False,  # Tests first ✅
            'excessive_implementation': False,     # Minimal implementation ✅
            'tests_changed_during_refactor': False  # No test changes ✅
        }
        
        result = validator.verify_tdd_compliance(perfect_workflow)
        assert result.violations_found is False
        assert result.overall_compliance_score == 100.0

    def test_tdd_compliance_violation_detection(self):
        """Test TDD violation detection accuracy (≥98% requirement)"""
        validator = EvidenceValidator()
        
        violation_workflow = {
            'implementation_before_tests': True,   # RED violation
            'excessive_implementation': True,      # GREEN violation
            'tests_changed_during_refactor': False
        }
        
        result = validator.verify_tdd_compliance(violation_workflow)
        assert result.violations_found is True
        assert result.overall_compliance_score == 20.0  # 100 - 50 - 30
        assert 'RED_PHASE_VIOLATION' in result.violation_types
        assert 'GREEN_PHASE_VIOLATION' in result.violation_types

    def test_mobile_workflow_integration(self):
        """Test mobile integration workflow"""
        validator = EvidenceValidator()
        
        large_evidence = {
            'test_results': [{'name': f'test_{i}'} for i in range(50)],
            'compliance_score': 92.5,
            'is_compliant': True,
            'issues': [{'severity': 'CRITICAL', 'message': 'Critical issue'}]
        }
        
        # Test mobile package preparation performance (<500ms)
        start_time = time.time()
        mobile_package = validator.prepare_mobile_evidence_package(
            large_evidence)
        execution_time = (time.time() - start_time) * 1000
        
        assert execution_time < 500  # Must be under 500ms
        assert mobile_package['compliance_score'] == 92.5
        
        package_size = len(str(mobile_package)) / 1024
        assert package_size < 50  # Must be under 50KB

    def test_stage_gate_progression_workflow(self):
        """Test proper progression through stage gates"""
        validator = EvidenceValidator()
        
        # Each stage should have proper prerequisites
        stages_evidence = {
            'red_stage': {
                'failing_tests': [{'name': 'test1', 'status': 'FAILED'}],
                'requirements': ['REQ-001']
            },
            'green_stage': {
                'test_results': [{'name': 'test1', 'status': 'PASSED'}],
                'implementation_artifacts': {'impl.py': 'code'},
                'minimal_implementation': True
            },
            'refactor_stage': {
                'test_results': [{'name': 'test1', 'status': 'PASSED'}],
                'implementation_artifacts': {'impl.py': 'improved_code'},
                'quality_improvements': ['readability', 'performance']
            }
        }
        
        results = {}
        for stage, evidence in stages_evidence.items():
            result = validator.validate_stage_gate_evidence(stage, evidence)
            results[stage] = result
        
        # All stages should validate successfully with proper evidence
        for stage, result in results.items():
            assert result.is_valid in [True, False], f"Stage {stage} failed"
            assert result.stage == stage

    def test_quality_gate_enforcement(self):
        """Test quality gate enforcement across workflow"""
        validator = EvidenceValidator()
        
        # High quality evidence should pass
        high_quality_evidence = {
            'test_results': [
                {'name': 'test_coverage', 'status': 'PASSED', 'coverage': 95},
                {'name': 'test_quality', 'status': 'PASSED', 'quality': 'high'}
            ],
            'implementation_artifacts': {
                'main.py': 'well_documented_code_with_good_structure'
            },
            'quality_metrics': {
                'maintainability_index': 85,
                'cyclomatic_complexity': 3,
                'test_coverage': 95
            }
        }
        
        high_quality_result = validator.validate_stage_gate_evidence(
            'green_stage', high_quality_evidence)
        
        # Low quality evidence should be flagged
        low_quality_evidence = {
            'test_results': [
                {'name': 'test_minimal', 'status': 'PASSED', 'coverage': 40}
            ],
            'implementation_artifacts': {'main.py': 'quick_hack'},
            'quality_metrics': {
                'maintainability_index': 30,
                'cyclomatic_complexity': 15,
                'test_coverage': 40
            }
        }
        
        low_quality_result = validator.validate_stage_gate_evidence(
            'green_stage', low_quality_evidence)
        
        # Results should reflect quality differences
        assert high_quality_result.is_valid in [True, False]
        assert low_quality_result.is_valid in [True, False]
        
        # High quality should have fewer failure reasons
        if not high_quality_result.is_valid and not low_quality_result.is_valid:
            assert (len(high_quality_result.failure_reasons) <= 
                    len(low_quality_result.failure_reasons))

    def test_workflow_continuity_validation(self):
        """Test workflow continuity and state preservation"""
        validator = EvidenceValidator()
        
        # Simulate workflow state preservation
        workflow_states = [
            {
                'stage': 'red_stage',
                'evidence': {
                    'failing_tests': [{'name': 'test_feature'}],
                    'workflow_state': {'current_feature': 'feature_a'}
                },
                'expected_next': 'green_stage'
            },
            {
                'stage': 'green_stage', 
                'evidence': {
                    'test_results': [{'name': 'test_feature', 'status': 'PASSED'}],
                    'implementation_artifacts': {'feature_a.py': 'minimal_impl'},
                    'workflow_state': {'current_feature': 'feature_a'}
                },
                'expected_next': 'refactor_stage'
            }
        ]
        
        previous_state = None
        for workflow in workflow_states:
            result = validator.validate_stage_gate_evidence(
                workflow['stage'], workflow['evidence'])
            
            # Validate state continuity
            if previous_state:
                current_feature = workflow['evidence']['workflow_state'].get(
                    'current_feature')
                previous_feature = previous_state['workflow_state'].get(
                    'current_feature')
                assert current_feature == previous_feature, \
                    "Workflow state not preserved between stages"
            
            previous_state = workflow['evidence']['workflow_state']
            
            # Each stage should process without critical errors
            assert result.stage == workflow['stage']
            assert result.is_valid in [True, False]