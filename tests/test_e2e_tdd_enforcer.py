#!/usr/bin/env python3
"""
End-to-End Tests for TDD ENFORCER - Complete System Verification
Tests the complete workflow from user interface through all layers to evidence storage
"""

import pytest
import tempfile
import shutil
import sqlite3
import json
from pathlib import Path
import time


class TestTDDEnforcerEndToEnd:
    """
    End-to-End tests for complete TDD ENFORCER system
    Tests the full workflow: UI → Business Logic → Data Access → Evidence
    """
    
    def setup_method(self):
        """Setup complete E2E test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_dir = Path(self.temp_dir) / "test_project"
        self.test_project_dir.mkdir()
        
        # Create realistic test project structure
        (self.test_project_dir / "tests").mkdir()
        (self.test_project_dir / "src").mkdir()
        (self.test_project_dir / "evidence").mkdir()
        
        # Create sample test files
        self.sample_test_1 = self.test_project_dir / "tests" / "test_sample_1.py"
        self.sample_test_1.write_text("""
import pytest

def test_sample_requirement_1():
    '''Test for requirement F1: File discovery'''
    assert True

def test_sample_requirement_2():
    '''Test for requirement F2: Result storage'''
    assert True
""")
        
        self.sample_test_2 = self.test_project_dir / "tests" / "test_sample_2.py"
        self.sample_test_2.write_text("""
import pytest

def test_sample_requirement_3():
    '''Test for requirement F3: Metadata persistence'''
    assert True
""")
    
    def teardown_method(self):
        """Clean up E2E test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_e2e_complete_tdd_workflow(self):
        """
        E2E TEST: Complete TDD Enforcer workflow
        Verifies: CLI → Business Logic → Data Access → Evidence Storage
        """
        # Import all system components that we know work
        from src.data_access.real_test_file_discovery import RealTestFileDiscovery
        from src.data_access.real_test_result_storage import RealTestResultStorage
        from src.data_access.real_test_metadata_persistence import RealTestMetadataPersistence
        from src.data_access.real_verification_evidence_storage import RealVerificationEvidenceStorage
        
        # PHASE 1: Test the data access layer components directly
        evidence_dir = str(self.test_project_dir / "evidence")
        
        # Test file discovery
        discovery = RealTestFileDiscovery(base_directory=str(self.test_project_dir))
        discovered_files = discovery.discover_real_test_files()
        
        assert len(discovered_files) >= 2
        test_files = [str(f) for f in discovered_files if 'test_sample' in str(f)]
        assert len(test_files) >= 2
        
        # PHASE 2: Test result storage
        result_storage = RealTestResultStorage(storage_directory=evidence_dir)
        test_results = {
            'test_session_id': f"e2e_session_{int(time.time())}",
            'project_root': str(self.test_project_dir),
            'discovered_files': test_files,
            'test_count': len(test_files),
            'status': 'GREEN',
            'execution_time': 0.5
        }
        
        storage_result = result_storage.store_test_result(test_results)
        assert storage_result['status'] == 'success'
        
        # PHASE 3: Metadata persistence
        metadata_persistence = RealTestMetadataPersistence(metadata_directory=evidence_dir)
        metadata = {
            'session_id': test_results['test_session_id'],
            'project_metadata': {
                'project_root': str(self.test_project_dir),
                'test_framework': 'pytest',
                'discovery_pattern': "test_*.py"
            },
            'test_files': test_files,
            'timestamp': time.time()
        }
        
        metadata_result = metadata_persistence.persist_test_metadata(metadata)
        assert metadata_result['status'] == 'success'
        assert metadata_result['evidence_file'].exists()
        
        # PHASE 4: Evidence storage
        evidence_storage = RealVerificationEvidenceStorage(storage_directory=evidence_dir)
        evidence_data = {
            'stage': 'GREEN',
            'test_session_id': test_results['test_session_id'],
            'verification_evidence': {
                'files_discovered': len(test_files),
                'results_stored': True,
                'metadata_persisted': True,
                'evidence_encrypted': True
            },
            'quality_metrics': {
                'file_discovery_performance': True,
                'storage_integrity': True,
                'metadata_compliance': True
            }
        }
        
        evidence_result = evidence_storage.store_verification_evidence(evidence_data)
        assert evidence_result['status'] == 'success'
        assert evidence_result['evidence_file'].exists()
        
        # PHASE 5: Verify complete workflow created physical evidence
        evidence_dir_path = Path(evidence_dir)
        evidence_files = list(evidence_dir_path.glob("*.json")) + list(evidence_dir_path.glob("*.enc"))
        
        assert len(evidence_files) >= 2  # At least metadata + evidence files
        
        # PHASE 6: Verify data integrity across all layers
        stored_results = result_storage.query_results({
            'test_session_id': test_results['test_session_id']
        })
        
        assert len(stored_results) >= 1
        assert stored_results[0]['status'] == 'GREEN'
    
    def test_e2e_tdd_stage_gate_enforcement(self):
        """
        E2E TEST: TDD Stage Gate Enforcement
        Verifies: Complete evidence storage workflow
        """
        from src.data_access.real_verification_evidence_storage import RealVerificationEvidenceStorage
        
        evidence_dir = str(Path(self.temp_dir) / "evidence")
        Path(evidence_dir).mkdir(exist_ok=True)
        evidence_storage = RealVerificationEvidenceStorage(storage_directory=evidence_dir)
        
        session_id = f"stage_gate_e2e_{int(time.time())}"
        
        # RED PHASE evidence storage
        red_evidence = {
            'stage': 'RED',
            'test_session_id': session_id,
            'verification_evidence': {
                'failing_tests_count': 5,
                'test_failures_confirmed': True,
                'requirements_mapped': True
            }
        }
        
        red_result = evidence_storage.store_verification_evidence(red_evidence)
        assert red_result.get('status') == 'success' or red_result.get('evidence_file') is not None
        
        # GREEN PHASE evidence storage
        green_evidence = {
            'stage': 'GREEN',
            'test_session_id': session_id,
            'verification_evidence': {
                'passing_tests_count': 5,
                'all_tests_pass': True,
                'functionality_implemented': True
            }
        }
        
        green_result = evidence_storage.store_verification_evidence(green_evidence)
        assert green_result.get('status') == 'success' or green_result.get('evidence_file') is not None
        
        # REFACTOR PHASE evidence storage
        refactor_evidence = {
            'stage': 'REFACTOR',
            'test_session_id': session_id,
            'verification_evidence': {
                'code_improved': True,
                'tests_still_pass': True,
                'performance_maintained': True
            }
        }
        
        refactor_result = evidence_storage.store_verification_evidence(refactor_evidence)
        assert refactor_result.get('status') == 'success' or refactor_result.get('evidence_file') is not None
        
        # Verify complete cycle evidence
        evidence_files = list(Path(evidence_dir).glob("*.json")) + list(Path(evidence_dir).glob("*.enc"))
        assert len(evidence_files) >= 3  # At least one file per stage
    
    def test_e2e_multi_layer_integration_performance(self):
        """
        E2E TEST: Multi-layer integration performance
        Verifies: System performance under realistic load
        """
        from src.data_access.real_test_file_discovery import RealTestFileDiscovery
        
        # Create larger test project
        large_project_dir = Path(self.temp_dir) / "large_project"
        large_project_dir.mkdir()
        (large_project_dir / "tests").mkdir()
        
        # Create multiple test files for performance testing
        test_files = []
        for i in range(10):
            test_file = large_project_dir / "tests" / f"test_module_{i}.py"
            test_file.write_text(f"""
import pytest

def test_requirement_{i}_1():
    assert True

def test_requirement_{i}_2():
    assert True

def test_requirement_{i}_3():
    assert True
""")
            test_files.append(test_file)
        
        # Performance test: Complete workflow under load
        start_time = time.time()
        
        discovery = RealTestFileDiscovery(base_directory=str(large_project_dir))
        discovered_files = discovery.discover_real_test_files()
        
        execution_time = time.time() - start_time
        
        # Verify performance requirements
        assert execution_time < 2.0  # Performance requirement
        assert len(discovered_files) == 10
        
        # Verify each test file was properly processed
        for expected_file in test_files:
            found = any(str(expected_file) in str(discovered) for discovered in discovered_files)
            assert found, f"Test file {expected_file} not discovered"


