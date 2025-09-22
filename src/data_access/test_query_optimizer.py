"""
Test Query Optimizer - Database query performance optimization under 100ms
Minimal GREEN phase implementation
"""
import sqlite3
import time
from typing import List, Dict, Any

class TestQueryOptimizer:
    """REAL database query performance optimization under 100ms"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_optimized_schema()
    
    def _init_optimized_schema(self):
        """Initialize optimized database schema with indexes"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT,
                    status TEXT,
                    execution_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_name ON test_cases(name);
                CREATE INDEX IF NOT EXISTS idx_category ON test_cases(category);
                CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status);
                
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY,
                    test_case_id INTEGER,
                    result TEXT,
                    execution_time REAL,
                    FOREIGN KEY (test_case_id) REFERENCES test_cases(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_test_case_id ON test_results(test_case_id);
            ''')
    
    def setup_test_data(self, num_records: int):
        """Setup test data for performance testing"""
        with sqlite3.connect(self.db_path) as conn:
            # Insert test cases
            test_cases = []
            for i in range(num_records):
                test_cases.append((
                    f'test_{i:04d}',
                    'unit' if i % 2 == 0 else 'integration',
                    'pass' if i % 3 != 0 else 'fail',
                    0.01 + (i % 10) * 0.01
                ))
            
            conn.executemany(
                'INSERT OR REPLACE INTO test_cases (name, category, status, execution_time) VALUES (?, ?, ?, ?)',
                test_cases
            )
            
            # Insert test results
            test_results = []
            for i in range(num_records):
                test_results.append((
                    i + 1,  # test_case_id
                    'pass' if i % 4 != 0 else 'fail',
                    0.02 + (i % 5) * 0.01
                ))
            
            conn.executemany(
                'INSERT OR REPLACE INTO test_results (test_case_id, result, execution_time) VALUES (?, ?, ?)',
                test_results
            )
            conn.commit()
    
    def query_test_cases_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Query test cases by name pattern (optimized)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                'SELECT * FROM test_cases WHERE name LIKE ? ORDER BY name LIMIT 100',
                (name_pattern,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def query_test_results_with_metadata(self) -> List[Dict[str, Any]]:
        """Query test results with metadata (optimized join)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT tc.name, tc.category, tr.result, tr.execution_time
                FROM test_cases tc
                JOIN test_results tr ON tc.id = tr.test_case_id
                WHERE tc.category IN ('unit', 'integration')
                ORDER BY tc.name
                LIMIT 100
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def query_by_indexed_field(self, field: str, value: str) -> List[Dict[str, Any]]:
        """Query by indexed field for optimal performance"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                f'SELECT * FROM test_cases WHERE {field} = ? LIMIT 50',
                (value,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get aggregated test statistics (optimized)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total_tests,
                    AVG(execution_time) as avg_execution_time,
                    MIN(execution_time) as min_execution_time,
                    MAX(execution_time) as max_execution_time,
                    COUNT(CASE WHEN status = 'pass' THEN 1 END) as passed_tests,
                    COUNT(CASE WHEN status = 'fail' THEN 1 END) as failed_tests
                FROM test_cases
            ''')
            row = cursor.fetchone()
            
            return {
                'total_tests': row[0] or 0,
                'avg_execution_time': row[1] or 0.0,
                'min_execution_time': row[2] or 0.0,
                'max_execution_time': row[3] or 0.0,
                'passed_tests': row[4] or 0,
                'failed_tests': row[5] or 0
            }