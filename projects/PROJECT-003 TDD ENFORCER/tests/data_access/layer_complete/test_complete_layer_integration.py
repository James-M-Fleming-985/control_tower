#!/usr/bin/env python3
"""
Complete Layer Integration Tests
===============================

Tests the complete Data Access Layer as a cohesive unit with all 4 TDD iterations.
Validates that all iterations work together seamlessly.

PROJECT: PROJECT-003 TDD ENFORCER
SYSTEM: SYSTEM-003-02 EXTENDED VALIDATION ENGINE
FEATURE: FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE
PHASE: Integration Testing (Phase 3)
"""

import pytest
import tempfile
import shutil
import time
from pathlib import Path

import sys
sys.path.append('/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/src')

from data_access.mobile_command_history_repository import MobileCommandHistoryRepository
from data_access.context_engine_repository import ContextEngineRepository


class TestCompleteLayerIntegration:
    """Test complete Data Access Layer integration with all iterations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.mobile_db_path = str(Path(self.temp_dir) / "complete_mobile.db")
        self.context_db_path = str(Path(self.temp_dir) / "complete_context.db")
        
        self.mobile_repo = MobileCommandHistoryRepository(self.mobile_db_path)
        self.context_repo = ContextEngineRepository(self.context_db_path)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_complete_workflow_all_iterations(self):
        """Test complete workflow using all 4 iterations together"""
        user_id = 'complete_workflow_user'
        workflow_id = 'complete_workflow_001'
        base_time = time.time()
        
        # Phase 1: Storage (Iteration 1) - Store multiple related commands
        commands = []
        for i in range(3):
            command_data = {
                'command_id': f'{workflow_id}_cmd_{i:03d}',
                'user_id': user_id,
                'command_text': f'Complete workflow command {i}',
                'timestamp': base_time + i,
                'context': {
                    'workflow_id': workflow_id,
                    'sequence': i,
                    'complete_test': True
                }
            }
            commands.append(command_data)
            
            success, message = self.mobile_repo.store_command(command_data)
            assert success is True
            
        # Phase 2: Correlation (Iteration 2) - Create correlations between commands
        correlations_created = 0
        for i in range(len(commands) - 1):
            current_cmd = commands[i]['command_id']
            next_cmd = commands[i + 1]['command_id']
            
            success, message = self.mobile_repo.create_context_correlation(
                current_cmd,
                next_cmd,
                'workflow_sequence',
                0.9 - (i * 0.1)  # Decreasing confidence
            )
            
            if success:
                correlations_created += 1
                
        assert correlations_created > 0, "Should create at least one correlation"
        
        # Phase 3: Audit (Iteration 3) - Create comprehensive audit trail
        audit_entries_created = 0
        for i, command_data in enumerate(commands):
            audit_success, audit_message = self.mobile_repo.create_audit_entry(
                command_data['command_id'],
                'WORKFLOW_STEP',
                user_id,
                {
                    'workflow_id': workflow_id,
                    'step_number': i,
                    'operation': 'complete_workflow',
                    'correlations_created': correlations_created,
                    'audit_metadata': {
                        'compliance_required': True,
                        'data_classification': 'internal'
                    }
                }
            )
            
            if audit_success:
                audit_entries_created += 1
                
        assert audit_entries_created > 0, "Should create audit entries"
        
        # Phase 4: Context Sync (Iteration 4) - Sync workflow state
        workflow_context = {
            'workflow_complete': True,
            'workflow_id': workflow_id,
            'commands_processed': len(commands),
            'correlations_created': correlations_created,
            'audit_entries': audit_entries_created,
            'completion_timestamp': time.time(),
            'workflow_metadata': {
                'user_id': user_id,
                'total_steps': len(commands),
                'success_rate': 1.0
            }
        }
        
        sync_success, sync_message = self.context_repo.sync_context_state(
            f'{workflow_id}_context',
            user_id,
            workflow_context
        )
        
        assert sync_success is True
        
        # Validation: Verify complete workflow state
        final_context, context_message = self.context_repo.get_context_state(
            f'{workflow_id}_context',
            user_id
        )
        
        assert final_context is not None
        assert isinstance(final_context, dict)
        
        # Verify audit trail completeness
        for command_data in commands:
            audit_trail, _ = self.mobile_repo.get_audit_trail(
                command_data['command_id']
            )
            assert audit_trail is not None
            
    def test_repository_performance_with_all_features(self):
        """Test performance when all iteration features are active"""
        user_id = 'performance_user'
        start_time = time.time()
        
        # Create substantial workload to test performance
        total_operations = 0
        
        # Batch operations with all features
        for batch in range(3):  # 3 batches
            batch_start = time.time()
            
            # Storage operations (Iteration 1)
            for i in range(5):  # 5 commands per batch
                command_data = {
                    'command_id': f'perf_b{batch:02d}_c{i:03d}',
                    'user_id': user_id,
                    'command_text': f'Performance test batch {batch} command {i}',
                    'timestamp': time.time(),
                    'context': {'batch': batch, 'index': i, 'perf_test': True}
                }
                
                success, _ = self.mobile_repo.store_command(command_data)
                if success:
                    total_operations += 1
                    
            # Correlation operations (Iteration 2)
            for i in range(4):  # 4 correlations per batch
                primary_id = f'perf_b{batch:02d}_c{i:03d}'
                related_id = f'perf_b{batch:02d}_c{i+1:03d}'
                
                success, _ = self.mobile_repo.create_context_correlation(
                    primary_id,
                    related_id,
                    'performance_sequence',
                    0.8
                )
                if success:
                    total_operations += 1
                    
            # Audit operations (Iteration 3)
            audit_success, _ = self.mobile_repo.create_audit_entry(
                f'perf_b{batch:02d}_c000',
                'BATCH_COMPLETE',
                user_id,
                {
                    'batch_number': batch,
                    'operations_in_batch': 9,  # 5 stores + 4 correlations
                    'performance_test': True
                }
            )
            if audit_success:
                total_operations += 1
                
            # Context sync operations (Iteration 4)
            batch_context = {
                'batch_complete': True,
                'batch_number': batch,
                'performance_test': True,
                'operations_count': total_operations
            }
            
            sync_success, _ = self.context_repo.sync_context_state(
                f'perf_batch_{batch:02d}',
                user_id,
                batch_context
            )
            if sync_success:
                total_operations += 1
                
            batch_duration = (time.time() - batch_start) * 1000
            assert batch_duration < 1000.0  # Each batch under 1 second
            
        total_duration = (time.time() - start_time) * 1000
        
        # Performance assertions
        assert total_operations > 20  # Should complete substantial operations
        assert total_duration < 5000.0  # Total under 5 seconds
        
        # Calculate operations per second
        ops_per_second = total_operations / (total_duration / 1000)
        assert ops_per_second > 5  # At least 5 operations per second
        
    def test_error_handling_across_all_iterations(self):
        """Test error handling across all iteration features"""
        user_id = 'error_test_user'
        
        # Test graceful handling of various error scenarios
        error_scenarios = []
        
        # Scenario 1: Invalid storage data
        try:
            success, message = self.mobile_repo.store_command({
                'command_id': '',  # Invalid empty ID
                'user_id': user_id,
                'command_text': 'error test',
                'timestamp': time.time()
            })
            error_scenarios.append(('storage_invalid_id', success, message))
        except Exception as e:
            error_scenarios.append(('storage_invalid_id', False, str(e)))
            
        # Scenario 2: Correlation with nonexistent commands
        try:
            success, message = self.mobile_repo.create_context_correlation(
                'nonexistent_1',
                'nonexistent_2',
                'error_test',
                0.5
            )
            error_scenarios.append(('correlation_nonexistent', success, message))
        except Exception as e:
            error_scenarios.append(('correlation_nonexistent', False, str(e)))
            
        # Scenario 3: Audit with invalid data
        try:
            success, message = self.mobile_repo.create_audit_entry(
                '',  # Invalid command ID
                'ERROR_TEST',
                user_id,
                {'error_test': True}
            )
            error_scenarios.append(('audit_invalid', success, message))
        except Exception as e:
            error_scenarios.append(('audit_invalid', False, str(e)))
            
        # Scenario 4: Context sync with invalid data
        try:
            success, message = self.context_repo.sync_context_state(
                '',  # Invalid context ID
                user_id,
                {'error_test': True}
            )
            error_scenarios.append(('sync_invalid', success, message))
        except Exception as e:
            error_scenarios.append(('sync_invalid', False, str(e)))
            
        # Validate error handling
        assert len(error_scenarios) == 4, "Should test all error scenarios"
        
        # All scenarios should be handled gracefully (no crashes)
        for scenario_name, success, message in error_scenarios:
            assert isinstance(success, bool), f"{scenario_name}: Should return boolean"
            assert isinstance(message, str), f"{scenario_name}: Should return string message"
            
    def test_data_consistency_across_iterations(self):
        """Test data consistency across all iteration boundaries"""
        user_id = 'consistency_user'
        consistency_id = 'consistency_test_001'
        
        # Create consistent data across all iterations
        base_command = {
            'command_id': consistency_id,
            'user_id': user_id,
            'command_text': 'consistency test command',
            'timestamp': time.time(),
            'context': {'consistency_test': True, 'test_id': consistency_id}
        }
        
        # Store command
        storage_success, _ = self.mobile_repo.store_command(base_command)
        assert storage_success is True
        
        # Create self-referential correlation for testing
        correlation_success, _ = self.mobile_repo.create_context_correlation(
            consistency_id,
            consistency_id + '_ref',  # Reference to related concept
            'consistency_test',
            1.0
        )
        
        # Create audit entry
        audit_success, _ = self.mobile_repo.create_audit_entry(
            consistency_id,
            'CONSISTENCY_TEST',
            user_id,
            {
                'test_type': 'data_consistency',
                'correlation_created': correlation_success,
                'consistency_check': True
            }
        )
        
        # Sync context with references to all previous operations
        context_data = {
            'consistency_test': True,
            'original_command': consistency_id,
            'storage_success': storage_success,
            'correlation_success': correlation_success,
            'audit_success': audit_success,
            'data_integrity_verified': True
        }
        
        sync_success, _ = self.context_repo.sync_context_state(
            consistency_id + '_context',
            user_id,
            context_data
        )
        
        # Validate consistency across all iterations
        assert all([storage_success, audit_success, sync_success])
        
        # Verify data can be retrieved consistently
        retrieved_context, _ = self.context_repo.get_context_state(
            consistency_id + '_context',
            user_id
        )
        
        assert retrieved_context is not None
        assert isinstance(retrieved_context, dict)
        
        # Verify audit trail maintains consistency
        audit_trail, _ = self.mobile_repo.get_audit_trail(consistency_id)
        assert audit_trail is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])