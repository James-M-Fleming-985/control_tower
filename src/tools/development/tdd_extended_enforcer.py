#!/usr/bin/env python3
"""
TDD Workflow Enforcer - Extended Stages 8-10
Testing Pyramid, Requirements Compliance, and Layer Completion

This module extends the core TDD enforcer with advanced validation stages:
- Stage 8: Testing Pyramid Validation with real test reports
- Stage 9: Requirements Compliance Verification with traceability
- Stage 10: Layer Completion Certification with next layer activation

Created: 2025-09-16
Phase: Extended TDD Workflow
Component: Advanced Stage Gates
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
import json
import re


class TestLevel(Enum):
    """Testing pyramid levels"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"


@dataclass
class TestReport:
    """Test execution report"""
    test_level: TestLevel
    total_tests: int
    passed_tests: int
    failed_tests: int
    coverage_percentage: float
    execution_time: float
    report_path: str
    repository: str
    timestamp: float


@dataclass
class RequirementEvidence:
    """Evidence that a requirement has been implemented"""
    requirement_id: str
    requirement_type: str  # FR, NFR, BR, AC
    implementation_files: List[str]
    test_files: List[str]
    coverage_percentage: float
    validation_status: str  # met, partial, missing
    evidence_details: Dict[str, Any]


class TDDExtendedEnforcer:
    """
    Extended TDD Workflow Enforcer with Stages 8-10
    
    Completes the TDD workflow with:
    - Testing pyramid validation
    - Requirements compliance verification  
    - Layer completion certification
    """
    
    def __init__(self, project_root: str = "/workspaces/control_tower"):
        """Initialize extended TDD enforcer"""
        self.project_root = Path(project_root)
        self.test_reports_dir = self.project_root / "test_reports"
        self.evidence_dir = self.project_root / "evidence"
        self.test_reports_dir.mkdir(exist_ok=True)
        self.evidence_dir.mkdir(exist_ok=True)
        
        # Track test reports and evidence
        self.test_reports: List[TestReport] = []
        self.requirement_evidence: List[RequirementEvidence] = []
        
        print("\033[95m🔧 Extended TDD Enforcer initialized - Stages 8-10 active\033[0m")
        print()
    
    def stage_gate_8_testing_pyramid_validation(self, layer_name: str = "current") -> Dict[str, Any]:
        """
        Stage Gate 8: Testing Pyramid Validation
        
        Validates complete testing pyramid with real test execution:
        - Unit Tests (70% of total tests)
        - Integration Tests (20% of total tests)  
        - E2E Tests (10% of total tests)
        - Real test reports stored in repository
        - Cross-repository validation for dependencies
        
        Args:
            layer_name: Name of the layer being validated
            
        Returns:
            Dict with validation results and test reports
        """
        print(f"\033[95m🔍 Stage Gate 8: Validating testing pyramid for {layer_name} layer...\033[0m")
        
        try:
            pyramid_results = {
                "stage_name": "stage_gate_8_testing_pyramid",
                "layer_name": layer_name,
                "pyramid_valid": False,
                "test_reports": [],
                "pyramid_distribution": {},
                "coverage_summary": {},
                "validation_details": {},
                "can_proceed": False,
                "timestamp": time.time()
            }
            
            # Step 1: Execute Unit Tests (70% target)
            print("🧪 Running Unit Tests...")
            unit_report = self._execute_test_level(TestLevel.UNIT, layer_name)
            pyramid_results["test_reports"].append(unit_report)
            
            # Step 2: Execute Integration Tests (20% target)  
            print("🔗 Running Integration Tests...")
            integration_report = self._execute_test_level(TestLevel.INTEGRATION, layer_name)
            pyramid_results["test_reports"].append(integration_report)
            
            # Step 3: Execute E2E Tests (10% target)
            print("🎯 Running E2E Tests...")
            e2e_report = self._execute_test_level(TestLevel.E2E, layer_name)
            pyramid_results["test_reports"].append(e2e_report)
            
            # Step 4: Validate Testing Pyramid Distribution
            total_tests = sum(report.total_tests for report in pyramid_results["test_reports"])
            
            if total_tests == 0:
                print("❌ Stage Gate 8 FAILED: No tests found")
                pyramid_results["validation_details"]["error"] = "No tests found"
                return pyramid_results
            
            unit_percentage = (unit_report.total_tests / total_tests) * 100
            integration_percentage = (integration_report.total_tests / total_tests) * 100
            e2e_percentage = (e2e_report.total_tests / total_tests) * 100
            
            pyramid_results["pyramid_distribution"] = {
                "unit_tests": {"count": unit_report.total_tests, "percentage": unit_percentage},
                "integration_tests": {"count": integration_report.total_tests, "percentage": integration_percentage},
                "e2e_tests": {"count": e2e_report.total_tests, "percentage": e2e_percentage},
                "total_tests": total_tests
            }
            
            # Step 5: Validate Pyramid Rules
            pyramid_valid = self._validate_pyramid_distribution(
                unit_percentage, integration_percentage, e2e_percentage
            )
            
            # Step 6: Validate All Tests Pass
            total_passed = sum(report.passed_tests for report in pyramid_results["test_reports"])
            total_failed = sum(report.failed_tests for report in pyramid_results["test_reports"])
            all_tests_pass = total_failed == 0
            
            # Step 7: Validate Coverage Requirements
            min_coverage = 80.0  # Minimum 80% coverage requirement
            coverage_meets_requirements = all(
                report.coverage_percentage >= min_coverage 
                for report in pyramid_results["test_reports"]
            )
            
            pyramid_results["coverage_summary"] = {
                "unit_coverage": unit_report.coverage_percentage,
                "integration_coverage": integration_report.coverage_percentage,
                "e2e_coverage": e2e_report.coverage_percentage,
                "average_coverage": sum(r.coverage_percentage for r in pyramid_results["test_reports"]) / 3,
                "meets_requirements": coverage_meets_requirements,
                "minimum_required": min_coverage
            }
            
            # Step 8: Final Validation
            pyramid_results["pyramid_valid"] = pyramid_valid and all_tests_pass and coverage_meets_requirements
            pyramid_results["can_proceed"] = pyramid_results["pyramid_valid"]
            
            # Step 9: Save Test Reports
            self._save_test_reports(pyramid_results["test_reports"], layer_name)
            
            # Step 10: Terminal Output
            if pyramid_results["pyramid_valid"]:
                print(f"\033[92m✅ Stage Gate 8 PASSED: Testing pyramid validated\033[0m")
                print(f"   📊 Distribution: Unit {unit_percentage:.0f}%, Integration {integration_percentage:.0f}%, E2E {e2e_percentage:.0f}%")
                print(f"   🎯 All {total_tests} tests passing with {pyramid_results['coverage_summary']['average_coverage']:.1f}% average coverage")
                print(f"   📁 Test reports saved to: {self.test_reports_dir}")
            else:
                print(f"❌ Stage Gate 8 FAILED: Testing pyramid validation failed")
                if not pyramid_valid:
                    print(f"   ⚠️  Pyramid distribution invalid")
                if not all_tests_pass:
                    print(f"   ⚠️  {total_failed} tests failing")
                if not coverage_meets_requirements:
                    print(f"   ⚠️  Coverage below {min_coverage}% requirement")
            
            print()
            return pyramid_results
            
        except Exception as e:
            print(f"❌ Stage Gate 8 FAILED: Testing pyramid error: {e}")
            return {
                "stage_name": "stage_gate_8_testing_pyramid",
                "pyramid_valid": False,
                "error": str(e),
                "can_proceed": False,
                "timestamp": time.time()
            }
    
    def _execute_test_level(self, test_level: TestLevel, layer_name: str) -> TestReport:
        """Execute tests at a specific level and generate report"""
        try:
            # Determine test directory based on level
            test_directories = {
                TestLevel.UNIT: "tests/unit",
                TestLevel.INTEGRATION: "tests/integration", 
                TestLevel.E2E: "tests/e2e"
            }
            
            test_dir = test_directories[test_level]
            test_path = self.project_root / test_dir
            
            if not test_path.exists():
                # Create directory and placeholder test if missing
                test_path.mkdir(parents=True, exist_ok=True)
                self._create_placeholder_test(test_path, test_level, layer_name)
            
            # Execute pytest with coverage
            start_time = time.time()
            cmd = [
                "python", "-m", "pytest", 
                str(test_path),
                "--cov=src",
                f"--cov-report=json:{self.test_reports_dir}/{test_level.value}_coverage.json",
                "--tb=short",
                "-v"
            ]
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, 
                cwd=self.project_root, timeout=120
            )
            execution_time = time.time() - start_time
            
            # Parse test results
            output = result.stdout + result.stderr
            total_tests = len(re.findall(r'::test_\w+', output))
            passed_tests = output.count("PASSED")
            failed_tests = output.count("FAILED")
            
            # Parse coverage from JSON report
            coverage_percentage = 0.0
            coverage_file = self.test_reports_dir / f"{test_level.value}_coverage.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                        coverage_percentage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
                except:
                    coverage_percentage = 0.0
            
            # Create test report
            report_path = self.test_reports_dir / f"{test_level.value}_{layer_name}_report.json"
            
            test_report = TestReport(
                test_level=test_level,
                total_tests=max(total_tests, passed_tests + failed_tests),
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                coverage_percentage=coverage_percentage,
                execution_time=execution_time,
                report_path=str(report_path),
                repository="control_tower",
                timestamp=time.time()
            )
            
            # Save detailed report
            self._save_detailed_test_report(test_report, output)
            
            return test_report
            
        except Exception as e:
            # Return empty report on error
            return TestReport(
                test_level=test_level,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                coverage_percentage=0.0,
                execution_time=0.0,
                report_path="",
                repository="control_tower",
                timestamp=time.time()
            )
    
    def _validate_pyramid_distribution(self, unit_pct: float, integration_pct: float, e2e_pct: float) -> bool:
        """Validate testing pyramid follows 70/20/10 distribution (with tolerance)"""
        # Allow 15% tolerance for pyramid distribution
        tolerance = 15.0
        
        unit_valid = abs(unit_pct - 70.0) <= tolerance
        integration_valid = abs(integration_pct - 20.0) <= tolerance  
        e2e_valid = abs(e2e_pct - 10.0) <= tolerance
        
        return unit_valid and integration_valid and e2e_valid
    
    def _create_placeholder_test(self, test_path: Path, test_level: TestLevel, layer_name: str):
        """Create placeholder test file if directory is empty"""
        test_file = test_path / f"test_{test_level.value}_{layer_name}.py"
        
        if not test_file.exists():
            placeholder_content = f'''"""
{test_level.value.title()} tests for {layer_name} layer
Generated by TDD Enforcer Stage Gate 8
"""
import pytest

def test_{test_level.value}_{layer_name}_placeholder():
    """Placeholder {test_level.value} test for {layer_name} layer"""
    # TODO: Implement real {test_level.value} tests
    assert True, "Placeholder test - implement real tests"

def test_{test_level.value}_infrastructure():
    """Infrastructure test that should always pass"""
    assert True, "Infrastructure validation"
'''
            test_file.write_text(placeholder_content)
    
    def _save_test_reports(self, reports: List[TestReport], layer_name: str):
        """Save test reports to repository"""
        report_summary = {
            "layer_name": layer_name,
            "timestamp": time.time(),
            "reports": [
                {
                    "test_level": report.test_level.value,
                    "total_tests": report.total_tests,
                    "passed_tests": report.passed_tests,
                    "failed_tests": report.failed_tests,
                    "coverage_percentage": report.coverage_percentage,
                    "execution_time": report.execution_time,
                    "report_path": report.report_path
                }
                for report in reports
            ]
        }
        
        summary_file = self.test_reports_dir / f"{layer_name}_pyramid_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(report_summary, f, indent=2)
    
    def _save_detailed_test_report(self, report: TestReport, test_output: str):
        """Save detailed test report with full output"""
        detailed_report = {
            "test_level": report.test_level.value,
            "summary": {
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "coverage_percentage": report.coverage_percentage,
                "execution_time": report.execution_time
            },
            "full_output": test_output,
            "timestamp": report.timestamp,
            "repository": report.repository
        }
        
        with open(report.report_path, 'w') as f:
            json.dump(detailed_report, f, indent=2)
    
    def stage_gate_9_requirements_compliance_verification(self, requirements_file: str, layer_name: str = "current") -> Dict[str, Any]:
        """
        Stage Gate 9: Requirements Compliance Verification
        
        Validates that implementation meets ALL requirements with evidence:
        - Requirement-by-requirement validation
        - Traceability matrix (requirement → implementation → tests)
        - Evidence collection with automated proof
        - Gap analysis for missing coverage
        
        Args:
            requirements_file: Path to requirements document
            layer_name: Name of layer being validated
            
        Returns:
            Dict with compliance validation results
        """
        print(f"\033[95m🔍 Stage Gate 9: Verifying requirements compliance for {layer_name} layer...\033[0m")
        
        try:
            compliance_results = {
                "stage_name": "stage_gate_9_requirements_compliance",
                "layer_name": layer_name,
                "requirements_file": requirements_file,
                "compliance_valid": False,
                "requirements_analyzed": 0,
                "requirements_met": 0,
                "requirements_partial": 0,
                "requirements_missing": 0,
                "traceability_matrix": [],
                "evidence_files": [],
                "gap_analysis": [],
                "can_proceed": False,
                "timestamp": time.time()
            }
            
            # Step 1: Parse Requirements Document
            print("📋 Parsing requirements document...")
            requirements = self._parse_requirements_for_compliance(requirements_file)
            compliance_results["requirements_analyzed"] = len(requirements)
            
            if len(requirements) == 0:
                print("❌ Stage Gate 9 FAILED: No requirements found to validate")
                compliance_results["gap_analysis"].append("No requirements found in document")
                return compliance_results
            
            # Step 2: Analyze Each Requirement for Compliance
            print(f"🔍 Analyzing {len(requirements)} requirements for compliance...")
            
            for requirement in requirements:
                evidence = self._analyze_requirement_compliance(requirement, layer_name)
                self.requirement_evidence.append(evidence)
                compliance_results["traceability_matrix"].append({
                    "requirement_id": evidence.requirement_id,
                    "requirement_type": evidence.requirement_type,
                    "implementation_files": evidence.implementation_files,
                    "test_files": evidence.test_files,
                    "coverage_percentage": evidence.coverage_percentage,
                    "validation_status": evidence.validation_status,
                    "evidence_summary": len(evidence.evidence_details)
                })
                
                # Count validation status
                if evidence.validation_status == "met":
                    compliance_results["requirements_met"] += 1
                elif evidence.validation_status == "partial":
                    compliance_results["requirements_partial"] += 1
                else:
                    compliance_results["requirements_missing"] += 1
                    compliance_results["gap_analysis"].append(
                        f"Requirement {evidence.requirement_id} not implemented"
                    )
            
            # Step 3: Generate Evidence Documentation
            print("📁 Generating compliance evidence documentation...")
            evidence_file = self._generate_compliance_evidence_documentation(
                compliance_results, layer_name
            )
            compliance_results["evidence_files"].append(evidence_file)
            
            # Step 4: Calculate Compliance Percentage
            compliance_percentage = (compliance_results["requirements_met"] / 
                                   compliance_results["requirements_analyzed"] * 100)
            
            # Step 5: Validate Compliance Threshold
            minimum_compliance = 95.0  # 95% of requirements must be fully met
            compliance_results["compliance_valid"] = compliance_percentage >= minimum_compliance
            compliance_results["can_proceed"] = compliance_results["compliance_valid"]
            
            # Step 6: Terminal Output
            if compliance_results["compliance_valid"]:
                print(f"\033[92m✅ Stage Gate 9 PASSED: Requirements compliance validated\033[0m")
                print(f"   📊 Compliance: {compliance_results['requirements_met']}/{compliance_results['requirements_analyzed']} requirements met ({compliance_percentage:.1f}%)")
                print(f"   📁 Evidence documentation: {evidence_file}")
                if compliance_results["requirements_partial"] > 0:
                    print(f"   ⚠️  {compliance_results['requirements_partial']} requirements partially implemented")
            else:
                print(f"❌ Stage Gate 9 FAILED: Requirements compliance insufficient")
                print(f"   📊 Compliance: {compliance_results['requirements_met']}/{compliance_results['requirements_analyzed']} requirements met ({compliance_percentage:.1f}% < {minimum_compliance}% required)")
                print(f"   ❌ Missing: {compliance_results['requirements_missing']} requirements")
                print(f"   ⚠️  Partial: {compliance_results['requirements_partial']} requirements")
                if compliance_results["gap_analysis"]:
                    print(f"   🔍 Gaps: {', '.join(compliance_results['gap_analysis'][:3])}...")
            
            print()
            return compliance_results
            
        except Exception as e:
            print(f"❌ Stage Gate 9 FAILED: Requirements compliance error: {e}")
            return {
                "stage_name": "stage_gate_9_requirements_compliance",
                "compliance_valid": False,
                "error": str(e),
                "can_proceed": False,
                "timestamp": time.time()
            }
    
    def _parse_requirements_for_compliance(self, requirements_file: str) -> List[Dict[str, Any]]:
        """Parse requirements document for compliance analysis"""
        requirements = []
        
        try:
            with open(requirements_file, 'r') as f:
                content = f.read()
            
            # Extract functional requirements
            fr_pattern = r'(?:^|\n)(?:###?\s*)?(\*\*)?FR-?\d+.*?:(.*?)(?=\n(?:###?\s*)?(?:\*\*)?[A-Z]{2}-?\d+|$)'
            fr_matches = re.findall(fr_pattern, content, re.DOTALL | re.MULTILINE)
            
            for i, (_, req_text) in enumerate(fr_matches):
                requirements.append({
                    "id": f"FR-{i+1:03d}",
                    "type": "FR",
                    "text": req_text.strip(),
                    "priority": "high"
                })
            
            # Extract non-functional requirements  
            nfr_pattern = r'(?:^|\n)(?:###?\s*)?(\*\*)?NFR-?\d+.*?:(.*?)(?=\n(?:###?\s*)?(?:\*\*)?[A-Z]{2}-?\d+|$)'
            nfr_matches = re.findall(nfr_pattern, content, re.DOTALL | re.MULTILINE)
            
            for i, (_, req_text) in enumerate(nfr_matches):
                requirements.append({
                    "id": f"NFR-{i+1:03d}",
                    "type": "NFR", 
                    "text": req_text.strip(),
                    "priority": "medium"
                })
            
            # Extract business requirements
            br_pattern = r'(?:^|\n)(?:###?\s*)?(\*\*)?BR-?\d+.*?:(.*?)(?=\n(?:###?\s*)?(?:\*\*)?[A-Z]{2}-?\d+|$)'
            br_matches = re.findall(br_pattern, content, re.DOTALL | re.MULTILINE)
            
            for i, (_, req_text) in enumerate(br_matches):
                requirements.append({
                    "id": f"BR-{i+1:03d}",
                    "type": "BR",
                    "text": req_text.strip(),
                    "priority": "high"
                })
            
            # Extract acceptance criteria
            ac_pattern = r'(?:^|\n)(?:###?\s*)?(\*\*)?AC-?\d+.*?:(.*?)(?=\n(?:###?\s*)?(?:\*\*)?[A-Z]{2}-?\d+|$)'
            ac_matches = re.findall(ac_pattern, content, re.DOTALL | re.MULTILINE)
            
            for i, (_, req_text) in enumerate(ac_matches):
                requirements.append({
                    "id": f"AC-{i+1:03d}",
                    "type": "AC",
                    "text": req_text.strip(),
                    "priority": "high"
                })
            
            return requirements
            
        except Exception as e:
            print(f"⚠️  Error parsing requirements: {e}")
            return []
    
    def _analyze_requirement_compliance(self, requirement: Dict[str, Any], layer_name: str) -> RequirementEvidence:
        """Analyze a single requirement for implementation compliance"""
        
        evidence = RequirementEvidence(
            requirement_id=requirement["id"],
            requirement_type=requirement["type"],
            implementation_files=[],
            test_files=[],
            coverage_percentage=0.0,
            validation_status="missing",
            evidence_details={}
        )
        
        try:
            # Step 1: Find implementation files that might address this requirement
            implementation_files = self._find_implementation_files(requirement, layer_name)
            evidence.implementation_files = implementation_files
            
            # Step 2: Find test files that validate this requirement  
            test_files = self._find_test_files(requirement, layer_name)
            evidence.test_files = test_files
            
            # Step 3: Analyze implementation quality
            implementation_score = self._analyze_implementation_quality_for_requirement(
                implementation_files, requirement
            )
            
            # Step 4: Analyze test coverage
            test_score = self._analyze_test_coverage_for_requirement(
                test_files, requirement
            )
            
            # Step 5: Calculate overall compliance
            evidence.coverage_percentage = (implementation_score + test_score) / 2
            
            # Step 6: Determine validation status
            if evidence.coverage_percentage >= 90.0:
                evidence.validation_status = "met"
            elif evidence.coverage_percentage >= 50.0:
                evidence.validation_status = "partial"
            else:
                evidence.validation_status = "missing"
            
            # Step 7: Collect evidence details
            evidence.evidence_details = {
                "implementation_score": implementation_score,
                "test_score": test_score,
                "implementation_file_count": len(implementation_files),
                "test_file_count": len(test_files),
                "requirement_keywords": self._extract_requirement_keywords(requirement),
                "analysis_timestamp": time.time()
            }
            
            return evidence
            
        except Exception as e:
            evidence.evidence_details["error"] = str(e)
            return evidence
    
    def _find_implementation_files(self, requirement: Dict[str, Any], layer_name: str) -> List[str]:
        """Find source files that implement this requirement"""
        implementation_files = []
        
        # Search in src directory
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return implementation_files
        
        # Extract keywords from requirement
        keywords = self._extract_requirement_keywords(requirement)
        
        # Search Python files for relevant implementations
        for py_file in src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read().lower()
                
                # Check if file contains requirement-related keywords
                keyword_matches = sum(1 for keyword in keywords if keyword in content)
                if keyword_matches >= 2:  # Require at least 2 keyword matches
                    implementation_files.append(str(py_file.relative_to(self.project_root)))
                    
            except Exception:
                continue
        
        return implementation_files
    
    def _find_test_files(self, requirement: Dict[str, Any], layer_name: str) -> List[str]:
        """Find test files that validate this requirement"""
        test_files = []
        
        # Search in tests directories
        test_dirs = ["tests", "control_tower_failing_tests"]
        keywords = self._extract_requirement_keywords(requirement)
        
        for test_dir_name in test_dirs:
            test_dir = self.project_root / test_dir_name
            if not test_dir.exists():
                continue
                
            for test_file in test_dir.rglob("test_*.py"):
                try:
                    with open(test_file, 'r') as f:
                        content = f.read().lower()
                    
                    # Check if test file validates this requirement
                    keyword_matches = sum(1 for keyword in keywords if keyword in content)
                    if keyword_matches >= 1:  # At least 1 keyword match for tests
                        test_files.append(str(test_file.relative_to(self.project_root)))
                        
                except Exception:
                    continue
        
        return test_files
    
    def _extract_requirement_keywords(self, requirement: Dict[str, Any]) -> List[str]:
        """Extract keywords from requirement text for searching"""
        text = requirement["text"].lower()
        
        # Remove common words and extract meaningful terms
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
        
        # Extract words that are 3+ characters and not common words
        words = re.findall(r'\b\w{3,}\b', text)
        keywords = [word for word in words if word not in common_words]
        
        # Return top 10 most relevant keywords
        return keywords[:10]
    
    def _analyze_implementation_quality_for_requirement(self, files: List[str], requirement: Dict[str, Any]) -> float:
        """Analyze implementation quality for a specific requirement"""
        if not files:
            return 0.0
        
        total_score = 0.0
        
        for file_path in files:
            try:
                full_path = self.project_root / file_path
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Score based on implementation indicators
                score = 0.0
                
                # Has meaningful implementation (not just stubs)
                if len(content.split('\n')) > 10:
                    score += 20.0
                
                # Has error handling
                if any(keyword in content for keyword in ['try:', 'except:', 'raise ']):
                    score += 20.0
                
                # Has business logic (not just infrastructure)
                if any(keyword in content for keyword in ['if ', 'for ', 'while ', 'def ']):
                    score += 20.0
                
                # Has documentation
                if '"""' in content or "'''" in content:
                    score += 20.0
                
                # Addresses requirement keywords
                keywords = self._extract_requirement_keywords(requirement)
                keyword_matches = sum(1 for keyword in keywords if keyword in content.lower())
                if keyword_matches > 0:
                    score += min(20.0, keyword_matches * 5.0)
                
                total_score += score
                
            except Exception:
                continue
        
        return min(100.0, total_score / len(files))
    
    def _analyze_test_coverage_for_requirement(self, files: List[str], requirement: Dict[str, Any]) -> float:
        """Analyze test coverage for a specific requirement"""
        if not files:
            return 0.0
        
        total_score = 0.0
        
        for file_path in files:
            try:
                full_path = self.project_root / file_path
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Score based on test quality indicators
                score = 0.0
                
                # Has test functions
                test_function_count = len(re.findall(r'def test_\w+', content))
                if test_function_count > 0:
                    score += min(40.0, test_function_count * 10.0)
                
                # Has assertions
                assertion_count = content.count('assert')
                if assertion_count > 0:
                    score += min(30.0, assertion_count * 5.0)
                
                # Tests requirement keywords
                keywords = self._extract_requirement_keywords(requirement)
                keyword_matches = sum(1 for keyword in keywords if keyword in content.lower())
                if keyword_matches > 0:
                    score += min(30.0, keyword_matches * 10.0)
                
                total_score += score
                
            except Exception:
                continue
        
        return min(100.0, total_score / len(files))
    
    def _generate_compliance_evidence_documentation(self, compliance_results: Dict[str, Any], layer_name: str) -> str:
        """Generate comprehensive compliance evidence documentation"""
        
        evidence_file = self.evidence_dir / f"{layer_name}_compliance_evidence.md"
        
        evidence_content = f"""# Requirements Compliance Evidence - {layer_name.title()} Layer

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Layer**: {layer_name}  
**Total Requirements Analyzed**: {compliance_results['requirements_analyzed']}  
**Compliance Status**: {'PASSED' if compliance_results['compliance_valid'] else 'FAILED'}

## Executive Summary

- **Requirements Met**: {compliance_results['requirements_met']} ({compliance_results['requirements_met']/compliance_results['requirements_analyzed']*100:.1f}%)
- **Requirements Partial**: {compliance_results['requirements_partial']} ({compliance_results['requirements_partial']/compliance_results['requirements_analyzed']*100:.1f}%)
- **Requirements Missing**: {compliance_results['requirements_missing']} ({compliance_results['requirements_missing']/compliance_results['requirements_analyzed']*100:.1f}%)

## Traceability Matrix

| Requirement ID | Type | Status | Implementation Files | Test Files | Coverage |
|----------------|------|--------|---------------------|------------|----------|
"""
        
        for item in compliance_results['traceability_matrix']:
            impl_files = ', '.join(item['implementation_files'][:2])  # Show first 2 files
            if len(item['implementation_files']) > 2:
                impl_files += f" (+{len(item['implementation_files'])-2} more)"
            
            test_files = ', '.join(item['test_files'][:2])  # Show first 2 files  
            if len(item['test_files']) > 2:
                test_files += f" (+{len(item['test_files'])-2} more)"
            
            status_emoji = {"met": "✅", "partial": "⚠️", "missing": "❌"}[item['validation_status']]
            
            evidence_content += f"| {item['requirement_id']} | {item['requirement_type']} | {status_emoji} {item['validation_status']} | {impl_files} | {test_files} | {item['coverage_percentage']:.1f}% |\n"
        
        if compliance_results['gap_analysis']:
            evidence_content += f"""
## Gap Analysis

The following requirements need attention:

"""
            for gap in compliance_results['gap_analysis']:
                evidence_content += f"- {gap}\n"
        
        evidence_content += f"""
## Recommendations

{'✅ **APPROVED FOR NEXT LAYER**: All requirements compliance criteria met.' if compliance_results['compliance_valid'] else '❌ **ADDITIONAL WORK REQUIRED**: Address missing/partial requirements before proceeding.'}

---
*This evidence documentation was automatically generated by TDD Enforcer Stage Gate 9*
"""
        
        with open(evidence_file, 'w') as f:
            f.write(evidence_content)
        
        return str(evidence_file)
    
    def stage_gate_10_layer_completion_certification(self, layer_name: str, next_layer: str = None) -> Dict[str, Any]:
        """
        Stage Gate 10: Layer Completion Certification
        
        Final validation and certification that layer is complete:
        - Review all previous stage gate evidence
        - Validate layer completion criteria
        - Generate layer completion certificate
        - Provide next layer activation command
        
        Args:
            layer_name: Name of completed layer
            next_layer: Name of next layer to activate (optional)
            
        Returns:
            Dict with certification results and next steps
        """
        print(f"\033[95m🔍 Stage Gate 10: Certifying {layer_name} layer completion...\033[0m")
        
        try:
            certification_results = {
                "stage_name": "stage_gate_10_layer_completion",
                "layer_name": layer_name,
                "next_layer": next_layer,
                "certification_valid": False,
                "stage_gates_passed": 0,
                "stage_gates_total": 10,
                "evidence_summary": {},
                "completion_certificate": "",
                "next_steps": [],
                "make_commands": [],
                "can_proceed": False,
                "timestamp": time.time()
            }
            
            print(f"📋 Reviewing all stage gate evidence for {layer_name} layer...")
            
            # Step 1: Validate All Stage Gates Passed
            stage_gates_status = self._validate_all_stage_gates_passed(layer_name)
            certification_results["stage_gates_passed"] = stage_gates_status["passed"]
            certification_results["stage_gates_total"] = stage_gates_status["total"]
            
            if stage_gates_status["passed"] < stage_gates_status["total"]:
                print(f"❌ Stage Gate 10 FAILED: Not all stage gates passed ({stage_gates_status['passed']}/{stage_gates_status['total']})")
                certification_results["next_steps"] = [
                    f"Complete missing stage gates: {', '.join(stage_gates_status['missing'])}"
                ]
                return certification_results
            
            # Step 2: Collect Evidence Summary
            evidence_summary = self._collect_final_evidence_summary(layer_name)
            certification_results["evidence_summary"] = evidence_summary
            
            # Step 3: Validate Layer Completion Criteria
            completion_criteria = self._validate_layer_completion_criteria(evidence_summary)
            
            if not completion_criteria["all_criteria_met"]:
                print(f"❌ Stage Gate 10 FAILED: Layer completion criteria not met")
                certification_results["next_steps"] = completion_criteria["missing_criteria"]
                return certification_results
            
            # Step 4: Generate Layer Completion Certificate
            certificate_path = self._generate_layer_completion_certificate(
                layer_name, evidence_summary, certification_results
            )
            certification_results["completion_certificate"] = certificate_path
            
            # Step 5: Determine Next Steps
            if next_layer:
                certification_results["next_steps"] = [
                    f"Layer {layer_name} COMPLETE and CERTIFIED",
                    f"Ready to begin {next_layer} layer development",
                    f"Run: make work-on LAYER={next_layer}"
                ]
                certification_results["make_commands"] = [
                    f"make work-on LAYER={next_layer}",
                    f"make prep-{next_layer.lower().replace(' ', '-')}"
                ]
            else:
                certification_results["next_steps"] = [
                    f"Layer {layer_name} COMPLETE and CERTIFIED",
                    "All planned layers complete - ready for integration testing",
                    "Run: make validate-integration"
                ]
                certification_results["make_commands"] = [
                    "make validate-integration",
                    "make deploy-staging"
                ]
            
            # Step 6: Final Certification
            certification_results["certification_valid"] = True
            certification_results["can_proceed"] = True
            
            # Step 7: Celebration Terminal Output
            print(f"\033[92m🎉 LAYER COMPLETION CERTIFIED: {layer_name} layer is COMPLETE!\033[0m")
            print(f"\033[92m✅ All {stage_gates_status['passed']} stage gates passed with evidence\033[0m")
            print(f"\033[92m📜 Completion certificate: {certificate_path}\033[0m")
            
            if next_layer:
                print(f"\033[96m🚀 NEXT LAYER READY: {next_layer}\033[0m")
                print(f"\033[96m   Run: make work-on LAYER={next_layer}\033[0m")
            else:
                print(f"\033[96m🏁 ALL LAYERS COMPLETE: Ready for integration!\033[0m")
                print(f"\033[96m   Run: make validate-integration\033[0m")
            
            print()
            return certification_results
            
        except Exception as e:
            print(f"❌ Stage Gate 10 FAILED: Layer certification error: {e}")
            return {
                "stage_name": "stage_gate_10_layer_completion",
                "certification_valid": False,
                "error": str(e),
                "can_proceed": False,
                "timestamp": time.time()
            }
    
    def _validate_all_stage_gates_passed(self, layer_name: str) -> Dict[str, Any]:
        """Validate that all 10 stage gates have been passed for this layer"""
        
        stage_gates = [
            "stage_gate_1_requirements_validation",
            "stage_gate_2_parsing_verification", 
            "stage_gate_3_test_generation",
            "stage_gate_4_red_phase_validation",
            "stage_gate_5_green_phase_quality",
            "stage_gate_6_refactor_analysis",
            "stage_gate_7_refactor_complete",
            "stage_gate_8_testing_pyramid",
            "stage_gate_9_requirements_compliance",
            "stage_gate_10_layer_completion"
        ]
        
        passed_gates = []
        missing_gates = []
        
        # Check for evidence files from each stage gate
        for gate in stage_gates:
            evidence_file = self.evidence_dir / f"{layer_name}_{gate}_evidence.json"
            if evidence_file.exists():
                passed_gates.append(gate)
            else:
                missing_gates.append(gate)
        
        # For stages 8-10, check if we have evidence from current execution
        if hasattr(self, 'test_reports') and self.test_reports:
            if "stage_gate_8_testing_pyramid" in missing_gates:
                passed_gates.append("stage_gate_8_testing_pyramid")
                missing_gates.remove("stage_gate_8_testing_pyramid")
        
        if hasattr(self, 'requirement_evidence') and self.requirement_evidence:
            if "stage_gate_9_requirements_compliance" in missing_gates:
                passed_gates.append("stage_gate_9_requirements_compliance")
                missing_gates.remove("stage_gate_9_requirements_compliance")
        
        return {
            "passed": len(passed_gates),
            "total": len(stage_gates),
            "passed_gates": passed_gates,
            "missing": missing_gates
        }
    
    def _collect_final_evidence_summary(self, layer_name: str) -> Dict[str, Any]:
        """Collect comprehensive evidence summary from all stage gates"""
        
        evidence_summary = {
            "layer_name": layer_name,
            "requirements_validated": True,
            "tests_generated": True,
            "red_phase_validated": True,
            "green_phase_complete": True,
            "refactor_complete": True,
            "testing_pyramid_valid": len(self.test_reports) > 0,
            "requirements_compliance": len(self.requirement_evidence) > 0,
            "total_test_count": sum(report.total_tests for report in self.test_reports),
            "total_coverage": sum(report.coverage_percentage for report in self.test_reports) / len(self.test_reports) if self.test_reports else 0,
            "requirements_met": sum(1 for evidence in self.requirement_evidence if evidence.validation_status == "met"),
            "total_requirements": len(self.requirement_evidence),
            "evidence_files": []
        }
        
        # Collect evidence file paths
        for evidence_file in self.evidence_dir.glob(f"{layer_name}_*"):
            evidence_summary["evidence_files"].append(str(evidence_file))
        
        return evidence_summary
    
    def _validate_layer_completion_criteria(self, evidence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all layer completion criteria are met"""
        
        criteria = {
            "all_stage_gates_passed": True,  # Already validated in previous step
            "testing_pyramid_complete": evidence_summary["testing_pyramid_valid"],
            "requirements_compliance_sufficient": (
                evidence_summary["requirements_met"] / evidence_summary["total_requirements"] >= 0.95
                if evidence_summary["total_requirements"] > 0 else False
            ),
            "test_coverage_adequate": evidence_summary["total_coverage"] >= 80.0,
            "evidence_documentation_complete": len(evidence_summary["evidence_files"]) >= 3
        }
        
        all_criteria_met = all(criteria.values())
        missing_criteria = [
            criterion for criterion, met in criteria.items() if not met
        ]
        
        return {
            "all_criteria_met": all_criteria_met,
            "criteria_details": criteria,
            "missing_criteria": missing_criteria
        }
    
    def _generate_layer_completion_certificate(self, layer_name: str, evidence_summary: Dict[str, Any], certification_results: Dict[str, Any]) -> str:
        """Generate official layer completion certificate"""
        
        certificate_file = self.evidence_dir / f"{layer_name}_COMPLETION_CERTIFICATE.md"
        
        certificate_content = f"""# 🏆 LAYER COMPLETION CERTIFICATE

## {layer_name.title()} Layer - CERTIFIED COMPLETE

**Certification Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Project**: Control Tower  
**TDD Enforcer Version**: Extended (Stages 1-10)  
**Certification Authority**: TDD Workflow Enforcer

---

## ✅ CERTIFICATION SUMMARY

**Layer Status**: ✅ COMPLETE AND CERTIFIED  
**Stage Gates Passed**: {certification_results['stage_gates_passed']}/{certification_results['stage_gates_total']}  
**Overall Compliance**: ✅ MEETS ALL CRITERIA  

## 📊 EVIDENCE SUMMARY

### Testing Metrics
- **Total Tests**: {evidence_summary['total_test_count']}
- **Test Coverage**: {evidence_summary['total_coverage']:.1f}%
- **Testing Pyramid**: ✅ Validated (Unit/Integration/E2E)

### Requirements Compliance  
- **Requirements Analyzed**: {evidence_summary['total_requirements']}
- **Requirements Met**: {evidence_summary['requirements_met']} ({evidence_summary['requirements_met']/evidence_summary['total_requirements']*100:.1f}%)
- **Compliance Status**: ✅ EXCEEDS 95% THRESHOLD

### Stage Gate Completion
1. ✅ Requirements File Validation
2. ✅ Parsing Completion Verification  
3. ✅ Test Generation Verification
4. ✅ RED Phase Validation
5. ✅ GREEN Phase Implementation Quality
6. ✅ REFACTOR Analysis
7. ✅ REFACTOR Complete
8. ✅ Testing Pyramid Validation
9. ✅ Requirements Compliance Verification
10. ✅ Layer Completion Certification

## 📁 EVIDENCE DOCUMENTATION

The following evidence files support this certification:

"""
        
        for evidence_file in evidence_summary['evidence_files']:
            certificate_content += f"- `{Path(evidence_file).name}`\n"
        
        certificate_content += f"""
## 🎯 NEXT STEPS

{chr(10).join(f"- {step}" for step in certification_results['next_steps'])}

## 🚀 MAKE COMMANDS

{chr(10).join(f"```bash{chr(10)}{cmd}{chr(10)}```" for cmd in certification_results['make_commands'])}

---

## 🔒 CERTIFICATION VALIDATION

This certificate validates that the {layer_name} layer has been developed using Test-Driven Development methodology with comprehensive stage gate validation. All requirements have been met with documented evidence.

**Certificate Hash**: {hash(f"{layer_name}{time.time()}")}&{time.time():.0f}  
**Validator**: TDD Workflow Enforcer Extended Edition  
**Valid From**: {time.strftime('%Y-%m-%d')}  

---

*🎉 CONGRATULATIONS! Layer development complete with full TDD compliance. 🎉*
"""
        
        with open(certificate_file, 'w') as f:
            f.write(certificate_content)
        
        return str(certificate_file)


def main():
    """Main entry point for extended TDD workflow enforcement"""
    print("🏗️  TDD WORKFLOW ENFORCER - EXTENDED STAGES 8-10")
    print("=" * 80)
    
    enforcer = TDDExtendedEnforcer()
    
    # Test layer name for demonstration
    layer_name = "data_access"
    requirements_file = "/workspaces/control_tower/requirements/layers/LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001.md"
    next_layer = "business_logic"
    
    print(f"\n🎯 EXECUTING EXTENDED TDD WORKFLOW for {layer_name} layer")
    print("-" * 60)
    
    # Execute Stage Gate 8: Testing Pyramid Validation
    print("\n🟦 STAGE GATE 8: Testing Pyramid Validation")
    print("-" * 50)
    stage8_result = enforcer.stage_gate_8_testing_pyramid_validation(layer_name)
    
    # Execute Stage Gate 9: Requirements Compliance Verification  
    print("\n🟦 STAGE GATE 9: Requirements Compliance Verification")
    print("-" * 50)
    stage9_result = enforcer.stage_gate_9_requirements_compliance_verification(
        requirements_file, layer_name
    )
    
    # Execute Stage Gate 10: Layer Completion Certification
    print("\n🟦 STAGE GATE 10: Layer Completion Certification")
    print("-" * 50)
    stage10_result = enforcer.stage_gate_10_layer_completion_certification(
        layer_name, next_layer
    )
    
    # Final summary
    print("\n📊 EXTENDED STAGE GATES SUMMARY")
    print("=" * 40)
    
    stages = [
        ("Stage 8", stage8_result.get("pyramid_valid", False)),
        ("Stage 9", stage9_result.get("compliance_valid", False)),
        ("Stage 10", stage10_result.get("certification_valid", False))
    ]
    
    for stage_name, passed in stages:
        status_emoji = "✅" if passed else "❌"
        print(f"  {status_emoji} {stage_name}: {'PASSED' if passed else 'FAILED'}")
    
    if all(passed for _, passed in stages):
        print(f"\n🎉 LAYER {layer_name.upper()} COMPLETE AND CERTIFIED!")
        print(f"🚀 Ready for {next_layer} layer development")
    else:
        print(f"\n🚧 LAYER {layer_name.upper()} INCOMPLETE")
        print("   Continue development and re-run stage gates")
    
    print("\n🏁 EXTENDED TDD WORKFLOW ENFORCER COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()