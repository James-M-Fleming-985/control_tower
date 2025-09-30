import pytest
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from data_access.context_engine_repository import ContextEngineRepository


class TestContextEngineDataSync:
    
    def test_sync_context_data_succeeds(self):
        """GREEN: Context data synchronization should work with valid data"""
        repository = ContextEngineRepository()
        context_data = {
            "user_id": "user_123",
            "context_state": {
                "active_feature": "validation_engine",
                "current_layer": "business_logic",
                "test_results": []
            }
        }
        
        # GREEN: This should succeed and return True
        result = repository.sync_context_state(context_data)
        
        # Validate the result
        assert result is True
        assert isinstance(result, bool)
    
    def test_retrieve_context_state_succeeds(self):
        """GREEN: Context state retrieval should return context data"""
        repository = ContextEngineRepository()
        
        # First sync some context data
        context_data = {
            "user_id": "user_123",
            "context_state": {
                "active_feature": "validation_engine",
                "current_layer": "business_logic",
                "test_results": ["test_1", "test_2"]
            }
        }
        repository.sync_context_state(context_data)
        
        # GREEN: This should succeed and return context state
        result = repository.get_context_state("user_123")
        
        # Validate the result
        assert isinstance(result, dict)
        assert result["user_id"] == "user_123"
        assert "context_state" in result
        assert "sync_id" in result
        assert "version" in result
        assert result["version"] == 1
    
    def test_context_conflict_resolution_succeeds(self):
        """GREEN: Context conflict resolution should return resolved data"""
        repository = ContextEngineRepository()
        conflict_data = {
            "user_id": "user_123",
            "local_context": {"version": 1, "data": {"local": "value"}},
            "remote_context": {"version": 2, "data": {"remote": "value"}}
        }
        
        # GREEN: This should succeed and return resolution record
        result = repository.resolve_context_conflicts(conflict_data)
        
        # Validate the result
        assert isinstance(result, dict)
        assert result["user_id"] == "user_123"
        assert "resolution_id" in result
        assert "resolved_context" in result
        assert "resolution_strategy" in result
        assert result["resolution_strategy"] in ["remote_preferred", "local_preferred", "merged"]
    
    def test_context_sync_performance_requirements(self):
        """GREEN: Context operations should meet performance requirements"""
        repository = ContextEngineRepository()
        
        # Test sync performance
        context_data = {
            "user_id": "user_perf",
            "context_state": {"performance": "test"}
        }
        
        import time
        start_time = time.time()
        repository.sync_context_state(context_data)
        sync_duration = (time.time() - start_time) * 1000  # Convert to ms
        
        # Test retrieval performance
        start_time = time.time()
        repository.get_context_state("user_perf")
        retrieval_duration = (time.time() - start_time) * 1000
        
        # Validate performance requirements (should be sub-10ms)
        assert sync_duration < 10, f"Sync took {sync_duration:.2f}ms, should be <10ms"
        assert retrieval_duration < 10, f"Retrieval took {retrieval_duration:.2f}ms, should be <10ms"