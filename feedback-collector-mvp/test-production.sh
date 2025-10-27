#!/bin/bash
# Production Deployment Test Suite for Feedback360

echo "╔══════════════════════════════════════════════════════╗"
echo "║  Feedback360 Production Deployment Test Suite       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

BACKEND_URL="https://energetic-purpose-production.up.railway.app"
FRONTEND_URL="https://frontend-b24kitgwi-james-flemings-projects.vercel.app"

# Test 1: Backend Health
echo "📡 Test 1: Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend API docs accessible (HTTP $BACKEND_STATUS)"
else
    echo "❌ Backend API docs not accessible (HTTP $BACKEND_STATUS)"
fi
echo ""

# Test 2: Frontend Health
echo "🌐 Test 2: Frontend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend accessible (HTTP $FRONTEND_STATUS)"
    FRONTEND_CONTENT=$(curl -s "$FRONTEND_URL" | grep -o "Feedback360" | head -1)
    if [ -n "$FRONTEND_CONTENT" ]; then
        echo "✅ Frontend contains expected content"
    else
        echo "⚠️  Frontend loaded but content check failed"
    fi
else
    echo "❌ Frontend not accessible (HTTP $FRONTEND_STATUS)"
fi
echo ""

# Test 3: CORS Configuration
echo "🔐 Test 3: CORS Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CORS_HEADER=$(curl -s -H "Origin: $FRONTEND_URL" -I "$BACKEND_URL/docs" 2>&1 | grep -i "access-control-allow-origin" || echo "")
if [ -n "$CORS_HEADER" ]; then
    echo "✅ CORS headers present"
    echo "   $CORS_HEADER"
else
    echo "⚠️  CORS headers not found (may need manual verification)"
fi
echo ""

# Test 4: API Endpoints
echo "🔌 Test 4: API Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test feedback endpoint
FEEDBACK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND_URL/feedback" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test feedback", "category": "general"}')
if [ "$FEEDBACK_STATUS" = "200" ] || [ "$FEEDBACK_STATUS" = "201" ]; then
    echo "✅ Feedback API endpoint working (HTTP $FEEDBACK_STATUS)"
else
    echo "⚠️  Feedback API endpoint status: HTTP $FEEDBACK_STATUS"
fi

# Test Stripe checkout endpoint (should fail without valid Stripe key)
STRIPE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND_URL/api/stripe/create-checkout-session" \
  -H "Content-Type: application/json" \
  -d '{"customer_email": "test@example.com"}')
echo "ℹ️  Stripe checkout endpoint status: HTTP $STRIPE_STATUS"
if [ "$STRIPE_STATUS" = "500" ]; then
    echo "   (Expected - placeholder Stripe keys in use)"
fi
echo ""

# Test 5: Performance
echo "⚡ Test 5: Performance Metrics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
BACKEND_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$BACKEND_URL/docs")
FRONTEND_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$FRONTEND_URL")
echo "⏱️  Backend response time: ${BACKEND_TIME}s"
echo "⏱️  Frontend response time: ${FRONTEND_TIME}s"
echo ""

# Test 6: Environment Variables Check
echo "⚙️  Test 6: Configuration Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ℹ️  Backend URL: $BACKEND_URL"
echo "ℹ️  Frontend URL: $FRONTEND_URL"
echo "⚠️  Stripe keys: Using placeholder values (need real keys)"
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Test Summary                                        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "🔗 Links:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend API Docs: $BACKEND_URL/docs"
echo "   Railway Dashboard: https://railway.app/project/491ff138-e5a2-429c-a0fd-969d8c76ff14"
echo ""
echo "📋 Next Steps:"
echo "   1. Open frontend in browser and test user flows"
echo "   2. Add real Stripe API keys in Railway dashboard"
echo "   3. Set up Stripe webhook endpoint"
echo "   4. Test Stripe checkout flow with test card"
echo "   5. Monitor Railway logs for any errors"
echo ""
