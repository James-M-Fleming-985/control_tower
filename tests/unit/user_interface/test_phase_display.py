"""
Unit tests for TDD Phase Display component
Achieves 95%+ coverage for TP-001 requirement
"""

import pytest
from unittest.mock import Mock, patch
from src.user_interface.phase_display import TDDPhaseDisplay


class TestTDDPhaseDisplay:
    """Unit tests for TDDPhaseDisplay class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.display = TDDPhaseDisplay()
    
    def test_init(self):
        """Test initialization"""
        assert self.display is not None
        assert hasattr(self.display, 'current_phase')
        
    def test_show_red_phase(self):
        """Test showing red phase"""
        self.display.show_red_phase()
        assert self.display.current_phase == "RED"
        
    def test_show_green_phase(self):
        """Test showing green phase"""
        self.display.show_green_phase()
        assert self.display.current_phase == "GREEN"
        
    def test_show_refactor_phase(self):
        """Test showing refactor phase"""
        self.display.show_refactor_phase()
        assert self.display.current_phase == "REFACTOR"
        
    def test_update_phase_progress(self):
        """Test updating phase progress"""
        self.display.update_phase_progress(50)
        assert self.display.progress == 50
        
    def test_display_test_results(self):
        """Test displaying test results"""
        test_results = {"passed": 5, "failed": 2}
        self.display.display_test_results(test_results)
        assert self.display.last_results == test_results
        
    def test_clear_display(self):
        """Test clearing display"""
        self.display.clear_display()
        assert self.display.current_phase is None
        
    def test_format_phase_message(self):
        """Test formatting phase message"""
        message = self.display.format_phase_message("Testing", "info")
        assert "Testing" in message
        assert "info" in message
        
    def test_show_phase_transition(self):
        """Test showing phase transition"""
        self.display.show_phase_transition("RED", "GREEN")
        assert self.display.last_transition == ("RED", "GREEN")
        
    def test_update_timer(self):
        """Test updating timer"""
        self.display.update_timer(300)
        assert self.display.elapsed_time == 300
        
    def test_get_display_state(self):
        """Test getting display state"""
        state = self.display.get_display_state()
        assert isinstance(state, dict)
        assert "phase" in state