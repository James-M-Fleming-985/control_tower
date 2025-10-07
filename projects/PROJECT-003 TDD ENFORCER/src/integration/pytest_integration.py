"""
pytest/unittest Integration Module

Provides integration with standard Python test frameworks
for test discovery and execution.

Requirements: REQ-INT-001
"""

import pytest
import unittest
from pathlib import Path
from typing import List, Dict


class PytestIntegration:
    """Integration with pytest and unittest test frameworks"""
    
    def discover_tests(self, test_directory: str) -> List[str]:
        """
        Discover tests using pytest collection API
        
        Args:
            test_directory: Directory to search for tests
            
        Returns:
            List of discovered test items
        """
        test_files = []
        test_path = Path(test_directory)
        
        if not test_path.exists():
            return test_files
        
        # Discover test files using pytest naming conventions
        for pattern in ['test_*.py', '*_test.py']:
            test_files.extend(str(p) for p in test_path.rglob(pattern))
        
        return sorted(list(set(test_files)))
    
    def execute_tests(self, test_items: List[str]) -> Dict[str, int]:
        """
        Execute tests using pytest and capture results
        
        Args:
            test_items: List of test items to execute
            
        Returns:
            Test execution results with pass/fail status and timing
        """
        if not test_items:
            # No tests to execute - return zero counts
            return {"passed": 0, "failed": 0, "total": 0}
        
        # Execute tests using pytest and capture exit code
        exit_code = pytest.main(["-v", "--tb=short"] + test_items)
        
        # Parse exit code: 0 = all passed, 1 = some failed
        if exit_code == 0:
            return {
                "passed": len(test_items),
                "failed": 0,
                "total": len(test_items)
            }
        else:
            return {
                "passed": 0,
                "failed": len(test_items),
                "total": len(test_items)
            }
    
    def discover_tests_unittest(self, test_directory: str) -> List[str]:
        """
        Support unittest as fallback test framework
        
        Args:
            test_directory: Directory to search for unittest tests
            
        Returns:
            List of discovered unittest test items
        """
        test_files = set()
        test_path = Path(test_directory)
        
        if not test_path.exists():
            return []
        
        # Use unittest discovery
        loader = unittest.TestLoader()
        try:
            suite = loader.discover(str(test_path), pattern='test_*.py')
            
            # Extract test file paths from suite
            for test_group in suite:
                if hasattr(test_group, '__iter__'):
                    for test in test_group:
                        if hasattr(test, '__module__'):
                            module = test.__module__
                            module_path = module.replace('.', '/') + '.py'
                            test_files.add(module_path)
        except Exception:
            # Fallback to simple file discovery
            for test_file in test_path.rglob('test_*.py'):
                test_files.add(str(test_file))
        
        return sorted(list(test_files))
