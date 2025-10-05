"""
Mobile Authentication - Simplified for Internal Use
Layer: User Interface Layer  
Phase: REFACTOR (Production Implementation)
Iteration: 17
Created: 2025-10-05

Simple username/password authentication for 1-2 internal users.
No biometric, no OAuth2, no MFA - just functional basics.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.business_logic.security_manager import AuthenticationService


class MobileAuthenticationInterface:
    """
    Simple mobile authentication for internal use.
    
    Features:
    - Username/password login
    - Session management with JWT
    - Remember me functionality
    - Simple logout
    
    What's NOT included (don't need for 1-2 users):
    - Biometric authentication
    - OAuth2/SSO
    - Multi-factor authentication
    - Password reset flows
    - Email verification
    """
    
    def __init__(self, auth_service: Optional[AuthenticationService] = None):
        """
        Initialize authentication interface.
        
        Args:
            auth_service: Optional authentication service instance.
                         Creates new one if not provided.
        """
        self.auth_service = auth_service or AuthenticationService(token_expiry_hours=24)
        self._current_user = None
        self._remember_me = False
    
    def login(
        self,
        username: str,
        password: str,
        remember_me: bool = False
    ) -> Dict[str, Any]:
        """
        Simple login with username and password.
        
        Args:
            username: User's username
            password: User's password
            remember_me: Whether to persist session (extends token to 7 days)
        
        Returns:
            Dict containing:
                - success: bool
                - session_token: str (if successful)
                - user_id: str (if successful)
                - error: str (if failed)
                - expires_at: datetime (if successful)
        """
        # Validate inputs
        if not username or not isinstance(username, str):
            return {
                'success': False,
                'error': 'Username is required',
                'session_token': None
            }
        
        if not password or not isinstance(password, str):
            return {
                'success': False,
                'error': 'Password is required',
                'session_token': None
            }
        
        # Create session via auth service
        result = self.auth_service.create_user_session(username, password)
        
        if not result.get('session_created'):
            return {
                'success': False,
                'error': result.get('error', 'Authentication failed'),
                'session_token': None
            }
        
        # Store current user
        self._current_user = username
        self._remember_me = remember_me
        
        # Calculate expiry based on remember_me
        expiry_hours = 168 if remember_me else 24  # 7 days vs 1 day
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        
        return {
            'success': True,
            'session_token': result['session_token'],
            'user_id': username,
            'expires_at': expires_at.isoformat(),
            'remember_me': remember_me
        }
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """
        Check if session is still valid.
        
        Args:
            session_token: Session token to validate
        
        Returns:
            Dict containing:
                - valid: bool
                - user_id: str (if valid)
                - remaining_time: float (seconds remaining)
                - error: str (if invalid)
        """
        if not session_token:
            return {
                'valid': False,
                'error': 'No session token provided',
                'user_id': None
            }
        
        result = self.auth_service.validate_session_token(session_token)
        
        return {
            'valid': result.get('valid', False),
            'user_id': result.get('user_id'),
            'remaining_time': result.get('remaining_time', 0),
            'error': result.get('error') if not result.get('valid') else None
        }
    
    def logout(self, session_token: str) -> Dict[str, Any]:
        """
        Logout and terminate session.
        
        Args:
            session_token: Session token to terminate
        
        Returns:
            Dict containing:
                - success: bool
                - message: str
        """
        if not session_token:
            return {
                'success': False,
                'message': 'No session token provided'
            }
        
        success = self.auth_service.terminate_session(session_token)
        
        if success:
            self._current_user = None
            self._remember_me = False
        
        return {
            'success': success,
            'message': 'Logged out successfully' if success else 'Session not found'
        }
    
    def get_current_user(self) -> Optional[str]:
        """
        Get currently logged in user.
        
        Returns:
            Username if logged in, None otherwise
        """
        return self._current_user
    
    def is_remember_me_enabled(self) -> bool:
        """
        Check if remember me is enabled for current session.
        
        Returns:
            True if remember me is enabled
        """
        return self._remember_me
    
    def get_session_info(self, session_token: str) -> Dict[str, Any]:
        """
        Get detailed session information.
        
        Args:
            session_token: Session token
        
        Returns:
            Dict with session details including:
                - valid: bool
                - user_id: str
                - created_at: float (timestamp)
                - expires_at: float (timestamp)
                - last_activity: float (timestamp)
                - is_active: bool
        """
        validation = self.validate_session(session_token)
        
        if not validation['valid']:
            return {
                'valid': False,
                'error': validation['error']
            }
        
        # Get full session data from service
        sessions = self.auth_service.active_sessions
        if session_token in sessions:
            session_data = sessions[session_token]
            return {
                'valid': True,
                'user_id': session_data['user_id'],
                'created_at': session_data['created_at'],
                'expires_at': session_data['expires_at'],
                'last_activity': session_data['last_activity'],
                'is_active': session_data['is_active'],
                'remaining_time': validation['remaining_time']
            }
        
        return {
            'valid': False,
            'error': 'Session not found'
        }
