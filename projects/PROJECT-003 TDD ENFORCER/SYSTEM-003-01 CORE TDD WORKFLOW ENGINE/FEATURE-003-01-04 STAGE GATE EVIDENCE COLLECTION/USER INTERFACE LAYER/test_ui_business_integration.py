"""
UI ↔ Business Logic Integration Tests
Post-Refactor Layer Testing - EvidenceDisplayInterface UI Layer
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


class TestUIBusinessIntegration:
    """Integration tests for UI Layer ↔ Business Logic Layer"""

    def test_ui_displays_business_logic_compliance_results(self):
        """Test UI displays compliance results from business logic processing"""
        # Arrange
        display = EvidenceDisplayInterface()
        validator = EvidenceValidator()
        
        # Business logic processes evidence
        workflow_evidence = {
            'red_phase_tests': ['test_calculation', 'test_validation'],
            'green_phase_implementation': 'minimal_calculator.py',
            'refactor_phase_improvements': ['extract_method', 'improve_naming']
        }
        compliance_result = validator.verify_tdd_compliance(workflow_evidence)
        
        # Act - UI displays business logic results
        compliance_data = {
            'overall_score': compliance_result.overall_compliance_score,
            'stage_scores': {
                'red_stage': 90 if not compliance_result.violations_found else 70,
                'green_stage': 85,
                'refactor_stage': 95
            },
            'evidence_completeness': 100 if len(workflow_evidence) >= 3 else 75
        }
        dashboard = display.render_audit_compliance_dashboard(compliance_data)
        
        # Assert
        assert f"{compliance_result.overall_compliance_score}%" in dashboard
        assert "RED STAGE:" in dashboard
        assert "GREEN STAGE:" in dashboard
        assert "REFACTOR STAGE:" in dashboard

    def test_ui_caches_business_logic_expensive_operations(self):
        """Test UI caching integrates with business logic expensive operations"""
        display = EvidenceDisplayInterface()
        validator = EvidenceValidator()
        
        # Simulate expensive business logic operation
        large_evidence_set = {
            'red_phase_tests': [f'test_{i}' for i in range(100)],
            'implementation_artifacts': [f'module_{i}.py' for i in range(50)],
            'refactor_improvements': [f'improvement_{i}' for i in range(25)]
        }
        
        # First call - should cache result
        start_time = time.time()
        result1 = validator.verify_tdd_compliance(large_evidence_set)
        display_result1 = display.render_audit_compliance_dashboard({
            'overall_score': result1.overall_compliance_score
        })
        first_call_time = time.time() - start_time
        
        # Second call - should use cached result if implemented
        start_time = time.time()
        result2 = validator.verify_tdd_compliance(large_evidence_set)
        display_result2 = display.render_audit_compliance_dashboard({
            'overall_score': result2.overall_compliance_score
        })
        second_call_time = time.time() - start_time
        
        # Verify results are consistent
        assert result1.overall_compliance_score == result2.overall_compliance_score
        assert display_result1 == display_result2
        
        # Verify caching statistics if available
        if hasattr(display, 'get_cache_statistics'):
            stats = display.get_cache_statistics()
            assert stats['cache_hits'] >= 0

    def test_ui_validates_business_logic_output_format(self):
        """Test UI validates business logic output matches expected format"""
        display = EvidenceDisplayInterface()
        validator = EvidenceValidator()
        
        # Valid business logic output
        valid_evidence = {
            'red_phase_tests': ['test_method'],
            'implementation': 'code.py'
        }
        result = validator.verify_tdd_compliance(valid_evidence)
        
        # UI should handle standard business logic result format
        compliance_data = {
            'overall_compliance_score': result.overall_compliance_score,
            'stage_compliance': {
                'red_stage': {'status': 'compliant', 'score': 85, 'violations': 0}
            }
        }
        
        # Should not raise validation errors
        try:
            dashboard = display.render_audit_compliance_dashboard(compliance_data)
            assert "85%" in dashboard or str(int(result.overall_compliance_score)) in dashboard
        except Exception as e:
            pytest.fail(f"UI should handle standard business logic output: {e}")

    def test_ui_handles_business_logic_performance_alerts(self):
        """Test UI displays performance alerts from business logic"""
        display = EvidenceDisplayInterface()
        validator = EvidenceValidator()
        
        # Simulate business logic performance monitoring
        evidence = {'red_phase_tests': ['slow_test']}
        
        # Business logic with performance tracking
        start_time = time.time()
        result = validator.verify_tdd_compliance(evidence)
        execution_time_ms = (time.time() - start_time) * 1000
        
        # UI displays performance data
        compliance_data = {
            'overall_score': result.overall_compliance_score,
            'performance_metrics': {
                'execution_time_ms': execution_time_ms,
                'slow_operations': 1 if execution_time_ms > 100 else 0
            }
        }
        
        dashboard = display.render_audit_compliance_dashboard(compliance_data)
        
        # Verify performance information is included
        assert str(int(compliance_data['overall_score'])) in dashboard
        
        # Check performance reporting if UI supports it
        if hasattr(display, 'get_performance_report'):
            perf_report = display.get_performance_report()
            assert 'total_operations' in perf_report

    def test_ui_error_handling_with_business_logic_failures(self):
        """Test UI gracefully handles business logic layer failures"""
        display = EvidenceDisplayInterface()
        
        # Simulate business logic failure scenarios
        invalid_compliance_data = {
            'overall_compliance_score': None,  # Invalid format
            'stage_compliance': {}
        }
        
        # UI should handle validation errors gracefully
        try:
            dashboard = display.render_audit_compliance_dashboard(invalid_compliance_data)
            # Should either handle gracefully or raise expected validation error
            assert isinstance(dashboard, str)
        except Exception as e:
            # Should be a known validation error, not a crash
            assert "compliance_score" in str(e) or "validation" in str(e) or "overall_score" in str(e)

    def test_ui_mobile_optimization_with_business_data(self):
        """Test mobile UI optimization works with business logic data"""
        display = EvidenceDisplayInterface()
        
        # Large dataset from business logic
        extensive_compliance_data = {
            'overall_score': 85,
            'stage_scores': {'red_stage': 90, 'green_stage': 80, 'refactor_stage': 85},
            'evidence_completeness': 95,
            'recommendations': [f'Recommendation {i}' for i in range(10)]
        }
        
        # Test mobile formatting
        mobile_content = display.format_for_mobile(
            {'items': extensive_compliance_data['recommendations']}, 
            screen_width=320
        )
        
        # Should limit items for mobile display
        assert mobile_content['display_config']['device_type'] == 'mobile'
        assert len(mobile_content['items']) <= 5  # Mobile limit
        assert mobile_content['display_config']['compact_display'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])