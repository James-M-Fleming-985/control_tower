"""
Analytics Service
Analyzes feedback and calculates goal alignment scores
Uses keyword matching and NLP techniques
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional
import re

from ..models import (
    User, UserGoal, FeedbackRequest, 
    FeedbackResponse, UserActivity
)


# Keyword mappings for each competency area
COMPETENCY_KEYWORDS = {
    "leadership": [
        "lead", "leader", "leadership", "manage", "manager", "management",
        "direct", "delegate", "vision", "strategic", "inspire", "motivate",
        "mentor", "coach", "guide", "decision", "initiative"
    ],
    "communication": [
        "communicate", "communication", "explain", "present", "presentation",
        "articulate", "clear", "clarity", "listen", "feedback", "express",
        "speak", "write", "verbal", "written", "email", "meeting"
    ],
    "technical": [
        "technical", "skill", "expertise", "knowledge", "proficient",
        "competent", "quality", "code", "design", "implement", "solve",
        "analyze", "data", "system", "tool", "technology", "efficient"
    ],
    "collaboration": [
        "team", "collaborate", "cooperation", "together", "partner",
        "help", "support", "share", "contribute", "group", "collective",
        "inclusive", "cooperative", "helpful", "responsive"
    ],
    "innovation": [
        "innovative", "creative", "creativity", "idea", "solution",
        "improve", "improvement", "new", "fresh", "original", "think",
        "problem-solve", "initiative", "suggest", "propose"
    ],
    "reliability": [
        "reliable", "dependable", "consistent", "punctual", "deadline",
        "deliver", "complete", "finish", "follow-through", "commit",
        "responsible", "accountable", "trust", "timely", "organized"
    ]
}


def calculate_keyword_score(text: str, keywords: List[str]) -> float:
    """
    Calculate score based on keyword presence in text
    Returns a score between 0 and 1
    """
    if not text:
        return 0.0
    
    text_lower = text.lower()
    
    # Count keyword matches
    matches = 0
    for keyword in keywords:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            matches += 1
    
    # Normalize score (max out at 0.5 of keywords matched)
    max_score = len(keywords) * 0.5
    score = min(matches / max_score, 1.0) if max_score > 0 else 0
    
    return score


def analyze_feedback_alignment(
    feedback_text: str,
    user_goal: UserGoal
) -> Dict[str, float]:
    """
    Analyze feedback text and calculate alignment scores for each competency
    Returns dict with alignment scores (0-100) for each area
    """
    alignment_scores = {}
    
    # Calculate scores for each competency
    for competency, keywords in COMPETENCY_KEYWORDS.items():
        score = calculate_keyword_score(feedback_text, keywords)
        alignment_scores[f"{competency}_alignment"] = score * 100
    
    # Calculate overall goal alignment
    # Weight based on user's focus areas
    weights = {
        "leadership": 1.0,
        "communication": 1.0,
        "technical": 1.0,
        "collaboration": 1.0,
        "innovation": 1.0,
        "reliability": 1.0
    }
    
    # Increase weight for primary and secondary focus areas
    if user_goal.primary_focus_area:
        primary = user_goal.primary_focus_area.lower().replace(" ", "_")
        if primary in weights:
            weights[primary] = 2.0
    
    if user_goal.secondary_focus_area:
        secondary = user_goal.secondary_focus_area.lower().replace(" ", "_")
        if secondary in weights:
            weights[secondary] = 1.5
    
    # Calculate weighted average
    total_weight = sum(weights.values())
    weighted_score = sum(
        alignment_scores.get(f"{comp}_alignment", 0) * weight
        for comp, weight in weights.items()
    ) / total_weight
    
    alignment_scores["goal_alignment_score"] = weighted_score
    
    return alignment_scores


def analyze_sentiment(text: str) -> float:
    """
    Simple sentiment analysis
    Returns a score between -1 (negative) and 1 (positive)
    """
    positive_words = [
        "excellent", "great", "good", "outstanding", "exceptional",
        "strong", "impressive", "talented", "skilled", "effective",
        "helpful", "amazing", "wonderful", "fantastic", "brilliant",
        "thorough", "dedicated", "professional", "positive", "superb"
    ]
    
    negative_words = [
        "poor", "weak", "lacking", "insufficient", "inadequate",
        "needs improvement", "struggle", "difficult", "challenging",
        "confusing", "unclear", "ineffective", "unprofessional",
        "disappointing", "frustrating", "missed", "late", "slow"
    ]
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    total = positive_count + negative_count
    if total == 0:
        return 0.0  # Neutral
    
    sentiment = (positive_count - negative_count) / total
    return max(-1.0, min(1.0, sentiment))


def extract_key_themes(text: str) -> List[str]:
    """
    Extract key themes/topics from feedback text
    Returns list of detected themes
    """
    themes = []
    
    for competency, keywords in COMPETENCY_KEYWORDS.items():
        score = calculate_keyword_score(text, keywords)
        if score > 0.1:  # Theme is present
            themes.append(competency.replace("_", " ").title())
    
    return themes


def process_feedback_response(
    db: Session,
    response_id: int
) -> FeedbackResponse:
    """
    Process a feedback response: analyze sentiment, themes, and goal alignment
    Updates the response with calculated scores
    """
    response = db.query(FeedbackResponse).filter(
        FeedbackResponse.id == response_id
    ).first()
    
    if not response:
        return None
    
    # Get the request and user
    request = db.query(FeedbackRequest).filter(
        FeedbackRequest.id == response.request_id
    ).first()
    
    user = db.query(User).filter(User.id == request.user_id).first()
    user_goal = db.query(UserGoal).filter(
        UserGoal.user_id == user.id
    ).first()
    
    # Analyze feedback
    feedback_text = response.content
    
    # Calculate sentiment
    response.sentiment_score = analyze_sentiment(feedback_text)
    
    # Extract themes
    response.key_themes = extract_key_themes(feedback_text)
    
    # Calculate alignment scores if user has goals
    if user_goal:
        alignment = analyze_feedback_alignment(feedback_text, user_goal)
        
        response.leadership_alignment = alignment.get("leadership_alignment", 0)
        response.communication_alignment = alignment.get("communication_alignment", 0)
        response.technical_alignment = alignment.get("technical_alignment", 0)
        response.collaboration_alignment = alignment.get("collaboration_alignment", 0)
        response.innovation_alignment = alignment.get("innovation_alignment", 0)
        response.reliability_alignment = alignment.get("reliability_alignment", 0)
        response.goal_alignment_score = alignment.get("goal_alignment_score", 0)
        
        # Award points for high alignment
        if response.goal_alignment_score >= 80:
            from .gamification_service import award_points, check_and_award_achievement
            award_points(db, user.id, 25, "high_alignment_feedback")
            check_and_award_achievement(db, user.id, "aligned_achiever")
    
    db.commit()
    db.refresh(response)
    
    # Update request's average alignment
    update_request_alignment(db, request.id)
    
    return response


def update_request_alignment(db: Session, request_id: int):
    """Update the average alignment score for a request"""
    request = db.query(FeedbackRequest).filter(
        FeedbackRequest.id == request_id
    ).first()
    
    if not request:
        return
    
    # Calculate average alignment from all responses
    avg_alignment = db.query(
        func.avg(FeedbackResponse.goal_alignment_score)
    ).filter(
        FeedbackResponse.request_id == request_id,
        FeedbackResponse.goal_alignment_score.isnot(None)
    ).scalar()
    
    avg_sentiment = db.query(
        func.avg(FeedbackResponse.sentiment_score)
    ).filter(
        FeedbackResponse.request_id == request_id,
        FeedbackResponse.sentiment_score.isnot(None)
    ).scalar()
    
    request.alignment_score = avg_alignment or 0
    request.sentiment_score = avg_sentiment or 0
    
    db.commit()


def calculate_goal_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Calculate user's goal progress statistics
    Used for the dashboard
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Get total feedback count
    total_feedback = db.query(func.count(FeedbackResponse.id)).join(
        FeedbackRequest
    ).filter(
        FeedbackRequest.user_id == user_id
    ).scalar() or 0
    
    # Get average alignment score
    avg_alignment = db.query(
        func.avg(FeedbackResponse.goal_alignment_score)
    ).join(FeedbackRequest).filter(
        FeedbackRequest.user_id == user_id,
        FeedbackResponse.goal_alignment_score.isnot(None)
    ).scalar() or 0
    
    # Find top aligned area (highest average score)
    alignment_fields = [
        ("leadership", FeedbackResponse.leadership_alignment),
        ("communication", FeedbackResponse.communication_alignment),
        ("technical", FeedbackResponse.technical_alignment),
        ("collaboration", FeedbackResponse.collaboration_alignment),
        ("innovation", FeedbackResponse.innovation_alignment),
        ("reliability", FeedbackResponse.reliability_alignment)
    ]
    
    area_scores = {}
    for area_name, field in alignment_fields:
        avg_score = db.query(func.avg(field)).join(FeedbackRequest).filter(
            FeedbackRequest.user_id == user_id,
            field.isnot(None)
        ).scalar() or 0
        area_scores[area_name] = avg_score
    
    top_aligned_area = max(area_scores, key=area_scores.get) if area_scores else "N/A"
    
    # Find improvement areas (lowest scores)
    improvement_areas = sorted(
        area_scores.items(), 
        key=lambda x: x[1]
    )[:3]
    improvement_area_names = [area[0] for area in improvement_areas if area[1] < avg_alignment]
    
    return {
        "total_feedback_received": total_feedback,
        "average_alignment_score": round(avg_alignment, 1),
        "top_aligned_area": top_aligned_area.replace("_", " ").title(),
        "improvement_areas": [
            area.replace("_", " ").title() 
            for area in improvement_area_names
        ],
        "achievements_count": len(user.achievements or []),
        "level": user.level,
        "points": user.total_points
    }
