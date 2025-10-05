"""
Tests for Mobile Auth UI Integration - Iteration 20
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.user_interface.mobile_auth_ui_integration import MobileAuthUI


class TestMobileAuthUI:
    """Test suite for Mobile Auth UI Integration"""
    
    @pytest.fixture
    def auth_ui(self):
        """Create MobileAuthUI instance"""
        return MobileAuthUI()
    
    def test_render_login_form_basic(self, auth_ui):
        """Should render basic login form"""
        result = auth_ui.render_login_form()
        
        assert result['form_rendered'] is True
        assert result['mobile_optimized'] is True
        assert len(result['fields']) == 3
        assert result['fields'][0]['name'] == 'username'
        assert result['fields'][1]['name'] == 'password'
        assert result['fields'][2]['name'] == 'remember_me'
    
    def test_render_login_form_with_remember_me(self, auth_ui):
        """Should render login form with remember me enabled"""
        result = auth_ui.render_login_form({'remember_me': True})
        
        assert result['remember_me_available'] is True
        remember_field = [f for f in result['fields'] if f['name'] == 'remember_me'][0]
        assert remember_field['default'] is True
    
    def test_handle_login_success(self, auth_ui):
        """Should successfully handle valid login"""
        credentials = {
            'username': 'testuser',
            'password': 'testpass',
            'remember_me': False
        }
        
        result = auth_ui.handle_login(credentials)
        
        assert result['success'] is True
        assert 'session_token' in result
        assert result['user_id'] == 'user_123'
        assert result['redirect_url'] == '/dashboard'
    
    def test_handle_login_invalid_credentials(self, auth_ui):
        """Should reject invalid credentials"""
        credentials = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        
        result = auth_ui.handle_login(credentials)
        
        assert result['success'] is False
        assert 'error_message' in result
        assert result['error_code'] == 'invalid_credentials'
    
    def test_handle_login_missing_credentials(self, auth_ui):
        """Should reject missing credentials"""
        result = auth_ui.handle_login({'username': '', 'password': ''})
        
        assert result['success'] is False
        assert result['error_code'] == 'missing_credentials'
    
    def test_handle_logout(self, auth_ui):
        """Should handle logout successfully"""
        # Login first
        login_result = auth_ui.handle_login({
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Logout
        result = auth_ui.handle_logout(login_result['session_token'])
        
        assert result['success'] is True
        assert result['redirect_url'] == '/login'
        assert result['session_cleared'] is True
    
    def test_check_session_valid(self, auth_ui):
        """Should validate active session"""
        # Login first
        login_result = auth_ui.handle_login({
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Check session
        result = auth_ui.check_session(login_result['session_token'])
        
        assert result['valid'] is True
        assert result['user_id'] == 'user_123'
        assert result['expired'] is False
    
    def test_check_session_invalid(self, auth_ui):
        """Should reject invalid session"""
        result = auth_ui.check_session('invalid_token')
        
        assert result['valid'] is False
        assert result['expired'] is True
    
    def test_render_logout_button(self, auth_ui):
        """Should render logout button"""
        result = auth_ui.render_logout_button()
        
        assert result['button_rendered'] is True
        assert result['mobile_optimized'] is True
        assert result['button_text'] == 'Logout'
