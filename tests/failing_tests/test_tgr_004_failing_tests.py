"""
FUNCTIONAL REQUIREMENT TEST - TGR-004
Test Data Validation
"""
import pytest

class TestTGR004:
    """Test Data Validation for test case data integrity"""
    
    def test_test_data_validation_fails(self):
        """Test REAL test data validation with comprehensive integrity checks"""
        from src.data_access.test_data_validator import TestDataValidator
        
        validator = TestDataValidator()
        
        # Test valid test case data
        valid_test_data = {
            'name': 'test_valid_function',
            'description': 'A valid test case',
            'test_code': 'def test_valid_function(): assert True',
            'expected_result': 'pass',
            'tags': ['unit', 'validation'],
            'category': 'functional',
            'timeout': 30
        }
        
        is_valid, errors = validator.validate_test_data(valid_test_data)
        assert is_valid, f"Valid test data should pass validation: {errors}"
        assert len(errors) == 0, "No errors should be present for valid data"
        
        # Test invalid test case data - missing required fields
        invalid_test_data = {
            'description': 'Missing name field',
            'test_code': 'def test_something(): pass'
        }
        
        is_invalid, error_list = validator.validate_test_data(invalid_test_data)
        assert not is_invalid, "Invalid test data should fail validation"
        assert len(error_list) > 0, "Error list should contain validation errors"
        assert any('name' in error.lower() for error in error_list), "Should have name field error"
        
        # Test code syntax validation
        invalid_code_data = {
            'name': 'test_syntax_error',
            'description': 'Test with syntax error',
            'test_code': 'def test_syntax_error( assert True',  # Missing closing parenthesis
            'expected_result': 'pass'
        }
        
        is_code_valid, code_errors = validator.validate_test_data(invalid_code_data)
        assert not is_code_valid, "Test data with syntax errors should fail validation"
        assert any('syntax' in error.lower() for error in code_errors), "Should have syntax error"
        
        # Test data type validation
        type_invalid_data = {
            'name': 123,  # Should be string
            'description': 'Test with wrong types',
            'test_code': 'def test_something(): pass',
            'timeout': 'invalid'  # Should be number
        }
        
        is_type_valid, type_errors = validator.validate_test_data(type_invalid_data)
        assert not is_type_valid, "Test data with wrong types should fail validation"
        
        # Test comprehensive integrity check
        integrity_result = validator.check_data_integrity([valid_test_data, invalid_test_data])
        assert 'valid_count' in integrity_result, "Integrity check should return valid count"
        assert 'invalid_count' in integrity_result, "Integrity check should return invalid count"
        assert integrity_result['valid_count'] == 1, "Should have 1 valid test case"