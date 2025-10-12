```python
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil


class TestAC001ValidateSrcAndTestsDirectories:
    """Test class for AC-001: Validate src/ and tests/ directories exist"""
    
    def test_src_directory_exists(self):
        """Test that src/ directory exists in project root"""
        project_root = Path.cwd()
        src_dir = project_root / "src"
        assert src_dir.exists(), "src/ directory does not exist"
        assert src_dir.is_dir(), "src/ is not a directory"
    
    def test_tests_directory_exists(self):
        """Test that tests/ directory exists in project root"""
        project_root = Path.cwd()
        tests_dir = project_root / "tests"
        assert tests_dir.exists(), "tests/ directory does not exist"
        assert tests_dir.is_dir(), "tests/ is not a directory"
    
    def test_both_directories_exist_simultaneously(self):
        """Test that both src/ and tests/ directories exist at the same time"""
        project_root = Path.cwd()
        src_dir = project_root / "src"
        tests_dir = project_root / "tests"
        assert src_dir.exists() and tests_dir.exists(), "Both directories must exist"
    
    def test_directories_are_not_files(self):
        """Test that src/ and tests/ are directories, not files"""
        project_root = Path.cwd()
        src_dir = project_root / "src"
        tests_dir = project_root / "tests"
        if src_dir.exists():
            assert src_dir.is_dir(), "src/ exists but is not a directory"
        if tests_dir.exists():
            assert tests_dir.is_dir(), "tests/ exists but is not a directory"


class TestAC002CheckRequirementsTemplateFiles:
    """Test class for AC-002: Check for requirements template files"""
    
    def test_requirements_txt_exists(self):
        """Test that requirements.txt file exists"""
        project_root = Path.cwd()
        requirements_file = project_root / "requirements.txt"
        assert requirements_file.exists(), "requirements.txt does not exist"
        assert requirements_file.is_file(), "requirements.txt is not a file"
    
    def test_requirements_dev_txt_exists(self):
        """Test that requirements-dev.txt file exists"""
        project_root = Path.cwd()
        requirements_dev_file = project_root / "requirements-dev.txt"
        assert requirements_dev_file.exists(), "requirements-dev.txt does not exist"
        assert requirements_dev_file.is_file(), "requirements-dev.txt is not a file"
    
    def test_requirements_txt_is_readable(self):
        """Test that requirements.txt is readable"""
        project_root = Path.cwd()
        requirements_file = project_root / "requirements.txt"
        assert requirements_file.exists(), "requirements.txt does not exist"
        with open(requirements_file, 'r') as f:
            content = f.read()
        assert content is not None, "requirements.txt is not readable"
    
    def test_at_least_one_requirements_file_exists(self):
        """Test that at least one requirements file exists"""
        project_root = Path.cwd()
        requirements_files = [
            project_root / "requirements.txt",
            project_root / "requirements-dev.txt",
            project_root / "requirements" / "base.txt"
        ]
        exists = any(f.exists() for f in requirements_files)
        assert exists, "No requirements file found"


class TestAC003ValidatePyprojectOrSetupPy:
    """Test class for AC-003: Validate pyproject.toml or setup.py exists"""
    
    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml file exists"""
        project_root = Path.cwd()
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml does not exist"
        assert pyproject_file.is_file(), "pyproject.toml is not a file"
    
    def test_setup_py_exists(self):
        """Test that setup.py file exists"""
        project_root = Path.cwd()
        setup_file = project_root / "setup.py"
        assert setup_file.exists(), "setup.py does not exist"
        assert setup_file.is_file(), "setup.py is not a file"
    
    def test_at_least_one_config_file_exists(self):
        """Test that either pyproject.toml or setup.py exists"""
        project_root = Path.cwd()
        pyproject_file = project_root / "pyproject.toml"
        setup_file = project_root / "setup.py"
        assert pyproject_file.exists() or setup_file.exists(), \
            "Neither pyproject.toml nor setup.py exists"
    
    def test_pyproject_toml_is_valid_toml(self):
        """Test that pyproject.toml is valid TOML format"""
        import tomli
        project_root = Path.cwd()
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml does not exist"
        with open(pyproject_file, 'rb') as f:
            data = tomli.load(f)
        assert data is not None, "pyproject.toml is not valid TOML"


class TestAC004ProvideMissingStructureGuidance:
    """Test class for AC-004: Provide guidance for missing structure elements"""
    
    def test_guidance_function_exists(self):
        """Test that a guidance function exists for missing structure"""
        from project_validator import provide_missing_structure_guidance
        assert callable(provide_missing_structure_guidance), \
            "provide_missing_structure_guidance function does not exist"
    
    def test_guidance_for_missing_src_directory(self):
        """Test that guidance is provided when src/ directory is missing"""
        from project_validator import provide_missing_structure_guidance
        guidance = provide_missing_structure_guidance(missing_src=True)
        assert guidance is not None, "No guidance provided for missing src/"
        assert "src" in guidance.lower(), "Guidance does not mention src directory"
    
    def test_guidance_for_missing_tests_directory(self):
        """Test that guidance is provided when tests/ directory is missing"""
        from project_validator import provide_missing_structure_guidance
        guidance = provide_missing_structure_guidance(missing_tests=True)
        assert guidance is not None, "No guidance provided for missing tests/"
        assert "test" in guidance.lower(), "Guidance does not mention tests directory"
    
    def test_guidance_for_missing_config_files(self):
        """Test that guidance is provided when config files are missing"""
        from project_validator import provide_missing_structure_guidance
        guidance = provide_missing_structure_guidance(missing_config=True)
        assert guidance is not None, "No guidance provided for missing config"
        assert any(word in guidance.lower() for word in ["pyproject", "setup"]), \
            "Guidance does not mention config files"
    
    def test_guidance_returns_string_type(self):
        """Test that guidance function returns a string"""
        from project_validator import provide_missing_structure_guidance
        guidance = provide_missing_structure_guidance()
        assert isinstance(guidance, str), "Guidance is not a string"
    
    def test_comprehensive_guidance_for_all_missing_elements(self):
        """Test that comprehensive guidance is provided when all elements are missing"""
        from project_validator import provide_missing_structure_guidance
        guidance = provide_missing_structure_guidance(
            missing_src=True,
            missing_tests=True,
            missing_config=True,
            missing_requirements=True
        )
        assert len(guidance) > 50, "Guidance is too short for all missing elements"
        assert "src" in guidance.lower(), "Guidance missing src directory info"
        assert "test" in guidance.lower(), "Guidance missing tests directory info"
```