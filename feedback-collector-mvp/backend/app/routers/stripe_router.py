from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import Dict, Any, List

from ..stripe_service import StripeService
from ..config.subscription_tiers import (
    SubscriptionTier, 
    get_tier_pricing, 
    get_tier_features_list,
    get_tier_limits,
    TIER_FEATURES
)

router = APIRouter()
stripe_service = StripeService()

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    try:
        data = await request.json()
        email = data.get("customer_email")
        tier = data.get("tier", "pro")  # Default to pro
        
        # Convert string tier to enum
        try:
            tier_enum = SubscriptionTier(tier.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid tier: {tier}. Must be one of: free, pro, premium, enterprise"
            )
        
        # Free tier doesn't need Stripe checkout
        if tier_enum == SubscriptionTier.FREE:
            raise HTTPException(
                status_code=400,
                detail="Free tier doesn't require payment"
            )
        
        # Get pricing configuration
        pricing = get_tier_pricing(tier_enum)
        price_id_env = pricing.get("stripe_price_id_env")
        
        if not price_id_env:
            raise HTTPException(
                status_code=400,
                detail=f"No Stripe configuration for tier: {tier}"
            )
        
        price_id = os.getenv(price_id_env)

        if not price_id or price_id.startswith("price_placeholder"):
            # For development, create a test message instead of failing
            if os.getenv("RAILWAY_ENVIRONMENT") == "production":
                msg = f"Price ID not configured for tier: {tier}"
                raise HTTPException(status_code=400, detail=msg)
            else:
                # For local development, return a placeholder response
                return {
                    "checkout_url": "https://stripe.com/test",
                    "session_id": "test_session",
                    "message": "Stripe not configured - test response"
                }

        session = stripe_service.create_checkout_session(
            price_id=price_id,
            success_url=os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/success") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("STRIPE_CANCEL_URL", "http://localhost:3000"),
            customer_email=email,
            metadata={"tier": tier_enum.value}
        )
        
        # Return the format expected by frontend
        return {"checkout_url": session.url, "session_id": session.id}
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

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


@router.get("/tiers")
async def get_subscription_tiers():
    """
    Get all available subscription tiers with pricing and features
    """
    tiers_info = []
    
    for tier in SubscriptionTier:
        pricing = get_tier_pricing(tier)
        features = get_tier_features_list(tier)
        limits = get_tier_limits(tier)
        tier_data = TIER_FEATURES[tier]
        
        tiers_info.append({
            "tier": tier.value,
            "name": tier_data["name"],
            "tagline": tier_data["tagline"],
            "price": pricing["price"],
            "currency": pricing["currency"],
            "interval": pricing["interval"],
            "features": features,
            "limits": limits,
            "is_popular": tier == SubscriptionTier.PRO,
            "is_free": tier == SubscriptionTier.FREE
        })
    
    return {"tiers": tiers_info}
