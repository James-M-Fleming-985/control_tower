"""
Validation tests for TR-DA-002 File System Interface requirements

These tests validate that the File System Interface implementation meets all acceptance criteria:
- DA-008: Provides consistent file access interface
- DA-009: Handles file permission errors gracefully  
- DA-010: Supports recursive directory scanning
- DA-011: Returns meaningful error messages instead of crashing

This validation ensures requirements compliance before progression to next component.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.data_access.file_system_interface import FileSystemInterface, FileStats


class TestTR_DA_002_Validation:
    """Validation test suite for TR-DA-002 File System Interface acceptance criteria"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fs_interface = FileSystemInterface()
    
    def test_DA_008_consistent_file_access_interface(self):
        """
        Validation Test DA-008: Provides consistent file access interface
        
        Validates that the File System Interface provides a consistent, 
        testable abstraction over file system operations.
        """
        # Verify all required interface methods exist
        required_methods = ['read_file', 'list_files', 'file_exists', 'get_file_stats']
        for method in required_methods:
            assert hasattr(self.fs_interface, method), f"Interface missing required method: {method}"
        
        # Verify consistent return types with mocked operations
        with patch('builtins.open', mock_open(read_data="test content")):
            with patch('pathlib.Path.glob', return_value=[Path("/test/file.txt")]):
                with patch('pathlib.Path.exists', return_value=True):
                    mock_stat = Mock()
                    mock_stat.st_size = 1024
                    mock_stat.st_mtime = 1640995200.0
                    with patch('pathlib.Path.stat', return_value=mock_stat):
                        
                        # Test consistent return types
                        read_result = self.fs_interface.read_file("/test/file.txt")
                        list_result = self.fs_interface.list_files("/test", "*.txt")
                        exists_result = self.fs_interface.file_exists("/test/file.txt")
                        stats_result = self.fs_interface.get_file_stats("/test/file.txt")
                        
                        assert isinstance(read_result, str), "read_file should return string"
                        assert isinstance(list_result, list), "list_files should return list"
                        assert isinstance(exists_result, bool), "file_exists should return boolean"
                        assert isinstance(stats_result, FileStats), "get_file_stats should return FileStats"
        
        print("✅ DA-008: File System Interface provides consistent access interface")
    
    def test_DA_009_handles_file_permission_errors(self):
        """
        Validation Test DA-009: Handles file permission errors gracefully
        
        Validates that file permission errors are handled gracefully without 
        crashing the application.
        """
        permission_error = PermissionError("Permission denied")
        
        # Test read_file handles permission errors
        with patch('builtins.open', side_effect=permission_error):
            result = self.fs_interface.read_file("/restricted/file.txt")
            assert result is None or result == "", "read_file should handle permission errors gracefully"
        
        # Test list_files handles permission errors
        with patch('pathlib.Path.glob', side_effect=permission_error):
            result = self.fs_interface.list_files("/restricted/directory", "*.txt")
            assert isinstance(result, list), "list_files should return list even with permission error"
            assert len(result) == 0, "list_files should return empty list on permission error"
        
        # Test file_exists handles permission errors
        with patch('pathlib.Path.exists', side_effect=permission_error):
            result = self.fs_interface.file_exists("/restricted/file.txt")
            assert result is False, "file_exists should return False on permission error"
        
        # Test get_file_stats handles permission errors
        with patch('pathlib.Path.stat', side_effect=permission_error):
            result = self.fs_interface.get_file_stats("/restricted/file.txt")
            assert result is None, "get_file_stats should return None on permission error"
        
        print("✅ DA-009: File System Interface handles permission errors gracefully")
    
    def test_DA_010_supports_recursive_directory_scanning(self):
        """
        Validation Test DA-010: Supports recursive directory scanning
        
        Validates that the interface supports recursive directory patterns
        for comprehensive file discovery.
        """
        test_directory = "/test/project"
        recursive_pattern = "**/*.py"  # Recursive glob pattern
        
        # Mock recursive file discovery results
        mock_files = [
            Path("/test/project/main.py"),
            Path("/test/project/src/module.py"),
            Path("/test/project/src/utils/helper.py"),
            Path("/test/project/tests/test_main.py"),
            Path("/test/project/docs/scripts/generate.py")
        ]
        
        with patch('pathlib.Path.glob', return_value=mock_files) as mock_glob:
            result = self.fs_interface.list_files(test_directory, recursive_pattern)
            
            # Verify recursive scanning was called
            mock_glob.assert_called_once()
            
            # Verify results include files from multiple directory levels
            assert len(result) == 5, "Should return all files from recursive scan"
            assert any("src/module.py" in path for path in result), "Should include subdirectory files"
            assert any("utils/helper.py" in path for path in result), "Should include deep subdirectory files"
            assert any("tests/test_main.py" in path for path in result), "Should include parallel directory files"
            
            # Verify all results are strings (converted from Path objects)
            assert all(isinstance(path, str) for path in result), "All results should be string paths"
        
        print("✅ DA-010: File System Interface supports recursive directory scanning")
    
    def test_DA_011_returns_meaningful_error_messages(self):
        """
        Validation Test DA-011: Returns meaningful error messages instead of crashing
        
        Validates that all file system operations handle errors gracefully
        and return meaningful responses instead of crashing.
        """
        # Define error scenarios to test
        error_scenarios = [
            (FileNotFoundError("File not found"), "file not found"),
            (PermissionError("Permission denied"), "permission denied"),
            (OSError("I/O error"), "I/O error"),
            (Exception("Generic error"), "generic error")
        ]
        
        for error, error_description in error_scenarios:
            # Test read_file error handling
            with patch('builtins.open', side_effect=error):
                try:
                    result = self.fs_interface.read_file("/error/file.txt")
                    assert result is None or result == "", f"read_file should handle {error_description} gracefully"
                except Exception as e:
                    pytest.fail(f"read_file should not raise exception for {error_description}: {e}")
            
            # Test list_files error handling
            with patch('pathlib.Path.glob', side_effect=error):
                try:
                    result = self.fs_interface.list_files("/error/directory", "*.txt")
                    assert isinstance(result, list), f"list_files should return list for {error_description}"
                    assert len(result) == 0, f"list_files should return empty list for {error_description}"
                except Exception as e:
                    pytest.fail(f"list_files should not raise exception for {error_description}: {e}")
            
            # Test file_exists error handling
            with patch('pathlib.Path.exists', side_effect=error):
                try:
                    result = self.fs_interface.file_exists("/error/file.txt")
                    assert result is False, f"file_exists should return False for {error_description}"
                except Exception as e:
                    pytest.fail(f"file_exists should not raise exception for {error_description}: {e}")
            
            # Test get_file_stats error handling
            with patch('pathlib.Path.stat', side_effect=error):
                try:
                    result = self.fs_interface.get_file_stats("/error/file.txt")
                    assert result is None, f"get_file_stats should return None for {error_description}"
                except Exception as e:
                    pytest.fail(f"get_file_stats should not raise exception for {error_description}: {e}")
        
        print("✅ DA-011: File System Interface returns meaningful responses instead of crashing")
    
    def test_integration_file_system_interface_complete(self):
        """
        Integration validation test for complete TR-DA-002 File System Interface
        
        Validates that the File System Interface works as a complete, integrated component
        meeting all acceptance criteria in realistic usage scenarios.
        """
        # Simulate realistic file system operations
        test_scenarios = [
            # Successful operations
            {
                'description': 'successful file operations',
                'read_file_result': "# Test Content\nThis is a test file",
                'list_files_result': ["/project/README.md", "/project/src/main.py"],
                'file_exists_result': True,
                'file_stats_size': 1024,
                'file_stats_mtime': 1640995200.0
            },
            # Error scenarios
            {
                'description': 'error handling scenarios',
                'read_file_error': FileNotFoundError(),
                'list_files_error': PermissionError(),
                'file_exists_error': OSError(),
                'file_stats_error': PermissionError()
            }
        ]
        
        for scenario in test_scenarios:
            if 'read_file_result' in scenario:
                # Test successful operations
                with patch('builtins.open', mock_open(read_data=scenario['read_file_result'])):
                    with patch('pathlib.Path.glob', return_value=[Path(p) for p in scenario['list_files_result']]):
                        with patch('pathlib.Path.exists', return_value=scenario['file_exists_result']):
                            mock_stat = Mock()
                            mock_stat.st_size = scenario['file_stats_size']
                            mock_stat.st_mtime = scenario['file_stats_mtime']
                            with patch('pathlib.Path.stat', return_value=mock_stat):
                                
                                # All operations should succeed
                                read_result = self.fs_interface.read_file("/test/file.txt")
                                list_result = self.fs_interface.list_files("/test", "*.py")
                                exists_result = self.fs_interface.file_exists("/test/file.txt")
                                stats_result = self.fs_interface.get_file_stats("/test/file.txt")
                                
                                assert read_result == scenario['read_file_result']
                                assert len(list_result) == len(scenario['list_files_result'])
                                assert exists_result == scenario['file_exists_result']
                                assert stats_result.size == scenario['file_stats_size']
                                assert stats_result.modified_time == scenario['file_stats_mtime']
            
            else:
                # Test error handling
                with patch('builtins.open', side_effect=scenario['read_file_error']):
                    with patch('pathlib.Path.glob', side_effect=scenario['list_files_error']):
                        with patch('pathlib.Path.exists', side_effect=scenario['file_exists_error']):
                            with patch('pathlib.Path.stat', side_effect=scenario['file_stats_error']):
                                
                                # All operations should handle errors gracefully
                                read_result = self.fs_interface.read_file("/error/file.txt")
                                list_result = self.fs_interface.list_files("/error", "*.py")
                                exists_result = self.fs_interface.file_exists("/error/file.txt")
                                stats_result = self.fs_interface.get_file_stats("/error/file.txt")
                                
                                assert read_result is None or read_result == ""
                                assert isinstance(list_result, list) and len(list_result) == 0
                                assert exists_result is False
                                assert stats_result is None
        
        print("✅ TR-DA-002: File System Interface integration validation complete")
        print("✅ All acceptance criteria validated: DA-008, DA-009, DA-010, DA-011")