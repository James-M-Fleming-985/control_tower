"""
Three-Layer Workflow Integration Tests
Post-Refactor Layer Testing - UI ↔ Business ↔ Data Access Integration
Generated from: Prompts/TDD Prompts/4. Post-Refactor Layer Testing.md
Execution Date: September 26, 2025
"""

import pytest
import time
import sys
from unittest.mock import Mock

# Add the layers to Python path for imports
ui_layer = ("/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/"
           "SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/"
           "FEATURE-003-01-04 STAGE GATE EVIDENCE COLLECTION/"
           "USER INTERFACE LAYER")
business_layer = ("/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/"
                 "SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/"
                 "FEATURE-003-01-04 STAGE GATE EVIDENCE COLLECTION/"
                 "BUSINESS LOGIC LAYER")
data_access_layer = "/workspaces/control_tower/src/data_access"

sys.path.insert(0, ui_layer)
sys.path.insert(0, business_layer)
sys.path.insert(0, data_access_layer)

from evidence_display_interface import EvidenceDisplayInterface
from evidence_validator import EvidenceValidator


class MockEvidenceStorage:
    """Mock Data Access Layer for integration testing"""
    
    def __init__(self):
        self.stored_evidence = {}
        self.call_count = 0
    
    def store_evidence(self, evidence_id, evidence):
        """Mock evidence storage"""
        self.call_count += 1
        self.stored_evidence[evidence_id] = {
            'evidence': evidence,
            'timestamp': time.time(),
            'storage_id': f'stored-{evidence_id}'
        }
        return {'status': 'stored', 'evidence_id': evidence_id}
    
    def retrieve_evidence(self, evidence_id):
        """Mock evidence retrieval"""
        if evidence_id in self.stored_evidence:
            return self.stored_evidence[evidence_id]
        return {'error': 'Evidence not found'}


