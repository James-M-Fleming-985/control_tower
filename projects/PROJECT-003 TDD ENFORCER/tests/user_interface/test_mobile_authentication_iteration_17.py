"""
Tests for Mobile Authentication Interface - Iteration 17
Simplified for internal use (1-2 users)
"""

import pytest
import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.user_interface.mobile_authentication_refactored import MobileAuthenticationInterface


class TestMobileAuthenticationSimplified:
    """Tests for simplified mobile authentication"""
    
    def test_successful_login(self):
        """Should successfully login with valid credentials"""
        auth = MobileAuthenticationInterface()
        
        result = auth.login('testuser', 'validpassword123')
        
        assert result['success'] is True
        assert 'session_token' in result
        assert result['session_token'] is not None
        assert result['user_id'] == 'testuser'
        assert 'expires_at' in result
    
    def test_login_with_remember_me(self):
        """Should extend session when remember_me is True"""
        auth = MobileAuthenticationInterface()
        
        result = auth.login('testuser', 'validpassword123', remember_me=True)
        
        assert result['success'] is True
        assert result['remember_me'] is True
        assert auth.is_remember_me_enabled() is True
    
    def test_login_failure_invalid_credentials(self):
        """Should fail login with invalid credentials"""
        auth = MobileAuthenticationInterface()
        
        # Short password (< 8 chars) should fail
        result = auth.login('testuser', 'short')
        
        assert result['success'] is False
        assert 'error' in result
        assert result['session_token'] is None
    
    def test_login_missing_username(self):
        """Should fail when username is missing"""
        auth = MobileAuthenticationInterface()
        
        result = auth.login('', 'password123')
        
        assert result['success'] is False
        assert result['error'] == 'Username is required'
    
    def test_login_missing_password(self):
        """Should fail when password is missing"""
        auth = MobileAuthenticationInterface()
        
        result = auth.login('testuser', '')
        
        assert result['success'] is False
        assert result['error'] == 'Password is required'
    
    def test_session_validation(self):
        """Should validate active session"""
        auth = MobileAuthenticationInterface()
        
        login_result = auth.login('testuser', 'validpassword123')
        session_token = login_result['session_token']
        
        validation = auth.validate_session(session_token)
        
        assert validation['valid'] is True
        assert validation['user_id'] == 'testuser'
        assert validation['remaining_time'] > 0
    
    def test_session_validation_invalid_token(self):
        """Should reject invalid session token"""
        auth = MobileAuthenticationInterface()
        
        validation = auth.validate_session('invalid_token')
        
        assert validation['valid'] is False
        assert 'error' in validation
    
    def test_logout(self):
        """Should successfully logout and terminate session"""
        auth = MobileAuthenticationInterface()
        
        login_result = auth.login('testuser', 'validpassword123')
        session_token = login_result['session_token']
        
        logout_result = auth.logout(session_token)
        
        assert logout_result['success'] is True
        assert auth.get_current_user() is None
        
        # Session should no longer be valid
        validation = auth.validate_session(session_token)
        assert validation['valid'] is False
    
    def test_get_current_user(self):
        """Should return current logged in user"""
        auth = MobileAuthenticationInterface()
        
        # No user initially
        assert auth.get_current_user() is None
        
        # User set after login
        auth.login('testuser', 'validpassword123')
        assert auth.get_current_user() == 'testuser'
    
    def test_get_session_info(self):
        """Should return detailed session information"""
        auth = MobileAuthenticationInterface()
        
        login_result = auth.login('testuser', 'validpassword123')
        session_token = login_result['session_token']
        
        info = auth.get_session_info(session_token)
        
        assert info['valid'] is True
        assert info['user_id'] == 'testuser'
        assert 'created_at' in info
        assert 'expires_at' in info
        assert 'last_activity' in info
        assert info['is_active'] is True
        assert info['remaining_time'] > 0
