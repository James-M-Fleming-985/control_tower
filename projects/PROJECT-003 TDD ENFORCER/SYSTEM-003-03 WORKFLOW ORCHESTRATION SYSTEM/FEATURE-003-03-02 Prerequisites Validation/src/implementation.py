```python
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PrerequisitesValidator:
    """Validates system prerequisites for the TDD Enforcer workflow."""
    
    def __init__(self):
        self.validation_results: Dict[str, Dict] = {}
        self.python_min_version = (3, 7)
    
    def validate_all(self) -> Dict[str, Dict]:
        """
        Run all prerequisite validations.
        
        Returns:
            Dict containing validation results for all checks
        """
        self.validate_python_environment()
        self.validate_tools()
        self.validate_project_structure()
        self.validate_requirement_templates()
        return self.validation_results
    
    def validate_python_environment(self) -> Dict:
        """
        Validate Python environment and version.
        
        Returns:
            Dict with validation result
        """
        result = {
            'valid': False,
            'version': None,
            'message': '',
            'guidance': []
        }
        
        try:
            version = sys.version_info
            result['version'] = f"{version.major}.{version.minor}.{version.micro}"
            
            if (version.major, version.minor) >= self.python_min_version:
                result['valid'] = True
                result['message'] = f"Python {result['version']} is valid"
            else:
                result['message'] = f"Python version {result['version']} is below minimum {self.python_min_version[0]}.{self.python_min_version[1]}"
                result['guidance'] = [
                    f"Current Python version: {result['version']}",
                    f"Minimum required version: {self.python_min_version[0]}.{self.python_min_version[1]}",
                    "Please upgrade Python to a supported version",
                    "Visit https://www.python.org/downloads/ for installation"
                ]
        except Exception as e:
            result['message'] = f"Failed to check Python version: {str(e)}"
            result['guidance'] = ["Unable to detect Python installation"]
        
        self.validation_results['python_environment'] = result
        return result
    
    def validate_tools(self) -> Dict:
        """
        Validate pytest and coverage tools availability.
        
        Returns:
            Dict with validation result
        """
        result = {
            'valid': False,
            'tools': {},
            'message': '',
            'guidance': []
        }
        
        tools_to_check = {
            'pytest': 'pytest',
            'coverage': 'coverage'
        }
        
        missing_tools = []
        
        for tool_name, import_name in tools_to_check.items():
            try:
                __import__(import_name)
                result['tools'][tool_name] = True
            except ImportError:
                result['tools'][tool_name] = False
                missing_tools.append(tool_name)
        
        if not missing_tools:
            result['valid'] = True
            result['message'] = "All required tools are available"
        else:
            result['message'] = f"Missing tools: {', '.join(missing_tools)}"
            result['guidance'] = [
                f"Missing required tools: {', '.join(missing_tools)}",
                f"Install using: pip install {' '.join(missing_tools)}",
                "Or install all dev requirements: pip install -r requirements-dev.txt"
            ]
        
        self.validation_results['tools'] = result
        return result
    
    def validate_project_structure(self) -> Dict:
        """
        Validate project structure (src/, tests/ directories).
        
        Returns:
            Dict with validation result
        """
        result = {
            'valid': False,
            'directories': {},
            'message': '',
            'guidance': []
        }
        
        required_dirs = ['src', 'tests']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            exists = dir_path.exists() and dir_path.is_dir()
            result['directories'][dir_name] = exists
            if not exists:
                missing_dirs.append(dir_name)
        
        if not missing_dirs:
            result['valid'] = True
            result['message'] = "Project structure is valid"
        else:
            result['message'] = f"Missing directories: {', '.join(missing_dirs)}"
            result['guidance'] = [
                f"Missing required directories: {', '.join(missing_dirs)}",
                "Create the following structure:",
                "  project_root/",
                "    ├── src/",
                "    └── tests/",
                f"Run: mkdir -p {' '.join(missing_dirs)}"
            ]
        
        self.validation_results['project_structure'] = result
        return result
    
    def validate_requirement_templates(self) -> Dict:
        """
        Validate requirement templates availability.
        
        Returns:
            Dict with validation result
        """
        result = {
            'valid': False,
            'templates': {},
            'message': '',
            'guidance': []
        }
        
        template_locations = [
            'templates/requirements',
            'requirements/templates',
            '.templates/requirements',
            'templates'
        ]
        
        found_templates = []
        
        for location in template_locations:
            template_path = Path(location)
            if template_path.exists():
                found_templates.append(str(template_path))
                result['templates'][str(template_path)] = True
        
        if found_templates:
            result['valid'] = True
            result['message'] = f"Requirement templates found at: {', '.join(found_templates)}"
        else:
            result['message'] = "No requirement templates found"
            result['guidance'] = [
                "No requirement template directories found",
                "Expected locations:",
                "  - templates/requirements/",
                "  - requirements/templates/",
                "  - .templates/requirements/",
                "  - templates/",
                "Create a templates directory and add requirement templates",
                "Example: mkdir -p templates/requirements"
            ]
        
        self.validation_results['requirement_templates'] = result
        return result
    
    def get_validation_summary(self) -> Dict:
        """
        Get summary of all validations.
        
        Returns:
            Dict with overall validation status
        """
        if not self.validation_results:
            self.validate_all()
        
        all_valid = all(
            result.get('valid', False) 
            for result in self.validation_results.values()
        )
        
        return {
            'all_valid': all_valid,
            'results': self.validation_results,
            'total_checks': len(self.validation_results),
            'passed_checks': sum(
                1 for r in self.validation_results.values() if r.get('valid', False)
            )
        }
    
    def get_guidance(self) -> List[str]:
        """
        Get guidance for fixing all validation failures.
        
        Returns:
            List of guidance messages
        """
        if not self.validation_results:
            self.validate_all()
        
        all_guidance = []
        
        for check_name, result in self.validation_results.items():
            if not result.get('valid', False) and result.get('guidance'):
                all_guidance.append(f"\n{check_name.upper().replace('_', ' ')}:")
                all_guidance.extend(f"  - {g}" for g in result['guidance'])
        
        return all_guidance


def validate_prerequisites() -> PrerequisitesValidator:
    """
    Convenience function to create and run validator.
    
    Returns:
        PrerequisitesValidator instance with results
    """
    validator = PrerequisitesValidator()
    validator.validate_all()
    return validator
```