import pytest
import os
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

class TestEvidenceStorage:
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp(prefix="evidence_test_")
        try:
            from evidence_storage import EvidenceStorage
            self.storage = EvidenceStorage(self.test_dir)
        except ImportError:
            raise AssertionError("EvidenceStorage class not implemented - create evidence_storage.py")
    
    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # REQ-FUNC-001: Dual Project Type Evidence Storage
    def test_detect_workflow_type_software_development(self):
        """Test detection of software development workflow"""
        config_path = os.path.join(self.test_dir, "workflow_config.json")
        with open(config_path, 'w') as f:
            json.dump({"project_type": "SOFTWARE_DEV"}, f)
        
        workflow_type = self.storage.detect_workflow_type(self.test_dir)
        assert workflow_type == "SOFTWARE_DEV"
    
    def test_detect_workflow_type_standard_delivery(self):
        """Test detection of standard delivery workflow"""
        config_path = os.path.join(self.test_dir, "workflow_config.json")
        with open(config_path, 'w') as f:
            json.dump({"project_type": "STANDARD_DELIVERY"}, f)
        
        workflow_type = self.storage.detect_workflow_type(self.test_dir)
        assert workflow_type == "STANDARD_DELIVERY"

    def test_store_evidence_software_dev_hierarchy(self):
        """Test storing evidence in SOFTWARE_DEV hierarchy"""
        content = {"test_result": "PASS", "duration": "2.3s"}
        
        result = self.storage.store_evidence(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
            "LAYER-003-01-04-001", "red_stage", content, "test_result"
        )
        
        assert result["status"] == "stored"
        assert "PROJECT-003/SYSTEM-003-01/FEATURE-003-01-04/LAYER-003-01-04-001/red_stage" in result["path"]

    def test_store_evidence_standard_delivery_hierarchy(self):
        """Test storing evidence in STANDARD_DELIVERY hierarchy"""
        content = {"deliverable": "Requirements Document v1.0", "status": "approved"}
        
        result = self.storage.store_evidence(
            "PROJECT-005", "WORKPACKAGE-005-02", "MILESTONE-005-02-03", 
            "TASK-005-02-03-001", "approval_stage", content, "document"
        )
        
        assert result["status"] == "stored"
        assert "PROJECT-005/WORKPACKAGE-005-02/MILESTONE-005-02-03/TASK-005-02-03-001/approval_stage" in result["path"]

    # REQ-FUNC-002: Workflow-Aware Activity Logging
    def test_log_activity_with_workflow_context(self):
        """Test activity logging with workflow context"""
        self.storage.log_activity(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", "LAYER-003-01-04-001",
            "test_execution", {"test_count": 5, "failures": 0}, {"workflow_type": "SOFTWARE_DEV"}
        )
        
        log_path = os.path.join(self.test_dir, "PROJECT-003/SYSTEM-003-01/FEATURE-003-01-04/LAYER-003-01-04-001/activity_log.txt")
        assert os.path.exists(log_path)

    # REQ-FUNC-003: Intelligent Evidence Retrieval
    def test_retrieve_evidence_by_workflow_type(self):
        """Test retrieving evidence filtered by workflow type"""
        # Store evidence first
        self.storage.store_evidence(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
            "LAYER-003-01-04-001", "green_stage", {"test": "passed"}, "test_result"
        )
        
        results = self.storage.retrieve_evidence(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
            "LAYER-003-01-04-001", "green_stage", workflow_type="SOFTWARE_DEV"
        )
        
        assert len(results) > 0
        assert results[0]["artifact_type"] == "test_result"

    # REQ-FUNC-004: Advanced Storage Organization
    def test_create_directory_structure_software_dev(self):
        """Test creating SOFTWARE_DEV directory structure"""
        self.storage.create_directory_structure(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
            "LAYER-003-01-04-001", "SOFTWARE_DEV"
        )
        
        base_path = os.path.join(self.test_dir, "PROJECT-003/SYSTEM-003-01/FEATURE-003-01-04/LAYER-003-01-04-001")
        assert os.path.exists(os.path.join(base_path, "red_stage"))
        assert os.path.exists(os.path.join(base_path, "green_stage"))
        assert os.path.exists(os.path.join(base_path, "refactor_stage"))

    # REQ-FUNC-005: Requirements-Test Traceability Management
    def test_generate_requirements_matrix(self):
        """Test generating requirements traceability matrix"""
        matrix = self.storage.generate_requirements_matrix(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", "LAYER-003-01-04-001"
        )
        
        assert "requirements" in matrix
        assert "tests" in matrix
        assert "traceability_links" in matrix

    # REQ-FUNC-006: Test Generation Validation
    def test_validate_test_generation_rejects_placeholders(self):
        """Test validation rejects placeholder tests"""
        requirements_spec = "REQ-001: System shall validate user input"
        placeholder_tests = [
            "def test_validation(): pass",
            "def test_input(): pytest.skip('TODO: implement')"
        ]
        
        result = self.storage.validate_test_generation(requirements_spec, placeholder_tests)
        assert result["valid"] == False
        assert "placeholder" in result["errors"][0].lower()

    # REQ-FUNC-007: Multi-Level Testing Cascade Management
    def test_check_cascade_trigger_detects_completion(self):
        """Test cascade trigger detection"""
        # Simulate completed layer
        self.storage.store_evidence(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
            "LAYER-003-01-04-001", "unit_testing_stage", {"status": "complete"}, "completion_marker"
        )
        
        trigger_result = self.storage.check_cascade_trigger(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", "LAYER-003-01-04-001"
        )
        
        assert trigger_result["cascade_ready"] == True
        assert trigger_result["next_level"] == "FEATURE"

    # REQ-FUNC-008: Workflow Type Recognition and Management
    def test_workflow_type_from_directory_structure(self):
        """Test workflow type detection from directory structure"""
        # Create SOFTWARE_DEV structure
        os.makedirs(os.path.join(self.test_dir, "PROJECT-003/SYSTEM-003-01"), exist_ok=True)
        
        workflow_type = self.storage.detect_workflow_type(self.test_dir)
        assert workflow_type in ["SOFTWARE_DEV", "STANDARD_DELIVERY"]

    # REQ-FUNC-009: Failure Detection and Rollback Management
    def test_detect_failure_and_execute_rollback(self):
        """Test failure detection and rollback execution"""
        # Create checkpoint first
        checkpoint = self.storage.create_checkpoint(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", "LAYER-003-01-04-001"
        )
        
        # Execute rollback
        rollback_result = self.storage.execute_rollback(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
            "LAYER-003-01-04-001", checkpoint["checkpoint_id"]
        )
        
        assert rollback_result["status"] == "success"
        assert rollback_result["target"] == checkpoint["checkpoint_id"]

    # REQ-FUNC-010: Checkpoint and Recovery System
    def test_create_stable_checkpoint(self):
        """Test creating stable checkpoints"""
        checkpoint = self.storage.create_checkpoint(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", "LAYER-003-01-04-001"
        )
        
        assert "checkpoint_id" in checkpoint
        assert checkpoint["status"] == "created"
        assert checkpoint["timestamp"] is not None

    # REQ-FUNC-011: Configurable Failure Thresholds
    def test_configure_failure_thresholds(self):
        """Test configuring failure thresholds"""
        config_result = self.storage.configure_thresholds(
            failure_count=3, time_limit=300  # 5 minutes
        )
        
        assert config_result["failure_threshold"] == 3
        assert config_result["time_limit"] == 300
        assert config_result["status"] == "configured"

    # REQ-FUNC-012: Interactive User Rollback Notification
    def test_notify_user_rollback_decision(self):
        """Test user notification for rollback decisions"""
        notification_result = self.storage.notify_user(
            "Failure threshold exceeded. Rollback recommended?", 
            notification_type="rollback_decision"
        )
        
        assert notification_result["status"] == "sent"
        assert notification_result["type"] == "rollback_decision"
        assert "notification_id" in notification_result

    # REQ-FUNC-013: Mobile API Integration
    def test_start_mobile_api_server(self):
        """Test starting mobile API server"""
        api_result = self.storage.start_mobile_api()
        
        assert api_result["status"] == "started"
        assert api_result["port"] is not None
        assert api_result["endpoints"] is not None

    def test_mobile_workflow_control_endpoints(self):
        """Test mobile workflow control API endpoints"""
        # Simulate API call
        response = self.storage.handle_mobile_request(
            endpoint="/workflow/status",
            method="GET",
            params={"project_id": "PROJECT-003"}
        )
        
        assert response["status_code"] == 200
        assert "workflow_status" in response["data"]

    # REQ-FUNC-014: Mobile Push Notification System
    def test_send_push_notification(self):
        """Test sending push notifications to mobile"""
        push_result = self.storage.send_push_notification(
            user_id="user123",
            message="Rollback decision required for PROJECT-003"
        )
        
        assert push_result["status"] == "sent"
        assert push_result["user_id"] == "user123"
        assert "notification_id" in push_result

    # REQ-FUNC-015: Mobile Decision Interface
    def test_get_mobile_decision(self):
        """Test mobile decision interface"""
        # Create decision request
        decision_id = "decision_123"
        
        decision_result = self.storage.get_mobile_decision(decision_id)
        
        assert "decision_id" in decision_result
        assert "options" in decision_result
        assert "timeout" in decision_result

    def test_mobile_biometric_authentication(self):
        """Test mobile biometric authentication"""
        auth_result = self.storage.authenticate_mobile_user(
            user_id="user123",
            auth_type="biometric",
            auth_data={"fingerprint": "encrypted_hash"}
        )
        
        assert auth_result["authenticated"] == True
        assert auth_result["session_token"] is not None

    # REQ-FUNC-016: Mobile Rollback Execution and Monitoring
    def test_execute_mobile_rollback(self):
        """Test mobile-initiated rollback execution"""
        rollback_result = self.storage.execute_mobile_rollback(
            rollback_id="rollback_456",
            user_confirmation=True
        )
        
        assert rollback_result["status"] == "executed"
        assert rollback_result["rollback_id"] == "rollback_456"
        assert "completion_time" in rollback_result

    def test_mobile_rollback_monitoring(self):
        """Test monitoring rollback progress via mobile"""
        monitor_result = self.storage.get_rollback_status(
            rollback_id="rollback_456"
        )
        
        assert "progress_percentage" in monitor_result
        assert "current_step" in monitor_result
        assert "estimated_completion" in monitor_result

