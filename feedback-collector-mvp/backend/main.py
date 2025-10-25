from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os
from dotenv import load_dotenv
from app.routers.stripe_router import router as stripe_router

# Load environment variables
load_dotenv()

app = FastAPI(title="Anonymous Feedback Collector API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe routes (checkout, webhook, portal)
app.include_router(stripe_router, prefix="/api/stripe")

# In-memory storage (replace with database in production)
feedback_storage: List[dict] = []

class FeedbackCreate(BaseModel):
    content: str
    category: Optional[str] = "general"

class FeedbackResponse(BaseModel):
    id: int
    content: str
    category: str
    created_at: datetime
    status: str = "received"

@app.get("/")
async def root():
    return {
        "message": "Anonymous Feedback Collector API",
        "version": "1.0.0",
        "endpoints": {
            "/api/feedback": "POST - Submit feedback",
            "/api/feedback": "GET - List all feedback (admin)",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/feedback", response_model=FeedbackResponse)
async def create_feedback(feedback: FeedbackCreate):
    """Submit anonymous feedback"""
    if not feedback.content.strip():
        raise HTTPException(status_code=400, detail="Feedback content cannot be empty")
    
    if len(feedback.content) > 5000:
        raise HTTPException(status_code=400, detail="Feedback content too long (max 5000 characters)")
    
    new_feedback = {
        "id": len(feedback_storage) + 1,
        "content": feedback.content.strip(),
        "category": feedback.category or "general",
        "created_at": datetime.utcnow(),
        "status": "received"
    }
    
    feedback_storage.append(new_feedback)
    
    # TODO: Send email notification here
    # send_email_notification(new_feedback)
    
    return FeedbackResponse(**new_feedback)

@app.get("/api/feedback", response_model=List[FeedbackResponse])
async def list_feedback(skip: int = 0, limit: int = 100):
    """List all feedback (for admin view)"""
    return [FeedbackResponse(**fb) for fb in feedback_storage[skip:skip + limit]]

@app.get("/api/stats")
async def get_stats():
    """Get feedback statistics"""
    total = len(feedback_storage)
    by_category = {}
    for fb in feedback_storage:
        category = fb.get("category", "general")
        by_category[category] = by_category.get(category, 0) + 1
    
    return {
        "total_feedback": total,
        "by_category": by_category,
        "last_feedback": feedback_storage[-1] if feedback_storage else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
