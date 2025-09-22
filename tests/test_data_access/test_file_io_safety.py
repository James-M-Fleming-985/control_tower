"""
Critical File I/O and Data Persistence Safety Tests
FEATURE-003-01-03 Risk Mitigation - Priority 3

These tests focus on preventing data corruption and ensuring
reliable persistence operations under failure conditions.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import json

from src.data_access.real_test_result_storage import RealTestResultStorage
from src.data_access.real_test_metadata_persistence import RealTestMetadataPersistence  
from src.data_access.real_verification_evidence_storage import RealVerificationEvidenceStorage
from src.data_access.real_test_file_discovery import RealTestFileDiscovery


class TestFileIOSafety:
    """Critical safety tests for file I/O operations"""
    
    def setup_method(self):
        """Setup test environment with temporary directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = RealTestResultStorage(base_path=self.temp_dir)
        
    def teardown_method(self):
        """Clean up temporary test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_file_write_permission_failure(self):
        """Test handling of file write permission failures"""
        # Create read-only directory to simulate permission failure
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only permissions
        
        test_data = {"test": "data", "timestamp": "2025-09-20T12:00:00Z"}
        
        try:
            result = self.storage.safe_write_test_results(
                file_path=os.path.join(readonly_dir, "test_results.json"),
                data=test_data
            )
            
            # Should handle permission failure gracefully
            assert result.success is False
            assert result.permission_denied is True
            assert "permission denied" in result.error_message.lower()
            assert result.data_preserved is True  # Should preserve in temp location
            
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)
    
    def test_disk_space_exhaustion_handling(self):
        """Test handling when disk space is exhausted during write"""
        large_data = {"data": "x" * 1024 * 1024}  # 1MB of data
        
        # Mock disk space check to simulate exhaustion
        with patch('shutil.disk_usage') as mock_disk_usage:
            mock_disk_usage.return_value = (1000, 100, 50)  # Total, used, free (very low free space)
            
            result = self.storage.write_with_space_check(
                file_path=os.path.join(self.temp_dir, "large_file.json"),
                data=large_data,
                required_space_mb=2  # Requires more than available
            )
            
            assert result.success is False
            assert result.insufficient_space is True
            assert result.required_mb > result.available_mb
            assert result.fallback_location_used is True
    
    def test_file_corruption_detection(self):
        """Test detection and handling of corrupted files"""
        corrupted_file_path = os.path.join(self.temp_dir, "corrupted.json")
        
        # Create file with invalid JSON content
        with open(corrupted_file_path, 'w') as f:
            f.write('{"invalid": json, "missing": quote}')  # Invalid JSON
        
        result = self.storage.safe_read_with_validation(corrupted_file_path)
        
        assert result.success is False
        assert result.corruption_detected is True
        assert result.backup_attempted is True
        assert "json decode error" in result.error_message.lower()
    
    def test_concurrent_file_access_protection(self):
        """Test protection against concurrent file access conflicts"""
        import threading
        import time
        
        file_path = os.path.join(self.temp_dir, "concurrent_test.json")
        results = []
        
        def concurrent_write_attempt(thread_id, data):
            """Simulate concurrent file write"""
            result = self.storage.thread_safe_write(
                file_path=file_path,
                data={"thread_id": thread_id, "data": data},
                timeout_seconds=5
            )
            results.append(result)
        
        # Launch multiple concurrent write operations
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=concurrent_write_attempt,
                args=(f"thread_{i}", f"data_{i}")
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All operations should complete successfully (serialized)
        successful_writes = [r for r in results if r.success]
        assert len(successful_writes) == 3
        assert all(r.file_lock_acquired for r in successful_writes)
    
    def test_atomic_write_operation_failure(self):
        """Test atomic write operations handle failures correctly"""
        file_path = os.path.join(self.temp_dir, "atomic_test.json")
        
        # First, create a valid file
        initial_data = {"version": 1, "data": "initial"}
        with open(file_path, 'w') as f:
            json.dump(initial_data, f)
        
        # Simulate failure during atomic write
        with patch('builtins.open', side_effect=IOError("Disk write error")):
            result = self.storage.atomic_write(
                file_path=file_path,
                new_data={"version": 2, "data": "updated"}
            )
            
            # Original file should remain unchanged
            assert result.success is False
            assert result.original_preserved is True
            
            # Verify original file is intact
            with open(file_path, 'r') as f:
                current_data = json.load(f)
                assert current_data == initial_data


class TestDataPersistenceSafety:
    """Safety tests for data persistence components"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.metadata_persistence = RealTestMetadataPersistence(base_path=self.temp_dir)
        self.evidence_storage = RealVerificationEvidenceStorage(base_path=self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_metadata_persistence_corruption_recovery(self):
        """Test recovery from corrupted metadata files"""
        metadata_file = os.path.join(self.temp_dir, "test_metadata.json")
        
        # Create corrupted metadata file
        with open(metadata_file, 'w') as f:
            f.write('{"corrupted": metadata, "invalid": }')  # Invalid JSON
        
        # System should detect corruption and recover
        result = self.metadata_persistence.load_with_recovery(metadata_file)
        
        assert result.corruption_detected is True
        assert result.recovery_attempted is True
        assert result.fallback_data_used is True
        assert result.original_backed_up is True
    
    def test_evidence_storage_integrity_validation(self):
        """Test verification evidence storage integrity validation"""
        evidence_data = {
            "test_execution_id": "test_001",
            "timestamp": "2025-09-20T12:00:00Z",
            "results": {"passed": 10, "failed": 0},
            "checksum": "abc123def456"  # Mock checksum
        }
        
        # Store evidence with integrity check
        result = self.evidence_storage.store_with_integrity_check(
            evidence_id="evidence_001",
            data=evidence_data
        )
        
        assert result.success is True
        assert result.integrity_verified is True
        assert result.checksum_generated is True
        
        # Later, verify integrity on read
        read_result = self.evidence_storage.read_with_integrity_verification(
            evidence_id="evidence_001"
        )
        
        assert read_result.success is True
        assert read_result.integrity_valid is True
        assert read_result.data == evidence_data
    
    def test_backup_strategy_under_failure(self):
        """Test backup strategy when primary storage fails"""
        primary_path = os.path.join(self.temp_dir, "primary")
        backup_path = os.path.join(self.temp_dir, "backup")
        
        # Make primary path inaccessible
        os.makedirs(primary_path)
        os.chmod(primary_path, 0o000)  # No permissions
        
        test_data = {"critical": "data", "must_not_lose": True}
        
        try:
            result = self.evidence_storage.store_with_backup_strategy(
                primary_location=primary_path,
                backup_location=backup_path,
                data=test_data
            )
            
            # Should fallback to backup location
            assert result.primary_failed is True
            assert result.backup_used is True
            assert result.data_preserved is True
            
            # Verify data is in backup location
            assert os.path.exists(os.path.join(backup_path, "data.json"))
            
        finally:
            # Restore permissions for cleanup
            os.chmod(primary_path, 0o755)
    
    def test_large_dataset_streaming_persistence(self):
        """Test streaming persistence for large datasets"""
        # Simulate large test result dataset
        large_dataset = {
            "test_results": [{"test_id": f"test_{i}", "result": "passed"} for i in range(10000)],
            "metadata": {"total_tests": 10000, "execution_time": "300s"}
        }
        
        result = self.metadata_persistence.stream_large_dataset(
            file_path=os.path.join(self.temp_dir, "large_results.json"),
            data=large_dataset,
            chunk_size=1000
        )
        
        assert result.success is True
        assert result.streaming_used is True
        assert result.memory_efficient is True
        assert result.chunks_written > 1
    
    def test_transactional_data_operations(self):
        """Test transactional consistency in data operations"""
        # Simulate multi-file transaction
        files_to_update = [
            {"path": os.path.join(self.temp_dir, "file1.json"), "data": {"id": 1}},
            {"path": os.path.join(self.temp_dir, "file2.json"), "data": {"id": 2}},
            {"path": os.path.join(self.temp_dir, "file3.json"), "data": {"id": 3}},
        ]
        
        # Simulate failure on third file
        with patch('builtins.open') as mock_open_call:
            # First two calls succeed, third fails
            mock_open_call.side_effect = [
                mock_open(read_data='').return_value,  # file1 success
                mock_open(read_data='').return_value,  # file2 success  
                IOError("Disk full")  # file3 fails
            ]
            
            result = self.metadata_persistence.transactional_update(files_to_update)
            
            # Should rollback all changes
            assert result.success is False
            assert result.transaction_rolled_back is True
            assert result.partial_changes_reverted is True
            assert len(result.rollback_operations) == 2  # Two successful operations rolled back


class TestFileDiscoverySafety:
    """Safety tests for file discovery operations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_discovery = RealTestFileDiscovery(search_root=self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_infinite_loop_protection_in_symlinks(self):
        """Test protection against infinite loops from circular symlinks"""
        # Create circular symlink structure
        dir1 = os.path.join(self.temp_dir, "dir1")
        dir2 = os.path.join(self.temp_dir, "dir2")
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        # Create circular symlinks
        os.symlink(dir2, os.path.join(dir1, "link_to_dir2"))
        os.symlink(dir1, os.path.join(dir2, "link_to_dir1"))
        
        result = self.file_discovery.safe_directory_traversal(
            root_path=self.temp_dir,
            max_depth=10,
            symlink_protection=True
        )
        
        assert result.success is True
        assert result.circular_symlinks_detected is True
        assert result.infinite_loop_prevented is True
        assert result.traversal_completed is True
    
    def test_permission_denied_directory_handling(self):
        """Test handling of directories with access permissions denied"""
        # Create directory with no read permissions
        restricted_dir = os.path.join(self.temp_dir, "restricted")
        os.makedirs(restricted_dir)
        os.chmod(restricted_dir, 0o000)  # No permissions
        
        try:
            result = self.file_discovery.discover_test_files_with_error_handling(
                search_paths=[self.temp_dir]
            )
            
            assert result.success is True  # Overall operation succeeds
            assert result.permission_errors_encountered is True
            assert "restricted" in result.inaccessible_directories
            assert result.accessible_files_found >= 0  # Should continue with accessible areas
            
        finally:
            # Restore permissions for cleanup
            os.chmod(restricted_dir, 0o755)