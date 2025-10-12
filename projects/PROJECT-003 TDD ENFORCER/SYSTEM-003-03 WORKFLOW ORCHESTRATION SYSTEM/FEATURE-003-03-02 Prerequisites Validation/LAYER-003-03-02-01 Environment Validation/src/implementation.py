```python
import sys
import os
from typing import Dict, List, Optional, Set


class EnvironmentValidator:
    """Validates the execution environment for the workflow orchestration system."""
    
    def __init__(self, required_env_vars: Optional[List[str]] = None):
        """
        Initialize the environment validator.
        
        Args:
            required_env_vars: List of required environment variable names
        """
        self.required_env_vars = required_env_vars or []
        self._validation_errors: List[str] = []
    
    def validate_python_version(self, min_version: tuple = (3, 8)) -> bool:
        """
        Validate that Python version meets minimum requirements.
        
        Args:
            min_version: Minimum required Python version as tuple (major, minor)
            
        Returns:
            True if Python version is valid, False otherwise
        """
        current_version = sys.version_info[:2]
        if current_version < min_version:
            self._validation_errors.append(
                f"Python version {current_version[0]}.{current_version[1]} is below minimum required version {min_version[0]}.{min_version[1]}"
            )
            return False
        return True
    
    def detect_virtual_environment(self) -> bool:
        """
        Detect if code is running in a virtual environment.
        
        Returns:
            True if running in virtual environment, False otherwise
        """
        # Check multiple indicators for virtual environment
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get('VIRTUAL_ENV') is not None
        )
        
        if not in_venv:
            self._validation_errors.append(
                "Not running in a virtual environment"
            )
        
        return in_venv
    
    def validate_environment_variables(self, required_vars: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Validate that required environment variables are set.
        
        Args:
            required_vars: List of required environment variable names.
                          If None, uses self.required_env_vars
            
        Returns:
            Dictionary mapping variable names to their validation status
        """
        vars_to_check = required_vars if required_vars is not None else self.required_env_vars
        results = {}
        
        for var in vars_to_check:
            is_set = var in os.environ and os.environ[var] != ''
            results[var] = is_set
            
            if not is_set:
                self._validation_errors.append(
                    f"Required environment variable '{var}' is not set"
                )
        
        return results
    
    def validate_all(self, min_python_version: tuple = (3, 8)) -> bool:
        """
        Run all validations.
        
        Args:
            min_python_version: Minimum required Python version
            
        Returns:
            True if all validations pass, False otherwise
        """
        self._validation_errors = []
        
        python_valid = self.validate_python_version(min_python_version)
        venv_valid = self.detect_virtual_environment()
        env_vars_results = self.validate_environment_variables()
        env_vars_valid = all(env_vars_results.values()) if env_vars_results else True
        
        return python_valid and venv_valid and env_vars_valid
    
    def get_validation_errors(self) -> List[str]:
        """
        Get list of validation errors from last validation run.
        
        Returns:
            List of error messages
        """
        return self._validation_errors.copy()
    
    def get_validation_report(self) -> Dict[str, any]:
        """
        Get detailed validation report.
        
        Returns:
            Dictionary containing validation results and details
        """
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        in_venv = self.detect_virtual_environment()
        env_vars = self.validate_environment_variables()
        
        return {
            'python_version': python_version,
            'python_version_valid': self.validate_python_version(),
            'virtual_environment': in_venv,
            'environment_variables': env_vars,
            'all_valid': self.validate_all(),
            'errors': self.get_validation_errors()
        }


def validate_environment(
    required_env_vars: Optional[List[str]] = None,
    min_python_version: tuple = (3, 8)
) -> bool:
    """
    Convenience function to validate environment.
    
    Args:
        required_env_vars: List of required environment variable names
        min_python_version: Minimum required Python version
        
    Returns:
        True if environment is valid, False otherwise
    """
    validator = EnvironmentValidator(required_env_vars)
    return validator.validate_all(min_python_version)


def get_python_version() -> str:
    """
    Get current Python version string.
    
    Returns:
        Python version string (e.g., "3.8.10")
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def is_virtual_environment() -> bool:
    """
    Check if running in a virtual environment.
    
    Returns:
        True if in virtual environment, False otherwise
    """
    validator = EnvironmentValidator()
    return validator.detect_virtual_environment()


def check_environment_variables(variable_names: List[str]) -> Dict[str, bool]:
    """
    Check if environment variables are set.
    
    Args:
        variable_names: List of variable names to check
        
    Returns:
        Dictionary mapping variable names to whether they are set
    """
    validator = EnvironmentValidator()
    return validator.validate_environment_variables(variable_names)
```