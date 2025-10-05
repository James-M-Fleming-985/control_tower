"""
Completion Notifications - Iteration 23
Layer: User Interface Layer
Phase: REFACTOR (Enhanced Implementation)
Created: 2025-10-05

Provides simple in-app notification system for task completions.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone


class CompletionNotifications:
    """Manage and display completion notifications."""
    
    def __init__(self):
        """Initialize notification system."""
        self._notifications = []
        self._user_preferences = {}
    
    def create_notification(
        self,
        message: str,
        notification_type: str = 'info',
        user_id: str = 'default'
    ) -> Dict[str, Any]:
        """
        Create a new notification.
        
        Args:
            message: Notification message
            notification_type: Type ('info', 'success', 'warning', 'error')
            user_id: Target user ID
        
        Returns:
            Dict containing notification details
        """
        notification = {
            'id': len(self._notifications) + 1,
            'message': message,
            'type': notification_type,
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'read': False
        }
        
        self._notifications.append(notification)
        
        return notification
    
    def get_notifications(
        self,
        user_id: str = 'default',
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID to get notifications for
            unread_only: If True, only return unread notifications
        
        Returns:
            Dict containing notification list and counts
        """
        user_notifications = [
            n for n in self._notifications if n['user_id'] == user_id
        ]
        
        if unread_only:
            user_notifications = [
                n for n in user_notifications if not n['read']
            ]
        
        unread_count = sum(1 for n in user_notifications if not n['read'])
        
        return {
            'notifications': user_notifications,
            'total': len(user_notifications),
            'unread_count': unread_count
        }
    
    def mark_as_read(self, notification_id: int) -> Dict[str, Any]:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of notification to mark as read
        
        Returns:
            Dict with success status
        """
        for notification in self._notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return {'success': True, 'notification_id': notification_id}
        
        return {'success': False, 'error': 'Notification not found'}
    
    def clear_notifications(self, user_id: str = 'default') -> Dict[str, Any]:
        """
        Clear all read notifications for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with count of cleared notifications
        """
        initial_count = len(self._notifications)
        self._notifications = [
            n for n in self._notifications
            if not (n['user_id'] == user_id and n['read'])
        ]
        cleared = initial_count - len(self._notifications)
        
        return {
            'success': True,
            'cleared_count': cleared
        }
    
    def set_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set notification preferences for a user.
        
        Args:
            user_id: User ID
            preferences: Dict with preference settings
                - email_enabled: bool
                - show_info: bool
                - show_success: bool
                - show_warnings: bool
                - show_errors: bool
        
        Returns:
            Dict with updated preferences
        """
        self._user_preferences[user_id] = preferences
        
        return {
            'success': True,
            'user_id': user_id,
            'preferences': preferences
        }
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get notification preferences for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with user preferences or defaults
        """
        return self._user_preferences.get(user_id, {
            'email_enabled': False,
            'show_info': True,
            'show_success': True,
            'show_warnings': True,
            'show_errors': True
        })
