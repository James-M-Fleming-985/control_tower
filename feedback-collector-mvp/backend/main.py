from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv
from app.routers.stripe_router import router as stripe_router
from app.routers.feedback_router import router as feedback_router
from app.routers.usage_router import router as usage_router
from app.routers.goals_router import router as goals_router

# Load environment variables
load_dotenv()

app = FastAPI(title="Anonymous Feedback Collector API")

# CORS configuration - allow frontend domains
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    # Railway frontend
    "https://feedback360-frontend-production.up.railway.app",
    "https://frontend-b24kitgwi-james-flemings-projects.vercel.app",
    "https://*.vercel.app",  # Allow Vercel preview deployments
    os.getenv("FRONTEND_URL", ""),  # Additional frontend URL from env
]
# Filter out empty strings
allowed_origins = [origin for origin in allowed_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe routes (checkout, webhook, portal)
app.include_router(stripe_router, prefix="/api/stripe")

# Feedback routes (requests, responses)
app.include_router(feedback_router, prefix="/api/feedback")

# Usage tracking routes
app.include_router(usage_router, prefix="/api/usage")

# Goals routes
app.include_router(goals_router, prefix="/api/goals")


@app.get("/")
async def root():
    return {
        "message": "Feedback360 - Anonymous Feedback Collector API",
        "version": "2.0.1",
        "status": "running",
        "deployed_at": "2025-10-30T11:10:00Z",
        "endpoints": {
            "/api/feedback/requests": "POST - Create feedback request",
            "/api/feedback/responses": "POST - Submit feedback response",
            "/api/stripe/*": "Stripe payment endpoints",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
