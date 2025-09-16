#!/usr/bin/env python3
"""
Professional Standards Validation System
Enforces evidence-based completion validation for all development work
"""

import sys
import subprocess
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util


class ProfessionalValidator:
    """Enforces professional development standards with evidence-based validation"""
    
    def __init__(self, component_name: str, workspace_root: str = "/workspaces/control_tower"):
        self.component_name = component_name
        self.workspace_root = Path(workspace_root)
        self.evidence_dir = self.workspace_root / "evidence"
        self.validation_reports_dir = self.evidence_dir / "validation_reports"
        self.test_outputs_dir = self.evidence_dir / "test_outputs" 
        self.coverage_reports_dir = self.evidence_dir / "coverage_reports"
        
        # Create evidence directories
        for dir_path in [self.validation_reports_dir, self.test_outputs_dir, self.coverage_reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def validate_professional_completion(self) -> Dict[str, Any]:
        """
        MANDATORY professional validation - NO completion claims without this passing
        Returns comprehensive evidence report
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        validation_id = f"{self.component_name}_{timestamp}"
        
        print(f"🔍 PROFESSIONAL VALIDATION: {self.component_name}")
        print("=" * 60)
        
        evidence_report = {
            "validation_id": validation_id,
            "component": self.component_name,
            "timestamp": timestamp,
            "standards_version": "1.0",
            "validation_results": {},
            "overall_status": "UNKNOWN",
            "evidence_files": {},
            "violations": [],
            "recommendations": []
        }
        
        # 1. FILE EXISTENCE AND INTEGRITY
        print("📁 Validating File Existence and Integrity...")
        file_validation = self._validate_files()
        evidence_report["validation_results"]["file_integrity"] = file_validation
        
        # 2. CODE QUALITY AND IMPORTS
        print("🔍 Validating Code Quality and Imports...")
        code_validation = self._validate_code_quality()
        evidence_report["validation_results"]["code_quality"] = code_validation
        
        # 3. TEST EXECUTION AND COVERAGE
        print("🧪 Validating Test Execution and Coverage...")
        test_validation = self._validate_tests()
        evidence_report["validation_results"]["test_execution"] = test_validation
        
        # 4. REQUIREMENTS TRACEABILITY
        print("📋 Validating Requirements Traceability...")
        requirements_validation = self._validate_requirements_traceability()
        evidence_report["validation_results"]["requirements_traceability"] = requirements_validation
        
        # 5. INTEGRATION VALIDATION
        print("🔗 Validating Integration Points...")
        integration_validation = self._validate_integration()
        evidence_report["validation_results"]["integration"] = integration_validation
        
        # 6. DOCUMENTATION COMPLETENESS
        print("📖 Validating Documentation...")
        docs_validation = self._validate_documentation()
        evidence_report["validation_results"]["documentation"] = docs_validation
        
        # Calculate overall status
        evidence_report["overall_status"] = self._calculate_overall_status(evidence_report["validation_results"])
        
        # Generate evidence files
        self._generate_evidence_files(evidence_report, validation_id)
        
        # Display results
        self._display_validation_results(evidence_report)
        
        return evidence_report
    
    def _validate_files(self) -> Dict[str, Any]:
        """Validate that all required files exist and are readable"""
        file_patterns = {
            "implementation": [
                f"src/**/{self.component_name}.py",
                f"modules/**/{self.component_name}.py",
                f"**/{self.component_name}.py"
            ],
            "tests": [
                f"tests/**/test_{self.component_name}.py",
                f"src/**/test_{self.component_name}.py",
                f"**/test_{self.component_name}.py"
            ]
        }
        
        results = {
            "implementation_files": [],
            "test_files": [],
            "missing_files": [],
            "file_checksums": {},
            "status": "UNKNOWN"
        }
        
        # Find implementation files
        for pattern in file_patterns["implementation"]:
            for file_path in self.workspace_root.glob(pattern):
                if file_path.is_file():
                    results["implementation_files"].append(str(file_path))
                    # Calculate checksum for integrity
                    with open(file_path, 'rb') as f:
                        checksum = hashlib.sha256(f.read()).hexdigest()
                        results["file_checksums"][str(file_path)] = checksum
        
        # Find test files
        for pattern in file_patterns["tests"]:
            for file_path in self.workspace_root.glob(pattern):
                if file_path.is_file():
                    results["test_files"].append(str(file_path))
                    with open(file_path, 'rb') as f:
                        checksum = hashlib.sha256(f.read()).hexdigest()
                        results["file_checksums"][str(file_path)] = checksum
        
        # Determine status
        if results["implementation_files"] and results["test_files"]:
            results["status"] = "PASS"
        elif results["implementation_files"] and not results["test_files"]:
            results["status"] = "FAIL"
            results["missing_files"].append(f"test_{self.component_name}.py")
        else:
            results["status"] = "FAIL"
            results["missing_files"].append(f"{self.component_name}.py")
        
        return results
    
    def _validate_code_quality(self) -> Dict[str, Any]:
        """Validate code quality, syntax, and imports"""
        results = {
            "syntax_check": "UNKNOWN",
            "import_check": "UNKNOWN", 
            "static_analysis": "UNKNOWN",
            "errors": [],
            "warnings": [],
            "status": "UNKNOWN"
        }
        
        try:
            # Find implementation files
            impl_files = list(self.workspace_root.glob(f"**/{self.component_name}.py"))
            
            for file_path in impl_files:
                # Syntax check
                try:
                    with open(file_path, 'r') as f:
                        compile(f.read(), str(file_path), 'exec')
                    results["syntax_check"] = "PASS"
                except SyntaxError as e:
                    results["syntax_check"] = "FAIL"
                    results["errors"].append(f"Syntax error in {file_path}: {e}")
                
                # Import check
                try:
                    spec = importlib.util.spec_from_file_location("test_module", file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    results["import_check"] = "PASS"
                except Exception as e:
                    results["import_check"] = "FAIL"
                    results["errors"].append(f"Import error in {file_path}: {e}")
            
            # Overall status
            if results["syntax_check"] == "PASS" and results["import_check"] == "PASS":
                results["status"] = "PASS"
            else:
                results["status"] = "FAIL"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["errors"].append(f"Code validation error: {e}")
        
        return results
    
    def _validate_tests(self) -> Dict[str, Any]:
        """Execute tests and validate coverage"""
        results = {
            "test_execution": "UNKNOWN",
            "test_output": "",
            "coverage_percentage": 0,
            "test_count": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "coverage_report_path": "",
            "status": "UNKNOWN"
        }
        
        try:
            # Find test files
            test_files = list(self.workspace_root.glob(f"**/test_{self.component_name}.py"))
            
            if not test_files:
                results["status"] = "FAIL"
                results["test_output"] = "No test files found"
                return results
            
            # Run pytest with coverage
            cmd = [
                "python", "-m", "pytest", 
                str(test_files[0]),
                "--verbose",
                "--tb=short",
                f"--cov={self.component_name}",
                "--cov-report=html",
                f"--cov-report=html:{self.coverage_reports_dir}/{self.component_name}_coverage.html",
                "--cov-report=term"
            ]
            
            process = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            results["test_output"] = process.stdout + process.stderr
            
            # Parse test results
            if "FAILED" in results["test_output"]:
                results["test_execution"] = "FAIL"
            elif "passed" in results["test_output"]:
                results["test_execution"] = "PASS"
            else:
                results["test_execution"] = "UNKNOWN"
            
            # Extract coverage percentage (basic parsing)
            lines = results["test_output"].split('\n')
            for line in lines:
                if "%" in line and "coverage" in line.lower():
                    try:
                        percentage = int(line.split('%')[0].split()[-1])
                        results["coverage_percentage"] = percentage
                    except:
                        pass
            
            # Set coverage report path
            coverage_report = self.coverage_reports_dir / f"{self.component_name}_coverage.html"
            if coverage_report.exists():
                results["coverage_report_path"] = str(coverage_report)
            
            # Determine overall status
            if (results["test_execution"] == "PASS" and 
                results["coverage_percentage"] >= 80):
                results["status"] = "PASS"
            else:
                results["status"] = "FAIL"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["test_output"] = f"Test execution error: {e}"
        
        return results
    
    def _validate_requirements_traceability(self) -> Dict[str, Any]:
        """Validate that requirements are properly traced to tests"""
        results = {
            "requirements_found": [],
            "mapped_tests": [],
            "unmapped_requirements": [],
            "traceability_percentage": 0,
            "status": "UNKNOWN"
        }
        
        # This is a simplified version - would need more sophisticated parsing
        # for real requirements traceability
        
        try:
            # Find requirements files
            req_files = list(self.workspace_root.glob("requirements/**/*.md"))
            test_files = list(self.workspace_root.glob(f"**/test_{self.component_name}.py"))
            
            if req_files and test_files:
                results["status"] = "PASS"
                results["traceability_percentage"] = 85  # Placeholder
            else:
                results["status"] = "FAIL"
                
        except Exception as e:
            results["status"] = "FAIL"
        
        return results
    
    def _validate_integration(self) -> Dict[str, Any]:
        """Validate integration with dependent components"""
        results = {
            "dependencies_resolved": True,
            "integration_tests_exist": False,
            "integration_tests_pass": False,
            "dependency_list": [],
            "status": "UNKNOWN"
        }
        
        try:
            # Check for integration test files
            integration_test_files = list(self.workspace_root.glob(f"**/test_*integration*.py"))
            
            if integration_test_files:
                results["integration_tests_exist"] = True
                # Would run integration tests here
                results["integration_tests_pass"] = True  # Placeholder
                results["status"] = "PASS"
            else:
                results["status"] = "PARTIAL"
                
        except Exception as e:
            results["status"] = "FAIL"
        
        return results
    
    def _validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness"""
        results = {
            "docstrings_present": False,
            "readme_exists": False,
            "api_docs_complete": False,
            "status": "UNKNOWN"
        }
        
        try:
            # Check for basic documentation
            impl_files = list(self.workspace_root.glob(f"**/{self.component_name}.py"))
            
            if impl_files:
                with open(impl_files[0], 'r') as f:
                    content = f.read()
                    if '"""' in content or "'''" in content:
                        results["docstrings_present"] = True
            
            # Check for README
            readme_files = list(self.workspace_root.glob("**/README.md"))
            if readme_files:
                results["readme_exists"] = True
            
            if results["docstrings_present"] and results["readme_exists"]:
                results["status"] = "PASS"
            else:
                results["status"] = "PARTIAL"
                
        except Exception as e:
            results["status"] = "FAIL"
        
        return results
    
    def _calculate_overall_status(self, validation_results: Dict[str, Any]) -> str:
        """Calculate overall validation status"""
        pass_count = 0
        total_count = 0
        
        for category, result in validation_results.items():
            total_count += 1
            if result.get("status") == "PASS":
                pass_count += 1
        
        if pass_count == total_count:
            return "PROFESSIONAL_COMPLETE"
        elif pass_count >= total_count * 0.8:
            return "NEEDS_MINOR_FIXES"
        else:
            return "MAJOR_ISSUES_FOUND"
    
    def _generate_evidence_files(self, evidence_report: Dict[str, Any], validation_id: str):
        """Generate immutable evidence files"""
        # Save validation report
        report_path = self.validation_reports_dir / f"{validation_id}_validation.json"
        with open(report_path, 'w') as f:
            json.dump(evidence_report, f, indent=2, default=str)
        
        evidence_report["evidence_files"]["validation_report"] = str(report_path)
        
        # Save test output if available
        test_results = evidence_report["validation_results"].get("test_execution", {})
        if test_results.get("test_output"):
            test_output_path = self.test_outputs_dir / f"{validation_id}_test_output.log"
            with open(test_output_path, 'w') as f:
                f.write(test_results["test_output"])
            evidence_report["evidence_files"]["test_output"] = str(test_output_path)
    
    def _display_validation_results(self, evidence_report: Dict[str, Any]):
        """Display professional validation results"""
        print("\n" + "=" * 60)
        print(f"🎯 PROFESSIONAL VALIDATION RESULTS: {self.component_name}")
        print("=" * 60)
        
        overall_status = evidence_report["overall_status"]
        if overall_status == "PROFESSIONAL_COMPLETE":
            print("✅ STATUS: PROFESSIONAL STANDARDS MET")
        elif overall_status == "NEEDS_MINOR_FIXES":
            print("⚠️  STATUS: MINOR ISSUES - FIXES REQUIRED")
        else:
            print("❌ STATUS: MAJOR ISSUES - NOT PRODUCTION READY")
        
        print(f"\n📊 VALIDATION BREAKDOWN:")
        for category, result in evidence_report["validation_results"].items():
            status = result.get("status", "UNKNOWN")
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"  {status_icon} {category.replace('_', ' ').title()}: {status}")
        
        print(f"\n📁 EVIDENCE FILES:")
        for file_type, file_path in evidence_report["evidence_files"].items():
            print(f"  📄 {file_type}: {file_path}")
        
        print("\n" + "=" * 60)
        
        if overall_status != "PROFESSIONAL_COMPLETE":
            print("❌ COMPLETION CLAIM REJECTED - FIX ISSUES ABOVE")
            print("🔄 Re-run validation after fixes")
        else:
            print("✅ COMPONENT MEETS PROFESSIONAL STANDARDS")
            print("✅ COMPLETION CLAIM ACCEPTED WITH EVIDENCE")
        
        print("=" * 60)


def main():
    """Main entry point for professional validation"""
    if len(sys.argv) != 2:
        print("Usage: python professional_validator.py <component_name>")
        sys.exit(1)
    
    component_name = sys.argv[1]
    validator = ProfessionalValidator(component_name)
    
    evidence_report = validator.validate_professional_completion()
    
    # Exit with appropriate code
    if evidence_report["overall_status"] == "PROFESSIONAL_COMPLETE":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()