#!/usr/bin/env python3
"""
Requirements Traceability Validator

Auto-discovers # REQ-XXX comments in code, compares with manually_registered
YAMLs, detects orphaned code, validates all acceptance criteria have tests
and implementations.

Usage:
    python validate_traceability.py
    python validate_traceability.py --layer LAYER-003-03-01-01
    python validate_traceability.py --feature FEATURE-003-03-01
    python validate_traceability.py --fix-orphans
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


class TraceabilityValidator:
    """Validates requirements traceability."""
    
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.project_root = system_root.parent.parent.parent
        self.auto_discovered = {}  # {req_id: [file_paths]}
        self.manually_registered = {}  # {req_id: yaml_data}
        self.orphaned_code = []
        self.missing_implementations = []
        
    def scan_codebase_for_requirements(self) -> Dict[str, List[str]]:
        """Scan all Python files for # REQ-XXX comments."""
        print(f"\n{'='*70}")
        print(f"Scanning Codebase for Requirement Comments")
        print(f"{'='*70}")
        
        req_pattern = re.compile(r'#\s*REQ-([A-Z0-9-]+)')
        discovered = {}
        
        # Scan src/ and implementation directories
        search_dirs = [
            self.project_root / 'src',
            self.project_root / 'lib',
            self.project_root / 'app',
        ]
        
        file_count = 0
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            for py_file in search_dir.rglob('*.py'):
                file_count += 1
                try:
                    with open(py_file, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            matches = req_pattern.findall(line)
                            for match in matches:
                                req_id = f"REQ-{match}"
                                location = f"{py_file}:{line_num}"
                                
                                if req_id not in discovered:
                                    discovered[req_id] = []
                                discovered[req_id].append(location)
                except Exception as e:
                    print(f"⚠️  Error scanning {py_file}: {e}")
        
        print(f"Scanned {file_count} Python files")
        print(f"Found {len(discovered)} unique requirement references")
        
        self.auto_discovered = discovered
        return discovered
    
    def load_manual_registrations(self, scope: str = 'system') -> Dict:
        """Load manually registered requirements from YAMLs."""
        print(f"\n{'='*70}")
        print(f"Loading Manual Requirement Registrations")
        print(f"{'='*70}")
        
        registered = {}
        
        # Load from layer, feature, and system YAMLs
        yaml_files = list(self.system_root.rglob('*.yaml'))
        
        # Filter out verification templates
        yaml_files = [
            f for f in yaml_files
            if 'requirements_verification' not in str(f)
        ]
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Extract requirement_id
                metadata = data.get('metadata', {})
                req_id = metadata.get('requirement_id')
                
                if not req_id:
                    continue
                
                # Get traceability section
                traceability = data.get('traceability', {})
                manually_reg = traceability.get('manually_registered', [])
                
                if manually_reg:
                    registered[req_id] = {
                        'yaml_file': str(yaml_file),
                        'manually_registered': manually_reg,
                        'metadata': metadata
                    }
                
                # Also check acceptance criteria
                acceptance_criteria = data.get('acceptance_criteria', [])
                for criterion in acceptance_criteria:
                    criterion_id = criterion.get('criterion', '').split(':')[0]
                    if criterion_id:
                        registered[criterion_id] = {
                            'yaml_file': str(yaml_file),
                            'criterion': criterion,
                            'parent_requirement': req_id
                        }
                
            except Exception as e:
                print(f"⚠️  Error loading {yaml_file}: {e}")
        
        print(f"Loaded {len(registered)} manual registrations from {len(yaml_files)} YAML files")
        
        self.manually_registered = registered
        return registered
    
    def compare_auto_vs_manual(self) -> Dict:
        """Compare auto-discovered vs manually registered requirements."""
        print(f"\n{'='*70}")
        print(f"Comparing Auto-Discovered vs Manual Registrations")
        print(f"{'='*70}")
        
        auto_req_ids = set(self.auto_discovered.keys())
        manual_req_ids = set(self.manually_registered.keys())
        
        # Find mismatches
        only_in_code = auto_req_ids - manual_req_ids
        only_in_yaml = manual_req_ids - auto_req_ids
        in_both = auto_req_ids & manual_req_ids
        
        comparison = {
            'auto_discovered_count': len(auto_req_ids),
            'manually_registered_count': len(manual_req_ids),
            'matching_count': len(in_both),
            'only_in_code': list(only_in_code),
            'only_in_yaml': list(only_in_yaml),
            'matches': list(in_both),
            'compliance': len(in_both) / len(auto_req_ids) if auto_req_ids else 0
        }
        
        # Print results
        print(f"\nAuto-Discovered Requirements: {comparison['auto_discovered_count']}")
        print(f"Manually Registered Requirements: {comparison['manually_registered_count']}")
        print(f"Matching: {comparison['matching_count']}")
        print(f"Compliance: {comparison['compliance']:.1%}")
        
        if only_in_code:
            print(f"\n⚠️  Found {len(only_in_code)} requirements in code but not in YAML:")
            for req_id in sorted(only_in_code)[:10]:  # Show first 10
                locations = self.auto_discovered[req_id]
                print(f"  - {req_id} (in {len(locations)} locations)")
                for loc in locations[:3]:  # Show first 3 locations
                    print(f"      {loc}")
        
        if only_in_yaml:
            print(f"\n⚠️  Found {len(only_in_yaml)} requirements in YAML but not in code:")
            for req_id in sorted(only_in_yaml)[:10]:
                yaml_file = self.manually_registered[req_id].get('yaml_file', 'unknown')
                print(f"  - {req_id} (in {Path(yaml_file).name})")
        
        return comparison
    
    def detect_orphaned_code(self) -> List[Dict]:
        """Detect code files with no requirement comments."""
        print(f"\n{'='*70}")
        print(f"Detecting Orphaned Code (No Requirement Comments)")
        print(f"{'='*70}")
        
        orphaned = []
        
        # Get all files that have requirement comments
        files_with_reqs = set()
        for locations in self.auto_discovered.values():
            for location in locations:
                file_path = location.split(':')[0]
                files_with_reqs.add(file_path)
        
        # Scan all Python files
        search_dirs = [
            self.project_root / 'src',
            self.project_root / 'lib',
            self.project_root / 'app',
        ]
        
        all_files = set()
        for search_dir in search_dirs:
            if search_dir.exists():
                for py_file in search_dir.rglob('*.py'):
                    # Skip __init__.py and test files
                    if py_file.name == '__init__.py' or 'test' in py_file.name:
                        continue
                    all_files.add(str(py_file))
        
        # Find orphaned files
        orphaned_files = all_files - files_with_reqs
        
        for file_path in sorted(orphaned_files):
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    # Count non-empty, non-comment lines
                    code_lines = [
                        l for l in lines
                        if l.strip() and not l.strip().startswith('#')
                    ]
                    
                    if len(code_lines) > 10:  # Only report substantial files
                        orphaned.append({
                            'file': file_path,
                            'lines_of_code': len(code_lines)
                        })
            except Exception:
                pass
        
        print(f"Found {len(orphaned)} orphaned files (>10 LOC, no requirement comments)")
        
        if orphaned:
            print("\nTop 10 Orphaned Files:")
            for item in sorted(orphaned, key=lambda x: x['lines_of_code'], reverse=True)[:10]:
                print(f"  - {item['file']} ({item['lines_of_code']} LOC)")
        
        self.orphaned_code = orphaned
        return orphaned
    
    def validate_acceptance_criteria_coverage(self, layer_id: str = None) -> Dict:
        """Validate all acceptance criteria have tests and implementations."""
        print(f"\n{'='*70}")
        print(f"Validating Acceptance Criteria Coverage")
        if layer_id:
            print(f"Scope: {layer_id}")
        print(f"{'='*70}")
        
        coverage = {
            'total_criteria': 0,
            'with_tests': 0,
            'with_implementation': 0,
            'fully_covered': 0,
            'missing_tests': [],
            'missing_implementation': []
        }
        
        # Find relevant YAMLs
        if layer_id:
            yaml_files = list(self.system_root.rglob(f"{layer_id}_*.yaml"))
        else:
            yaml_files = list(self.system_root.rglob('LAYER-*.yaml'))
        
        # Exclude verification templates
        yaml_files = [
            f for f in yaml_files
            if 'requirements_verification' not in str(f)
        ]
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                acceptance_criteria = data.get('acceptance_criteria', [])
                
                for criterion in acceptance_criteria:
                    coverage['total_criteria'] += 1
                    
                    criterion_id = criterion.get('criterion', '').split(':')[0]
                    test_file = criterion.get('test_file', '')
                    status = criterion.get('status', 'not_implemented')
                    
                    # Check if test file exists
                    has_test = False
                    if test_file and test_file != 'Unknown':
                        test_path = self.project_root / test_file
                        has_test = test_path.exists()
                    
                    if has_test:
                        coverage['with_tests'] += 1
                    else:
                        coverage['missing_tests'].append({
                            'criterion': criterion_id,
                            'yaml': yaml_file.name,
                            'test_file': test_file
                        })
                    
                    # Check implementation status
                    has_implementation = status == 'implemented'
                    
                    if has_implementation:
                        coverage['with_implementation'] += 1
                    else:
                        coverage['missing_implementation'].append({
                            'criterion': criterion_id,
                            'yaml': yaml_file.name,
                            'status': status
                        })
                    
                    if has_test and has_implementation:
                        coverage['fully_covered'] += 1
                
            except Exception as e:
                print(f"⚠️  Error processing {yaml_file}: {e}")
        
        # Print results
        print(f"\nTotal Acceptance Criteria: {coverage['total_criteria']}")
        print(f"With Tests: {coverage['with_tests']} ({coverage['with_tests']/coverage['total_criteria']:.1%})")
        print(f"With Implementation: {coverage['with_implementation']} ({coverage['with_implementation']/coverage['total_criteria']:.1%})")
        print(f"Fully Covered: {coverage['fully_covered']} ({coverage['fully_covered']/coverage['total_criteria']:.1%})")
        
        if coverage['missing_tests']:
            print(f"\n⚠️  {len(coverage['missing_tests'])} criteria missing tests:")
            for item in coverage['missing_tests'][:10]:
                print(f"  - {item['criterion']} ({item['yaml']})")
        
        if coverage['missing_implementation']:
            print(f"\n⚠️  {len(coverage['missing_implementation'])} criteria not implemented:")
            for item in coverage['missing_implementation'][:10]:
                print(f"  - {item['criterion']} ({item['yaml']}) - status: {item['status']}")
        
        return coverage
    
    def generate_traceability_report(self, comparison: Dict, coverage: Dict) -> str:
        """Generate comprehensive traceability report."""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"REQUIREMENTS TRACEABILITY REPORT")
        report.append(f"{'='*70}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Auto vs Manual Comparison
        report.append("AUTO-DISCOVERED VS MANUAL REGISTRATION")
        report.append("-" * 70)
        report.append(f"Auto-Discovered: {comparison['auto_discovered_count']}")
        report.append(f"Manually Registered: {comparison['manually_registered_count']}")
        report.append(f"Matching: {comparison['matching_count']}")
        report.append(f"Compliance: {comparison['compliance']:.1%}")
        report.append("")
        
        if comparison['only_in_code']:
            report.append(f"Requirements in Code but not YAML: {len(comparison['only_in_code'])}")
            for req_id in sorted(comparison['only_in_code'])[:5]:
                report.append(f"  - {req_id}")
            report.append("")
        
        if comparison['only_in_yaml']:
            report.append(f"Requirements in YAML but not Code: {len(comparison['only_in_yaml'])}")
            for req_id in sorted(comparison['only_in_yaml'])[:5]:
                report.append(f"  - {req_id}")
            report.append("")
        
        # Orphaned Code
        if self.orphaned_code:
            report.append("ORPHANED CODE (No Requirement Comments)")
            report.append("-" * 70)
            report.append(f"Files with no requirement comments: {len(self.orphaned_code)}")
            for item in self.orphaned_code[:5]:
                report.append(f"  - {Path(item['file']).name} ({item['lines_of_code']} LOC)")
            report.append("")
        
        # Acceptance Criteria Coverage
        report.append("ACCEPTANCE CRITERIA COVERAGE")
        report.append("-" * 70)
        report.append(f"Total Criteria: {coverage['total_criteria']}")
        report.append(f"With Tests: {coverage['with_tests']} ({coverage['with_tests']/coverage['total_criteria']:.1%})")
        report.append(f"Fully Implemented: {coverage['with_implementation']} ({coverage['with_implementation']/coverage['total_criteria']:.1%})")
        report.append(f"Fully Covered: {coverage['fully_covered']} ({coverage['fully_covered']/coverage['total_criteria']:.1%})")
        report.append("")
        
        # Overall Assessment
        overall_compliant = (
            comparison['compliance'] >= 0.90 and
            len(self.orphaned_code) == 0 and
            coverage['fully_covered'] / coverage['total_criteria'] >= 0.80
        )
        
        report.append("="* 70)
        if overall_compliant:
            report.append("✅ TRACEABILITY VALIDATION PASSED")
        else:
            report.append("⚠️  TRACEABILITY VALIDATION HAS ISSUES")
        report.append("="* 70)
        report.append("")
        
        return "\n".join(report)


def main():
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description='Validate requirements traceability'
    )
    parser.add_argument(
        '--system-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Path to SYSTEM-003-03 root directory'
    )
    parser.add_argument(
        '--layer',
        help='Validate specific layer only'
    )
    parser.add_argument(
        '--feature',
        help='Validate specific feature only'
    )
    parser.add_argument(
        '--fix-orphans',
        action='store_true',
        help='Generate skeleton requirement comments for orphaned files'
    )
    
    args = parser.parse_args()
    
    try:
        validator = TraceabilityValidator(args.system_root)
        
        print(f"\n{'#'*70}")
        print(f"# REQUIREMENTS TRACEABILITY VALIDATION")
        print(f"{'#'*70}\n")
        
        # Scan codebase
        validator.scan_codebase_for_requirements()
        
        # Load manual registrations
        validator.load_manual_registrations()
        
        # Compare
        comparison = validator.compare_auto_vs_manual()
        
        # Detect orphaned code
        validator.detect_orphaned_code()
        
        # Validate acceptance criteria coverage
        coverage = validator.validate_acceptance_criteria_coverage(
            layer_id=args.layer
        )
        
        # Generate report
        report = validator.generate_traceability_report(comparison, coverage)
        print(report)
        
        # Save report
        report_path = args.system_root / f"traceability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_path}")
        
        # Exit with appropriate code
        compliant = (
            comparison['compliance'] >= 0.90 and
            len(validator.orphaned_code) == 0 and
            coverage['fully_covered'] / coverage['total_criteria'] >= 0.80
        )
        sys.exit(0 if compliant else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