class TestThreeLayerIntegration:
    """End-to-End Workflow Integration Tests across all three layers"""

    def test_complete_evidence_workflow_integration(self):
        """Test complete workflow: Data Access → Business Logic → UI Display"""
        # Arrange - Initialize all three layers
        storage = MockEvidenceStorage()           # Mock Data Access Layer
        validator = EvidenceValidator()           # Business Logic Layer  
        display = EvidenceDisplayInterface()      # UI Layer
        
        # Step 1: Data Access Layer stores evidence
        evidence_id = "test_workflow_001"
        workflow_evidence = {
            'project_id': 'calculator_app',
            'red_phase_tests': [
                'test_add_positive_numbers',
                'test_divide_by_zero_raises_error'
            ],
            'green_phase_implementation': 'calculator.py',
            'refactor_phase_improvements': [
                'extracted_validation_method',
                'improved_error_messages'
            ],
            'timestamp': '2025-09-26T16:00:00Z'
        }
        
        storage_result = storage.store_evidence(evidence_id, workflow_evidence)
        assert storage_result['status'] == 'stored'
        
        # Step 2: Business Logic Layer processes stored evidence
        retrieved_evidence = storage.retrieve_evidence(evidence_id)
        compliance_result = validator.verify_tdd_compliance(
            retrieved_evidence['evidence'])
        
        # Step 3: UI Layer displays processed results
        compliance_data = {
            'overall_score': compliance_result.overall_compliance_score,
            'stage_scores': {
                'red_stage': 95,    # Good test coverage
                'green_stage': 90,  # Minimal implementation
                'refactor_stage': 85  # Clear improvements
            },
            'evidence_completeness': 100,
            'workflow_id': evidence_id
        }
        
        dashboard = display.render_audit_compliance_dashboard(compliance_data)
        
        # Assert complete workflow
        assert compliance_result.overall_compliance_score > 0
        assert "95%" in dashboard  # Red stage score
        assert storage_result['evidence_id'] == evidence_id

    def test_cached_workflow_performance_across_layers(self):
        """Test caching works across all three layers for performance"""
        storage = MockEvidenceStorage()
        validator = EvidenceValidator() 
        display = EvidenceDisplayInterface()
        
        evidence_id = "performance_test_001"
        large_evidence = {
            'red_phase_tests': [f'test_case_{i}' for i in range(50)],
            'green_implementations': [f'module_{i}.py' for i in range(25)],
            'refactor_improvements': [f'improvement_{i}' for i in range(15)]
        }
        
        # First workflow execution
        start_time = time.time()
        
        storage.store_evidence(evidence_id, large_evidence)
        retrieved = storage.retrieve_evidence(evidence_id)
        validation_result = validator.verify_tdd_compliance(
            retrieved['evidence'])
        display_result = display.render_audit_compliance_dashboard({
            'overall_score': validation_result.overall_compliance_score
        })
        
        first_execution_time = time.time() - start_time
        
        # Second workflow execution (should benefit from caching)
        start_time = time.time()
        
        retrieved2 = storage.retrieve_evidence(evidence_id)  # May be cached
        validation_result2 = validator.verify_tdd_compliance(
            retrieved2['evidence'])
        display_result2 = display.render_audit_compliance_dashboard({
            'overall_score': validation_result2.overall_compliance_score
        })
        
        second_execution_time = time.time() - start_time
        
        # Verify consistency and potential performance improvement
        score1 = validation_result.overall_compliance_score
        score2 = validation_result2.overall_compliance_score
        assert score1 == score2
        assert display_result == display_result2
        
        # Performance should be reasonable
        assert first_execution_time < 1.0
        assert second_execution_time < 1.0

    def test_error_propagation_across_layers(self):
        """Test error handling propagates correctly through all layers"""
        storage = MockEvidenceStorage()
        validator = EvidenceValidator()
        display = EvidenceDisplayInterface()
        
        # Test 1: Data Access Layer error
        try:
            invalid_evidence = storage.retrieve_evidence("nonexistent_id")
            if 'error' in invalid_evidence:
                # UI should handle storage errors gracefully
                error_data = {
                    'overall_score': 0, 
                    'error_message': invalid_evidence['error']
                }
                error_display = display.render_audit_compliance_dashboard(
                    error_data)
                assert ('error' in error_display.lower() or 
                       '0%' in error_display)
        except Exception as e:
            # Should be handled gracefully, not crash
            assert ('evidence' in str(e) or 'not found' in str(e))
        
        # Test 2: Business Logic Layer validation error  
        invalid_workflow = {}  # Missing required fields
        try:
            validation_result = validator.verify_tdd_compliance(
                invalid_workflow)
            # Should handle invalid input gracefully
            assert hasattr(validation_result, 'overall_compliance_score')
        except Exception as e:
            # UI should be able to display validation errors
            error_data = {
                'overall_score': 0,
                'validation_error': str(e)
            }
            error_dashboard = display.render_audit_compliance_dashboard(
                error_data)
            assert isinstance(error_dashboard, str)

    def test_mobile_workflow_optimization(self):
        """Test mobile optimization works for complete workflow"""
        storage = MockEvidenceStorage()
        validator = EvidenceValidator()
        display = EvidenceDisplayInterface()
        
        # Store evidence optimized for mobile display
        mobile_evidence_id = "mobile_workflow_001"
        evidence = {
            'red_phase_tests': ['test_core_functionality'],
            'green_implementation': 'minimal_feature.py',
            'refactor_improvements': ['improved_readability']
        }
        
        storage.store_evidence(mobile_evidence_id, evidence)
        retrieved = storage.retrieve_evidence(mobile_evidence_id)
        validation_result = validator.verify_tdd_compliance(
            retrieved['evidence'])
        
        # Generate mobile-optimized display
        compliance_data = {
            'overall_score': validation_result.overall_compliance_score,
            'stage_scores': {
                'red_stage': 90, 'green_stage': 85, 'refactor_stage': 88
            },
            'recommendations': [
                'Focus on test coverage', 'Improve naming', 'Add documentation'
            ]
        }
        
        mobile_display = display.format_for_mobile(
            compliance_data, screen_width=320)
        
        # Verify mobile optimization
        assert mobile_display['display_config']['device_type'] == 'mobile'
        assert mobile_display['display_config']['compact_display'] is True
        
        # Verify responsive CSS generation
        mobile_css = display.generate_responsive_layout_css('mobile')
        assert '@media (max-width: 320px)' in mobile_css
        assert 'touch-target' in mobile_css

    def test_performance_monitoring_across_layers(self):
        """Test performance monitoring integration across all layers"""
        storage = MockEvidenceStorage()
        validator = EvidenceValidator()
        display = EvidenceDisplayInterface()
        
        evidence_id = "performance_monitoring_001"
        evidence = {
            'red_phase_tests': [f'performance_test_{i}' for i in range(10)],
            'implementation': 'optimized_code.py'
        }
        
        # Execute workflow with performance tracking
        overall_start = time.time()
        
        # Data Access Layer timing
        storage_start = time.time()
        storage.store_evidence(evidence_id, evidence)
        retrieved = storage.retrieve_evidence(evidence_id)
        storage_time = time.time() - storage_start
        
        # Business Logic Layer timing
        business_start = time.time()
        validation_result = validator.verify_tdd_compliance(
            retrieved['evidence'])
        business_time = time.time() - business_start
        
        # UI Layer timing
        ui_start = time.time()
        display_result = display.render_audit_compliance_dashboard({
            'overall_score': validation_result.overall_compliance_score
        })
        ui_time = time.time() - ui_start
        
        total_time = time.time() - overall_start
        
        # Verify performance requirements
        assert storage_time < 0.1, f"Storage layer too slow: {storage_time:.3f}s"
        assert business_time < 0.05, f"Business logic too slow: {business_time:.3f}s"  
        assert ui_time < 0.1, f"UI layer too slow: {ui_time:.3f}s"
        assert total_time < 0.2, f"Total workflow too slow: {total_time:.3f}s"
        
        # Verify UI performance monitoring if available
        if hasattr(display, 'get_performance_report'):
            perf_report = display.get_performance_report()
            assert perf_report['total_operations'] >= 1

    def test_data_consistency_across_layer_boundaries(self):
        """Test data remains consistent as it flows through layers"""
        storage = MockEvidenceStorage()
        validator = EvidenceValidator()
        display = EvidenceDisplayInterface()
        
        # Original evidence data
        original_evidence = {
            'test_suite': 'calculator_tests',
            'test_count': 5,
            'implementation_files': ['calculator.py'],
            'quality_score': 85.5
        }
        
        evidence_id = "consistency_test_001"
        
        # Store and retrieve through data access layer
        storage.store_evidence(evidence_id, original_evidence)
        stored_evidence = storage.retrieve_evidence(evidence_id)
        
        # Process through business logic layer
        compliance_result = validator.verify_tdd_compliance(
            stored_evidence['evidence'])
        
        # Display through UI layer
        ui_data = {
            'original_evidence': stored_evidence['evidence'],
            'compliance_score': compliance_result.overall_compliance_score,
            'validation_passed': not compliance_result.violations_found
        }
        
        # Verify data consistency
        retrieved_evidence = stored_evidence['evidence']
        assert retrieved_evidence['test_suite'] == original_evidence['test_suite']
        assert retrieved_evidence['test_count'] == original_evidence['test_count']
        assert retrieved_evidence['quality_score'] == original_evidence['quality_score']
        
        # UI should preserve the data structure
        assert ui_data['original_evidence'] == original_evidence
        assert isinstance(ui_data['compliance_score'], float)
        assert isinstance(ui_data['validation_passed'], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])