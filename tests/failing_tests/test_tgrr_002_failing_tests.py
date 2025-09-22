"""
RELIABILITY REQUIREMENT TEST - TGRR-002
Test Data Backup Automated
"""
import pytest
import tempfile
import os
import time
import json

class TestTGRR002:
    """Test Automated Backup System for test generation data"""
    
    def test_test_data_backup_automated_fails(self):
        """Test REAL automated backup system for test generation data protection"""
        from src.data_access.test_backup_manager import TestBackupManager
        
        # Setup temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, 'data')
            backup_dir = os.path.join(temp_dir, 'backups')
            os.makedirs(data_dir)
            os.makedirs(backup_dir)
            
            backup_manager = TestBackupManager(data_dir, backup_dir)
            
            # Setup test data
            test_data = {
                'test_cases': [
                    {'id': 1, 'name': 'test_login', 'status': 'pass'},
                    {'id': 2, 'name': 'test_logout', 'status': 'fail'},
                    {'id': 3, 'name': 'test_register', 'status': 'pass'}
                ],
                'test_results': [
                    {'test_id': 1, 'execution_time': 0.5, 'timestamp': '2025-09-21T10:00:00'},
                    {'test_id': 2, 'execution_time': 0.3, 'timestamp': '2025-09-21T10:01:00'},
                    {'test_id': 3, 'execution_time': 0.7, 'timestamp': '2025-09-21T10:02:00'}
                ]
            }
            
            # Store initial test data
            data_file = os.path.join(data_dir, 'test_data.json')
            with open(data_file, 'w') as f:
                json.dump(test_data, f)
            
            # Test manual backup creation
            backup_id = backup_manager.create_backup()
            assert backup_id is not None, "Should create backup successfully"
            
            # Verify backup file exists
            backup_files = backup_manager.list_backups()
            assert len(backup_files) > 0, "Should have at least one backup"
            assert backup_id in [b['id'] for b in backup_files], "Created backup should be in list"
            
            # Test automated backup scheduling
            schedule_success = backup_manager.schedule_automatic_backups(interval_minutes=1)
            assert schedule_success, "Should successfully schedule automatic backups"
            
            # Add more test data to trigger backup
            additional_data = {'id': 4, 'name': 'test_delete', 'status': 'pass'}
            test_data['test_cases'].append(additional_data)
            
            with open(data_file, 'w') as f:
                json.dump(test_data, f)
            
            # Wait for automatic backup to trigger (simulate with manual trigger)
            auto_backup_id = backup_manager.trigger_automatic_backup()
            assert auto_backup_id is not None, "Automatic backup should be created"
            
            # Verify multiple backups exist
            updated_backup_files = backup_manager.list_backups()
            assert len(updated_backup_files) >= 2, "Should have multiple backups"
            
            # Test backup verification
            latest_backup = backup_manager.get_latest_backup()
            assert latest_backup is not None, "Should have latest backup"
            
            backup_valid = backup_manager.verify_backup(latest_backup['id'])
            assert backup_valid, "Latest backup should be valid"
            
            # Test backup restoration
            # Simulate data loss
            os.remove(data_file)
            assert not os.path.exists(data_file), "Data file should be deleted"
            
            # Restore from backup
            restore_success = backup_manager.restore_from_backup(latest_backup['id'])
            assert restore_success, "Should successfully restore from backup"
            
            # Verify data is restored
            assert os.path.exists(data_file), "Data file should be restored"
            
            with open(data_file, 'r') as f:
                restored_data = json.load(f)
            
            assert len(restored_data['test_cases']) == 4, "Should restore all test cases"
            assert len(restored_data['test_results']) == 3, "Should restore all test results"
            
            # Test backup cleanup (old backups removal)
            # Create multiple backups
            for i in range(5):
                backup_manager.create_backup()
                time.sleep(0.1)  # Small delay to ensure different timestamps
            
            # Set retention policy
            cleanup_success = backup_manager.cleanup_old_backups(max_backups=3)
            assert cleanup_success, "Should successfully cleanup old backups"
            
            # Verify only recent backups remain
            final_backups = backup_manager.list_backups()
            assert len(final_backups) <= 3, "Should have at most 3 backups after cleanup"
            
            # Test backup statistics
            backup_stats = backup_manager.get_backup_statistics()
            assert 'total_backups' in backup_stats, "Should track total backups"
            assert 'total_size_mb' in backup_stats, "Should track total backup size"
            assert 'last_backup_time' in backup_stats, "Should track last backup time"
            assert 'success_rate' in backup_stats, "Should track backup success rate"