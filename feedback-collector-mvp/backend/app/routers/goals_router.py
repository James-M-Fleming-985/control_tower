"""
User Goals Router
Handles goal-setting survey and goal management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..database import get_db
from ..models import User, UserGoal

router = APIRouter(prefix="/api/goals", tags=["goals"])


class GoalSurveyRequest(BaseModel):
    """Request model for goal-setting survey"""
    # Current self-assessment (1-10 scale)
    leadership_score: int = Field(ge=1, le=10, description="Leadership skills")
    communication_score: int = Field(ge=1, le=10, description="Communication skills")
    technical_skills_score: int = Field(ge=1, le=10, description="Technical expertise")
    collaboration_score: int = Field(ge=1, le=10, description="Team collaboration")
    innovation_score: int = Field(ge=1, le=10, description="Innovation & creativity")
    reliability_score: int = Field(ge=1, le=10, description="Reliability & consistency")
    
    # Focus areas
    primary_focus_area: str = Field(..., description="Main area to improve")
    secondary_focus_area: Optional[str] = Field(None, description="Secondary focus area")
    
    # Custom goals
    custom_goals: List[str] = Field(default_factory=list, description="Custom improvement goals")


class GoalSurveyResponse(BaseModel):
    """Response model for goal survey"""
    id: int
    user_id: int
    leadership_score: int
    communication_score: int
    technical_skills_score: int
    collaboration_score: int
    innovation_score: int
    reliability_score: int
    primary_focus_area: str
    secondary_focus_area: Optional[str]
    custom_goals: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserGoalStats(BaseModel):
    """User's goal progress and alignment stats"""
    total_feedback_received: int
    average_alignment_score: float
    top_aligned_area: str
    improvement_areas: List[str]
    achievements_count: int
    level: int
    points: int


@router.post("/survey", response_model=GoalSurveyResponse)
async def submit_goal_survey(
    survey: GoalSurveyRequest,
    user_email: str,  # TODO: Get from JWT auth token
    db: Session = Depends(get_db)
):
    """
    Submit or update user's goal-setting survey
    This helps the system understand what the user wants to improve
    """
    # Get or create user
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Check if user already has goals
    existing_goal = db.query(UserGoal).filter(
        UserGoal.user_id == user.id
    ).first()
    
    if existing_goal:
        # Update existing goals
        for key, value in survey.dict().items():
            setattr(existing_goal, key, value)
        goal = existing_goal
    else:
        # Create new goal
        goal = UserGoal(user_id=user.id, **survey.dict())
        db.add(goal)
        
        # Award achievement for setting goals
        from ..services.gamification_service import award_achievement
        award_achievement(db, user.id, "goal_setter")
    
    db.commit()
    db.refresh(goal)
    
    return goal


@router.get("/survey", response_model=Optional[GoalSurveyResponse])
async def get_user_goals(
    user_email: str,  # TODO: Get from JWT auth token
    db: Session = Depends(get_db)
):
    """Get user's current goals and self-assessment"""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return None
    
    goal = db.query(UserGoal).filter(UserGoal.user_id == user.id).first()
    return goal


@router.get("/stats", response_model=UserGoalStats)
async def get_goal_stats(
    user_email: str,  # TODO: Get from JWT auth token
    db: Session = Depends(get_db)
):
    """
    Get user's goal progress statistics
    Shows how well feedback aligns with their goals
    """
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from ..services.analytics_service import calculate_goal_stats
    stats = calculate_goal_stats(db, user.id)
    
    return stats


@router.get("/focus-areas")
async def get_focus_areas():
    """Get list of available focus areas for the survey"""
    return {
        "focus_areas": [
            {"id": "leadership", "label": "Leadership & Management", "icon": "👔"},
            {"id": "communication", "label": "Communication Skills", "icon": "💬"},
            {"id": "technical", "label": "Technical Expertise", "icon": "⚙️"},
            {"id": "collaboration", "label": "Team Collaboration", "icon": "👥"},
            {"id": "innovation", "label": "Innovation & Creativity", "icon": "💡"},
            {"id": "reliability", "label": "Reliability & Consistency", "icon": "✅"},
            {"id": "problem_solving", "label": "Problem Solving", "icon": "🧩"},
            {"id": "time_management", "label": "Time Management", "icon": "⏰"},
            {"id": "emotional_intelligence", "label": "Emotional Intelligence", "icon": "❤️"},
            {"id": "strategic_thinking", "label": "Strategic Thinking", "icon": "🎯"}
        ]
    }
