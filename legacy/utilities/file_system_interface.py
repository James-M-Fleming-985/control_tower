"""
File System Interface - TR-DA-002 implementation

Provides a consistent, testable abstraction over file system operations for the control tower system.
Handles file access, directory scanning, and error management gracefully.

Acceptance Criteria:
- DA-008: Provides consistent file access interface
- DA-009: Handles file permission errors gracefully  
- DA-010: Supports recursive directory scanning
- DA-011: Returns meaningful error messages instead of crashing
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import logging


@dataclass
class FileStats:
    """File statistics data structure"""
    size: int
    modified_time: float


class FileSystemInterface:
    """
    Abstracted file system interface for testable and reliable file operations.
    
    This interface provides a consistent abstraction over file system operations,
    enabling easy testing and error handling throughout the control tower system.
    """
    
    def __init__(self):
        """Initialize the file system interface"""
        self.logger = logging.getLogger(__name__)
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        Read the contents of a file as a string.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File contents as string, or None if error occurs
            
        Acceptance Criteria: DA-008, DA-009, DA-011
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            self.logger.warning(f"File not found: {file_path}")
            return None
        except PermissionError:
            self.logger.warning(f"Permission denied accessing file: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def list_files(self, directory: str, pattern: str) -> List[str]:
        """
        List files in a directory matching the given pattern.
        
        Args:
            directory: Directory path to search in
            pattern: Glob pattern to match (supports ** for recursive)
            
        Returns:
            List of file paths as strings, empty list if error occurs
            
        Acceptance Criteria: DA-008, DA-009, DA-010, DA-011
        """
        try:
            directory_path = Path(directory)
            matching_files = list(directory_path.glob(pattern))
            return [str(file_path) for file_path in matching_files]
        except FileNotFoundError:
            self.logger.warning(f"Directory not found: {directory}")
            return []
        except PermissionError:
            self.logger.warning(f"Permission denied accessing directory: {directory}")
            return []
        except Exception as e:
            self.logger.error(f"Error listing files in {directory} with pattern {pattern}: {e}")
            return []
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file exists, False otherwise (including on errors)
            
        Acceptance Criteria: DA-008, DA-009, DA-011
        """
        try:
            return Path(file_path).exists()
        except PermissionError:
            self.logger.warning(f"Permission denied checking file existence: {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking file existence {file_path}: {e}")
            return False
    
    def get_file_stats(self, file_path: str) -> Optional[FileStats]:
        """
        Get file statistics (size, modification time).
        
        Args:
            file_path: Path to the file to get stats for
            
        Returns:
            FileStats object with file information, or None if error occurs
            
        Acceptance Criteria: DA-008, DA-009, DA-011
        """
        try:
            file_path_obj = Path(file_path)
            stat_info = file_path_obj.stat()
            return FileStats(
                size=stat_info.st_size,
                modified_time=stat_info.st_mtime
            )
        except FileNotFoundError:
            self.logger.warning(f"File not found for stats: {file_path}")
            return None
        except PermissionError:
            self.logger.warning(f"Permission denied getting file stats: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting file stats {file_path}: {e}")
            return None