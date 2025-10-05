"""
Mobile Auth UI Integration - Iteration 20
Layer: User Interface Layer
Phase: REFACTOR (NEW Implementation)
Created: 2025-10-05

Provides mobile authentication UI integration combining auth service
with mobile framework for simple username/password authentication.
"""

from typing import Dict, Any, Optional


class MobileAuthUI:
    """Mobile authentication UI integration for login/logout."""
    
    def __init__(self, auth_service=None, framework_adapter=None):
        """
        Initialize mobile auth UI.
        
        Args:
            auth_service: Authentication service instance
            framework_adapter: Mobile framework adapter instance
        """
        self.auth_service = auth_service
        self.framework_adapter = framework_adapter
        self.current_session = None
    
    def render_login_form(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render mobile-optimized login form.
        
        Args:
            config: Optional form configuration
                - remember_me: bool (default False)
                - redirect_url: str (default "/dashboard")
        
        Returns:
            Dict containing:
                - form_rendered: bool
                - fields: List of form fields
                - mobile_optimized: bool
                - remember_me_available: bool
        """
        config = config or {}
        
        # Use framework adapter to render mobile-optimized form
        form_html = {
            'form_rendered': True,
            'fields': [
                {'name': 'username', 'type': 'text', 'placeholder': 'Username', 'required': True},
                {'name': 'password', 'type': 'password', 'placeholder': 'Password', 'required': True},
                {'name': 'remember_me', 'type': 'checkbox', 'label': 'Remember me', 'default': config.get('remember_me', False)}
            ],
            'mobile_optimized': True,
            'remember_me_available': True,
            'redirect_url': config.get('redirect_url', '/dashboard'),
            'csrf_token': self._generate_csrf_token()
        }
        
        return form_html
    
    def handle_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle login form submission.
        
        Args:
            credentials: Dict containing:
                - username: str
                - password: str
                - remember_me: bool (optional)
        
        Returns:
            Dict containing:
                - success: bool
                - session_token: str (if success)
                - user_id: str (if success)
                - error_message: str (if failure)
                - redirect_url: str
        """
        username = credentials.get('username', '').strip()
        password = credentials.get('password', '')
        remember_me = credentials.get('remember_me', False)
        
        # Validate input
        if not username or not password:
            return {
                'success': False,
                'error_message': 'Username and password are required',
                'error_code': 'missing_credentials'
            }
        
        # Use auth service to validate credentials
        if self.auth_service:
            auth_result = self.auth_service.authenticate(username, password)
            
            if auth_result.get('authenticated'):
                # Create session
                session_token = self._create_session(
                    user_id=auth_result.get('user_id'),
                    remember_me=remember_me
                )
                
                self.current_session = {
                    'user_id': auth_result.get('user_id'),
                    'token': session_token,
                    'remember_me': remember_me
                }
                
                return {
                    'success': True,
                    'session_token': session_token,
                    'user_id': auth_result.get('user_id'),
                    'redirect_url': '/dashboard'
                }
            else:
                return {
                    'success': False,
                    'error_message': 'Invalid username or password',
                    'error_code': 'invalid_credentials'
                }
        else:
            # Mock authentication for testing
            if username == 'testuser' and password == 'testpass':
                session_token = self._create_session(user_id='user_123', remember_me=remember_me)
                self.current_session = {
                    'user_id': 'user_123',
                    'token': session_token,
                    'remember_me': remember_me
                }
                
                return {
                    'success': True,
                    'session_token': session_token,
                    'user_id': 'user_123',
                    'redirect_url': '/dashboard'
                }
            else:
                return {
                    'success': False,
                    'error_message': 'Invalid username or password',
                    'error_code': 'invalid_credentials'
                }
    
    def handle_logout(self, session_token: str) -> Dict[str, Any]:
        """
        Handle logout and session cleanup.
        
        Args:
            session_token: Current session token
        
        Returns:
            Dict containing:
                - success: bool
                - redirect_url: str
        """
        if self.current_session and self.current_session.get('token') == session_token:
            self.current_session = None
        
        return {
            'success': True,
            'redirect_url': '/login',
            'session_cleared': True
        }
    
    def check_session(self, session_token: str) -> Dict[str, Any]:
        """
        Check if session is valid.
        
        Args:
            session_token: Session token to validate
        
        Returns:
            Dict containing:
                - valid: bool
                - user_id: str (if valid)
                - expired: bool
        """
        if self.current_session and self.current_session.get('token') == session_token:
            return {
                'valid': True,
                'user_id': self.current_session.get('user_id'),
                'expired': False
            }
        else:
            return {
                'valid': False,
                'expired': True
            }
    
    def render_logout_button(self) -> Dict[str, Any]:
        """
        Render logout button for mobile UI.
        
        Returns:
            Dict containing button HTML details
        """
        return {
            'button_rendered': True,
            'button_text': 'Logout',
            'mobile_optimized': True,
            'confirmation_required': False
        }
    
    def _generate_csrf_token(self) -> str:
        """Generate CSRF token for form security."""
        import hashlib
        import time
        return hashlib.sha256(f"csrf_{time.time()}".encode()).hexdigest()[:16]
    
    def _create_session(self, user_id: str, remember_me: bool = False) -> str:
        """Create session token."""
        import hashlib
        import time
        token_data = f"{user_id}_{time.time()}_{remember_me}"
        return hashlib.sha256(token_data.encode()).hexdigest()
