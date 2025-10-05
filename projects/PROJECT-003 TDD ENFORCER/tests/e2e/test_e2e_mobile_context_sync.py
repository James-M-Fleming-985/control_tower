"""
E2E Test: Mobile Context Sync Workflow

Tests complete mobile context synchronization across all layers.
"""

import unittest
from src.integration.context_engine_api_integration_iteration_9 import (
    ContextEngineAPIIntegration
)
from src.integration.cross_system_security_integration_iteration_10 import (
    CrossSystemSecurityIntegration
)


class TestE2EMobileContextSync(unittest.TestCase):
    """End-to-end test for mobile context synchronization workflow"""

    def setUp(self):
        """Set up E2E test fixtures"""
        self.context_api = ContextEngineAPIIntegration()
        self.security = CrossSystemSecurityIntegration()

    def test_complete_mobile_context_sync_workflow(self):
        """Test complete mobile context sync from auth to audit"""
        # Step 1: User authenticates via mobile
        auth_event = {
            'event_type': 'mobile_authentication',
            'source_system': 'mobile_app',
            'target_system': 'context_engine',
            'user_id': 'mobile_user_123',
            'risk_level': 'low'
        }
        auth_result = self.security.audit_cross_system_security_events(
            auth_event
        )
        self.assertEqual(auth_result['status'], 'success')
        self.assertIn('audit_id', auth_result)

        # Step 2: User fetches context state
        sync_request = {
            'user_id': 'mobile_user_123',
            'local_context': {'device': 'mobile', 'status': 'active'},
            'remote_context': {'device': 'mobile', 'status': 'synced'},
            'sync_strategy': 'bidirectional'
        }
        sync_result = self.context_api.sync_with_external_context_engine(
            sync_request
        )
        self.assertEqual(sync_result['status'], 'success')
        self.assertIn('synced_context', sync_result)

        # Step 3: User pushes context changes (sync handles bidirectional)
        push_request = {
            'user_id': 'mobile_user_123',
            'local_context': {'device': 'mobile', 'data': 'updated'},
            'remote_context': {'device': 'mobile', 'data': 'current'},
            'sync_strategy': 'bidirectional'
        }
        push_result = self.context_api.sync_with_external_context_engine(
            push_request
        )
        self.assertEqual(push_result['status'], 'success')
        self.assertIn('synced_context', push_result)

        # Step 4: System logs security audit
        audit_event = {
            'event_type': 'context_sync_complete',
            'source_system': 'mobile_app',
            'target_system': 'context_engine',
            'user_id': 'mobile_user_123',
            'risk_level': 'low'
        }
        audit_result = self.security.audit_cross_system_security_events(
            audit_event
        )
        self.assertEqual(audit_result['status'], 'success')
        self.assertIn('automated_actions', audit_result)

        # Verify complete workflow
        self.assertIsNotNone(auth_result['audit_id'])
        self.assertIsNotNone(sync_result['synced_context'])
        self.assertIsNotNone(push_result['synced_context'])
        self.assertIsNotNone(audit_result['audit_id'])


if __name__ == '__main__':
    unittest.main()
