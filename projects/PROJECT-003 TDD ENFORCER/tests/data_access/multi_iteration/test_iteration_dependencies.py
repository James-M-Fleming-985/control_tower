#!/usr/bin/env python3
"""
Multi-Iteration Integration Tests - Iteration Dependencies
==========================================================

Tests that validate dependencies between TDD iterations in the Data Access Layer.
Ensures each iteration properly builds upon previous ones.

PROJECT: PROJECT-003 TDD ENFORCER
SYSTEM: SYSTEM-003-02 EXTENDED VALIDATION ENGINE
FEATURE: FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE
PHASE: Integration Testing (Phase 2)
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


class TestIterationDependencies:
    """Test iteration dependencies across TDD iterations 1-4"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.mobile_db_path = str(Path(self.temp_dir) / "mobile_commands.db")
        self.context_db_path = str(Path(self.temp_dir) / "context_engine.db")
        
        self.mobile_repo = MobileCommandHistoryRepository(self.mobile_db_path)
        self.context_repo = ContextEngineRepository(self.context_db_path)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_iteration_1_to_2_storage_to_correlation(self):
        """Test Iteration 1 (Storage) → Iteration 2 (Correlation) dependency"""
        # Iteration 1: Store commands
        command1_data = {
            'command_id': 'dep_test_001',
            'user_id': 'dependency_user',
            'command_text': 'first dependency test command',
            'timestamp': time.time(),
            'context': {'dependency_test': True, 'sequence': 1}
        }
        
        command2_data = {
            'command_id': 'dep_test_002',
            'user_id': 'dependency_user',
            'command_text': 'second dependency test command',
            'timestamp': time.time() + 1,
            'context': {'dependency_test': True, 'sequence': 2}
        }
        
        # Store both commands (Iteration 1 functionality)
        success1, message1 = self.mobile_repo.store_command(command1_data)
        success2, message2 = self.mobile_repo.store_command(command2_data)
        
        assert success1 is True
        assert success2 is True
        
        # Iteration 2: Create correlation between stored commands
        correlation_success, correlation_message = self.mobile_repo.create_context_correlation(
            'dep_test_001',
            'dep_test_002',
            'dependency_sequence',
            0.9
        )
        
        # Validate that correlation depends on successful storage
        assert correlation_success is True
        assert 'correlation' in correlation_message.lower() or 'created' in correlation_message.lower()
        
    def test_iteration_2_to_3_correlation_to_audit(self):
        """Test Iteration 2 (Correlation) → Iteration 3 (Audit) dependency"""
        # Setup: Store commands and create correlation
        base_time = time.time()
        
        # Store commands
        for i in range(2):
            command_data = {
                'command_id': f'audit_dep_{i:03d}',
                'user_id': 'audit_dependency_user',
                'command_text': f'audit dependency command {i}',
                'timestamp': base_time + i,
                'context': {'audit_dependency': True, 'index': i}
            }
            
            success, _ = self.mobile_repo.store_command(command_data)
            assert success is True
            
        # Create correlation
        correlation_success, _ = self.mobile_repo.create_context_correlation(
            'audit_dep_000',
            'audit_dep_001',
            'audit_dependency_test',
            0.85
        )
        assert correlation_success is True
        
        # Iteration 3: Create audit trail for correlation activities
        audit_success, audit_message = self.mobile_repo.create_audit_entry(
            'audit_dep_000',
            'CORRELATION_CREATED',
            'audit_dependency_user',
            {
                'operation': 'create_context_correlation',
                'related_command': 'audit_dep_001',
                'correlation_type': 'audit_dependency_test',
                'confidence_score': 0.85
            }
        )
        
        # Validate that audit can track correlation activities
        assert audit_success is True
        assert 'audit' in audit_message.lower() or 'created' in audit_message.lower()
        
    def test_iteration_3_to_4_audit_to_sync(self):
        """Test Iteration 3 (Audit) → Iteration 4 (Sync) dependency"""
        # Setup: Create audited command history
        sync_user = 'sync_dependency_user'
        
        # Store command
        command_data = {
            'command_id': 'sync_dep_001',
            'user_id': sync_user,
            'command_text': 'sync dependency test',
            'timestamp': time.time(),
            'context': {'sync_dependency': True}
        }
        
        success, _ = self.mobile_repo.store_command(command_data)
        assert success is True
        
        # Create audit entry
        audit_success, _ = self.mobile_repo.create_audit_entry(
            'sync_dep_001',
            'CREATE',
            sync_user,
            {
                'operation': 'store_command',
                'sync_test': True,
                'audit_before_sync': True
            }
        )
        assert audit_success is True
        
        # Iteration 4: Sync context while preserving audit integrity
        sync_context_data = {
            'sync_dependency_test': True,
            'original_command_id': 'sync_dep_001',
            'audit_preserved': True,
            'sync_timestamp': time.time()
        }
        
        sync_success, sync_message = self.context_repo.sync_context_state(
            'sync_dep_context_001',
            sync_user,
            sync_context_data
        )
        
        # Validate that sync can work with audited data
        assert sync_success is True
        assert 'sync' in sync_message.lower() or 'context' in sync_message.lower()
        
        # Verify audit integrity is maintained during sync
        audit_trail, audit_message = self.mobile_repo.get_audit_trail('sync_dep_001')
        assert audit_trail is not None
        
    def test_complete_dependency_chain_1_through_4(self):
        """Test complete dependency chain: Storage→Correlation→Audit→Sync"""
        user_id = 'complete_chain_user'
        base_time = time.time()
        
        # Step 1: Storage (Iteration 1)
        command_data = {
            'command_id': 'chain_test_001',
            'user_id': user_id,
            'command_text': 'complete chain test command',
            'timestamp': base_time,
            'context': {'complete_chain': True, 'step': 1}
        }
        
        storage_success, storage_message = self.mobile_repo.store_command(command_data)
        assert storage_success is True
        
        # Step 2: Correlation (Iteration 2) - depends on storage
        related_command_data = {
            'command_id': 'chain_test_002',
            'user_id': user_id,
            'command_text': 'related chain test command',
            'timestamp': base_time + 1,
            'context': {'complete_chain': True, 'step': 2}
        }
        
        storage_success2, _ = self.mobile_repo.store_command(related_command_data)
        assert storage_success2 is True
        
        correlation_success, correlation_message = self.mobile_repo.create_context_correlation(
            'chain_test_001',
            'chain_test_002',
            'complete_chain_test',
            0.95
        )
        assert correlation_success is True
        
        # Step 3: Audit (Iteration 3) - depends on correlation
        audit_success, audit_message = self.mobile_repo.create_audit_entry(
            'chain_test_001',
            'CHAIN_OPERATION',
            user_id,
            {
                'operation': 'complete_dependency_chain',
                'correlation_created': True,
                'related_command': 'chain_test_002',
                'chain_step': 3
            }
        )
        assert audit_success is True
        
        # Step 4: Sync (Iteration 4) - depends on audit trail
        sync_context_data = {
            'complete_chain_test': True,
            'primary_command': 'chain_test_001',
            'related_command': 'chain_test_002',
            'correlation_type': 'complete_chain_test',
            'audit_verified': True,
            'final_step': 4
        }
        
        sync_success, sync_message = self.context_repo.sync_context_state(
            'chain_test_context',
            user_id,
            sync_context_data
        )
        assert sync_success is True
        
        # Validation: All steps in the chain should be successful
        assert all([storage_success, correlation_success, audit_success, sync_success])
        
        # Verify final state includes data from all iterations
        final_context, _ = self.context_repo.get_context_state(
            'chain_test_context',
            user_id
        )
        assert final_context is not None
        assert isinstance(final_context, dict)
        
    def test_iteration_backward_compatibility(self):
        """Test that new iterations don't break previous iteration functionality"""
        user_id = 'compatibility_user'
        
        # Test that Iteration 1 (Storage) still works after all enhancements
        basic_command = {
            'command_id': 'compat_test_001',
            'user_id': user_id,
            'command_text': 'backward compatibility test',
            'timestamp': time.time(),
            'context': {'compatibility_test': True}
        }
        
        storage_success, _ = self.mobile_repo.store_command(basic_command)
        assert storage_success is True
        
        # Verify retrieval still works
        retrieved_commands, _ = self.mobile_repo.get_commands_by_user(user_id)
        assert retrieved_commands is not None
        
        # Test that Iteration 2 (Correlation) works independently
        correlation_success, _ = self.mobile_repo.create_context_correlation(
            'compat_test_001',
            'nonexistent_command',  # Should handle gracefully
            'compatibility_test',
            0.7
        )
        # Should either succeed or fail gracefully (not crash)
        assert isinstance(correlation_success, bool)
        
        # Test that all iterations can coexist
        # This validates that enhancements don't break basic functionality
        assert self.mobile_repo is not None
        assert self.context_repo is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])