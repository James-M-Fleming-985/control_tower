import time
import uuid
import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import sys
sys.path.append('/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/src')
from data_access.context_engine_repository import ContextEngineRepository


class TestContextEngineDataSyncRefactor:
    
    def test_enhanced_sync_with_priority_and_analytics(self):
        """REFACTOR: Enhanced sync with priority levels and analytics"""
        repository = ContextEngineRepository()
        
        # Test high priority sync
        context_data = {
            "user_id": "user_refactor",
            "context_state": {
                "active_feature": "enhanced_validation",
                "priority_data": {"critical": True}
            }
        }
        
        result = repository.sync_context_state(context_data, priority='high')
        
        # Validate enhanced response
        assert isinstance(result, dict)
        assert result['success'] is True
        assert 'sync_id' in result
        assert 'version' in result
        assert result['priority'] == 'high'
        assert 'performance_ms' in result
        assert result['performance_ms'] < 10  # Performance requirement
    
    def test_context_retrieval_with_caching_and_analytics(self):
        """REFACTOR: Context retrieval with caching optimization"""
        repository = ContextEngineRepository()
        
        # Setup context data
        context_data = {
            "user_id": "user_cache",
            "context_state": {"test": "cache_optimization"}
        }
        repository.sync_context_state(context_data)
        
        # Test cached retrieval with analytics
        start_time = time.time()
        result = repository.get_context_state("user_cache", include_analytics=True)
        retrieval_time = (time.time() - start_time) * 1000
        
        # Validate enhanced retrieval
        assert isinstance(result, dict)
        assert result['user_id'] == "user_cache"
        assert 'analytics' in result
        assert 'sync_count' in result['analytics']
        assert 'recent_operations' in result['analytics']
        assert retrieval_time < 5  # Should be faster due to caching
    
    def test_advanced_conflict_resolution_strategies(self):
        """REFACTOR: Advanced conflict resolution with multiple strategies"""
        repository = ContextEngineRepository()
        
        conflict_data = {
            "user_id": "user_conflict",
            "local_context": {
                "version": 1, 
                "data": {"local": "value"},
                "timestamp": "2025-09-30T10:00:00Z"
            },
            "remote_context": {
                "version": 2, 
                "data": {"remote": "value"},
                "timestamp": "2025-09-30T11:00:00Z"
            }
        }
        
        # Test timestamp-based strategy
        result = repository.resolve_context_conflicts(conflict_data, strategy='timestamp')
        
        # Validate enhanced resolution
        assert isinstance(result, dict)
        assert 'resolution_strategy' in result
        assert result['resolution_strategy'] == 'timestamp_based_remote'
        assert 'conflict_complexity' in result
        assert 'confidence_score' in result
        assert isinstance(result['confidence_score'], float)
        assert 0.0 <= result['confidence_score'] <= 1.0
    
    def test_thread_safety_and_concurrent_operations(self):
        """REFACTOR: Thread safety validation for concurrent operations"""
        repository = ContextEngineRepository()
        import threading
        
        results = []
        
        def sync_operation(user_suffix):
            context_data = {
                "user_id": f"user_thread_{user_suffix}",
                "context_state": {"thread_test": user_suffix}
            }
            result = repository.sync_context_state(context_data)
            results.append(result['success'])
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=sync_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Validate all operations succeeded
        assert len(results) == 5
        assert all(results)  # All should be True
    
    def test_performance_optimization_validation(self):
        """REFACTOR: Performance optimization and metrics collection"""
        repository = ContextEngineRepository()
        
        # Test multiple operations for performance validation
        performance_results = []
        
        for i in range(10):
            context_data = {
                "user_id": f"user_perf_{i}",
                "context_state": {"performance_test": i}
            }
            
            start_time = time.time()
            result = repository.sync_context_state(context_data)
            operation_time = (time.time() - start_time) * 1000
            
            performance_results.append(operation_time)
            assert result['performance_ms'] < 10
        
        # Validate performance consistency
        avg_performance = sum(performance_results) / len(performance_results)
        assert avg_performance < 5  # Average should be under 5ms
        
        # Test retrieval performance
        retrieval_results = []
        for i in range(10):
            start_time = time.time()
            repository.get_context_state(f"user_perf_{i}")
            retrieval_time = (time.time() - start_time) * 1000
            retrieval_results.append(retrieval_time)
        
        avg_retrieval = sum(retrieval_results) / len(retrieval_results)
        assert avg_retrieval < 3  # Cached retrieval should be faster
    
    def test_data_integrity_and_checksum_validation(self):
        """REFACTOR: Data integrity validation with checksums"""
        repository = ContextEngineRepository()
        
        context_data = {
            "user_id": "user_integrity",
            "context_state": {"integrity_test": "checksum_validation"}
        }
        
        result = repository.sync_context_state(context_data)
        retrieved = repository.get_context_state("user_integrity")
        
        # Validate data integrity
        assert 'checksum' in retrieved
        assert isinstance(retrieved['checksum'], str)
        assert len(retrieved['checksum']) == 8  # 8-character checksum
        
        # Verify checksum consistency
        checksum1 = repository._generate_checksum(context_data)
        checksum2 = repository._generate_checksum(context_data)
        assert checksum1 == checksum2  # Should be deterministic