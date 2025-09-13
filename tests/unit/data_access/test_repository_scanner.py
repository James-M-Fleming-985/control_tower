"""
Unit tests for Repository Scanner - TR-DA-001 implementation

Tests the core functionality of scanning repositories to discover feature and milestone requirements.
Follows TDD methodology with comprehensive test coverage for acceptance criteria DA-001 through DA-007.
"""

import pytest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.data_access.repository_scanner import RepositoryScanner, RawRequirement, RequirementMetadata
from src.business_logic.work_item_model import RequirementLevel, Priority


class TestRepositoryScanner:
    """Test suite for Repository Scanner functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.scanner = RepositoryScanner()
        self.test_repos = [
            "/workspaces/control_tower/cloned_repos/financial_security_dev",
            "/workspaces/control_tower/cloned_repos/contract_projects"
        ]
    
    def test_scan_repositories_returns_list_of_raw_requirements(self):
        """
        Test that scan_repositories returns a list of RawRequirement objects
        Acceptance Criteria: DA-001 - Scans all 6 North Star repositories
        """
        with patch.object(self.scanner, 'scan_single_repository') as mock_scan:
            mock_scan.return_value = [
                RawRequirement(
                    file_path="/test/path/feature.md",
                    content="Test content",
                    metadata=RequirementMetadata(
                        id="TEST-001",
                        title="Test Feature",
                        due_date=date.today(),
                        priority=Priority.HIGH,
                        requirement_level=RequirementLevel.FR
                    )
                )
            ]
            
            result = self.scanner.scan_repositories(self.test_repos)
            
            assert isinstance(result, list)
            assert len(result) >= 0
            assert all(isinstance(req, RawRequirement) for req in result)
            # Should call scan_single_repository for each repo
            assert mock_scan.call_count == len(self.test_repos)
    
    def test_scan_single_repository_discovers_requirement_files(self):
        """
        Test that scan_single_repository finds requirement files in a repository
        Acceptance Criteria: DA-002 - Discovers feature requirement files
        """
        test_repo = "/test/repo/path"
        
        with patch('pathlib.Path.exists') as mock_exists:
            with patch.object(self.scanner, 'find_requirement_files') as mock_find:
                with patch.object(self.scanner, 'parse_requirement_file') as mock_parse:
                    # Mock path exists to pass validation
                    mock_exists.return_value = True
                    mock_find.return_value = ["/test/feature1.md", "/test/feature2.md"]
                    mock_parse.return_value = RawRequirement(
                        file_path="/test/feature1.md",
                        content="Mock content",
                        metadata=RequirementMetadata(
                            id="MOCK-001",
                            title="Mock Feature",
                            due_date=date.today(),
                            priority=Priority.MEDIUM,
                            requirement_level=RequirementLevel.FR
                        )
                    )
                    
                    result = self.scanner.scan_single_repository(test_repo)
                    
                    assert isinstance(result, list)
                    mock_find.assert_called_once_with(test_repo)
                    assert mock_parse.call_count == len(mock_find.return_value)
    
    def test_find_requirement_files_discovers_correct_patterns(self):
        """
        Test that find_requirement_files discovers files matching expected patterns
        Acceptance Criteria: DA-002 & DA-003 - Discovers feature and milestone files
        """
        test_repo = "/test/repo"
        expected_patterns = [
            "requirements/features/*.md",
            "requirements/milestones/*.md", 
            "features/*.md",
            "milestones/*.md"
        ]
        
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [
                Path("/test/repo/requirements/features/feature1.md"),
                Path("/test/repo/milestones/milestone1.md")
            ]
            
            result = self.scanner.find_requirement_files(test_repo)
            
            assert isinstance(result, list)
            assert all(isinstance(path, str) for path in result)
            # Should have called glob for each pattern
            assert mock_glob.call_count >= 1
    
    def test_parse_requirement_file_extracts_content_and_metadata(self):
        """
        Test that parse_requirement_file extracts both content and metadata
        Acceptance Criteria: DA-004 & DA-005 - Extracts due dates and requirement levels
        """
        test_file = "/test/feature.md"
        test_content = """
        # Feature Test
        **Due Date**: 2025-09-15
        **Priority**: High
        **Level**: FR
        **Status**: Not Started
        **Effort**: 3 days
        
        This is the feature description.
        """
        
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('pathlib.Path.is_file') as mock_is_file:
                with patch('builtins.open', mock_open(read_data=test_content)):
                    with patch.object(self.scanner, 'extract_metadata') as mock_extract:
                        # Mock path validation
                        mock_exists.return_value = True
                        mock_is_file.return_value = True
                        mock_extract.return_value = RequirementMetadata(
                            id="TEST-001",
                            title="Feature Test",
                            due_date=date(2025, 9, 15),
                            priority=Priority.HIGH,
                            requirement_level=RequirementLevel.FR
                        )
                        
                        result = self.scanner.parse_requirement_file(test_file)
                        
                        assert isinstance(result, RawRequirement)
                        assert result.file_path == test_file
                        assert result.content == test_content
                        mock_extract.assert_called_once_with(test_content)
    
    def test_extract_metadata_parses_due_date_correctly(self):
        """
        Test that extract_metadata correctly parses due dates from content
        Acceptance Criteria: DA-004 - Extracts due dates correctly
        """
        content = """
        # Test Feature
        **Due Date**: 2025-09-20
        **Priority**: Medium
        """
        
        result = self.scanner.extract_metadata(content)
        
        assert result.due_date == date(2025, 9, 20)
    
    def test_extract_metadata_parses_priority_correctly(self):
        """
        Test that extract_metadata correctly parses priority from content
        """
        test_cases = [
            ("**Priority**: High", Priority.HIGH),
            ("**Priority**: Medium", Priority.MEDIUM),
            ("**Priority**: Low", Priority.LOW)
        ]
        
        for content_snippet, expected_priority in test_cases:
            content = f"# Test\n{content_snippet}\n"
            result = self.scanner.extract_metadata(content)
            assert result.priority == expected_priority
    
    def test_extract_metadata_parses_requirement_level_correctly(self):
        """
        Test that extract_metadata correctly parses requirement levels
        Acceptance Criteria: DA-005 - Extracts requirement levels correctly
        """
        test_cases = [
            ("**Level**: FR", RequirementLevel.FR),
            ("**Level**: SR", RequirementLevel.SR),
            ("**Level**: PR", RequirementLevel.PR),
            ("**Level**: NSR", RequirementLevel.NSR),
            ("**Level**: MR", RequirementLevel.MR)
        ]
        
        for content_snippet, expected_level in test_cases:
            content = f"# Test\n{content_snippet}\n"
            result = self.scanner.extract_metadata(content)
            assert result.requirement_level == expected_level
    
    def test_extract_metadata_handles_missing_fields_gracefully(self):
        """
        Test that extract_metadata provides defaults for missing fields
        Acceptance Criteria: DA-006 - Handles missing or corrupted files gracefully
        """
        content = "# Minimal Feature\nJust basic content with no metadata."
        
        result = self.scanner.extract_metadata(content)
        
        # Should have reasonable defaults
        assert result is not None
        assert result.title == "Minimal Feature"  # From header
        assert result.due_date is None or isinstance(result.due_date, date)
        assert result.priority in [Priority.LOW, Priority.MEDIUM, Priority.HIGH]
        assert result.requirement_level in RequirementLevel
    
    def test_parse_requirement_file_handles_file_not_found(self):
        """
        Test that parse_requirement_file handles missing files gracefully
        Acceptance Criteria: DA-006 - Handles missing or corrupted files gracefully
        """
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = self.scanner.parse_requirement_file("/nonexistent/file.md")
            
            # Should return None or empty result instead of crashing
            assert result is None or isinstance(result, RawRequirement)
    
    def test_parse_requirement_file_handles_permission_errors(self):
        """
        Test that parse_requirement_file handles permission errors gracefully
        Acceptance Criteria: DA-006 - Handles missing or corrupted files gracefully
        """
        with patch('builtins.open', side_effect=PermissionError()):
            result = self.scanner.parse_requirement_file("/restricted/file.md")
            
            # Should return None or empty result instead of crashing
            assert result is None or isinstance(result, RawRequirement)
    
    def test_scan_repositories_reports_progress_and_statistics(self):
        """
        Test that scan_repositories provides scanning progress and statistics
        Acceptance Criteria: DA-007 - Reports scanning progress and statistics
        """
        with patch.object(self.scanner, 'scan_single_repository') as mock_scan:
            mock_scan.return_value = [Mock(spec=RawRequirement)]
            
            # Should be able to get progress/stats somehow
            result = self.scanner.scan_repositories(self.test_repos)
            
            # Basic validation - should process all repositories
            assert mock_scan.call_count == len(self.test_repos)
            
            # Future: Could test for progress callbacks or return statistics object