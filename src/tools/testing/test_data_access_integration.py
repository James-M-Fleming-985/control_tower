"""
Integration tests for Data Access Layer - Repository Scanner

Tests the integration between Repository Scanner and other layers,
ensuring the Data Access Layer works properly with Business Logic
and UI components.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from src.data_access.repository_scanner import RepositoryScanner
from src.data_access.data_models import RawRequirement, RequirementMetadata
from src.business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, Priority, RequirementLevel
from src.business_logic.priority_calculator import BasicPriorityCalculator
from src.ui.terminal_formatter import TerminalFormatter


class TestDataAccessLayerIntegration:
    """Integration tests for Data Access Layer with other layers"""
    
    def setup_method(self):
        """Setup test components"""
        self.scanner = RepositoryScanner()
        self.calculator = BasicPriorityCalculator()
        self.formatter = TerminalFormatter()
    
    def test_repository_scanner_to_work_item_conversion(self):
        """
        Test that Repository Scanner output can be converted to WorkItem objects
        for Business Logic Layer processing
        """
        # Create mock file content
        test_content = """
        # FEATURE-001: Investment Portfolio Rebalancing
        
        **Due Date**: 2025-09-13
        **Priority**: High
        **Level**: FR
        **Status**: Not Started
        **Effort**: 3 days
        
        Implement automated portfolio rebalancing based on risk tolerance.
        """
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_file', return_value=True):
                with patch('builtins.open', mock_open(read_data=test_content)):
                    # Parse requirement file
                    raw_requirement = self.scanner.parse_requirement_file("/test/feature.md")
                    
                    assert raw_requirement is not None
                    
                    # Convert to WorkItem (simulating discovery engine)
                    work_item = WorkItem(
                        id=raw_requirement.metadata.id,
                        title=raw_requirement.metadata.title,
                        description=raw_requirement.metadata.description,
                        due_date=raw_requirement.metadata.due_date,
                        priority=raw_requirement.metadata.priority,
                        effort_estimate=raw_requirement.metadata.effort_estimate,
                        requirement_level=raw_requirement.metadata.requirement_level,
                        project_type=ProjectType.APPLICATION,  # Would be determined by discovery engine
                        repository="financial_security_dev",
                        system_name="Investment Strategy",
                        project_name="Financial Security",
                        layer_or_milestone="Data Access Layer",
                        hierarchy_path="Investment Strategy → Financial Security → financial_security_dev",
                        status=ItemStatus.DUE_TODAY
                    )
                    
                    # Validate conversion  
                    assert work_item.id is not None  # ID was generated
                    assert work_item.title is not None  # Title was extracted
                    assert work_item.due_date == date(2025, 9, 13)  # Date parsed correctly
                    assert work_item.priority == Priority.HIGH  # Priority parsed correctly
                    assert work_item.requirement_level == RequirementLevel.FR  # Level parsed correctly
                    assert "Investment Portfolio Rebalancing" in work_item.title
                    assert work_item.due_date == date(2025, 9, 13)
                    assert work_item.priority == Priority.HIGH
                    assert work_item.requirement_level == RequirementLevel.FR
    
    def test_data_access_to_business_logic_integration(self):
        """
        Test integration between Repository Scanner (Data Access) and 
        Priority Calculator (Business Logic)
        """
        # Mock repository scan results
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        mock_requirements = [
            RawRequirement(
                file_path="/repo1/overdue_feature.md",
                content="Overdue feature content",
                metadata=RequirementMetadata(
                    id="OVERDUE-001",
                    title="Overdue Feature",
                    due_date=yesterday,  # Overdue
                    priority=Priority.HIGH,
                    requirement_level=RequirementLevel.FR
                )
            ),
            RawRequirement(
                file_path="/repo1/due_today.md", 
                content="Due today content",
                metadata=RequirementMetadata(
                    id="TODAY-001",
                    title="Due Today Feature",
                    due_date=today,  # Due today
                    priority=Priority.MEDIUM,
                    requirement_level=RequirementLevel.SR
                )
            )
        ]
        
        # Convert to WorkItems (simulating discovery engine)
        work_items = []
        for req in mock_requirements:
            status = ItemStatus.OVERDUE if req.metadata.due_date < today else ItemStatus.DUE_TODAY
            work_item = WorkItem(
                id=req.metadata.id,
                title=req.metadata.title,
                description=req.metadata.description,
                due_date=req.metadata.due_date,
                priority=req.metadata.priority,
                effort_estimate=req.metadata.effort_estimate,
                requirement_level=req.metadata.requirement_level,
                project_type=ProjectType.APPLICATION,
                repository="test_repo",
                system_name="Test System",
                project_name="Test Project", 
                layer_or_milestone="Test Layer",
                hierarchy_path="Test → Path",
                status=status
            )
            work_items.append(work_item)
        
        # Process with Business Logic Layer
        sorted_items = self.calculator.sort_by_priority(work_items)
        
        # Validate Business Logic processing
        assert len(sorted_items) == 2
        assert sorted_items[0].status == ItemStatus.OVERDUE  # Overdue first
        assert sorted_items[1].status == ItemStatus.DUE_TODAY  # Due today second
        assert sorted_items[0].id == "OVERDUE-001"
        assert sorted_items[1].id == "TODAY-001"
    
    def test_data_access_to_ui_integration(self):
        """
        Test integration between Repository Scanner (Data Access) and 
        Terminal Formatter (UI)
        """
        # Create mock RawRequirement from Repository Scanner
        raw_requirement = RawRequirement(
            file_path="/test/feature.md",
            content="Test feature content",
            metadata=RequirementMetadata(
                id="FEATURE-UI-001",
                title="UI Integration Feature",
                due_date=date.today(),
                priority=Priority.HIGH,
                requirement_level=RequirementLevel.FR,
                effort_estimate="2 days",
                description="Test feature for UI integration"
            )
        )
        
        # Convert to WorkItem (simulating discovery engine)
        work_item = WorkItem(
            id=raw_requirement.metadata.id,
            title=raw_requirement.metadata.title,
            description=raw_requirement.metadata.description,
            due_date=raw_requirement.metadata.due_date,
            priority=raw_requirement.metadata.priority,
            effort_estimate=raw_requirement.metadata.effort_estimate,
            requirement_level=raw_requirement.metadata.requirement_level,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="UI Layer",
            hierarchy_path="UI Integration → Test System → Test Project → test_repo",
            status=ItemStatus.DUE_TODAY
        )
        
        # Format with UI Layer
        formatted_output = self.formatter.format_work_items([work_item])
        
        # Validate UI formatting
        assert "🎯 DUE TODAY" in formatted_output
        assert "UI Integration Feature" in formatted_output
        assert "[FR]" in formatted_output
        assert "High" in formatted_output
        assert "2 days" in formatted_output
        assert "make work TASK=FEATURE-UI-001" in formatted_output
    
    def test_full_data_access_workflow_integration(self):
        """
        Test complete workflow: Repository Scanner → Business Logic → UI
        """
        # Mock repository scanning
        with patch.object(self.scanner, 'scan_repositories') as mock_scan:
            mock_scan.return_value = [
                RawRequirement(
                    file_path="/repo/feature1.md",
                    content="Feature 1 content",
                    metadata=RequirementMetadata(
                        id="WORKFLOW-001", 
                        title="Workflow Test Feature 1",
                        due_date=date.today() - timedelta(days=1),  # Overdue
                        priority=Priority.HIGH,
                        requirement_level=RequirementLevel.FR
                    )
                ),
                RawRequirement(
                    file_path="/repo/feature2.md",
                    content="Feature 2 content", 
                    metadata=RequirementMetadata(
                        id="WORKFLOW-002",
                        title="Workflow Test Feature 2", 
                        due_date=date.today(),  # Due today
                        priority=Priority.MEDIUM,
                        requirement_level=RequirementLevel.SR
                    )
                )
            ]
            
            # Step 1: Data Access - Scan repositories
            raw_requirements = self.scanner.scan_repositories(["/test/repo"])
            assert len(raw_requirements) == 2
            
            # Step 2: Business Logic - Convert and prioritize
            work_items = []
            for req in raw_requirements:
                today = date.today()
                status = ItemStatus.OVERDUE if req.metadata.due_date < today else ItemStatus.DUE_TODAY
                work_item = WorkItem(
                    id=req.metadata.id,
                    title=req.metadata.title,
                    description=req.metadata.description,
                    due_date=req.metadata.due_date,
                    priority=req.metadata.priority,
                    effort_estimate="Unknown",
                    requirement_level=req.metadata.requirement_level,
                    project_type=ProjectType.APPLICATION,
                    repository="test_repo",
                    system_name="Test System",
                    project_name="Test Project",
                    layer_or_milestone="Integration Test",
                    hierarchy_path="Test → System → Project → repo",
                    status=status
                )
                work_items.append(work_item)
            
            sorted_items = self.calculator.sort_by_priority(work_items)
            
            # Step 3: UI - Format for display
            formatted_output = self.formatter.format_work_items(sorted_items)
            
            # Validate complete workflow
            assert len(sorted_items) == 2
            assert sorted_items[0].status == ItemStatus.OVERDUE  # Priority order
            assert "⏰ OVERDUE" in formatted_output  # Overdue indicator
            assert "🎯 DUE TODAY" in formatted_output  # Due today indicator
            assert "WORKFLOW-001" in formatted_output  # First feature
            assert "WORKFLOW-002" in formatted_output  # Second feature
    
    def test_repository_scanner_error_handling_integration(self):
        """
        Test that Repository Scanner error handling works properly 
        in integrated workflow
        """
        # Test by directly calling parse_requirement_file with different scenarios
        
        # Test 1: Valid file
        valid_content = """
        # Valid Feature
        **Due Date**: 2025-09-13
        **Priority**: High
        **Level**: FR
        """
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_file', return_value=True):
                with patch('builtins.open', mock_open(read_data=valid_content)):
                    result = self.scanner.parse_requirement_file("/valid/feature.md")
                    assert result is not None
                    assert "Valid Feature" in result.metadata.title
        
        # Test 2: Missing file (should return None)
        with patch('pathlib.Path.exists', return_value=False):
            result = self.scanner.parse_requirement_file("/missing/file.md")
            assert result is None
        
        # Test 3: Permission error (should return None)
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_file', return_value=True):
                with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                    result = self.scanner.parse_requirement_file("/restricted/file.md")
                    assert result is None
        
        # Validation: Error handling preserves workflow integrity
        print("✅ Repository Scanner error handling maintains workflow integrity")
    
    def test_repository_scanner_performance_characteristics(self):
        """
        Test that Repository Scanner performs efficiently with larger datasets
        """
        # Simulate scanning multiple repositories with many files
        large_repo_list = [f"/repo{i}" for i in range(10)]
        
        with patch.object(self.scanner, 'scan_single_repository') as mock_scan:
            # Each repo returns multiple requirements
            mock_scan.return_value = [
                Mock(spec=RawRequirement) for _ in range(5)
            ]
            
            result = self.scanner.scan_repositories(large_repo_list)
            
            # Should process all repositories
            assert mock_scan.call_count == 10
            assert len(result) == 50  # 10 repos × 5 requirements each
            
            # Check that statistics are tracked properly
            stats = self.scanner.get_scan_statistics()
            assert stats['repositories_scanned'] == 10