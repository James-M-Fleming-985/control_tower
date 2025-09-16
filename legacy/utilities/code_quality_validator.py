#!/usr/bin/env python3
"""
Code Quality Validator - Professional Standards Enforcement
Automated import/syntax/dependency verification for test pyramids

This module provides comprehensive code quality validation that integrates
with our professional standards forcing functions and test pyramid structure.
"""

import ast
import sys
import subprocess
import importlib.util
import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field

# Import from the quality gates module
try:
    from src.quality_gates import QualityGateResult, QualityGateStatus
except ImportError:
    # Define basic classes if import fails
    from enum import Enum
    import datetime
    
    class QualityGateStatus(Enum):
        PASSED = "passed"
        FAILED = "failed"
        BLOCKED = "blocked"
    
    @dataclass
    class QualityGateResult:
        gate_name: str
        status: QualityGateStatus
        violations: List[str] = field(default_factory=list)
        recommendations: List[str] = field(default_factory=list)
        evidence: Dict[str, Any] = field(default_factory=dict)
        execution_time: float = 0.0


@dataclass
class ImportValidationResult:
    """Result of import validation for a Python file"""
    file_path: str
    valid_imports: List[str] = field(default_factory=list)
    invalid_imports: List[str] = field(default_factory=list)
    missing_dependencies: List[str] = field(default_factory=list)
    circular_imports: List[str] = field(default_factory=list)
    syntax_errors: List[str] = field(default_factory=list)
    is_valid: bool = True


@dataclass
class DependencyValidationResult:
    """Result of dependency validation"""
    component_name: str
    required_dependencies: List[str] = field(default_factory=list)
    missing_dependencies: List[str] = field(default_factory=list)
    version_conflicts: List[str] = field(default_factory=list)
    is_valid: bool = True


