#!/usr/bin/env python3
"""
Additional validation tests for EvidenceStorage (Post-Refactor Testing)
Demonstrates unit, integration, and E2E testing patterns for personal/small team use.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from evidence_storage import EvidenceStorage, ValidationError, StorageError


class TestEvidenceStorageValidation:
    """Additional validation tests for post-refactor verification."""
    
    def setup_method(self):
        """Setup test directory for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = EvidenceStorage(self.test_dir)
    
    def teardown_method(self):
        """Cleanup test directory after each test."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    # === UNIT TESTS ===
    
    def test_custom_exceptions_work(self):
        """Test custom exception hierarchy works correctly."""
        # Test ValidationError
        with pytest.raises(ValidationError):
            self.storage.detect_workflow_type("")
        
        with pytest.raises(ValidationError):
            self.storage.store_evidence("", "", "", "", "", {}, "")
    
    def test_enhanced_documentation_exists(self):
        """Test that enhanced methods have proper docstrings."""
        methods_to_check = [
            'detect_workflow_type', 'store_evidence', 'log_activity',
            'retrieve_evidence', 'create_directory_structure'
        ]
        
        for method_name in methods_to_check:
            method = getattr(self.storage, method_name)
            assert method.__doc__ is not None, f"{method_name} missing docstring"
            assert len(method.__doc__.strip()) > 20, f"{method_name} docstring too short"
    
    def test_mobile_api_structure(self):
        """Test mobile API methods return expected structure."""
        api_result = self.storage.start_mobile_api()
        assert "status" in api_result
        assert "port" in api_result
        assert "endpoints" in api_result
        assert api_result["status"] == "started"
    
    # === INTEGRATION TESTS ===
    
    def test_file_system_integration(self):
        """Test that file system operations work correctly."""
        # Store evidence
        result = self.storage.store_evidence(
            "TEST-001", "SYS-001", "FEAT-001", "COMP-001",
            "test_stage", {"test": "data"}, "test_artifact"
        )
        
        assert result["status"] == "stored"
        
        # Verify file was created
        evidence_dir = Path(self.test_dir) / "TEST-001" / "SYS-001" / "FEAT-001" / "COMP-001" / "test_stage"
        assert evidence_dir.exists()
        
        # Verify evidence can be retrieved
        evidence = self.storage.retrieve_evidence(
            "TEST-001", "SYS-001", "FEAT-001", "COMP-001", "test_stage"
        )
        assert len(evidence) > 0
        assert evidence[0]["content"]["test"] == "data"
    
    def test_workflow_directory_creation(self):
        """Test directory structure creation for both workflow types."""
        # Test SOFTWARE_DEV structure
        self.storage.create_directory_structure(
            "PROJ-001", "SYS-001", "FEAT-001", "COMP-001", "SOFTWARE_DEV"
        )
        
        expected_stages = ["red_stage", "green_stage", "refactor_stage"]
        for stage in expected_stages:
            stage_path = Path(self.test_dir) / "PROJ-001" / "SYS-001" / "FEAT-001" / "COMP-001" / stage
            assert stage_path.exists(), f"Missing {stage} directory"
    
    # === END-TO-END TESTS ===
    
    def test_complete_evidence_workflow(self):
        """E2E: Complete evidence workflow from detection to retrieval."""
        # Setup mock project directory with config
        project_dir = Path(self.test_dir) / "mock_project"
        project_dir.mkdir(exist_ok=True)
        
        config_file = project_dir / "workflow_config.json"
        with open(config_file, 'w') as f:
            json.dump({"project_type": "SOFTWARE_DEV"}, f)
        
        # Detect workflow type
        workflow_type = self.storage.detect_workflow_type(str(project_dir))
        assert workflow_type == "SOFTWARE_DEV"
        
        # Create directory structure
        self.storage.create_directory_structure(
            "E2E-001", "SYS-001", "FEAT-001", "COMP-001", workflow_type
        )
        
        # Store evidence across multiple stages
        stages = ["red_stage", "green_stage", "refactor_stage"]
        for i, stage in enumerate(stages):
            # Store evidence
            self.storage.store_evidence(
                "E2E-001", "SYS-001", "FEAT-001", "COMP-001",
                stage, {"stage": stage, "data": f"content_{i}"}, f"artifact_{i}"
            )
            
            # Log activity
            self.storage.log_activity(
                "E2E-001", "SYS-001", "FEAT-001", "COMP-001",
                f"Completed {stage}", {"success": True}
            )
        
        # Verify all evidence stored and retrievable
        for stage in stages:
            evidence = self.storage.retrieve_evidence(
                "E2E-001", "SYS-001", "FEAT-001", "COMP-001", stage
            )
            assert len(evidence) > 0
            assert evidence[0]["content"]["stage"] == stage
        
        # Verify activity log exists
        log_file = Path(self.test_dir) / "E2E-001" / "SYS-001" / "FEAT-001" / "COMP-001" / "activity_log.txt"
        assert log_file.exists()
        
        log_content = log_file.read_text()
        for stage in stages:
            assert f"Completed {stage}" in log_content
    
    def test_rollback_workflow_integration(self):
        """E2E: Test rollback and mobile workflow integration."""
        # Create checkpoint
        checkpoint = self.storage.create_checkpoint(
            "ROLLBACK-001", "SYS-001", "FEAT-001", "COMP-001"
        )
        assert checkpoint["status"] == "created"
        checkpoint_id = checkpoint["checkpoint_id"]
        
        # Test mobile authentication
        auth_result = self.storage.authenticate_mobile_user(
            "test_user", "biometric", {"fingerprint": "test_data"}
        )
        assert auth_result["authenticated"] == True
        assert auth_result["session_token"] is not None
        
        # Test mobile rollback execution
        rollback_result = self.storage.execute_mobile_rollback(
            checkpoint_id, True
        )
        assert rollback_result["status"] == "executed"
        assert rollback_result["user_confirmed"] == True
        
        # Test rollback status monitoring
        status = self.storage.get_rollback_status(checkpoint_id)
        assert "progress_percentage" in status
        assert isinstance(status["progress_percentage"], int)


if __name__ == "__main__":
    # Simple test runner for validation
    pytest.main([__file__, "-v"])