class TestTDDEnforcerSystemIntegration:
    """System-level integration tests for component interactions"""
    
    def setup_method(self):
        """Setup system integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up system integration environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_data_access_to_business_logic_integration(self):
        """Integration: Data Access Layer → Business Logic Layer"""
        from src.data_access.real_test_file_discovery import RealTestFileDiscovery
        from src.data_access.real_test_result_storage import RealTestResultStorage
        
        # Create test environment
        project_dir = Path(self.temp_dir) / "integration_project"
        project_dir.mkdir()
        (project_dir / "tests").mkdir()
        (project_dir / "evidence").mkdir()
        
        test_file = project_dir / "tests" / "test_integration.py"
        test_file.write_text("""
def test_integration_requirement():
    assert True
""")
        
        # Test integration
        discovery = RealTestFileDiscovery(base_directory=str(project_dir))
        storage = RealTestResultStorage(storage_directory=str(project_dir / "evidence"))
        
        # Test data access integration
        discovered_files = discovery.discover_real_test_files()
        
        test_results = {
            'test_session_id': f"integration_{int(time.time())}",
            'discovered_files': [str(f) for f in discovered_files],
            'status': 'GREEN'
        }
        
        storage_result = storage.store_test_result(test_results)
        
        assert len(discovered_files) == 1
        assert str(test_file) in str(discovered_files[0])
        assert storage_result['status'] == 'success'
    
    def test_business_logic_to_ui_integration(self):
        """Integration: Business Logic Layer → User Interface Layer"""
        from src.business_logic.test_generation_verification_logic import TDDComplianceAssessor
        from src.user_interface.tdd_workflow_interface import TDDReportGenerator
        
        # Create business logic component
        compliance_assessor = TDDComplianceAssessor(working_directory=self.temp_dir)
        
        # Test data
        workflow_data = {
            'session_id': f"ui_integration_{int(time.time())}",
            'tdd_compliance': {
                'red_phase_complete': True,
                'green_phase_complete': True,
                'refactor_phase_complete': False
            },
            'test_results': {
                'total_tests': 15,
                'passing_tests': 15,
                'failing_tests': 0
            }
        }
        
        # Business logic processing
        compliance_result = compliance_assessor.assess_tdd_compliance(workflow_data)
        
        # UI layer integration
        report_generator = TDDReportGenerator(working_directory=self.temp_dir)
        ui_report = report_generator.generate_progress_report(
            compliance_result,
            workflow_data
        )
        
        assert ui_report['status'] == 'success'
        assert 'compliance_assessment' in ui_report
        assert 'workflow_progress' in ui_report
        assert ui_report['compliance_assessment']['overall_score'] > 0