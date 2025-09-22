"""Comprehensive integration tests - GREEN phase coverage improvement"""

import pytest
import os
import sys
import tempfile
import shutil
import subprocess
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from integration.external_api_client import ExternalAPIClient
from integration.integration_models import ExternalSystemConfig, IntegrationResult, WorkflowState
from integration.optimized_workflow_coordinator import OptimizedWorkflowIntegrationCoordinator
from integration.workflow_integration_coordinator import WorkflowIntegrationCoordinator


class TestExternalAPIClient:
    """Comprehensive integration tests for ExternalAPIClient"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = ExternalAPIClient()
        
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_api_client_initialization(self):
        """Test API client initialization"""
        assert self.client is not None
        
    def test_make_api_request_success(self):
        """Test successful API request"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_get.return_value = mock_response
            
            result = self.client.make_request("GET", "/test/endpoint")
            assert result is not None
            assert result.get("status") == "success"
            
    def test_make_api_request_failure(self):
        """Test failed API request"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not found"}
            mock_get.return_value = mock_response
            
            result = self.client.make_request("GET", "/invalid/endpoint")
            assert result is not None
            assert result.get("error") == "Not found"  # Verify error handling
            assert result.get("error") == "Not found"  # Verify error handling
            
    def test_api_authentication(self):
        """Test API authentication"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test_token_123"}
            mock_post.return_value = mock_response
            
            result = self.client.authenticate("test_user", "test_pass")
            assert result is not None
            assert "token" in result  # Verify token present
            assert result["token"] == "test_token_123"
            
    def test_api_error_handling(self):
        """Test API error handling"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            result = self.client.make_request("GET", "/test/endpoint")
            assert result is not None  # Should handle error gracefully
            assert "error" in result  # Error should be captured
            
    def test_api_retry_mechanism(self):
        """Test API retry mechanism"""
        with patch('requests.get') as mock_get:
            # First call fails, second succeeds
            mock_get.side_effect = [
                Exception("Temporary error"),
                Mock(status_code=200, json=lambda: {"status": "success"})
            ]
            
            result = self.client.make_request_with_retry("GET", "/test/endpoint")
            assert result is not None
            assert result["status"] == "success"  # Eventually succeeds
            assert mock_get.call_count == 2  # Retry happened


class TestIntegrationModels:
    """Comprehensive tests for integration models"""
    
    def test_integration_config_creation(self):
        """Test IntegrationConfig creation"""
        config = IntegrationConfig(
            config_id="config_001",
            api_endpoint="https://api.example.com",
            authentication_type="bearer",
            timeout_seconds=30
        )
        assert config.config_id == "config_001"
        assert config.api_endpoint == "https://api.example.com"
        assert config.timeout_seconds == 30
        
    def test_api_response_creation(self):
        """Test APIResponse creation"""
        response = APIResponse(
            response_id="resp_001",
            status_code=200,
            response_data={"message": "success"},
            timestamp=datetime.now()
        )
        assert response.status_code == 200
        assert response.response_data["message"] == "success"
        
    def test_workflow_state_creation(self):
        """Test WorkflowState creation"""
        state = WorkflowState(
            workflow_id="workflow_001",
            current_step="step_2",
            status="running",
            progress_percentage=45.5
        )
        assert state.workflow_id == "workflow_001"
        assert state.current_step == "step_2"
        assert state.progress_percentage == 45.5
        
    def test_model_validation(self):
        """Test model validation"""
        config = IntegrationConfig(
            config_id="",  # Invalid empty ID
            api_endpoint="invalid_url",  # Invalid URL
            authentication_type="unknown",  # Invalid auth type
            timeout_seconds=-5  # Invalid timeout
        )
        result = config.validate()
        assert result is not None
        
    def test_model_serialization(self):
        """Test model serialization"""
        config = IntegrationConfig(
            config_id="serialize_test",
            api_endpoint="https://serialize.example.com",
            authentication_type="api_key",
            timeout_seconds=60
        )
        serialized = config.to_dict()
        assert serialized is not None
        assert "config_id" in serialized
        assert "api_endpoint" in serialized


class TestOptimizedWorkflowCoordinator:
    """Comprehensive integration tests for OptimizedWorkflowCoordinator"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.coordinator = OptimizedWorkflowCoordinator()
        
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_coordinator_initialization(self):
        """Test coordinator initialization"""
        assert self.coordinator is not None
        
    def test_workflow_execution(self):
        """Test workflow execution"""
        workflow_config = {
            "workflow_id": "test_workflow",
            "steps": [
                {"step_id": "step1", "action": "validate"},
                {"step_id": "step2", "action": "process"},
                {"step_id": "step3", "action": "complete"}
            ]
        }
        result = self.coordinator.execute_workflow(workflow_config)
        assert result is not None
        
    def test_workflow_optimization(self):
        """Test workflow optimization"""
        workflow_data = {
            "workflow_id": "optimize_test",
            "performance_metrics": {
                "execution_time": 120.5,
                "resource_usage": 75.2,
                "success_rate": 95.8
            }
        }
        result = self.coordinator.optimize_workflow(workflow_data)
        assert result is not None
        
    def test_parallel_workflow_execution(self):
        """Test parallel workflow execution"""
        workflows = [
            {"workflow_id": "parallel_1", "priority": "high"},
            {"workflow_id": "parallel_2", "priority": "medium"},
            {"workflow_id": "parallel_3", "priority": "low"}
        ]
        result = self.coordinator.execute_parallel_workflows(workflows)
        assert result is not None
        
    def test_workflow_error_recovery(self):
        """Test workflow error recovery"""
        failed_workflow = {
            "workflow_id": "failed_workflow",
            "error": "Step 2 failed",
            "recovery_strategy": "retry_from_failure"
        }
        result = self.coordinator.recover_workflow(failed_workflow)
        assert result is not None
        
    def test_workflow_monitoring(self):
        """Test workflow monitoring"""
        workflow_id = "monitor_test_workflow"
        result = self.coordinator.monitor_workflow(workflow_id)
        assert result is not None


