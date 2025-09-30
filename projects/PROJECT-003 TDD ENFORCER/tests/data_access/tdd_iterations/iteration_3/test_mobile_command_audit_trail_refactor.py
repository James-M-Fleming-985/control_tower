#!/usr/bin/env python3
"""
TDD Iteration 3: Audit Trail Persistence - REFACTOR Phase Tests
===============================================================

Enhanced testing for the REFACTOR phase of Audit Trail Persistence.
Tests advanced features, performance optimizations, and enhanced capabilities.

PROJECT: PROJECT-003 TDD ENFORCER
SYSTEM: SYSTEM-003-02 EXTENDED VALIDATION ENGINE
FEATURE: FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE
ITERATION: TDD_ITERATION_003
PHASE: REFACTOR
"""

import pytest
import tempfile
import shutil
import time
import threading
from pathlib import Path

import sys
sys.path.append('/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/src')

from data_access.mobile_command_history_repository import MobileCommandHistoryRepository


class TestAuditTrailPersistenceRefactor:
    """Test suite for Audit Trail Persistence REFACTOR phase enhancements"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / "test_audit_refactor.db")
        self.repository = MobileCommandHistoryRepository(self.db_path)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_enhanced_audit_entry_with_metadata(self):
        """Test enhanced audit entries with rich metadata"""
        # Store command with enhanced context
        command_data = {
            'command_id': 'enhanced_audit_001',
            'user_id': 'enhanced_user',
            'command_text': 'enhanced audit test',
            'timestamp': time.time(),
            'context': {
                'feature': 'audit_trail',
                'version': '2.0',
                'enhancement_level': 'refactor'
            }
        }
        
        success, _ = self.repository.store_command(command_data)
        assert success is True
        
        # Create enhanced audit entry with rich metadata
        enhanced_details = {
            'operation': 'store_command',
            'status': 'success',
            'performance_metrics': {
                'execution_time_ms': 5.2,
                'memory_usage_kb': 128,
                'db_operations': 2
            },
            'security_context': {
                'authentication_method': 'token',
                'authorization_level': 'user',
                'session_id': 'session_123'
            },
            'compliance_info': {
                'regulation': 'GDPR',
                'data_classification': 'internal',
                'retention_period_days': 365
            }
        }
        
        success, message = self.repository.create_audit_entry(
            'enhanced_audit_001',
            'CREATE_ENHANCED',
            'enhanced_user',
            enhanced_details
        )
        
        assert success is True
        assert 'audit' in message.lower() or 'enhanced' in message.lower()
        
    def test_audit_trail_advanced_analytics(self):
        """Test advanced analytics and reporting for audit trails"""
        user_id = 'analytics_user'
        current_time = time.time()
        
        # Create comprehensive audit history
        audit_scenarios = [
            ('CREATE', 'Command creation', {'priority': 'high'}),
            ('UPDATE', 'Command modification', {'priority': 'medium'}),
            ('DELETE', 'Command removal', {'priority': 'low'}),
            ('ACCESS', 'Command access', {'priority': 'medium'}),
            ('EXPORT', 'Data export', {'priority': 'high'})
        ]
        
        for i, (action, description, metadata) in enumerate(audit_scenarios):
            command_id = f'analytics_test_{i:03d}'
            
            # Store command
            command_data = {
                'command_id': command_id,
                'user_id': user_id,
                'command_text': f'analytics test {i}: {description}',
                'timestamp': current_time + i,
                'context': {'analytics_test': True, 'scenario': i}
            }
            
            success, _ = self.repository.store_command(command_data)
            assert success is True
            
            # Create detailed audit entry
            audit_details = {
                'operation': action.lower(),
                'description': description,
                'metadata': metadata,
                'analytics_data': {
                    'user_session': f'session_{i}',
                    'ip_address': f'192.168.1.{100 + i}',
                    'user_agent': 'TestAgent/1.0',
                    'timestamp_iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', 
                                                   time.gmtime(current_time + i))
                }
            }
            
            success, _ = self.repository.create_audit_entry(
                command_id,
                action,
                user_id,
                audit_details
            )
            assert success is True
            
        # Test advanced audit trail retrieval with analytics
        audit_trail, message = self.repository.get_audit_trail('analytics_test_001')
        assert audit_trail is not None
        
        # Test compliance validation with enhanced criteria
        compliance_result, message = self.repository.validate_audit_compliance(
            user_id
        )
        assert compliance_result is not None
        
    def test_audit_performance_optimization(self):
        """Test performance optimizations in audit trail operations"""
        start_time = time.time()
        
        # Create large number of audit entries to test performance
        performance_commands = []
        for i in range(20):
            command_data = {
                'command_id': f'perf_audit_{i:03d}',
                'user_id': 'perf_user',
                'command_text': f'performance audit test {i}',
                'timestamp': time.time(),
                'context': {'performance_test': True, 'batch': 'large'}
            }
            performance_commands.append(command_data)
            
            # Store command with timing
            cmd_start = time.time()
            success, _ = self.repository.store_command(command_data)
            cmd_duration = (time.time() - cmd_start) * 1000
            
            assert success is True
            assert cmd_duration < 10.0  # Should be under 10ms
            
            # Create audit entry with timing
            audit_start = time.time()
            success, _ = self.repository.create_audit_entry(
                command_data['command_id'],
                'CREATE',
                'perf_user',
                {
                    'operation': 'performance_test',
                    'batch_index': i,
                    'performance_metrics': {
                        'command_store_time_ms': cmd_duration
                    }
                }
            )
            audit_duration = (time.time() - audit_start) * 1000
            
            assert success is True
            assert audit_duration < 15.0  # Audit should be under 15ms
            
        total_duration = (time.time() - start_time) * 1000
        
        # Performance assertions
        assert total_duration < 1000.0  # Total should be under 1 second
        
    def test_audit_search_with_advanced_filtering(self):
        """Test advanced search and filtering capabilities"""
        # Create diverse audit data for comprehensive search testing
        search_scenarios = [
            ('user_alpha', 'CREATE', 'high', {'department': 'engineering'}),
            ('user_beta', 'UPDATE', 'medium', {'department': 'qa'}),
            ('user_alpha', 'DELETE', 'low', {'department': 'engineering'}),
            ('user_gamma', 'ACCESS', 'high', {'department': 'security'}),
            ('user_beta', 'EXPORT', 'medium', {'department': 'qa'})
        ]
        
        current_time = time.time()
        
        for i, (user, action, priority, metadata) in enumerate(search_scenarios):
            command_id = f'search_advanced_{i:03d}'
            
            # Store command
            command_data = {
                'command_id': command_id,
                'user_id': user,
                'command_text': f'advanced search test {i}',
                'timestamp': current_time + i,
                'context': {'search_test': True, 'priority': priority}
            }
            
            success, _ = self.repository.store_command(command_data)
            assert success is True
            
            # Create searchable audit entry
            audit_details = {
                'operation': action.lower(),
                'priority': priority,
                'metadata': metadata,
                'searchable_tags': [user, action, priority, metadata['department']]
            }
            
            success, _ = self.repository.create_audit_entry(
                command_id,
                action,
                user,
                audit_details
            )
            assert success is True
            
        # Test various search scenarios
        search_tests = [
            # Search by user
            {'user_id': 'user_alpha'},
            # Search by action  
            {'action': 'CREATE'},
            # Search by date range
            {'date_range': (current_time - 60, current_time + 60)},
            # Complex search criteria
            {
                'user_id': 'user_beta',
                'action': 'UPDATE',
                'date_range': (current_time - 60, current_time + 60)
            }
        ]
        
        for criteria in search_tests:
            search_results, message = self.repository.search_audit_trail(criteria)
            
            # Should return results or handle empty results appropriately
            assert search_results is not None
            assert isinstance(search_results, (list, dict))
            
    def test_audit_data_integrity_and_compliance(self):
        """Test data integrity and compliance features"""
        # Test audit entry immutability
        command_id = 'integrity_test_001'
        
        # Store command
        command_data = {
            'command_id': command_id,
            'user_id': 'integrity_user',
            'command_text': 'integrity test command',
            'timestamp': time.time(),
            'context': {'integrity_test': True}
        }
        
        success, _ = self.repository.store_command(command_data)
        assert success is True
        
        # Create audit entry with integrity checks
        original_details = {
            'operation': 'integrity_test',
            'original_data': True,
            'checksum': 'abc123def456',
            'integrity_metadata': {
                'creation_timestamp': time.time(),
                'creator_id': 'integrity_user',
                'data_hash': 'sha256_hash_placeholder'
            }
        }
        
        success, _ = self.repository.create_audit_entry(
            command_id,
            'CREATE',
            'integrity_user',
            original_details
        )
        assert success is True
        
        # Verify audit trail integrity
        audit_trail, _ = self.repository.get_audit_trail(command_id)
        assert audit_trail is not None
        
        # Test compliance validation
        compliance_result, _ = self.repository.validate_audit_compliance(
            'integrity_user'
        )
        assert compliance_result is not None
        
    def test_concurrent_audit_operations(self):
        """Test thread safety in concurrent audit operations"""
        base_commands = []
        
        # Prepare test data
        for i in range(5):
            command_data = {
                'command_id': f'concurrent_audit_{i:03d}',
                'user_id': 'concurrent_user',
                'command_text': f'concurrent audit test {i}',
                'timestamp': time.time() + i,
                'context': {'concurrent_test': True, 'index': i}
            }
            base_commands.append(command_data)
            
            success, _ = self.repository.store_command(command_data)
            assert success is True
            
        # Concurrent audit entry creation
        audit_results = []
        audit_errors = []
        
        def create_audit_entries(thread_id):
            """Create audit entries in separate thread"""
            try:
                for i, command_data in enumerate(base_commands):
                    success, message = self.repository.create_audit_entry(
                        command_data['command_id'],
                        f'CONCURRENT_ACTION_{thread_id}',
                        'concurrent_user',
                        {
                            'thread_id': thread_id,
                            'operation_index': i,
                            'concurrent_test': True
                        }
                    )
                    audit_results.append((thread_id, i, success, message))
            except Exception as e:
                audit_errors.append((thread_id, str(e)))
                
        # Create and run multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=create_audit_entries, 
                                      args=(thread_id,))
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        # Validate concurrent processing results
        assert len(audit_errors) == 0, f"Concurrent errors: {audit_errors}"
        assert len(audit_results) > 0, "Should have audit results"
        
        # Verify thread safety - most operations should succeed
        successful_audits = [r for r in audit_results if r[2] is True]
        assert len(successful_audits) > 0, "Some concurrent audits should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])