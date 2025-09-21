"""
FUNCTIONAL REQUIREMENT TEST - TGR-001
Test Repository CRUD Operations
"""
import pytest
import sqlite3
from pathlib import Path
import tempfile
import os

class TestTGR001:
    """Test Repository CRUD Operations for test case management"""
    
    def test_test_repository_crud_operations_fails(self):
        """Test REAL test repository CRUD operations for test case management"""
        from src.data_access.test_generation_repository import TestGenerationRepository
        
        # Setup temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            repo = TestGenerationRepository(db_path)
            
            # Test CREATE operation
            test_case_data = {
                'name': 'test_example',
                'description': 'Example test case',
                'expected_result': 'pass',
                'test_code': 'def test_example(): assert True'
            }
            test_id = repo.create_test_case(test_case_data)
            assert test_id is not None, "Failed to create test case"
            
            # Test READ operation
            retrieved_test = repo.get_test_case(test_id)
            assert retrieved_test is not None, "Failed to retrieve test case"
            assert retrieved_test['name'] == 'test_example'
            
            # Test UPDATE operation
            updated_data = {'description': 'Updated test case description'}
            success = repo.update_test_case(test_id, updated_data)
            assert success, "Failed to update test case"
            
            # Verify update
            updated_test = repo.get_test_case(test_id)
            assert updated_test['description'] == 'Updated test case description'
            
            # Test DELETE operation
            delete_success = repo.delete_test_case(test_id)
            assert delete_success, "Failed to delete test case"
            
            # Verify deletion
            deleted_test = repo.get_test_case(test_id)
            assert deleted_test is None, "Test case should be deleted"
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)