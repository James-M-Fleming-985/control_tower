from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    """Base schema for feedback"""
    content: str = Field(..., min_length=1, max_length=5000, description="Feedback content")
    category: Optional[str] = Field(None, max_length=100, description="Feedback category")
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Feedback content cannot be empty')
        return v.strip()

class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback"""
    pass

class FeedbackResponse(FeedbackBase):
    """Schema for feedback response"""
    id: int
    created_at: datetime
    status: str = "pending"
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "content": "Great service, very helpful!",
                "category": "general",
                "created_at": "2025-10-24T12:00:00",
                "status": "pending"
            }
        }

class FeedbackList(BaseModel):
    """Schema for list of feedback"""
    items: list[FeedbackResponse]
    total: int
    page: int
    page_size: int
