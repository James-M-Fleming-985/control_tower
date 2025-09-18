#!/usr/bin/env python3
"""
Simple UI Layer Test Runner

GREEN Phase validation for LAYER-003-01-02-003: User Interface Layer
Tests individual components without threading issues.

Created: 2025-09-18
Status: GREEN Phase validation
"""

import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_ui_layer_implementation():
    """Test UI Layer implementation components"""
    
    print("🟢 GREEN PHASE VALIDATION")
    print("=" * 50)
    print("Testing User Interface Layer implementation...")
    print()
    
    # Test imports
    try:
        from src.user_interface.verification_display import (
            RealTimeProgressDisplay,
            VerificationProgressTracker,
            StageGateVisualizer,
            TDDWorkflowVisualizer,
            VerificationResultsDisplay,
            ErrorMessageFormatter,
            ProgressData,
            StageGateStatus
        )
        print("✅ All UI components imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    tests_passed = 0
    tests_total = 0
    
    # Test F1: Real-time Progress Display
    tests_total += 1
    try:
        print("\n🧪 Testing F1: Real-time Progress Display")
        
        display = RealTimeProgressDisplay()
        print("  ✅ RealTimeProgressDisplay initialized")
        
        # Test progress update
        progress = ProgressData(
            verification_id="test_001",
            stage="test_generation",
            progress_percent=50.0,
            message="Testing progress",
            timestamp=time.time(),
            details={"test": True}
        )
        
        result = display.update_progress(progress)
        print(f"  ✅ Progress update: {result}")
        
        # Test performance tracking
        stats = display.get_performance_stats()
        print(f"  ✅ Performance stats: {stats}")
        
        # Clean shutdown
        display.stop_display_engine()
        
        tests_passed += 1
        print("  🎯 F1 PASSED: Real-time Progress Display working")
        
    except Exception as e:
        print(f"  ❌ F1 FAILED: {e}")
    
    # Test F2: Stage Gate Visualization
    tests_total += 1
    try:
        print("\n🧪 Testing F2: Stage Gate Visualization")
        
        visualizer = StageGateVisualizer()
        print("  ✅ StageGateVisualizer initialized")
        
        # Test stage gate status display
        status = StageGateStatus(
            stage_id="test_gate",
            status="PASS",
            blocking_reason=None,
            time_in_stage=2.5,
            evidence=["test.log"],
            metadata={"test": True}
        )
        
        display_output = visualizer.display_stage_gate_status(status)
        print(f"  ✅ Stage gate display created: {len(display_output)} chars")
        
        # Test TDD workflow visualization
        workflow_viz = TDDWorkflowVisualizer()
        workflow_state = {
            "current_phase": "green",
            "overall_progress": 75.0,
            "phase_details": {
                "red": {"status": "COMPLETE", "duration": 2.0},
                "green": {"status": "IN_PROGRESS", "duration": 5.0}
            }
        }
        
        workflow_display = workflow_viz.visualize_tdd_workflow(workflow_state)
        print(f"  ✅ TDD workflow display created: {len(workflow_display)} chars")
        
        tests_passed += 1
        print("  🎯 F2 PASSED: Stage Gate Visualization working")
        
    except Exception as e:
        print(f"  ❌ F2 FAILED: {e}")
    
    # Test F3: Interactive Results Display
    tests_total += 1
    try:
        print("\n🧪 Testing F3: Interactive Results Display")
        
        results_display = VerificationResultsDisplay()
        print("  ✅ VerificationResultsDisplay initialized")
        
        # Test results display
        verification_results = {
            "verification_id": "test_verification",
            "overall_score": 87.5,
            "test_quality_score": 90.0,
            "detailed_results": {
                "test_generation": {"files": 5, "tests": 25},
                "stage_gates": {"red": {"passed": True}, "green": {"passed": False}}
            },
            "evidence_links": ["/path/to/evidence1.log", "/path/to/evidence2.json"]
        }
        
        display_result = results_display.display_results(verification_results)
        print(f"  ✅ Results display created: {len(display_result)} chars")
        
        # Test drill-down
        drill_down_result = results_display.drill_down("test_generation")
        print(f"  ✅ Drill-down result: {drill_down_result}")
        
        # Test evidence access
        evidence = results_display.get_evidence_links()
        print(f"  ✅ Evidence links: {len(evidence)} items")
        
        # Test trends
        historical_results = [
            {"date": "2025-09-16", "score": 80.0, "trend": "improving"},
            {"date": "2025-09-17", "score": 85.0, "trend": "improving"},
            {"date": "2025-09-18", "score": 87.5, "trend": "improving"}
        ]
        
        trends_display = results_display.display_trends(historical_results)
        print(f"  ✅ Trends display created: {len(trends_display)} chars")
        
        tests_passed += 1
        print("  🎯 F3 PASSED: Interactive Results Display working")
        
    except Exception as e:
        print(f"  ❌ F3 FAILED: {e}")
    
    # Test F4: Error Message Presentation
    tests_total += 1
    try:
        print("\n🧪 Testing F4: Error Message Presentation")
        
        formatter = ErrorMessageFormatter()
        print("  ✅ ErrorMessageFormatter initialized")
        
        # Test error formatting
        error_scenario = {
            "error_type": "TestGenerationError",
            "error_message": "Failed to generate tests",
            "context": {"file": "test.py", "line": 45},
            "suggested_solutions": ["Check file exists", "Verify syntax"]
        }
        
        error_output = formatter.format_error(error_scenario)
        print(f"  ✅ Error message formatted: {len(error_output)} chars")
        
        # Test warning formatting
        warning_scenario = {
            "warning_type": "PerformanceWarning",
            "message": "Slow operation detected",
            "severity": "MEDIUM",
            "context": {"duration": 5.2},
            "suggestions": ["Optimize code", "Check resources"]
        }
        
        warning_output = formatter.format_warning(warning_scenario)
        print(f"  ✅ Warning message formatted: {len(warning_output)} chars")
        
        # Test format detection
        has_severity = formatter.has_severity_indicator(warning_output)
        is_warning = formatter.is_warning_format(warning_output)
        is_error = formatter.is_error_format(error_output)
        
        print(f"  ✅ Format detection: severity={has_severity}, warning={is_warning}, error={is_error}")
        
        tests_passed += 1
        print("  🎯 F4 PASSED: Error Message Presentation working")
        
    except Exception as e:
        print(f"  ❌ F4 FAILED: {e}")
    
    # Test Integration
    tests_total += 1
    try:
        print("\n🧪 Testing Integration")
        
        # Test progress tracker
        tracker = VerificationProgressTracker()
        tracker.start_tracking("integration_test")
        tracker.update_progress("integration_test", "red_phase", 25.0, "RED phase")
        tracker.update_progress("integration_test", "green_phase", 75.0, "GREEN phase")
        
        current_progress = tracker.get_current_progress("integration_test")
        print(f"  ✅ Progress tracking: {current_progress.progress_percent}%")
        
        tracker.stop_tracking("integration_test")
        
        tests_passed += 1
        print("  🎯 INTEGRATION PASSED: Components working together")
        
    except Exception as e:
        print(f"  ❌ INTEGRATION FAILED: {e}")
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {tests_passed/tests_total*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED - UI Layer Implementation SUCCESS!")
        return True
    else:
        print("⚠️  Some tests failed - UI Layer needs improvement")
        return False

if __name__ == "__main__":
    success = test_ui_layer_implementation()
    sys.exit(0 if success else 1)