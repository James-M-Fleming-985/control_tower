import pytest
import sys
import os
import time

# Add the integration layer and src paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'integration_layer'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestCriticalFailures:
    """Test critical failures identified in Requirements Matrix analysis"""
    
    def setup_method(self):
        """Setup for critical failure tests"""
        try:
            from tdd_integration import TDDIntegration
            self.tdd = TDDIntegration()
        except ImportError:
            pytest.fail("TDDIntegration class not implemented yet - blocking critical failure tests")

    # P0 CRITICAL FAILING TESTS (Fix Today)
    
    def test_performance_optimization_data_memory_constraint(self):
        """CRITICAL P0: Memory usage must stay under 256MB during large dataset operations
        
        Maps to: REQ-PERF-001, LAYER-003-01-02-001 (Data Access)
        Issue: Memory usage exceeded 256MB limit
        Impact: DEPLOYMENT BLOCKER - affects all layers
        """
        try:
            import psutil
        except ImportError:
            pytest.fail("CRITICAL DEPENDENCY MISSING: psutil required for memory monitoring (pip install psutil)")
        
        import gc
        
        # Get baseline memory
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # This should fail until memory optimization is implemented
        try:
            from src.data_access.test_memory_manager import TestMemoryManager
            memory_manager = TestMemoryManager()
            
            # Execute memory-intensive operation that currently fails
            memory_manager.load_large_test_dataset(size_mb=100)
            
            # Force garbage collection
            gc.collect()
            
            # Check memory constraint - THIS WILL FAIL
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - baseline_memory
            
            assert memory_increase < 256, f"CRITICAL FAILURE: Memory usage {memory_increase}MB exceeds 256MB limit (REQ-PERF-001)"
            
        except ImportError as e:
            pytest.fail(f"CRITICAL FAILURE: TestMemoryManager not available: {e}")

    def test_memory_efficient_test_file_processing(self):
        """CRITICAL P0: Test file processing must use streaming/chunked approach
        
        Maps to: REQ-FUNC-001 (Test file discovery)
        Issue: Large test files cause memory bloat
        Impact: Blocks test discovery at scale
        """
        try:
            import psutil
        except ImportError:
            pytest.fail("CRITICAL DEPENDENCY MISSING: psutil required for memory monitoring")
            
        # This should fail until streaming is implemented
        test_files = [f"large_test_file_{i}.py" for i in range(50)]  # Simulate many test files
        
        # Memory tracking during test file processing
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024
        
        # This operation should fail due to memory constraints
        result = self.tdd.verify_tests(test_files)  # Will fail - not memory efficient
        
        end_memory = process.memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory
        
        assert memory_used < 100, f"CRITICAL FAILURE: Test processing used {memory_used}MB, must be <100MB"
        assert isinstance(result, bool), "verify_tests() must complete without memory errors"

    def test_complex_requirements_parsing_facade_integration(self):
        """CRITICAL P0: Requirements parser must integrate with TDD facade without import errors
        
        Maps to: REQ-FUNC-001, REQ-FUNC-004 (Test discovery, Traceability)
        Issue: Missing requirements_parser module facade integration 
        Impact: SYSTEM-WIDE FAILURE - no data ingestion possible
        """
        # This should fail until facade integration is fixed
        try:
            from src.requirements_parser.data_access_layer_parser import DataAccessLayerRequirementsParser
            from integration_layer.tdd_integration import TDDIntegration
            
            # Test that facade can use existing parsers
            tdd = TDDIntegration()
            parser = DataAccessLayerRequirementsParser("/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/FEATURE-003-01-02 TEST GENERATION VERIFICATION SYSTEM/DATA ACCESS LAYER/LAYER-003-01-02-001_data_access_requirements.md")
            
            # This should NOT fail with import errors - but currently does
            parsed_requirements = parser.parse_requirements()
            result = tdd.verify_tests(["test_based_on_requirements.py"])
            
            assert parsed_requirements is not None, "CRITICAL FAILURE: Requirements parsing failed"
            assert isinstance(result, bool), "CRITICAL FAILURE: Facade integration broken"
            
        except ImportError as e:
            assert False, f"CRITICAL FAILURE: Requirements parser facade integration broken: {e}"

    def test_requirements_traceability_integration(self):
        """CRITICAL P0: Requirements must be traceable through facade layer
        
        Maps to: REQ-FUNC-004 (Requirements traceability)
        Issue: Traceability broken due to facade complexity
        Impact: Cannot validate requirements compliance
        """
        # This should fail until traceability integration works
        try:
            from src.requirements_parser.data_access_layer_parser import DataAccessLayerRequirementsParser
            
            parser = DataAccessLayerRequirementsParser("test_requirements.md")
            
            # Parse requirements and trace through facade
            requirements = parser.parse_requirements()  # Will fail - not integrated
            
            # Facade should be able to trace requirements to tests
            traceability_result = self.tdd.verify_tests(["test_req_traceability.py"])
            
            assert requirements is not None, "CRITICAL FAILURE: Requirements parsing not integrated"
            assert isinstance(traceability_result, bool), "CRITICAL FAILURE: Requirements traceability broken"
            
        except ImportError as e:
            pytest.fail(f"CRITICAL FAILURE: Requirements parser not available: {e}")

    # P1 HIGH PRIORITY FAILING TESTS (Fix This Week)

    def test_end_to_end_workflow_validation_cross_layer_integration(self):
        """HIGH PRIORITY P1: E2E workflow must work across all layers
        
        Maps to: REQ-FUNC-002, REQ-FUNC-003 (TDD workflow, Real-time monitoring)  
        Issue: E2E integration gaps between layers
        Impact: Fragmented system - layers work individually but not together
        """
        # This should fail until cross-layer integration is complete
        try:
            from src.requirements_parser.data_access_layer_parser import DataAccessLayerRequirementsParser
            from integration_layer.tdd_integration import TDDIntegration
            
            # Test complete workflow: Requirements -> Parsing -> Verification -> Results
            parser = DataAccessLayerRequirementsParser("test_workflow_requirements.md")
            tdd = TDDIntegration()
            
            # Step 1: Parse requirements (Data Access Layer)
            parsed_data = parser.parse_requirements()  # May work individually
            
            # Step 2: Process through business logic (Integration Layer) 
            verification_result = tdd.verify_tests(["workflow_test.py"])  # May work individually
            
            # Step 3: Check stage gate (Cross-layer operation) - THIS WILL FAIL
            stage_result = tdd.check_stage_gate("RED")
            
            # Step 4: Get compliance score (Integration across all layers) - THIS WILL FAIL  
            compliance_score = tdd.get_compliance_score()
            
            # E2E validation - should work as complete workflow
            assert parsed_data is not None, "Step 1 failed: Requirements parsing"
            assert isinstance(verification_result, bool), "Step 2 failed: Test verification"  
            assert isinstance(stage_result, bool), "Step 3 FAILED: Stage gate cross-layer integration"
            assert isinstance(compliance_score, int), "Step 4 FAILED: Compliance scoring cross-layer"
            
            # Complete workflow must complete in reasonable time
            start_time = time.time()
            
            # Run complete workflow 
            full_workflow_result = self._run_complete_e2e_workflow()
            
            workflow_time = time.time() - start_time
            assert workflow_time < 5.0, f"E2E workflow took {workflow_time}s, must be <5s"
            assert full_workflow_result["success"], "CRITICAL: E2E workflow integration failed"
            
        except ImportError as e:
            pytest.fail(f"E2E WORKFLOW FAILURE: Required components not available: {e}")

    def _run_complete_e2e_workflow(self):
        """Helper method to run complete E2E workflow - will fail until integration complete"""
        try:
            # This represents the complete workflow that currently fails
            workflow_steps = [
                ("parse_requirements", lambda: True),  # Individual layer works
                ("verify_tests", lambda: self.tdd.verify_tests(["test.py"])),  # Individual layer works
                ("check_stage_gate", lambda: self.tdd.check_stage_gate("RED")),  # Integration may fail
                ("get_compliance", lambda: self.tdd.get_compliance_score()),  # Integration may fail
                ("quality_check", lambda: self.tdd.run_quality_check())  # Integration may fail
            ]
            
            results = {}
            for step_name, step_func in workflow_steps:
                results[step_name] = step_func()
                
            return {"success": all(r is not None for r in results.values()), "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_data_access_to_business_logic_handoff(self):
        """HIGH PRIORITY P1: Data must flow properly from data access to business logic
        
        Maps to: Cross-layer communication (REQ-FUNC-002)
        Issue: Layer handoff points have integration gaps
        Impact: Data doesn't flow properly between working layers
        """
        # This should fail until layer handoffs work properly
        try:
            from src.requirements_parser.data_access_layer_parser import DataAccessLayerRequirementsParser
            
            # Data Access Layer operation
            parser = DataAccessLayerRequirementsParser("handoff_test_requirements.md")
            data_access_result = parser.parse_requirements()  # This works individually
            
            # Business Logic Layer operation through facade
            business_logic_result = self.tdd.verify_tests(["based_on_parsed_data.py"])  # This may work individually
            
            # The handoff between layers - THIS IS WHERE IT FAILS
            # Data from data access should properly inform business logic decisions
            compliance_with_parsed_data = self.tdd.get_compliance_score()  # Fails - doesn't use parsed data
            
            assert data_access_result is not None, "Data Access Layer works individually"
            assert isinstance(business_logic_result, bool), "Business Logic Layer works individually" 
            assert isinstance(compliance_with_parsed_data, int), "HANDOFF FAILURE: Data not flowing between layers"
            
            # Verify the business logic actually used the parsed data (integration test)
            # This assertion will fail until proper integration
            assert compliance_with_parsed_data > 0, "INTEGRATION FAILURE: Business logic not using data access results"
            
        except ImportError as e:
            pytest.fail(f"LAYER HANDOFF FAILURE: Required components not available: {e}")

    def test_advanced_visualization_charts_dependencies(self):
        """HIGH PRIORITY P1: Visualization libraries must be available and working
        
        Maps to: REQ-USE-001 (CLI interface with progress feedback)
        Issue: Chart rendering library dependencies missing (matplotlib/plotly)
        Impact: Reduced user experience - text-only reporting
        """
        # This should fail until visualization dependencies are installed
        try:
            import matplotlib.pyplot as plt
            import plotly.graph_objects as go
            
            # Test basic chart creation capability
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 2])
            
            # Test plotly integration
            plotly_fig = go.Figure(data=go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]))
            
            assert True, "Visualization dependencies available"
            
        except ImportError as e:
            assert False, f"VISUALIZATION FAILURE: Missing dependencies: {e} (pip install matplotlib plotly)"

    def test_ui_layer_chart_rendering_integration(self):
        """HIGH PRIORITY P1: UI layer must be able to render progress charts
        
        Maps to: REQ-USE-001 (Intuitive CLI interface)
        Issue: Chart rendering not integrated with TDD facade
        Impact: Poor user experience, no visual progress feedback
        """
        # This should fail until chart rendering is integrated
        try:
            # Get quality data from facade
            quality_result = self.tdd.run_quality_check()
            
            # Attempt to create visualization of results - will fail
            import matplotlib.pyplot as plt
            
            if "score" in quality_result:
                scores = [quality_result["score"], 100 - quality_result["score"]]
                labels = ["Passed", "Remaining"]
                
                plt.pie(scores, labels=labels)
                chart_created = True
            else:
                chart_created = False
                
            assert chart_created, "VISUALIZATION FAILURE: Cannot create charts from TDD facade data"
            assert quality_result.get("score") is not None, "Quality data not available for visualization"
            
        except ImportError:
            assert False, "VISUALIZATION FAILURE: Chart libraries not available (matplotlib/plotly missing)"
        except Exception as e:
            assert False, f"INTEGRATION FAILURE: Chart rendering integration broken: {e}"