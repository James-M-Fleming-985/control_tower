"""
Data Access Layer Utilities - Shared Common Functions

This module provides shared utilities for all data access classes to eliminate
code duplication and provide consistent patterns across the layer.

Created: 2025-09-18
Phase: REFACTOR phase - extracting common patterns
Purpose: DRY principle implementation and maintainability improvement
"""

import json
import hashlib
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import uuid


class DataAccessUtilities:
    """
    Shared utilities for data access layer classes
    
    Provides common functionality for:
    - ID generation
    - Hash calculation  
    - Directory management
    - JSON operations
    - File operations with error handling
    """
    
    @staticmethod
    def generate_unique_id(prefix: str = "id", include_timestamp: bool = True) -> str:
        """
        Generate a unique ID with optional timestamp
        
        Args:
            prefix: Prefix for the ID
            include_timestamp: Whether to include timestamp in the ID
            
        Returns:
            Unique ID string
        """
        if include_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
            return f'{prefix}_{timestamp}_{random_suffix}'
        else:
            return f'{prefix}_{str(uuid.uuid4()).replace("-", "_")}'
    
    @staticmethod
    def calculate_data_integrity_hash(data: Dict) -> str:
        """
        Calculate SHA-256 integrity hash for data
        
        Args:
            data: Dictionary to hash
            
        Returns:
            SHA-256 hash string
        """
        # Create deterministic string representation
        sorted_content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(sorted_content.encode()).hexdigest()
    
    @staticmethod
    def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
        """
        Ensure directory exists, creating it if necessary
        
        Args:
            directory_path: Path to directory
            
        Returns:
            Path object for the directory
        """
        path_obj = Path(directory_path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    
    @staticmethod
    def safe_json_write(file_path: Union[str, Path], data: Dict, 
                       indent: int = 2, encoding: str = 'utf-8') -> bool:
        """
        Safely write JSON data to file with error handling
        
        Args:
            file_path: Path to write to
            data: Data to write
            indent: JSON indentation
            encoding: File encoding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except (IOError, OSError, json.JSONEncodeError):
            return False
    
    @staticmethod
    def safe_json_read(file_path: Union[str, Path], 
                      encoding: str = 'utf-8') -> Optional[Dict]:
        """
        Safely read JSON data from file with error handling
        
        Args:
            file_path: Path to read from
            encoding: File encoding
            
        Returns:
            Dictionary data or None if error
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except (IOError, OSError, json.JSONDecodeError):
            return None
    
    @staticmethod
    def safe_text_write(file_path: Union[str, Path], content: str,
                       encoding: str = 'utf-8') -> bool:
        """
        Safely write text content to file
        
        Args:
            file_path: Path to write to
            content: Text content to write
            encoding: File encoding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except (IOError, OSError):
            return False
    
    @staticmethod
    def safe_text_read(file_path: Union[str, Path],
                      encoding: str = 'utf-8') -> Optional[str]:
        """
        Safely read text content from file
        
        Args:
            file_path: Path to read from
            encoding: File encoding
            
        Returns:
            Text content or None if error
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except (IOError, OSError):
            return None
    
    @staticmethod
    def create_timestamped_filename(base_name: str, extension: str = '.json',
                                   timestamp_format: str = '%Y-%m-%d_%H-%M-%S') -> str:
        """
        Create filename with timestamp
        
        Args:
            base_name: Base name for file
            extension: File extension
            timestamp_format: Timestamp format string
            
        Returns:
            Timestamped filename
        """
        timestamp = datetime.now().strftime(timestamp_format)
        return f'{base_name}_{timestamp}{extension}'


class ThreadSafeDataAccess:
    """
    Base class providing thread-safe operations for data access classes
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._utilities = DataAccessUtilities()
    
    def safe_operation(self, operation_func, *args, **kwargs):
        """
        Execute operation with thread safety
        
        Args:
            operation_func: Function to execute safely
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the operation or None if error
        """
        try:
            with self._lock:
                return operation_func(*args, **kwargs)
        except Exception as e:
            # Log error in production
            return None
    
    def generate_id(self, prefix: str = "item") -> str:
        """Generate unique ID using utilities"""
        return self._utilities.generate_unique_id(prefix)
    
    def calculate_hash(self, data: Dict) -> str:
        """Calculate integrity hash using utilities"""
        return self._utilities.calculate_data_integrity_hash(data)
    
    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists using utilities"""
        return self._utilities.ensure_directory_exists(path)
    
    def write_json(self, path: Union[str, Path], data: Dict) -> bool:
        """Write JSON safely using utilities"""
        return self._utilities.safe_json_write(path, data)
    
    def read_json(self, path: Union[str, Path]) -> Optional[Dict]:
        """Read JSON safely using utilities"""
        return self._utilities.safe_json_read(path)


class DataAccessConfiguration:
    """
    Configuration management for data access layer
    """
    
    DEFAULT_SETTINGS = {
        'file_encoding': 'utf-8',
        'json_indent': 2,
        'backup_retention_days': 30,
        'performance_thresholds': {
            'file_discovery_max_time': 0.1,  # 100ms
            'recovery_max_time': 5.0,        # 5 seconds
            'min_files_per_second': 1000     # Performance requirement
        },
        'security_settings': {
            'encryption_enabled': True,
            'access_control_enabled': True,
            'integrity_verification': True
        }
    }
    
    def __init__(self, custom_settings: Optional[Dict] = None):
        """
        Initialize configuration with optional custom settings
        
        Args:
            custom_settings: Optional custom configuration overrides
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        if custom_settings:
            self._merge_settings(custom_settings)
    
    def _merge_settings(self, custom_settings: Dict):
        """Recursively merge custom settings with defaults"""
        for key, value in custom_settings.items():
            if key in self.settings and isinstance(self.settings[key], dict) and isinstance(value, dict):
                self.settings[key].update(value)
            else:
                self.settings[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_performance_threshold(self, threshold_name: str) -> float:
        """Get performance threshold value"""
        return self.get(f'performance_thresholds.{threshold_name}', 0.0)
    
    def is_security_enabled(self, feature: str) -> bool:
        """Check if security feature is enabled"""
        return self.get(f'security_settings.{feature}', False)


# Singleton configuration instance
_config_instance = None

def get_data_access_config() -> DataAccessConfiguration:
    """Get singleton configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = DataAccessConfiguration()
    return _config_instance

def set_data_access_config(config: DataAccessConfiguration):
    """Set singleton configuration instance"""
    global _config_instance
    _config_instance = config