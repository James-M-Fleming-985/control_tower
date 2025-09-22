"""
Test Data Validator - Comprehensive validation for test case data
Minimal GREEN phase implementation
"""
import ast
import re
from typing import Dict, Any, List, Tuple

class TestDataValidator:
    """REAL test data validation with comprehensive integrity checks"""
    
    def __init__(self):
        self.required_fields = ['name', 'test_code']
        self.optional_fields = ['description', 'expected_result', 'tags', 'category', 'timeout']
    
    def validate_test_data(self, test_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate test case data"""
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in test_data:
                errors.append(f"Missing required field: {field}")
            elif not test_data[field]:
                errors.append(f"Required field '{field}' cannot be empty")
        
        # Validate field types
        if 'name' in test_data and not isinstance(test_data['name'], str):
            errors.append("Field 'name' must be a string")
        
        if 'timeout' in test_data and test_data['timeout'] is not None:
            try:
                float(test_data['timeout'])
            except (ValueError, TypeError):
                errors.append("Field 'timeout' must be a number")
        
        # Validate test code syntax
        if 'test_code' in test_data:
            syntax_valid, syntax_error = self._validate_code_syntax(test_data['test_code'])
            if not syntax_valid:
                errors.append(f"Test code syntax error: {syntax_error}")
        
        # Validate name format
        if 'name' in test_data and isinstance(test_data['name'], str):
            name_valid, name_error = self._validate_test_name(test_data['name'])
            if not name_valid:
                errors.append(name_error)
        
        return len(errors) == 0, errors
    
    def _validate_code_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Python code syntax"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    def _validate_test_name(self, name: str) -> Tuple[bool, str]:
        """Validate test name format"""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            return False, "Test name must start with letter and contain only letters, numbers, and underscores"
        
        if len(name) > 100:
            return False, "Test name must be 100 characters or less"
        
        return True, ""
    
    def check_data_integrity(self, test_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check integrity of multiple test cases"""
        valid_count = 0
        invalid_count = 0
        errors = []
        
        for i, test_data in enumerate(test_data_list):
            is_valid, validation_errors = self.validate_test_data(test_data)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                errors.extend([f"Test {i}: {error}" for error in validation_errors])
        
        return {
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'total_count': len(test_data_list),
            'errors': errors
        }