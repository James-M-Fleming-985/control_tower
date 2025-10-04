"""
Mobile Authentication Integration Tests - TDD Iteration 8
GREEN Phase: Tests validating minimal implementation
Layer: Integration Layer
Requirement: REQ-DATA-005 Mobile Session Management
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), '..', '..', 'src', 'integration'
    )
)

from mobile_auth_integration_iteration_8 import MobileAuthIntegration


class TestMobileAuthenticationIntegrationGreen:
    """GREEN Phase: Test that implementation works correctly"""
    
    def test_authenticate_mobile_user_returns_valid_response(self):
        """GREEN: Mobile authentication should return valid authentication response"""
        auth_integration = MobileAuthIntegration()
        auth_request = {
            "user_credentials": {
                "username": "user_123",
                "device_id": "mobile_abc"
            },
            "authentication_method": "biometric",
            "security_level": "high"
        }
        
        result = auth_integration.authenticate_mobile_user(auth_request)
        
        # Validate response structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "authenticated" in result, "Result should have 'authenticated' field"
        assert "session_id" in result, "Result should have 'session_id' field"
        assert "jwt_token" in result, "Result should have 'jwt_token' field"
        assert "user_id" in result, "Result should have 'user_id' field"
        assert "device_registered" in result, "Result should have 'device_registered'"
        assert "security_level" in result, "Result should have 'security_level'"
        
        # Validate response values
        assert result["authenticated"] is True, "Authentication should succeed"
        assert result["session_id"] != "", "Session ID should not be empty"
        assert result["jwt_token"] != "", "JWT token should not be empty"
        assert result["user_id"] == "user_123", "User ID should match username"
        assert result["device_registered"] is True, "Device should be registered"
        assert result["security_level"] == "high", "Security level should be preserved"
    
    def test_sync_session_across_platforms_returns_valid_response(self):
        """GREEN: Session sync should return valid sync response"""
        auth_integration = MobileAuthIntegration()
        sync_request = {
            "session_id": "sess_789",
            "source_platform": "mobile",
            "target_platforms": ["web", "api"]
        }
        
        result = auth_integration.sync_session_across_platforms(sync_request)
        
        # Validate response structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "session_id" in result, "Result should have 'session_id' field"
        assert "synced" in result, "Result should have 'synced' field"
        assert "sync_timestamp" in result, "Result should have 'sync_timestamp'"
        assert "platforms_synced" in result, "Result should have 'platforms_synced'"
        assert "sync_failures" in result, "Result should have 'sync_failures'"
        
        # Validate response values
        assert result["session_id"] == "sess_789", "Session ID should match"
        assert result["synced"] is True, "Sync should succeed"
        assert "web" in result["platforms_synced"], "'web' should be synced"
        assert "api" in result["platforms_synced"], "'api' should be synced"
        assert len(result["sync_failures"]) == 0, "No sync failures expected"
        assert result["sync_timestamp"] != "", "Sync timestamp should not be empty"
    
    def test_validate_mobile_security_context_returns_valid_response(self):
        """GREEN: Security context validation should return valid validation response"""
        auth_integration = MobileAuthIntegration()
        
        result = auth_integration.validate_mobile_security_context("sess_789")
        
        # Validate response structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "session_id" in result, "Result should have 'session_id' field"
        assert "valid" in result, "Result should have 'valid' field"
        assert "security_checks_passed" in result, "Result should have 'security_checks_passed'"
        assert "security_checks_failed" in result, "Result should have 'security_checks_failed'"
        assert "risk_level" in result, "Result should have 'risk_level'"
        assert "validation_timestamp" in result, "Result should have 'validation_timestamp'"
        assert "checks_performed" in result, "Result should have 'checks_performed'"
        
        # Validate response values
        assert result["session_id"] == "sess_789", "Session ID should match"
        assert result["valid"] is True, "Security context should be valid"
        assert result["security_checks_passed"] > 0, "Some checks should pass"
        assert result["security_checks_failed"] == 0, "No checks should fail for valid session"
        assert result["risk_level"] == "low", "Risk level should be low for valid session"
        assert len(result["checks_performed"]) > 0, "Should have performed checks"
        assert result["validation_timestamp"] != "", "Validation timestamp should not be empty"
