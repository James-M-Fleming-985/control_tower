from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
import secrets
from datetime import datetime

from ..database import get_db
from ..models import (
    User, FeedbackRequest as DBFeedbackRequest,
    FeedbackRecipient, FeedbackResponse as DBFeedbackResponse,
    FeedbackContext, FeedbackMode
)
from ..services.usage_tracking_service import UsageTrackingService
from ..services import gamification_service
from ..email_service import email_service

router = APIRouter()


class FeedbackRequestCreate(BaseModel):
    user_id: Optional[int] = 1  # Default to user 1 for MVP
    recipient_emails: List[EmailStr]
    context: str = "professional"
    mode: str = "freetext"
    title: str = "Feedback Request"
    custom_message: str = ""
    prompts: Optional[List[str]] = None


class FeedbackResponseSubmit(BaseModel):
    token: str
    content: str
    rating: Optional[int] = None


@router.post("/requests")
async def create_feedback_request(
    request: FeedbackRequestCreate,
    db: Session = Depends(get_db)
):
    """Create a new feedback request and send emails to recipients"""

    # Get or create default user for MVP
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        # Create default user for MVP
        user = User(
            email="demo@feedback360.com",
            name="Demo User",
            subscription_tier="FREE"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Validate inputs
    if not request.recipient_emails:
        raise HTTPException(
            status_code=400,
            detail="At least one email required"
        )

    # Convert string context/mode to enums
    try:
        context_enum = FeedbackContext(request.context.lower())
        mode_enum = FeedbackMode(request.mode.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check usage limits
    usage_service = UsageTrackingService(db)
    can_create = usage_service.can_create_request(
        user,
        mode_enum,
        len(request.recipient_emails)
    )

    if not can_create["allowed"]:
        return {
            "success": False,
            "error": can_create["reason"],
            "upgrade_info": can_create.get("upgrade_info")
        }

    # Create feedback request in database
    db_request = DBFeedbackRequest(
        user_id=user.id,
        title=request.title,
        context=context_enum,
        mode=mode_enum,
        prompts=request.prompts or []
    )
    db.add(db_request)
    db.flush()  # Get ID without committing

    # Create recipients and send emails
    sent_count = 0
    failed = []

    for recipient_email in request.recipient_emails:
        # Generate unique response token
        token = secrets.token_urlsafe(32)

        # Create recipient record
        recipient = FeedbackRecipient(
            request_id=db_request.id,
            email=recipient_email,
            token=token
        )
        db.add(recipient)

        # Send email
        success = await email_service.send_feedback_request(
            recipient_email=recipient_email,
            request_id=str(db_request.id),
            token=token,
            context=request.context,
            custom_message=request.custom_message
        )

        if success:
            sent_count += 1
        else:
            failed.append(recipient_email)

    # Increment usage counter
    usage_service.increment_usage(user, mode_enum)

    # Award points for creating request
    gamification_service.award_points(
        db=db,
        user_id=user.id,
        points=10,
        activity_type="feedback_request_created",
        metadata={
            "request_id": db_request.id,
            "context": request.context,
            "mode": request.mode
        }
    )

    db.commit()

    return {
        "success": True,
        "request_id": db_request.id,
        "sent": sent_count,
        "total": len(request.recipient_emails),
        "failed": failed,
        "message": f"Sent to {sent_count}/{len(request.recipient_emails)}"
        f" recipients"
    }


@router.post("/responses")
async def submit_feedback_response(
    response: FeedbackResponseSubmit,
    db: Session = Depends(get_db)
):
    """Submit anonymous feedback response"""

    # Validate token and get recipient
    recipient = db.query(FeedbackRecipient).filter(
        FeedbackRecipient.token == response.token
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Invalid or expired token"
        )

    if recipient.responded_at:
        raise HTTPException(
            status_code=400,
            detail="This token has already been used"
        )

    # Get the feedback request
    db_request = db.query(DBFeedbackRequest).filter(
        DBFeedbackRequest.id == recipient.request_id
    ).first()

    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Create feedback response
    db_response = DBFeedbackResponse(
        request_id=db_request.id,
        recipient_id=recipient.id,
        content=response.content
    )
    db.add(db_response)

    # Mark recipient as responded
    recipient.responded_at = datetime.utcnow()

    # Award points to the requester for receiving feedback
    user = db.query(User).filter(User.id == db_request.user_id).first()
    gamification_service.award_points(
        db=db,
        user_id=user.id,
        points=25,
        activity_type="feedback_received",
        metadata={"request_id": db_request.id}
    )

    db.commit()

    return {
        "success": True,
        "message": "Feedback submitted successfully",
        "thank_you": True
    }


@router.get("/requests/{request_id}")
async def get_feedback_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Get feedback request and responses"""

    db_request = db.query(DBFeedbackRequest).filter(
        DBFeedbackRequest.id == request_id
    ).first()

    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Get all recipients and responses
    recipients = db.query(FeedbackRecipient).filter(
        FeedbackRecipient.request_id == request_id
    ).all()

    responses = db.query(DBFeedbackResponse).filter(
        DBFeedbackResponse.request_id == request_id
    ).all()

    return {
        "id": db_request.id,
        "title": db_request.title,
        "context": db_request.context.value,
        "mode": db_request.mode.value,
        "created_at": db_request.created_at.isoformat(),
        "recipient_count": len(recipients),
        "response_count": len(responses),
        "responses": [
            {
                "content": r.content,
                "sentiment_score": r.sentiment_score,
                "submitted_at": r.created_at.isoformat()
            }
            for r in responses
        ]
    }

