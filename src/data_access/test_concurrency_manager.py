"""
Test Concurrency Manager - Support for 10+ concurrent test generation operations
Minimal GREEN phase implementation
"""
import sqlite3
import threading
import time
from typing import Dict, Any, List, Optional

class TestConcurrencyManager:
    """REAL concurrency support for 10+ simultaneous test operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database with WAL mode for better concurrency"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrent access
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=MEMORY')
            
            # Create test data table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS concurrent_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    data TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Populate with initial test data
            for i in range(100):
                conn.execute(
                    'INSERT OR IGNORE INTO concurrent_tests (name, data, created_by) VALUES (?, ?, ?)',
                    (f'test_{i}', f'test_data_{i}', 'system')
                )
            conn.commit()
    
    def read_test_data(self, test_name: str) -> List[Dict[str, Any]]:
        """Read test data with concurrent access support"""
        try:
            # Use connection with timeout for concurrent access
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute(
                'SELECT * FROM concurrent_tests WHERE name LIKE ? LIMIT 10',
                (f'{test_name}%',)
            )
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return results
        except Exception:
            return []
    
    def write_test_data(self, test_data: Dict[str, Any]) -> bool:
        """Write test data with concurrent access support"""
        try:
            # Use lock for write operations to ensure data integrity
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                conn.execute(
                    'INSERT INTO concurrent_tests (name, data, created_by) VALUES (?, ?, ?)',
                    (
                        test_data.get('name', 'unknown'),
                        test_data.get('description', ''),
                        'concurrent_operation'
                    )
                )
                conn.commit()
                conn.close()
            
            return True
        except Exception:
            return False
    
    def bulk_read_operation(self, operation_id: int) -> Dict[str, Any]:
        """Perform bulk read operation for concurrency testing"""
        try:
            start_time = time.time()
            
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            
            # Read multiple records
            cursor = conn.execute(
                'SELECT COUNT(*) as count FROM concurrent_tests WHERE id > ?',
                (operation_id * 10,)
            )
            count_result = cursor.fetchone()
            
            cursor = conn.execute(
                'SELECT * FROM concurrent_tests ORDER BY id LIMIT 5 OFFSET ?',
                (operation_id * 5,)
            )
            data_results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            end_time = time.time()
            
            return {
                'operation_id': operation_id,
                'count': count_result[0] if count_result else 0,
                'data_count': len(data_results),
                'duration': end_time - start_time,
                'success': True
            }
        except Exception as e:
            return {
                'operation_id': operation_id,
                'error': str(e),
                'success': False
            }
    
    def bulk_write_operation(self, operation_id: int, batch_size: int = 5) -> Dict[str, Any]:
        """Perform bulk write operation for concurrency testing"""
        try:
            start_time = time.time()
            
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                
                # Write multiple records
                test_data = []
                for i in range(batch_size):
                    test_data.append((
                        f'concurrent_test_{operation_id}_{i}',
                        f'bulk_data_{operation_id}_{i}',
                        f'operation_{operation_id}'
                    ))
                
                conn.executemany(
                    'INSERT INTO concurrent_tests (name, data, created_by) VALUES (?, ?, ?)',
                    test_data
                )
                conn.commit()
                conn.close()
            
            end_time = time.time()
            
            return {
                'operation_id': operation_id,
                'records_written': batch_size,
                'duration': end_time - start_time,
                'success': True
            }
        except Exception as e:
            return {
                'operation_id': operation_id,
                'error': str(e),
                'success': False
            }