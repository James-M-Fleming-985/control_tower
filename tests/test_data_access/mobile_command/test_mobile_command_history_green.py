# File: test_mobile_command_history_green.py
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from data_access.mobile_command_history_repository import (
    MobileCommandHistoryRepository
)


class TestMobileCommandHistoryGreen:
    """GREEN phase tests - validate working implementation"""
    
    def test_store_mobile_command_succeeds(self):
        """GREEN: Command storage should work correctly"""
        repository = MobileCommandHistoryRepository()
        command_data = {
            "command_id": "cmd_001",
            "user_id": "user_123",
            "command_type": "validate_pyramid",
            "timestamp": "2025-09-29T10:00:00Z",
            "execution_context": "mobile_app"
        }
        
        # This should succeed and return the command_id
        result = repository.store_command(command_data)
        assert result == "cmd_001"
        assert repository.command_exists("cmd_001")
    
    def test_retrieve_command_history_succeeds(self):
        """GREEN: Command retrieval should work correctly"""
        repository = MobileCommandHistoryRepository()
        
        # Store some test commands
        command1 = {
            "command_id": "cmd_001",
            "user_id": "user_123",
            "command_type": "validate_pyramid",
            "timestamp": "2025-09-29T10:00:00Z"
        }
        command2 = {
            "command_id": "cmd_002",
            "user_id": "user_123",
            "command_type": "run_tests",
            "timestamp": "2025-09-29T11:00:00Z"
        }
        
        repository.store_command(command1)
        repository.store_command(command2)
        
        # Retrieve command history
        history = repository.get_command_history("user_123")
        assert len(history) == 2
        assert history[0]["command_id"] in ["cmd_001", "cmd_002"]
        assert history[1]["command_id"] in ["cmd_001", "cmd_002"]
    
    def test_command_exists_check_succeeds(self):
        """GREEN: Command existence check should work correctly"""
        repository = MobileCommandHistoryRepository()
        
        # Initially should not exist
        assert not repository.command_exists("cmd_001")
        
        # Store a command
        command_data = {"command_id": "cmd_001", "user_id": "user_123"}
        repository.store_command(command_data)
        
        # Now should exist
        assert repository.command_exists("cmd_001")
    
    def test_delete_command_succeeds(self):
        """GREEN: Command deletion should work correctly"""
        repository = MobileCommandHistoryRepository()
        
        # Store a command
        command_data = {"command_id": "cmd_001", "user_id": "user_123"}
        repository.store_command(command_data)
        
        # Verify it exists
        assert repository.command_exists("cmd_001")
        
        # Delete it
        result = repository.delete_command("cmd_001")
        assert result is True
        
        # Verify it no longer exists
        assert not repository.command_exists("cmd_001")
        
        # Deleting non-existent should return False
        result = repository.delete_command("cmd_999")
        assert result is False
    
    def test_get_command_count_succeeds(self):
        """GREEN: Command count retrieval should work correctly"""
        repository = MobileCommandHistoryRepository()
        
        # Initially should be 0
        assert repository.get_command_count("user_123") == 0
        
        # Store some commands
        for i in range(3):
            command_data = {
                "command_id": f"cmd_00{i+1}",
                "user_id": "user_123"
            }
            repository.store_command(command_data)
        
        # Should now have 3 commands
        assert repository.get_command_count("user_123") == 3
        
        # Different user should have 0
        assert repository.get_command_count("user_456") == 0
    
    def test_performance_requirements(self):
        """GREEN: Validate performance requirements are met"""
        repository = MobileCommandHistoryRepository()
        
        # Store a command and check performance metadata
        command_data = {
            "command_id": "cmd_perf",
            "user_id": "user_123",
            "command_type": "performance_test"
        }
        
        repository.store_command(command_data)
        history = repository.get_command_history("user_123")
        
        # Check that performance metrics are recorded
        assert len(history) == 1
        command = history[0]
        assert "storage_time_ms" in command
        assert "retrieval_time_ms" in command
        assert "stored_at" in command
        
        # Performance should be reasonable (under 200ms target)
        assert command["storage_time_ms"] < 200
        assert command["retrieval_time_ms"] < 200