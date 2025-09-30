# File: test_mobile_command_history_refactor.py
import pytest
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import sys
sys.path.append('/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/src')
from data_access.mobile_command_history_repository import (
    MobileCommandHistoryRepository, CommandStatus, SecurityValidator
)


class TestMobileCommandHistoryRefactor:
    """REFACTOR phase tests - validate enhanced functionality"""
    
    def test_security_validation(self):
        """Test enhanced security validation"""
        repository = MobileCommandHistoryRepository()
        
        # Test invalid user_id
        with pytest.raises(ValueError, match="Invalid user_id format"):
            repository.store_command({"user_id": "invalid user!", "data": "test"})
    
    def test_command_limits(self):
        """Test user command limits"""
        repository = MobileCommandHistoryRepository(max_commands_per_user=2)
        
        # Store commands up to limit
        repository.store_command({"user_id": "test_user", "data": "cmd1"})
        repository.store_command({"user_id": "test_user", "data": "cmd2"})
        
        # Third command should exceed limit
        with pytest.raises(ValueError, match="exceeded maximum commands limit"):
            repository.store_command({"user_id": "test_user", "data": "cmd3"})
    
    def test_enhanced_command_history_filtering(self):
        """Test enhanced command history with filtering"""
        repository = MobileCommandHistoryRepository()
        
        # Store commands with different statuses
        cmd1_data = {"user_id": "test_user", "status": CommandStatus.COMPLETED.value}
        cmd2_data = {"user_id": "test_user", "status": CommandStatus.PENDING.value}
        
        repository.store_command(cmd1_data)
        repository.store_command(cmd2_data)
        
        # Test status filtering
        completed_commands = repository.get_command_history(
            "test_user", status_filter=CommandStatus.COMPLETED
        )
        assert len(completed_commands) == 1
        assert completed_commands[0]["status"] == CommandStatus.COMPLETED.value
        
        # Test limit
        limited_commands = repository.get_command_history("test_user", limit=1)
        assert len(limited_commands) == 1
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        repository = MobileCommandHistoryRepository()
        
        # Perform some operations
        repository.store_command({"user_id": "test_user", "data": "test"})
        repository.get_command_history("test_user")
        
        # Get performance metrics
        metrics = repository.get_performance_metrics()
        
        assert "store_command_avg_ms" in metrics
        assert "get_command_history_avg_ms" in metrics
        assert "total_operations" in metrics
        assert "success_rate" in metrics
        assert metrics["success_rate"] == 100.0
    
    def test_repository_stats(self):
        """Test repository statistics"""
        repository = MobileCommandHistoryRepository()
        
        # Store some commands
        repository.store_command({"user_id": "user1", "data": "test1"})
        repository.store_command({"user_id": "user2", "data": "test2"})
        
        stats = repository.get_repository_stats()
        
        assert stats["total_commands"] == 2
        assert stats["total_users"] == 2
        assert stats["total_operations"] > 0
        assert stats["failed_operations"] == 0
    
    def test_security_validator(self):
        """Test SecurityValidator functionality"""
        validator = SecurityValidator()
        
        # Test valid user_ids
        assert validator.validate_user_id("user_123")
        assert validator.validate_user_id("test-user")
        
        # Test invalid user_ids
        assert not validator.validate_user_id("user with spaces")
        assert not validator.validate_user_id("user@domain.com")
        assert not validator.validate_user_id("")
        assert not validator.validate_user_id(None)
        
        # Test command data sanitization
        dirty_data = {
            "command_id": "  cmd_001  ",
            "user_id": "test_user",
            "dangerous_field": "should_be_removed",
            "command_type": "x" * 2000  # Too long
        }
        
        clean_data = validator.sanitize_command_data(dirty_data)
        
        assert clean_data["command_id"] == "cmd_001"
        assert clean_data["user_id"] == "test_user"
        assert "dangerous_field" not in clean_data
        assert len(clean_data["command_type"]) <= 1000
        
        # Test secure command ID generation
        cmd_id = validator.generate_secure_command_id()
        assert cmd_id.startswith("cmd_")
        assert len(cmd_id) == 20  # cmd_ + 16 hex chars
    
    def test_enhanced_error_handling(self):
        """Test comprehensive error handling"""
        repository = MobileCommandHistoryRepository()
        
        # Test invalid inputs
        with pytest.raises(ValueError):
            repository.store_command(None)
        
        with pytest.raises(TypeError):
            repository.store_command("not_a_dict")
        
        with pytest.raises(ValueError):
            repository.store_command({})
        
        with pytest.raises(ValueError):
            repository.get_command_history("")
        
        with pytest.raises(ValueError):
            repository.command_exists("")
        
        with pytest.raises(ValueError):
            repository.delete_command("")
    
    def test_context_engine_integration_readiness(self):
        """Test Context Engine integration preparation"""
        repository = MobileCommandHistoryRepository()
        
        # Store command and verify context-ready metadata
        cmd_id = repository.store_command({
            "user_id": "test_user",
            "command_type": "context_test",
            "metadata": {"context_data": "test"}
        })
        
        history = repository.get_command_history("test_user")
        command = history[0]
        
        # Verify context-ready fields
        assert command["context_ready"] is True
        assert command["version"] == "1.0"
        assert command["security_validated"] is True
        assert "stored_at" in command
        assert "retrieved_at" in command