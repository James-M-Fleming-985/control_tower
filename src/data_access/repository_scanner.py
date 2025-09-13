"""
Repository Scanner - TR-DA-001 Implementation

Scans repository file systems to discover feature and milestone requirements.
Extracts metadata from markdown files and provides structured data for work item discovery.

This implements the Data Access Layer for the Phase 1 make what-next command.

Performance Optimizations:
- Efficient glob pattern matching
- Lazy evaluation for large repositories  
- Robust error handling with detailed logging
- Memory-efficient file processing
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import re
import logging
from datetime import datetime, date
from src.data_access.data_models import RawRequirement, RequirementMetadata
from src.business_logic.work_item_model import RequirementLevel, Priority

# Configure logging for better debugging
logger = logging.getLogger(__name__)


class RepositoryScanner:
    """
    High-performance repository scanner with comprehensive error handling
    
    Provides the core data access functionality for the make what-next command,
    discovering feature and milestone requirements from the file system with
    optimized algorithms and robust error recovery.
    """
    
    # Compile regex patterns once for better performance
    _METADATA_PATTERNS = {
        'title': re.compile(r'^#\s+(.+)', re.MULTILINE),
        'due_date': re.compile(r'\*\*Due Date\*\*:\s*(\d{4}-\d{2}-\d{2})'),
        'priority': re.compile(r'\*\*Priority\*\*:\s*(High|Medium|Low)', re.IGNORECASE),
        'level': re.compile(r'\*\*Level\*\*:\s*(FR|SR|PR|NSR|MR)'),
        'status': re.compile(r'\*\*Status\*\*:\s*([^*\n]+)'),
        'effort': re.compile(r'\*\*Effort\*\*:\s*([^*\n]+)')
    }
    
    # File discovery patterns for different repository structures
    _FILE_PATTERNS = [
        "requirements/features/*.md",
        "requirements/milestones/*.md", 
        "features/*.md",
        "milestones/*.md",
        "**/features/*.md",  # Nested features directories
        "**/milestones/*.md"  # Nested milestones directories
    ]
    
    def __init__(self):
        """Initialize scanner with performance optimizations"""
        self._scan_stats = {
            'repositories_scanned': 0,
            'files_discovered': 0,
            'files_parsed': 0,
            'parsing_errors': 0
        }
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Get scanning statistics for progress reporting"""
        return self._scan_stats.copy()
    
    def scan_repositories(self, repo_paths: List[str]) -> List[RawRequirement]:
        """
        Scan multiple repositories for requirement files with progress tracking
        
        Args:
            repo_paths: List of repository directory paths to scan
            
        Returns:
            List of RawRequirement objects discovered from all repositories
            
        Acceptance Criteria:
            - DA-001: Scans all 6 North Star repositories
            - DA-007: Reports scanning progress and statistics
        """
        logger.info(f"Starting scan of {len(repo_paths)} repositories")
        all_requirements = []
        self._scan_stats['repositories_scanned'] = 0
        
        for repo_path in repo_paths:
            try:
                logger.debug(f"Scanning repository: {repo_path}")
                repo_requirements = self.scan_single_repository(repo_path)
                all_requirements.extend(repo_requirements)
                self._scan_stats['repositories_scanned'] += 1
                
            except Exception as e:
                logger.error(f"Error scanning repository {repo_path}: {e}")
                # Continue with other repositories instead of failing completely
                continue
        
        logger.info(f"Scan complete. Found {len(all_requirements)} requirements from {self._scan_stats['repositories_scanned']} repositories")
        return all_requirements
    
    def scan_single_repository(self, repo_path: str) -> List[RawRequirement]:
        """
        Scan a single repository for requirement files with error resilience
        
        Args:
            repo_path: Path to repository directory
            
        Returns:
            List of RawRequirement objects from this repository
        """
        if not Path(repo_path).exists():
            logger.warning(f"Repository path does not exist: {repo_path}")
            return []
        
        requirements = []
        requirement_files = self.find_requirement_files(repo_path)
        self._scan_stats['files_discovered'] += len(requirement_files)
        
        for file_path in requirement_files:
            requirement = self.parse_requirement_file(file_path)
            if requirement is not None:
                requirements.append(requirement)
                self._scan_stats['files_parsed'] += 1
            else:
                self._scan_stats['parsing_errors'] += 1
        
        logger.debug(f"Repository {repo_path}: found {len(requirements)} valid requirements from {len(requirement_files)} files")
        return requirements
    
    def find_requirement_files(self, repo_path: str) -> List[str]:
        """
        Find all requirement files in a repository using optimized glob patterns
        
        Args:
            repo_path: Path to repository directory
            
        Returns:
            List of file paths matching requirement patterns
            
        Acceptance Criteria:
            - DA-002: Discovers feature requirement files
            - DA-003: Discovers milestone requirement files
        """
        found_files = []
        repo_path_obj = Path(repo_path)
        
        # Use cached patterns for better performance
        for pattern in self._FILE_PATTERNS:
            try:
                matching_files = repo_path_obj.glob(pattern)
                # Convert to strings and filter out non-files
                valid_files = [str(f) for f in matching_files if f.is_file()]
                found_files.extend(valid_files)
                
            except (OSError, PermissionError) as e:
                logger.warning(f"Cannot access pattern {pattern} in {repo_path}: {e}")
                continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for file_path in found_files:
            if file_path not in seen:
                seen.add(file_path)
                unique_files.append(file_path)
        
        logger.debug(f"Found {len(unique_files)} requirement files in {repo_path}")
        return unique_files
    
    def parse_requirement_file(self, file_path: str) -> Optional[RawRequirement]:
        """
        Parse a single requirement file with comprehensive error handling
        
        Args:
            file_path: Path to requirement file
            
        Returns:
            RawRequirement object or None if parsing fails
            
        Acceptance Criteria:
            - DA-006: Handles missing or corrupted files gracefully
        """
        try:
            # Use Path for better file handling
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.debug(f"File does not exist: {file_path}")
                return None
            
            if not file_path_obj.is_file():
                logger.debug(f"Path is not a file: {file_path}")
                return None
            
            # Read with multiple encoding attempts for better compatibility
            content = self._read_file_with_fallback_encoding(file_path_obj)
            if content is None:
                return None
            
            # Extract metadata using optimized patterns
            metadata = self.extract_metadata(content)
            
            return RawRequirement(
                file_path=str(file_path_obj),
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Unexpected error parsing file {file_path}: {e}")
            return None
    
    def _read_file_with_fallback_encoding(self, file_path: Path) -> Optional[str]:
        """
        Read file with multiple encoding attempts for better compatibility
        
        Args:
            file_path: Path object for the file
            
        Returns:
            File content as string or None if all encodings fail
        """
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.debug(f"Cannot read file {file_path}: {e}")
                return None
        
        logger.warning(f"Could not decode file {file_path} with any encoding")
        return None
    
    def extract_metadata(self, content: str) -> RequirementMetadata:
        """
        Extract structured metadata from requirement file content with optimized parsing
        
        Args:
            content: Raw content of requirement file
            
        Returns:
            RequirementMetadata object with extracted information
            
        Acceptance Criteria:
            - DA-004: Extracts due dates correctly
            - DA-005: Extracts requirement levels correctly
        """
        # Use pre-compiled patterns for better performance
        title = self._extract_title(content)
        id_value = self._generate_id_from_title(title)
        due_date = self._extract_due_date(content)
        priority = self._extract_priority(content)
        level = self._extract_requirement_level(content)
        status = self._extract_status(content)
        effort = self._extract_effort(content)
        description = self._extract_description(content)
        
        return RequirementMetadata(
            id=id_value,
            title=title,
            due_date=due_date,
            priority=priority,
            requirement_level=level,
            status=status,
            effort_estimate=effort,
            description=description
        )
    
    def _extract_title(self, content: str) -> str:
        """Extract title from first header with fallbacks"""
        match = self._METADATA_PATTERNS['title'].search(content)
        if match:
            return match.group(1).strip()
        
        # Fallback: try to extract from filename patterns
        lines = content.split('\n')[:5]  # Check first 5 lines only
        for line in lines:
            line = line.strip()
            if line and not line.startswith('*') and not line.startswith('-'):
                return line[:50]  # Truncate long titles
        
        return "Unknown Requirement"
    
    def _generate_id_from_title(self, title: str) -> str:
        """Generate a clean ID from title"""
        # Remove special characters and create readable ID
        clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        words = clean_title.split()[:3]  # Use first 3 words
        return '-'.join(word.upper() for word in words)[:20]
    
    def _extract_due_date(self, content: str) -> Optional[date]:
        """Extract due date with robust error handling"""
        match = self._METADATA_PATTERNS['due_date'].search(content)
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d').date()
            except ValueError as e:
                logger.debug(f"Invalid date format: {match.group(1)}: {e}")
        return None
    
    def _extract_priority(self, content: str) -> Priority:
        """Extract priority with case-insensitive matching"""
        match = self._METADATA_PATTERNS['priority'].search(content)
        if match:
            priority_text = match.group(1).lower()
            if priority_text == 'high':
                return Priority.HIGH
            elif priority_text == 'low':
                return Priority.LOW
        return Priority.MEDIUM  # Default
    
    def _extract_requirement_level(self, content: str) -> RequirementLevel:
        """Extract requirement level with validation"""
        match = self._METADATA_PATTERNS['level'].search(content)
        if match:
            try:
                return RequirementLevel(match.group(1))
            except ValueError:
                logger.debug(f"Invalid requirement level: {match.group(1)}")
        return RequirementLevel.FR  # Default
    
    def _extract_status(self, content: str) -> str:
        """Extract status with trimming"""
        match = self._METADATA_PATTERNS['status'].search(content)
        return match.group(1).strip() if match else "Not Started"
    
    def _extract_effort(self, content: str) -> str:
        """Extract effort estimate with trimming"""
        match = self._METADATA_PATTERNS['effort'].search(content)
        return match.group(1).strip() if match else "Unknown"
    
    def _extract_description(self, content: str) -> str:
        """Extract meaningful description from content"""
        # Remove metadata lines for cleaner description
        lines = content.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip metadata lines and headers
            if not line.startswith('**') and not line.startswith('#') and line:
                description_lines.append(line)
                if len(description_lines) >= 3:  # Get first 3 content lines
                    break
        
        description = ' '.join(description_lines)
        return description[:200] + "..." if len(description) > 200 else description