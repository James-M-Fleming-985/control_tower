"""
Utility Functions for Requirements Parser & Test Generator Layer

Provides helper functions for parsing, validation, and test generation
with FR-002 compliance and forcing functions.

Created: 2025-09-15
Layer: Data Access (Requirements Parser & Test Generator)
TDD Phase: Architecture Definition (Pre-RED)
"""

import re
import hashlib
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime
import json

from .interfaces import ValidationResult, AcceptanceCriteria


class MarkdownParser:
    """Utility class for parsing markdown content"""
    
    @staticmethod
    def extract_sections(content: str) -> Dict[str, str]:
        """Extract sections from markdown content by headers"""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for headers
            if line.strip().startswith('#'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip('#').strip().lower()
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def extract_metadata_fields(content: str) -> Dict[str, str]:
        """Extract structured metadata fields from markdown"""
        metadata = {}
        
        # Pattern for **Field Name**: Value format
        pattern = re.compile(r'\*\*([^*]+)\*\*:\s*(.+)', re.IGNORECASE)
        matches = pattern.findall(content)
        
        for field_name, value in matches:
            clean_field = field_name.strip().lower().replace(' ', '_')
            metadata[clean_field] = value.strip()
        
        return metadata
    
    @staticmethod
    def extract_list_items(content: str, list_type: str = "bullet") -> List[str]:
        """Extract list items from markdown content"""
        items = []
        
        if list_type == "bullet":
            pattern = re.compile(r'^\s*[-*+]\s+(.+)', re.MULTILINE)
        elif list_type == "numbered":
            pattern = re.compile(r'^\s*\d+\.\s+(.+)', re.MULTILINE)
        elif list_type == "checkbox":
            pattern = re.compile(r'^\s*-\s*\[([ x])\]\s+(.+)', re.MULTILINE)
            matches = pattern.findall(content)
            return [{"checked": check.lower() == 'x', "text": text.strip()} for check, text in matches]
        else:
            return items
        
        matches = pattern.findall(content)
        items = [match.strip() for match in matches]
        
        return items


class RequirementValidator:
    """Utility class for validating requirements with forcing functions"""
    
    @staticmethod
    def validate_requirement_id(req_id: str) -> ValidationResult:
        """Validate requirement ID format with forcing function"""
        result = ValidationResult(is_valid=True)
        
        if not req_id:
            result.add_error("Requirement ID cannot be empty")
            return result
        
        # Check format patterns
        valid_patterns = [
            re.compile(r'^[A-Z]+-[A-Z]+-[A-Z]+-\d+$'),  # LAY-APP-REQUIREMENTS-001
            re.compile(r'^[A-Z]+-[A-Z]+-\w+-\d+$'),     # FEATURE-MAKE-001
            re.compile(r'^[A-Z]+-\d+-\d+-\d+$'),        # FEATURE-001-002-003
        ]
        
        is_valid_format = any(pattern.match(req_id) for pattern in valid_patterns)
        
        if not is_valid_format:
            result.add_error(f"Invalid requirement ID format: {req_id}")
            result.add_error("Expected formats: PREFIX-TYPE-NAME-NUMBER or PREFIX-NUMBER-NUMBER-NUMBER")
        
        # Set forcing function result
        if result.is_valid:
            output = f"✅ Requirement ID validated: {req_id} (format valid)"
        else:
            output = f"❌ Requirement ID validation failed: {req_id} (invalid format)"
        
        result.set_forcing_function_result(result.is_valid, output)
        
        return result
    
    @staticmethod
    def validate_acceptance_criteria(criteria_list: List[Dict[str, Any]]) -> ValidationResult:
        """Validate acceptance criteria with forcing function"""
        result = ValidationResult(is_valid=True)
        
        if not criteria_list:
            result.add_error("At least one acceptance criterion is required")
            result.set_forcing_function_result(False, "❌ Acceptance criteria validation failed: no criteria found")
            return result
        
        for i, criteria in enumerate(criteria_list):
            if not isinstance(criteria, dict):
                result.add_error(f"Criterion {i+1} is not a valid dictionary")
                continue
            
            # Check required fields
            if 'id' not in criteria:
                result.add_error(f"Criterion {i+1} missing 'id' field")
            
            if 'description' not in criteria:
                result.add_error(f"Criterion {i+1} missing 'description' field")
            
            # Check description quality
            description = criteria.get('description', '')
            if len(description.strip()) < 10:
                result.add_warning(f"Criterion {i+1} has very short description (may not be testable)")
            
            # Check for testable language
            testable_keywords = ['should', 'must', 'when', 'then', 'verify', 'ensure', 'validate']
            has_testable_language = any(keyword in description.lower() for keyword in testable_keywords)
            
            if not has_testable_language:
                result.add_warning(f"Criterion {i+1} may not be easily testable (lacks action verbs)")
        
        # Set forcing function result
        criteria_count = len(criteria_list)
        error_count = len(result.error_messages)
        warning_count = len(result.warning_messages)
        
        if result.is_valid:
            output = f"✅ Acceptance criteria validated: {criteria_count} criteria, {warning_count} warnings"
        else:
            output = f"❌ Acceptance criteria validation failed: {error_count} errors, {warning_count} warnings"
        
        result.set_forcing_function_result(result.is_valid, output)
        
        return result


class TestCodeGenerator:
    """Utility class for generating test code snippets"""
    
    @staticmethod
    def generate_test_function_name(criteria_id: str, description: str) -> str:
        """Generate a valid pytest function name from criteria"""
        # Clean and normalize the description
        clean_desc = re.sub(r'[^\w\s]', '', description.lower())
        words = clean_desc.split()[:5]  # Limit to first 5 words
        desc_part = '_'.join(words)
        
        # Clean criteria ID
        clean_id = criteria_id.lower().replace('-', '_')
        
        return f"test_{clean_id}_{desc_part}"
    
    @staticmethod
    def generate_test_skeleton(
        test_name: str,
        criteria_description: str,
        requirement_id: str
    ) -> str:
        """Generate a basic test function skeleton"""
        return f'''def {test_name}():
    """
    Test for: {criteria_description}
    Requirement: {requirement_id}
    
    This is a failing test that needs implementation.
    """
    # Arrange
    # TODO: Set up test data and mocks
    
    # Act
    # TODO: Execute the code under test
    
    # Assert
    # TODO: Verify the expected behavior
    assert False, "Test not implemented - implement code to make this pass"'''
    
    @staticmethod
    def generate_test_imports() -> List[str]:
        """Generate standard imports for test files"""
        return [
            "import pytest",
            "from unittest.mock import Mock, patch, MagicMock, call",
            "from pathlib import Path",
            "import tempfile",
            "import json",
            "from typing import Any, Dict, List",
        ]
    
    @staticmethod
    def generate_fixtures() -> List[str]:
        """Generate common pytest fixtures"""
        return [
            '''@pytest.fixture
def temp_requirement_file():
    """Create a temporary requirement file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# Test Requirement

**Requirement ID**: TEST-REQ-001
**Requirement Type**: Feature Requirement

## Primary Objective
Test the requirements parsing functionality

## Acceptance Criteria
- [x] **AC-001**: Should parse requirement ID correctly
- [ ] **AC-002**: Should extract acceptance criteria
        """)
        f.flush()
        yield f.name
    
    # Cleanup
    Path(f.name).unlink(missing_ok=True)''',
            
            '''@pytest.fixture
def mock_parser():
    """Create a mock parser for testing"""
    parser = Mock()
    parser.parse_work_item_requirements.return_value = Mock()
    parser.extract_acceptance_criteria.return_value = []
    parser.validate_requirement_completeness.return_value = Mock(is_valid=True)
    parser.create_requirement_traceability.return_value = Mock()
    return parser''',
            
            '''@pytest.fixture
def sample_parsed_requirement():
    """Create a sample parsed requirement for testing"""
    from src.data_access.interfaces import ParsedRequirement
    return ParsedRequirement(
        requirement_id="TEST-REQ-001",
        requirement_type="Feature Requirement",
        primary_objective="Test parsing functionality",
        acceptance_criteria=[
            {"id": "AC-001", "description": "Should parse correctly"},
            {"id": "AC-002", "description": "Should validate properly"}
        ]
    )'''
        ]


class FileSystemUtils:
    """Utility class for file system operations with validation"""
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> ValidationResult:
        """Validate file path exists and is accessible"""
        result = ValidationResult(is_valid=True)
        
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                result.add_error(f"File does not exist: {file_path}")
            elif not path_obj.is_file():
                result.add_error(f"Path is not a file: {file_path}")
            elif not path_obj.stat().st_size > 0:
                result.add_warning(f"File is empty: {file_path}")
            
            # Check read permissions
            try:
                with open(path_obj, 'r') as f:
                    f.read(1)  # Try to read first character
            except PermissionError:
                result.add_error(f"No read permission for file: {file_path}")
            except Exception as e:
                result.add_error(f"Cannot read file {file_path}: {e}")
        
        except Exception as e:
            result.add_error(f"Invalid file path {file_path}: {e}")
        
        # Set forcing function result
        if result.is_valid:
            file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
            output = f"✅ File validated: {file_path} (size: {file_size} bytes)"
        else:
            output = f"❌ File validation failed: {file_path}"
        
        result.set_forcing_function_result(result.is_valid, output)
        
        return result
    
    @staticmethod
    def create_directory_if_not_exists(dir_path: Union[str, Path]) -> bool:
        """Create directory if it doesn't exist"""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Failed to create directory {dir_path}: {e}")
            return False
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path]) -> str:
        """Get SHA-256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def backup_file(file_path: Union[str, Path], backup_dir: Optional[str] = None) -> Optional[Path]:
        """Create backup of file with timestamp"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return None
            
            if backup_dir:
                backup_path = Path(backup_dir)
            else:
                backup_path = source_path.parent / "backups"
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_file_path = backup_path / backup_filename
            
            # Copy file
            import shutil
            shutil.copy2(source_path, backup_file_path)
            
            return backup_file_path
            
        except Exception as e:
            print(f"❌ Backup failed for {file_path}: {e}")
            return None


