# Stripe Integration Setup Guide

This guide walks you through setting up Stripe subscriptions for Feedback360.

## 1. Get Stripe API Keys

1. Sign up at [Stripe Dashboard](https://dashboard.stripe.com/register)
2. For testing, use Test Mode (toggle in top right)
3. Navigate to **Developers → API Keys**
4. Copy your **Secret key** (starts with `sk_test_` for test mode)

## 2. Create Your Product and Price

1. Go to **Products** in the Stripe Dashboard
2. Click **Add Product**
3. Enter:
   - **Name**: `Feedback360 Pro`
   - **Description**: `Professional tier with unlimited feedback requests`
   - **Pricing Model**: Recurring
   - **Price**: `9.99 GBP`
   - **Billing Period**: Monthly
4. Save and copy the **Price ID** (starts with `price_`)

## 3. Set Up Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and set:
```bash
STRIPE_SECRET_KEY=sk_test_xxxxx  # From step 1
PRICE_ID_PRO=price_xxxxx         # From step 2
STRIPE_SUCCESS_URL=http://localhost:3000/success
STRIPE_CANCEL_URL=http://localhost:3000/pricing
```

## 4. Test Webhooks Locally

Install the [Stripe CLI](https://stripe.com/docs/stripe-cli):
```bash
# Linux/Mac
curl -sL https://github.com/stripe/stripe-cli/releases/download/v1.19.5/stripe_1.19.5_linux_x86_64.tar.gz | tar -xz

# Or use Homebrew
brew install stripe/stripe-cli/stripe
```

Login:
```bash
stripe login
```

Forward webhooks to your local server:
```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

This will output a webhook signing secret like `whsec_xxxxx`. Add it to your `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

## 5. Start the Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Test the Integration

### Test Creating a Checkout Session
```bash
curl -X POST http://localhost:8000/api/stripe/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_xxxxx", "customer_email": "test@example.com"}'
```

You should get back a `checkout_url`. Open it in a browser.

### Test with Stripe Test Cards
Use these test card numbers:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`

Any future expiry date and any 3-digit CVC will work.

### Monitor Webhooks
In your Stripe CLI terminal, you'll see webhook events as they arrive:
```
2025-10-25 12:34:56   --> checkout.session.completed
```

## 7. Production Deployment

### Set Up Production Webhook

1. Deploy your backend to production (Railway, Heroku, AWS, etc.)
2. In Stripe Dashboard, go to **Developers → Webhooks**
3. Click **Add endpoint**
4. Enter your production URL: `https://your-api.com/api/stripe/webhook`
5. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
6. Copy the **Signing secret** (starts with `whsec_`)
7. Add it to your production environment variables as `STRIPE_WEBHOOK_SECRET`

### Switch to Live Mode

1. Toggle to **Live Mode** in Stripe Dashboard
2. Get your **Live Secret Key** from API Keys (starts with `sk_live_`)
3. Get your **Live Price ID** from your product (create product in Live Mode)
4. Update production environment variables:
   ```bash
   STRIPE_SECRET_KEY=sk_live_xxxxx
   PRICE_ID_PRO=price_xxxxx  # Live mode price
   STRIPE_WEBHOOK_SECRET=whsec_xxxxx  # From webhook endpoint
   STRIPE_SUCCESS_URL=https://feedback360.com/success
   STRIPE_CANCEL_URL=https://feedback360.com/pricing
   ```

## 8. Database Setup (Production)

The current implementation uses in-memory storage. Before production:

1. Set up PostgreSQL database
2. Create tables for users and subscriptions:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_price_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

3. Update `stripe_service.py` to save subscription data to DB instead of in-memory dict

## 9. Analytics Integration

The webhook handler in `stripe_service.py` has TODO comments for analytics. Add:

```python
# In handle_checkout_completed:
analytics.track('subscription_completed', {
    'user_email': customer_email,
    'plan': 'pro',
    'amount': 9.99,
    'currency': 'GBP'
})

# In handle_subscription_updated:
analytics.track('subscription_updated', {
    'subscription_id': subscription_id,
    'status': status
})
```

Integrate with:
- [Mixpanel](https://mixpanel.com/docs)
- [Google Analytics 4](https://developers.google.com/analytics/devguides/collection/ga4)
- [Amplitude](https://www.docs.developers.amplitude.com/)

## Troubleshooting

### Webhook signature verification fails
- Ensure `STRIPE_WEBHOOK_SECRET` matches the secret from your webhook endpoint
- Check that the raw request body is passed to `stripe.Webhook.construct_event()`
- Verify you're using the correct secret (test vs live mode)

### Checkout session creation fails
- Check `STRIPE_SECRET_KEY` is set correctly
- Verify `PRICE_ID_PRO` exists in your Stripe account
- Ensure you're in the correct mode (test vs live)

### Customer portal doesn't work
- Customer must have an active subscription
- Ensure `STRIPE_CUSTOMER_ID` is saved when subscription is created
- Check return URL is set correctly

## Resources

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Customer Portal](https://stripe.com/docs/billing/subscriptions/integrating-customer-portal)
- [Stripe Test Cards](https://stripe.com/docs/testing)
