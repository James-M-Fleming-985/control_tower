from datetime import datetime
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import sys
sys.path.append('/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/src')
from data_access.mobile_command_history_repository import (
    MobileCommandHistoryRepository
)


class TestMobileCommandAuditTrail:
    
    def test_create_audit_trail_entry_green_phase(self):
        """GREEN: Audit trail creation should work with valid data"""
        repository = MobileCommandHistoryRepository()
        audit_data = {
            "command_id": "cmd_003",
            "audit_event": "command_executed",
            "user_id": "user_123",
            "session_id": "sess_456",
            "audit_metadata": {
                "before_state": {},
                "after_state": {},
                "change_summary": "Command validation executed"
            }
        }
        
        # GREEN: This should succeed and return an audit ID
        audit_id = repository.create_audit_entry(audit_data)
        
        # Validate the returned audit ID
        assert audit_id is not None
        assert isinstance(audit_id, str)
        assert audit_id.startswith("audit_")
        assert len(audit_id) > 6  # audit_ + some hex chars
    
    def test_get_audit_trail_green_phase(self):
        """GREEN: Audit trail retrieval should return audit entries"""
        repository = MobileCommandHistoryRepository()
        
        # First create an audit entry
        audit_data = {
            "command_id": "cmd_003",
            "audit_event": "command_executed",
            "user_id": "user_123",
            "session_id": "sess_456"
        }
        
        repository.create_audit_entry(audit_data)
        
        # GREEN: This should succeed and return audit entries
        audit_trail = repository.get_audit_trail("cmd_003")
        
        # Validate the audit trail
        assert isinstance(audit_trail, list)
        assert len(audit_trail) == 1
        assert audit_trail[0]["command_id"] == "cmd_003"
        assert audit_trail[0]["audit_event"] == "command_executed"
        assert audit_trail[0]["user_id"] == "user_123"
        assert "audit_id" in audit_trail[0]
    
    def test_audit_compliance_validation_green_phase(self):
        """GREEN: Compliance validation should return validation results"""
        repository = MobileCommandHistoryRepository()
        
        # Store a command first
        command_data = {
            "command_id": "cmd_003",
            "user_id": "user_123",
            "command_type": "validation",
            "timestamp": datetime.now().isoformat()
        }
        repository.store_command(command_data)
        
        # Create audit entry for the command
        audit_data = {
            "command_id": "cmd_003",
            "audit_event": "command_executed",
            "user_id": "user_123"
        }
        repository.create_audit_entry(audit_data)
        
        compliance_criteria = {
            "retention_period_days": 90,
            "required_fields": ["user_id", "timestamp", "command_type"],
            "security_level": "high"
        }
        
        # GREEN: This should succeed and return validation results
        validation_result = repository.validate_audit_compliance(
            "cmd_003", compliance_criteria)
        
        # Validate the compliance result
        assert isinstance(validation_result, dict)
        assert "command_id" in validation_result
        assert "compliance_status" in validation_result
        assert "validation_results" in validation_result
        assert validation_result["command_id"] == "cmd_003"
        expected_statuses = ["compliant", "non_compliant", "warning"]
        assert validation_result["compliance_status"] in expected_statuses
    
    def test_audit_trail_search_green_phase(self):
        """GREEN: Audit trail search should return matching entries"""
        repository = MobileCommandHistoryRepository()
        
        # Create multiple audit entries for search
        audit_entries = [
            {
                "command_id": "cmd_001",
                "audit_event": "command_executed",
                "user_id": "user_123",
                "timestamp": "2025-09-29T10:00:00Z"
            },
            {
                "command_id": "cmd_002",
                "audit_event": "validation_completed",
                "user_id": "user_123",
                "timestamp": "2025-09-29T11:00:00Z"
            },
            {
                "command_id": "cmd_003",
                "audit_event": "command_executed",
                "user_id": "user_456",
                "timestamp": "2025-09-29T12:00:00Z"
            }
        ]
        
        for audit_data in audit_entries:
            repository.create_audit_entry(audit_data)
        
        search_criteria = {
            "date_range": {
                "start": "2025-09-29T00:00:00Z",
                "end": "2025-09-29T23:59:59Z"
            },
            "user_id": "user_123",
            "audit_events": ["command_executed", "validation_completed"]
        }
        
        # GREEN: This should succeed and return matching entries
        search_results = repository.search_audit_trail(search_criteria)
        
        # Validate the search results
        assert isinstance(search_results, list)
        assert len(search_results) == 2  # Should match 2 entries for user_123
        
        # Verify all results match the criteria
        for entry in search_results:
            assert entry["user_id"] == "user_123"
            expected_events = ["command_executed", "validation_completed"]
            assert entry["audit_event"] in expected_events
            assert "2025-09-29" in entry["timestamp"]
