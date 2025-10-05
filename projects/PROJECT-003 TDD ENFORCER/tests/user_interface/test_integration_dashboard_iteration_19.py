"""
Tests for Integration Dashboard REFACTOR (Iteration 19)
"""

import pytest
from src.user_interface.integration_dashboard_refactored import (
    ComponentRegistry,
    IntegrationDashboard
)


class TestComponentRegistry:
    """Test component registry functionality."""

    def setup_method(self):
        """Setup test registry."""
        self.registry = ComponentRegistry()

    def test_register_new_component(self):
        """Test registering a new component."""
        result = self.registry.register_component(
            "comp-1",
            "Test Component",
            "service",
            "active"
        )

        assert result is True
        assert len(self.registry.list_components()) == 1

    def test_register_duplicate_component(self):
        """Test registering duplicate component fails."""
        self.registry.register_component("comp-1", "Test 1")
        result = self.registry.register_component("comp-1", "Test 2")

        assert result is False
        assert len(self.registry.list_components()) == 1

    def test_get_component(self):
        """Test getting component by ID."""
        self.registry.register_component("comp-1", "Test", "api")
        component = self.registry.get_component("comp-1")

        assert component['id'] == "comp-1"
        assert component['name'] == "Test"
        assert component['type'] == "api"

    def test_get_nonexistent_component(self):
        """Test getting nonexistent component returns error."""
        component = self.registry.get_component("missing")

        assert 'error' in component

    def test_list_all_components(self):
        """Test listing all components."""
        self.registry.register_component("comp-1", "Test 1")
        self.registry.register_component("comp-2", "Test 2")

        components = self.registry.list_components()

        assert len(components) == 2

    def test_list_components_by_status(self):
        """Test filtering components by status."""
        self.registry.register_component("comp-1", "Test 1", status="active")
        self.registry.register_component("comp-2", "Test 2", status="inactive")
        self.registry.register_component("comp-3", "Test 3", status="active")

        active = self.registry.list_components(status_filter="active")

        assert len(active) == 2
        assert all(c['status'] == "active" for c in active)

    def test_update_status(self):
        """Test updating component status."""
        self.registry.register_component("comp-1", "Test", status="active")
        result = self.registry.update_status("comp-1", "inactive")

        assert result is True
        component = self.registry.get_component("comp-1")
        assert component['status'] == "inactive"

    def test_update_status_nonexistent(self):
        """Test updating nonexistent component fails."""
        result = self.registry.update_status("missing", "active")

        assert result is False

    def test_get_stats(self):
        """Test registry statistics."""
        self.registry.register_component("c1", "T1", status="active")
        self.registry.register_component("c2", "T2", status="inactive")
        self.registry.register_component("c3", "T3", status="error")

        stats = self.registry.get_stats()

        assert stats['total_components'] == 3
        assert stats['active'] == 1
        assert stats['inactive'] == 1
        assert stats['error'] == 1


class TestIntegrationDashboard:
    """Test integration dashboard functionality."""

    def setup_method(self):
        """Setup test dashboard with sample data."""
        self.registry = ComponentRegistry()
        self.registry.register_component("comp-1", "Component 1", "service")
        self.registry.register_component("comp-2", "Component 2", "api")
        self.dashboard = IntegrationDashboard(self.registry)

    def test_update_dashboard(self):
        """Test dashboard update returns components."""
        result = self.dashboard.update_dashboard()

        assert result['success'] is True
        assert len(result['components']) == 2
        assert result['component_count'] == 2

    def test_update_dashboard_with_filter(self):
        """Test dashboard update with status filter."""
        self.registry.update_status("comp-1", "inactive")
        result = self.dashboard.update_dashboard(status_filter="active")

        assert result['success'] is True
        assert result['component_count'] == 1
        assert result['components'][0]['id'] == "comp-2"

    def test_get_component_details_success(self):
        """Test getting component details."""
        result = self.dashboard.get_component_details("comp-1")

        assert result['success'] is True
        assert result['component']['name'] == "Component 1"

    def test_get_component_details_failure(self):
        """Test getting nonexistent component details."""
        result = self.dashboard.get_component_details("missing")

        assert result['success'] is False
        assert 'error' in result

    def test_search_components_by_name(self):
        """Test searching components by name."""
        result = self.dashboard.search_components("Component 1")

        assert result['success'] is True
        assert result['match_count'] == 1
        assert result['matches'][0]['name'] == "Component 1"

    def test_search_components_by_type(self):
        """Test searching components by type."""
        result = self.dashboard.search_components("service")

        assert result['success'] is True
        assert result['match_count'] == 1
        assert result['matches'][0]['type'] == "service"

    def test_search_case_insensitive(self):
        """Test search is case-insensitive."""
        result = self.dashboard.search_components("COMPONENT")

        assert result['success'] is True
        assert result['match_count'] == 2  # Matches both components

    def test_search_no_results(self):
        """Test search with no matches."""
        result = self.dashboard.search_components("nonexistent")

        assert result['success'] is True
        assert result['match_count'] == 0

    def test_get_status_summary(self):
        """Test status summary calculation."""
        self.registry.register_component("comp-3", "Test 3", status="error")
        result = self.dashboard.get_status_summary()

        assert result['success'] is True
        assert result['total'] == 3
        assert result['active'] == 2
        assert result['error'] == 1

    def test_health_percentage_calculation(self):
        """Test health percentage is calculated correctly."""
        self.registry.update_status("comp-1", "inactive")
        result = self.dashboard.get_status_summary()

        # 1 active out of 2 total = 50%
        assert result['health_percentage'] == 50.0

    def test_refresh(self):
        """Test dashboard refresh returns updated data."""
        result = self.dashboard.refresh()

        assert result['success'] is True
        assert 'components' in result
        assert 'stats' in result
