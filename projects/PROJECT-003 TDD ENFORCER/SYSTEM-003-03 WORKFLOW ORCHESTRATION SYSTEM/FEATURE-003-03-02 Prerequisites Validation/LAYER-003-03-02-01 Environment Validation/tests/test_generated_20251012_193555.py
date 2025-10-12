```python
import os
import sys
import pytest
from unittest.mock import patch, MagicMock


class TestPythonVersionValidation:
    """Test suite for Python version validation >= 3.8"""

    def test_python_version_is_at_least_3_8(self):
        """Test that Python version is at least 3.8"""
        version_info = sys.version_info
        assert version_info.major >= 3
        assert version_info.minor >= 8
        assert (version_info.major, version_info.minor) >= (3, 8)

    def test_python_version_validation_function_fails_for_old_version(self):
        """Test that validation function rejects Python versions below 3.8"""
        with patch('sys.version_info') as mock_version:
            mock_version.major = 3
            mock_version.minor = 7
            
            def validate_python_version():
                if sys.version_info < (3, 8):
                    raise RuntimeError("Python version must be >= 3.8")
                return True
            
            with pytest.raises(RuntimeError, match="Python version must be >= 3.8"):
                validate_python_version()

    def test_python_version_string_format(self):
        """Test that Python version string contains proper format"""
        version_string = f"{sys.version_info.major}.{sys.version_info.minor}"
        parts = version_string.split('.')
        assert len(parts) >= 2
        assert int(parts[0]) >= 3
        assert int(parts[1]) >= 8

    def test_python_version_below_3_8_raises_exception(self):
        """Test that Python versions below 3.8 raise an exception"""
        def check_version(major, minor):
            if (major, minor) < (3, 8):
                raise ValueError(f"Unsupported Python version: {major}.{minor}")
            return True
        
        with pytest.raises(ValueError, match="Unsupported Python version"):
            check_version(3, 7)


class TestVirtualEnvironmentDetection:
    """Test suite for virtual environment activation detection"""

    def test_virtual_environment_is_activated(self):
        """Test that a virtual environment is currently activated"""
        is_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        assert is_venv is True, "Virtual environment is not activated"

    def test_virtual_env_variable_exists(self):
        """Test that VIRTUAL_ENV environment variable is set"""
        virtual_env = os.environ.get('VIRTUAL_ENV')
        assert virtual_env is not None, "VIRTUAL_ENV environment variable not set"
        assert len(virtual_env) > 0, "VIRTUAL_ENV is empty"

    def test_detect_venv_without_activation_fails(self):
        """Test that detection fails when venv is not activated"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.prefix', '/usr'):
                with patch('sys.base_prefix', '/usr'):
                    def detect_virtual_env():
                        if not os.environ.get('VIRTUAL_ENV'):
                            raise EnvironmentError("Virtual environment not activated")
                        return True
                    
                    with pytest.raises(EnvironmentError, match="Virtual environment not activated"):
                        detect_virtual_env()

    def test_sys_prefix_differs_from_base_prefix(self):
        """Test that sys.prefix differs from sys.base_prefix in venv"""
        if hasattr(sys, 'base_prefix'):
            assert sys.prefix != sys.base_prefix, "sys.prefix should differ from base_prefix in venv"
        else:
            pytest.fail("sys.base_prefix attribute not found")


class TestRequiredEnvironmentVariables:
    """Test suite for required environment variables validation"""

    def test_required_env_vars_are_set(self):
        """Test that all required environment variables are set"""
        required_vars = ['DATABASE_URL', 'API_KEY', 'SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        assert len(missing_vars) == 0, f"Missing required environment variables: {missing_vars}"

    def test_database_url_environment_variable(self):
        """Test that DATABASE_URL environment variable exists and is valid"""
        database_url = os.environ.get('DATABASE_URL')
        assert database_url is not None, "DATABASE_URL is not set"
        assert len(database_url) > 0, "DATABASE_URL is empty"
        assert database_url.startswith(('postgresql://', 'mysql://', 'sqlite://')), \
            "DATABASE_URL does not have valid database scheme"

    def test_api_key_environment_variable(self):
        """Test that API_KEY environment variable exists"""
        api_key = os.environ.get('API_KEY')
        assert api_key is not None, "API_KEY is not set"
        assert len(api_key) >= 32, "API_KEY is too short (minimum 32 characters)"

    def test_missing_env_var_raises_exception(self):
        """Test that missing required environment variable raises exception"""
        def validate_env_var(var_name):
            if not os.environ.get(var_name):
                raise KeyError(f"Required environment variable {var_name} is not set")
            return True
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyError, match="Required environment variable .* is not set"):
                validate_env_var('MISSING_VAR')

    def test_secret_key_environment_variable(self):
        """Test that SECRET_KEY environment variable exists and meets requirements"""
        secret_key = os.environ.get('SECRET_KEY')
        assert secret_key is not None, "SECRET_KEY is not set"
        assert len(secret_key) >= 32, "SECRET_KEY must be at least 32 characters long"

    def test_all_required_vars_validation_function(self):
        """Test validation function for all required environment variables"""
        def validate_all_required_env_vars():
            required = ['DATABASE_URL', 'API_KEY', 'SECRET_KEY', 'REDIS_URL']
            missing = [v for v in required if not os.environ.get(v)]
            if missing:
                raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            return True
        
        with pytest.raises(ValueError, match="Missing required environment variables"):
            validate_all_required_env_vars()
```