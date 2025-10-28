"""
Stripe Service for Feedback360
Business logic for handling Stripe payments and subscriptions
"""
import stripe
import os
from typing import Dict, Any, Optional


class StripeService:
    """Service for handling Stripe payment operations"""
    
    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        if not self.api_key or self.api_key.startswith("sk_test_51QGjZdGt9vZpMqGgabcdef"):
            print("⚠️  WARNING: Using placeholder Stripe API key. Please set STRIPE_SECRET_KEY in .env")
            print("   Get your keys from: https://dashboard.stripe.com/test/apikeys")
        stripe.api_key = self.api_key
    
    def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None
    ) -> stripe.checkout.Session:
        """Create a Stripe Checkout session for £9.99/month subscription"""
        session_params = {
            "mode": "subscription",
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "allow_promotion_codes": True,
            "billing_address_collection": "auto",
        }
        
        if customer_email:
            session_params["customer_email"] = customer_email
        
        return stripe.checkout.Session.create(**session_params)
    
    def create_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> stripe.billing_portal.Session:
        """Create a Customer Portal session for managing subscriptions"""
        return stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
    
    async def handle_checkout_completed(self, session: Dict[str, Any]) -> None:
        """Handle successful checkout - user subscribed to Pro (£9.99/month)"""
        customer_id = session.get("customer")
        customer_email = session.get("customer_email") or \
                        session.get("customer_details", {}).get("email")
        subscription_id = session.get("subscription")
        
        print(f"✅ New Pro subscription: {customer_email}")
        print(f"   Customer ID: {customer_id}")
        print(f"   Subscription ID: {subscription_id}")
        
        # Track analytics event
        self._track_analytics('subscription_completed', {
            'customer_id': customer_id,
            'customer_email': customer_email,
            'subscription_id': subscription_id,
            'plan': 'pro',
            'amount': 9.99,
            'currency': 'GBP'
        })
        
        # TODO: Update your database
        # TODO: Send welcome email
    
    async def handle_subscription_updated(
        self, subscription: Dict[str, Any]
    ) -> None:
        """Handle subscription update (renewal, etc.)"""
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        status = subscription.get("status")
        
        print(f"🔄 Subscription updated: {subscription_id}")
        print(f"   Customer: {customer_id}")
        print(f"   Status: {status}")
        
        # TODO: Update database
    
    async def handle_subscription_deleted(
        self, subscription: Dict[str, Any]
    ) -> None:
        """Handle subscription cancellation"""
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        
        print(f"❌ Subscription cancelled: {subscription_id}")
        print(f"   Customer: {customer_id}")
        
        # Track analytics event
        self._track_analytics('subscription_cancelled', {
            'customer_id': customer_id,
            'subscription_id': subscription_id
        })
        
        # TODO: Update database
        # TODO: Send cancellation email
    
    async def handle_payment_failed(self, invoice: Dict[str, Any]) -> None:
        """Handle failed payment"""
        customer_id = invoice.get("customer")
        
        print(f"⚠️ Payment failed for customer: {customer_id}")
        
        # TODO: Send payment failed email
    
    async def get_subscription_status(
        self, customer_id: str
    ) -> Dict[str, Any]:
        """Get current subscription status for a customer"""
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="all",
                limit=1
            )
            
            if not subscriptions.data:
                return {"status": "none"}
            
            sub = subscriptions.data[0]
            
            return {
                "status": sub.status,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end,
                "plan": (sub.items.data[0].price.id
                        if sub.items.data else None)
            }
        except Exception as e:
            print(f"Error fetching subscription: {e}")
            return {"status": "error", "message": str(e)}
    
    def _track_analytics(self, event: str, properties: Dict[str, Any]) -> None:
        """
        Track analytics events to external services
        TODO: Implement actual integrations with Mixpanel, GA4, Amplitude
        """
        print(f"📊 Analytics Event: {event}")
        print(f"   Properties: {properties}")
        
        # TODO: Send to Mixpanel
        # mixpanel.track(properties.get('customer_email'), event, properties)
        
        # TODO: Send to Google Analytics 4
        # ga4_client.track(event, properties)
        
        # TODO: Send to Amplitude
        # amplitude.track(event, properties)
