#!/usr/bin/env python3
"""
Master Layer Execution Script

Makes layer requirements executable by:
1. Generating test files from acceptance criteria
2. Creating implementation stubs
3. Running tests in RED/GREEN/REFACTOR phases
4. Collecting evidence in Testing Outputs/
5. Updating Requirements Verification/

Usage:
    python execute_layer.py --layer LAYER-003-03-01-01 --phase red
    python execute_layer.py --layer LAYER-003-03-01-01 --phase green
    python execute_layer.py --layer LAYER-003-03-01-01 --phase refactor
    python execute_layer.py --layer LAYER-003-03-01-01 --full-cycle
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class LayerExecutor:
    """Makes layer requirements executable through TDD cycle."""
    
    def __init__(self, layer_id: str, system_root: Path):
        self.layer_id = layer_id
        self.system_root = system_root
        self.layer_path = self._find_layer_path()
        self.layer_yaml = self._load_layer_yaml()
        self.project_root = system_root.parent.parent.parent
        self.evidence = []
        
    def _find_layer_path(self) -> Path:
        """Find the layer folder based on layer ID."""
        for yaml_file in self.system_root.rglob(f"{self.layer_id}_*.yaml"):
            if "requirements_verification" not in str(yaml_file):
                return yaml_file.parent
        raise FileNotFoundError(f"Layer {self.layer_id} not found")
    
    def _load_layer_yaml(self) -> dict:
        """Load layer requirements YAML."""
        yaml_files = list(self.layer_path.glob(f"{self.layer_id}_*.yaml"))
        if not yaml_files:
            raise FileNotFoundError(f"No YAML file found for {self.layer_id}")
        
        with open(yaml_files[0], 'r') as f:
            return yaml.safe_load(f)
    
    def generate_test_files(self) -> List[Path]:
        """Generate test files from acceptance criteria."""
        print(f"\n{'='*70}")
        print(f"Generating Test Files for {self.layer_id}")
        print(f"{'='*70}")
        
        acceptance_criteria = self.layer_yaml.get('acceptance_criteria', [])
        test_files = []
        
        # Create tests directory structure
        layer_name = self.layer_yaml['metadata']['requirement_name'].lower().replace(' ', '_')
        tests_dir = self.project_root / 'tests' / 'layer' / layer_name
        tests_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unit tests
        unit_test_file = tests_dir / f'test_{layer_name}_unit.py'
        self._generate_unit_tests(unit_test_file, acceptance_criteria)
        test_files.append(unit_test_file)
        
        # Generate integration tests
        integration_test_file = tests_dir / f'test_{layer_name}_integration.py'
        self._generate_integration_tests(integration_test_file, acceptance_criteria)
        test_files.append(integration_test_file)
        
        # Save evidence
        self._save_evidence(
            'test_generation',
            f"Generated {len(test_files)} test files with {len(acceptance_criteria)} acceptance criteria"
        )
        
        return test_files
    
    def _generate_unit_tests(self, test_file: Path, criteria: List[Dict]):
        """Generate unit test file from acceptance criteria."""
        test_content = [
            '"""',
            f'Unit Tests for {self.layer_yaml["metadata"]["requirement_name"]}',
            f'Layer: {self.layer_id}',
            '',
            'AUTO-GENERATED from acceptance criteria.',
            'Tests follow TDD RED phase - they should FAIL initially.',
            '"""',
            '',
            'import pytest',
            'from datetime import datetime',
            'from typing import Dict, List',
            '',
            f'# REQ-{self.layer_id}',
            '',
        ]
        
        # Generate test class
        class_name = self._to_class_name(self.layer_yaml['metadata']['requirement_name'])
        test_content.extend([
            '',
            f'class Test{class_name}Unit:',
            f'    """Unit tests for {class_name}."""',
            '',
            '    def setup_method(self):',
            '        """Setup test fixtures."""',
            '        # TODO: Initialize test fixtures',
            '        pass',
            '',
        ])
        
        # Generate test methods for each acceptance criterion
        for criterion in criteria:
            criterion_text = criterion.get('criterion', '')
            criterion_id = criterion_text.split(':')[0] if ':' in criterion_text else 'AC-XXX'
            description = criterion_text.split(':', 1)[1].strip() if ':' in criterion_text else criterion_text
            
            test_method_name = self._to_method_name(description)
            
            test_content.extend([
                f'    def test_{test_method_name}(self):',
                f'        """',
                f'        {criterion_id}: {description}',
                f'        ',
                f'        This test validates acceptance criterion {criterion_id}.',
                f'        Expected to FAIL in RED phase until implementation is complete.',
                f'        """',
                f'        # REQ-{criterion_id}',
                f'        ',
                f'        # Arrange',
                f'        # TODO: Setup test data and dependencies',
                f'        ',
                f'        # Act',
                f'        # TODO: Execute the functionality being tested',
                f'        result = None  # Replace with actual implementation call',
                f'        ',
                f'        # Assert',
                f'        # TODO: Replace with real assertion',
                f'        assert result is not None, "Implementation not complete"',
                f'        # Expected to FAIL until GREEN phase',
                f'        ',
                '',
            ])
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write('\n'.join(test_content))
        
        print(f"✅ Generated unit tests: {test_file}")
    
    def _generate_integration_tests(self, test_file: Path, criteria: List[Dict]):
        """Generate integration test file."""
        test_content = [
            '"""',
            f'Integration Tests for {self.layer_yaml["metadata"]["requirement_name"]}',
            f'Layer: {self.layer_id}',
            '',
            'Tests integration with other layers and dependencies.',
            '"""',
            '',
            'import pytest',
            '',
            f'# REQ-{self.layer_id}',
            '',
            'pytestmark = pytest.mark.integration',
            '',
        ]
        
        class_name = self._to_class_name(self.layer_yaml['metadata']['requirement_name'])
        test_content.extend([
            '',
            f'class Test{class_name}Integration:',
            f'    """Integration tests for {class_name}."""',
            '',
        ])
        
        # Get dependencies
        dependencies = self.layer_yaml.get('dependencies', {})
        layer_deps = dependencies.get('layer_dependencies', [])
        
        if layer_deps:
            test_content.extend([
                f'    def test_integration_with_dependencies(self):',
                f'        """Test integration with dependent layers."""',
                f'        # Dependencies: {", ".join(layer_deps)}',
                f'        ',
                f'        # TODO: Test integration with:',
            ])
            for dep in layer_deps:
                test_content.append(f'        # - {dep}')
            test_content.extend([
                f'        ',
                f'        assert False, "Integration tests not implemented"',
                f'        ',
                '',
            ])
        else:
            test_content.extend([
                f'    def test_standalone_integration(self):',
                f'        """Test layer functions independently."""',
                f'        # This layer has no dependencies',
                f'        ',
                f'        assert False, "Integration tests not implemented"',
                f'        ',
                '',
            ])
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write('\n'.join(test_content))
        
        print(f"✅ Generated integration tests: {test_file}")
    
    def generate_implementation_stubs(self) -> List[Path]:
        """Generate implementation file stubs."""
        print(f"\n{'='*70}")
        print(f"Generating Implementation Stubs for {self.layer_id}")
        print(f"{'='*70}")
        
        # Create src directory structure
        layer_name = self.layer_yaml['metadata']['requirement_name'].lower().replace(' ', '_')
        impl_dir = self.project_root / 'src' / 'layer' / layer_name
        impl_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate main implementation file
        impl_file = impl_dir / f'{layer_name}.py'
        self._generate_implementation_file(impl_file)
        
        # Generate __init__.py
        init_file = impl_dir / '__init__.py'
        with open(init_file, 'w') as f:
            class_name = self._to_class_name(self.layer_yaml['metadata']['requirement_name'])
            f.write(f'"""Layer: {self.layer_yaml["metadata"]["requirement_name"]}"""\n\n')
            f.write(f'from .{layer_name} import {class_name}\n\n')
            f.write(f'__all__ = ["{class_name}"]\n')
        
        print(f"✅ Generated implementation stubs in {impl_dir}")
        
        # Save evidence
        self._save_evidence(
            'stub_generation',
            f"Generated implementation stubs in {impl_dir}"
        )
        
        return [impl_file, init_file]
    
    def _generate_implementation_file(self, impl_file: Path):
        """Generate main implementation file."""
        class_name = self._to_class_name(self.layer_yaml['metadata']['requirement_name'])
        
        impl_content = [
            '"""',
            f'{self.layer_yaml["metadata"]["requirement_name"]}',
            '',
            f'Layer: {self.layer_id}',
            f'Requirement: {self.layer_yaml["metadata"]["requirement_name"]}',
            '',
            'AUTO-GENERATED implementation stub.',
            'Fill in the TODO sections to make tests pass (GREEN phase).',
            '"""',
            '',
            'from typing import Dict, List, Optional',
            'from datetime import datetime',
            '',
            f'# REQ-{self.layer_id}',
            '',
            '',
            f'class {class_name}:',
            f'    """',
            f'    {self.layer_yaml["metadata"]["requirement_name"]}',
            f'    ',
            f'    Acceptance Criteria:',
        ]
        
        # Add acceptance criteria as docstring
        for criterion in self.layer_yaml.get('acceptance_criteria', []):
            criterion_text = criterion.get('criterion', '')
            impl_content.append(f'    - {criterion_text}')
        
        impl_content.extend([
            f'    """',
            '',
            '    def __init__(self):',
            '        """Initialize the component."""',
            '        # TODO: Initialize component state',
            '        pass',
            '',
        ])
        
        # Generate method stubs for each acceptance criterion
        for criterion in self.layer_yaml.get('acceptance_criteria', []):
            criterion_text = criterion.get('criterion', '')
            criterion_id = criterion_text.split(':')[0] if ':' in criterion_text else 'AC-XXX'
            description = criterion_text.split(':', 1)[1].strip() if ':' in criterion_text else criterion_text
            
            method_name = self._to_method_name(description)
            
            impl_content.extend([
                f'    def {method_name}(self) -> bool:',
                f'        """',
                f'        {criterion_id}: {description}',
                f'        ',
                f'        Returns:',
                f'            bool: True if successful, False otherwise',
                f'        """',
                f'        # REQ-{criterion_id}',
                f'        ',
                f'        # TODO: Implement {description}',
                f'        raise NotImplementedError("{criterion_id} not implemented")',
                f'        ',
                '',
            ])
        
        # Write implementation file
        with open(impl_file, 'w') as f:
            f.write('\n'.join(impl_content))
        
        print(f"✅ Generated implementation: {impl_file}")
    
    def run_red_phase(self) -> Tuple[bool, Dict]:
        """Execute RED phase - tests should FAIL."""
        print(f"\n{'='*70}")
        print(f"RED PHASE: Running Tests (Expected to FAIL)")
        print(f"{'='*70}")
        
        # Generate tests if they don't exist
        test_files = self.generate_test_files()
        
        # Run tests - they should fail
        layer_name = self.layer_yaml['metadata']['requirement_name'].lower().replace(' ', '_')
        tests_dir = self.project_root / 'tests' / 'layer' / layer_name
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        junit_file = self.layer_path / 'Testing Outputs' / f'red_phase_results_{timestamp}.xml'
        log_file = self.layer_path / 'Testing Outputs' / f'red_phase_log_{timestamp}.txt'
        
        cmd = [
            'pytest',
            str(tests_dir),
            '-v',
            '--tb=short',
            f'--junitxml={junit_file}'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        
        # Save test output
        with open(log_file, 'w') as f:
            f.write(f"RED PHASE TEST EXECUTION\n")
            f.write(f"{'='*70}\n")
            f.write(f"Layer: {self.layer_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"{'='*70}\n\n")
            f.write(result.stdout)
            if result.stderr:
                f.write(f"\n\nSTDERR:\n{result.stderr}")
        
        # Tests SHOULD fail in RED phase
        tests_failed = result.returncode != 0
        
        if tests_failed:
            print(f"✅ RED PHASE PASSED: Tests are failing as expected")
            print(f"   Log saved to: {log_file}")
            status = 'passed'
        else:
            print(f"❌ RED PHASE FAILED: Tests should fail but they passed!")
            print(f"   This violates TDD - tests must fail before implementation")
            status = 'violated'
        
        # Save evidence
        self._save_evidence(
            'red_phase',
            f"Tests {'failed as expected' if tests_failed else 'INCORRECTLY PASSED'}",
            {
                'junit_file': str(junit_file),
                'log_file': str(log_file),
                'tests_failed': tests_failed,
                'returncode': result.returncode
            }
        )
        
        return tests_failed, {
            'status': status,
            'junit_file': str(junit_file),
            'log_file': str(log_file)
        }
    
    def run_green_phase(self) -> Tuple[bool, Dict]:
        """Execute GREEN phase - implement and make tests PASS."""
        print(f"\n{'='*70}")
        print(f"GREEN PHASE: Implementing Requirements")
        print(f"{'='*70}")
        
        # Generate implementation stubs if they don't exist
        impl_files = self.generate_implementation_stubs()
        
        print(f"\n⚠️  Implementation stubs generated.")
        print(f"   Please implement the TODOs in:")
        for impl_file in impl_files:
            print(f"   - {impl_file}")
        print(f"\n   After implementation, run tests again...")
        
        # Run tests with coverage
        layer_name = self.layer_yaml['metadata']['requirement_name'].lower().replace(' ', '_')
        tests_dir = self.project_root / 'tests' / 'layer' / layer_name
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        junit_file = self.layer_path / 'Testing Outputs' / f'green_phase_results_{timestamp}.xml'
        log_file = self.layer_path / 'Testing Outputs' / f'green_phase_log_{timestamp}.txt'
        coverage_file = self.layer_path / 'Testing Outputs' / f'coverage_{timestamp}.json'
        
        cmd = [
            'pytest',
            str(tests_dir),
            '-v',
            '--tb=short',
            f'--cov=src/layer/{layer_name}',
            '--cov-report=term-missing',
            '--cov-report=html',
            f'--cov-report=json:{coverage_file}',
            f'--junitxml={junit_file}'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        
        # Save test output
        with open(log_file, 'w') as f:
            f.write(f"GREEN PHASE TEST EXECUTION\n")
            f.write(f"{'='*70}\n")
            f.write(f"Layer: {self.layer_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"{'='*70}\n\n")
            f.write(result.stdout)
            if result.stderr:
                f.write(f"\n\nSTDERR:\n{result.stderr}")
        
        tests_passed = result.returncode == 0
        
        # Parse coverage
        coverage_pct = 0
        if coverage_file.exists():
            with open(coverage_file, 'r') as f:
                cov_data = json.load(f)
                coverage_pct = cov_data.get('totals', {}).get('percent_covered', 0)
        
        required_coverage = self.layer_yaml.get('testing_requirements', {}).get('unit_tests', {}).get('coverage_threshold', 90) * 100
        
        if tests_passed and coverage_pct >= required_coverage:
            print(f"✅ GREEN PHASE PASSED: All tests passing")
            print(f"   Coverage: {coverage_pct:.1f}% (required: {required_coverage:.1f}%)")
            print(f"   Results saved to: {junit_file}")
            status = 'passed'
        else:
            print(f"⚠️  GREEN PHASE IN PROGRESS")
            if not tests_passed:
                print(f"   Some tests still failing")
            if coverage_pct < required_coverage:
                print(f"   Coverage: {coverage_pct:.1f}% < {required_coverage:.1f}%")
            status = 'in_progress'
        
        # Save evidence
        self._save_evidence(
            'green_phase',
            f"Tests {'passed' if tests_passed else 'failing'}, Coverage: {coverage_pct:.1f}%",
            {
                'junit_file': str(junit_file),
                'log_file': str(log_file),
                'coverage_file': str(coverage_file),
                'tests_passed': tests_passed,
                'coverage': coverage_pct,
                'required_coverage': required_coverage
            }
        )
        
        return tests_passed and coverage_pct >= required_coverage, {
            'status': status,
            'junit_file': str(junit_file),
            'log_file': str(log_file),
            'coverage': coverage_pct
        }
    
    def run_refactor_phase(self) -> Tuple[bool, Dict]:
        """Execute REFACTOR phase - improve code while keeping tests green."""
        print(f"\n{'='*70}")
        print(f"REFACTOR PHASE: Verify Tests Still Pass")
        print(f"{'='*70}")
        
        # Run tests again to verify refactoring didn't break anything
        layer_name = self.layer_yaml['metadata']['requirement_name'].lower().replace(' ', '_')
        tests_dir = self.project_root / 'tests' / 'layer' / layer_name
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        junit_file = self.layer_path / 'Testing Outputs' / f'refactor_phase_results_{timestamp}.xml'
        log_file = self.layer_path / 'Testing Outputs' / f'refactor_phase_log_{timestamp}.txt'
        
        cmd = [
            'pytest',
            str(tests_dir),
            '-v',
            '--tb=short',
            f'--cov=src/layer/{layer_name}',
            '--cov-report=term-missing',
            f'--junitxml={junit_file}'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        
        # Save test output
        with open(log_file, 'w') as f:
            f.write(f"REFACTOR PHASE TEST EXECUTION\n")
            f.write(f"{'='*70}\n")
            f.write(f"Layer: {self.layer_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"{'='*70}\n\n")
            f.write(result.stdout)
        
        tests_passed = result.returncode == 0
        
        if tests_passed:
            print(f"✅ REFACTOR PHASE PASSED: Tests still passing after refactoring")
            status = 'passed'
        else:
            print(f"❌ REFACTOR PHASE FAILED: Tests broken by refactoring!")
            status = 'failed'
        
        # Save evidence
        self._save_evidence(
            'refactor_phase',
            f"Tests {'passed' if tests_passed else 'FAILED'} after refactoring",
            {
                'junit_file': str(junit_file),
                'log_file': str(log_file),
                'tests_passed': tests_passed
            }
        )
        
        return tests_passed, {
            'status': status,
            'junit_file': str(junit_file),
            'log_file': str(log_file)
        }
    
    def update_requirements_verification(self):
        """Update requirements verification YAML with execution results."""
        print(f"\n{'='*70}")
        print(f"Updating Requirements Verification")
        print(f"{'='*70}")
        
        verification_file = self.layer_path / 'Requirements Verification' / 'requirements_verification_template.yaml'
        
        if not verification_file.exists():
            print(f"⚠️  Verification file not found: {verification_file}")
            return
        
        with open(verification_file, 'r') as f:
            verification = yaml.safe_load(f)
        
        # Update with evidence
        verification['verification_execution'] = {
            'executed_at': datetime.now().isoformat(),
            'evidence': self.evidence
        }
        
        verification['verification_status'] = 'in_progress'
        
        # Save updated YAML
        with open(verification_file, 'w') as f:
            yaml.dump(verification, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Updated verification YAML with {len(self.evidence)} evidence entries")
    
    def _save_evidence(self, phase: str, description: str, data: Dict = None):
        """Save evidence entry."""
        evidence_entry = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'description': description
        }
        if data:
            evidence_entry['data'] = data
        
        self.evidence.append(evidence_entry)
        
        # Also save to JSON file
        evidence_file = self.layer_path / 'Requirements Verification' / 'execution_evidence.json'
        with open(evidence_file, 'w') as f:
            json.dump(self.evidence, f, indent=2)
    
    def _to_class_name(self, text: str) -> str:
        """Convert text to PascalCase class name."""
        words = text.replace('-', ' ').replace('_', ' ').split()
        return ''.join(word.capitalize() for word in words)
    
    def _to_method_name(self, text: str) -> str:
        """Convert text to snake_case method name."""
        # Remove special characters
        text = text.lower()
        text = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
        words = text.split()
        return '_'.join(words[:6])  # Limit to 6 words


def main():
    parser = argparse.ArgumentParser(description='Execute layer requirements through TDD')
    parser.add_argument('--layer', required=True, help='Layer ID (e.g., LAYER-003-03-01-01)')
    parser.add_argument('--phase', choices=['red', 'green', 'refactor', 'full-cycle'],
                       help='TDD phase to execute')
    parser.add_argument('--system-root', type=Path,
                       default=Path(__file__).parent.parent,
                       help='Path to SYSTEM-003-03 root directory')
    
    args = parser.parse_args()
    
    try:
        executor = LayerExecutor(args.layer, args.system_root)
        
        print(f"\n{'#'*70}")
        print(f"# LAYER REQUIREMENT EXECUTOR")
        print(f"# Layer: {args.layer}")
        print(f"# Phase: {args.phase or 'full-cycle'}")
        print(f"{'#'*70}\n")
        
        if args.phase == 'red':
            success, results = executor.run_red_phase()
            executor.update_requirements_verification()
            sys.exit(0 if success else 1)
            
        elif args.phase == 'green':
            success, results = executor.run_green_phase()
            executor.update_requirements_verification()
            sys.exit(0 if success else 1)
            
        elif args.phase == 'refactor':
            success, results = executor.run_refactor_phase()
            executor.update_requirements_verification()
            sys.exit(0 if success else 1)
            
        else:  # full-cycle
            print("Executing FULL TDD CYCLE (RED → GREEN → REFACTOR)")
            
            # RED phase
            red_success, red_results = executor.run_red_phase()
            if not red_success:
                print("\n❌ RED PHASE FAILED: Tests should fail but didn't")
                sys.exit(1)
            
            # GREEN phase
            green_success, green_results = executor.run_green_phase()
            if not green_success:
                print("\n⚠️  GREEN PHASE INCOMPLETE: Implement TODOs and run again")
                executor.update_requirements_verification()
                sys.exit(1)
            
            # REFACTOR phase
            refactor_success, refactor_results = executor.run_refactor_phase()
            
            executor.update_requirements_verification()
            
            if red_success and green_success and refactor_success:
                print(f"\n{'='*70}")
                print("✅ FULL TDD CYCLE COMPLETE")
                print(f"{'='*70}\n")
                sys.exit(0)
            else:
                sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