class TimestampUtils:
    """Utility class for timestamp operations"""
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def get_formatted_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object"""
        try:
            return datetime.fromisoformat(timestamp_str)
        except Exception:
            return None


class IDGenerator:
    """Utility class for generating IDs"""
    
    @staticmethod
    def generate_acceptance_criteria_id(index: int, prefix: str = "AC") -> str:
        """Generate acceptance criteria ID"""
        return f"{prefix}-{index:03d}"
    
    @staticmethod
    def generate_test_id(requirement_id: str, criteria_id: str) -> str:
        """Generate test ID from requirement and criteria IDs"""
        req_clean = requirement_id.replace('-', '_').lower()
        criteria_clean = criteria_id.replace('-', '_').lower()
        return f"test_{req_clean}_{criteria_clean}"
    
    @staticmethod
    def generate_traceability_id(requirement_id: str) -> str:
        """Generate traceability ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TRACE_{requirement_id}_{timestamp}"


def format_terminal_output(
    status: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """Format consistent terminal output for forcing functions"""
    if status.lower() == "success":
        icon = "✅"
    elif status.lower() == "warning":
        icon = "⚠️"
    elif status.lower() == "error":
        icon = "❌"
    else:
        icon = "ℹ️"
    
    output = f"{icon} {message}"
    
    if details:
        detail_lines = []
        for key, value in details.items():
            detail_lines.append(f"  - {key}: {value}")
        if detail_lines:
            output += "\n" + "\n".join(detail_lines)
    
    return output


def measure_execution_time(func):
    """Decorator to measure and log execution time"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            print(f"⏱️ {func.__name__} executed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            print(f"❌ {func.__name__} failed after {execution_time:.3f} seconds: {e}")
            raise
    
    return wrapper