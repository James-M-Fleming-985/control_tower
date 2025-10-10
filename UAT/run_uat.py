#!/usr/bin/env python3
"""
UAT Execution Script for SYSTEM-004-01 AI Code Generation System

This script executes end-to-end User Acceptance Testing by:
1. Running the AI Code Generator on a real feature specification
2. Monitoring the complete TDD cycle (RED → GREEN → REFACTOR)
3. Verifying all artifacts are generated correctly
4. Producing a comprehensive UAT report

Usage:
    python run_uat.py
    python run_uat.py --provider anthropic
    python run_uat.py --verbose
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class UATExecutor:
    """Execute comprehensive UAT for the AI Code Generation System."""
    
    def __init__(self, spec_file=None, provider="openai", verbose=False):
        """Initialize UAT executor."""
        self.uat_dir = Path("/workspaces/control_tower/UAT")
        self.output_dir = self.uat_dir / "output"
        # Default to workflow state management (real production feature)
        if spec_file is None:
            spec_file = "LAYER-UAT-002_workflow_state_management.yaml"
        self.spec_file = self.uat_dir / spec_file if not Path(spec_file).is_absolute() else Path(spec_file)
        self.provider = provider
        self.verbose = verbose
        self.system_root = self.workspace_root / "projects" / "PROJECT-004 AI CODE GENERATOR" / "SYSTEM-004-01 AI CODE GENERATION SYSTEM"
        
        self.uat_results = {
            "test_scenario": spec_file.replace("LAYER-UAT-002_", "").replace(".yaml", "").replace("_", " ").title() if spec_file else "Workflow State Management",
            "test_date": datetime.now().isoformat(),
            "ai_provider": provider,
            "execution": {},
            "artifacts": {},
            "tests": {},
            "overall_result": "PENDING"
        }
        
    def print_header(self, message: str):
        """Print formatted header."""
        print("\n" + "=" * 80)
        print(f"  {message}")
        print("=" * 80 + "\n")
        
    def print_step(self, step: str, message: str):
        """Print step information."""
        print(f"[{step}] {message}")
        
    def check_prerequisites(self) -> bool:
        """Verify all prerequisites are met."""
        self.print_header("Step 1: Checking Prerequisites")
        
        all_good = True
        
        # Check API key
        api_key = os.getenv(f"{self.provider.upper()}_API_KEY")
        if api_key:
            self.print_step("✓", f"{self.provider.upper()}_API_KEY is set")
        else:
            self.print_step("✗", f"{self.provider.upper()}_API_KEY is NOT set")
            print(f"    Please set: export {self.provider.upper()}_API_KEY='your-key-here'")
            all_good = False
            
        # Check YAML file exists
        if self.yaml_file.exists():
            self.print_step("✓", f"UAT YAML file exists: {self.yaml_file}")
        else:
            self.print_step("✗", f"UAT YAML file NOT found: {self.yaml_file}")
            all_good = False
            
        # Check required packages
        required_packages = ["openai", "anthropic", "pytest", "yaml"]
        for package in required_packages:
            try:
                __import__(package)
                self.print_step("✓", f"Package '{package}' is installed")
            except ImportError:
                self.print_step("✗", f"Package '{package}' is NOT installed")
                print(f"    Please install: pip install {package}")
                all_good = False
                
        # Check system root
        if self.system_root.exists():
            self.print_step("✓", f"System root found: {self.system_root}")
        else:
            self.print_step("✗", f"System root NOT found: {self.system_root}")
            all_good = False
            
        if all_good:
            print("\n✅ All prerequisites met! Ready to execute UAT.\n")
        else:
            print("\n❌ Some prerequisites are missing. Please fix them before proceeding.\n")
            
        return all_good
        
    def execute_ai_generation(self) -> bool:
        """Execute the AI Code Generation System."""
        self.print_header("Step 2: Executing AI Code Generation System")
        
        # Prepare output directory
        if self.output_dir.exists():
            self.print_step("INFO", f"Removing existing output directory: {self.output_dir}")
            import shutil
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        
        # Build command
        script_path = self.system_root / "scripts" / "execute_layer.py"
        
        if not script_path.exists():
            self.print_step("✗", f"Execution script not found: {script_path}")
            return False
            
        cmd = [
            sys.executable,
            str(script_path),
            "--yaml-file", str(self.yaml_file),
            "--output-dir", str(self.output_dir),
            "--provider", self.provider,
            "--full-cycle"
        ]
        
        if self.verbose:
            cmd.append("--verbose")
            
        self.print_step("EXEC", f"Running: {' '.join(cmd)}")
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.system_root),
                capture_output=not self.verbose,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.uat_results["execution"]["duration_seconds"] = duration
            self.uat_results["execution"]["duration_minutes"] = round(duration / 60, 2)
            self.uat_results["execution"]["ai_provider"] = self.provider
            
            if result.returncode == 0:
                self.print_step("✓", f"Execution completed successfully in {duration:.1f} seconds")
                self.uat_results["execution"]["status"] = "SUCCESS"
                return True
            else:
                self.print_step("✗", f"Execution failed with return code: {result.returncode}")
                if not self.verbose and result.stderr:
                    print(f"Error output:\n{result.stderr}")
                self.uat_results["execution"]["status"] = "FAILED"
                self.uat_results["execution"]["error"] = result.stderr
                return False
                
        except subprocess.TimeoutExpired:
            self.print_step("✗", "Execution timed out after 10 minutes")
            self.uat_results["execution"]["status"] = "TIMEOUT"
            return False
        except Exception as e:
            self.print_step("✗", f"Execution error: {str(e)}")
            self.uat_results["execution"]["status"] = "ERROR"
            self.uat_results["execution"]["error"] = str(e)
            return False
            
    def verify_artifacts(self) -> bool:
        """Verify all expected artifacts were generated."""
        self.print_header("Step 3: Verifying Generated Artifacts")
        
        all_verified = True
        artifact_counts = {
            "implementation_files": 0,
            "test_files": 0,
            "verification_reports": 0,
            "logs": 0
        }
        
        # Check expected directories
        expected_dirs = [
            self.output_dir / "src" / "orchestration" / "state",
            self.output_dir / "tests" / "layer" / "workflow_state",
            self.output_dir / "Requirements Verification",
            self.output_dir / "Testing Outputs"
        ]
        
        for dir_path in expected_dirs:
            if dir_path.exists():
                self.print_step("✓", f"Directory exists: {dir_path.name}")
            else:
                self.print_step("✗", f"Directory MISSING: {dir_path}")
                all_verified = False
                
        # Check implementation file
        impl_file = self.output_dir / "src" / "orchestration" / "state" / "workflow_state_manager.py"
        if impl_file.exists():
            self.print_step("✓", "Implementation file: workflow_state_manager.py")
            artifact_counts["implementation_files"] += 1
            
            # Check syntax
            try:
                subprocess.run(
                    [sys.executable, "-m", "py_compile", str(impl_file)],
                    check=True,
                    capture_output=True
                )
                self.print_step("✓", "Implementation is syntactically valid")
            except subprocess.CalledProcessError:
                self.print_step("✗", "Implementation has syntax errors!")
                all_verified = False
        else:
            self.print_step("✗", "Implementation file MISSING")
            all_verified = False
            
        # Check test files
        test_files = list((self.output_dir / "tests" / "layer" / "workflow_state").glob("test_*.py"))
        artifact_counts["test_files"] = len(test_files)
        if test_files:
            self.print_step("✓", f"Test files: {len(test_files)} found")
            for test_file in test_files:
                self.print_step("  ", f"- {test_file.name}")
        else:
            self.print_step("✗", "No test files found")
            all_verified = False
            
        # Check verification reports
        verification_dir = self.output_dir / "Requirements Verification"
        if verification_dir.exists():
            reports = list(verification_dir.glob("*.yaml")) + list(verification_dir.glob("*.json"))
            artifact_counts["verification_reports"] = len(reports)
            if reports:
                self.print_step("✓", f"Verification reports: {len(reports)} found")
            else:
                self.print_step("⚠", "No verification reports found")
        else:
            self.print_step("✗", "Verification directory missing")
            all_verified = False
            
        # Check logs
        logs_dir = self.output_dir / "Testing Outputs"
        if logs_dir.exists():
            logs = list(logs_dir.glob("*_phase_log_*.txt"))
            artifact_counts["logs"] = len(logs)
            if logs:
                self.print_step("✓", f"Phase logs: {len(logs)} found")
                # Check for all three phases
                has_red = any("red_phase" in str(log) for log in logs)
                has_green = any("green_phase" in str(log) for log in logs)
                has_refactor = any("refactor_phase" in str(log) for log in logs)
                
                if has_red:
                    self.print_step("  ", "- RED phase log found")
                else:
                    self.print_step("  ✗", "- RED phase log MISSING")
                    all_verified = False
                    
                if has_green:
                    self.print_step("  ", "- GREEN phase log found")
                else:
                    self.print_step("  ✗", "- GREEN phase log MISSING")
                    all_verified = False
                    
                if has_refactor:
                    self.print_step("  ", "- REFACTOR phase log found")
                else:
                    self.print_step("  ✗", "- REFACTOR phase log MISSING")
                    all_verified = False
            else:
                self.print_step("⚠", "No phase logs found")
        else:
            self.print_step("✗", "Logs directory missing")
            all_verified = False
            
        self.uat_results["artifacts"] = artifact_counts
        
        if all_verified:
            print("\n✅ All expected artifacts verified!\n")
        else:
            print("\n❌ Some artifacts are missing or invalid.\n")
            
        return all_verified
        
    def run_tests(self) -> bool:
        """Execute the generated tests and collect results."""
        self.print_header("Step 4: Running Generated Tests")
        
        test_dir = self.output_dir / "tests"
        if not test_dir.exists():
            self.print_step("✗", "Test directory not found")
            return False
            
        # Run pytest
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_dir),
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=" + str(self.output_dir / "test_results.json")
        ]
        
        self.print_step("EXEC", f"Running tests: pytest {test_dir}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.output_dir),
                capture_output=True,
                text=True
            )
            
            # Parse results
            results_file = self.output_dir / "test_results.json"
            if results_file.exists():
                with open(results_file) as f:
                    test_data = json.load(f)
                    summary = test_data.get("summary", {})
                    
                    self.uat_results["tests"] = {
                        "total": summary.get("total", 0),
                        "passed": summary.get("passed", 0),
                        "failed": summary.get("failed", 0),
                        "skipped": summary.get("skipped", 0),
                        "pass_rate": f"{summary.get('passed', 0) / max(summary.get('total', 1), 1) * 100:.1f}%"
                    }
            else:
                # Fallback: parse from pytest output
                lines = result.stdout.split("\n")
                for line in lines:
                    if "passed" in line.lower():
                        self.print_step("INFO", line.strip())
                        
            if result.returncode == 0:
                self.print_step("✓", "All tests PASSED")
                return True
            else:
                self.print_step("✗", "Some tests FAILED")
                print(result.stdout)
                return False
                
        except Exception as e:
            self.print_step("✗", f"Test execution error: {str(e)}")
            return False
            
    def generate_uat_report(self):
        """Generate comprehensive UAT report."""
        self.print_header("Step 5: Generating UAT Report")
        
        # Determine overall result
        if (self.uat_results["execution"].get("status") == "SUCCESS" and
            self.uat_results["artifacts"].get("implementation_files", 0) > 0 and
            self.uat_results["artifacts"].get("test_files", 0) > 0 and
            self.uat_results["tests"].get("failed", 1) == 0):
            self.uat_results["overall_result"] = "✅ PASS"
        else:
            self.uat_results["overall_result"] = "❌ FAIL"
            
        # Save report
        report_file = self.uat_dir / f"uat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.uat_results, f, indent=2)
            
        self.print_step("✓", f"UAT report saved: {report_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("  UAT EXECUTION SUMMARY")
        print("=" * 80)
        print(f"\n📋 Test Scenario: {self.uat_results['test_scenario']}")
        print(f"📅 Execution Date: {self.uat_results['test_date']}")
        print(f"⏱️  Duration: {self.uat_results['execution'].get('duration_minutes', 'N/A')} minutes")
        print(f"🤖 AI Provider: {self.uat_results['execution'].get('ai_provider', 'N/A')}")
        
        print(f"\n📦 Artifacts Generated:")
        print(f"   - Implementation files: {self.uat_results['artifacts'].get('implementation_files', 0)}")
        print(f"   - Test files: {self.uat_results['artifacts'].get('test_files', 0)}")
        print(f"   - Verification reports: {self.uat_results['artifacts'].get('verification_reports', 0)}")
        print(f"   - Logs: {self.uat_results['artifacts'].get('logs', 0)}")
        
        if self.uat_results["tests"]:
            print(f"\n🧪 Test Results:")
            print(f"   - Total: {self.uat_results['tests'].get('total', 0)}")
            print(f"   - Passed: {self.uat_results['tests'].get('passed', 0)}")
            print(f"   - Failed: {self.uat_results['tests'].get('failed', 0)}")
            print(f"   - Pass Rate: {self.uat_results['tests'].get('pass_rate', 'N/A')}")
            
        print(f"\n🎯 OVERALL RESULT: {self.uat_results['overall_result']}")
        print("\n" + "=" * 80 + "\n")
        
    def run(self):
        """Execute complete UAT workflow."""
        print("\n🚀 Starting UAT for SYSTEM-004-01 AI Code Generation System\n")
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("❌ UAT cannot proceed due to missing prerequisites.")
            return False
            
        # Step 2: Execute AI generation
        if not self.execute_ai_generation():
            print("❌ UAT failed during AI code generation.")
            self.generate_uat_report()
            return False
            
        # Step 3: Verify artifacts
        if not self.verify_artifacts():
            print("⚠️  Some artifacts missing, but continuing...")
            
        # Step 4: Run tests
        if not self.run_tests():
            print("⚠️  Some tests failed, but continuing...")
            
        # Step 5: Generate report
        self.generate_uat_report()
        
        # Final result
        if self.uat_results["overall_result"] == "✅ PASS":
            print("🎉 UAT PASSED! System is ready for production deployment.\n")
            return True
        else:
            print("❌ UAT FAILED. Please review the report and fix issues.\n")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Execute UAT for SYSTEM-004-01 AI Code Generation System"
    )
    parser.add_argument(
        "--spec",
        default=None,
        help="UAT specification file (default: LAYER-UAT-002_workflow_state_management.yaml)"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        default="openai",
        help="AI provider to use (default: openai)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output during execution"
    )
    
    args = parser.parse_args()
    
    executor = UATExecutor(spec_file=args.spec, provider=args.provider, verbose=args.verbose)
    success = executor.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
