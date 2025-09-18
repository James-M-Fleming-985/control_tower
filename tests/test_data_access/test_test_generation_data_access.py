#!/usr/bin/env python3
"""
Test Generation Verification System - Data Access Layer Tests

Tests for LAYER-003-01-02-001: Data Access Layer for Test Generation Verification
Validates REAL file verification, test discovery, and physical evidence storage.

Created: 2025-09-18
Phase: TDD RED phase - Failing tests first
"""

import pytest
import tempfile
import os
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Import the module we're testing (will fail initially - RED phase)
try:
    from src.data_access.test_generation_data_access import (
        TestFileDiscovery,
        TestResultStorage,
        TestMetadataPersistence,
        VerificationEvidenceStorage
    )
except ImportError:
    # Expected in RED phase - tests should fail first
    TestFileDiscovery = None
    TestResultStorage = None
    TestMetadataPersistence = None
    VerificationEvidenceStorage = None


class TestTestFileDiscovery:
    """Test REAL test file discovery and physical file verification"""
    
    def setup_method(self):
        """Setup test environment with real temporary files"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_discovery = TestFileDiscovery(self.temp_dir) if TestFileDiscovery else None
        
        # Create real test files for REAL verification
        self.test_files = [
            Path(self.temp_dir) / "test_example.py",
            Path(self.temp_dir) / "test_integration.py",
            Path(self.temp_dir) / "test_unit.py"
        ]
        
        for test_file in self.test_files:
            test_file.write_text(f"""
def test_example():
    assert True

def test_another():
    pass
""")
    
    def teardown_method(self):
        """Clean up real test files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_discover_real_test_files(self):
        """Test REAL test file discovery from physical file system"""
        if not self.test_discovery:
            pytest.skip("Module not implemented yet - RED phase")
            
        # REAL verification: Discover actual test files
        discovered_files = self.test_discovery.discover_test_files()
        
        # Physical verification: Check actual files exist
        assert len(discovered_files) == 3
        for file_path in discovered_files:
            assert Path(file_path).exists()
            assert Path(file_path).name.startswith("test_")
            assert Path(file_path).suffix == ".py"
    
    def test_verify_physical_file_existence(self):
        """Test REAL file existence verification"""
        if not self.test_discovery:
            pytest.skip("Module not implemented yet - RED phase")
            
        # Test real file verification
        real_file = self.test_files[0]
        verification_result = self.test_discovery.verify_file_exists(str(real_file))
        
        assert verification_result.exists == True
        assert verification_result.is_test_file == True
        assert verification_result.file_size > 0
        assert verification_result.last_modified is not None
    
    def test_reject_non_existent_files(self):
        """Test rejection of non-existent files"""
        if not self.test_discovery:
            pytest.skip("Module not implemented yet - RED phase")
            
        fake_file = "/fake/path/test_nonexistent.py"
        verification_result = self.test_discovery.verify_file_exists(fake_file)
        
        assert verification_result.exists == False
        assert verification_result.is_test_file == False
        assert verification_result.error_message is not None


class TestTestResultStorage:
    """Test REAL test execution result storage with file system persistence"""
    
    def setup_method(self):
        """Setup real storage environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = TestResultStorage(self.temp_dir) if TestResultStorage else None
        
        # Real test result data
        self.test_result = {
            "test_name": "test_example",
            "status": "passed",
            "duration": 0.001,
            "timestamp": datetime.now().isoformat(),
            "file_path": "/path/to/test_example.py",
            "output": "Test passed successfully"
        }
    
    def teardown_method(self):
        """Clean up real storage files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_store_real_test_results(self):
        """Test REAL test result storage to physical file system"""
        if not self.storage:
            pytest.skip("Module not implemented yet - RED phase")
            
        # Store real test result
        result_id = self.storage.store_test_result(self.test_result)
        
        # Verify physical storage
        assert result_id is not None
        stored_result = self.storage.get_test_result(result_id)
        assert stored_result["test_name"] == "test_example"
        assert stored_result["status"] == "passed"
        
        # Verify physical file exists
        db_path = Path(self.temp_dir) / "test_results.db"
        assert db_path.exists()
    
    def test_query_stored_results(self):
        """Test querying stored test results"""
        if not self.storage:
            pytest.skip("Module not implemented yet - RED phase")
            
        # Store multiple results
        result_ids = []
        for i in range(3):
            test_result = self.test_result.copy()
            test_result["test_name"] = f"test_example_{i}"
            result_id = self.storage.store_test_result(test_result)
            result_ids.append(result_id)
        
        # Query all results
        all_results = self.storage.query_test_results()
        assert len(all_results) == 3
        
        # Query by status
        passed_results = self.storage.query_test_results(status="passed")
        assert len(passed_results) == 3


