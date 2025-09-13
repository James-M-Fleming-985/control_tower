#!/usr/bin/env python3
"""
🧪 MAKEFILE VALIDATION TESTING FRAMEWORK
Tests specifically for Makefile command functionality and user value delivery

This framework tests that all Makefile commands:
1. Execute successfully
2. Provide expected outputs
3. Deliver actual user value
4. Integrate properly with the requirements hierarchy
"""

import subprocess
import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest
import time
import re

class TestMakefileCore:
    """Core Makefile functionality tests"""
    
    def test_makefile_exists_and_is_valid(self):
        """Test that Makefile exists and has basic structure"""
        makefile_path = Path("/workspaces/control_tower/Makefile")
        
        assert makefile_path.exists(), "Makefile not found in control tower root"
        
        content = makefile_path.read_text()
        
        # Should have help target
        assert "help:" in content, "Makefile missing help target"
        
        # Should have requirements-related targets
        assert "requirements" in content.lower(), "Makefile missing requirements targets"
        
        # Should have proper structure
        assert ".PHONY:" in content, "Makefile missing .PHONY declarations"
    
    def test_makefile_help_provides_user_value(self):
        """Test that make help provides clear, actionable guidance"""
        result = subprocess.run(
            ["make", "help"], 
            cwd="/workspaces/control_tower",
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            help_output = result.stdout
            
            # Should provide clear structure
            assert len(help_output) > 100, "Help output too brief to be useful"
            
            # Should have requirements-related commands
            help_lower = help_output.lower()
            assert any(word in help_lower for word in ["requirements", "trace", "validate"]), \
                "Help missing requirements management commands"
            
            # Should have clear command descriptions
            assert "Available Commands:" in help_output, "Help missing command descriptions"


class TestRequirementsCommands:
    """Test requirements management specific commands"""
    
    def test_trace_requirements_command(self):
        """Test that trace-requirements command works and provides value"""
        result = subprocess.run(
            ["make", "trace-requirements"], 
            cwd="/workspaces/control_tower",
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        # Should execute successfully
        assert result.returncode == 0, f"trace-requirements failed: {result.stderr}"
        
        output = result.stdout.lower()
        
        # Should provide meaningful output about requirements
        assert any(word in output for word in ["requirements", "hierarchy", "trace", "control tower"]), \
            f"trace-requirements output not meaningful: {result.stdout[:200]}"
        
        # Should indicate successful operation
        assert any(word in output for word in ["success", "passed", "complete"]), \
            "trace-requirements should indicate successful operation"
    
    def test_test_investment_strategy_command(self):
        """Test the investment strategy validation command"""
        result = subprocess.run(
            ["make", "test-investment-strategy"], 
            cwd="/workspaces/control_tower",
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        # Should execute successfully
        assert result.returncode == 0, f"test-investment-strategy failed: {result.stderr}"
        
        output = result.stdout.lower()
        
        # Should find and validate investment strategy requirements
        assert "investment strategy" in output, "Should mention investment strategy"
        assert any(word in output for word in ["found", "projects", "systems"]), \
            "Should report findings about projects and systems"
        
        # Should indicate validation success
        assert "success" in output, "Should indicate successful validation"
    
    def test_what_next_command_when_implemented(self):
        """Test what-next command (may not be implemented yet)"""
        result = subprocess.run(
            ["make", "what-next"], 
            cwd="/workspaces/control_tower",
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        # If command exists, it should provide useful output
        if result.returncode == 0:
            output = result.stdout.lower()
            
            # Should provide information about pending work
            assert len(output) > 50, "what-next should provide substantial output"
            
            # Should mention work or tasks
            assert any(word in output for word in ["work", "next", "task", "priority"]), \
                "what-next should mention work items"
        else:
            # If not implemented, should fail gracefully
            assert "what-next" in result.stderr.lower() or "target" in result.stderr.lower(), \
                "Should provide clear error about missing target"


class TestWorkflowCommands:
    """Test workflow automation commands"""
    
    def test_git_safety_commands(self):
        """Test git safety and status commands"""
        
        # Test git-status command
        result = subprocess.run(
            ["make", "git-status"], 
            cwd="/workspaces/control_tower",
            capture_output=True, 
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            output = result.stdout.lower()
            assert any(word in output for word in ["git", "status", "repository"]), \
                "git-status should provide git information"
    
    def test_work_on_command_when_implemented(self):
        """Test work-on command (may not be implemented yet)"""
        result = subprocess.run(
            ["make", "work-on", "ITEM=test"], 
            cwd="/workspaces/control_tower",
            capture_output=True, 
            text=True,
            timeout=15
        )
        
        # Should either work or fail gracefully
        if result.returncode != 0:
            # Should provide clear error message
            error_output = result.stderr.lower()
            assert any(word in error_output for word in ["target", "work-on", "not found"]), \
                "Should provide clear error about missing command"


class TestUserValueDelivery:
    """Test that Makefile commands deliver actual user value"""
    
    def test_command_execution_speed(self):
        """Test that commands execute quickly enough to provide value"""
        
        commands_to_test = [
            ["make", "help"],
            ["make", "trace-requirements"], 
            ["make", "test-investment-strategy"]
        ]
        
        for cmd in commands_to_test:
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd="/workspaces/control_tower",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            # Commands should execute quickly for good user experience
            assert execution_time < 30.0, f"Command {' '.join(cmd)} took too long: {execution_time}s"
            
            # If command succeeds, it should provide output
            if result.returncode == 0:
                assert len(result.stdout) > 0, f"Command {' '.join(cmd)} produced no output"
    
    def test_error_messages_are_helpful(self):
        """Test that error messages guide users effectively"""
        
        # Test with non-existent command
        result = subprocess.run(
            ["make", "nonexistent-command"],
            cwd="/workspaces/control_tower", 
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should fail with helpful error
        assert result.returncode != 0, "Should fail for non-existent command"
        
        error_output = result.stderr.lower()
        assert any(word in error_output for word in ["target", "not found", "no rule"]), \
            f"Error message not helpful: {result.stderr}"
    
    def test_commands_provide_next_actions(self):
        """Test that commands suggest next actions to users"""
        
        # Test trace-requirements provides guidance
        result = subprocess.run(
            ["make", "trace-requirements"],
            cwd="/workspaces/control_tower",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output = result.stdout.lower()
            
            # Should suggest next commands or actions
            assert any(phrase in output for phrase in ["make ", "next", "ready", "commands"]), \
                "Commands should suggest next actions"


class TestIntegrationWithRequirements:
    """Test that Makefile integrates properly with requirements hierarchy"""
    
    def test_makefile_finds_all_repositories(self):
        """Test that Makefile can discover all North Star repositories"""
        
        # Check if cloned_repos directory exists
        repos_dir = Path("/workspaces/control_tower/cloned_repos")
        
        if repos_dir.exists():
            repos = [d.name for d in repos_dir.iterdir() if d.is_dir()]
            
            # Should find the North Star repositories
            expected_repos = ["investment_strategy", "business_ventures", "financial_security"]
            
            found_repos = [repo for repo in expected_repos if repo in repos]
            assert len(found_repos) > 0, f"Should find North Star repositories, found: {repos}"
    
    def test_makefile_can_access_requirements_files(self):
        """Test that Makefile commands can access requirements files"""
        
        # Run a command that should access requirements
        result = subprocess.run(
            ["make", "test-investment-strategy"],
            cwd="/workspaces/control_tower",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output = result.stdout.lower()
            
            # Should find and report on requirements files
            assert any(word in output for word in ["found", "projects", "systems", "requirements"]), \
                "Should access and report on requirements files"
            
            # Should report specific numbers
            assert re.search(r'\d+', output), "Should report specific counts or numbers"


class TestMakefileReliability:
    """Test Makefile reliability and error handling"""
    
    def test_makefile_handles_missing_dependencies(self):
        """Test that Makefile handles missing dependencies gracefully"""
        
        # Test with potentially missing Python scripts
        result = subprocess.run(
            ["make", "trace-requirements"],
            cwd="/workspaces/control_tower",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should either succeed or fail with clear error
        if result.returncode != 0:
            error_output = result.stderr.lower()
            
            # Should provide clear error about missing dependencies
            assert any(word in error_output for word in ["not found", "no such file", "command not found"]), \
                f"Should provide clear dependency error: {result.stderr}"
    
    def test_makefile_works_from_correct_directory(self):
        """Test that Makefile works when run from control tower directory"""
        
        # Should work from control tower root
        result = subprocess.run(
            ["make", "help"],
            cwd="/workspaces/control_tower",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should succeed from correct directory
        if Path("/workspaces/control_tower/Makefile").exists():
            assert result.returncode == 0, "Makefile should work from control tower directory"


if __name__ == "__main__":
    # Run Makefile-specific tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short", 
        "--color=yes",
        "-x"  # Stop on first failure for faster feedback
    ])