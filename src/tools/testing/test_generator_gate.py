#!/usr/bin/env python3
"""
Test Generator Quality Gates - Phase 2A
Automated quality validation for test generation functionality
"""

import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, Any, List
import ast

from ..quality_gates import QualityGate, QualityGateResult, QualityGateStatus


class TestGeneratorQualityGate(QualityGate):
    """Quality gate for TestGenerator component validation"""
    
    def __init__(self, workspace_root: str = "/workspaces/control_tower"):
        super().__init__("TestGenerator_Professional_Standards", workspace_root)
        self.test_generator_path = self.workspace_root / "src" / "data_access" / "test_generator.py"
        self.test_file_path = self.workspace_root / "tests" / "unit" / "data_access" / "test_test_generator.py"
    
    def validate_pre_execution(self, context: Dict[str, Any]) -> List[str]:
        """Validate TestGenerator before execution"""
        violations = []
        
        # Standard pre-execution validation
        test_generator_path = self.workspace_root / "src" / "data_access" / "test_generator.py"
        
        if not test_generator_path.exists():
            violations.append(f"TestGenerator file not found: {test_generator_path}")
            return violations
        
        # Code Quality Validation - Import/Syntax/Dependencies
        print("  🔍 Running code quality validation...")
        try:
            from . import validate_component_quality
            quality_result = validate_component_quality(str(test_generator_path), "test_generator")
            
            if quality_result.status != QualityGateStatus.PASSED:
                violations.extend([f"Code Quality: {v}" for v in quality_result.violations])
                print("  ❌ Code quality validation failed")
                for violation in quality_result.violations:
                    print(f"    🔥 {violation}")
            else:
                print("  ✅ Code quality validation passed")
                
        except Exception as e:
            violations.append(f"Code quality validation failed: {str(e)}")
            print(f"  ❌ Code quality validation error: {e}")
        
        # TestGenerator Class Validation
        try:
            # Test import TestGenerator class
            import sys
            sys.path.append(str(self.workspace_root))
            from src.data_access.test_generator import TestGenerator
            
            # Verify required methods exist
            required_methods = [
                'generate_tests_from_requirement',
                'generate_unit_tests', 
                'generate_integration_tests',
                'create_test_file_structure'
            ]
            
            for method in required_methods:
                if not hasattr(TestGenerator, method):
                    violations.append(f"TestGenerator missing required method: {method}")
                else:
                    print(f"  ✅ Method found: {method}")
            
            if not violations:
                print("  ✅ TestGenerator class validation passed")
            
        except ImportError as e:
            violations.append(f"Import failure: {str(e)}")
            print(f"  ❌ Import failed: {e}")
        except Exception as e:
            violations.append(f"TestGenerator class not found in module")
            print(f"  ❌ Class validation failed: {e}")
        
        return violations
    
    def monitor_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor test execution and implementation validation"""
        monitoring_data = {}
        
        # Check imports work
        try:
            spec = importlib.util.spec_from_file_location("test_generator", self.test_generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            monitoring_data["imports_successful"] = True
            monitoring_data["test_generator_class"] = hasattr(module, 'TestGenerator')
        except Exception as e:
            monitoring_data["imports_successful"] = False
            monitoring_data["import_error"] = str(e)
        
        return monitoring_data
    
    def validate_post_execution(self, context: Dict[str, Any]) -> QualityGateResult:
        """Validate TestGenerator meets professional standards"""
        violations = []
        recommendations = []
        validation_results = {}
        
        # Check imports work
        if not context.get("imports_successful", False):
            violations.append(f"Import failure: {context.get('import_error', 'Unknown error')}")
            recommendations.append("Fix import errors in test_generator.py")
        
        # Check TestGenerator class exists
        if not context.get("test_generator_class", False):
            violations.append("TestGenerator class not found in module")
            recommendations.append("Ensure TestGenerator class is properly defined")
        
        # Run tests if imports work
        if context.get("imports_successful", False):
            test_results = self._run_tests()
            validation_results.update(test_results)
            
            if test_results.get("test_failures", 0) > 0:
                violations.append(f"{test_results['test_failures']} tests failed")
                recommendations.append("Fix failing tests to meet professional standards")
            
            if test_results.get("coverage_percentage", 0) < 80:
                violations.append(f"Coverage {test_results.get('coverage_percentage', 0)}% below 80% requirement")
                recommendations.append("Increase test coverage to meet professional standards")
        
        # Check for required methods based on test expectations
        if context.get("imports_successful", False):
            missing_methods = self._check_required_methods()
            if missing_methods:
                violations.extend([f"Missing method: {method}" for method in missing_methods])
                recommendations.append("Implement all methods expected by tests")
        
        status = QualityGateStatus.PASSED if not violations else QualityGateStatus.FAILED
        
        return QualityGateResult(
            gate_name=self.gate_name,
            status=status,
            timestamp=context.get("timestamp"),
            validation_results=validation_results,
            evidence_files=[],
            violations=violations,
            recommendations=recommendations,
            blocking_issues=violations
        )
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run TestGenerator tests and collect results"""
        try:
            # Run pytest on the test file
            result = subprocess.run([
                "python", "-m", "pytest", 
                str(self.test_file_path),
                "-v", "--tb=short"
            ], cwd=self.workspace_root, capture_output=True, text=True, timeout=60)
            
            output = result.stdout + result.stderr
            
            # Parse results
            test_results = {
                "test_output": output,
                "test_passed": result.returncode == 0,
                "test_failures": output.count("FAILED"),
                "test_passes": output.count("PASSED"),
                "coverage_percentage": 0  # TODO: Parse coverage from output
            }
            
            return test_results
            
        except Exception as e:
            return {
                "test_output": f"Test execution error: {e}",
                "test_passed": False,
                "test_failures": 999,
                "test_passes": 0,
                "coverage_percentage": 0
            }
    
    def _check_required_methods(self) -> List[str]:
        """Check if TestGenerator has all methods expected by tests"""
        missing_methods = []
        
        try:
            # Read the test file to see what methods are expected
            with open(self.test_file_path, 'r') as f:
                test_content = f.read()
            
            # Look for method calls on self.test_generator
            expected_methods = []
            lines = test_content.split('\n')
            for line in lines:
                if 'self.test_generator.' in line and '(' in line:
                    # Extract method name
                    start = line.find('self.test_generator.') + len('self.test_generator.')
                    end = line.find('(', start)
                    if end > start:
                        method_name = line[start:end]
                        if method_name and method_name not in expected_methods:
                            expected_methods.append(method_name)
            
            # Check if TestGenerator has these methods
            try:
                spec = importlib.util.spec_from_file_location("test_generator", self.test_generator_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'TestGenerator'):
                    test_generator_class = getattr(module, 'TestGenerator')
                    for method in expected_methods:
                        if not hasattr(test_generator_class, method):
                            missing_methods.append(method)
            except:
                # If we can't import, we can't check methods
                pass
                
        except Exception:
            # If we can't read the test file, we can't check
            pass
        
        return missing_methods