class TestTestMetadataPersistence:
    """Test REAL test metadata persistence with physical evidence collection"""
    
    def setup_method(self):
        """Setup metadata persistence environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.metadata_store = TestMetadataPersistence(self.temp_dir) if TestMetadataPersistence else None
    
    def teardown_method(self):
        """Clean up metadata files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_persist_test_metadata(self):
        """Test REAL test metadata persistence to physical files"""
        if not self.metadata_store:
            pytest.skip("Module not implemented yet - RED phase")
            
        metadata = {
            "test_file": "/path/to/test_example.py",
            "test_count": 5,
            "last_run": datetime.now().isoformat(),
            "coverage_percentage": 85.5,
            "dependencies": ["pytest", "mock"]
        }
        
        # Store metadata physically
        metadata_id = self.metadata_store.store_metadata(metadata)
        
        # Verify physical storage
        assert metadata_id is not None
        stored_metadata = self.metadata_store.get_metadata(metadata_id)
        assert stored_metadata["test_count"] == 5
        assert stored_metadata["coverage_percentage"] == 85.5
        
        # Verify JSON file exists
        metadata_file = Path(self.temp_dir) / f"metadata_{metadata_id}.json"
        assert metadata_file.exists()
    
    def test_collect_physical_evidence(self):
        """Test physical evidence collection for test metadata"""
        if not self.metadata_store:
            pytest.skip("Module not implemented yet - RED phase")
            
        # Create physical test file
        test_file = Path(self.temp_dir) / "test_evidence.py"
        test_file.write_text("def test_function(): pass")
        
        # Collect evidence
        evidence = self.metadata_store.collect_file_evidence(str(test_file))
        
        # Verify physical evidence
        assert evidence["file_exists"] == True
        assert evidence["file_size"] > 0
        assert evidence["line_count"] == 1
        assert "test_function" in evidence["function_names"]


class TestVerificationEvidenceStorage:
    """Test REAL verification evidence storage for stage gate enforcement"""
    
    def setup_method(self):
        """Setup evidence storage environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.evidence_store = VerificationEvidenceStorage(self.temp_dir) if VerificationEvidenceStorage else None
    
    def teardown_method(self):
        """Clean up evidence files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_store_stage_gate_evidence(self):
        """Test REAL stage gate evidence storage"""
        if not self.evidence_store:
            pytest.skip("Module not implemented yet - RED phase")
            
        evidence = {
            "stage_gate": "TEST_GENERATION",
            "requirement_id": "LAY-003-01-02-001",
            "verification_timestamp": datetime.now().isoformat(),
            "evidence_type": "PHYSICAL_FILE_VERIFICATION",
            "evidence_data": {
                "files_discovered": 5,
                "files_verified": 5,
                "total_tests": 25,
                "verification_passed": True
            },
            "physical_artifacts": [
                "/path/to/test_discovery_log.json",
                "/path/to/verification_report.html"
            ]
        }
        
        # Store evidence
        evidence_id = self.evidence_store.store_evidence(evidence)
        
        # Verify storage
        assert evidence_id is not None
        stored_evidence = self.evidence_store.get_evidence(evidence_id)
        assert stored_evidence["stage_gate"] == "TEST_GENERATION"
        assert stored_evidence["evidence_data"]["verification_passed"] == True
        
        # Verify physical evidence file
        evidence_file = Path(self.temp_dir) / f"evidence_{evidence_id}.json"
        assert evidence_file.exists()
    
    def test_query_evidence_by_stage_gate(self):
        """Test querying evidence by stage gate"""
        if not self.evidence_store:
            pytest.skip("Module not implemented yet - RED phase")
            
        # Store evidence for different stage gates
        stage_gates = ["TEST_GENERATION", "RED_PHASE", "GREEN_PHASE"]
        for stage in stage_gates:
            evidence = {
                "stage_gate": stage,
                "requirement_id": "LAY-003-01-02-001",
                "verification_timestamp": datetime.now().isoformat(),
                "evidence_type": "VERIFICATION",
                "evidence_data": {"passed": True}
            }
            self.evidence_store.store_evidence(evidence)
        
        # Query by stage gate
        test_gen_evidence = self.evidence_store.query_evidence_by_stage("TEST_GENERATION")
        assert len(test_gen_evidence) == 1
        assert test_gen_evidence[0]["stage_gate"] == "TEST_GENERATION"
    
    def test_validate_evidence_integrity(self):
        """Test evidence integrity validation"""
        if not self.evidence_store:
            pytest.skip("Module not implemented yet - RED phase")
            
        evidence = {
            "stage_gate": "TEST_GENERATION",
            "requirement_id": "LAY-003-01-02-001",
            "verification_timestamp": datetime.now().isoformat(),
            "evidence_type": "PHYSICAL_VERIFICATION",
            "evidence_data": {"verification_passed": True}
        }
        
        evidence_id = self.evidence_store.store_evidence(evidence)
        
        # Validate integrity
        integrity_check = self.evidence_store.validate_evidence_integrity(evidence_id)
        assert integrity_check["is_valid"] == True
        assert integrity_check["checksum"] is not None
        assert integrity_check["file_exists"] == True


