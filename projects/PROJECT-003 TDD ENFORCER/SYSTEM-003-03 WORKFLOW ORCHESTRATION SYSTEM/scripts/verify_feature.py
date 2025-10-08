#!/usr/bin/env python3
"""
Feature-Level Verification Script

Runs all layer tests for a feature, validates layer integration,
runs feature-level e2e tests, and generates feature verification report.

Usage:
    python verify_feature.py --feature FEATURE-003-03-01
    python verify_feature.py --feature FEATURE-003-03-02 --verbose
    python verify_feature.py --feature FEATURE-003-03-01 --update-yaml
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class FeatureVerifier:
    """Verifies a complete feature by testing all its layers and integration."""
    
    def __init__(self, feature_id: str, system_root: Path):
        self.feature_id = feature_id
        self.system_root = system_root
        self.feature_path = self._find_feature_path()
        self.feature_yaml = self._load_feature_yaml()
        self.layer_results = {}
        self.feature_test_results = {}
        
    def _find_feature_path(self) -> Path:
        """Find the feature folder based on feature ID."""
        for yaml_file in self.system_root.rglob(f"{self.feature_id}_*.yaml"):
            # Skip layer YAMLs and verification templates
            if "LAYER-" not in str(yaml_file) and "requirements_verification" not in str(yaml_file):
                return yaml_file.parent
        raise FileNotFoundError(f"Feature {self.feature_id} not found in {self.system_root}")
    
    def _load_feature_yaml(self) -> dict:
        """Load feature requirements YAML."""
        yaml_files = list(self.feature_path.glob(f"{self.feature_id}_*.yaml"))
        if not yaml_files:
            raise FileNotFoundError(f"No YAML file found for {self.feature_id}")
        
        with open(yaml_files[0], 'r') as f:
            return yaml.safe_load(f)
    
    def get_layers(self) -> List[str]:
        """Get all layer IDs for this feature."""
        layers = []
        for layer_folder in self.feature_path.iterdir():
            if layer_folder.is_dir() and layer_folder.name.startswith("LAYER-"):
                # Extract layer ID from folder name
                layer_id = layer_folder.name.split()[0]
                layers.append(layer_id)
        return sorted(layers)
    
    def run_layer_tests(self, layer_id: str, verbose: bool = False) -> Tuple[bool, Dict]:
        """Run tests for a specific layer using run_layer_tests.py script."""
        print(f"\n{'='*70}")
        print(f"Running Layer Tests: {layer_id}")
        print(f"{'='*70}")
        
        script_path = self.system_root / "scripts" / "run_layer_tests.py"
        
        if not script_path.exists():
            print(f"⚠️  Layer test script not found: {script_path}")
            return False, {'status': 'error', 'reason': 'script_not_found'}
        
        cmd = [
            'python3',
            str(script_path),
            '--layer', layer_id,
            '--phase', 'all',
            '--system-root', str(self.system_root)
        ]
        
        if verbose:
            cmd.append('--verbose')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            
            layer_results = {
                'status': 'passed' if success else 'failed',
                'returncode': result.returncode,
                'output': result.stdout
            }
            
            self.layer_results[layer_id] = layer_results
            
            return success, layer_results
            
        except Exception as e:
            print(f"❌ Error running layer tests: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def run_all_layer_tests(self, verbose: bool = False) -> bool:
        """Run tests for all layers in this feature."""
        print(f"\n{'#'*70}")
        print(f"# RUNNING ALL LAYER TESTS FOR {self.feature_id}")
        print(f"{'#'*70}\n")
        
        layers = self.get_layers()
        
        if not layers:
            print(f"⚠️  No layers found for {self.feature_id}")
            return False
        
        print(f"Found {len(layers)} layers:")
        for layer in layers:
            print(f"  - {layer}")
        print()
        
        all_passed = True
        for layer_id in layers:
            passed, results = self.run_layer_tests(layer_id, verbose)
            all_passed = all_passed and passed
        
        return all_passed
    
    def run_feature_integration_tests(self, verbose: bool = False) -> Tuple[bool, Dict]:
        """Run feature-level integration tests."""
        print(f"\n{'='*70}")
        print(f"Running Feature Integration Tests: {self.feature_id}")
        print(f"{'='*70}")
        
        test_req = self.feature_yaml.get('testing_requirements', {})
        integration_req = test_req.get('integration_tests', {})
        
        if not integration_req.get('required', True):
            print("⚠️  Integration tests not required for this feature")
            return True, {'status': 'skipped', 'reason': 'not_required'}
        
        # Get test paths from implementations
        test_paths = self._get_feature_test_paths('integration')
        
        if not test_paths:
            print(f"⚠️  No feature integration test files found")
            # Try to find tests in feature folder
            test_paths = self._search_for_tests('integration')
        
        if not test_paths:
            print(f"❌ No integration tests found for {self.feature_id}")
            return False, {'status': 'failed', 'reason': 'no_tests_found'}
        
        min_tests = integration_req.get('minimum_count', 0)
        coverage_threshold = integration_req.get('coverage_threshold', 0.85)
        
        cmd = [
            'pytest',
            *test_paths,
            '--verbose' if verbose else '--quiet',
            '--tb=short',
            '-m', 'integration',
            f'--cov=src',
            '--cov-report=term-missing',
            f'--junitxml={self.feature_path}/integration_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
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
            
            self.feature_test_results['integration_tests'] = results
            
            if success:
                print(f"\n✅ Feature integration tests PASSED")
                print(f"   Tests: {test_count} (required: {min_tests})")
            else:
                print(f"\n❌ Feature integration tests FAILED")
            
            return success, results
            
        except Exception as e:
            print(f"❌ Error running integration tests: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def run_feature_e2e_tests(self, verbose: bool = False) -> Tuple[bool, Dict]:
        """Run feature-level end-to-end tests."""
        print(f"\n{'='*70}")
        print(f"Running Feature E2E Tests: {self.feature_id}")
        print(f"{'='*70}")
        
        test_req = self.feature_yaml.get('testing_requirements', {})
        e2e_req = test_req.get('e2e_tests', {})
        
        if not e2e_req.get('required', False):
            print("⚠️  E2E tests not required for this feature")
            return True, {'status': 'skipped', 'reason': 'not_required'}
        
        test_paths = self._get_feature_test_paths('e2e')
        
        if not test_paths:
            test_paths = self._search_for_tests('e2e')
        
        if not test_paths:
            print(f"❌ No E2E tests found for {self.feature_id}")
            return False, {'status': 'failed', 'reason': 'no_tests_found'}
        
        min_tests = e2e_req.get('minimum_count', 0)
        coverage_threshold = e2e_req.get('coverage_threshold', 0.70)
        
        cmd = [
            'pytest',
            *test_paths,
            '--verbose' if verbose else '--quiet',
            '--tb=short',
            '-m', 'e2e',
            f'--junitxml={self.feature_path}/e2e_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
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
            
            self.feature_test_results['e2e_tests'] = results
            
            if success:
                print(f"\n✅ Feature E2E tests PASSED")
                print(f"   Tests: {test_count} (required: {min_tests})")
            else:
                print(f"\n❌ Feature E2E tests FAILED")
            
            return success, results
            
        except Exception as e:
            print(f"❌ Error running E2E tests: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def verify_acceptance_criteria(self) -> Dict:
        """Verify all feature acceptance criteria."""
        print(f"\n{'='*70}")
        print(f"Verifying Feature Acceptance Criteria: {self.feature_id}")
        print(f"{'='*70}")
        
        criteria = self.feature_yaml.get('acceptance_criteria', [])
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
            
            criterion_result = {
                'criterion': criterion_id,
                'description': criterion.get('criterion', ''),
                'status': status,
                'test_file': test_file,
                'verified': status == 'implemented'
            }
            
            verification['criteria_status'].append(criterion_result)
            
            if status == 'implemented':
                verification['implemented'] += 1
            elif status == 'in_progress':
                verification['in_progress'] += 1
            else:
                verification['not_implemented'] += 1
            
            status_icon = '✅' if criterion_result['verified'] else '⚠️' if status == 'in_progress' else '❌'
            print(f"{status_icon} {criterion_id}: {status}")
        
        verification['compliance'] = verification['implemented'] / verification['total_criteria'] if verification['total_criteria'] > 0 else 0
        
        print(f"\nFeature Compliance: {verification['compliance']:.1%}")
        
        return verification
    
    def _get_feature_test_paths(self, test_type: str) -> List[str]:
        """Get feature-level test paths."""
        implementations = self.feature_yaml.get('implementations', {})
        test_files = []
        
        # Check implementations for test files
        for phase in ['red_phase', 'green_phase', 'refactor_phase']:
            phase_data = implementations.get(phase, {})
            if 'test_files' in phase_data:
                for test_file_info in phase_data['test_files']:
                    if isinstance(test_file_info, dict):
                        path = test_file_info.get('path', '')
                    else:
                        path = str(test_file_info)
                    
                    if test_type in path:
                        test_files.append(path)
        
        return list(set(test_files))
    
    def _search_for_tests(self, test_type: str) -> List[str]:
        """Search for test files in standard locations."""
        # Try tests/feature/<feature_name>/ pattern
        feature_name = self.feature_yaml['metadata']['requirement_name'].lower().replace(' ', '_')
        test_dir = self.system_root.parent.parent.parent / 'tests' / 'feature' / feature_name
        
        if test_dir.exists():
            return [str(f) for f in test_dir.glob(f'*{test_type}*.py')]
        
        return []
    
    def _count_tests_from_output(self, output: str) -> int:
        """Count tests from pytest output."""
        import re
        match = re.search(r'(\d+) passed', output)
        return int(match.group(1)) if match else 0
    
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
    
    def generate_report(self, acceptance_verification: Dict) -> str:
        """Generate comprehensive feature verification report."""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"FEATURE VERIFICATION REPORT: {self.feature_id}")
        report.append(f"{'='*70}")
        report.append(f"Feature: {self.feature_yaml['metadata']['requirement_name']}")
        report.append(f"System: {self.feature_yaml['metadata']['parent_system']}")
        report.append(f"Status: {self.feature_yaml['metadata']['status']}")
        report.append(f"Progress: {self.feature_yaml['metadata']['progress_percentage']}%")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Layer Results Summary
        report.append("LAYER TEST RESULTS")
        report.append("-" * 70)
        for layer_id, results in self.layer_results.items():
            status = results.get('status', 'unknown').upper()
            icon = '✅' if status == 'PASSED' else '❌'
            report.append(f"{icon} {layer_id}: {status}")
        report.append("")
        
        # Feature Integration Tests
        if 'integration_tests' in self.feature_test_results:
            it = self.feature_test_results['integration_tests']
            report.append("FEATURE INTEGRATION TESTS")
            report.append("-" * 70)
            report.append(f"Status: {it.get('status', 'unknown').upper()}")
            report.append(f"Tests: {it.get('test_count', 0)} (required: {it.get('minimum_tests', 0)})")
            report.append(f"Passed: {it.get('tests_passed', 0)}")
            report.append(f"Failed: {it.get('tests_failed', 0)}")
            report.append("")
        
        # Feature E2E Tests
        if 'e2e_tests' in self.feature_test_results:
            e2e = self.feature_test_results['e2e_tests']
            report.append("FEATURE E2E TESTS")
            report.append("-" * 70)
            report.append(f"Status: {e2e.get('status', 'unknown').upper()}")
            report.append(f"Tests: {e2e.get('test_count', 0)} (required: {e2e.get('minimum_tests', 0)})")
            report.append(f"Passed: {e2e.get('tests_passed', 0)}")
            report.append(f"Failed: {e2e.get('tests_failed', 0)}")
            report.append("")
        
        # Acceptance Criteria
        report.append("ACCEPTANCE CRITERIA")
        report.append("-" * 70)
        for criterion in acceptance_verification['criteria_status']:
            icon = '✅' if criterion['verified'] else '⚠️' if criterion['status'] == 'in_progress' else '❌'
            report.append(f"{icon} {criterion['criterion']}: {criterion['status']}")
        report.append("")
        report.append(f"Compliance: {acceptance_verification['compliance']:.1%}")
        report.append(f"{'='*70}\n")
        
        return "\n".join(report)
    
    def update_feature_yaml(self, acceptance_verification: Dict):
        """Update feature YAML with verification results."""
        yaml_file = list(self.feature_path.glob(f"{self.feature_id}_*.yaml"))[0]
        
        # Calculate overall status
        layers_passed = all(r.get('status') == 'passed' for r in self.layer_results.values())
        integration_passed = self.feature_test_results.get('integration_tests', {}).get('status') == 'passed'
        e2e_passed = self.feature_test_results.get('e2e_tests', {}).get('status') in ['passed', 'skipped']
        
        # Update progress if all tests pass
        if layers_passed and integration_passed and e2e_passed and acceptance_verification['compliance'] == 1.0:
            self.feature_yaml['metadata']['status'] = 'implemented'
            self.feature_yaml['metadata']['progress_percentage'] = 100
        elif acceptance_verification['compliance'] > 0:
            self.feature_yaml['metadata']['status'] = 'in_progress'
        
        # Save updated YAML
        with open(yaml_file, 'w') as f:
            yaml.dump(self.feature_yaml, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Updated feature YAML: {yaml_file}")


def main():
    parser = argparse.ArgumentParser(description='Verify a complete feature')
    parser.add_argument('--feature', required=True, help='Feature ID (e.g., FEATURE-003-03-01)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--update-yaml', action='store_true',
                       help='Update feature YAML with verification results')
    parser.add_argument('--system-root', type=Path,
                       default=Path(__file__).parent.parent,
                       help='Path to SYSTEM-003-03 root directory')
    parser.add_argument('--skip-layers', action='store_true',
                       help='Skip layer tests (only run feature-level tests)')
    
    args = parser.parse_args()
    
    try:
        verifier = FeatureVerifier(args.feature, args.system_root)
        
        print(f"\n{'#'*70}")
        print(f"# FEATURE VERIFICATION")
        print(f"# Feature: {args.feature}")
        print(f"{'#'*70}\n")
        
        all_passed = True
        
        # Run layer tests
        if not args.skip_layers:
            layers_passed = verifier.run_all_layer_tests(verbose=args.verbose)
            all_passed = all_passed and layers_passed
        
        # Run feature integration tests
        integration_passed, _ = verifier.run_feature_integration_tests(verbose=args.verbose)
        all_passed = all_passed and integration_passed
        
        # Run feature E2E tests
        e2e_passed, _ = verifier.run_feature_e2e_tests(verbose=args.verbose)
        all_passed = all_passed and e2e_passed
        
        # Verify acceptance criteria
        acceptance_verification = verifier.verify_acceptance_criteria()
        
        # Generate report
        report = verifier.generate_report(acceptance_verification)
        print(report)
        
        # Update YAML if requested
        if args.update_yaml:
            verifier.update_feature_yaml(acceptance_verification)
        
        # Save report
        report_path = verifier.feature_path / f"feature_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_path}")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed and acceptance_verification['compliance'] >= 0.5 else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
