"""
Test Generation Repository - CRUD operations for test case management
Minimal GREEN phase implementation
"""
import sqlite3
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

class TestGenerationRepository:
    """REAL test repository CRUD operations with SQLite database persistence"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with enhanced test case table schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrency
            conn.execute('PRAGMA journal_mode=WAL')
            
            # Create enhanced test_cases table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    test_code TEXT,
                    expected_result TEXT,
                    category TEXT,
                    tags TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_hash TEXT,
                    version INTEGER DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create audit_log table for change tracking
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    operation TEXT NOT NULL,
                    old_values TEXT,
                    new_values TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'system'
                )
            ''')
            
            # Create deletion_log table for backup
            conn.execute('''
                CREATE TABLE IF NOT EXISTS deletion_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    record_data TEXT NOT NULL,
                    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_by TEXT DEFAULT 'system'
                )
            ''')
            
            # Create performance indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_test_cases_content_hash ON test_cases(content_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_test_cases_name ON test_cases(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_test_cases_category ON test_cases(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_record ON audit_log(table_name, record_id)')
            
            conn.commit()
            conn.commit()
    
    def create_test_case(self, test_case_data: Dict[str, Any]) -> int:
        """Create test case with advanced validation, duplicate detection, and performance profiling"""
        import time
        import hashlib
        
        start_time = time.time()
        
        # Advanced validation
        required_fields = ['name', 'test_code']
        for field in required_fields:
            if field not in test_case_data or not test_case_data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Duplicate detection using content hash
        content_hash = hashlib.sha256(
            (test_case_data['name'] + test_case_data['test_code']).encode()
        ).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            # Check for duplicates
            existing = conn.execute(
                'SELECT id FROM test_cases WHERE name = ? OR content_hash = ?',
                (test_case_data['name'], content_hash)
            ).fetchone()
            
            if existing:
                raise ValueError(f"Duplicate test case detected: {test_case_data['name']}")
            
            # Create with content hash
            cursor = conn.execute('''
                INSERT INTO test_cases (name, description, test_code, expected_result, 
                                      category, tags, content_hash) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_case_data['name'],
                test_case_data.get('description', ''),
                test_case_data['test_code'],
                test_case_data.get('expected_result', ''),
                test_case_data.get('category', 'unit'),
                json.dumps(test_case_data.get('tags', [])),
                content_hash
            ))
            
            test_id = cursor.lastrowid
            
            # Performance profiling
            execution_time = (time.time() - start_time) * 1000
            if execution_time > 50:  # Log slow operations
                print(f"WARNING: Slow test case creation: {execution_time:.2f}ms")
            
            return test_id
    
    def get_test_case(self, test_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve test case by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM test_cases WHERE id = ?', (test_id,)
                )
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    result['tags'] = json.loads(result['tags']) if result['tags'] else []
                    return result
                return None
        except Exception:
            return None
    
    def update_test_case(self, test_id: int, update_data: Dict[str, Any]) -> bool:
        """Update test case with versioned metadata, conflict resolution, and audit trail logging"""
        import time
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get current version and metadata
                current = conn.execute(
                    'SELECT version, updated_at FROM test_cases WHERE id = ?',
                    (test_id,)
                ).fetchone()
                
                if not current:
                    raise ValueError(f"Test case {test_id} not found")
                
                current_version, last_updated = current
                
                # Conflict resolution: check if updated since last known version
                if 'expected_version' in update_data:
                    if current_version != update_data['expected_version']:
                        raise ValueError(f"Version conflict: expected {update_data['expected_version']}, current {current_version}")
                
                # Prepare updates with versioning
                new_version = (current_version or 0) + 1
                set_clauses = []
                values = []
                
                for key, value in update_data.items():
                    if key == 'expected_version':
                        continue  # Skip this internal field
                    elif key == 'tags':
                        set_clauses.append(f"{key} = ?")
                        values.append(json.dumps(value))
                    else:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                # Add version and timestamp
                set_clauses.extend(['version = ?', 'updated_at = ?'])
                values.extend([new_version, time.time()])
                values.append(test_id)
                
                # Audit trail logging
                conn.execute('''
                    INSERT OR IGNORE INTO audit_log (test_id, old_version, new_version, changes, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (test_id, current_version or 0, new_version, json.dumps(update_data), time.time()))
                
                # Update test case
                cursor = conn.execute(
                    f"UPDATE test_cases SET {', '.join(set_clauses)} WHERE id = ?",
                    values
                )
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Update failed: {e}")
            return False
    
    def get_test_results(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get test results with intelligent indexing, query optimization, and result caching"""
        import time
        import hashlib
        
        start_time = time.time()
        
        # Create cache key from filters
        filter_key = json.dumps(filters or {}, sort_keys=True)
        cache_key = hashlib.md5(filter_key.encode()).hexdigest()
        
        # Simple in-memory cache (in production, use Redis)
        if not hasattr(self, '_cache'):
            self._cache = {}
            self._cache_timestamps = {}
        
        # Check cache (5 second TTL)
        if cache_key in self._cache:
            cache_age = time.time() - self._cache_timestamps[cache_key]
            if cache_age < 5:  # 5 second cache TTL
                return self._cache[cache_key]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Optimized query with proper indexing
                base_query = '''
                    SELECT tc.*, COUNT(al.id) as audit_count
                    FROM test_cases tc
                    LEFT JOIN audit_log al ON tc.id = al.test_id
                '''
                
                where_clauses = []
                params = []
                
                if filters:
                    if 'category' in filters:
                        where_clauses.append('tc.category = ?')
                        params.append(filters['category'])
                    
                    if 'tags' in filters:
                        # JSON search for tags
                        where_clauses.append("tc.tags LIKE ?")
                        params.append(f'%{filters["tags"]}%')
                    
                    if 'name_pattern' in filters:
                        where_clauses.append('tc.name LIKE ?')
                        params.append(f'%{filters["name_pattern"]}%')
                
                if where_clauses:
                    base_query += ' WHERE ' + ' AND '.join(where_clauses)
                
                base_query += ' GROUP BY tc.id ORDER BY tc.created_at DESC'
                
                # Add LIMIT for performance
                if 'limit' in (filters or {}):
                    base_query += f' LIMIT {filters["limit"]}'
                else:
                    base_query += ' LIMIT 1000'  # Default limit
                
                cursor = conn.execute(base_query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    result = dict(row)
                    result['tags'] = json.loads(result['tags']) if result['tags'] else []
                    results.append(result)
                
                # Cache results
                self._cache[cache_key] = results
                self._cache_timestamps[cache_key] = time.time()
                
                # Performance monitoring
                execution_time = (time.time() - start_time) * 1000
                if execution_time > 25:  # Log slow queries
                    print(f"WARNING: Slow query execution: {execution_time:.2f}ms")
                
                return results
                
        except Exception as e:
            print(f"ERROR: Query execution failed: {e}")
            return []
                
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity with checksum validation, foreign key verification, and corruption detection"""
        import hashlib
        import time
        
        integrity_report = {
            'status': 'healthy',
            'issues': [],
            'stats': {},
            'timestamp': time.time()
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check for missing content hashes
                missing_hashes = conn.execute('''
                    SELECT id, name FROM test_cases WHERE content_hash IS NULL OR content_hash = ''
                ''').fetchall()
                
                if missing_hashes:
                    integrity_report['issues'].append({
                        'type': 'missing_content_hash',
                        'count': len(missing_hashes),
                        'details': [{'id': row[0], 'name': row[1]} for row in missing_hashes]
                    })
                
                # Verify content hash integrity
                corrupted_records = []
                all_records = conn.execute('''
                    SELECT id, name, test_code, content_hash FROM test_cases 
                    WHERE content_hash IS NOT NULL AND content_hash != ''
                ''').fetchall()
                
                for record in all_records:
                    record_id, name, test_code, stored_hash = record
                    calculated_hash = hashlib.sha256((name + test_code).encode()).hexdigest()
                    
                    if calculated_hash != stored_hash:
                        corrupted_records.append({
                            'id': record_id,
                            'name': name,
                            'stored_hash': stored_hash,
                            'calculated_hash': calculated_hash
                        })
                
                if corrupted_records:
                    integrity_report['issues'].append({
                        'type': 'content_hash_mismatch',
                        'count': len(corrupted_records),
                        'details': corrupted_records
                    })
                    integrity_report['status'] = 'corrupted'
                
                # Check for orphaned audit log entries
                orphaned_audits = conn.execute('''
                    SELECT COUNT(*) FROM audit_log al 
                    LEFT JOIN test_cases tc ON al.test_id = tc.id 
                    WHERE tc.id IS NULL
                ''').fetchone()[0]
                
                if orphaned_audits > 0:
                    integrity_report['issues'].append({
                        'type': 'orphaned_audit_entries',
                        'count': orphaned_audits
                    })
                
                # Foreign key verification
                foreign_key_violations = conn.execute('''
                    SELECT name FROM pragma_foreign_key_check()
                ''').fetchall()
                
                if foreign_key_violations:
                    integrity_report['issues'].append({
                        'type': 'foreign_key_violations',
                        'count': len(foreign_key_violations),
                        'details': foreign_key_violations
                    })
                    integrity_report['status'] = 'corrupted'
                
                # Statistics
                stats = conn.execute('''
                    SELECT 
                        COUNT(*) as total_test_cases,
                        COUNT(CASE WHEN content_hash IS NOT NULL THEN 1 END) as verified_test_cases,
                        MAX(version) as max_version,
                        COUNT(DISTINCT category) as categories
                    FROM test_cases
                ''').fetchone()
                
                integrity_report['stats'] = {
                    'total_test_cases': stats[0],
                    'verified_test_cases': stats[1],
                    'max_version': stats[2] or 0,
                    'categories': stats[3] or 0,
                    'integrity_percentage': (stats[1] / stats[0] * 100) if stats[0] > 0 else 100
                }
                
                if len(integrity_report['issues']) == 0:
                    integrity_report['status'] = 'healthy'
                elif any(issue['type'] in ['content_hash_mismatch', 'foreign_key_violations'] 
                        for issue in integrity_report['issues']):
                    integrity_report['status'] = 'corrupted'
                else:
                    integrity_report['status'] = 'warning'
                
        except Exception as e:
            integrity_report['status'] = 'error'
            integrity_report['issues'].append({
                'type': 'validation_error',
                'message': str(e)
            })
        
        return integrity_report

    def delete_test_case(self, test_id: int) -> bool:
        """Delete test case with backup creation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create backup before deletion
                backup_data = conn.execute(
                    'SELECT * FROM test_cases WHERE id = ?', (test_id,)
                ).fetchone()
                
                if backup_data:
                    # Store in deletion log
                    conn.execute('''
                        INSERT OR IGNORE INTO deletion_log (test_id, backup_data, deleted_at)
                        VALUES (?, ?, ?)
                    ''', (test_id, json.dumps(dict(backup_data)), time.time()))
                
                cursor = conn.execute(
                    'DELETE FROM test_cases WHERE id = ?', (test_id,)
                )
                return cursor.rowcount > 0
        except Exception:
            return False