# Integration test for complete data access layer
class TestDataAccessLayerIntegration:
    """Integration tests for complete data access layer functionality"""
    
    def setup_method(self):
        """Setup complete integration environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.components_available = all([
            TestFileDiscovery, TestResultStorage, 
            TestMetadataPersistence, VerificationEvidenceStorage
        ])
    
    def teardown_method(self):
        """Clean up integration environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_verification_workflow(self):
        """Test complete REAL verification workflow"""
        if not self.components_available:
            pytest.skip("Components not implemented yet - RED phase")
            
        # 1. Discover real test files
        discovery = TestFileDiscovery(self.temp_dir)
        
        # Create real test files
        test_file = Path(self.temp_dir) / "test_integration.py"
        test_file.write_text("def test_example(): assert True")
        
        discovered_files = discovery.discover_test_files()
        assert len(discovered_files) >= 1
        
        # 2. Store test results
        storage = TestResultStorage(self.temp_dir)
        test_result = {
            "test_name": "test_example",
            "status": "passed",
            "duration": 0.001,
            "timestamp": datetime.now().isoformat(),
            "file_path": str(test_file)
        }
        result_id = storage.store_test_result(test_result)
        
        # 3. Persist metadata
        metadata_store = TestMetadataPersistence(self.temp_dir)
        metadata = {
            "test_file": str(test_file),
            "test_count": 1,
            "last_run": datetime.now().isoformat()
        }
        metadata_id = metadata_store.store_metadata(metadata)
        
        # 4. Store verification evidence
        evidence_store = VerificationEvidenceStorage(self.temp_dir)
        evidence = {
            "stage_gate": "COMPLETE_VERIFICATION",
            "requirement_id": "LAY-003-01-02-001",
            "verification_timestamp": datetime.now().isoformat(),
            "evidence_type": "INTEGRATION_TEST",
            "evidence_data": {
                "files_discovered": len(discovered_files),
                "results_stored": 1,
                "metadata_persisted": 1,
                "verification_complete": True
            }
        }
        evidence_id = evidence_store.store_evidence(evidence)
        
        # Verify complete workflow
        assert result_id is not None
        assert metadata_id is not None
        assert evidence_id is not None
        
        # Verify all physical artifacts exist
        db_path = Path(self.temp_dir) / "test_results.db"
        metadata_path = Path(self.temp_dir) / f"metadata_{metadata_id}.json"
        evidence_path = Path(self.temp_dir) / f"evidence_{evidence_id}.json"
        
        assert db_path.exists()
        assert metadata_path.exists()
        assert evidence_path.exists()


if __name__ == "__main__":
    # Run tests to verify RED phase (all should fail initially)
    pytest.main([__file__, "-v"])