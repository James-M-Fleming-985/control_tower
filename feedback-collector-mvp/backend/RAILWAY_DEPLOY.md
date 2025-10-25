# Feedback360 Backend Deployment

## Quick Deploy to Railway

1. **Install Railway CLI** (if not already installed):
```bash
npm i -g @railway/cli
railway login
```

2. **Initialize Railway project**:
```bash
cd feedback-collector-mvp/backend
railway init
```

3. **Set environment variables** in Railway dashboard:
```bash
railway variables set STRIPE_SECRET_KEY=sk_live_your_key
railway variables set PRICE_ID_PRO=price_your_price_id
railway variables set STRIPE_WEBHOOK_SECRET=whsec_your_secret
railway variables set STRIPE_SUCCESS_URL=https://your-frontend.vercel.app/success
railway variables set STRIPE_CANCEL_URL=https://your-frontend.vercel.app/pricing
railway variables set FRONTEND_URL=https://your-frontend.vercel.app
```

4. **Deploy**:
```bash
railway up
```

5. **Get your backend URL**:
```bash
railway domain
```

## GitHub Integration (Alternative)

1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose `control_tower` repository
4. Set root directory to: `feedback-collector-mvp/backend`
5. Railway will auto-detect Python and use `railway.json` config
6. Add environment variables in Railway dashboard
7. Deploy!

## Environment Variables Required

- `STRIPE_SECRET_KEY` - Your Stripe secret key (live mode)
- `PRICE_ID_PRO` - Stripe price ID for £9.99/month Pro tier
- `STRIPE_WEBHOOK_SECRET` - Webhook signing secret from Stripe
- `STRIPE_SUCCESS_URL` - Frontend URL for successful checkout
- `STRIPE_CANCEL_URL` - Frontend URL for cancelled checkout
- `FRONTEND_URL` - Your frontend domain for CORS

## After Deployment

1. Copy your Railway backend URL
2. In Stripe Dashboard:
   - Go to Developers → Webhooks
   - Add endpoint: `https://your-backend.railway.app/api/stripe/webhook`
   - Select events: `checkout.session.completed`, `customer.subscription.*`
   - Copy webhook signing secret and update `STRIPE_WEBHOOK_SECRET`
3. Update frontend to use production backend URL
