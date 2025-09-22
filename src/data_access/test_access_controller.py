"""
Test Access Controller - Role-based access control for test operations
Minimal GREEN phase implementation
"""
import sqlite3
import hashlib
import time
import json
from typing import Dict, Any, List, Optional

class TestAccessController:
    """REAL role-based access control for test operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_security_database()
    
    def _init_security_database(self):
        """Initialize security database with roles and users"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    permissions TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    role_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (role_id) REFERENCES roles(id)
                );
                
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    resource TEXT,
                    result TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
    
    def create_role(self, role_name: str, permissions: List[str]) -> bool:
        """Create a new role with specified permissions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO roles (name, permissions) VALUES (?, ?)',
                    (role_name, json.dumps(permissions))
                )
                conn.commit()
            return True
        except Exception:
            return False
    
    def create_user(self, username: str, role_name: str) -> bool:
        """Create a new user with specified role"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get role ID
                cursor = conn.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
                role_row = cursor.fetchone()
                
                if not role_row:
                    return False
                
                role_id = role_row[0]
                
                conn.execute(
                    'INSERT INTO users (username, role_id) VALUES (?, ?)',
                    (username, role_id)
                )
                conn.commit()
            return True
        except Exception:
            return False
    
    def get_user_context(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user context including role and permissions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT u.id, u.username, r.name as role_name, r.permissions
                    FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE u.username = ?
                ''', (username,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row['id'],
                        'username': row['username'],
                        'role': row['role_name'],
                        'permissions': json.loads(row['permissions'])
                    }
                return None
        except Exception:
            return None
    
    def check_permission(self, user_context: Dict[str, Any], permission: str) -> bool:
        """Check if user has specific permission"""
        if not user_context:
            return False
        
        user_permissions = user_context.get('permissions', [])
        return permission in user_permissions
    
    def secure_read_operation(self, user_context: Dict[str, Any], resource: str) -> Dict[str, Any]:
        """Perform secure read operation with access control"""
        if not self.check_permission(user_context, 'read'):
            self._log_audit_event(user_context, 'read', resource, 'access_denied')
            return {'success': False, 'error': 'Access denied: insufficient permissions'}
        
        try:
            # Simulate read operation
            data = {'resource': resource, 'data': 'test_data', 'timestamp': time.time()}
            self._log_audit_event(user_context, 'read', resource, 'success')
            return {'success': True, 'data': data}
        except Exception as e:
            self._log_audit_event(user_context, 'read', resource, 'error')
            return {'success': False, 'error': str(e)}
    
    def secure_write_operation(self, user_context: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform secure write operation with access control"""
        if not self.check_permission(user_context, 'write'):
            self._log_audit_event(user_context, 'write', 'test_data', 'access_denied')
            return {'success': False, 'error': 'Access denied: insufficient permissions'}
        
        try:
            # Simulate write operation
            resource_id = f"resource_{int(time.time())}"
            self._log_audit_event(user_context, 'write', resource_id, 'success')
            return {'success': True, 'resource_id': resource_id}
        except Exception as e:
            self._log_audit_event(user_context, 'write', 'test_data', 'error')
            return {'success': False, 'error': str(e)}
    
    def _log_audit_event(self, user_context: Dict[str, Any], action: str, resource: str, result: str):
        """Log audit event"""
        try:
            user_id = user_context.get('user_id') if user_context else None
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO audit_log (user_id, action, resource, result) VALUES (?, ?, ?, ?)',
                    (user_id, action, resource, result)
                )
                conn.commit()
        except Exception:
            pass  # Audit logging failure shouldn't break operations
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT al.*, u.username
                    FROM audit_log al
                    LEFT JOIN users u ON al.user_id = u.id
                    ORDER BY al.timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def create_session(self, username: str) -> Optional[str]:
        """Create a new session for user"""
        try:
            user_context = self.get_user_context(username)
            if not user_context:
                return None
            
            # Generate session ID
            session_data = f"{username}_{time.time()}"
            session_id = hashlib.md5(session_data.encode()).hexdigest()
            
            expires_at = time.time() + 3600  # 1 hour from now
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)',
                    (session_id, user_context['user_id'], expires_at)
                )
                conn.commit()
            
            return session_id
        except Exception:
            return None
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if session is active and not expired"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT expires_at, active FROM sessions WHERE id = ?',
                    (session_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                expires_at, active = row
                current_time = time.time()
                
                return active and expires_at > current_time
        except Exception:
            return False
    
    def expire_session(self, session_id: str) -> bool:
        """Expire a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'UPDATE sessions SET active = FALSE WHERE id = ?',
                    (session_id,)
                )
                conn.commit()
            return True
        except Exception:
            return False