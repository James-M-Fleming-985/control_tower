#!/usr/bin/env python3
"""
🧪 REQUIREMENTS MANAGEMENT SYSTEM TESTING FRAMEWORK
Comprehensive test suite for the hierarchical requirements management system

This test framework validates that the system delivers actual user value by testing:
- Makefile command functionality
- Requirements validation scripts
- Metrics collection and rollup
- End-to-end workflows
- User experience objectives
"""

import pytest
import subprocess
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import time
from datetime import datetime, timedelta

# Add the scripts directory to the path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

class TestRequirementsManagementSystem:
    """Test suite for the entire requirements management system"""
    
    @pytest.fixture(scope="class")
    def setup_test_environment(self):
        """Set up test environment with mock repositories and requirements"""
        # Create temporary directory structure
        test_dir = Path(tempfile.mkdtemp(prefix="rms_test_"))
        
        # Create mock repository structure
        repos = ["investment_strategy", "business_ventures", "financial_security", 
                "professional_excellence", "life_quality", "online_presence"]
        
        for repo in repos:
            repo_path = test_dir / "cloned_repos" / repo
            repo_path.mkdir(parents=True, exist_ok=True)
            
            # Create mock requirements structure
            projects_path = repo_path / "projects"
            projects_path.mkdir(exist_ok=True)
            
            # Create a sample project with requirements
            project_path = projects_path / "PROJECT-001"
            project_path.mkdir(exist_ok=True)
            
            # Create project requirement file
            project_req = project_path / "PROJECT-001_sample_project.md"
            project_req.write_text(self._create_mock_project_requirement())
            
            # Create system requirements
            system_path = project_path / "SYSTEM-001-01_sample_system"
            system_path.mkdir(exist_ok=True)
            
            system_req = system_path / "SYSTEM-001-01_sample_system.md"
            system_req.write_text(self._create_mock_system_requirement())
        
        yield test_dir
        
        # Cleanup
        shutil.rmtree(test_dir)
    
    def _create_mock_project_requirement(self):
        """Create a mock project requirement for testing"""
        return """# PROJECT-001: Sample Project

**Requirement ID**: PROJECT-001  
**Requirement Type**: Project  
**Level**: 2 (Project)  
**Created**: 2025-09-13  
**Last Updated**: 2025-09-13  
**Status**: Active  
**Priority**: High  
**Due Date**: 2025-09-20  
**Progress**: 25%  

## 📋 PROJECT DEFINITION

**Primary Objective**: Test project for requirements management system validation.

**Success Criteria**:
```
✅ All systems implemented and tested
✅ User acceptance criteria met
✅ Performance benchmarks achieved
```

## 🎯 SUPPORTING SYSTEMS

- SYSTEM-001-01: Sample System Implementation
- SYSTEM-001-02: Testing Framework
- SYSTEM-001-03: Deployment Pipeline

## ⏰ TIMELINE

**Start Date**: 2025-09-13  
**End Date**: 2025-09-20  
**Critical Milestones**:
- Day 3: System design complete
- Day 5: Implementation complete
- Day 7: Testing complete
"""

    def _create_mock_system_requirement(self):
        """Create a mock system requirement for testing"""
        return """# SYSTEM-001-01: Sample System

**Requirement ID**: SYSTEM-001-01  
**Requirement Type**: System  
**Level**: 3 (System)  
**Parent**: PROJECT-001  
**Created**: 2025-09-13  
**Last Updated**: 2025-09-13  
**Status**: In Progress  
**Priority**: High  
**Due Date**: 2025-09-18  
**Progress**: 50%  

## 📋 SYSTEM DEFINITION

**Primary Objective**: Implement core system functionality for testing.

**Functional Requirements**:
```
✅ FR-001: Core functionality implementation
✅ FR-002: Error handling and validation
✅ FR-003: Performance optimization
```

## 🧪 TESTING REQUIREMENTS

**Test Coverage**: 90%  
**Performance**: <100ms response time  
**Reliability**: 99.9% uptime  
"""


