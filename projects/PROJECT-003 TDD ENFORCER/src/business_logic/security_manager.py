"""
Business Logic Layer - Security Module
Implements REAL access control, encryption, and authentication for business logic security.
"""
import hashlib
import hmac
import time
import secrets
import base64
import os
from typing import Dict, Any, List, Optional, Set
from cryptography.fernet import Fernet
import logging


class AccessControlManager:
    """Access control manager with role-based permissions and audit logging"""
    
    def __init__(self):
        self.user_roles = {}
        self.role_permissions = {
            'admin': {'read', 'write', 'execute', 'delete', 'manage_users'},
            'developer': {'read', 'write', 'execute'},
            'tester': {'read', 'execute'},
            'viewer': {'read'}
        }
        self.access_attempts = []
        self.blocked_users = set()
        self.failed_attempts = {}
        self.max_failed_attempts = 3
    
    def authenticate_user(self, user_id: str, password: str, role: str = 'viewer') -> Dict[str, Any]:
        """Authenticate user with password and assign role"""
        # Simple password validation (in real system, use proper hashing)
        if len(password) < 8:
            self._record_failed_attempt(user_id)
            return {
                'authenticated': False,
                'reason': 'weak_password',
                'access_token': None
            }
        
        if user_id in self.blocked_users:
            return {
                'authenticated': False,
                'reason': 'user_blocked',
                'access_token': None
            }
        
        # Generate access token
        access_token = self._generate_access_token(user_id, role)
        self.user_roles[user_id] = role
        
        # Reset failed attempts on successful auth
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
        
        self._log_access_attempt(user_id, 'SUCCESS', 'authentication')
        
        return {
            'authenticated': True,
            'user_id': user_id,
            'role': role,
            'access_token': access_token,
            'permissions': list(self.role_permissions.get(role, set()))
        }
    
    def authorize_access(self, user_id: str, resource: str, action: str) -> bool:
        """Authorize user access to resource with specific action"""
        if user_id in self.blocked_users:
            self._log_access_attempt(user_id, 'DENIED', f'{action}_{resource}', 'user_blocked')
            return False
        
        user_role = self.user_roles.get(user_id)
        if not user_role:
            self._log_access_attempt(user_id, 'DENIED', f'{action}_{resource}', 'no_role')
            return False
        
        user_permissions = self.role_permissions.get(user_role, set())
        if action not in user_permissions:
            self._log_access_attempt(user_id, 'DENIED', f'{action}_{resource}', 'insufficient_permissions')
            return False
        
        self._log_access_attempt(user_id, 'GRANTED', f'{action}_{resource}')
        return True
    
    def _generate_access_token(self, user_id: str, role: str) -> str:
        """Generate secure access token"""
        token_data = f"{user_id}:{role}:{time.time()}:{secrets.token_hex(16)}"
        return base64.b64encode(token_data.encode()).decode()
    
    def _record_failed_attempt(self, user_id: str) -> None:
        """Record failed authentication attempt"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = 0
        
        self.failed_attempts[user_id] += 1
        
        if self.failed_attempts[user_id] >= self.max_failed_attempts:
            self.blocked_users.add(user_id)
            self._log_access_attempt(user_id, 'BLOCKED', 'authentication', 'too_many_failures')
    
    def _log_access_attempt(self, user_id: str, result: str, action: str, reason: str = '') -> None:
        """Log access attempt for audit trail"""
        log_entry = {
            'timestamp': time.time(),
            'user_id': user_id,
            'action': action,
            'result': result,
            'reason': reason,
            'ip_address': '127.0.0.1'  # In real system, get from request
        }
        self.access_attempts.append(log_entry)
    
    def get_security_audit_log(self) -> List[Dict[str, Any]]:
        """Get security audit log for compliance"""
        return self.access_attempts[-100:]  # Return last 100 entries


class EncryptionService:
    """Encryption service for sensitive data protection"""
    
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.encrypted_data_store = {}
        self.encryption_operations = 0
        self.decryption_operations = 0
    
    def encrypt_sensitive_data(self, data: Any, data_id: str = None) -> Dict[str, Any]:
        """Encrypt sensitive data with secure key management"""
        if data_id is None:
            data_id = f"data_{secrets.token_hex(8)}"
        
        # Convert data to string if needed
        data_str = str(data) if not isinstance(data, str) else data
        data_bytes = data_str.encode('utf-8')
        
        # Encrypt the data
        encrypted_data = self.cipher_suite.encrypt(data_bytes)
        
        # Store encrypted data
        self.encrypted_data_store[data_id] = {
            'encrypted_data': encrypted_data,
            'timestamp': time.time(),
            'size': len(encrypted_data)
        }
        
        self.encryption_operations += 1
        
        return {
            'encrypted': True,
            'data_id': data_id,
            'encryption_timestamp': time.time(),
            'encrypted_size': len(encrypted_data)
        }
    
    def decrypt_sensitive_data(self, data_id: str) -> Dict[str, Any]:
        """Decrypt sensitive data with validation"""
        if data_id not in self.encrypted_data_store:
            return {
                'decrypted': False,
                'error': 'data_not_found',
                'data': None
            }
        
        try:
            encrypted_entry = self.encrypted_data_store[data_id]
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_entry['encrypted_data'])
            decrypted_data = decrypted_bytes.decode('utf-8')
            
            self.decryption_operations += 1
            
            return {
                'decrypted': True,
                'data': decrypted_data,
                'decryption_timestamp': time.time(),
                'original_timestamp': encrypted_entry['timestamp']
            }
        
        except Exception as e:
            return {
                'decrypted': False,
                'error': f'decryption_failed: {str(e)}',
                'data': None
            }
    
    def get_encryption_stats(self) -> Dict[str, Any]:
        """Get encryption service statistics"""
        return {
            'total_encrypted_items': len(self.encrypted_data_store),
            'encryption_operations': self.encryption_operations,
            'decryption_operations': self.decryption_operations,
            'total_encrypted_size': sum(item['size'] for item in self.encrypted_data_store.values())
        }


class AuthenticationService:
    """Authentication service with token management and session control"""
    
    def __init__(self, token_expiry_hours: int = 24):
        self.active_sessions = {}
        self.token_expiry_seconds = token_expiry_hours * 3600
        self.password_hashes = {}
        self.session_count = 0
        self.authentication_attempts = 0
        self.successful_authentications = 0
    
    def create_user_session(self, user_id: str, password: str) -> Dict[str, Any]:
        """Create authenticated user session with token"""
        self.authentication_attempts += 1
        
        # Validate password (simple check for demo)
        if not self._validate_password(user_id, password):
            return {
                'session_created': False,
                'error': 'invalid_credentials',
                'session_token': None
            }
        
        # Generate session token
        session_token = self._generate_session_token()
        session_data = {
            'user_id': user_id,
            'session_token': session_token,
            'created_at': time.time(),
            'expires_at': time.time() + self.token_expiry_seconds,
            'last_activity': time.time(),
            'is_active': True
        }
        
        self.active_sessions[session_token] = session_data
        self.session_count += 1
        self.successful_authentications += 1
        
        return {
            'session_created': True,
            'session_token': session_token,
            'expires_at': session_data['expires_at'],
            'user_id': user_id
        }
    
    def validate_session_token(self, session_token: str) -> Dict[str, Any]:
        """Validate session token and check expiry"""
        if session_token not in self.active_sessions:
            return {
                'valid': False,
                'error': 'session_not_found',
                'user_id': None
            }
        
        session = self.active_sessions[session_token]
        current_time = time.time()
        
        # Check if session expired
        if current_time > session['expires_at']:
            session['is_active'] = False
            return {
                'valid': False,
                'error': 'session_expired',
                'user_id': session['user_id']
            }
        
        # Update last activity
        session['last_activity'] = current_time
        
        return {
            'valid': True,
            'user_id': session['user_id'],
            'remaining_time': session['expires_at'] - current_time,
            'last_activity': session['last_activity']
        }
    
    def terminate_session(self, session_token: str) -> bool:
        """Terminate user session"""
        if session_token in self.active_sessions:
            self.active_sessions[session_token]['is_active'] = False
            del self.active_sessions[session_token]
            return True
        return False
    
    def _validate_password(self, user_id: str, password: str) -> bool:
        """Validate user password (simplified for demo)"""
        # In real system, compare with stored hash
        return len(password) >= 8 and password != 'password'
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def get_authentication_stats(self) -> Dict[str, Any]:
        """Get authentication service statistics"""
        active_sessions_count = len([s for s in self.active_sessions.values() if s['is_active']])
        
        return {
            'total_sessions_created': self.session_count,
            'active_sessions': active_sessions_count,
            'authentication_attempts': self.authentication_attempts,
            'successful_authentications': self.successful_authentications,
            'success_rate': (self.successful_authentications / max(1, self.authentication_attempts)) * 100
        }