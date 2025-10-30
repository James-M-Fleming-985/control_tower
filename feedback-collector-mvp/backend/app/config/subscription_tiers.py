"""
Subscription Tier Configuration for Feedback360
Defines pricing, features, and limits for each tier
"""
from typing import Dict, Any, List
from enum import Enum


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


# Pricing configuration (in GBP)
TIER_PRICING = {
    SubscriptionTier.FREE: {
        "price": 0,
        "currency": "GBP",
        "interval": None,
        "stripe_price_id_env": None,
    },
    SubscriptionTier.PRO: {
        "price": 9.99,
        "currency": "GBP",
        "interval": "month",
        "stripe_price_id_env": "PRICE_ID_PRO",
    },
    SubscriptionTier.PREMIUM: {
        "price": 24.99,
        "currency": "GBP",
        "interval": "month",
        "stripe_price_id_env": "PRICE_ID_PREMIUM",
    },
    SubscriptionTier.ENTERPRISE: {
        "price": 99.99,
        "currency": "GBP",
        "interval": "month",
        "stripe_price_id_env": "PRICE_ID_ENTERPRISE",
    },
}


# Feature configuration for each tier
TIER_FEATURES = {
    SubscriptionTier.FREE: {
        "name": "Free",
        "tagline": "Perfect for trying out feedback",
        "features": [
            "Prompted feedback only",
            "Up to 3 feedback requests per month",
            "Basic feedback templates",
            "Email notifications",
            "7-day feedback history"
        ],
        "limits": {
            "freetext_requests_per_month": 0,
            "prompted_requests_per_month": 3,
            "total_requests_per_month": 3,
            "recipients_per_request": 3,
            "feedback_history_days": 7,
            "goal_tracking": False,
            "analytics_access": False,
            "priority_support": False,
        }
    },
    SubscriptionTier.PRO: {
        "name": "Pro",
        "tagline": "For individuals serious about growth",
        "features": [
            "5 free-text feedback requests per month",
            "Unlimited prompted feedback",
            "Advanced feedback templates",
            "Goal alignment scoring",
            "Basic analytics dashboard",
            "30-day feedback history",
            "Email support"
        ],
        "limits": {
            "freetext_requests_per_month": 5,
            "prompted_requests_per_month": -1,  # -1 means unlimited
            "total_requests_per_month": -1,
            "recipients_per_request": 10,
            "feedback_history_days": 30,
            "goal_tracking": True,
            "analytics_access": True,
            "priority_support": False,
        }
    },
    SubscriptionTier.PREMIUM: {
        "name": "Premium",
        "tagline": "For professionals maximizing development",
        "features": [
            "Unlimited free-text feedback requests",
            "Unlimited prompted feedback",
            "All feedback templates",
            "Advanced goal alignment & tracking",
            "Comprehensive analytics dashboard",
            "Gamification & achievements",
            "Unlimited feedback history",
            "Priority email support",
            "Export feedback reports (PDF/CSV)"
        ],
        "limits": {
            "freetext_requests_per_month": -1,  # Unlimited
            "prompted_requests_per_month": -1,
            "total_requests_per_month": -1,
            "recipients_per_request": 25,
            "feedback_history_days": -1,  # Unlimited
            "goal_tracking": True,
            "analytics_access": True,
            "priority_support": True,
            "export_reports": True,
        }
    },
    SubscriptionTier.ENTERPRISE: {
        "name": "Enterprise",
        "tagline": "For teams and organizations",
        "features": [
            "Everything in Premium",
            "Team collaboration features",
            "Custom feedback templates",
            "Advanced team analytics",
            "API access",
            "SSO integration",
            "Dedicated account manager",
            "24/7 priority support",
            "Custom integrations"
        ],
        "limits": {
            "freetext_requests_per_month": -1,
            "prompted_requests_per_month": -1,
            "total_requests_per_month": -1,
            "recipients_per_request": -1,  # Unlimited
            "feedback_history_days": -1,
            "goal_tracking": True,
            "analytics_access": True,
            "priority_support": True,
            "export_reports": True,
            "api_access": True,
            "sso_enabled": True,
            "team_features": True,
        }
    },
}


def get_tier_limits(tier: SubscriptionTier) -> Dict[str, Any]:
    """
    Get usage limits for a subscription tier
    
    Args:
        tier: SubscriptionTier enum value
        
    Returns:
        Dictionary of limits for the tier
    """
    return TIER_FEATURES.get(tier, TIER_FEATURES[SubscriptionTier.FREE])["limits"]


def get_tier_features_list(tier: SubscriptionTier) -> List[str]:
    """
    Get feature list for a subscription tier
    
    Args:
        tier: SubscriptionTier enum value
        
    Returns:
        List of feature descriptions
    """
    return TIER_FEATURES.get(tier, TIER_FEATURES[SubscriptionTier.FREE])["features"]


def get_tier_pricing(tier: SubscriptionTier) -> Dict[str, Any]:
    """
    Get pricing info for a subscription tier
    
    Args:
        tier: SubscriptionTier enum value
        
    Returns:
        Dictionary with price, currency, and interval
    """
    return TIER_PRICING.get(tier, TIER_PRICING[SubscriptionTier.FREE])


def can_create_freetext_request(tier: SubscriptionTier, current_usage: int) -> bool:
    """
    Check if user can create a free-text feedback request
    
    Args:
        tier: User's subscription tier
        current_usage: Number of free-text requests used this month
        
    Returns:
        True if user can create another request, False otherwise
    """
    limits = get_tier_limits(tier)
    max_freetext = limits.get("freetext_requests_per_month", 0)
    
    # -1 means unlimited
    if max_freetext == -1:
        return True
    
    return current_usage < max_freetext


def can_create_prompted_request(tier: SubscriptionTier, current_usage: int) -> bool:
    """
    Check if user can create a prompted feedback request
    
    Args:
        tier: User's subscription tier
        current_usage: Number of prompted requests used this month
        
    Returns:
        True if user can create another request, False otherwise
    """
    limits = get_tier_limits(tier)
    max_prompted = limits.get("prompted_requests_per_month", 0)
    
    # -1 means unlimited
    if max_prompted == -1:
        return True
    
    return current_usage < max_prompted


def get_upgrade_recommendation(tier: SubscriptionTier, reason: str = "limits") -> Dict[str, Any]:
    """
    Get upgrade recommendation for a user
    
    Args:
        tier: Current subscription tier
        reason: Reason for upgrade suggestion
        
    Returns:
        Dictionary with recommended tier and upgrade message
    """
    if tier == SubscriptionTier.FREE:
        return {
            "recommended_tier": SubscriptionTier.PRO,
            "message": "Upgrade to Pro for free-text feedback and goal tracking!",
            "benefits": get_tier_features_list(SubscriptionTier.PRO)[:3]
        }
    elif tier == SubscriptionTier.PRO:
        return {
            "recommended_tier": SubscriptionTier.PREMIUM,
            "message": "Upgrade to Premium for unlimited requests and advanced analytics!",
            "benefits": get_tier_features_list(SubscriptionTier.PREMIUM)[:3]
        }
    elif tier == SubscriptionTier.PREMIUM:
        return {
            "recommended_tier": SubscriptionTier.ENTERPRISE,
            "message": "Upgrade to Enterprise for team features and dedicated support!",
            "benefits": get_tier_features_list(SubscriptionTier.ENTERPRISE)[:3]
        }
    
    return None
