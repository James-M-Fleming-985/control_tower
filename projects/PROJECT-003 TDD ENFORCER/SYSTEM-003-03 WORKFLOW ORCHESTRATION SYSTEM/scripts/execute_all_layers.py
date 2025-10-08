#!/usr/bin/env python3
"""
Batch Layer Executor

Executes all layers in dependency order with full TDD cycle.
Collects all evidence and generates comprehensive reports.

Usage:
    python execute_all_layers.py
    python execute_all_layers.py --feature FEATURE-003-03-02
    python execute_all_layers.py --phase red
    python execute_all_layers.py --parallel
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class BatchLayerExecutor:
    """Executes multiple layers in dependency order."""
    
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.system_yaml = self._load_system_yaml()
        self.execution_results = {}
        
    def _load_system_yaml(self) -> dict:
        """Load system requirements YAML."""
        yaml_file = self.system_root / "SYSTEM-003-03_workflow_orchestration_system.yaml"
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    def get_all_layers(self) -> List[Tuple[str, str, int]]:
        """Get all layers with their features and priorities."""
        layers = []
        
        # Priority order for features (2→1→4→3)
        feature_priority = {
            'FEATURE-003-03-02': 1,  # Prerequisites (foundation)
            'FEATURE-003-03-01': 2,  # Orchestration (core)
            'FEATURE-003-03-04': 3,  # Monitoring (observability)
            'FEATURE-003-03-03': 4,  # Failure Handling (integration)
        }
        
        for feature_folder in sorted(self.system_root.iterdir()):
            if not feature_folder.is_dir() or not feature_folder.name.startswith("FEATURE-"):
                continue
            
            feature_id = feature_folder.name.split()[0]
            priority = feature_priority.get(feature_id, 999)
            
            for layer_folder in sorted(feature_folder.iterdir()):
                if layer_folder.is_dir() and layer_folder.name.startswith("LAYER-"):
                    layer_id = layer_folder.name.split()[0]
                    layers.append((layer_id, feature_id, priority))
        
        # Sort by priority then layer ID
        layers.sort(key=lambda x: (x[2], x[0]))
        
        return layers
    
    def execute_layer(self, layer_id: str, phase: str = 'full-cycle') -> Tuple[bool, Dict]:
        """Execute a single layer."""
        print(f"\n{'='*70}")
        print(f"Executing Layer: {layer_id} (Phase: {phase})")
        print(f"{'='*70}")
        
        script_path = self.system_root / "scripts" / "execute_layer.py"
        
        cmd = [
            'python3',
            str(script_path),
            '--layer', layer_id,
            '--phase', phase,
            '--system-root', str(self.system_root)
        ]
        
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
            
            execution_result = {
                'layer_id': layer_id,
                'phase': phase,
                'status': 'passed' if success else 'failed',
                'returncode': result.returncode,
                'timestamp': datetime.now().isoformat()
            }
            
            self.execution_results[layer_id] = execution_result
            
            return success, execution_result
            
        except Exception as e:
            print(f"❌ Error executing layer: {e}")
            return False, {'status': 'error', 'error': str(e)}
    
    def execute_all_sequential(self, phase: str = 'full-cycle') -> bool:
        """Execute all layers sequentially in dependency order."""
        print(f"\n{'#'*70}")
        print(f"# BATCH LAYER EXECUTION (SEQUENTIAL)")
        print(f"# Phase: {phase}")
        print(f"{'#'*70}\n")
        
        layers = self.get_all_layers()
        
        print(f"Execution order ({len(layers)} layers):")
        for i, (layer_id, feature_id, priority) in enumerate(layers, 1):
            print(f"  {i}. {layer_id} ({feature_id})")
        print()
        
        all_passed = True
        for layer_id, feature_id, priority in layers:
            success, results = self.execute_layer(layer_id, phase)
            all_passed = all_passed and success
            
            if not success and phase == 'full-cycle':
                print(f"\n⚠️  Layer {layer_id} failed. Continue? (y/n)")
                # For automation, continue anyway
                continue
        
        return all_passed
    
    def execute_all_parallel(self, phase: str = 'full-cycle', max_workers: int = 4) -> bool:
        """Execute layers in parallel where dependencies allow."""
        print(f"\n{'#'*70}")
        print(f"# BATCH LAYER EXECUTION (PARALLEL)")
        print(f"# Phase: {phase}")
        print(f"# Max Workers: {max_workers}")
        print(f"{'#'*70}\n")
        
        layers = self.get_all_layers()
        
        # Group layers by priority (can run same priority in parallel)
        priority_groups = {}
        for layer_id, feature_id, priority in layers:
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append((layer_id, feature_id))
        
        all_passed = True
        
        for priority in sorted(priority_groups.keys()):
            layer_group = priority_groups[priority]
            print(f"\n{'='*70}")
            print(f"Executing Priority {priority} ({len(layer_group)} layers in parallel)")
            print(f"{'='*70}\n")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.execute_layer, layer_id, phase): layer_id
                    for layer_id, _ in layer_group
                }
                
                for future in as_completed(futures):
                    layer_id = futures[future]
                    try:
                        success, results = future.result()
                        all_passed = all_passed and success
                    except Exception as e:
                        print(f"❌ Exception executing {layer_id}: {e}")
                        all_passed = False
        
        return all_passed
    
    def execute_feature_layers(self, feature_id: str, phase: str = 'full-cycle') -> bool:
        """Execute all layers for a specific feature."""
        print(f"\n{'#'*70}")
        print(f"# EXECUTING FEATURE LAYERS")
        print(f"# Feature: {feature_id}")
        print(f"# Phase: {phase}")
        print(f"{'#'*70}\n")
        
        layers = [
            (lid, fid, pri)
            for lid, fid, pri in self.get_all_layers()
            if fid == feature_id
        ]
        
        if not layers:
            print(f"⚠️  No layers found for {feature_id}")
            return False
        
        print(f"Found {len(layers)} layers for {feature_id}:")
        for layer_id, _, _ in layers:
            print(f"  - {layer_id}")
        print()
        
        all_passed = True
        for layer_id, _, _ in layers:
            success, results = self.execute_layer(layer_id, phase)
            all_passed = all_passed and success
        
        return all_passed
    
    def generate_batch_report(self) -> str:
        """Generate batch execution report."""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"BATCH LAYER EXECUTION REPORT")
        report.append(f"{'='*70}")
        report.append(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Layers: {len(self.execution_results)}")
        report.append("")
        
        # Group by status
        passed = [k for k, v in self.execution_results.items() if v['status'] == 'passed']
        failed = [k for k, v in self.execution_results.items() if v['status'] == 'failed']
        errors = [k for k, v in self.execution_results.items() if v['status'] == 'error']
        
        report.append("EXECUTION SUMMARY")
        report.append("-" * 70)
        report.append(f"Passed: {len(passed)}")
        report.append(f"Failed: {len(failed)}")
        report.append(f"Errors: {len(errors)}")
        report.append("")
        
        if passed:
            report.append("PASSED LAYERS")
            report.append("-" * 70)
            for layer_id in sorted(passed):
                report.append(f"  ✅ {layer_id}")
            report.append("")
        
        if failed:
            report.append("FAILED LAYERS")
            report.append("-" * 70)
            for layer_id in sorted(failed):
                report.append(f"  ❌ {layer_id}")
            report.append("")
        
        if errors:
            report.append("ERRORS")
            report.append("-" * 70)
            for layer_id in sorted(errors):
                error = self.execution_results[layer_id].get('error', 'Unknown error')
                report.append(f"  ⚠️  {layer_id}: {error}")
            report.append("")
        
        # Overall status
        all_passed = len(failed) == 0 and len(errors) == 0
        report.append("="* 70)
        if all_passed:
            report.append("✅ BATCH EXECUTION COMPLETED SUCCESSFULLY")
        else:
            report.append("❌ BATCH EXECUTION COMPLETED WITH FAILURES")
        report.append("="* 70)
        report.append("")
        
        return "\n".join(report)
    
    def save_execution_evidence(self):
        """Save batch execution evidence."""
        evidence_file = self.system_root / f"batch_execution_evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        evidence = {
            'execution_timestamp': datetime.now().isoformat(),
            'total_layers': len(self.execution_results),
            'results': self.execution_results
        }
        
        with open(evidence_file, 'w') as f:
            json.dump(evidence, f, indent=2)
        
        print(f"\n📄 Execution evidence saved to: {evidence_file}")


def main():
    parser = argparse.ArgumentParser(description='Execute all layers in batch')
    parser.add_argument('--system-root', type=Path,
                       default=Path(__file__).parent.parent,
                       help='Path to SYSTEM-003-03 root directory')
    parser.add_argument('--feature', help='Execute only layers for specific feature')
    parser.add_argument('--phase', choices=['red', 'green', 'refactor', 'full-cycle'],
                       default='full-cycle',
                       help='TDD phase to execute')
    parser.add_argument('--parallel', action='store_true',
                       help='Execute layers in parallel where possible')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Maximum parallel workers')
    
    args = parser.parse_args()
    
    try:
        executor = BatchLayerExecutor(args.system_root)
        
        if args.feature:
            success = executor.execute_feature_layers(args.feature, args.phase)
        elif args.parallel:
            success = executor.execute_all_parallel(args.phase, args.max_workers)
        else:
            success = executor.execute_all_sequential(args.phase)
        
        # Generate report
        report = executor.generate_batch_report()
        print(report)
        
        # Save evidence
        executor.save_execution_evidence()
        
        # Save report
        report_file = args.system_root / f"batch_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
