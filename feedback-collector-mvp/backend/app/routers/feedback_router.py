from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import secrets
from datetime import datetime

from ..email_service import email_service

router = APIRouter()

# In-memory storage for feedback requests (replace with database)
feedback_requests = {}
response_tokens = {}


class FeedbackRequest(BaseModel):
    context: str = "professional"
    mode: str = "standard"
    emails: List[EmailStr]
    custom_message: str = ""


class FeedbackResponse(BaseModel):
    token: str
    content: str
    rating: int = None


@router.post("/requests")
async def create_feedback_request(request: FeedbackRequest):
    """Create a new feedback request and send emails to recipients"""
    
    if not request.emails:
        raise HTTPException(status_code=400, detail="At least one email required")
    
    if len(request.emails) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 recipients allowed"
        )
    
    # Generate unique request ID
    request_id = secrets.token_urlsafe(16)
    
    # Store request
    feedback_requests[request_id] = {
        "id": request_id,
        "context": request.context,
        "mode": request.mode,
        "custom_message": request.custom_message,
        "recipients": request.emails,
        "created_at": datetime.utcnow().isoformat(),
        "responses": []
    }
    
    # Send emails to each recipient
    sent_count = 0
    failed = []
    
    for recipient_email in request.emails:
        # Generate unique response token
        token = secrets.token_urlsafe(32)
        response_tokens[token] = {
            "request_id": request_id,
            "recipient_email": recipient_email,
            "created_at": datetime.utcnow().isoformat(),
            "responded": False
        }
        
        # Send email
        success = await email_service.send_feedback_request(
            recipient_email=recipient_email,
            request_id=request_id,
            token=token,
            context=request.context,
            custom_message=request.custom_message
        )
        
        if success:
            sent_count += 1
        else:
            failed.append(recipient_email)
    
    return {
        "request_id": request_id,
        "sent": sent_count,
        "total": len(request.emails),
        "failed": failed,
        "message": f"Sent to {sent_count}/{len(request.emails)} recipients"
    }


@router.post("/responses")
async def submit_feedback_response(response: FeedbackResponse):
    """Submit anonymous feedback response"""
    
    # Validate token
    if response.token not in response_tokens:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
    
    token_data = response_tokens[response.token]
    
    if token_data["responded"]:
        raise HTTPException(
            status_code=400,
            detail="This token has already been used"
        )
    
    # Get the request
    request_id = token_data["request_id"]
    if request_id not in feedback_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Store response
    feedback_requests[request_id]["responses"].append({
        "content": response.content,
        "rating": response.rating,
        "submitted_at": datetime.utcnow().isoformat()
    })
    
    # Mark token as used
    response_tokens[response.token]["responded"] = True
    
    return {
        "message": "Feedback submitted successfully",
        "thank_you": True
    }


@router.get("/requests/{request_id}")
async def get_feedback_request(request_id: str):
    """Get feedback request and responses"""
    
    if request_id not in feedback_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return feedback_requests[request_id]