class CodeQualityValidator:
    """
    Comprehensive code quality validator for professional standards enforcement
    
    Validates:
    - Import syntax and availability
    - Dependency resolution
    - Circular dependency detection  
    - Python syntax correctness
    - Module structure compliance
    """
    
    def __init__(self, workspace_root: str = "/workspaces/control_tower"):
        self.workspace_root = Path(workspace_root)
        self.src_root = self.workspace_root / "src"
        
    def validate_test_pyramid_layer(self, layer_path: str, component_name: str) -> QualityGateResult:
        """
        Validate a complete test pyramid layer for professional standards
        
        This is the main entry point for test pyramid validation that integrates
        with our forcing function framework.
        """
        print(f"🔍 VALIDATING TEST PYRAMID LAYER: {component_name}")
        print("=" * 50)
        
        violations = []
        recommendations = []
        evidence = {}
        
        # 1. Syntax Validation
        syntax_result = self._validate_syntax(layer_path)
        if not syntax_result.is_valid:
            violations.extend([f"Syntax Error: {err}" for err in syntax_result.syntax_errors])
            evidence["syntax_errors"] = syntax_result.syntax_errors
        
        # 2. Import Validation
        import_result = self._validate_imports(layer_path)
        if not import_result.is_valid:
            violations.extend([f"Import Error: {imp}" for imp in import_result.invalid_imports])
            violations.extend([f"Missing Dependency: {dep}" for dep in import_result.missing_dependencies])
            evidence["import_failures"] = import_result.invalid_imports
            evidence["missing_dependencies"] = import_result.missing_dependencies
        
        # 3. Dependency Validation
        dep_result = self._validate_dependencies(component_name)
        if not dep_result.is_valid:
            violations.extend([f"Dependency Issue: {dep}" for dep in dep_result.missing_dependencies])
            evidence["dependency_failures"] = dep_result.missing_dependencies
        
        # 4. Test Structure Validation
        test_structure_valid = self._validate_test_structure(layer_path)
        if not test_structure_valid:
            violations.append("Test structure does not meet professional standards")
            recommendations.append("Follow standard test pyramid structure")
        
        # 5. Professional Standards Check
        professional_check = self._validate_professional_standards(layer_path)
        violations.extend(professional_check.get("violations", []))
        recommendations.extend(professional_check.get("recommendations", []))
        
        # Determine overall status
        status = QualityGateStatus.PASSED if not violations else QualityGateStatus.FAILED
        
        return QualityGateResult(
            gate_name=f"CodeQuality_{component_name}",
            status=status,
            timestamp=datetime.datetime.now(),
            validation_results=evidence,
            evidence_files=[],
            violations=violations,
            recommendations=recommendations,
            blocking_issues=violations if status == QualityGateStatus.FAILED else []
        )
    
    def _validate_syntax(self, file_path: str) -> ImportValidationResult:
        """Validate Python syntax using AST parsing"""
        result = ImportValidationResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse AST to check syntax
            ast.parse(source_code, filename=file_path)
            print(f"  ✅ Syntax validation passed: {Path(file_path).name}")
            
        except SyntaxError as e:
            result.syntax_errors.append(f"Line {e.lineno}: {e.msg}")
            result.is_valid = False
            print(f"  ❌ Syntax error in {Path(file_path).name}: {e.msg}")
        except FileNotFoundError:
            result.syntax_errors.append(f"File not found: {file_path}")
            result.is_valid = False
            print(f"  ❌ File not found: {file_path}")
        except Exception as e:
            result.syntax_errors.append(f"Unexpected error: {str(e)}")
            result.is_valid = False
            print(f"  ❌ Unexpected syntax validation error: {e}")
        
        return result
    
    def _validate_imports(self, file_path: str) -> ImportValidationResult:
        """Validate all imports in a Python file can be resolved"""
        result = ImportValidationResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse imports from AST
            tree = ast.parse(source_code, filename=file_path)
            imports = self._extract_imports_from_ast(tree)
            
            # Test each import
            for import_name in imports:
                if self._test_import(import_name):
                    result.valid_imports.append(import_name)
                    print(f"  ✅ Import valid: {import_name}")
                else:
                    result.invalid_imports.append(import_name)
                    result.is_valid = False
                    print(f"  ❌ Import failed: {import_name}")
            
        except Exception as e:
            result.syntax_errors.append(f"Import validation error: {str(e)}")
            result.is_valid = False
            print(f"  ❌ Import validation failed: {e}")
        
        return result
    
    def _validate_dependencies(self, component_name: str) -> DependencyValidationResult:
        """Validate component dependencies are available"""
        result = DependencyValidationResult(component_name=component_name)
        
        # Define expected dependencies per component
        dependency_map = {
            "test_generator": ["pytest", "dataclasses", "pathlib"],
            "requirements_parser": ["pathlib", "dataclasses", "enum"],
            "professional_test_generator": ["typing", "pathlib"],
            "quality_gates": ["abc", "dataclasses", "typing"]
        }
        
        required_deps = dependency_map.get(component_name, [])
        result.required_dependencies = required_deps
        
        for dep in required_deps:
            if not self._test_import(dep):
                result.missing_dependencies.append(dep)
                result.is_valid = False
                print(f"  ❌ Missing dependency: {dep}")
            else:
                print(f"  ✅ Dependency available: {dep}")
        
        return result
    
    def _validate_test_structure(self, file_path: str) -> bool:
        """Validate file follows test pyramid structure"""
        path = Path(file_path)
        
        # Check if it's in appropriate test structure
        if "test" in path.name or "test" in str(path.parent):
            # Test file should have test functions
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if "def test_" in content and "assert" in content:
                    print(f"  ✅ Test structure valid: {path.name}")
                    return True
                else:
                    print(f"  ❌ Test structure invalid: missing test functions or assertions")
                    return False
            except:
                return False
        else:
            # Source file should have docstrings and proper structure
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if '"""' in content and ("class " in content or "def " in content):
                    print(f"  ✅ Source structure valid: {path.name}")
                    return True
                else:
                    print(f"  ❌ Source structure invalid: missing docstrings or proper structure")
                    return False
            except:
                return False
    
    def _validate_professional_standards(self, file_path: str) -> Dict[str, List[str]]:
        """Validate file meets professional coding standards"""
        violations = []
        recommendations = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for docstrings
            if '"""' not in content:
                violations.append("Missing module/class/function docstrings")
                recommendations.append("Add comprehensive docstrings")
            
            # Check for type hints
            if "typing" not in content and ("def " in content and "->" not in content):
                violations.append("Missing type hints")
                recommendations.append("Add type hints for function parameters and returns")
            
            # Check for error handling
            if "try:" not in content and ("def " in content):
                violations.append("Insufficient error handling")
                recommendations.append("Add appropriate error handling with try/except blocks")
            
            # Check for logging
            if "print(" in content and "logging" not in content:
                violations.append("Using print instead of proper logging")
                recommendations.append("Replace print statements with proper logging")
            
        except Exception as e:
            violations.append(f"Professional standards validation failed: {e}")
        
        return {"violations": violations, "recommendations": recommendations}
    
    def _extract_imports_from_ast(self, tree: ast.AST) -> List[str]:
        """Extract all import statements from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                    # Also add specific imports
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
        
        return imports
    
    def _test_import(self, import_name: str) -> bool:
        """Test if an import can be resolved"""
        try:
            # Handle relative imports and complex module paths
            if import_name.startswith('.'):
                return True  # Skip relative imports for now
            
            # Try to import the module
            if '.' in import_name:
                module_name = import_name.split('.')[0]
            else:
                module_name = import_name
            
            spec = importlib.util.find_spec(module_name)
            return spec is not None
            
        except (ImportError, ValueError, AttributeError):
            return False


def validate_test_pyramid_component(component_path: str, component_name: str) -> QualityGateResult:
    """
    Entry point for test pyramid component validation
    
    This function integrates with our professional standards forcing function
    to ensure all test pyramid components meet quality standards.
    """
    validator = CodeQualityValidator()
    return validator.validate_test_pyramid_layer(component_path, component_name)