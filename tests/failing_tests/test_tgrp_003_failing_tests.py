"""
PERFORMANCE REQUIREMENT TEST - TGRP-003
Concurrent Operations Support 10+
"""
import pytest
import threading
import time
import tempfile
import os

class TestTGRP003:
    """Test Concurrent Operations Support for 10+ test generation operations"""
    
    def test_concurrent_operations_support_10_plus_fails(self):
        """Test REAL concurrent operations support for 10+ simultaneous test generation operations"""
        from src.data_access.test_concurrency_manager import TestConcurrencyManager
        
        # Setup temporary database for concurrent access
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            concurrency_manager = TestConcurrencyManager(db_path)
            
            # Test concurrent read operations
            num_concurrent_operations = 15
            results = []
            errors = []
            
            def concurrent_read_operation(operation_id):
                try:
                    start_time = time.time()
                    test_data = concurrency_manager.read_test_data(f"test_{operation_id}")
                    end_time = time.time()
                    
                    results.append({
                        'operation_id': operation_id,
                        'duration': end_time - start_time,
                        'data_count': len(test_data) if test_data else 0,
                        'success': True
                    })
                except Exception as e:
                    errors.append({
                        'operation_id': operation_id,
                        'error': str(e)
                    })
            
            # Create and start concurrent threads
            threads = []
            for i in range(num_concurrent_operations):
                thread = threading.Thread(target=concurrent_read_operation, args=(i,))
                threads.append(thread)
            
            # Start all threads simultaneously
            start_time = time.time()
            for thread in threads:
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            # Verify concurrent operations completed successfully
            assert len(errors) == 0, f"Concurrent operations should not have errors: {errors}"
            assert len(results) == num_concurrent_operations, f"Should have {num_concurrent_operations} results"
            
            # Test concurrent write operations
            write_results = []
            write_errors = []
            
            def concurrent_write_operation(operation_id):
                try:
                    test_case_data = {
                        'name': f'concurrent_test_{operation_id}',
                        'description': f'Test case created by operation {operation_id}',
                        'test_code': f'def test_concurrent_{operation_id}(): assert True'
                    }
                    
                    success = concurrency_manager.write_test_data(test_case_data)
                    write_results.append({
                        'operation_id': operation_id,
                        'success': success
                    })
                except Exception as e:
                    write_errors.append({
                        'operation_id': operation_id,
                        'error': str(e)
                    })
            
            # Test concurrent writes
            write_threads = []
            for i in range(num_concurrent_operations):
                thread = threading.Thread(target=concurrent_write_operation, args=(i,))
                write_threads.append(thread)
            
            for thread in write_threads:
                thread.start()
            
            for thread in write_threads:
                thread.join()
            
            # Verify concurrent writes
            assert len(write_errors) == 0, f"Concurrent writes should not have errors: {write_errors}"
            assert len(write_results) == num_concurrent_operations, "All write operations should complete"
            assert all(result['success'] for result in write_results), "All write operations should succeed"
            
            # Test concurrent mixed operations (read/write)
            mixed_results = []
            mixed_errors = []
            
            def mixed_operation(operation_id):
                try:
                    if operation_id % 2 == 0:
                        # Read operation
                        data = concurrency_manager.read_test_data(f"test_{operation_id}")
                        mixed_results.append({'type': 'read', 'operation_id': operation_id, 'success': True})
                    else:
                        # Write operation
                        test_data = {'name': f'mixed_test_{operation_id}'}
                        success = concurrency_manager.write_test_data(test_data)
                        mixed_results.append({'type': 'write', 'operation_id': operation_id, 'success': success})
                except Exception as e:
                    mixed_errors.append({'operation_id': operation_id, 'error': str(e)})
            
            mixed_threads = []
            for i in range(num_concurrent_operations):
                thread = threading.Thread(target=mixed_operation, args=(i,))
                mixed_threads.append(thread)
            
            for thread in mixed_threads:
                thread.start()
            
            for thread in mixed_threads:
                thread.join()
            
            assert len(mixed_errors) == 0, f"Mixed concurrent operations should not have errors: {mixed_errors}"
            assert len(mixed_results) == num_concurrent_operations, "All mixed operations should complete"
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)