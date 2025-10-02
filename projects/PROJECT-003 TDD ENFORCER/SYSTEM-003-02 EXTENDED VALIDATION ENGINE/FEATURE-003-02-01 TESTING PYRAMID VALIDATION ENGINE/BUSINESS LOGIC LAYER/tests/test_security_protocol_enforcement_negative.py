"""
Security Protocol Service Negative Tests - TDD Iteration 7
Layer: LAY-003-02-01-002 (Business Logic)
Requirements: REQ-SEC-DATA-001, REQ-SEC-DATA-002
TDD Phase: REFACTOR (Negative test cases)
"""
import sys
from pathlib import Path

import pytest

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from business_logic.security_protocol_service import (
    SecurityProtocolService
)


class TestSecurityProtocolEnforcementNegative:
    """Negative test cases for Security Protocol enforcement."""
    
    def test_enforce_data_encryption_invalid_input_type(self):
        """TypeError when sensitive_data is not a dict"""
        security_service = SecurityProtocolService()
        
        with pytest.raises(TypeError, match="sensitive_data must be dict"):
            security_service.enforce_data_encryption("not_a_dict")
    
    def test_enforce_data_encryption_empty_dict(self):
        """ValueError when sensitive_data is empty"""
        security_service = SecurityProtocolService()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            security_service.enforce_data_encryption({})
    
    def test_validate_access_permissions_invalid_input_type(self):
        """TypeError when access_request is not a dict"""
        security_service = SecurityProtocolService()
        
        with pytest.raises(TypeError, match="access_request must be dict"):
            security_service.validate_access_permissions("not_a_dict")
    
    def test_validate_access_permissions_no_user_id(self):
        """ValueError when user_id field missing"""
        security_service = SecurityProtocolService()
        access_request = {
            "requested_operation": "read",
            "resource": "data"
        }
        
        with pytest.raises(ValueError, match="must contain 'user_id'"):
            security_service.validate_access_permissions(access_request)
    
    def test_validate_access_permissions_empty_user_id(self):
        """Returns False when user_id is empty"""
        security_service = SecurityProtocolService()
        access_request = {
            "user_id": "",
            "requested_operation": "read"
        }
        
        result = security_service.validate_access_permissions(
            access_request
        )
        assert result is False
    
    def test_validate_access_permissions_whitespace_user_id(self):
        """Returns False when user_id is only whitespace"""
        security_service = SecurityProtocolService()
        access_request = {
            "user_id": "   ",
            "requested_operation": "read"
        }
        
        result = security_service.validate_access_permissions(
            access_request
        )
        assert result is False
    
    def test_audit_security_event_invalid_input_type(self):
        """TypeError when security_event is not a dict"""
        security_service = SecurityProtocolService()
        
        with pytest.raises(TypeError, match="security_event must be dict"):
            security_service.audit_security_event("not_a_dict")
    
    def test_audit_security_event_no_event_type(self):
        """ValueError when event_type field missing"""
        security_service = SecurityProtocolService()
        security_event = {
            "user_id": "user_123",
            "resource": "data"
        }
        
        with pytest.raises(ValueError, match="must contain 'event_type'"):
            security_service.audit_security_event(security_event)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
