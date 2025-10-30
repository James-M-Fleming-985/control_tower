"""
Database Models for Feedback360
Includes users, feedback requests, responses, goals, and analytics
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Float, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class FeedbackContext(str, enum.Enum):
    """Context for feedback request"""
    PROFESSIONAL = "professional"
    PERSONAL = "personal"


class FeedbackMode(str, enum.Enum):
    """Mode of feedback collection"""
    FREETEXT = "freetext"
    PROMPTED = "prompted"
    OBJECTIVE = "objective"


class User(Base):
    """User model with subscription and goal tracking"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Subscription info
    subscription_tier = Column(
        SQLEnum(SubscriptionTier), 
        default=SubscriptionTier.FREE
    )
    stripe_customer_id = Column(String(255), unique=True, index=True)
    subscription_status = Column(String(50))  # active, canceled, past_due, etc.
    subscription_ends_at = Column(DateTime(timezone=True))
    
    # Usage tracking
    monthly_freetext_requests = Column(Integer, default=0)
    monthly_prompted_requests = Column(Integer, default=0)
    monthly_requests_reset_date = Column(DateTime(timezone=True))
    
    # Gamification
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    achievements = Column(JSON, default=list)  # List of achievement IDs
    
    # Relationships
    goals = relationship("UserGoal", back_populates="user", cascade="all, delete-orphan")
    feedback_requests = relationship("FeedbackRequest", back_populates="user", cascade="all, delete-orphan")


class UserGoal(Base):
    """User's professional development goals for alignment scoring"""
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Goal categories (professional development areas)
    leadership_score = Column(Integer, default=5)  # 1-10 scale
    communication_score = Column(Integer, default=5)
    technical_skills_score = Column(Integer, default=5)
    collaboration_score = Column(Integer, default=5)
    innovation_score = Column(Integer, default=5)
    reliability_score = Column(Integer, default=5)
    
    # Target areas (what user wants to improve)
    primary_focus_area = Column(String(100))  # e.g., "leadership", "communication"
    secondary_focus_area = Column(String(100))
    
    # Custom goals
    custom_goals = Column(JSON, default=list)  # ["Improve presentation skills", ...]
    
    # Relationship
    user = relationship("User", back_populates="goals")


class FeedbackRequest(Base):
    """Feedback request sent to recipients"""
    __tablename__ = "feedback_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Request details
    title = Column(String(255), nullable=False)
    context = Column(SQLEnum(FeedbackContext), default=FeedbackContext.PROFESSIONAL)
    mode = Column(SQLEnum(FeedbackMode), default=FeedbackMode.FREETEXT)
    
    # Prompts/questions
    prompts = Column(JSON, default=list)  # List of questions for prompted mode
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    
    # Recipients count
    total_recipients = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    
    # Analytics
    alignment_score = Column(Float)  # How well responses align with goals (0-100)
    sentiment_score = Column(Float)  # Overall sentiment (-1 to 1)
    
    # Relationships
    user = relationship("User", back_populates="feedback_requests")
    responses = relationship("FeedbackResponse", back_populates="request", cascade="all, delete-orphan")
    recipients = relationship("FeedbackRecipient", back_populates="request", cascade="all, delete-orphan")


class FeedbackRecipient(Base):
    """Individual recipient of a feedback request"""
    __tablename__ = "feedback_recipients"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("feedback_requests.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Recipient info (anonymous token-based)
    email = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Status
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True))
    has_responded = Column(Boolean, default=False)
    responded_at = Column(DateTime(timezone=True))
    
    # Relationship
    request = relationship("FeedbackRequest", back_populates="recipients")


class FeedbackResponse(Base):
    """Anonymous feedback response"""
    __tablename__ = "feedback_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("feedback_requests.id"), nullable=False)
    recipient_token = Column(String(255), index=True)  # Link to recipient anonymously
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Response content
    content = Column(Text, nullable=False)
    prompted_responses = Column(JSON)  # For prompted mode: {question: answer}
    
    # AI Analysis
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    key_themes = Column(JSON, default=list)  # Extracted themes/topics
    
    # Goal alignment scoring
    leadership_alignment = Column(Float)  # How much this response relates to leadership
    communication_alignment = Column(Float)
    technical_alignment = Column(Float)
    collaboration_alignment = Column(Float)
    innovation_alignment = Column(Float)
    reliability_alignment = Column(Float)
    
    # Overall alignment with user's goals
    goal_alignment_score = Column(Float)  # 0-100 score
    
    # Relationship
    request = relationship("FeedbackRequest", back_populates="responses")


class UserActivity(Base):
    """Track user activities for gamification and analytics"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Activity details
    activity_type = Column(String(100), nullable=False)
    points_earned = Column(Integer, default=0)
    activity_metadata = Column(JSON)  # Changed from 'metadata'
    
    # Achievement tracking
    achievement_unlocked = Column(String(100))


class Achievement(Base):
    """Achievement definitions for gamification"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(50))  # Emoji or icon name
    points = Column(Integer, default=0)
    tier = Column(String(50))  # bronze, silver, gold, platinum
    
    # Unlock criteria
    criteria_type = Column(String(100))  # requests_sent, responses_received, etc.
    criteria_threshold = Column(Integer)  # Number needed to unlock
