"""
Gamification Service
Handles points, levels, achievements, and user progression
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..models import (
    User, UserActivity, Achievement, 
    FeedbackRequest, FeedbackResponse
)


def calculate_level(points: int) -> int:
    """
    Calculate user level based on total points
    Level 1: 0-99 points
    Level 2: 100-249 points
    Level 3: 250-499 points
    Level 4: 500-999 points
    Level 5: 1000-1999 points
    ...and so on
    """
    if points < 100:
        return 1
    elif points < 250:
        return 2
    elif points < 500:
        return 3
    elif points < 1000:
        return 4
    elif points < 2000:
        return 5
    elif points < 4000:
        return 6
    elif points < 8000:
        return 7
    elif points < 15000:
        return 8
    elif points < 25000:
        return 9
    else:
        return 10


def award_points(
    db: Session, 
    user_id: int, 
    points: int, 
    activity_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> User:
    """Award points to user and update their level"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Add points
    user.total_points += points
    
    # Update level
    new_level = calculate_level(user.total_points)
    if new_level > user.level:
        user.level = new_level
        # Award bonus points for leveling up
        user.total_points += 50
        
        # Log level-up activity
        level_activity = UserActivity(
            user_id=user_id,
            activity_type="level_up",
            points_earned=50,
            activity_metadata={"new_level": new_level}
        )
        db.add(level_activity)
    
    # Log activity
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        points_earned=points,
        activity_metadata=metadata or {}
    )
    db.add(activity)
    
    db.commit()
    db.refresh(user)
    
    return user


def check_and_award_achievement(
    db: Session,
    user_id: int,
    achievement_id: str
) -> Optional[Achievement]:
    """Check if user has unlocked an achievement and award it"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Check if already has achievement
    if achievement_id in (user.achievements or []):
        return None
    
    # Get achievement details
    achievement = db.query(Achievement).filter(
        Achievement.achievement_id == achievement_id
    ).first()
    
    if not achievement:
        return None
    
    # Award achievement
    if user.achievements is None:
        user.achievements = []
    user.achievements.append(achievement_id)
    
    # Award points
    award_points(
        db, 
        user_id, 
        achievement.points, 
        "achievement_unlocked",
        {"achievement_id": achievement_id, "achievement_name": achievement.name}
    )
    
    # Log achievement
    activity = UserActivity(
        user_id=user_id,
        activity_type="achievement_unlocked",
        points_earned=achievement.points,
        achievement_unlocked=achievement_id,
        activity_metadata={"name": achievement.name, "tier": achievement.tier}
    )
    db.add(activity)
    
    db.commit()
    
    return achievement


def award_achievement(
    db: Session,
    user_id: int,
    achievement_id: str
) -> Optional[Achievement]:
    """Directly award an achievement (wrapper for check_and_award)"""
    return check_and_award_achievement(db, user_id, achievement_id)


def check_achievements_for_user(db: Session, user_id: int) -> List[Achievement]:
    """
    Check all achievements and award any that the user has earned
    Returns list of newly unlocked achievements
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    newly_unlocked = []
    
    # Get counts for various activities
    total_requests = db.query(func.count(FeedbackRequest.id)).filter(
        FeedbackRequest.user_id == user_id
    ).scalar()
    
    total_responses = db.query(func.count(FeedbackResponse.id)).join(
        FeedbackRequest
    ).filter(
        FeedbackRequest.user_id == user_id
    ).scalar()
    
    total_recipients = db.query(func.sum(FeedbackRequest.total_recipients)).filter(
        FeedbackRequest.user_id == user_id
    ).scalar() or 0
    
    # Check each achievement
    achievements = db.query(Achievement).all()
    
    for achievement in achievements:
        # Skip if already unlocked
        if achievement.achievement_id in (user.achievements or []):
            continue
        
        # Check criteria
        should_unlock = False
        
        if achievement.criteria_type == "requests_sent":
            should_unlock = total_requests >= achievement.criteria_threshold
        elif achievement.criteria_type == "responses_received":
            should_unlock = total_responses >= achievement.criteria_threshold
        elif achievement.criteria_type == "total_recipients":
            should_unlock = total_recipients >= achievement.criteria_threshold
        
        if should_unlock:
            unlocked = check_and_award_achievement(db, user_id, achievement.achievement_id)
            if unlocked:
                newly_unlocked.append(unlocked)
    
    return newly_unlocked


def get_user_progress(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive user progress data
    Including level, points, achievements, next level progress
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    current_level = user.level
    current_points = user.total_points
    
    # Calculate points needed for next level
    if current_level == 1:
        next_level_points = 100
    elif current_level == 2:
        next_level_points = 250
    elif current_level == 3:
        next_level_points = 500
    elif current_level == 4:
        next_level_points = 1000
    elif current_level == 5:
        next_level_points = 2000
    elif current_level == 6:
        next_level_points = 4000
    elif current_level == 7:
        next_level_points = 8000
    elif current_level == 8:
        next_level_points = 15000
    elif current_level == 9:
        next_level_points = 25000
    else:
        next_level_points = current_points + 10000  # Max level
    
    points_to_next_level = next_level_points - current_points
    progress_percentage = min(100, (current_points / next_level_points) * 100)
    
    # Get achievements
    achievements = db.query(Achievement).filter(
        Achievement.achievement_id.in_(user.achievements or [])
    ).all()
    
    return {
        "level": current_level,
        "points": current_points,
        "points_to_next_level": max(0, points_to_next_level),
        "progress_percentage": progress_percentage,
        "achievements": [
            {
                "id": a.achievement_id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "tier": a.tier,
                "points": a.points
            }
            for a in achievements
        ],
        "achievements_count": len(achievements)
    }
