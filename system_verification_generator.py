#!/usr/bin/env python3
"""
System-Level Verification Generator
Aggregates layer-level verification artifacts to generate system-level testing pyramid and traceability matrix.
Follows the same pattern as layer-level verification to "close the loop" at the system level.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class LayerVerification:
    """Verification data from a single layer."""
    layer_id: str
    layer_name: str
    feature_id: str
    pyramid_data: Dict[str, Any]
    traceability_data: Dict[str, Any]
    test_count: int
    coverage: float


class SystemVerificationGenerator:
    """Generate system-level verification artifacts by aggregating layer data."""
    
    def __init__(self, system_dir: Path, system_id: str, system_name: str):
        """
        Initialize system verification generator.
        
        Args:
            system_dir: Root directory of the system (contains FEATURE-XX directories)
            system_id: System ID (e.g., SYSTEM-CA-006)
            system_name: Human-readable system name
        """
        self.system_dir = system_dir
        self.system_id = system_id
        self.system_name = system_name
        self.layer_verifications: List[LayerVerification] = []
        
    def collect_layer_verifications(self) -> int:
        """
        Discover and collect all layer-level verification artifacts.
        
        Returns:
            Number of layer verifications collected
        """
        print(f"\n📊 Collecting layer verification artifacts from {self.system_dir}...")
        
        # Find all feature directories
        feature_dirs = sorted(self.system_dir.glob("FEATURE-*"))
        
        for feature_dir in feature_dirs:
            if not feature_dir.is_dir():
                continue
                
            feature_id = feature_dir.name
            
            # Find all layer directories within this feature
            layer_dirs = sorted(feature_dir.glob("LAYER-*"))
            
            for layer_dir in layer_dirs:
                if not layer_dir.is_dir():
                    continue
                    
                layer_id = layer_dir.name
                
                # Look for Requirements Verification directory
                verif_dir = layer_dir / "Requirements Verification"
                if not verif_dir.exists():
                    continue
                
                # Find most recent test pyramid report
                pyramids = list(verif_dir.glob("test_pyramid_report_*.yaml"))
                matrices = list(verif_dir.glob("traceability_matrix_*.yaml"))
                
                if not pyramids or not matrices:
                    continue
                
                # Get most recent files
                pyramid_file = max(pyramids, key=lambda p: p.stat().st_mtime)
                matrix_file = max(matrices, key=lambda p: p.stat().st_mtime)
                
                # Load the data
                try:
                    with open(pyramid_file, 'r') as f:
                        pyramid_data = yaml.safe_load(f)
                    with open(matrix_file, 'r') as f:
                        traceability_data = yaml.safe_load(f)
                    
                    # Extract metrics
                    test_count = self._extract_test_count(pyramid_data)
                    coverage = self._extract_coverage(pyramid_data)
                    
                    layer_verif = LayerVerification(
                        layer_id=layer_id,
                        layer_name=layer_dir.name,
                        feature_id=feature_id,
                        pyramid_data=pyramid_data,
                        traceability_data=traceability_data,
                        test_count=test_count,
                        coverage=coverage
                    )
                    
                    self.layer_verifications.append(layer_verif)
                    print(f"  ✓ {feature_id}/{layer_id}: {test_count} tests, {coverage:.1f}% coverage")
                    
                except Exception as e:
                    print(f"  ⚠️ Error loading {layer_id}: {e}")
                    continue
        
        print(f"\n✅ Collected {len(self.layer_verifications)} layer verifications")
        return len(self.layer_verifications)
    
    def _extract_test_count(self, pyramid_data: Dict) -> int:
        """Extract total test count from pyramid data."""
        metrics = pyramid_data.get('test_pyramid_metrics', {})
        return (
            metrics.get('unit_tests', 0) +
            metrics.get('integration_tests', 0) +
            metrics.get('system_tests', 0)
        )
    
    def _extract_coverage(self, pyramid_data: Dict) -> float:
        """Extract coverage percentage from pyramid data."""
        metrics = pyramid_data.get('test_pyramid_metrics', {})
        coverage_str = metrics.get('code_coverage', '0%')
        
        # Handle various formats: "85%", "85", 85, etc.
        if isinstance(coverage_str, (int, float)):
            return float(coverage_str)
        
        if isinstance(coverage_str, str):
            return float(coverage_str.rstrip('%'))
        
        return 0.0
    
    def generate_system_test_pyramid(self) -> Dict[str, Any]:
        """
        Generate system-level test pyramid by aggregating layer pyramids.
        
        Returns:
            System test pyramid data structure
        """
        total_unit = 0
        total_integration = 0
        total_system = 0
        total_coverage = 0.0
        
        feature_breakdown = {}
        
        for layer in self.layer_verifications:
            metrics = layer.pyramid_data.get('test_pyramid_metrics', {})
            
            unit = metrics.get('unit_tests', 0)
            integration = metrics.get('integration_tests', 0)
            system = metrics.get('system_tests', 0)
            
            total_unit += unit
            total_integration += integration
            total_system += system
            total_coverage += layer.coverage
            
            # Track by feature
            if layer.feature_id not in feature_breakdown:
                feature_breakdown[layer.feature_id] = {
                    'unit_tests': 0,
                    'integration_tests': 0,
                    'system_tests': 0,
                    'layers': []
                }
            
            feature_breakdown[layer.feature_id]['unit_tests'] += unit
            feature_breakdown[layer.feature_id]['integration_tests'] += integration
            feature_breakdown[layer.feature_id]['system_tests'] += system
            feature_breakdown[layer.feature_id]['layers'].append(layer.layer_id)
        
        total_tests = total_unit + total_integration + total_system
        avg_coverage = total_coverage / len(self.layer_verifications) if self.layer_verifications else 0.0
        
        pyramid = {
            'metadata': {
                'system_id': self.system_id,
                'system_name': self.system_name,
                'generated_at': datetime.now().isoformat(),
                'total_layers': len(self.layer_verifications),
                'total_features': len(feature_breakdown),
                'generator': 'SystemVerificationGenerator'
            },
            'pyramid_summary': {
                'total_tests': total_tests,
                'unit_tests': total_unit,
                'integration_tests': total_integration,
                'system_tests': total_system,
                'unit_percentage': round(total_unit / total_tests * 100, 1) if total_tests else 0,
                'integration_percentage': round(total_integration / total_tests * 100, 1) if total_tests else 0,
                'system_percentage': round(total_system / total_tests * 100, 1) if total_tests else 0
            },
            'coverage': {
                'average_coverage': round(avg_coverage, 1),
                'layers_above_80_percent': sum(1 for l in self.layer_verifications if l.coverage >= 80),
                'layers_above_90_percent': sum(1 for l in self.layer_verifications if l.coverage >= 90),
                'coverage_status': 'EXCELLENT' if avg_coverage >= 90 else 'GOOD' if avg_coverage >= 80 else 'NEEDS_IMPROVEMENT'
            },
            'feature_breakdown': feature_breakdown,
            'layer_details': [
                {
                    'layer_id': l.layer_id,
                    'feature_id': l.feature_id,
                    'test_count': l.test_count,
                    'coverage': round(l.coverage, 1)
                }
                for l in self.layer_verifications
            ]
        }
        
        return pyramid
    
    def generate_system_traceability_matrix(self) -> Dict[str, Any]:
        """
        Generate system-level traceability matrix.
        
        Returns:
            System traceability matrix data structure
        """
        feature_traceability = {}
        all_requirements = []
        requirements_verified = 0
        requirements_total = 0
        
        for layer in self.layer_verifications:
            trace_data = layer.traceability_data
            
            # Extract requirements from layer traceability
            layer_reqs = trace_data.get('requirements', [])
            all_requirements.extend(layer_reqs)
            
            for req in layer_reqs:
                requirements_total += 1
                if req.get('status') in ['VERIFIED', 'PASS', 'COMPLETE']:
                    requirements_verified += 1
            
            # Group by feature
            if layer.feature_id not in feature_traceability:
                feature_traceability[layer.feature_id] = {
                    'layers': [],
                    'total_requirements': 0,
                    'verified_requirements': 0,
                    'total_tests': 0
                }
            
            feature_traceability[layer.feature_id]['layers'].append({
                'layer_id': layer.layer_id,
                'requirements': len(layer_reqs),
                'tests': layer.test_count,
                'coverage': round(layer.coverage, 1)
            })
            feature_traceability[layer.feature_id]['total_requirements'] += len(layer_reqs)
            feature_traceability[layer.feature_id]['total_tests'] += layer.test_count
        
        verification_rate = round(requirements_verified / requirements_total * 100, 1) if requirements_total else 0
        
        matrix = {
            'metadata': {
                'system_id': self.system_id,
                'system_name': self.system_name,
                'generated_at': datetime.now().isoformat(),
                'total_layers': len(self.layer_verifications),
                'total_features': len(feature_traceability),
                'generator': 'SystemVerificationGenerator'
            },
            'verification_summary': {
                'total_requirements': requirements_total,
                'verified_requirements': requirements_verified,
                'verification_rate': verification_rate,
                'total_tests': sum(l.test_count for l in self.layer_verifications),
                'status': 'COMPLETE' if verification_rate >= 95 else 'IN_PROGRESS'
            },
            'feature_traceability': feature_traceability,
            'layer_summary': [
                {
                    'layer_id': l.layer_id,
                    'feature_id': l.feature_id,
                    'test_count': l.test_count,
                    'coverage': round(l.coverage, 1),
                    'status': 'VERIFIED' if l.coverage >= 80 else 'NEEDS_WORK'
                }
                for l in self.layer_verifications
            ]
        }
        
        return matrix
    
    def save_verification_artifacts(self) -> Tuple[Path, Path]:
        """
        Save system-level verification artifacts to disk.
        
        Returns:
            Tuple of (pyramid_path, matrix_path)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        pyramid_data = self.generate_system_test_pyramid()
        matrix_data = self.generate_system_traceability_matrix()
        
        # Save to system directory
        pyramid_path = self.system_dir / f"SYSTEM_TEST_PYRAMID_{timestamp}.yaml"
        matrix_path = self.system_dir / f"SYSTEM_TRACEABILITY_MATRIX_{timestamp}.yaml"
        
        with open(pyramid_path, 'w') as f:
            yaml.dump(pyramid_data, f, default_flow_style=False, sort_keys=False)
        
        with open(matrix_path, 'w') as f:
            yaml.dump(matrix_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n✅ System verification artifacts saved:")
        print(f"   📊 Test Pyramid: {pyramid_path.name}")
        print(f"   📋 Traceability Matrix: {matrix_path.name}")
        
        # Print summary
        pyramid_summary = pyramid_data['pyramid_summary']
        verif_summary = matrix_data['verification_summary']
        
        print(f"\n📈 System Verification Summary:")
        print(f"   Total Tests: {pyramid_summary['total_tests']}")
        print(f"   Unit: {pyramid_summary['unit_tests']} ({pyramid_summary['unit_percentage']}%)")
        print(f"   Integration: {pyramid_summary['integration_tests']} ({pyramid_summary['integration_percentage']}%)")
        print(f"   System: {pyramid_summary['system_tests']} ({pyramid_summary['system_percentage']}%)")
        print(f"   Average Coverage: {pyramid_data['coverage']['average_coverage']}%")
        print(f"   Requirements Verified: {verif_summary['verified_requirements']}/{verif_summary['total_requirements']} ({verif_summary['verification_rate']}%)")
        
        return pyramid_path, matrix_path


def main():
    """Example usage: generate system verification for CA-006."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate system-level verification artifacts")
    parser.add_argument("system_dir", help="Path to system directory")
    parser.add_argument("--system-id", required=True, help="System ID (e.g., SYSTEM-CA-006)")
    parser.add_argument("--system-name", required=True, help="System name")
    
    args = parser.parse_args()
    
    system_dir = Path(args.system_dir)
    if not system_dir.exists():
        print(f"❌ System directory not found: {system_dir}")
        return 1
    
    generator = SystemVerificationGenerator(
        system_dir=system_dir,
        system_id=args.system_id,
        system_name=args.system_name
    )
    
    count = generator.collect_layer_verifications()
    if count == 0:
        print("⚠️ No layer verifications found!")
        return 1
    
    generator.save_verification_artifacts()
    
    print("\n✅ System verification generation complete!")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
