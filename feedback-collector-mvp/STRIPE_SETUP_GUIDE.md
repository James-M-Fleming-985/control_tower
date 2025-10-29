# Stripe Setup Guide for Feedback360

## 🎯 Quick Setup Steps

### 1. Create Stripe Account (if needed)
- Go to: https://dashboard.stripe.com
- Sign up or log in
- Activate your account

### 2. Get Your API Keys
1. Go to: https://dashboard.stripe.com/test/apikeys
2. Copy your **Test Secret Key** (starts with `sk_test_`)
3. Copy your **Test Publishable Key** (starts with `pk_test_`)

### 3. Update Local Environment
```bash
cd /workspaces/control_tower/feedback-collector-mvp/backend
```

Edit `.env` file and replace:
```
STRIPE_SECRET_KEY=your_actual_secret_key_here
```

### 4. Run Setup Script
```bash
python setup_stripe.py
```

This will create:
- **Growth Plan**: £4.99/month (limited free-text responses)
- **Pro Plan**: £9.99/month (unlimited free-text responses)

### 5. Set Up Webhooks
1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. URL: `https://energetic-purpose-production.up.railway.app/api/stripe/webhook`
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Copy the webhook secret (starts with `whsec_`)

### 6. Update Railway Environment
```bash
railway variables --set "STRIPE_SECRET_KEY=sk_test_your_key"
railway variables --set "STRIPE_WEBHOOK_SECRET=whsec_your_secret"
railway variables --set "PRICE_ID_GROWTH=price_your_growth_id"
railway variables --set "PRICE_ID_PRO=price_your_pro_id"
```

## 🧪 Testing

Test checkout locally:
```bash
curl -X POST "http://localhost:8000/api/stripe/create-checkout-session" \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro", "customer_email": "test@example.com"}'
```

Test on production:
```bash
curl -X POST "https://energetic-purpose-production.up.railway.app/api/stripe/create-checkout-session" \
  -H "Content-Type: application/json" \
  -d '{"tier": "growth", "customer_email": "test@example.com"}'
```

## 📋 Current Status

- ✅ Frontend: 3-tier pricing deployed
- ✅ Backend: Stripe routing ready
- ⚠️ Stripe Keys: Need real keys (currently placeholders)
- ⚠️ Products: Need to run setup_stripe.py

## 🔗 Useful Links

- [Stripe Dashboard](https://dashboard.stripe.com)
- [Test API Keys](https://dashboard.stripe.com/test/apikeys)
- [Webhooks](https://dashboard.stripe.com/test/webhooks)
- [Test Cards](https://stripe.com/docs/testing#cards)