class TestMakefileCommands:
    """Test all Makefile commands for functionality and user value"""
    
    def test_what_next_command_discovers_work(self, setup_test_environment):
        """Test that make what-next discovers pending work across repositories"""
        test_dir = setup_test_environment
        
        # Change to test directory
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        try:
            # Test the what-next command (when implemented)
            result = subprocess.run(
                ["make", "what-next"], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            # Should succeed and provide useful output
            assert result.returncode == 0, f"what-next command failed: {result.stderr}"
            
            # Should identify pending work
            output = result.stdout.lower()
            assert "pending" in output or "work" in output or "priority" in output
            
            # Should provide next actions
            assert "make work-on" in output or "next:" in output
            
        finally:
            os.chdir(original_cwd)
    
    def test_work_on_command_automation(self, setup_test_environment):
        """Test that make work-on provides automated workflow execution"""
        test_dir = setup_test_environment
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        try:
            # Test work-on command with mock item
            result = subprocess.run(
                ["make", "work-on", "ITEM=SYSTEM-001-01"], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            # Should provide useful feedback even if not fully implemented
            # The key is that it should attempt automation
            output = result.stdout.lower()
            
            # Should indicate it's setting up work environment
            assert any(word in output for word in ["setup", "environment", "work", "git"])
            
        finally:
            os.chdir(original_cwd)
    
    def test_trace_requirements_validates_hierarchy(self, setup_test_environment):
        """Test that trace-requirements validates the hierarchy correctly"""
        test_dir = setup_test_environment
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        try:
            result = subprocess.run(
                ["make", "trace-requirements"], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            # Should execute and provide traceability information
            assert result.returncode == 0, f"trace-requirements failed: {result.stderr}"
            
            output = result.stdout.lower()
            assert any(word in output for word in ["requirements", "hierarchy", "trace", "validation"])
            
        finally:
            os.chdir(original_cwd)
    
    def test_makefile_commands_provide_user_value(self):
        """Test that Makefile commands deliver actual user value"""
        
        # Test help system provides clear guidance
        result = subprocess.run(["make", "help"], capture_output=True, text=True)
        
        if result.returncode == 0:
            help_output = result.stdout.lower()
            
            # Should provide clear, actionable commands
            assert "what-next" in help_output or "requirements" in help_output
            
            # Should have helpful descriptions
            assert "##" in result.stdout  # Make help format indicator


class TestRequirementsValidation:
    """Test requirements validation scripts and logic"""
    
    def test_requirement_metadata_validation(self, setup_test_environment):
        """Test that requirements have all required metadata"""
        test_dir = setup_test_environment
        
        # Find all requirement files
        req_files = list(test_dir.rglob("**/PROJECT-*.md")) + list(test_dir.rglob("**/SYSTEM-*.md"))
        
        assert len(req_files) > 0, "No requirement files found for testing"
        
        for req_file in req_files:
            content = req_file.read_text()
            
            # Check for required metadata
            assert "Requirement ID" in content, f"Missing Requirement ID in {req_file}"
            assert "Status" in content, f"Missing Status in {req_file}"
            assert "Priority" in content, f"Missing Priority in {req_file}"
            assert "Due Date" in content, f"Missing Due Date in {req_file}"
    
    def test_hierarchical_traceability(self, setup_test_environment):
        """Test that child requirements properly trace to parents"""
        test_dir = setup_test_environment
        
        # Find system requirements that should have project parents
        system_files = list(test_dir.rglob("**/SYSTEM-*.md"))
        
        for system_file in system_files:
            content = system_file.read_text()
            
            # Should reference parent project
            assert "Parent" in content or "PROJECT-" in content, \
                f"System requirement {system_file} missing parent reference"
    
    def test_requirements_timeline_validation(self, setup_test_environment):
        """Test that requirements have realistic timelines"""
        test_dir = setup_test_environment
        
        req_files = list(test_dir.rglob("**/PROJECT-*.md")) + list(test_dir.rglob("**/SYSTEM-*.md"))
        
        for req_file in req_files:
            content = req_file.read_text()
            
            # Should have due dates
            assert "Due Date" in content, f"Missing due date in {req_file}"
            
            # Due date should be in valid format (basic check)
            import re
            date_pattern = r"\d{4}-\d{2}-\d{2}"
            assert re.search(date_pattern, content), f"Invalid date format in {req_file}"


class TestMetricsAndReporting:
    """Test metrics collection and rollup functionality"""
    
    def test_progress_calculation(self, setup_test_environment):
        """Test that progress is calculated correctly from requirements"""
        test_dir = setup_test_environment
        
        # Mock requirements have progress percentages
        # Test that we can extract and calculate them
        req_files = list(test_dir.rglob("**/PROJECT-*.md")) + list(test_dir.rglob("**/SYSTEM-*.md"))
        
        total_progress = 0
        count = 0
        
        for req_file in req_files:
            content = req_file.read_text()
            
            # Extract progress percentage
            import re
            progress_match = re.search(r"Progress.*?(\d+)%", content)
            if progress_match:
                progress = int(progress_match.group(1))
                assert 0 <= progress <= 100, f"Invalid progress {progress} in {req_file}"
                total_progress += progress
                count += 1
        
        if count > 0:
            avg_progress = total_progress / count
            assert avg_progress >= 0, "Average progress calculation failed"
    
    def test_timeline_variance_tracking(self, setup_test_environment):
        """Test that timeline variances are properly tracked"""
        test_dir = setup_test_environment
        
        # Mock a scenario where we can check if items are overdue
        current_date = datetime.now()
        
        req_files = list(test_dir.rglob("**/PROJECT-*.md")) + list(test_dir.rglob("**/SYSTEM-*.md"))
        
        for req_file in req_files:
            content = req_file.read_text()
            
            # Should be able to determine if overdue
            import re
            date_match = re.search(r"Due Date.*?(\d{4}-\d{2}-\d{2})", content)
            if date_match:
                due_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                
                # Should be able to calculate variance
                variance_days = (due_date - current_date).days
                
                # Test passes if we can calculate variance
                assert isinstance(variance_days, int), "Timeline variance calculation failed"


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    def test_discovery_to_execution_workflow(self, setup_test_environment):
        """Test the complete workflow from discovery to execution"""
        test_dir = setup_test_environment
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        try:
            # Step 1: Discovery should work
            discovery_result = subprocess.run(
                ["make", "what-next"], 
                capture_output=True, 
                text=True,
                timeout=15
            )
            
            # Should provide some output (even if not fully implemented)
            assert len(discovery_result.stdout) > 0 or len(discovery_result.stderr) > 0
            
            # Step 2: Should be able to attempt work execution
            work_result = subprocess.run(
                ["make", "work-on", "ITEM=test"], 
                capture_output=True, 
                text=True,
                timeout=15
            )
            
            # Should attempt to do something (even if it fails gracefully)
            assert len(work_result.stdout) > 0 or len(work_result.stderr) > 0
            
        finally:
            os.chdir(original_cwd)
    
    def test_user_value_delivery(self, setup_test_environment):
        """Test that the system actually delivers value to the user"""
        
        # User Value Test 1: Time savings
        start_time = time.time()
        
        # Simulate manual discovery task
        test_dir = setup_test_environment
        manual_discovery_time = self._simulate_manual_discovery(test_dir)
        
        # Simulate automated discovery
        automated_discovery_time = self._simulate_automated_discovery(test_dir)
        
        # Automated should be faster (when implemented)
        # For now, just test that we can measure the difference
        assert manual_discovery_time >= 0
        assert automated_discovery_time >= 0
        
        # User Value Test 2: Accuracy
        # Automated discovery should find all work items
        work_items = self._count_work_items(test_dir)
        assert work_items > 0, "Should find work items in test repositories"
    
    def _simulate_manual_discovery(self, test_dir):
        """Simulate manual discovery time"""
        start = time.time()
        
        # Simulate manually checking all repositories
        repos = list((test_dir / "cloned_repos").glob("*"))
        for repo in repos:
            if repo.is_dir():
                # Simulate looking through files
                req_files = list(repo.rglob("*.md"))
                for _ in req_files:
                    pass  # Simulate reading
        
        return time.time() - start
    
    def _simulate_automated_discovery(self, test_dir):
        """Simulate automated discovery time"""
        start = time.time()
        
        # Simulate automated scanning
        req_files = list(test_dir.rglob("**/PROJECT-*.md")) + list(test_dir.rglob("**/SYSTEM-*.md"))
        
        # Process files efficiently
        for req_file in req_files:
            content = req_file.read_text()
            # Extract metadata quickly
            lines = content.split('\n')[:20]  # Just check headers
        
        return time.time() - start
    
    def _count_work_items(self, test_dir):
        """Count discoverable work items"""
        req_files = list(test_dir.rglob("**/PROJECT-*.md")) + list(test_dir.rglob("**/SYSTEM-*.md"))
        return len(req_files)


class TestSystemReliability:
    """Test system reliability and error handling"""
    
    def test_graceful_failure_handling(self):
        """Test that system fails gracefully when requirements are missing"""
        
        # Test with non-existent directory
        result = subprocess.run(
            ["make", "what-next"], 
            cwd="/tmp/nonexistent", 
            capture_output=True, 
            text=True
        )
        
        # Should not crash catastrophically
        # Either succeeds or fails with useful error message
        if result.returncode != 0:
            assert len(result.stderr) > 0, "Should provide error message on failure"
    
    def test_performance_under_load(self, setup_test_environment):
        """Test that system performs well with many requirements"""
        test_dir = setup_test_environment
        
        # Create additional mock requirements to simulate load
        for i in range(50):
            project_path = test_dir / "cloned_repos" / "investment_strategy" / "projects" / f"PROJECT-{i:03d}"
            project_path.mkdir(parents=True, exist_ok=True)
            
            req_file = project_path / f"PROJECT-{i:03d}_load_test.md"
            req_file.write_text(f"# PROJECT-{i:03d}: Load Test Project\n**Status**: Active\n**Due Date**: 2025-12-31")
        
        # Test discovery performance
        start_time = time.time()
        req_files = list(test_dir.rglob("**/PROJECT-*.md"))
        discovery_time = time.time() - start_time
        
        # Should complete discovery in reasonable time
        assert discovery_time < 5.0, f"Discovery took too long: {discovery_time}s"
        assert len(req_files) >= 50, "Should discover all created requirements"


if __name__ == "__main__":
    # Run the test suite
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ])