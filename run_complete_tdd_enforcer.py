#!/usr/bin/env python3
"""
Complete TDD Workflow Enforcer - Stages 1-10
Comprehensive Test-Driven Development workflow automation

This is the MAIN TDD enforcer that orchestrates all 10 stage gates:
Stages 1-7: Core TDD workflow (existing)
Stages 8-10: Extended validation (new)

This enforcer must be RUNNING before any development begins.

Created: 2025-09-16
Phase: Complete TDD Workflow Implementation
Component: Main TDD Orchestrator
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import core TDD enforcer (stages 1-7)
    from legacy.utilities.tdd_workflow_enforcer import TDDWorkflowEnforcer
    # Import extended TDD enforcer (stages 8-10)
    from src.tools.development.tdd_extended_enforcer import TDDExtendedEnforcer
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("⚠️  Please ensure all TDD enforcer modules are available")
    sys.exit(1)


class CompleteTDDEnforcer:
    """
    Complete TDD Workflow Enforcer (Stages 1-10)
    
    Orchestrates the full TDD workflow with all 10 stage gates:
    
    CORE STAGES (1-7):
    1. Requirements File Validation
    2. Parsing Completion Verification
    3. Test Generation Verification
    4. RED Phase Validation
    5. GREEN Phase Implementation Quality
    6. REFACTOR Analysis
    7. REFACTOR Complete
    
    EXTENDED STAGES (8-10):
    8. Testing Pyramid Validation (Unit/Integration/E2E)
    9. Requirements Compliance Verification (Traceability)
    10. Layer Completion Certification (Next layer activation)
    """
    
    def __init__(self, project_root: str = "/workspaces/control_tower"):
        """Initialize complete TDD enforcer"""
        self.project_root = Path(project_root)
        
        # Initialize core enforcer (stages 1-7)
        self.core_enforcer = TDDWorkflowEnforcer(str(project_root))
        
        # Initialize extended enforcer (stages 8-10)  
        self.extended_enforcer = TDDExtendedEnforcer(str(project_root))
        
        print("\033[95m🔥 COMPLETE TDD ENFORCER INITIALIZED - ALL 10 STAGES ACTIVE\033[0m")
        print("\033[96m   Core Stages 1-7: Requirements → Tests → TDD → Refactor\033[0m")
        print("\033[96m   Extended Stages 8-10: Testing Pyramid → Compliance → Certification\033[0m")
        print()
    
    def enforce_complete_tdd_workflow(self, requirements_file: str, layer_name: str = "current", next_layer: str = None) -> Dict[str, Any]:
        """
        Execute the complete 10-stage TDD workflow
        
        Args:
            requirements_file: Path to requirements document
            layer_name: Name of layer being developed
            next_layer: Name of next layer (for stage 10)
            
        Returns:
            Dict with complete workflow results
        """
        print(f"\033[95m🚀 EXECUTING COMPLETE TDD WORKFLOW: {layer_name} layer\033[0m")
        print(f"📋 Requirements: {requirements_file}")
        print(f"🎯 Target: {layer_name} → {next_layer or 'Integration'}")
        print("=" * 80)
        
        workflow_results = {
            "layer_name": layer_name,
            "next_layer": next_layer,
            "requirements_file": requirements_file,
            "workflow_complete": False,
            "stages_passed": 0,
            "stages_total": 10,
            "stage_results": {},
            "final_status": "in_progress",
            "completion_certificate": None,
            "next_commands": [],
            "timestamp": time.time()
        }
        
        try:
            # CORE STAGES 1-7: Classical TDD Workflow
            print("\n🟦 CORE TDD STAGES (1-7): Requirements → Tests → TDD → Refactor")
            print("-" * 60)
            
            # Stage 1: Requirements File Validation
            print("\n📋 Stage 1: Requirements File Validation")
            stage1_result = self.core_enforcer.stage_gate_1_requirements_file_validation(requirements_file)
            workflow_results["stage_results"]["stage_1"] = stage1_result
            if not stage1_result.get("validation_passed", False):
                return self._handle_stage_failure(workflow_results, 1, "Requirements validation failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 2: Parsing Completion Verification
            print("\n🔍 Stage 2: Parsing Completion Verification")
            stage2_result = self.core_enforcer.stage_gate_2_parsing_completion_verification(requirements_file)
            workflow_results["stage_results"]["stage_2"] = stage2_result
            if not stage2_result.get("parsing_valid", False):
                return self._handle_stage_failure(workflow_results, 2, "Requirements parsing failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 3: Test Generation Verification
            print("\n🧪 Stage 3: Test Generation Verification")
            stage3_result = self.core_enforcer.stage_gate_3_test_generation_verification(requirements_file)
            workflow_results["stage_results"]["stage_3"] = stage3_result
            if not stage3_result.get("generation_valid", False):
                return self._handle_stage_failure(workflow_results, 3, "Test generation failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 4: RED Phase Validation
            print("\n🔴 Stage 4: RED Phase Validation")
            stage4_result = self.core_enforcer.stage_gate_4_red_phase_validation(requirements_file)
            workflow_results["stage_results"]["stage_4"] = stage4_result
            if not stage4_result.get("red_phase_valid", False):
                return self._handle_stage_failure(workflow_results, 4, "RED phase validation failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 5: GREEN Phase Implementation Quality
            print("\n🟢 Stage 5: GREEN Phase Implementation Quality")
            stage5_result = self.core_enforcer.stage_gate_5_green_phase_implementation_quality(requirements_file)
            workflow_results["stage_results"]["stage_5"] = stage5_result
            if not stage5_result.get("green_phase_valid", False):
                return self._handle_stage_failure(workflow_results, 5, "GREEN phase quality validation failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 6: REFACTOR Analysis
            print("\n🔄 Stage 6: REFACTOR Analysis")
            stage6_result = self.core_enforcer.stage_gate_6_refactor_analysis(requirements_file)
            workflow_results["stage_results"]["stage_6"] = stage6_result
            if not stage6_result.get("refactor_analysis_valid", False):
                return self._handle_stage_failure(workflow_results, 6, "REFACTOR analysis failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 7: REFACTOR Complete
            print("\n✨ Stage 7: REFACTOR Complete")
            stage7_result = self.core_enforcer.stage_gate_7_refactor_complete(requirements_file)
            workflow_results["stage_results"]["stage_7"] = stage7_result
            if not stage7_result.get("refactor_complete", False):
                return self._handle_stage_failure(workflow_results, 7, "REFACTOR completion failed")
            workflow_results["stages_passed"] += 1
            
            print(f"\n✅ CORE TDD STAGES COMPLETE: {workflow_results['stages_passed']}/7 stages passed")
            
            # EXTENDED STAGES 8-10: Advanced Validation
            print("\n🟦 EXTENDED VALIDATION STAGES (8-10): Testing Pyramid → Compliance → Certification")
            print("-" * 60)
            
            # Stage 8: Testing Pyramid Validation
            print("\n🧪 Stage 8: Testing Pyramid Validation")
            stage8_result = self.extended_enforcer.stage_gate_8_testing_pyramid_validation(layer_name)
            workflow_results["stage_results"]["stage_8"] = stage8_result
            if not stage8_result.get("pyramid_valid", False):
                return self._handle_stage_failure(workflow_results, 8, "Testing pyramid validation failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 9: Requirements Compliance Verification
            print("\n📋 Stage 9: Requirements Compliance Verification")
            stage9_result = self.extended_enforcer.stage_gate_9_requirements_compliance_verification(requirements_file, layer_name)
            workflow_results["stage_results"]["stage_9"] = stage9_result
            if not stage9_result.get("compliance_valid", False):
                return self._handle_stage_failure(workflow_results, 9, "Requirements compliance verification failed")
            workflow_results["stages_passed"] += 1
            
            # Stage 10: Layer Completion Certification
            print("\n🏆 Stage 10: Layer Completion Certification")
            stage10_result = self.extended_enforcer.stage_gate_10_layer_completion_certification(layer_name, next_layer)
            workflow_results["stage_results"]["stage_10"] = stage10_result
            if not stage10_result.get("certification_valid", False):
                return self._handle_stage_failure(workflow_results, 10, "Layer completion certification failed")
            workflow_results["stages_passed"] += 1
            
            # SUCCESS: ALL STAGES COMPLETE
            workflow_results["workflow_complete"] = True
            workflow_results["final_status"] = "complete"
            workflow_results["completion_certificate"] = stage10_result.get("completion_certificate")
            workflow_results["next_commands"] = stage10_result.get("make_commands", [])
            
            # CELEBRATION OUTPUT
            print("\n" + "=" * 80)
            print("\033[92m🎉 COMPLETE TDD WORKFLOW SUCCESS! 🎉\033[0m")
            print(f"\033[92m✅ ALL {workflow_results['stages_passed']}/10 STAGES PASSED\033[0m")
            print(f"\033[92m🏆 LAYER {layer_name.upper()} CERTIFIED COMPLETE\033[0m")
            
            if workflow_results["completion_certificate"]:
                print(f"\033[96m📜 Certificate: {workflow_results['completion_certificate']}\033[0m")
            
            if workflow_results["next_commands"]:
                print(f"\033[96m🚀 Next Steps:\033[0m")
                for cmd in workflow_results["next_commands"]:
                    print(f"\033[96m   {cmd}\033[0m")
            
            print("=" * 80)
            
            return workflow_results
            
        except Exception as e:
            print(f"\n❌ COMPLETE TDD WORKFLOW FAILED: {e}")
            workflow_results["final_status"] = "error"
            workflow_results["error"] = str(e)
            return workflow_results
    
    def _handle_stage_failure(self, workflow_results: Dict[str, Any], stage_number: int, error_message: str) -> Dict[str, Any]:
        """Handle stage gate failure with helpful guidance"""
        workflow_results["final_status"] = "failed"
        workflow_results["failed_stage"] = stage_number
        workflow_results["error_message"] = error_message
        
        print(f"\n❌ WORKFLOW STOPPED AT STAGE {stage_number}")
        print(f"   Error: {error_message}")
        print(f"   Stages Passed: {workflow_results['stages_passed']}/10")
        print("\n🔧 REMEDIATION REQUIRED:")
        print(f"   1. Address stage {stage_number} issues")
        print(f"   2. Re-run TDD enforcer")
        print(f"   3. Continue from stage {stage_number}")
        
        return workflow_results
    
    def validate_enforcer_prerequisites(self) -> Dict[str, Any]:
        """Validate that TDD enforcer prerequisites are met"""
        print("\033[95m🔍 Validating TDD Enforcer Prerequisites...\033[0m")
        
        validation_results = {
            "prerequisites_met": False,
            "checks": {},
            "missing_requirements": [],
            "ready_for_development": False
        }
        
        # Check 1: Project structure exists
        required_dirs = ["src", "tests", "requirements"]
        for dir_name in required_dirs:
            dir_exists = (self.project_root / dir_name).exists()
            validation_results["checks"][f"{dir_name}_directory"] = dir_exists
            if not dir_exists:
                validation_results["missing_requirements"].append(f"Create {dir_name}/ directory")
        
        # Check 2: Requirements templates available
        templates_dir = self.project_root / "requirements_templates"
        templates_exist = templates_dir.exists()
        validation_results["checks"]["requirements_templates"] = templates_exist
        if not templates_exist:
            validation_results["missing_requirements"].append("Install requirements templates")
        
        # Check 3: Python testing framework available
        try:
            import pytest
            validation_results["checks"]["pytest_available"] = True
        except ImportError:
            validation_results["checks"]["pytest_available"] = False
            validation_results["missing_requirements"].append("Install pytest: pip install pytest pytest-cov")
        
        # Check 4: Core TDD enforcer modules available
        core_enforcer_available = hasattr(self, 'core_enforcer')
        validation_results["checks"]["core_enforcer"] = core_enforcer_available
        if not core_enforcer_available:
            validation_results["missing_requirements"].append("Fix core TDD enforcer imports")
        
        # Check 5: Extended TDD enforcer modules available
        extended_enforcer_available = hasattr(self, 'extended_enforcer')
        validation_results["checks"]["extended_enforcer"] = extended_enforcer_available
        if not extended_enforcer_available:
            validation_results["missing_requirements"].append("Fix extended TDD enforcer imports")
        
        # Final assessment
        validation_results["prerequisites_met"] = len(validation_results["missing_requirements"]) == 0
        validation_results["ready_for_development"] = validation_results["prerequisites_met"]
        
        # Output results
        if validation_results["prerequisites_met"]:
            print("\033[92m✅ TDD ENFORCER READY: All prerequisites met\033[0m")
            print("\033[92m🚀 DEVELOPMENT CAN BEGIN\033[0m")
        else:
            print("\033[91m❌ TDD ENFORCER NOT READY: Missing prerequisites\033[0m")
            print("\033[91m🚧 FIX REQUIRED BEFORE DEVELOPMENT:\033[0m")
            for requirement in validation_results["missing_requirements"]:
                print(f"\033[91m   - {requirement}\033[0m")
        
        print()
        return validation_results


def run_tdd_enforcer_for_layer(requirements_file: str, layer_name: str, next_layer: str = None) -> Dict[str, Any]:
    """
    Run the complete TDD enforcer for a specific layer
    
    This is the main entry point for layer development with TDD enforcement.
    Use this function to ensure a layer follows complete TDD methodology.
    
    Args:
        requirements_file: Path to layer requirements document
        layer_name: Name of layer being developed  
        next_layer: Name of next layer to activate after completion
        
    Returns:
        Dict with complete workflow results
    """
    enforcer = CompleteTDDEnforcer()
    
    # Validate prerequisites first
    prereq_check = enforcer.validate_enforcer_prerequisites()
    if not prereq_check["ready_for_development"]:
        print("❌ Cannot proceed: TDD enforcer prerequisites not met")
        return {
            "workflow_complete": False,
            "error": "Prerequisites not met",
            "missing_requirements": prereq_check["missing_requirements"]
        }
    
    # Execute complete TDD workflow
    return enforcer.enforce_complete_tdd_workflow(requirements_file, layer_name, next_layer)


def main():
    """Main entry point for complete TDD workflow enforcement"""
    print("🏗️  COMPLETE TDD WORKFLOW ENFORCER - STAGES 1-10")
    print("=" * 80)
    print("🎯 MISSION: Enforce Test-Driven Development with comprehensive validation")
    print("⚡ STAGES: Requirements → Tests → TDD → Refactor → Pyramid → Compliance → Certification")
    print("🔒 REQUIREMENT: This enforcer must be running before any development!")
    print()
    
    # Initialize enforcer
    enforcer = CompleteTDDEnforcer()
    
    # Validate prerequisites
    prereq_check = enforcer.validate_enforcer_prerequisites()
    
    if not prereq_check["ready_for_development"]:
        print("🚧 SETUP REQUIRED: Fix prerequisites before development")
        return
    
    # Demo layer for validation
    layer_name = "data_access"
    requirements_file = "/workspaces/control_tower/requirements/layers/LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001.md"
    next_layer = "business_logic"
    
    print(f"🎯 DEMO: Running complete TDD workflow for {layer_name} layer")
    print("-" * 60)
    
    # Execute complete workflow
    result = enforcer.enforce_complete_tdd_workflow(requirements_file, layer_name, next_layer)
    
    # Final status
    print("\n📊 COMPLETE TDD ENFORCER SUMMARY")
    print("=" * 40)
    print(f"Layer: {result['layer_name']}")
    print(f"Stages Passed: {result['stages_passed']}/10")
    print(f"Status: {result['final_status'].upper()}")
    
    if result["workflow_complete"]:
        print("🎉 READY FOR NEXT LAYER DEVELOPMENT!")
    else:
        print("🚧 CONTINUE DEVELOPMENT AND RE-RUN ENFORCER")
    
    print("\n🏁 COMPLETE TDD WORKFLOW ENFORCER FINISHED")
    print("=" * 80)


if __name__ == "__main__":
    main()