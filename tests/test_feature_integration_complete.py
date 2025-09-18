#!/usr/bin/env python3
"""
Feature Integration Testing - FEATURE-003-01-02 TEST GENERATION VERIFICATION SYSTEM
Quick validation that all 4 layers work together properly.
"""
import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import all layers
from src.data_access.test_file_discovery import TestFileDiscovery
from src.business_logic.test_generation_verification_logic import TestGenerationVerifier
from src.ui.progress_display import ProgressDisplay
from src.integration.workflow_integration_coordinator import WorkflowIntegrationCoordinator

class TestFeatureIntegrationComplete(unittest.TestCase):
    """Test complete feature integration across all layers"""
    
    def test_complete_feature_workflow(self):
        """Test complete workflow: Data Access → Business Logic → UI → Integration"""
        print("\n🔗 FEATURE INTEGRATION TEST")
        print("Testing all 4 layers working together...")
        
        # Layer 1: Data Access
        discovery = TestFileDiscovery()
        test_files = discovery.discover_test_files("tests/")
        self.assertGreater(len(test_files), 0, "Data Access Layer failed")
        print(f"✅ Data Access: Found {len(test_files)} test files")
        
        # Layer 2: Business Logic  
        verifier = TestGenerationVerifier()
        verification_result = verifier.verify_test_generation({
            "test_files": test_files[:5],  # Sample
            "project_path": os.getcwd()
        })
        self.assertTrue(verification_result.get("verification_successful", False))
        print(f"✅ Business Logic: Verification passed")
        
        # Layer 3: UI
        ui = ProgressDisplay()
        progress_id = ui.start_progress_tracking("feature_integration_test")
        ui.update_progress({
            "verification_id": progress_id,
            "stage": "integration_test", 
            "progress_percent": 100,
            "message": "Feature integration complete"
        })
        print(f"✅ UI Layer: Progress tracking working")
        
        # Layer 4: Integration
        coordinator = WorkflowIntegrationCoordinator()
        integration_result = coordinator.perform_integration_operation({
            "operation_id": "feature_integration_test",
            "operation_type": "feature_validation",
            "layers": ["data_access", "business_logic", "ui", "integration"]
        })
        self.assertTrue(integration_result.get("successful", False))
        print(f"✅ Integration Layer: Coordination successful")
        
        print("🎉 FEATURE INTEGRATION: ALL LAYERS WORKING TOGETHER!")

if __name__ == "__main__":
    unittest.main(verbosity=2)