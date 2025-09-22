"""
Unit tests for Enforcement Display component
Achieves 95%+ coverage for TP-001 requirement
"""

import pytest
from unittest.mock import Mock, patch
from src.user_interface.enforcement_display import EnforcementStatusDisplay


class TestEnforcementStatusDisplay:
    """Unit tests for EnforcementStatusDisplay class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.display = EnforcementStatusDisplay()
    
    def test_init(self):
        """Test initialization"""
        assert self.display is not None
        assert hasattr(self.display, 'enforcement_active')
        
    def test_show_enforcement_active(self):
        """Test showing enforcement active"""
        self.display.show_enforcement_active()
        assert self.display.enforcement_active is True
        
    def test_show_enforcement_inactive(self):
        """Test showing enforcement inactive"""
        self.display.show_enforcement_inactive()
        assert self.display.enforcement_active is False
        
    def test_display_violation(self):
        """Test displaying violation"""
        violation = {"type": "missing_test", "severity": "high"}
        self.display.display_violation(violation)
        assert self.display.last_violation == violation
        
    def test_display_compliance_status(self):
        """Test displaying compliance status"""
        status = {"compliant": True, "score": 95}
        self.display.display_compliance_status(status)
        assert self.display.compliance_status == status
        
    def test_update_metrics(self):
        """Test updating metrics"""
        metrics = {"coverage": 98, "test_count": 150}
        self.display.update_metrics(metrics)
        assert self.display.current_metrics == metrics
        
    def test_show_enforcement_summary(self):
        """Test showing enforcement summary"""
        summary = self.display.show_enforcement_summary()
        assert isinstance(summary, dict)
        assert "active" in summary
        
    def test_clear_violations(self):
        """Test clearing violations"""
        self.display.clear_violations()
        assert self.display.violations == []
        
    def test_format_violation_message(self):
        """Test formatting violation message"""
        violation = {"type": "test_failure", "message": "Test failed"}
        message = self.display.format_violation_message(violation)
        assert "test_failure" in message
        
    def test_get_enforcement_status(self):
        """Test getting enforcement status"""
        status = self.display.get_enforcement_status()
        assert isinstance(status, bool)
        
    def test_toggle_enforcement(self):
        """Test toggling enforcement"""
        initial_state = self.display.enforcement_active
        self.display.toggle_enforcement()
        assert self.display.enforcement_active != initial_state