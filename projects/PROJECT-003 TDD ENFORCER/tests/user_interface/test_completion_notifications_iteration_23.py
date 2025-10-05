"""
Tests for Completion Notifications - Iteration 23
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.user_interface.completion_notifications_refactored import (
    CompletionNotifications
)


class TestCompletionNotifications:
    """Test suite for Completion Notifications"""
    
    @pytest.fixture
    def notifier(self):
        """Create CompletionNotifications instance"""
        return CompletionNotifications()
    
    def test_create_notification(self, notifier):
        """Should create a new notification"""
        result = notifier.create_notification(
            message='Task completed',
            notification_type='success'
        )
        
        assert result['id'] == 1
        assert result['message'] == 'Task completed'
        assert result['type'] == 'success'
        assert result['read'] is False
        assert 'created_at' in result
    
    def test_get_notifications_all(self, notifier):
        """Should get all notifications for user"""
        notifier.create_notification('Test 1', 'info')
        notifier.create_notification('Test 2', 'success')
        
        result = notifier.get_notifications('default')
        
        assert result['total'] == 2
        assert len(result['notifications']) == 2
        assert result['unread_count'] == 2
    
    def test_get_notifications_unread_only(self, notifier):
        """Should get only unread notifications"""
        n1 = notifier.create_notification('Test 1', 'info')
        notifier.create_notification('Test 2', 'success')
        
        # Mark one as read
        notifier.mark_as_read(n1['id'])
        
        result = notifier.get_notifications('default', unread_only=True)
        
        assert len(result['notifications']) == 1
        assert result['notifications'][0]['message'] == 'Test 2'
    
    def test_mark_as_read(self, notifier):
        """Should mark notification as read"""
        notification = notifier.create_notification('Test', 'info')
        
        result = notifier.mark_as_read(notification['id'])
        
        assert result['success'] is True
        assert result['notification_id'] == notification['id']
        
        # Verify it's actually marked as read
        notifications = notifier.get_notifications('default')
        assert notifications['unread_count'] == 0
    
    def test_mark_as_read_not_found(self, notifier):
        """Should handle marking non-existent notification"""
        result = notifier.mark_as_read(999)
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_clear_notifications(self, notifier):
        """Should clear read notifications"""
        n1 = notifier.create_notification('Test 1', 'info')
        notifier.create_notification('Test 2', 'success')
        
        # Mark one as read
        notifier.mark_as_read(n1['id'])
        
        result = notifier.clear_notifications('default')
        
        assert result['success'] is True
        assert result['cleared_count'] == 1
        
        # Verify only unread remain
        remaining = notifier.get_notifications('default')
        assert remaining['total'] == 1
    
    def test_set_preferences(self, notifier):
        """Should set user preferences"""
        preferences = {
            'email_enabled': True,
            'show_info': False,
            'show_success': True
        }
        
        result = notifier.set_preferences('user123', preferences)
        
        assert result['success'] is True
        assert result['user_id'] == 'user123'
        assert result['preferences'] == preferences
    
    def test_get_preferences_default(self, notifier):
        """Should return default preferences for new user"""
        result = notifier.get_preferences('newuser')
        
        assert result['email_enabled'] is False
        assert result['show_info'] is True
        assert result['show_success'] is True
        assert result['show_warnings'] is True
        assert result['show_errors'] is True
    
    def test_get_preferences_custom(self, notifier):
        """Should return custom preferences after setting"""
        custom = {'email_enabled': True, 'show_info': False}
        notifier.set_preferences('user123', custom)
        
        result = notifier.get_preferences('user123')
        
        assert result == custom
