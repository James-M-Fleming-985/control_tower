## Deploying Feedback360 to Production

### Backend Deployment (Railway)

Since you have Railway CLI installed, we can deploy via GitHub integration which is easier:

1. **Go to Railway Dashboard**: https://railway.app/new
2. **Select "Deploy from GitHub repo"**
3. **Authorize GitHub** and select `control_tower` repository
4. **Configure deployment**:
   - Root Directory: `feedback-collector-mvp/backend`
   - Railway will auto-detect it's a Python app
5. **Generate Domain**: Railway will provide a URL like `your-app.railway.app`

### Setting Environment Variables in Railway

After creating the project, add these variables in Railway dashboard:

```
STRIPE_SECRET_KEY=sk_test_... (use test keys first, then switch to live)
PRICE_ID_PRO=price_... (your Pro tier price ID)
STRIPE_WEBHOOK_SECRET=whsec_... (from Stripe webhook endpoint)
STRIPE_SUCCESS_URL=https://your-frontend.vercel.app/success
STRIPE_CANCEL_URL=https://your-frontend.vercel.app/pricing
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend Deployment (Vercel - Recommended)

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy frontend**:
```bash
cd feedback-collector-mvp/frontend
vercel --prod
```

3. **Set environment variable** (when prompted or in Vercel dashboard):
```
VITE_API_URL=https://your-backend.railway.app
```

### Alternative: Use GitHub Integration for Both

**Railway** (Backend):
- Go to railway.app → New Project → Deploy from GitHub
- Select repo, set root to `feedback-collector-mvp/backend`

**Vercel** (Frontend):
- Go to vercel.com/new → Import Git Repository
- Select repo, set root to `feedback-collector-mvp/frontend`
- Framework: Vite
- Build: `npm run build`
- Output: `dist`

Let me know when you're ready and I'll guide you through the next steps!
