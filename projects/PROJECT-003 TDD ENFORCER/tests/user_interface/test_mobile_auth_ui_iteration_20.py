"""
Tests for Mobile Auth UI Integration (Iteration 20)
"""

import pytest
from src.user_interface.mobile_auth_ui import MobileAuthUI


class TestMobileAuthUI:
    """Test mobile authentication UI integration."""

    def setup_method(self):
        """Setup test UI instance."""
        self.ui = MobileAuthUI()

    def test_render_login_form(self):
        """Test login form HTML generation."""
        form_html = self.ui.render_login_form()

        assert '<form id="login-form"' in form_html
        assert 'type="text"' in form_html  # Username field
        assert 'type="password"' in form_html  # Password field
        assert 'type="checkbox"' in form_html  # Remember me
        assert 'type="submit"' in form_html  # Submit button

    def test_handle_login_success(self):
        """Test successful login handling."""
        result = self.ui.handle_login("testuser", "password123", False)

        assert result['success'] is True
        assert 'Welcome' in result['message']
        assert 'session_token' in result
        assert result['redirect_url'] == '/dashboard'

    def test_handle_login_sets_current_user(self):
        """Test login sets current user."""
        self.ui.handle_login("testuser", "password123")

        assert self.ui.is_logged_in()
        assert self.ui.get_current_user() == "testuser"

    def test_handle_login_failure(self):
        """Test failed login handling."""
        result = self.ui.handle_login("testuser", "wrong")

        assert result['success'] is False
        # Message should indicate auth problem (invalid_credentials, error, or fail)
        msg_lower = result['message'].lower()
        assert ('invalid' in msg_lower or 'error' in msg_lower or
                'fail' in msg_lower)
        assert result['error_type'] == 'authentication'

    def test_handle_login_failure_no_user_set(self):
        """Test failed login doesn't set current user."""
        self.ui.handle_login("testuser", "short")

        assert not self.ui.is_logged_in()
        assert self.ui.get_current_user() is None

    def test_render_logout_button_when_logged_in(self):
        """Test logout button renders when logged in."""
        self.ui.handle_login("testuser", "password123")
        logout_html = self.ui.render_logout_button()

        assert 'testuser' in logout_html
        assert 'logout-btn' in logout_html

    def test_render_logout_button_when_not_logged_in(self):
        """Test logout button empty when not logged in."""
        logout_html = self.ui.render_logout_button()

        assert logout_html == ""

    def test_handle_logout_success(self):
        """Test successful logout."""
        login_result = self.ui.handle_login("testuser", "password123")
        session_token = login_result['session_token']

        logout_result = self.ui.handle_logout(session_token)

        assert logout_result['success'] is True
        assert 'Logged out' in logout_result['message']
        assert logout_result['redirect_url'] == '/login'

    def test_handle_logout_clears_current_user(self):
        """Test logout clears current user."""
        login_result = self.ui.handle_login("testuser", "password123")
        self.ui.handle_logout(login_result['session_token'])

        assert not self.ui.is_logged_in()
        assert self.ui.get_current_user() is None

    def test_render_session_status_valid(self):
        """Test session status rendering for valid session."""
        login_result = self.ui.handle_login("testuser", "password123")
        status_html = self.ui.render_session_status(login_result['session_token'])

        assert 'testuser' in status_html
        assert 'Time remaining' in status_html

    def test_render_session_status_invalid(self):
        """Test session status for invalid token."""
        status_html = self.ui.render_session_status("invalid-token")

        assert 'expired' in status_html.lower() or 'login' in status_html.lower()

    def test_render_complete_login_page(self):
        """Test complete login page generation."""
        page_html = self.ui.render_complete_page("login")

        assert '<!DOCTYPE html>' in page_html
        assert '<meta name="viewport"' in page_html
        assert '<form id="login-form"' in page_html
        assert 'manifest.json' in page_html  # PWA enabled

    def test_render_complete_dashboard_page(self):
        """Test complete dashboard page generation."""
        self.ui.handle_login("testuser", "password123")
        page_html = self.ui.render_complete_page("dashboard")

        assert '<!DOCTYPE html>' in page_html
        assert 'logout-btn' in page_html

    def test_render_complete_session_status_page(self):
        """Test complete session status page."""
        login_result = self.ui.handle_login("testuser", "password123")
        page_html = self.ui.render_complete_page(
            "session_status",
            login_result['session_token']
        )

        assert '<!DOCTYPE html>' in page_html
        assert 'testuser' in page_html

    def test_validate_form_data_success(self):
        """Test form validation with valid data."""
        result = self.ui.validate_form_data("testuser", "password123")

        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_validate_form_data_missing_username(self):
        """Test validation fails on missing username."""
        result = self.ui.validate_form_data("", "password123")

        assert result['valid'] is False
        assert any('username' in err.lower() for err in result['errors'])

    def test_validate_form_data_short_password(self):
        """Test validation fails on short password."""
        result = self.ui.validate_form_data("testuser", "short")

        assert result['valid'] is False
        assert any('password' in err.lower() for err in result['errors'])

    def test_validate_form_data_multiple_errors(self):
        """Test validation returns all errors."""
        result = self.ui.validate_form_data("", "short")

        assert result['valid'] is False
        assert len(result['errors']) >= 2

    def test_pwa_enabled_by_default(self):
        """Test PWA features enabled in framework."""
        assert self.ui.framework.is_pwa_enabled()
