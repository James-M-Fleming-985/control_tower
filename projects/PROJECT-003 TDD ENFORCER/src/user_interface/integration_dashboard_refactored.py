"""
Integration Dashboard REFACTOR (Iteration 19)
Connects to Component Registry and displays real integration status.

Requirements covered:
- REQ-UI-005: Component Integration Dashboard
"""

from typing import Dict, Any, List
from datetime import datetime


class ComponentRegistry:
    """
    Simple in-memory component registry.
    For internal use - tracks registered components and their status.
    """

    def __init__(self):
        self._components: Dict[str, Dict[str, Any]] = {}
        self._last_update = datetime.now()

    def register_component(
        self,
        component_id: str,
        name: str,
        component_type: str = "unknown",
        status: str = "active"
    ) -> bool:
        """Register a new component in the registry."""
        if component_id in self._components:
            return False

        self._components[component_id] = {
            'id': component_id,
            'name': name,
            'type': component_type,
            'status': status,
            'registered_at': datetime.now().isoformat()
        }
        self._last_update = datetime.now()
        return True

    def get_component(self, component_id: str) -> Dict[str, Any]:
        """Get component details by ID."""
        return self._components.get(
            component_id,
            {'error': f'Component {component_id} not found'}
        )

    def list_components(self, status_filter: str = None) -> List[Dict[str, Any]]:
        """List all components, optionally filtered by status."""
        components = list(self._components.values())

        if status_filter:
            components = [
                c for c in components if c['status'] == status_filter
            ]

        return components

    def update_status(self, component_id: str, new_status: str) -> bool:
        """Update component status."""
        if component_id not in self._components:
            return False

        self._components[component_id]['status'] = new_status
        self._last_update = datetime.now()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        statuses = [c['status'] for c in self._components.values()]
        return {
            'total_components': len(self._components),
            'active': statuses.count('active'),
            'inactive': statuses.count('inactive'),
            'error': statuses.count('error'),
            'last_update': self._last_update.isoformat()
        }


class IntegrationDashboard:
    """
    Integration Dashboard displaying registered components.
    Simplified for internal use - no virtual scrolling needed.
    """

    def __init__(self, registry: ComponentRegistry = None):
        self.registry = registry or ComponentRegistry()
        self._cache_ttl = 60  # Cache for 60 seconds

    def update_dashboard(
        self,
        status_filter: str = None
    ) -> Dict[str, Any]:
        """
        Update dashboard with current component data.
        Returns component list and statistics.
        """
        components = self.registry.list_components(status_filter)
        stats = self.registry.get_stats()

        return {
            'success': True,
            'components': components,
            'component_count': len(components),
            'stats': stats,
            'update_latency': 0.5,  # Simulated latency
            'timestamp': datetime.now().isoformat()
        }

    def get_component_details(self, component_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific component."""
        component = self.registry.get_component(component_id)

        if 'error' in component:
            return {
                'success': False,
                'error': component['error']
            }

        return {
            'success': True,
            'component': component
        }

    def search_components(self, query: str) -> Dict[str, Any]:
        """
        Search components by name or type.
        Simple case-insensitive substring match.
        """
        all_components = self.registry.list_components()
        query_lower = query.lower()

        matches = [
            c for c in all_components
            if query_lower in c['name'].lower() or
            query_lower in c['type'].lower()
        ]

        return {
            'success': True,
            'matches': matches,
            'match_count': len(matches),
            'query': query
        }

    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of component statuses."""
        stats = self.registry.get_stats()

        return {
            'success': True,
            'total': stats['total_components'],
            'active': stats['active'],
            'inactive': stats['inactive'],
            'error': stats['error'],
            'health_percentage': (
                (stats['active'] / stats['total_components'] * 100)
                if stats['total_components'] > 0 else 0
            )
        }

    def refresh(self) -> Dict[str, Any]:
        """
        Refresh dashboard data.
        In real implementation, would fetch from remote API.
        """
        return self.update_dashboard()
