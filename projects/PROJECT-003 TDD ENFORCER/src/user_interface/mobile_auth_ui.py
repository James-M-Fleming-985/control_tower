"""
Mobile Auth UI Integration (Iteration 20)
Combines Mobile Authentication + Responsive Framework into UI component.

Requirements covered:
- REQ-UI-001: Responsive Mobile Interface (Auth flow)
- Integration of Iterations 17 + 18
"""

from typing import Dict, Any
from src.user_interface.mobile_authentication_refactored import (
    MobileAuthenticationInterface
)
from src.user_interface.responsive_web_framework import (
    ResponsiveWebFramework
)


class MobileAuthUI:
    """
    Complete mobile authentication UI with responsive framework.
    Simplified for internal use (1-2 users).
    """

    def __init__(self):
        self.auth = MobileAuthenticationInterface()
        self.framework = ResponsiveWebFramework()
        self.framework.enable_service_worker()  # Enable PWA
        self.current_user = None

    def render_login_form(self) -> str:
        """Generate responsive login form HTML."""
        return f"""
        <div class="container">
            <form id="login-form" class="responsive-grid">
                <h2>TDD Enforcer Login</h2>

                <div class="form-group">
                    <label for="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        class="btn"
                        required
                        autocomplete="username"
                    >
                </div>

                <div class="form-group">
                    <label for="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        class="btn"
                        required
                        autocomplete="current-password"
                    >
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" id="remember_me" name="remember_me">
                        Remember me for 7 days
                    </label>
                </div>

                <button type="submit" class="btn btn-primary">
                    Login
                </button>
            </form>
        </div>
        """

    def handle_login(
        self,
        username: str,
        password: str,
        remember_me: bool = False
    ) -> Dict[str, Any]:
        """
        Process login form submission.
        Returns login result with UI feedback message.
        """
        result = self.auth.login(username, password, remember_me)

        if result['success']:
            self.current_user = username
            return {
                'success': True,
                'message': f'Welcome, {username}!',
                'session_token': result['session_token'],
                'redirect_url': '/dashboard'
            }
        else:
            return {
                'success': False,
                'message': result.get('error', 'Login failed'),
                'error_type': 'authentication'
            }

    def render_logout_button(self) -> str:
        """Generate responsive logout button."""
        if not self.current_user:
            return ""

        return f"""
        <div class="container">
            <div class="user-info">
                Logged in as: <strong>{self.current_user}</strong>
            </div>
            <button id="logout-btn" class="btn btn-secondary">
                Logout
            </button>
        </div>
        """

    def handle_logout(self, session_token: str) -> Dict[str, Any]:
        """
        Process logout request.
        Returns logout result with UI feedback.
        """
        result = self.auth.logout(session_token)

        if result['success']:
            self.current_user = None
            return {
                'success': True,
                'message': 'Logged out successfully',
                'redirect_url': '/login'
            }
        else:
            return {
                'success': False,
                'message': 'Logout failed',
                'error_type': 'session'
            }

    def render_session_status(self, session_token: str) -> str:
        """Generate HTML showing current session status."""
        session_info = self.auth.get_session_info(session_token)

        if not session_info['valid']:
            return """
            <div class="container">
                <div class="alert alert-warning">
                    Session expired. Please login again.
                </div>
            </div>
            """

        return f"""
        <div class="container">
            <div class="session-status">
                <p>User: {session_info['user_id']}</p>
                <p>Time remaining: {session_info['remaining_time']:.0f} seconds</p>
                <p>Remember me: {'Yes' if self.auth.is_remember_me_enabled() else 'No'}</p>
            </div>
        </div>
        """

    def render_complete_page(
        self,
        page_type: str = "login",
        session_token: str = None
    ) -> str:
        """
        Generate complete responsive HTML page.
        page_type: 'login', 'dashboard', or 'session_status'
        """
        if page_type == "login":
            content = self.render_login_form()
        elif page_type == "dashboard":
            content = self.render_logout_button()
        elif page_type == "session_status" and session_token:
            content = self.render_session_status(session_token)
        else:
            content = "<div>Invalid page type</div>"

        # Get base template
        template = self.framework.get_responsive_html_template("TDD Enforcer")

        # Insert content into template
        return template.replace(
            '<!-- Content goes here -->',
            content
        )

    def validate_form_data(
        self,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Client-side validation before submission.
        Returns validation result.
        """
        errors = []

        if not username or len(username.strip()) == 0:
            errors.append("Username is required")

        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def is_logged_in(self) -> bool:
        """Check if user is currently logged in."""
        return self.current_user is not None

    def get_current_user(self) -> str:
        """Get current logged-in user."""
        return self.current_user
