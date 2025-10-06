"""
Test Discovery Module

Discovers tests in project directories using standard test naming conventions.

Requirements: REQ-INT-002
"""

from pathlib import Path
from typing import List, Dict


class TestDiscovery:
    """Test discovery using standard Python test patterns"""
    
    def discover_by_pattern(
        self, test_directory: str, patterns: List[str]
    ) -> List[str]:
        """
        Discover tests matching test_*.py and *_test.py patterns
        
        Args:
            test_directory: Directory to search
            patterns: List of filename patterns to match
            
        Returns:
            File paths with test functions/classes
        """
        test_files = set()
        base_path = Path(test_directory)
        
        if not base_path.exists():
            return []
        
        for pattern in patterns:
            test_files.update(str(p) for p in base_path.rglob(pattern))
        
        return sorted(test_files)
    
    def discover_in_subdirectories(
        self, base_directory: str, subdirectories: List[str]
    ) -> Dict[str, List[str]]:
        """
        Discover tests in unit/, integration/, e2e/ subdirectories
        
        Args:
            base_directory: Base directory to start search
            subdirectories: List of subdirectories to scan
            
        Returns:
            Dict mapping subdirectory to test list
        """
        results = {}
        base_path = Path(base_directory)
        
        for subdir in subdirectories:
            subdir_path = base_path / subdir
            if subdir_path.exists():
                test_files = sorted(
                    str(p) for p in subdir_path.rglob('test_*.py')
                )
                results[subdir] = test_files
            else:
                results[subdir] = []
        
        return results
    
    def list_all_tests(self, test_directory: str) -> List[str]:
        """
        Provide list of all discovered tests with metadata
        
        Args:
            test_directory: Directory to search
            
        Returns:
            List of test items with paths and metadata
        """
        return self.discover_by_pattern(
            test_directory,
            ['test_*.py', '*_test.py']
        )
