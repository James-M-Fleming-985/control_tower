#!/usr/bin/env python3
"""
System-Level Verification Orchestration Script

Executes complete system verification: all features, all layers,
system-level E2E tests, and performance validation.

Usage:
    python run_system_verification.py
    python run_system_verification.py --verbose
    python run_system_verification.py --feature FEATURE-003-03-01
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import yaml


class SystemVerifier:
    """Orchestrates complete system verification."""
    
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.system_yaml = self._load_system_yaml()
        self.feature_results = {}
        self.system_test_results = {}
        
    def _load_system_yaml(self) -> dict:
        """Load system requirements YAML."""
        yaml_file = self.system_root / "SYSTEM-003-03_workflow_orchestration_system.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"System YAML not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    def get_features(self) -> List[str]:
        """Get all feature IDs for this system."""
        features = []
        for feature_folder in self.system_root.iterdir():
            if feature_folder.is_dir() and feature_folder.name.startswith("FEATURE-"):
                feature_id = feature_folder.name.split()[0]
                features.append(feature_id)
        return sorted(features)
    
    def verify_feature(self, feature_id: str, verbose: bool = False):
        """Verify a complete feature using verify_feature.py script."""
        print(f"\n{'='*70}")
        print(f"Verifying Feature: {feature_id}")
        print(f"{'='*70}")
        
        script_path = self.system_root / "scripts" / "verify_feature.py"
        
        if not script_path.exists():
            print(f"⚠️  Feature verification script not found")
            return False, {'status': 'error', 'reason': 'script_not_found'}
        
        cmd = [
            'python3',
            str(script_path),
            '--feature', feature_id,
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
            
            feature_result = {
                'status': 'passed' if success else 'failed',
                'returncode': result.returncode
            }
            
            self.feature_results[feature_id] = feature_result
            
            return success, feature_result
            
        except Exception as e:
            print(f"❌ Error verifying feature: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def verify_all_features(self, verbose: bool = False) -> bool:
        """Verify all features in the system."""
        print(f"\n{'#'*70}")
        print(f"# VERIFYING ALL FEATURES")
        print(f"{'#'*70}\n")
        
        features = self.get_features()
        
        if not features:
            print("⚠️  No features found in system")
            return False
        
        # Implementation order: 2 → 1 → 4 → 3
        priority_order = {
            'FEATURE-003-03-02': 1,  # Prerequisites (foundation)
            'FEATURE-003-03-01': 2,  # Orchestration (core)
            'FEATURE-003-03-04': 3,  # Monitoring (observability)
            'FEATURE-003-03-03': 4,  # Failure Handling (integration)
        }
        
        # Sort by priority
        features = sorted(features, key=lambda f: priority_order.get(f, 999))
        
        print(f"Verification order (dependency-based):")
        for i, feature in enumerate(features, 1):
            print(f"  {i}. {feature}")
        print()
        
        all_passed = True
        for feature_id in features:
            passed, results = self.verify_feature(feature_id, verbose)
            all_passed = all_passed and passed
        
        return all_passed
    
    def run_system_e2e_tests(self, verbose: bool = False):
        """Run system-level end-to-end tests."""
        print(f"\n{'='*70}")
        print(f"Running System E2E Tests")
        print(f"{'='*70}")
        
        test_req = self.system_yaml.get('testing_requirements', {})
        e2e_req = test_req.get('e2e_tests', {})
        
        if not e2e_req.get('required', False):
            print("⚠️  System E2E tests not required")
            return True, {'status': 'skipped'}
        
        min_tests = e2e_req.get('minimum_count', 0)
        coverage_threshold = e2e_req.get('coverage_threshold', 0.80)
        
        # Find system E2E tests
        test_paths = self._find_system_tests('e2e')
        
        if not test_paths:
            print(f"❌ No system E2E tests found")
            return False, {'status': 'failed', 'reason': 'no_tests_found'}
        
        cmd = [
            'pytest',
            *test_paths,
            '--verbose' if verbose else '--quiet',
            '--tb=short',
            '-m', 'system_e2e',
            f'--junitxml={self.system_root}/system_e2e_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
        ]
        
        print(f"Command: {' '.join(str(c) for c in cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.system_root.parent.parent
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
                'minimum_tests': min_tests
            }
            
            self.system_test_results['e2e_tests'] = results
            
            if success:
                print(f"\n✅ System E2E tests PASSED")
                print(f"   Tests: {test_count} (required: {min_tests})")
            else:
                print(f"\n❌ System E2E tests FAILED")
            
            return success, results
            
        except Exception as e:
            print(f"❌ Error running system E2E tests: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def run_performance_tests(self, verbose: bool = False):
        """Run system performance tests."""
        print(f"\n{'='*70}")
        print(f"Running Performance Tests")
        print(f"{'='*70}")
        
        test_req = self.system_yaml.get('testing_requirements', {})
        perf_req = test_req.get('performance_tests', {})
        
        if not perf_req.get('required', False):
            print("⚠️  Performance tests not required")
            return True, {'status': 'skipped'}
        
        # Performance thresholds
        max_workflow_duration = perf_req.get('max_workflow_duration_seconds', 900)
        max_prereq_duration = perf_req.get('max_prerequisites_validation_seconds', 30)
        max_stage_duration = perf_req.get('max_stage_execution_seconds', 120)
        
        print(f"Performance Requirements:")
        print(f"  Max workflow duration: {max_workflow_duration}s")
        print(f"  Max prerequisites validation: {max_prereq_duration}s")
        print(f"  Max stage execution: {max_stage_duration}s")
        
        # Find performance tests
        test_paths = self._find_system_tests('performance')
        
        if not test_paths:
            print(f"⚠️  No performance tests found")
            return True, {'status': 'warning', 'reason': 'no_tests_found'}
        
        cmd = [
            'pytest',
            *test_paths,
            '--verbose' if verbose else '--quiet',
            '-m', 'performance',
            f'--junitxml={self.system_root}/performance_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.system_root.parent.parent
            )
            
            print(result.stdout)
            
            success = result.returncode == 0
            
            results = {
                'status': 'passed' if success else 'failed',
                'returncode': result.returncode
            }
            
            self.system_test_results['performance_tests'] = results
            
            return success, results
            
        except Exception as e:
            print(f"❌ Error running performance tests: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def _find_system_tests(self, test_type: str) -> List[str]:
        """Find system-level tests."""
        # Look in tests/system/ directory
        test_dir = self.system_root.parent.parent / 'tests' / 'system'
        
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
    
    def generate_system_report(self) -> str:
        """Generate comprehensive system verification report."""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"SYSTEM VERIFICATION REPORT")
        report.append(f"{'='*70}")
        report.append(f"System: {self.system_yaml['metadata']['requirement_name']}")
        report.append(f"System ID: {self.system_yaml['metadata']['requirement_id']}")
        report.append(f"Project: {self.system_yaml['metadata']['parent_project']}")
        report.append(f"Team Size: {self.system_yaml['metadata']['team_size']}")
        report.append(f"Risk Level: {self.system_yaml['metadata']['risk_level']}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Feature Results
        report.append("FEATURE VERIFICATION RESULTS")
        report.append("-" * 70)
        for feature_id, results in self.feature_results.items():
            status = results.get('status', 'unknown').upper()
            icon = '✅' if status == 'PASSED' else '❌'
            report.append(f"{icon} {feature_id}: {status}")
        
        features_passed = sum(1 for r in self.feature_results.values() if r.get('status') == 'passed')
        total_features = len(self.feature_results)
        report.append(f"\nFeatures Passed: {features_passed}/{total_features}")
        report.append("")
        
        # System E2E Tests
        if 'e2e_tests' in self.system_test_results:
            e2e = self.system_test_results['e2e_tests']
            report.append("SYSTEM E2E TESTS")
            report.append("-" * 70)
            report.append(f"Status: {e2e.get('status', 'unknown').upper()}")
            report.append(f"Tests: {e2e.get('test_count', 0)} (required: {e2e.get('minimum_tests', 0)})")
            report.append(f"Passed: {e2e.get('tests_passed', 0)}")
            report.append(f"Failed: {e2e.get('tests_failed', 0)}")
            report.append("")
        
        # Performance Tests
        if 'performance_tests' in self.system_test_results:
            perf = self.system_test_results['performance_tests']
            report.append("PERFORMANCE TESTS")
            report.append("-" * 70)
            report.append(f"Status: {perf.get('status', 'unknown').upper()}")
            report.append("")
        
        # Overall Status
        all_features_passed = all(r.get('status') == 'passed' for r in self.feature_results.values())
        e2e_passed = self.system_test_results.get('e2e_tests', {}).get('status') in ['passed', 'skipped']
        perf_passed = self.system_test_results.get('performance_tests', {}).get('status') in ['passed', 'skipped']
        
        overall_passed = all_features_passed and e2e_passed and perf_passed
        
        report.append("="* 70)
        if overall_passed:
            report.append("✅ SYSTEM VERIFICATION PASSED")
        else:
            report.append("❌ SYSTEM VERIFICATION FAILED")
        report.append("="* 70)
        report.append("")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Run complete system verification'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--system-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Path to SYSTEM-003-03 root directory'
    )
    parser.add_argument(
        '--feature',
        help='Verify only specific feature (e.g., FEATURE-003-03-01)'
    )
    parser.add_argument(
        '--skip-e2e',
        action='store_true',
        help='Skip system E2E tests'
    )
    parser.add_argument(
        '--skip-performance',
        action='store_true',
        help='Skip performance tests'
    )
    
    args = parser.parse_args()
    
    try:
        verifier = SystemVerifier(args.system_root)
        
        print(f"\n{'#'*70}")
        print(f"# SYSTEM VERIFICATION")
        print(f"# System: SYSTEM-003-03 Workflow Orchestration System")
        print(f"{'#'*70}\n")
        
        all_passed = True
        
        # Verify features
        if args.feature:
            # Single feature verification
            feature_passed, _ = verifier.verify_feature(
                args.feature,
                verbose=args.verbose
            )
            all_passed = all_passed and feature_passed
        else:
            # All features verification
            features_passed = verifier.verify_all_features(
                verbose=args.verbose
            )
            all_passed = all_passed and features_passed
        
        # System E2E tests
        if not args.skip_e2e:
            e2e_passed, _ = verifier.run_system_e2e_tests(
                verbose=args.verbose
            )
            all_passed = all_passed and e2e_passed
        
        # Performance tests
        if not args.skip_performance:
            perf_passed, _ = verifier.run_performance_tests(
                verbose=args.verbose
            )
            all_passed = all_passed and perf_passed
        
        # Generate report
        report = verifier.generate_system_report()
        print(report)
        
        # Save report
        report_path = args.system_root / f"system_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_path}")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
