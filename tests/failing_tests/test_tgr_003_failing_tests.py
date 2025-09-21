"""
FUNCTIONAL REQUIREMENT TEST - TGR-003
Test Database Schema Management
"""
import pytest
import sqlite3
import tempfile
import os

class TestTGR003:
    """Test Database Schema Management for SQLite operations"""
    
    def test_test_database_schema_management_fails(self):
        """Test REAL SQLite database operations with schema validation"""
        from src.data_access.test_database_schema import TestDatabaseSchema
        
        # Setup temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            schema_manager = TestDatabaseSchema(db_path)
            
            # Test schema initialization
            init_success = schema_manager.initialize_schema()
            assert init_success, "Failed to initialize database schema"
            
            # Test table creation
            test_table_schema = {
                'table_name': 'test_results',
                'columns': {
                    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                    'test_name': 'TEXT NOT NULL',
                    'result': 'TEXT NOT NULL',
                    'execution_time': 'REAL',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
            }
            
            table_success = schema_manager.create_table(test_table_schema)
            assert table_success, "Failed to create test table"
            
            # Test schema validation
            is_valid = schema_manager.validate_schema()
            assert is_valid, "Schema validation failed"
            
            # Test table exists check
            table_exists = schema_manager.table_exists('test_results')
            assert table_exists, "Test table should exist"
            
            # Test column validation
            expected_columns = ['id', 'test_name', 'result', 'execution_time', 'created_at']
            actual_columns = schema_manager.get_table_columns('test_results')
            for col in expected_columns:
                assert col in actual_columns, f"Column {col} missing from table"
            
            # Test index creation
            index_success = schema_manager.create_index('test_results', 'test_name')
            assert index_success, "Failed to create index"
            
            # Test schema backup
            backup_success = schema_manager.backup_schema()
            assert backup_success, "Failed to backup schema"
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)