#!/usr/bin/env python3
"""
Integration Tests for TestGenerator - TR-DA-003
Testing integration with other components and real file processing
"""

import pytest
import tempfile
from pathlib import Path


def test_test_generator_integrates_with_requirements_models():
    """Integration test: TestGenerator works with ParsedRequirement"""
    from src.data_access.test_generator import TestGenerator
    from src.data_access.requirements_models import ParsedRequirement
    
    # Create a realistic requirement
    requirement = ParsedRequirement(
        requirement_id="TR-DA-003",
        description="Requirements Parser & Test Generator",
        primary_objective="Generate tests from parsed requirements",
        acceptance_criteria=[
            {
                "id": "AC-DA-003-001", 
                "description": "Parse Real Feature File Successfully",
                "completed": False
            },
            {
                "id": "AC-DA-003-002",
                "description": "Generate Failing Tests Automatically", 
                "completed": False
            }
        ]
    )
    
    # Test integration
    generator = TestGenerator()
    tests = generator.generate_tests_from_requirement(requirement)
    
    # Verify integration works
    assert len(tests) == 2
    assert all(test.requirement_id == "TR-DA-003" for test in tests)
    assert all("def test_" in test.test_code for test in tests)


def test_test_generator_creates_realistic_test_files():
    """Integration test: Creates actual test files that can be executed"""
    from src.data_access.test_generator import TestGenerator
    from src.data_access.requirements_models import ParsedRequirement
    
    requirement = ParsedRequirement(
        requirement_id="TR-INTEGRATION-001",
        description="File creation integration test",
        acceptance_criteria=[
            {
                "id": "AC-001",
                "description": "Should create executable test files",
                "completed": False
            }
        ]
    )
    
    generator = TestGenerator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate tests
        tests = generator.generate_tests_from_requirement(requirement)
        
        # Write test to actual file
        test_file_path = Path(temp_dir) / "test_integration.py"
        with open(test_file_path, 'w') as f:
            f.write("import pytest\n\n")
            for test in tests:
                f.write(test.test_code + "\n\n")
        
        # Verify file can be imported (syntax check)
        import subprocess
        result = subprocess.run([
            "python", "-m", "py_compile", str(test_file_path)
        ], capture_output=True)
        
        assert result.returncode == 0, f"Generated test file has syntax errors: {result.stderr}"


def test_test_generator_handles_complex_requirements():
    """Integration test: Handles requirements with multiple criteria types"""
    from src.data_access.test_generator import TestGenerator
    from src.data_access.requirements_models import ParsedRequirement
    
    # Complex requirement with various criteria
    requirement = ParsedRequirement(
        requirement_id="TR-COMPLEX-001",
        description="Complex requirement with multiple acceptance criteria",
        acceptance_criteria=[
            {
                "id": "AC-001",
                "description": "Handle user input validation with special characters",
                "completed": False
            },
            {
                "id": "AC-002", 
                "description": "Process file paths containing spaces and unicode",
                "completed": False
            },
            {
                "id": "AC-003",
                "description": "Validate API responses with nested JSON structures",
                "completed": False
            }
        ]
    )
    
    generator = TestGenerator()
    tests = generator.generate_tests_from_requirement(requirement)
    
    # Verify all criteria are covered
    assert len(tests) == 3
    
    # Verify test names are valid Python identifiers
    for test in tests:
        assert test.test_name.startswith("test_")
        assert test.test_name.replace("_", "").isalnum()
        
    # Verify all generated code compiles
    for test in tests:
        compile(test.test_code, '<string>', 'exec')


def test_test_generator_integration_with_file_system():
    """Integration test: Test file structure creation works with file system"""
    from src.data_access.test_generator import TestGenerator
    
    generator = TestGenerator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory for test
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_dir)
            
            # Create test file structure
            result = generator.create_test_file_structure("sample_component", "unit")
            
            if result:  # If method returns a path
                test_file = Path(result)
                assert test_file.exists()
                assert test_file.suffix == '.py'
                assert 'test_' in test_file.name
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    print("🔺 RUNNING INTEGRATION TESTS (TDD Test Pyramid)")
    print("=" * 55)
    pytest.main([__file__, "-v"])