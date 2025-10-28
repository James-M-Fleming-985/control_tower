# 🚂 Railway Deployment Guide - Feedback360

## ✅ Updates Complete

### 🎨 Favicon Updates
- ✅ Created matching favicon design based on report generator
- ✅ Added 360° branding with blue gradient (matching Feedback360 theme)
- ✅ Created SVG, PNG, and ICO versions
- ✅ Updated HTML with proper favicon links

### 🔧 Production Configuration
- ✅ Created Railway.toml configurations for both frontend and backend
- ✅ Added API configuration with environment variables
- ✅ Updated frontend to use dynamic API URLs
- ✅ Gmail SMTP credentials configured for production

## 🚂 Railway Deployment Steps

### Prerequisites
1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Connection**: Connect your GitHub account to Railway
3. **Repository Access**: Ensure Railway has access to `control_tower` repo

### Step 1: Deploy Backend Service

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose Repository**: `James-M-Fleming-985/control_tower`
5. **Configure Service**:
   - **Service Name**: `feedback360-backend`
   - **Root Directory**: `feedback-collector-mvp/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. **Set Environment Variables**:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_USER=flemingjames298@gmail.com
   SMTP_PASSWORD=bcii exkf cftf stqi
   FROM_EMAIL=flemingjames298@gmail.com
   FROM_NAME=Feedback360
   STRIPE_SECRET_KEY=sk_test_51QGjZdGt9vZpMqGgabcdef1234567890
   PRICE_ID_PRO=price_1QGjZdGt9vZpMqGgabcdef
   STRIPE_WEBHOOK_SECRET=whsec_abcdef1234567890
   ```

7. **Deploy**: Click "Deploy"

### Step 2: Deploy Frontend Service

1. **Add New Service** to the same project
2. **Configure Service**:
   - **Service Name**: `feedback360-frontend`
   - **Root Directory**: `feedback-collector-mvp/frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   ```
   VITE_API_URL=https://[backend-service-url].railway.app
   NODE_ENV=production
   ```
   
   *Replace `[backend-service-url]` with your actual backend Railway URL*

4. **Deploy**: Click "Deploy"

### Step 3: Update Cross-References

After both services are deployed:

1. **Get Backend URL**: Copy the Railway URL for your backend service
2. **Update Frontend Environment**:
   - Go to frontend service settings
   - Update `VITE_API_URL` with the actual backend URL
   - Redeploy frontend

3. **Update Backend CORS**:
   - Add frontend URL to allowed origins in backend code if needed
   - Update `FRONTEND_URL` in backend environment variables

## 🔗 Expected URLs

After deployment, you'll have:
- **Backend API**: `https://feedback360-backend-xxx.railway.app`
- **Frontend App**: `https://feedback360-frontend-xxx.railway.app`

## ✅ Testing Checklist

After deployment:
- [ ] Frontend loads correctly
- [ ] Favicon appears in browser tab
- [ ] Can submit feedback request form
- [ ] Emails are sent successfully
- [ ] Email links work and lead back to frontend
- [ ] Stripe payments work (if using)

## 🔧 Local Testing Before Deploy

Test the production build locally:

```bash
# Backend
cd /workspaces/control_tower/feedback-collector-mvp/backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd /workspaces/control_tower/feedback-collector-mvp/frontend
npm run build
npm run preview
```

## 🚨 Important Notes

1. **Gmail App Password**: Already configured in Railway environment
2. **Stripe Keys**: Using test keys - update for production
3. **Domain**: Railway provides `.railway.app` subdomain
4. **SSL**: Railway automatically provides HTTPS
5. **Environment Variables**: Never commit sensitive data to Git

## 🎯 Next Steps

After successful deployment:
1. Test the complete email flow
2. Update any hardcoded URLs to use Railway URLs
3. Consider custom domain setup
4. Set up monitoring and logging
5. Update Stripe webhook URLs if needed

---

**Ready to deploy! 🚀**