"""
FUNCTIONAL REQUIREMENT TEST - TGR-002
Test Metadata Management
"""
import pytest
import json
import tempfile
import os

class TestTGR002:
    """Test Metadata Management for test case storage and retrieval"""
    
    def test_test_metadata_management_fails(self):
        """Test REAL test metadata storage, retrieval, and search functionality"""
        from src.data_access.test_metadata_manager import TestMetadataManager
        
        # Setup temporary metadata storage
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_manager = TestMetadataManager(temp_dir)
            
            # Test metadata storage
            test_metadata = {
                'test_id': 'test_001',
                'name': 'example_test',
                'tags': ['unit', 'core'],
                'category': 'functional',
                'created_date': '2025-09-21',
                'last_run': '2025-09-21T10:00:00',
                'execution_time': 0.05,
                'status': 'pass'
            }
            
            success = metadata_manager.store_metadata('test_001', test_metadata)
            assert success, "Failed to store test metadata"
            
            # Test metadata retrieval
            retrieved_metadata = metadata_manager.get_metadata('test_001')
            assert retrieved_metadata is not None, "Failed to retrieve metadata"
            assert retrieved_metadata['name'] == 'example_test'
            assert retrieved_metadata['tags'] == ['unit', 'core']
            
            # Test metadata search by tags
            search_results = metadata_manager.search_by_tags(['unit'])
            assert len(search_results) > 0, "Failed to search by tags"
            assert 'test_001' in [result['test_id'] for result in search_results]
            
            # Test metadata search by category
            category_results = metadata_manager.search_by_category('functional')
            assert len(category_results) > 0, "Failed to search by category"
            assert 'test_001' in [result['test_id'] for result in category_results]
            
            # Test metadata update
            updated_metadata = {'status': 'fail', 'last_run': '2025-09-21T11:00:00'}
            update_success = metadata_manager.update_metadata('test_001', updated_metadata)
            assert update_success, "Failed to update metadata"
            
            # Verify update
            updated_data = metadata_manager.get_metadata('test_001')
            assert updated_data['status'] == 'fail'
            assert updated_data['last_run'] == '2025-09-21T11:00:00'