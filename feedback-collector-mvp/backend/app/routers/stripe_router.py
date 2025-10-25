from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import Dict, Any

from ..stripe_service import StripeService

router = APIRouter()
stripe_service = StripeService()

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    email = data.get("customer_email")

    try:
        session = stripe_service.create_checkout_session(
            price_id=os.getenv("PRICE_ID_PRO"),
            success_url=os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/success") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("STRIPE_CANCEL_URL", "http://localhost:3000/pricing"),
            customer_email=email
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-portal-session")
async def create_portal_session(request: Request):
    data = await request.json()
    customer_id = data.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id required")
    try:
        session = stripe_service.create_portal_session(customer_id=customer_id, return_url=os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000"))
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    import stripe
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    event_data = event["data"]["object"]

    # Simple handling - delegate to stripe_service
    if event_type == "checkout.session.completed":
        await stripe_service.handle_checkout_completed(event_data)
    elif event_type == "customer.subscription.updated":
        await stripe_service.handle_subscription_updated(event_data)
    elif event_type == "customer.subscription.deleted":
        await stripe_service.handle_subscription_deleted(event_data)
    elif event_type == "invoice.payment_failed":
        await stripe_service.handle_payment_failed(event_data)

    return JSONResponse(content={"received": True})

@router.get("/subscription-status/{customer_id}")
async def subscription_status(customer_id: str):
    result = await stripe_service.get_subscription_status(customer_id)
    return result
