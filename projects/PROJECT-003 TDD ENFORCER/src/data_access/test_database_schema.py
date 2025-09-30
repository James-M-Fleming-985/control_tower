"""
Test Database Schema - SQLite database operations with schema validation
Minimal GREEN phase implementation
"""
import sqlite3
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class TestDatabaseSchema:
    """REAL SQLite database operations with schema validation and table management"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup"
    
    def initialize_schema(self) -> bool:
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create core tables
                conn.executescript('''
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version TEXT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE TABLE IF NOT EXISTS test_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        table_name TEXT NOT NULL,
                        column_info TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    INSERT OR IGNORE INTO schema_version (version) VALUES ('1.0.0');
                ''')
                conn.commit()
            return True
        except Exception:
            return False
    
    def create_table(self, table_schema: Dict[str, Any]) -> bool:
        """Create table with specified schema"""
        try:
            table_name = table_schema['table_name']
            columns = table_schema['columns']
            
            column_defs = []
            for col_name, col_type in columns.items():
                column_defs.append(f"{col_name} {col_type}")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(create_sql)
                
                # Store table metadata
                conn.execute(
                    'INSERT INTO test_metadata (table_name, column_info) VALUES (?, ?)',
                    (table_name, json.dumps(columns))
                )
                conn.commit()
            return True
        except Exception:
            return False
    
    def validate_schema(self) -> bool:
        """Validate database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if core tables exist
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('schema_version', 'test_metadata')"
                )
                tables = cursor.fetchall()
                return len(tables) >= 2
        except Exception:
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,)
                )
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get table column names"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                return [col[1] for col in columns]  # Column name is at index 1
        except Exception:
            return []
    
    def create_index(self, table_name: str, column_name: str) -> bool:
        """Create index on table column"""
        try:
            index_name = f"idx_{table_name}_{column_name}"
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})")
                conn.commit()
            return True
        except Exception:
            return False
    
    def backup_schema(self) -> bool:
        """Create backup of database"""
        try:
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            return True
        except Exception:
            return False