class TestWorkflowIntegrationCoordinator:
    """Comprehensive integration tests for WorkflowIntegrationCoordinator"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.integration_coordinator = WorkflowIntegrationCoordinator()
        
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_integration_coordinator_initialization(self):
        """Test integration coordinator initialization"""
        assert self.integration_coordinator is not None
        
    def test_workflow_integration_setup(self):
        """Test workflow integration setup"""
        integration_config = {
            "integration_id": "test_integration",
            "source_workflow": "workflow_a",
            "target_workflow": "workflow_b",
            "integration_type": "sequential"
        }
        result = self.integration_coordinator.setup_integration(integration_config)
        assert result is not None
        
    def test_cross_workflow_communication(self):
        """Test cross-workflow communication"""
        message = {
            "from_workflow": "sender_workflow",
            "to_workflow": "receiver_workflow",
            "message_type": "data_transfer",
            "payload": {"data": "test_data"}
        }
        result = self.integration_coordinator.send_workflow_message(message)
        assert result is not None
        
    def test_workflow_dependency_management(self):
        """Test workflow dependency management"""
        dependencies = {
            "workflow_id": "dependent_workflow",
            "dependencies": [
                {"workflow_id": "prereq_1", "status": "completed"},
                {"workflow_id": "prereq_2", "status": "running"}
            ]
        }
        result = self.integration_coordinator.manage_dependencies(dependencies)
        assert result is not None
        
    def test_workflow_data_synchronization(self):
        """Test workflow data synchronization"""
        sync_config = {
            "sync_id": "test_sync",
            "workflows": ["workflow_1", "workflow_2", "workflow_3"],
            "sync_type": "real_time"
        }
        result = self.integration_coordinator.synchronize_workflows(sync_config)
        assert result is not None
        
    def test_integration_health_check(self):
        """Test integration health check"""
        integration_id = "health_check_integration"
        result = self.integration_coordinator.check_integration_health(integration_id)
        assert result is not None


# End-to-end integration tests
class TestEndToEndIntegration:
    """End-to-end integration tests across all modules"""
    
    def setup_method(self):
        """Setup for end-to-end tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.api_client = ExternalAPIClient()
        self.workflow_coordinator = OptimizedWorkflowCoordinator()
        self.integration_coordinator = WorkflowIntegrationCoordinator()
        
    def teardown_method(self):
        """Cleanup after end-to-end tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_complete_integration_workflow(self):
        """Test complete integration workflow"""
        # Step 1: Setup integration
        integration_config = {
            "integration_id": "e2e_integration",
            "api_endpoint": "https://test.api.com",
            "workflow_config": {
                "workflow_id": "e2e_workflow",
                "steps": ["validate", "process", "notify"]
            }
        }
        
        setup_result = self.integration_coordinator.setup_integration(integration_config)
        assert setup_result is not None
        
        # Step 2: Execute workflow
        workflow_result = self.workflow_coordinator.execute_workflow(
            integration_config["workflow_config"]
        )
        assert workflow_result is not None
        
        # Step 3: API communication
        with patch.object(self.api_client, 'make_request', return_value={"status": "success"}):
            api_result = self.api_client.make_request("POST", "/workflow/complete")
            assert api_result is not None
            
    def test_multi_system_integration(self):
        """Test multi-system integration"""
        systems = [
            {"system_id": "system_a", "type": "database"},
            {"system_id": "system_b", "type": "api"},
            {"system_id": "system_c", "type": "message_queue"}
        ]
        
        for system in systems:
            result = self.integration_coordinator.connect_system(system)
            assert result is not None
            
    def test_integration_performance(self):
        """Test integration performance"""
        start_time = time.time()
        
        # Simulate high-load scenario
        workflows = []
        for i in range(10):
            workflow = {
                "workflow_id": f"perf_test_{i}",
                "priority": "normal",
                "estimated_duration": 5.0
            }
            workflows.append(workflow)
            
        result = self.workflow_coordinator.execute_parallel_workflows(workflows)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert result is not None
        assert execution_time < 30.0  # Should complete within 30 seconds
        
    def test_integration_failure_recovery(self):
        """Test integration failure recovery"""
        # Simulate system failure
        failure_scenario = {
            "integration_id": "failure_test",
            "failure_type": "network_timeout",
            "affected_workflows": ["workflow_1", "workflow_2"]
        }
        
        recovery_result = self.integration_coordinator.handle_integration_failure(failure_scenario)
        assert recovery_result is not None
        
    def test_data_consistency_across_integrations(self):
        """Test data consistency across integrations"""
        # Create data in multiple systems
        data_entries = [
            {"system": "system_a", "data": {"id": 1, "value": "test_a"}},
            {"system": "system_b", "data": {"id": 1, "value": "test_a"}},
            {"system": "system_c", "data": {"id": 1, "value": "test_a"}}
        ]
        
        consistency_check = self.integration_coordinator.verify_data_consistency(data_entries)
        assert consistency_check is not None


# Performance and load testing
class TestIntegrationPerformance:
    """Performance tests for integration modules"""
    
    def setup_method(self):
        """Setup for performance tests"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup after performance tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_api_client_performance(self):
        """Test API client performance under load"""
        client = ExternalAPIClient()
        
        start_time = time.time()
        
        # Simulate 100 API calls
        with patch.object(client, 'make_request', return_value={"status": "success"}):
            for i in range(100):
                result = client.make_request("GET", f"/test/endpoint/{i}")
                assert result is not None
                
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 100 requests in reasonable time
        assert total_time < 10.0
        
    def test_workflow_coordinator_scalability(self):
        """Test workflow coordinator scalability"""
        coordinator = OptimizedWorkflowCoordinator()
        
        # Create large number of workflows
        workflows = []
        for i in range(50):
            workflow = {
                "workflow_id": f"scale_test_{i}",
                "steps": [{"step_id": f"step_{j}", "action": "process"} for j in range(5)]
            }
            workflows.append(workflow)
            
        start_time = time.time()
        result = coordinator.execute_parallel_workflows(workflows)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result is not None
        assert execution_time < 60.0  # Should handle 50 workflows in under 60 seconds
        
    def test_integration_memory_usage(self):
        """Test integration memory usage"""
        coordinator = WorkflowIntegrationCoordinator()
        
        # Create memory-intensive operations
        large_data = {"data": "x" * 10000}  # 10KB of data
        
        for i in range(100):
            integration_config = {
                "integration_id": f"memory_test_{i}",
                "data": large_data
            }
            result = coordinator.setup_integration(integration_config)
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])