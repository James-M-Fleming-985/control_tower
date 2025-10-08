#!/usr/bin/env python3
"""
Layer-Level Test Runner and Verification Script

Executes tests for a specific layer, validates against acceptance criteria,
checks coverage thresholds, and generates verification reports.

Usage:
    python run_layer_tests.py --layer LAYER-003-03-01-01
    python run_layer_tests.py --layer LAYER-003-03-02-01 --phase red
    python run_layer_tests.py --layer LAYER-003-03-01-01 --update-verification
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


class LayerTestRunner:
    """Runs tests for a specific layer and validates against requirements."""
    
    def __init__(self, layer_id: str, system_root: Path):
        self.layer_id = layer_id
        self.system_root = system_root
        self.layer_path = self._find_layer_path()
        self.layer_yaml = self._load_layer_yaml()
        self.test_results = {}
        
    def _find_layer_path(self) -> Path:
        """Find the layer folder based on layer ID."""
        # Search for layer YAML file
        for yaml_file in self.system_root.rglob(f"{self.layer_id}_*.yaml"):
            if "requirements_verification" not in str(yaml_file):
                return yaml_file.parent
        raise FileNotFoundError(f"Layer {self.layer_id} not found in {self.system_root}")
    
    def _load_layer_yaml(self) -> dict:
        """Load layer requirements YAML."""
        yaml_file = self.layer_path / f"{self.layer_id}_{self.layer_path.name.lower().replace(' ', '_')}.yaml"
        if not yaml_file.exists():
            # Try finding any YAML in the layer folder
            yaml_files = list(self.layer_path.glob(f"{self.layer_id}_*.yaml"))
            if not yaml_files:
                raise FileNotFoundError(f"No YAML file found for {self.layer_id}")
            yaml_file = yaml_files[0]
        
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    def get_test_requirements(self) -> Dict:
        """Extract test requirements from layer YAML."""
        return self.layer_yaml.get('testing_requirements', {})
    
    def get_acceptance_criteria(self) -> List[Dict]:
        """Extract acceptance criteria from layer YAML."""
        return self.layer_yaml.get('acceptance_criteria', [])
    
    def run_unit_tests(self, verbose: bool = False) -> Tuple[bool, Dict]:
        """Run unit tests for this layer."""
        print(f"\n{'='*70}")
        print(f"Running Unit Tests for {self.layer_id}")
        print(f"{'='*70}")
        
        test_req = self.get_test_requirements()
        unit_req = test_req.get('unit_tests', {})
        
        if not unit_req.get('required', True):
            print("⚠️  Unit tests not required for this layer")
            return True, {'status': 'skipped', 'reason': 'not_required'}
        
        # Build pytest command
        test_paths = self._get_test_paths('unit')
        coverage_threshold = unit_req.get('coverage_threshold', 0.90)
        min_tests = unit_req.get('minimum_count', 0)
        
        if not test_paths:
            print(f"❌ No unit test files found for {self.layer_id}")
            return False, {'status': 'failed', 'reason': 'no_tests_found'}
        
        # Run pytest with coverage
        cmd = [
            'pytest',
            *test_paths,
            '--verbose' if verbose else '--quiet',
            '--tb=short',
            f'--cov=src',  # Adjust based on your structure
            '--cov-report=term-missing',
            '--cov-report=html',
            '--cov-report=json',
            f'--junitxml={self.layer_path}/Testing Outputs/unit_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
        ]
        
        print(f"Command: {' '.join(str(c) for c in cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.system_root.parent.parent.parent  # Go to project root
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Parse coverage from output or JSON
            coverage_data = self._parse_coverage()
            test_count = self._count_tests_from_output(result.stdout)
            
            success = (
                result.returncode == 0 and
                coverage_data.get('coverage', 0) >= coverage_threshold and
                test_count >= min_tests
            )
            
            results = {
                'status': 'passed' if success else 'failed',
                'test_count': test_count,
                'tests_passed': self._count_passed_tests(result.stdout),
                'tests_failed': self._count_failed_tests(result.stdout),
                'coverage': coverage_data.get('coverage', 0),
                'coverage_threshold': coverage_threshold,
                'minimum_tests': min_tests,
                'returncode': result.returncode
            }
            
            self.test_results['unit_tests'] = results
            
            if success:
                print(f"\n✅ Unit tests PASSED")
                print(f"   Tests: {test_count} (required: {min_tests})")
                print(f"   Coverage: {coverage_data.get('coverage', 0):.1%} (required: {coverage_threshold:.1%})")
            else:
                print(f"\n❌ Unit tests FAILED")
                if test_count < min_tests:
                    print(f"   ⚠️  Insufficient tests: {test_count} < {min_tests}")
                if coverage_data.get('coverage', 0) < coverage_threshold:
                    print(f"   ⚠️  Insufficient coverage: {coverage_data.get('coverage', 0):.1%} < {coverage_threshold:.1%}")
            
            return success, results
            
        except Exception as e:
            print(f"❌ Error running unit tests: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def run_integration_tests(self, verbose: bool = False) -> Tuple[bool, Dict]:
        """Run integration tests for this layer."""
        print(f"\n{'='*70}")
        print(f"Running Integration Tests for {self.layer_id}")
        print(f"{'='*70}")
        
        test_req = self.get_test_requirements()
        integration_req = test_req.get('integration_tests', {})
        
        if not integration_req.get('required', True):
            print("⚠️  Integration tests not required for this layer")
            return True, {'status': 'skipped', 'reason': 'not_required'}
        
        test_paths = self._get_test_paths('integration')
        coverage_threshold = integration_req.get('coverage_threshold', 0.80)
        min_tests = integration_req.get('minimum_count', 0)
        
        if not test_paths:
            print(f"❌ No integration test files found for {self.layer_id}")
            return False, {'status': 'failed', 'reason': 'no_tests_found'}
        
        # Run pytest with coverage
        cmd = [
            'pytest',
            *test_paths,
            '--verbose' if verbose else '--quiet',
            '--tb=short',
            '-m', 'integration',  # Mark integration tests
            f'--junitxml={self.layer_path}/Testing Outputs/integration_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
        ]
        
        print(f"Command: {' '.join(str(c) for c in cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.system_root.parent.parent.parent
            )
            
            print(result.stdout)
            
            test_count = self._count_tests_from_output(result.stdout)
            
            success = (
                result.returncode == 0 and
                test_count >= min_tests
            )
            
            results = {
                'status': 'passed' if success else 'failed',
                'test_count': test_count,
                'tests_passed': self._count_passed_tests(result.stdout),
                'tests_failed': self._count_failed_tests(result.stdout),
                'minimum_tests': min_tests,
                'returncode': result.returncode
            }
            
            self.test_results['integration_tests'] = results
            
            if success:
                print(f"\n✅ Integration tests PASSED")
                print(f"   Tests: {test_count} (required: {min_tests})")
            else:
                print(f"\n❌ Integration tests FAILED")
            
            return success, results
            
        except Exception as e:
            print(f"❌ Error running integration tests: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def verify_acceptance_criteria(self) -> Dict:
        """Verify all acceptance criteria have tests and implementations."""
        print(f"\n{'='*70}")
        print(f"Verifying Acceptance Criteria for {self.layer_id}")
        print(f"{'='*70}")
        
        criteria = self.get_acceptance_criteria()
        verification = {
            'total_criteria': len(criteria),
            'implemented': 0,
            'in_progress': 0,
            'not_implemented': 0,
            'criteria_status': []
        }
        
        for criterion in criteria:
            criterion_id = criterion.get('criterion', 'Unknown').split(':')[0]
            status = criterion.get('status', 'not_implemented')
            test_file = criterion.get('test_file', 'Unknown')
            
            # Check if test file exists
            test_exists = self._test_file_exists(test_file)
            
            criterion_result = {
                'criterion': criterion_id,
                'description': criterion.get('criterion', ''),
                'status': status,
                'test_file': test_file,
                'test_exists': test_exists,
                'verified': status == 'implemented' and test_exists
            }
            
            verification['criteria_status'].append(criterion_result)
            
            if status == 'implemented':
                verification['implemented'] += 1
            elif status == 'in_progress':
                verification['in_progress'] += 1
            else:
                verification['not_implemented'] += 1
            
            # Print status
            status_icon = '✅' if criterion_result['verified'] else '⚠️' if status == 'in_progress' else '❌'
            print(f"{status_icon} {criterion_id}: {status} (test: {'exists' if test_exists else 'missing'})")
        
        verification['compliance'] = verification['implemented'] / verification['total_criteria'] if verification['total_criteria'] > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"Acceptance Criteria Summary:")
        print(f"  Implemented: {verification['implemented']}/{verification['total_criteria']}")
        print(f"  In Progress: {verification['in_progress']}/{verification['total_criteria']}")
        print(f"  Not Implemented: {verification['not_implemented']}/{verification['total_criteria']}")
        print(f"  Compliance: {verification['compliance']:.1%}")
        print(f"{'='*70}")
        
        return verification
    
    def _get_test_paths(self, test_type: str) -> List[str]:
        """Get paths to test files for this layer."""
        # Look in implementations section
        implementations = self.layer_yaml.get('implementations', {})
        test_files = []
        
        # Check red_phase for test files
        red_phase = implementations.get('red_phase', {})
        if 'test_files' in red_phase:
            for test_file_info in red_phase['test_files']:
                if isinstance(test_file_info, dict):
                    path = test_file_info.get('path', '')
                else:
                    path = str(test_file_info)
                
                if test_type in path or test_type == 'unit':
                    test_files.append(path)
        
        # Also check acceptance_criteria for test files
        for criterion in self.get_acceptance_criteria():
            test_file = criterion.get('test_file', '')
            if test_file and (test_type in test_file or test_type == 'unit'):
                test_files.append(test_file)
        
        return list(set(test_files))  # Remove duplicates
    
    def _test_file_exists(self, test_file: str) -> bool:
        """Check if a test file exists."""
        if not test_file or test_file == 'Unknown':
            return False
        
        # Try relative to project root
        test_path = self.system_root.parent.parent.parent / test_file
        return test_path.exists()
    
    def _parse_coverage(self) -> Dict:
        """Parse coverage data from coverage.json."""
        coverage_file = self.system_root.parent.parent.parent / 'coverage.json'
        if coverage_file.exists():
            with open(coverage_file, 'r') as f:
                data = json.load(f)
                return {'coverage': data.get('totals', {}).get('percent_covered', 0) / 100}
        return {'coverage': 0}
    
    def _count_tests_from_output(self, output: str) -> int:
        """Count tests from pytest output."""
        # Look for "X passed" pattern
        import re
        match = re.search(r'(\d+) passed', output)
        if match:
            return int(match.group(1))
        return 0
    
    def _count_passed_tests(self, output: str) -> int:
        """Count passed tests."""
        import re
        match = re.search(r'(\d+) passed', output)
        return int(match.group(1)) if match else 0
    
    def _count_failed_tests(self, output: str) -> int:
        """Count failed tests."""
        import re
        match = re.search(r'(\d+) failed', output)
        return int(match.group(1)) if match else 0
    
    def update_verification_yaml(self, verification_results: Dict):
        """Update the requirements verification YAML with test results."""
        verification_path = self.layer_path / "Requirements Verification" / "requirements_verification_template.yaml"
        
        if not verification_path.exists():
            print(f"⚠️  Verification template not found at {verification_path}")
            return
        
        with open(verification_path, 'r') as f:
            verification_yaml = yaml.safe_load(f)
        
        # Update verification_results section
        verification_yaml['verification_results'] = {
            'unit_tests': {
                'total_tests': self.test_results.get('unit_tests', {}).get('test_count', 0),
                'tests_passing': self.test_results.get('unit_tests', {}).get('tests_passed', 0),
                'tests_failing': self.test_results.get('unit_tests', {}).get('tests_failed', 0),
                'coverage_actual': self.test_results.get('unit_tests', {}).get('coverage', 0),
                'coverage_required': self.test_results.get('unit_tests', {}).get('coverage_threshold', 0.90),
                'status': self.test_results.get('unit_tests', {}).get('status', 'not_started')
            },
            'integration_tests': {
                'total_tests': self.test_results.get('integration_tests', {}).get('test_count', 0),
                'tests_passing': self.test_results.get('integration_tests', {}).get('tests_passed', 0),
                'tests_failing': self.test_results.get('integration_tests', {}).get('tests_failed', 0),
                'coverage_actual': 0,  # Integration coverage not always measured separately
                'coverage_required': self.get_test_requirements().get('integration_tests', {}).get('coverage_threshold', 0.80),
                'status': self.test_results.get('integration_tests', {}).get('status', 'not_started')
            },
            'acceptance_criteria_status': {
                criterion['criterion']: 'met' if criterion['verified'] else 'not_met'
                for criterion in verification_results['criteria_status']
            },
            'overall_compliance': verification_results['compliance'],
            'last_updated': datetime.now().isoformat()
        }
        
        # Update verification_status
        if verification_results['compliance'] == 1.0:
            verification_yaml['verification_status'] = 'complete'
        elif verification_results['compliance'] > 0:
            verification_yaml['verification_status'] = 'in_progress'
        else:
            verification_yaml['verification_status'] = 'pending'
        
        # Save updated YAML
        with open(verification_path, 'w') as f:
            yaml.dump(verification_yaml, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n✅ Updated verification YAML: {verification_path}")
    
    def generate_report(self, verification_results: Dict) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"LAYER TEST REPORT: {self.layer_id}")
        report.append(f"{'='*70}")
        report.append(f"Layer: {self.layer_yaml['metadata']['requirement_name']}")
        report.append(f"Feature: {self.layer_yaml['metadata']['parent_feature']}")
        report.append(f"Status: {self.layer_yaml['metadata']['status']}")
        report.append(f"Progress: {self.layer_yaml['metadata']['progress_percentage']}%")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Test Results Summary
        report.append("TEST RESULTS SUMMARY")
        report.append("-" * 70)
        
        if 'unit_tests' in self.test_results:
            ut = self.test_results['unit_tests']
            report.append(f"Unit Tests:")
            report.append(f"  Status: {ut.get('status', 'unknown').upper()}")
            report.append(f"  Tests Run: {ut.get('test_count', 0)} (required: {ut.get('minimum_tests', 0)})")
            report.append(f"  Passed: {ut.get('tests_passed', 0)}")
            report.append(f"  Failed: {ut.get('tests_failed', 0)}")
            report.append(f"  Coverage: {ut.get('coverage', 0):.1%} (required: {ut.get('coverage_threshold', 0):.1%})")
            report.append("")
        
        if 'integration_tests' in self.test_results:
            it = self.test_results['integration_tests']
            report.append(f"Integration Tests:")
            report.append(f"  Status: {it.get('status', 'unknown').upper()}")
            report.append(f"  Tests Run: {it.get('test_count', 0)} (required: {it.get('minimum_tests', 0)})")
            report.append(f"  Passed: {it.get('tests_passed', 0)}")
            report.append(f"  Failed: {it.get('tests_failed', 0)}")
            report.append("")
        
        # Acceptance Criteria
        report.append("ACCEPTANCE CRITERIA VERIFICATION")
        report.append("-" * 70)
        for criterion in verification_results['criteria_status']:
            icon = '✅' if criterion['verified'] else '⚠️' if criterion['status'] == 'in_progress' else '❌'
            report.append(f"{icon} {criterion['criterion']}")
            report.append(f"   Status: {criterion['status']}")
            report.append(f"   Test File: {criterion['test_file']}")
            report.append(f"   Test Exists: {criterion['test_exists']}")
            report.append("")
        
        report.append(f"Overall Compliance: {verification_results['compliance']:.1%}")
        report.append(f"{'='*70}\n")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='Run tests for a specific layer')
    parser.add_argument('--layer', required=True, help='Layer ID (e.g., LAYER-003-03-01-01)')
    parser.add_argument('--phase', choices=['red', 'green', 'refactor', 'all'], default='all',
                       help='TDD phase to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--update-verification', action='store_true',
                       help='Update requirements verification YAML with results')
    parser.add_argument('--system-root', type=Path,
                       default=Path(__file__).parent.parent,
                       help='Path to SYSTEM-003-03 root directory')
    
    args = parser.parse_args()
    
    try:
        runner = LayerTestRunner(args.layer, args.system_root)
        
        print(f"\n{'#'*70}")
        print(f"# LAYER TEST RUNNER")
        print(f"# Layer: {args.layer}")
        print(f"# Phase: {args.phase}")
        print(f"{'#'*70}\n")
        
        # Run tests based on phase
        all_passed = True
        
        if args.phase in ['red', 'green', 'refactor', 'all']:
            unit_passed, unit_results = runner.run_unit_tests(verbose=args.verbose)
            all_passed = all_passed and unit_passed
        
        if args.phase in ['green', 'refactor', 'all']:
            integration_passed, integration_results = runner.run_integration_tests(verbose=args.verbose)
            all_passed = all_passed and integration_passed
        
        # Verify acceptance criteria
        verification_results = runner.verify_acceptance_criteria()
        
        # Generate report
        report = runner.generate_report(verification_results)
        print(report)
        
        # Update verification YAML if requested
        if args.update_verification:
            runner.update_verification_yaml(verification_results)
        
        # Save report to Testing Outputs
        report_path = runner.layer_path / "Testing Outputs" / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_path}")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed and verification_results['compliance'] >= 0.5 else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
