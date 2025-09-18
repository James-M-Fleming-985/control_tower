"""
REAL Test File Discovery - Data Access Layer
REQ-LAY-001-F1: REAL test file discovery and physical file verification

This module implements physical test file discovery with REAL file system verification,
meeting the performance requirement of 1000+ test files per second processing.

Created: 2025-09-18
Phase: GREEN phase implementation
Requirements Source: LAYER-003-01-02-001_data_access_requirements.md
"""

import os
import ast
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
import fnmatch
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from .utilities import ThreadSafeDataAccess, get_data_access_config


class RealTestFileDiscovery(ThreadSafeDataAccess):
    """
    REQ-LAY-001-F1: REAL test file discovery and physical file verification
    
    Discovers and verifies REAL test files from the physical file system
    with performance optimization for 1000+ files per second processing.
    """
    
    def __init__(self, base_directory: str):
        """
        Initialize test file discovery service
        
        Args:
            base_directory: Root directory for test file discovery
        """
        super().__init__()
        self.base_directory = self.ensure_dir(base_directory)
        self.config = get_data_access_config()
        
        self.test_file_patterns = [
            'test_*.py',
            '*_test.py', 
            'tests.py'
        ]
        self.excluded_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.pytest_cache'
        ]
        
        # Performance optimization settings
        self.max_workers = min(32, (os.cpu_count() or 1) + 4)
        self.cache = {}
        self.cache_lock = threading.Lock()
    
    def discover_real_test_files(self) -> List[str]:
        """
        REQ-LAY-001-F1-01: Discover REAL test files from physical file system
        
        Performance requirement: 1000+ test files per second
        
        Returns:
            List of absolute paths to discovered test files
        """
        discovered_files = []
        
        # Use concurrent processing for performance
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Get all Python files first
            python_files = list(self.base_directory.rglob('*.py'))
            
            # Filter test files concurrently
            futures = [
                executor.submit(self._is_test_file, str(file_path))
                for file_path in python_files
                if self._is_not_excluded(file_path)
            ]
            
            for future in futures:
                result = future.result()
                if result['is_test_file']:
                    discovered_files.append(result['file_path'])
        
        return discovered_files
    
    def verify_physical_test_file(self, file_path: str) -> Dict:
        """
        REQ-LAY-001-F1-02: Verify physical file existence and test content
        
        Args:
            file_path: Path to test file for verification
            
        Returns:
            Dictionary with verification results
        """
        verification_result = {
            'file_path': file_path,
            'file_exists': False,
            'is_test_file': False,
            'test_function_count': 0,
            'test_functions': [],
            'file_size': 0,
            'last_modified': None,
            'content_hash': None
        }
        
        try:
            file_path_obj = Path(file_path)
            
            # Physical existence verification
            if not file_path_obj.exists():
                return verification_result
            
            verification_result['file_exists'] = True
            verification_result['file_size'] = file_path_obj.stat().st_size
            verification_result['last_modified'] = file_path_obj.stat().st_mtime
            
            # Read and analyze file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate content hash for integrity verification
            verification_result['content_hash'] = self.calculate_hash({'content': content})
            
            # Parse AST to find test functions
            try:
                tree = ast.parse(content)
                test_functions = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith('test_'):
                            test_functions.append(node.name)
                
                verification_result['test_functions'] = test_functions
                verification_result['test_function_count'] = len(test_functions)
                verification_result['is_test_file'] = len(test_functions) > 0
                
            except SyntaxError:
                # File has syntax errors, not a valid test file
                verification_result['is_test_file'] = False
                
        except (IOError, OSError, PermissionError) as e:
            verification_result['error'] = str(e)
            
        return verification_result
    
    def validate_file_path(self, file_path: Optional[str]) -> Dict:
        """
        REQ-LAY-001-F1-04: REAL file path verification and input sanitization
        
        Args:
            file_path: File path to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'file_path': file_path,
            'is_valid': False,
            'is_safe': False,
            'normalized_path': None,
            'security_issues': []
        }
        
        if not file_path:
            validation_result['security_issues'].append('Empty or None file path')
            return validation_result
        
        try:
            # Normalize the path
            normalized = os.path.normpath(file_path)
            validation_result['normalized_path'] = normalized
            
            # Security checks
            security_issues = []
            
            # Check for path traversal attempts
            if '..' in normalized:
                security_issues.append('Path traversal detected')
            
            # Check if path is within allowed base directory
            try:
                resolved_path = Path(normalized).resolve()
                base_resolved = self.base_directory.resolve()
                
                if not str(resolved_path).startswith(str(base_resolved)):
                    security_issues.append('Path outside allowed directory')
                    
            except (OSError, ValueError):
                security_issues.append('Invalid path resolution')
            
            # Check for suspicious patterns
            suspicious_patterns = ['/etc/', '/root/', '/home/', '\\Windows\\']
            if any(pattern in normalized for pattern in suspicious_patterns):
                security_issues.append('Suspicious system path')
            
            validation_result['security_issues'] = security_issues
            validation_result['is_safe'] = len(security_issues) == 0
            validation_result['is_valid'] = (
                len(security_issues) == 0 and 
                len(normalized) > 0 and
                normalized.endswith('.py')
            )
            
        except Exception as e:
            validation_result['security_issues'].append(f'Validation error: {str(e)}')
            
        return validation_result
    
    def _is_test_file(self, file_path: str) -> Dict:
        """
        Internal method to check if a file is a test file
        
        Args:
            file_path: Path to check
            
        Returns:
            Dictionary with test file determination
        """
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name
        
        # Check cache first for performance
        with self.cache_lock:
            if file_path in self.cache:
                return self.cache[file_path]
        
        # Check if filename matches test patterns
        is_test_by_pattern = any(
            fnmatch.fnmatch(file_name, pattern)
            for pattern in self.test_file_patterns
        )
        
        result = {
            'file_path': file_path,
            'is_test_file': is_test_by_pattern,
            'match_pattern': None
        }
        
        if is_test_by_pattern:
            # Find which pattern matched
            for pattern in self.test_file_patterns:
                if fnmatch.fnmatch(file_name, pattern):
                    result['match_pattern'] = pattern
                    break
        
        # Cache result for performance
        with self.cache_lock:
            self.cache[file_path] = result
            
        return result
    
    def _is_not_excluded(self, file_path: Path) -> bool:
        """
        Check if file path is not in excluded patterns
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is not excluded
        """
        file_str = str(file_path)
        
        for pattern in self.excluded_patterns:
            if fnmatch.fnmatch(file_str, f'*{pattern}*'):
                return False
                
        return True
    
    def get_discovery_statistics(self) -> Dict:
        """
        Get statistics about the test file discovery process
        
        Returns:
            Dictionary with discovery statistics
        """
        return {
            'base_directory': str(self.base_directory),
            'test_patterns': self.test_file_patterns,
            'excluded_patterns': self.excluded_patterns,
            'cache_size': len(self.cache),
            'max_workers': self.max_workers
        }
    
    def clear_cache(self) -> None:
        """Clear the internal cache"""
        with self.cache_lock:
            self.cache.clear()