# === INTEGRATION TESTS ===

class TestEvidenceStorageIntegration:
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp(prefix="evidence_integration_")
        try:
            from evidence_storage import EvidenceStorage
            self.storage = EvidenceStorage(self.test_dir)
        except ImportError:
            raise AssertionError("EvidenceStorage class not implemented")
    
    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_full_workflow_software_dev(self):
        """Test complete SOFTWARE_DEV workflow"""
        # 1. Detect workflow type
        workflow_type = self.storage.detect_workflow_type(self.test_dir)
        
        # 2. Create directory structure
        self.storage.create_directory_structure(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
            "LAYER-003-01-04-001", "SOFTWARE_DEV"
        )
        
        # 3. Store evidence through TDD stages
        stages = ["requirements_analysis_stage", "test_generation_stage", "red_stage", "green_stage"]
        for stage in stages:
            self.storage.store_evidence(
                "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", 
                "LAYER-003-01-04-001", stage, {"status": "complete"}, "stage_completion"
            )
        
        # 4. Generate traceability matrix
        matrix = self.storage.generate_requirements_matrix(
            "PROJECT-003", "SYSTEM-003-01", "FEATURE-003-01-04", "LAYER-003-01-04-001"
        )
        
        assert len(matrix["requirements"]) > 0

    def test_mobile_workflow_integration(self):
        """Test mobile workflow integration"""
        # 1. Start mobile API
        api_result = self.storage.start_mobile_api()
        assert api_result["status"] == "started"
        
        # 2. Send push notification
        push_result = self.storage.send_push_notification(
            "user123", "Decision required"
        )
        assert push_result["status"] == "sent"
        
        # 3. Get mobile decision
        decision = self.storage.get_mobile_decision("decision_123")
        assert "options" in decision
        
        # 4. Execute mobile rollback
        rollback_result = self.storage.execute_mobile_rollback("rollback_456")
        assert rollback_result["status"] == "executed"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])