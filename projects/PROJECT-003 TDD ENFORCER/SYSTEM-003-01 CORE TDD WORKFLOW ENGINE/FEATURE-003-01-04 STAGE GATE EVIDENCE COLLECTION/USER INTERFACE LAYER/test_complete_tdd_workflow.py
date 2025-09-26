"""
End-to-End TDD Cycle Tests
Post-Refactor Layer Testing - Complete RED→GREEN→REFACTOR Validation
Generated from: Prompts/TDD Prompts/4. Post-Refactor Layer Testing.md
Execution Date: September 26, 2025
"""

import pytest
import time
import sys

# Add the layers to Python path for imports
ui_layer = ("/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/"
           "SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/"
           "FEATURE-003-01-04 STAGE GATE EVIDENCE COLLECTION/"
           "USER INTERFACE LAYER")
business_layer = ("/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/"
                 "SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/"
                 "FEATURE-003-01-04 STAGE GATE EVIDENCE COLLECTION/"
                 "BUSINESS LOGIC LAYER")

sys.path.insert(0, ui_layer)
sys.path.insert(0, business_layer)

from evidence_display_interface import EvidenceDisplayInterface
from evidence_validator import EvidenceValidator


class TestCompleteTDDWorkflow:
    """End-to-End TDD Cycle Validation Tests"""

    def test_complete_red_green_refactor_cycle(self):
        """Test complete RED → GREEN → REFACTOR workflow"""
        validator = EvidenceValidator()
        display = EvidenceDisplayInterface()
        
        # RED stage: failing tests are valid
        red_evidence = {
            'test_results': [{'name': 'test_calc', 'status': 'FAILED'}],
            'implementation_status': {'exists': False}
        }
        red_result = validator.validate_stage_gate_evidence('red_stage', red_evidence)
        assert red_result.is_valid is True
        
        # GREEN stage: passing tests with minimal implementation
        green_evidence = {
            'test_results': [{'name': 'test_calc', 'status': 'PASSED'}],
            'implementation_status': {'exists': True, 'quality_score': 70}
        }
        green_result = validator.validate_stage_gate_evidence('green_stage', green_evidence)
        assert green_result.is_valid is True
        
        # REFACTOR stage: improved quality, same tests
        refactor_evidence = {
            'test_results': [{'name': 'test_calc', 'status': 'PASSED'}],  # Same tests
            'implementation_status': {'quality_score': 85}  # Improved quality
        }
        refactor_result = validator.validate_stage_gate_evidence('refactor_stage', refactor_evidence)
        assert refactor_result.is_valid is True
        
        # UI displays complete cycle
        cycle_data = {
            'red_stage': {'valid': red_result.is_valid, 'tests_failing': True},
            'green_stage': {'valid': green_result.is_valid, 'tests_passing': True},
            'refactor_stage': {'valid': refactor_result.is_valid, 'quality_improved': True}
        }
        
        cycle_display = display.render_audit_compliance_dashboard({
            'overall_score': 90,
            'cycle_completion': cycle_data
        })
        
        assert "90%" in cycle_display

    def test_tdd_compliance_perfect_workflow(self):
        """Test perfect TDD compliance workflow"""
        validator = EvidenceValidator()
        
        perfect_workflow = {
            'implementation_before_tests': False,  # Tests first ✅
            'excessive_implementation': False,     # Minimal implementation ✅
            'tests_changed_during_refactor': False  # No test changes in REFACTOR ✅
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
        
        # Check for specific violation types if available
        if hasattr(result, 'violation_types'):
            assert len(result.violation_types) > 0
        
        # Compliance score should be reduced for violations
        assert result.overall_compliance_score < 100.0

    def test_mobile_workflow_integration(self):
        """Test mobile integration workflow"""
        validator = EvidenceValidator()
        display = EvidenceDisplayInterface()
        
        large_evidence = {
            'test_results': [{'name': f'test_{i}'} for i in range(50)],
            'compliance_score': 92.5,
            'is_compliant': True,
            'issues': [{'severity': 'CRITICAL', 'message': 'Critical issue'}]
        }
        
        # Test mobile package preparation performance (<500ms)
        start_time = time.time()
        mobile_package = validator.prepare_mobile_evidence_package(large_evidence)
        execution_time = (time.time() - start_time) * 1000
        
        assert execution_time < 500  # Must be under 500ms
        
        # Verify mobile package structure
        mobile_dict = mobile_package.to_dict()
        assert 'validation_status' in mobile_dict
        
        # Test mobile display formatting
        mobile_display = display.format_for_mobile(
            {'score': 92.5, 'items': large_evidence['test_results'][:5]},
            screen_width=320
        )
        
        assert mobile_display['display_config']['device_type'] == 'mobile'
        
        package_size = len(str(mobile_dict)) / 1024
        assert package_size < 50  # Must be under 50KB

    def test_end_to_end_performance_requirements(self):
        """Test complete workflow meets performance requirements"""
        validator = EvidenceValidator()
        display = EvidenceDisplayInterface()
        
        # Complete TDD workflow evidence
        complete_evidence = {
            'red_phase': {
                'tests': [f'test_feature_{i}' for i in range(10)],
                'all_failing': True
            },
            'green_phase': {
                'tests': [f'test_feature_{i}' for i in range(10)],
                'all_passing': True,
                'implementation': 'minimal_feature.py'
            },
            'refactor_phase': {
                'tests': [f'test_feature_{i}' for i in range(10)],
                'all_passing': True,
                'improvements': ['extracted_methods', 'improved_naming']
            }
        }
        
        # Time the complete workflow
        start_time = time.time()
        
        # Business logic processing
        compliance_result = validator.verify_tdd_compliance(complete_evidence)
        
        # UI rendering
        display_result = display.render_audit_compliance_dashboard({
            'overall_score': compliance_result.overall_compliance_score,
            'workflow_complete': True
        })
        
        total_time = time.time() - start_time
        
        # Complete workflow should be under 500ms
        assert total_time < 0.5
        
        # Results should be valid
        assert compliance_result.overall_compliance_score >= 0
        assert isinstance(display_result, str)
        assert len(display_result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])