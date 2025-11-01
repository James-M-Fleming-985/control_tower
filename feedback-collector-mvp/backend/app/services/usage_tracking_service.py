"""
Usage Tracking Service
Manages subscription tier limits and usage tracking
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models import User, FeedbackRequest, FeedbackMode
from ..config.subscription_tiers import (
    SubscriptionTier,
    can_create_freetext_request,
    can_create_prompted_request,
    get_tier_limits,
    get_upgrade_recommendation
)


class UsageTrackingService:
    """Service for tracking and enforcing usage limits"""

    def __init__(self, db: Session):
        self.db = db

    def reset_monthly_usage_if_needed(self, user: User) -> None:
        """
        Reset monthly usage counters if reset date has passed

        Args:
            user: User instance
        """
        now = datetime.utcnow()

        # Initialize reset date if not set
        if not user.monthly_requests_reset_date:
            user.monthly_requests_reset_date = now + timedelta(days=30)
            user.monthly_freetext_requests = 0
            user.monthly_prompted_requests = 0
            self.db.commit()
            return

        # Reset if date has passed
        if now >= user.monthly_requests_reset_date:
            user.monthly_freetext_requests = 0
            user.monthly_prompted_requests = 0
            user.monthly_requests_reset_date = now + timedelta(days=30)
            self.db.commit()

    def get_current_usage(self, user: User) -> Dict[str, Any]:
        """
        Get current usage stats for a user

        Args:
            user: User instance

        Returns:
            Dictionary with usage stats and limits
        """
        self.reset_monthly_usage_if_needed(user)

        limits = get_tier_limits(user.subscription_tier)

        return {
            "tier": user.subscription_tier.value,
            "usage": {
                "freetext_requests": user.monthly_freetext_requests,
                "prompted_requests": user.monthly_prompted_requests,
                "reset_date": user.monthly_requests_reset_date.isoformat()
                if user.monthly_requests_reset_date else None
            },
            "limits": {
                "freetext_requests_per_month":
                    limits["freetext_requests_per_month"],
                "prompted_requests_per_month":
                    limits["prompted_requests_per_month"],
                "recipients_per_request": limits["recipients_per_request"],
                "unlimited_freetext":
                    limits["freetext_requests_per_month"] == -1,
                "unlimited_prompted":
                    limits["prompted_requests_per_month"] == -1
            },
            "remaining": {
                "freetext_requests": self._calculate_remaining(
                    user.monthly_freetext_requests,
                    limits["freetext_requests_per_month"]
                ),
                "prompted_requests": self._calculate_remaining(
                    user.monthly_prompted_requests,
                    limits["prompted_requests_per_month"]
                )
            }
        }

    def _calculate_remaining(
        self,
        current_usage: int,
        limit: int
    ) -> int:
        """
        Calculate remaining requests

        Args:
            current_usage: Current usage count
            limit: Maximum allowed (-1 for unlimited)

        Returns:
            Remaining count (-1 for unlimited)
        """
        if limit == -1:
            return -1
        return max(0, limit - current_usage)

    def can_create_request(
        self,
        user: User,
        mode: FeedbackMode,
        recipient_count: int
    ) -> Dict[str, Any]:
        """
        Check if user can create a feedback request

        Args:
            user: User instance
            mode: FeedbackMode (freetext or prompted)
            recipient_count: Number of recipients

        Returns:
            Dict with allowed (bool), reason (str), upgrade_info (dict)
        """
        self.reset_monthly_usage_if_needed(user)

        limits = get_tier_limits(user.subscription_tier)

        # Check recipient limit
        max_recipients = limits["recipients_per_request"]
        if max_recipients != -1 and recipient_count > max_recipients:
            return {
                "allowed": False,
                "reason": f"Your {user.subscription_tier.value} plan allows"
                f" up to {max_recipients} recipients per request.",
                "upgrade_info": get_upgrade_recommendation(
                    user.subscription_tier,
                    "recipients"
                )
            }

        # Check mode-specific limits
        if mode == FeedbackMode.FREETEXT:
            can_create = can_create_freetext_request(
                user.subscription_tier,
                user.monthly_freetext_requests
            )

            if not can_create:
                limit = limits["freetext_requests_per_month"]
                return {
                    "allowed": False,
                    "reason": f"You've reached your monthly limit of"
                    f" {limit} free-text requests.",
                    "current_usage": user.monthly_freetext_requests,
                    "limit": limit,
                    "upgrade_info": get_upgrade_recommendation(
                        user.subscription_tier,
                        "freetext_limit"
                    )
                }

        elif mode == FeedbackMode.PROMPTED or mode == FeedbackMode.OBJECTIVE:
            # OBJECTIVE mode uses the same limits as PROMPTED
            can_create = can_create_prompted_request(
                user.subscription_tier,
                user.monthly_prompted_requests
            )

            if not can_create:
                limit = limits["prompted_requests_per_month"]
                mode_label = (
                    "objective" if mode == FeedbackMode.OBJECTIVE
                    else "prompted"
                )
                return {
                    "allowed": False,
                    "reason": f"You've reached your monthly limit of"
                    f" {limit} {mode_label} requests.",
                    "current_usage": user.monthly_prompted_requests,
                    "limit": limit,
                    "upgrade_info": get_upgrade_recommendation(
                        user.subscription_tier,
                        "prompted_limit"
                    )
                }

        return {
            "allowed": True,
            "reason": "Request can be created"
        }

    def increment_usage(
        self,
        user: User,
        mode: FeedbackMode
    ) -> None:
        """
        Increment usage counter for a user

        Args:
            user: User instance
            mode: FeedbackMode that was used
        """
        self.reset_monthly_usage_if_needed(user)

        if mode == FeedbackMode.FREETEXT:
            user.monthly_freetext_requests += 1
        elif mode == FeedbackMode.PROMPTED or mode == FeedbackMode.OBJECTIVE:
            # OBJECTIVE mode uses the same counter as PROMPTED
            user.monthly_prompted_requests += 1

        self.db.commit()

    def get_usage_percentage(
        self,
        user: User,
        mode: FeedbackMode
    ) -> Optional[float]:
        """
        Get usage as a percentage of limit

        Args:
            user: User instance
            mode: FeedbackMode to check

        Returns:
            Percentage (0-100) or None if unlimited
        """
        self.reset_monthly_usage_if_needed(user)

        limits = get_tier_limits(user.subscription_tier)

        if mode == FeedbackMode.FREETEXT:
            limit = limits["freetext_requests_per_month"]
            current = user.monthly_freetext_requests
        else:
            limit = limits["prompted_requests_per_month"]
            current = user.monthly_prompted_requests

        if limit == -1:
            return None

        if limit == 0:
            return 100.0

        return min(100.0, (current / limit) * 100)

    def should_show_upgrade_prompt(
        self,
        user: User,
        mode: FeedbackMode,
        threshold: float = 80.0
    ) -> bool:
        """
        Check if upgrade prompt should be shown

        Args:
            user: User instance
            mode: FeedbackMode to check
            threshold: Percentage threshold (default 80%)

        Returns:
            True if upgrade prompt should be shown
        """
        usage_pct = self.get_usage_percentage(user, mode)

        if usage_pct is None:
            return False

        return usage_pct >= threshold
