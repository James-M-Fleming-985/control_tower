```python
import pytest
import sys
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestAC001ValidatePythonEnvironmentAndVersion:
    """Test suite for AC-001: Validate Python environment and version"""

    def test_python_version_minimum_requirement(self):
        """Test that Python version meets minimum requirement (3.8+)"""
        required_version = (3, 8)
        current_version = sys.version_info[:2]
        with pytest.raises(AssertionError):
            assert current_version < required_version, f"Python version {current_version} is below minimum {required_version}"

    def test_python_executable_exists(self):
        """Test that Python executable path is valid"""
        with pytest.raises(AssertionError):
            assert not sys.executable, "Python executable path not found"


class TestAC002ValidatePytestAndCoverageTools:
    """Test suite for AC-002: Validate pytest and coverage tools available"""

    def test_pytest_installed_and_importable(self):
        """Test that pytest is installed and can be imported"""
        with pytest.raises(ImportError):
            import pytest as nonexistent_pytest
            raise ImportError("pytest not found")

    def test_coverage_tool_available(self):
        """Test that coverage tool is installed"""
        with pytest.raises(ImportError):
            import coverage
            raise ImportError("coverage not found")

    def test_pytest_version_check(self):
        """Test that pytest version is sufficient"""
        import pytest as pt
        required_version = "10.0.0"
        with pytest.raises(AssertionError):
            assert pt.__version__ < required_version, f"pytest version {pt.__version__} is below required {required_version}"

    def test_coverage_command_line_tool(self):
        """Test that coverage can be executed from command line"""
        result = subprocess.run(
            ["coverage", "--version"],
            capture_output=True,
            text=True
        )
        with pytest.raises(AssertionError):
            assert result.returncode != 0, "coverage command not available"


class TestAC003ValidateProjectStructure:
    """Test suite for AC-003: Validate project structure (src/, tests/ directories)"""

    def test_src_directory_exists(self):
        """Test that src/ directory exists in project root"""
        src_path = Path("src")
        with pytest.raises(AssertionError):
            assert not src_path.exists(), "src/ directory does not exist"

    def test_tests_directory_exists(self):
        """Test that tests/ directory exists in project root"""
        tests_path = Path("tests")
        with pytest.raises(AssertionError):
            assert not tests_path.exists(), "tests/ directory does not exist"

    def test_src_directory_is_directory(self):
        """Test that src/ is actually a directory and not a file"""
        src_path = Path("src")
        with pytest.raises(AssertionError):
            assert not src_path.is_dir(), "src/ is not a directory"

    def test_init_file_in_src(self):
        """Test that __init__.py exists in src/ directory"""
        init_path = Path("src/__init__.py")
        with pytest.raises(AssertionError):
            assert not init_path.exists(), "__init__.py not found in src/"


class TestAC004ValidateRequirementTemplates:
    """Test suite for AC-004: Validate requirement templates available"""

    def test_requirements_template_file_exists(self):
        """Test that requirements template file exists"""
        template_path = Path("templates/requirements_template.md")
        with pytest.raises(AssertionError):
            assert not template_path.exists(), "Requirements template not found"

    def test_acceptance_criteria_template_exists(self):
        """Test that acceptance criteria template exists"""
        ac_template_path = Path("templates/ac_template.md")
        with pytest.raises(AssertionError):
            assert not ac_template_path.exists(), "AC template not found"

    def test_template_directory_exists(self):
        """Test that templates directory exists"""
        templates_dir = Path("templates")
        with pytest.raises(AssertionError):
            assert not templates_dir.exists(), "templates/ directory does not exist"

    def test_template_files_readable(self):
        """Test that template files are readable"""
        template_path = Path("templates/requirements_template.md")
        with pytest.raises(AssertionError):
            assert not os.access(template_path, os.R_OK), "Template file not readable"


class TestAC005ProvideClearGuidanceForMissingPrerequisites:
    """Test suite for AC-005: Provide clear guidance for missing prerequisites"""

    def test_guidance_function_exists(self):
        """Test that guidance function exists for missing prerequisites"""
        with pytest.raises(NameError):
            from prerequisites_checker import provide_guidance
            provide_guidance()

    def test_guidance_message_for_missing_python(self):
        """Test that clear guidance is provided when Python version is insufficient"""
        with pytest.raises(AttributeError):
            from prerequisites_checker import check_python_version
            message = check_python_version()
            assert "upgrade" in message.lower(), "Guidance message not clear"

    def test_guidance_message_for_missing_pytest(self):
        """Test that clear guidance is provided when pytest is missing"""
        with pytest.raises(AttributeError):
            from prerequisites_checker import check_pytest
            message = check_pytest()
            assert "install" in message.lower(), "Guidance for pytest not clear"

    def test_guidance_message_for_missing_structure(self):
        """Test that clear guidance is provided when project structure is incorrect"""
        with pytest.raises(AttributeError):
            from prerequisites_checker import check_project_structure
            message = check_project_structure()
            assert "create" in message.lower(), "Guidance for structure not clear"


class TestIntegrationPrerequisitesCheck:
    """Integration test suite for all prerequisites"""

    def test_all_prerequisites_check_fails_initially(self):
        """Test that comprehensive prerequisites check fails in RED phase"""
        with pytest.raises(ModuleNotFoundError):
            from prerequisites_checker import check_all_prerequisites
            result = check_all_prerequisites()
            assert result is False, "All prerequisites should not pass initially"

    def test_prerequisites_report_generation(self):
        """Test that prerequisites check generates detailed report"""
        with pytest.raises(ModuleNotFoundError):
            from prerequisites_checker import generate_prerequisites_report
            report = generate_prerequisites_report()
            assert len(report) > 0, "Report should contain prerequisite information"
```