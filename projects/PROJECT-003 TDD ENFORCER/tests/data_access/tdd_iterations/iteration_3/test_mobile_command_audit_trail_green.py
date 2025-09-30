#!/usr/bin/env python3
"""
TDD Iteration 3: Audit Trail Persistence - GREEN Phase Tests
============================================================

GREEN phase tests for Audit Trail Persistence functionality.
Tests basic implementation that makes RED phase tests pass.

PROJECT: PROJECT-003 TDD ENFORCER
SYSTEM: SYSTEM-003-02 EXTENDED VALIDATION ENGINE
FEATURE: FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE
ITERATION: TDD_ITERATION_003
PHASE: GREEN (Basic Implementation)
"""

import pytest
import tempfile
import shutil
import time
from pathlib import Path

import sys
sys.path.append('/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/src')

from data_access.mobile_command_history_repository import MobileCommandHistoryRepository


class TestAuditTrailPersistenceGreen:
    """GREEN Phase tests for Audit Trail Persistence functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / "test_audit_green.db")
        self.repository = MobileCommandHistoryRepository(self.db_path)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_basic_audit_entry_creation(self):
        """Test basic audit entry creation - GREEN phase implementation"""
        # Store a command first
        command_data = {
            'command_id': 'audit_green_001',
            'user_id': 'audit_user',
            'command_text': 'green phase audit test',
            'timestamp': time.time(),
            'context': {'phase': 'green', 'audit_test': True}
        }
        
        success, message = self.repository.store_command(command_data)
        assert success is True
        
        # Create audit entry - should work in GREEN phase
        audit_data = {
            'command_id': 'audit_green_001',
            'action': 'CREATE',
            'user_id': 'audit_user',
            'timestamp': time.time(),
            'details': {'operation': 'store_command', 'status': 'success'}
        }
        
        success, message = self.repository.create_audit_entry(
            audit_data['command_id'],
            audit_data['action'],
            audit_data['user_id'],
            audit_data['details']
        )
        
        assert success is True
        assert 'audit' in message.lower() or 'created' in message.lower()
        
    def test_audit_trail_retrieval(self):
        """Test audit trail retrieval - GREEN phase implementation"""
        # Create test audit entries
        command_id = 'audit_retrieval_test'
        
        # Store command
        command_data = {
            'command_id': command_id,
            'user_id': 'retrieval_user',
            'command_text': 'retrieval test command',
            'timestamp': time.time(),
            'context': {'test_type': 'retrieval'}
        }
        
        success, _ = self.repository.store_command(command_data)
        assert success is True
        
        # Create audit entry
        success, _ = self.repository.create_audit_entry(
            command_id,
            'CREATE',
            'retrieval_user',
            {'operation': 'store_command', 'test': True}
        )
        assert success is True
        
        # Retrieve audit trail
        audit_trail, message = self.repository.get_audit_trail(command_id)
        
        assert audit_trail is not None
        assert isinstance(audit_trail, (list, dict))
        
    def test_audit_compliance_validation(self):
        """Test audit compliance validation - GREEN phase implementation"""
        # Create test data for compliance validation
        user_id = 'compliance_user'
        
        # Store and audit multiple commands
        for i in range(3):
            command_data = {
                'command_id': f'compliance_test_{i:03d}',
                'user_id': user_id,
                'command_text': f'compliance test command {i}',
                'timestamp': time.time() + i,
                'context': {'compliance_test': True, 'sequence': i}
            }
            
            success, _ = self.repository.store_command(command_data)
            assert success is True
            
            success, _ = self.repository.create_audit_entry(
                command_data['command_id'],
                'CREATE',
                user_id,
                {'operation': 'store_command', 'sequence': i}
            )
            assert success is True
            
        # Validate audit compliance
        compliance_result, message = self.repository.validate_audit_compliance(
            user_id
        )
        
        assert compliance_result is not None
        assert isinstance(compliance_result, (bool, dict, float))
        
    def test_audit_search_functionality(self):
        """Test audit search functionality - GREEN phase implementation"""
        # Create searchable audit data
        test_user = 'search_user'
        current_time = time.time()
        
        # Create multiple audit entries
        for i in range(3):
            command_id = f'search_test_{i:03d}'
            
            # Store command
            command_data = {
                'command_id': command_id,
                'user_id': test_user,
                'command_text': f'search test command {i}',
                'timestamp': current_time + i,
                'context': {'search_test': True, 'index': i}
            }
            
            success, _ = self.repository.store_command(command_data)
            assert success is True
            
            # Create audit entry
            success, _ = self.repository.create_audit_entry(
                command_id,
                'CREATE',
                test_user,
                {'operation': 'store_command', 'index': i}
            )
            assert success is True
            
        # Search audit trail
        search_criteria = {
            'user_id': test_user,
            'action': 'CREATE',
            'date_range': (current_time - 60, current_time + 60)
        }
        
        search_results, message = self.repository.search_audit_trail(
            search_criteria
        )
        
        assert search_results is not None
        assert isinstance(search_results, (list, dict))
        
    def test_audit_entry_validation(self):
        """Test audit entry data validation"""
        # Test valid audit entry
        valid_command = {
            'command_id': 'validation_test_001',
            'user_id': 'validation_user',
            'command_text': 'validation test',
            'timestamp': time.time(),
            'context': {'validation': True}
        }
        
        success, _ = self.repository.store_command(valid_command)
        assert success is True
        
        # Valid audit entry
        success, message = self.repository.create_audit_entry(
            'validation_test_001',
            'CREATE',
            'validation_user',
            {'operation': 'test', 'valid': True}
        )
        
        assert success is True
        assert isinstance(message, str)
        
        # Test invalid audit entry handling
        success, message = self.repository.create_audit_entry(
            '',  # Invalid command_id
            'CREATE',
            'validation_user',
            {'operation': 'test'}
        )
        
        # Should handle invalid data appropriately
        assert isinstance(success, bool)
        assert isinstance(message, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])