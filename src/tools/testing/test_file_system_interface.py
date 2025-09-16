"""
Unit tests for File System Interface - TR-DA-002 implementation

Tests the core functionality of abstracted file system access for testability and reliability.
Follows TDD methodology with comprehensive test coverage for acceptance criteria DA-008 through DA-011.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from dataclasses import dataclass
from typing import Optional, List
from src.data_access.file_system_interface import FileSystemInterface, FileStats


class TestFileSystemInterface:
    """Test suite for File System Interface functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fs_interface = FileSystemInterface()
    
    def test_read_file_returns_content_string(self):
        """
        Test that read_file returns file content as string
        Acceptance Criteria: DA-008 - Provides consistent file access interface
        """
        test_content = "This is test file content\nWith multiple lines"
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = self.fs_interface.read_file("/test/file.txt")
            
            assert isinstance(result, str)
            assert result == test_content
    
    def test_read_file_handles_file_not_found(self):
        """
        Test that read_file handles missing files gracefully
        Acceptance Criteria: DA-009 - Handles file permission errors
        """
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = self.fs_interface.read_file("/nonexistent/file.txt")
            
            # Should return None or empty string instead of crashing
            assert result is None or result == ""
    
    def test_read_file_handles_permission_errors(self):
        """
        Test that read_file handles permission errors gracefully
        Acceptance Criteria: DA-009 - Handles file permission errors  
        """
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = self.fs_interface.read_file("/restricted/file.txt")
            
            # Should return None or empty string instead of crashing
            assert result is None or result == ""
    
    def test_list_files_returns_matching_files(self):
        """
        Test that list_files returns files matching the pattern
        Acceptance Criteria: DA-010 - Supports recursive directory scanning
        """
        test_directory = "/test/directory"
        test_pattern = "*.md"
        
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [
                Path("/test/directory/file1.md"),
                Path("/test/directory/file2.md")
            ]
            
            result = self.fs_interface.list_files(test_directory, test_pattern)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(path, str) for path in result)
            assert all(path.endswith('.md') for path in result)
    
    def test_list_files_handles_directory_not_found(self):
        """
        Test that list_files handles missing directories gracefully
        Acceptance Criteria: DA-011 - Returns meaningful error messages
        """
        with patch('pathlib.Path.glob', side_effect=FileNotFoundError()):
            result = self.fs_interface.list_files("/nonexistent/directory", "*.txt")
            
            # Should return empty list instead of crashing
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_list_files_handles_permission_errors(self):
        """
        Test that list_files handles permission errors gracefully
        Acceptance Criteria: DA-009 - Handles file permission errors
        """
        with patch('pathlib.Path.glob', side_effect=PermissionError("Permission denied")):
            result = self.fs_interface.list_files("/restricted/directory", "*.txt")
            
            # Should return empty list instead of crashing
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_file_exists_returns_boolean(self):
        """
        Test that file_exists returns boolean indicating file existence
        Acceptance Criteria: DA-008 - Provides consistent file access interface
        """
        with patch('pathlib.Path.exists') as mock_exists:
            # Test existing file
            mock_exists.return_value = True
            assert self.fs_interface.file_exists("/existing/file.txt") is True
            
            # Test non-existing file
            mock_exists.return_value = False
            assert self.fs_interface.file_exists("/nonexistent/file.txt") is False
    
    def test_file_exists_handles_path_errors(self):
        """
        Test that file_exists handles path access errors gracefully
        Acceptance Criteria: DA-009 - Handles file permission errors
        """
        with patch('pathlib.Path.exists', side_effect=PermissionError("Permission denied")):
            result = self.fs_interface.file_exists("/restricted/file.txt")
            
            # Should return False instead of crashing
            assert result is False
    
    def test_get_file_stats_returns_file_statistics(self):
        """
        Test that get_file_stats returns file statistics object
        Acceptance Criteria: DA-008 - Provides consistent file access interface
        """
        mock_stat = Mock()
        mock_stat.st_size = 1024
        mock_stat.st_mtime = 1640995200.0  # 2022-01-01 timestamp
        
        with patch('pathlib.Path.stat', return_value=mock_stat):
            result = self.fs_interface.get_file_stats("/test/file.txt")
            
            assert isinstance(result, FileStats)
            assert result.size == 1024
            assert result.modified_time == 1640995200.0
    
    def test_get_file_stats_handles_file_not_found(self):
        """
        Test that get_file_stats handles missing files gracefully
        Acceptance Criteria: DA-011 - Returns meaningful error messages
        """
        with patch('pathlib.Path.stat', side_effect=FileNotFoundError()):
            result = self.fs_interface.get_file_stats("/nonexistent/file.txt")
            
            # Should return None instead of crashing
            assert result is None
    
    def test_get_file_stats_handles_permission_errors(self):
        """
        Test that get_file_stats handles permission errors gracefully
        Acceptance Criteria: DA-009 - Handles file permission errors
        """
        with patch('pathlib.Path.stat', side_effect=PermissionError("Permission denied")):
            result = self.fs_interface.get_file_stats("/restricted/file.txt")
            
            # Should return None instead of crashing
            assert result is None
    
    def test_recursive_directory_scanning_support(self):
        """
        Test that list_files supports recursive directory scanning
        Acceptance Criteria: DA-010 - Supports recursive directory scanning
        """
        test_directory = "/test/root"
        recursive_pattern = "**/*.py"  # Recursive pattern
        
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [
                Path("/test/root/file1.py"),
                Path("/test/root/subdir/file2.py"),
                Path("/test/root/subdir/deep/file3.py")
            ]
            
            result = self.fs_interface.list_files(test_directory, recursive_pattern)
            
            assert len(result) == 3
            assert any("subdir" in path for path in result)  # Contains subdirectory files
            assert any("deep" in path for path in result)    # Contains deep subdirectory files
    
    def test_meaningful_error_messages_integration(self):
        """
        Test that the interface provides meaningful error messages
        Acceptance Criteria: DA-011 - Returns meaningful error messages
        """
        # Test that operations don't crash and handle errors gracefully
        test_operations = [
            lambda: self.fs_interface.read_file("/nonexistent/file.txt"),
            lambda: self.fs_interface.list_files("/nonexistent/dir", "*.txt"),
            lambda: self.fs_interface.file_exists("/restricted/file.txt"),
            lambda: self.fs_interface.get_file_stats("/nonexistent/file.txt")
        ]
        
        # All operations should complete without exceptions
        for operation in test_operations:
            try:
                result = operation()
                # Results should be None, False, or empty list - not exceptions
                assert result is None or result is False or result == [] or result == ""
            except Exception as e:
                pytest.fail(f"Operation should not raise exception: {e}")
    
    def test_consistent_file_access_interface(self):
        """
        Test that all interface methods provide consistent behavior
        Acceptance Criteria: DA-008 - Provides consistent file access interface
        """
        # Test that all methods exist and return expected types
        assert hasattr(self.fs_interface, 'read_file')
        assert hasattr(self.fs_interface, 'list_files')
        assert hasattr(self.fs_interface, 'file_exists')
        assert hasattr(self.fs_interface, 'get_file_stats')
        
        # Test return types with mocked successful operations
        with patch('builtins.open', mock_open(read_data="test")):
            with patch('pathlib.Path.glob', return_value=[Path("/test.txt")]):
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('pathlib.Path.stat', return_value=Mock(st_size=100, st_mtime=1.0)):
                        
                        read_result = self.fs_interface.read_file("/test.txt")
                        list_result = self.fs_interface.list_files("/test", "*.txt")
                        exists_result = self.fs_interface.file_exists("/test.txt")
                        stats_result = self.fs_interface.get_file_stats("/test.txt")
                        
                        assert isinstance(read_result, str)
                        assert isinstance(list_result, list)
                        assert isinstance(exists_result, bool)
                        assert isinstance(stats_result, FileStats)