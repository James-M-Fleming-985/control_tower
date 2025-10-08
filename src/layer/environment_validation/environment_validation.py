"""Environment Validation Layer.

Layer: LAYER-003-03-02-01
Validates Python runtime environment meets TDD workflow requirements.
"""

import os
import sys
from typing import Dict, Tuple
from datetime import datetime


class EnvironmentValidation:
    """Validates Python environment for TDD workflows.
    
    Acceptance Criteria:
    - AC-001: Validate Python version >= 3.8
    - AC-002: Detect virtual environment activation
    - AC-003: Validate required environment variables
    """

    def __init__(self):
        """Initialize the environment validator."""
        self.python_version = sys.version_info
        self.validation_results: Dict[str, bool] = {}
        self.required_env_vars = ['HOME', 'USER']

    def validate_python_version_3_8(self) -> bool:
        """AC-001: Validate Python version >= 3.8.
        
        Returns:
            bool: True if Python >= 3.8, False otherwise
        """
        is_valid = (
            self.python_version.major == 3 and
            self.python_version.minor >= 8
        )
        self.validation_results['python_version'] = is_valid
        return is_valid

    def detect_virtual_environment_activation(self) -> bool:
        """AC-002: Detect virtual environment activation.
        
        Returns:
            bool: True if virtual environment is active, False otherwise
        """
        has_venv_var = 'VIRTUAL_ENV' in os.environ
        has_different_prefix = (
            hasattr(sys, 'base_prefix') and
            sys.base_prefix != sys.prefix
        )
        has_conda_env = 'CONDA_DEFAULT_ENV' in os.environ
        
        is_in_venv = has_venv_var or has_different_prefix or has_conda_env
        self.validation_results['virtual_environment'] = is_in_venv
        return is_in_venv

    def validate_required_environment_variables(self) -> bool:
        """AC-003: Validate required environment variables.
        
        Returns:
            bool: True if all required env vars are set, False otherwise
        """
        missing_vars = []
        for var in self.required_env_vars:
            if var not in os.environ:
                missing_vars.append(var)
        
        all_vars_present = len(missing_vars) == 0
        self.validation_results['environment_variables'] = all_vars_present
        self.validation_results['missing_vars'] = missing_vars
        return all_vars_present

    def get_validation_report(self) -> Dict:
        """Get comprehensive validation report.
        
        Returns:
            dict: Complete validation report with all check results
        """
        return {
            'python_version': {
                'valid': self.validation_results.get(
                    'python_version', False
                ),
                'version': (
                    f"{self.python_version.major}."
                    f"{self.python_version.minor}."
                    f"{self.python_version.micro}"
                ),
                'required': '>=3.8'
            },
            'virtual_environment': {
                'active': self.validation_results.get(
                    'virtual_environment', False
                ),
                'venv_path': os.environ.get('VIRTUAL_ENV', 'Not set'),
                'conda_env': os.environ.get('CONDA_DEFAULT_ENV', 'Not set')
            },
            'environment_variables': {
                'valid': self.validation_results.get(
                    'environment_variables', False
                ),
                'missing': self.validation_results.get('missing_vars', []),
                'required': self.required_env_vars
            },
            'timestamp': datetime.now().isoformat()
        }

    def validate_all(self) -> Tuple[bool, Dict]:
        """Run all validation checks.
        
        Returns:
            tuple: (all_valid: bool, report: dict)
        """
        python_ok = self.validate_python_version_3_8()
        venv_ok = self.detect_virtual_environment_activation()
        envvars_ok = self.validate_required_environment_variables()
        
        all_valid = python_ok and venv_ok and envvars_ok
        report = self.get_validation_report()
        
        return all_valid, report
