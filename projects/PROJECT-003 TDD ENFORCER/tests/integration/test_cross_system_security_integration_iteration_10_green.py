"""
Cross-System Security Integration - TDD Iteration 10 - REFACTOR Phase Tests
Tests for cross-system security protocol integration with validation tests
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent.parent / "src" / "integration"
sys.path.insert(0, str(src_path))

from cross_system_security_integration_iteration_10 import (
    CrossSystemSecurityIntegration
)


class TestCrossSystemSecurityIntegrationGreen:
    """GREEN Phase: Tests should pass with implementation"""
    
    def test_integrate_security_across_systems_returns_valid_response(self):
        """GREEN: Cross-system security integration returns valid response"""
        security_integration = CrossSystemSecurityIntegration()
        integration_request = {
            "systems": ["mobile_app", "context_engine", "validation_engine"],
            "security_level": "high",
            "encryption_requirements": {
                "data_at_rest": "AES-256",
                "data_in_transit": "TLS-1.3"
            }
        }
        
        result = security_integration.integrate_security_across_systems(
            integration_request
        )
        
        # Validate response structure
        assert isinstance(result, dict)
        assert "integration_status" in result
        assert "systems_integrated" in result
        assert "security_config" in result
        assert "integration_timestamp" in result
        
        # Validate integration status
        assert result["integration_status"] in ["success", "partial", "failed"]
        assert result["integration_status"] == "success"
        
        # Validate systems integrated
        assert isinstance(result["systems_integrated"], list)
        assert len(result["systems_integrated"]) == 3
        assert "mobile_app" in result["systems_integrated"]
        assert "context_engine" in result["systems_integrated"]
        assert "validation_engine" in result["systems_integrated"]
        
        # Validate security config
        assert isinstance(result["security_config"], dict)
        assert "level" in result["security_config"]
        assert result["security_config"]["level"] == "high"
        assert "encryption_at_rest" in result["security_config"]
        assert result["security_config"]["encryption_at_rest"] == "AES-256"
        assert "encryption_in_transit" in result["security_config"]
        assert result["security_config"]["encryption_in_transit"] == "TLS-1.3"
        
        # Validate timestamp
        assert isinstance(result["integration_timestamp"], str)
        assert "T" in result["integration_timestamp"]
    
    def test_validate_cross_system_permissions_returns_valid_response(self):
        """GREEN: Cross-system permission validation returns valid response"""
        security_integration = CrossSystemSecurityIntegration()
        permission_request = {
            "user_id": "user_123",
            "source_system": "mobile_app",
            "target_system": "context_engine",
            "requested_operations": ["read_context", "update_context"]
        }
        
        result = security_integration.validate_cross_system_permissions(
            permission_request
        )
        
        # Validate response structure
        assert isinstance(result, dict)
        assert "permission_granted" in result
        assert "granted_operations" in result
        assert "denied_operations" in result
        assert "permission_level" in result
        assert "validation_timestamp" in result
        
        # Validate permission granted
        assert isinstance(result["permission_granted"], bool)
        assert result["permission_granted"] is True
        
        # Validate granted operations
        assert isinstance(result["granted_operations"], list)
        assert len(result["granted_operations"]) == 2
        assert "read_context" in result["granted_operations"]
        assert "update_context" in result["granted_operations"]
        
        # Validate denied operations
        assert isinstance(result["denied_operations"], list)
        assert len(result["denied_operations"]) == 0
        
        # Validate permission level
        assert isinstance(result["permission_level"], str)
        assert result["permission_level"] in ["admin", "write", "read", "none"]
        assert result["permission_level"] == "write"
        
        # Validate timestamp
        assert isinstance(result["validation_timestamp"], str)
        assert "T" in result["validation_timestamp"]
    
    def test_audit_cross_system_security_events_returns_valid_response(self):
        """GREEN: Cross-system security event auditing returns valid response"""
        security_integration = CrossSystemSecurityIntegration()
        security_event = {
            "event_type": "cross_system_access",
            "source_system": "mobile_app",
            "target_system": "validation_engine",
            "user_id": "user_123",
            "risk_assessment": "medium"
        }
        
        result = security_integration.audit_cross_system_security_event(
            security_event
        )
        
        # Validate response structure
        assert isinstance(result, dict)
        assert "audit_recorded" in result
        assert "audit_id" in result
        assert "risk_level" in result
        assert "actions_taken" in result
        assert "audit_timestamp" in result
        
        # Validate audit recorded
        assert isinstance(result["audit_recorded"], bool)
        assert result["audit_recorded"] is True
        
        # Validate audit ID
        assert isinstance(result["audit_id"], str)
        assert len(result["audit_id"]) > 0
        assert result["audit_id"].startswith("audit_")
        
        # Validate risk level
        assert isinstance(result["risk_level"], str)
        assert result["risk_level"] in ["high", "medium", "low"]
        assert result["risk_level"] == "medium"
        
        # Validate actions taken
        assert isinstance(result["actions_taken"], list)
        assert len(result["actions_taken"]) > 0
        assert "log_event" in result["actions_taken"]
        assert "notify_security_team" in result["actions_taken"]
        
        # Validate timestamp
        assert isinstance(result["audit_timestamp"], str)
        assert "T" in result["audit_timestamp"]


class TestCrossSystemSecurityIntegrationValidation:
    """REFACTOR Phase: Input validation and error handling tests"""
    
    def test_integrate_security_invalid_request_type(self):
        """Test integrate_security raises TypeError for non-dict request"""
        security_integration = CrossSystemSecurityIntegration()
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            security_integration.integrate_security_across_systems("invalid")
    
    def test_integrate_security_invalid_systems_type(self):
        """Test integrate_security raises ValueError for invalid systems"""
        security_integration = CrossSystemSecurityIntegration()
        
        with pytest.raises(
            ValueError, match="All systems must be strings"
        ):
            security_integration.integrate_security_across_systems({
                "systems": ["valid", 123],
                "security_level": "high"
            })
    
    def test_integrate_security_invalid_encryption_type(self):
        """Test integrate_security raises TypeError for invalid encryption"""
        security_integration = CrossSystemSecurityIntegration()
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            security_integration.integrate_security_across_systems({
                "systems": ["system1"],
                "encryption_requirements": "invalid"
            })
    
    def test_validate_permissions_invalid_request_type(self):
        """Test validate_permissions raises TypeError for non-dict request"""
        security_integration = CrossSystemSecurityIntegration()
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            security_integration.validate_cross_system_permissions("invalid")
    
    def test_validate_permissions_invalid_operations_type(self):
        """Test validate_permissions raises TypeError for invalid ops"""
        security_integration = CrossSystemSecurityIntegration()
        
        with pytest.raises(TypeError, match="must be a list"):
            security_integration.validate_cross_system_permissions({
                "user_id": "user_123",
                "requested_operations": "invalid"
            })
    
    def test_validate_permissions_invalid_operation_item(self):
        """Test validate_permissions raises ValueError for invalid op item"""
        security_integration = CrossSystemSecurityIntegration()
        
        with pytest.raises(ValueError, match="must be strings"):
            security_integration.validate_cross_system_permissions({
                "user_id": "user_123",
                "requested_operations": ["read", 123]
            })
    
    def test_audit_event_invalid_type(self):
        """Test audit_event raises TypeError for non-dict event"""
        security_integration = CrossSystemSecurityIntegration()
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            security_integration.audit_cross_system_security_event("invalid")
    
    def test_validate_permissions_no_user_id(self):
        """Test validate_permissions returns denial for missing user_id"""
        security_integration = CrossSystemSecurityIntegration()
        
        result = security_integration.validate_cross_system_permissions({
            "requested_operations": ["read_context"]
        })
        
        assert result["permission_granted"] is False
        assert result["permission_level"] == "none"
        assert len(result["granted_operations"]) == 0
    
    def test_integrate_security_empty_systems(self):
        """Test integrate_security handles empty systems list"""
        security_integration = CrossSystemSecurityIntegration()
        
        result = security_integration.integrate_security_across_systems({
            "systems": [],
            "security_level": "high"
        })
        
        assert result["integration_status"] == "failed"
        assert len(result["systems_integrated"]) == 0


class TestCrossSystemSecurityIntegrationSecurity:
    """REFACTOR Phase: Security-specific tests"""
    
    def test_permission_denial_for_delete_operations(self):
        """Test that delete operations are denied for write-level users"""
        security_integration = CrossSystemSecurityIntegration()
        permission_request = {
            "user_id": "user_123",
            "source_system": "mobile_app",
            "target_system": "context_engine",
            "requested_operations": ["read_context", "delete_context"]
        }
        
        result = security_integration.validate_cross_system_permissions(
            permission_request
        )
        
        assert result["permission_granted"] is False
        assert "read_context" in result["granted_operations"]
        assert "delete_context" in result["denied_operations"]
    
    def test_high_risk_events_trigger_blocking(self):
        """Test high risk events trigger user blocking action"""
        security_integration = CrossSystemSecurityIntegration()
        security_event = {
            "event_type": "unauthorized_access",
            "source_system": "mobile_app",
            "target_system": "validation_engine",
            "user_id": "user_456",
            "risk_assessment": "high"
        }
        
        result = security_integration.audit_cross_system_security_event(
            security_event
        )
        
        assert result["audit_recorded"] is True
        assert result["risk_level"] == "high"
        assert "log_event" in result["actions_taken"]
        assert "alert_admin" in result["actions_taken"]
        assert "block_user" in result["actions_taken"]
        assert len(result["actions_taken"]) == 3
    
    def test_audit_id_uniqueness(self):
        """Test that audit IDs are unique across multiple events"""
        security_integration = CrossSystemSecurityIntegration()
        security_event = {
            "event_type": "access_attempt",
            "source_system": "mobile_app",
            "target_system": "context_engine",
            "user_id": "user_789",
            "risk_assessment": "low"
        }
        
        result1 = security_integration.audit_cross_system_security_event(
            security_event
        )
        result2 = security_integration.audit_cross_system_security_event(
            security_event
        )
        
        assert result1["audit_id"] != result2["audit_id"]
        assert result1["audit_id"].startswith("audit_")
        assert result2["audit_id"].startswith("audit_")
    
    def test_encryption_standard_validation(self):
        """Test that encryption standards are properly applied"""
        security_integration = CrossSystemSecurityIntegration()
        integration_request = {
            "systems": ["system1", "system2"],
            "security_level": "high",
            "encryption_requirements": {
                "data_at_rest": "AES-256",
                "data_in_transit": "TLS-1.3"
            }
        }
        
        result = security_integration.integrate_security_across_systems(
            integration_request
        )
        
        assert result["security_config"]["encryption_at_rest"] == "AES-256"
        assert (
            result["security_config"]["encryption_in_transit"] == "TLS-1.3"
        )
    
    def test_low_risk_events_minimal_action(self):
        """Test low risk events only trigger logging"""
        security_integration = CrossSystemSecurityIntegration()
        security_event = {
            "event_type": "routine_access",
            "source_system": "mobile_app",
            "target_system": "context_engine",
            "user_id": "user_111",
            "risk_assessment": "low"
        }
        
        result = security_integration.audit_cross_system_security_event(
            security_event
        )
        
        assert result["audit_recorded"] is True
        assert result["risk_level"] == "low"
        assert result["actions_taken"] == ["log_event"]
        assert len(result["actions_taken"]) == 1

