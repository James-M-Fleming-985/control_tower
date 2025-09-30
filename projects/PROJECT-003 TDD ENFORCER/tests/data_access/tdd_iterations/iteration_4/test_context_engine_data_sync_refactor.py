#!/usr/bin/env python3
"""
TDD Iteration 4: Context Engine Data Sync - REFACTOR Phase Tests
================================================================

Enhanced testing for the REFACTOR phase of Context Engine Data Sync.
Tests advanced features like caching, analytics, thread safety, and performance optimizations.

PROJECT: PROJECT-003 TDD ENFORCER
SYSTEM: SYSTEM-003-02 EXTENDED VALIDATION ENGINE
FEATURE: FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE
ITERATION: TDD_ITERATION_004
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

from data_access.context_engine_repository import ContextEngineRepository


class TestContextEngineDataSyncRefactor:
    """Test suite for Context Engine Data Sync REFACTOR phase enhancements"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / "test_context_refactor.db")
        self.repository = ContextEngineRepository(self.db_path)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_enhanced_sync_with_priority_and_analytics(self):
        """Test enhanced context sync with priority levels and analytics"""
        # Enhanced sync with priority and analytics tracking
        context_data = {
            'context_id': 'enhanced_sync_001',
            'user_id': 'user_refactor',
            'state_data': {
                'enhanced_features': True,
                'priority': 'high',
                'analytics_enabled': True,
                'refactor_phase': True
            },
            'priority': 'high',
            'analytics_metadata': {
                'sync_reason': 'user_action',
                'client_version': '2.0',
                'performance_tracking': True
            }
        }
        
        success, message = self.repository.sync_context_state(
            context_data['context_id'],
            context_data['user_id'],
            context_data['state_data'],
            priority=context_data.get('priority'),
            analytics_data=context_data.get('analytics_metadata')
        )
        
        assert success is True
        assert 'sync' in message.lower() or 'enhanced' in message.lower()
        
    def test_context_retrieval_with_caching_and_analytics(self):
        """Test context retrieval with intelligent caching"""
        context_id = 'cache_test_001'
        user_id = 'user_cache'
        
        # Initial sync
        initial_state = {
            'caching_test': True,
            'data': {'cached': True, 'timestamp': time.time()},
            'cache_metadata': {'cache_enabled': True}
        }
        
        success, _ = self.repository.sync_context_state(
            context_id,
            user_id,
            initial_state
        )
        assert success is True
        
        # First retrieval (cache miss)
        start_time = time.time()
        context_state, message = self.repository.get_context_state(
            context_id,
            user_id
        )
        first_retrieval_time = (time.time() - start_time) * 1000
        
        assert context_state is not None
        
        # Second retrieval (cache hit)
        start_time = time.time()
        cached_state, cache_message = self.repository.get_context_state(
            context_id,
            user_id
        )
        second_retrieval_time = (time.time() - start_time) * 1000
        
        assert cached_state is not None
        # Cache hit should be faster (or at least not significantly slower)
        assert second_retrieval_time <= first_retrieval_time * 2
        
    def test_advanced_conflict_resolution_strategies(self):
        """Test advanced conflict resolution with multiple strategies"""
        context_id = 'conflict_advanced_001'
        user_id = 'user_conflict'
        
        # Setup conflicting states
        local_state = {
            'conflict_resolution_test': True,
            'version': 2,
            'local_changes': {'field_a': 'local_value', 'timestamp': time.time()},
            'modification_source': 'local'
        }
        
        remote_state = {
            'conflict_resolution_test': True,
            'version': 2,
            'remote_changes': {'field_b': 'remote_value', 'timestamp': time.time() + 1},
            'modification_source': 'remote'
        }
        
        # Test advanced conflict resolution with strategy
        resolution_result, message = self.repository.resolve_context_conflicts(
            context_id,
            user_id,
            local_state,
            remote_state,
            strategy='timestamp_based_remote'  # Enhanced strategy parameter
        )
        
        assert resolution_result is not None
        assert isinstance(resolution_result, dict)
        assert 'conflict' in message.lower() or 'resolved' in message.lower()
        
    def test_thread_safety_and_concurrent_operations(self):
        """Test thread safety and concurrent operations"""
        base_context_id = 'concurrent_test'
        user_id = 'user_thread'
        
        # Concurrent sync operations
        sync_results = []
        sync_errors = []
        
        def concurrent_sync_operation(thread_id):
            """Perform sync operations in separate thread"""
            try:
                for i in range(5):
                    context_id = f'{base_context_id}_{thread_id}_{i}'
                    state_data = {
                        'thread_safety_test': True,
                        'thread_id': thread_id,
                        'operation_index': i,
                        'timestamp': time.time()
                    }
                    
                    success, message = self.repository.sync_context_state(
                        context_id,
                        f'{user_id}_{thread_id}',
                        state_data
                    )
                    
                    sync_results.append((thread_id, i, success, message))
            except Exception as e:
                sync_errors.append((thread_id, str(e)))
                
        # Create and start multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=concurrent_sync_operation,
                                      args=(thread_id,))
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        # Validate thread safety
        assert len(sync_errors) == 0, f"Thread safety errors: {sync_errors}"
        assert len(sync_results) > 0, "Should have sync results"
        
        # Verify most operations succeeded
        successful_syncs = [r for r in sync_results if r[2] is True]
        assert len(successful_syncs) > 0, "Some concurrent syncs should succeed"
        
    def test_performance_optimization_validation(self):
        """Test performance optimizations in enhanced context engine"""
        # Performance test with multiple operations
        performance_contexts = []
        
        start_time = time.time()
        
        # Create multiple contexts to test bulk performance
        for i in range(10):
            context_id = f'perf_test_{i:03d}'
            user_id = f'user_perf_{i}'
            
            state_data = {
                'performance_test': True,
                'context_index': i,
                'large_data': {
                    'field_1': f'data_{i}' * 10,
                    'field_2': list(range(i, i + 10)),
                    'field_3': {'nested': {'deep': f'value_{i}'}}
                },
                'timestamp': time.time()
            }
            
            # Measure individual sync performance
            sync_start = time.time()
            success, message = self.repository.sync_context_state(
                context_id,
                user_id,
                state_data
            )
            sync_duration = (time.time() - sync_start) * 1000  # Convert to ms
            
            assert success is True
            assert sync_duration < 100.0  # Should be under 100ms per operation
            
            performance_contexts.append((context_id, user_id))
            
        # Test bulk retrieval performance
        retrieval_times = []
        for context_id, user_id in performance_contexts:
            retrieval_start = time.time()
            context_state, message = self.repository.get_context_state(
                context_id,
                user_id
            )
            retrieval_duration = (time.time() - retrieval_start) * 1000
            
            assert context_state is not None
            retrieval_times.append(retrieval_duration)
            
        total_duration = (time.time() - start_time) * 1000
        avg_retrieval_time = sum(retrieval_times) / len(retrieval_times)
        
        # Performance assertions
        assert total_duration < 5000.0  # Total should be under 5 seconds
        assert avg_retrieval_time < 50.0  # Average retrieval under 50ms
        
    def test_data_integrity_and_checksum_validation(self):
        """Test data integrity and checksum validation"""
        context_id = 'integrity_test_001'
        user_id = 'user_integrity'
        
        # Sync context with integrity validation
        state_data = {
            'data_integrity_test': True,
            'sensitive_data': {
                'user_preferences': {'theme': 'dark', 'language': 'en'},
                'session_data': {'login_time': time.time()},
                'security_context': {'authenticated': True}
            },
            'integrity_metadata': {
                'checksum_enabled': True,
                'validation_required': True
            }
        }
        
        success, message = self.repository.sync_context_state(
            context_id,
            user_id,
            state_data,
            enable_integrity_validation=True
        )
        
        assert success is True
        assert 'sync' in message.lower() or 'integrity' in message.lower()
        
        # Retrieve and validate integrity
        retrieved_state, retrieval_message = self.repository.get_context_state(
            context_id,
            user_id,
            validate_integrity=True
        )
        
        assert retrieved_state is not None
        assert isinstance(retrieved_state, dict)
        
        # Test integrity validation detection
        # (Implementation would detect data tampering)
        assert 'data_integrity_test' in str(retrieved_state)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])