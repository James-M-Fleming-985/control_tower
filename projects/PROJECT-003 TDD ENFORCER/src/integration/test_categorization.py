"""
Test Categorization Module

Categorizes tests as unit/integration/e2e based on directory structure.

Requirements: REQ-INT-003
"""

import os
from typing import List, Dict


class TestCategorization:
    """Categorize tests by pyramid level based on directory structure"""
    
    def categorize_by_directory(
        self, test_items: List[str]
    ) -> Dict[str, List[str]]:
        """
        Categorize tests based on directory structure
        
        Args:
            test_items: List of test items with paths
            
        Returns:
            Dict with 'unit', 'integration', 'e2e' keys
        """
        categories = {'Unit': [], 'Integration': [], 'E2E': []}
        
        for test_path in test_items:
            test_path_lower = test_path.lower()
            if ('/unit/' in test_path_lower or
                    test_path_lower.startswith('tests/unit')):
                categories['Unit'].append(test_path)
            elif ('/integration/' in test_path_lower or
                  test_path_lower.startswith('tests/integration')):
                categories['Integration'].append(test_path)
            elif ('/e2e/' in test_path_lower or
                  test_path_lower.startswith('tests/e2e')):
                categories['E2E'].append(test_path)
        
        return categories
    
    def categorize_by_naming(
        self, test_items: List[str]
    ) -> Dict[str, List[str]]:
        """
        Use naming patterns as fallback categorization
        
        Args:
            test_items: List of test items to categorize
            
        Returns:
            Dict with categorized tests
        """
        categories = {'Unit': [], 'Integration': [], 'E2E': []}
        
        for test_path in test_items:
            filename = os.path.basename(test_path).lower()
            if 'e2e' in filename or 'end_to_end' in filename:
                categories['E2E'].append(test_path)
            elif 'integration' in filename or '_int_' in filename:
                categories['Integration'].append(test_path)
            else:
                categories['Unit'].append(test_path)
        
        return categories
    
    def count_by_category(
        self, categorized_tests: Dict[str, List[str]]
    ) -> Dict[str, int]:
        """Count tests by category."""
        return {
            category: len(tests)
            for category, tests in categorized_tests.items()
        }
