```python
"""
Project Structure Validator

Validates that a project has the required directory structure and configuration files.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union


class ProjectStructureValidator:
    """Validates project structure including directories and configuration files."""

    def __init__(self, project_root: Union[str, Path]):
        """
        Initialize the validator with a project root directory.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.validation_results: Dict[str, bool] = {}
        self.missing_elements: List[str] = []

    def validate(self) -> bool:
        """
        Validate the complete project structure.

        Returns:
            bool: True if all validations pass, False otherwise
        """
        self.validation_results.clear()
        self.missing_elements.clear()

        # AC-001: Validate src/ and tests/ directories exist
        src_exists = self._validate_directory("src")
        tests_exists = self._validate_directory("tests")
        self.validation_results["directories"] = src_exists and tests_exists

        # AC-002: Check for requirements template files
        requirements_exists = self._validate_requirements_files()
        self.validation_results["requirements"] = requirements_exists

        # AC-003: Validate pyproject.toml or setup.py exists
        config_exists = self._validate_config_files()
        self.validation_results["config"] = config_exists

        return all(self.validation_results.values())

    def _validate_directory(self, directory_name: str) -> bool:
        """
        Validate that a directory exists in the project root.

        Args:
            directory_name: Name of the directory to validate

        Returns:
            bool: True if directory exists, False otherwise
        """
        dir_path = self.project_root / directory_name
        exists = dir_path.exists() and dir_path.is_dir()
        
        if not exists:
            self.missing_elements.append(f"{directory_name}/ directory")
        
        return exists

    def _validate_requirements_files(self) -> bool:
        """
        Validate that requirements files exist.

        Returns:
            bool: True if at least one requirements file exists
        """
        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements.in",
        ]
        
        found_files = []
        for req_file in requirements_files:
            file_path = self.project_root / req_file
            if file_path.exists() and file_path.is_file():
                found_files.append(req_file)
        
        if not found_files:
            self.missing_elements.append("requirements files (requirements.txt, requirements-dev.txt, or requirements.in)")
            return False
        
        return True

    def _validate_config_files(self) -> bool:
        """
        Validate that configuration files exist (pyproject.toml or setup.py).

        Returns:
            bool: True if at least one config file exists
        """
        config_files = ["pyproject.toml", "setup.py"]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists() and file_path.is_file():
                return True
        
        self.missing_elements.append("configuration file (pyproject.toml or setup.py)")
        return False

    def get_guidance(self) -> str:
        """
        Provide guidance for missing structure elements.

        Returns:
            str: Guidance message for fixing missing elements
        """
        if not self.missing_elements:
            return "Project structure is valid. No issues found."
        
        guidance_lines = [
            "Project structure validation failed. Please address the following issues:",
            ""
        ]
        
        for i, element in enumerate(self.missing_elements, 1):
            guidance_lines.append(f"{i}. Missing: {element}")
        
        guidance_lines.extend([
            "",
            "Recommended actions:",
        ])
        
        if any("src/" in elem or "tests/" in elem for elem in self.missing_elements):
            guidance_lines.append("- Create missing directories: mkdir -p src tests")
        
        if any("requirements" in elem for elem in self.missing_elements):
            guidance_lines.append("- Create requirements.txt with project dependencies")
            guidance_lines.append("- Optionally create requirements-dev.txt for development dependencies")
        
        if any("configuration file" in elem for elem in self.missing_elements):
            guidance_lines.append("- Create pyproject.toml for modern Python projects")
            guidance_lines.append("- Or create setup.py for traditional Python packaging")
        
        return "\n".join(guidance_lines)

    def get_validation_results(self) -> Dict[str, bool]:
        """
        Get the validation results.

        Returns:
            Dict[str, bool]: Dictionary of validation results by category
        """
        return self.validation_results.copy()

    def get_missing_elements(self) -> List[str]:
        """
        Get the list of missing elements.

        Returns:
            List[str]: List of missing structure elements
        """
        return self.missing_elements.copy()


def validate_project_structure(project_root: Union[str, Path]) -> Dict[str, any]:
    """
    Convenience function to validate project structure and return results.

    Args:
        project_root: Path to the project root directory

    Returns:
        Dict containing validation status, results, missing elements, and guidance
    """
    validator = ProjectStructureValidator(project_root)
    is_valid = validator.validate()
    
    return {
        "valid": is_valid,
        "results": validator.get_validation_results(),
        "missing_elements": validator.get_missing_elements(),
        "guidance": validator.get_guidance()
    }
```