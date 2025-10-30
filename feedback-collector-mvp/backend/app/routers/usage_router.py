"""
Usage Tracking Router
API endpoints for checking and managing usage limits
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database import get_db
from ..models import User, FeedbackMode
from ..services.usage_tracking_service import UsageTrackingService

router = APIRouter()


@router.get("/usage/{user_id}")
async def get_user_usage(
    user_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current usage stats for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Usage statistics and limits
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    usage_service = UsageTrackingService(db)
    return usage_service.get_current_usage(user)


@router.post("/check-limit/{user_id}")
async def check_request_limit(
    user_id: int,
    mode: str,
    recipient_count: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check if user can create a feedback request

    Args:
        user_id: User ID
        mode: Feedback mode (freetext or prompted)
        recipient_count: Number of recipients
        db: Database session

    Returns:
        Dict with allowed status and upgrade info if needed
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert string mode to enum
    try:
        feedback_mode = FeedbackMode(mode.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {mode}. Must be 'freetext' or 'prompted'"
        )

    usage_service = UsageTrackingService(db)
    result = usage_service.can_create_request(
        user,
        feedback_mode,
        recipient_count
    )

    return result


@router.get("/upgrade-recommendation/{user_id}")
async def get_upgrade_recommendation_for_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get upgrade recommendation for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Upgrade recommendation details
    """
    from ..config.subscription_tiers import get_upgrade_recommendation

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recommendation = get_upgrade_recommendation(user.subscription_tier)

    if not recommendation:
        return {
            "has_recommendation": False,
            "message": "You're on the highest tier!"
        }

    return {
        "has_recommendation": True,
        **recommendation
    }
