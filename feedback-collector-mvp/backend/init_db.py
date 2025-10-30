#!/usr/bin/env python3
"""
Database initialization and migration script
Creates all tables and seeds initial data
"""
import sys
sys.path.append('.')

from app.database import init_db, engine, SessionLocal
from app.models import Achievement
from sqlalchemy import text


def seed_achievements(db):
    """Seed initial achievements for gamification"""
    achievements_data = [
        {
            "achievement_id": "first_request",
            "name": "First Steps",
            "description": "Created your first feedback request",
            "icon": "🎯",
            "points": 10,
            "tier": "bronze",
            "criteria_type": "requests_sent",
            "criteria_threshold": 1
        },
        {
            "achievement_id": "feedback_collector",
            "name": "Feedback Collector",
            "description": "Received 10 feedback responses",
            "icon": "📬",
            "points": 50,
            "tier": "silver",
            "criteria_type": "responses_received",
            "criteria_threshold": 10
        },
        {
            "achievement_id": "insight_seeker",
            "name": "Insight Seeker",
            "description": "Received 50 feedback responses",
            "icon": "🔍",
            "points": 150,
            "tier": "gold",
            "criteria_type": "responses_received",
            "criteria_threshold": 50
        },
        {
            "achievement_id": "growth_master",
            "name": "Growth Master",
            "description": "Received 100 feedback responses",
            "icon": "🏆",
            "points": 500,
            "tier": "platinum",
            "criteria_type": "responses_received",
            "criteria_threshold": 100
        },
        {
            "achievement_id": "goal_setter",
            "name": "Goal Setter",
            "description": "Completed your professional goals survey",
            "icon": "🎓",
            "points": 25,
            "tier": "bronze",
            "criteria_type": "goals_set",
            "criteria_threshold": 1
        },
        {
            "achievement_id": "aligned_achiever",
            "name": "Aligned Achiever",
            "description": "Received feedback with 80%+ goal alignment",
            "icon": "✨",
            "points": 100,
            "tier": "gold",
            "criteria_type": "high_alignment",
            "criteria_threshold": 1
        },
        {
            "achievement_id": "consistent_improver",
            "name": "Consistent Improver",
            "description": "Requested feedback 5 times in a month",
            "icon": "📈",
            "points": 75,
            "tier": "silver",
            "criteria_type": "monthly_requests",
            "criteria_threshold": 5
        },
        {
            "achievement_id": "team_builder",
            "name": "Team Builder",
            "description": "Sent feedback requests to 20+ people",
            "icon": "👥",
            "points": 125,
            "tier": "gold",
            "criteria_type": "total_recipients",
            "criteria_threshold": 20
        }
    ]
    
    for achievement_data in achievements_data:
        # Check if achievement already exists
        existing = db.query(Achievement).filter(
            Achievement.achievement_id == achievement_data["achievement_id"]
        ).first()
        
        if not existing:
            achievement = Achievement(**achievement_data)
            db.add(achievement)
    
    db.commit()
    print(f"✅ Seeded {len(achievements_data)} achievements")


def main():
    """Run migrations"""
    print("🚀 Starting database initialization...")
    
    # Create all tables
    init_db()
    
    # Seed data
    db = SessionLocal()
    try:
        seed_achievements(db)
        print("\n✅ Database initialization complete!")
        print("\n📊 Database Schema:")
        print("   - users")
        print("   - user_goals")
        print("   - feedback_requests")
        print("   - feedback_recipients")
        print("   - feedback_responses")
        print("   - user_activities")
        print("   - achievements")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
