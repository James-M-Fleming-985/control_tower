# Causal Affect Project Integration Plan

**Date:** October 13, 2025  
**Goal:** Work on business-ventures/causal-affect project through control_tower repo  
**Strategy:** Use PROJECT-004 AI Code Generator to build web application features

---

## Why This Is The Perfect Test Case

### 1. **Real Web Application** 🌐
- Actual UI/UX to validate quality
- Visual feedback on generated code
- User-facing features (high quality bar)
- Integration testing opportunities

### 2. **External Repository** 📦
- Tests cross-repo workflow
- Validates portability of build system
- Real-world development scenario
- Proves control_tower is reusable

### 3. **Business Value** 💰
- Actual product development
- Not just infrastructure/tools
- Measurable progress toward launch
- ROI on automation investment

---

## Architecture Options

### Option A: Clone Causal Affect into Control Tower

```
/workspaces/control_tower/
├── projects/
│   ├── PROJECT-003 TDD ENFORCER/
│   ├── PROJECT-004 AI CODE GENERATOR/
│   └── PROJECT-005 CAUSAL AFFECT/        ← NEW
│       ├── SYSTEM-005-01 Frontend/
│       ├── SYSTEM-005-02 Backend/
│       └── SYSTEM-005-03 Database/
├── build_feature.py
└── run_layer_generation.py
```

**Pros:**
- Single workspace
- Easy access to build tools
- Unified Git workflow
- Consistent structure

**Cons:**
- Mixes business logic with tooling
- Large repo size
- Harder to deploy separately
- Different deployment workflows

---

### Option B: Keep Separate, Link via Symlink

```
/workspaces/
├── control_tower/              (automation tools)
│   ├── build_feature.py
│   └── projects/
│
└── business-ventures/          (business code)
    └── causal-affect/
        ├── features/ → /workspaces/control_tower/build_feature.py
        └── src/
```

**Pros:**
- Clean separation
- Independent deployment
- Can work on causal-affect standalone
- Control tower remains pure tooling

**Cons:**
- Cross-repo complexity
- Path management issues
- Need symlinks or scripts
- Harder to track changes

---

### Option C: Control Tower as Submodule (RECOMMENDED) ✅

```
/workspaces/business-ventures/causal-affect/
├── .git/
├── src/
├── features/                    (YAML specs)
├── control_tower/               (Git submodule)
│   ├── build_feature.py
│   └── projects/PROJECT-004/
├── build.sh → control_tower/build_feature.py
└── package.json
```

**Pros:**
- ✅ Clean separation of concerns
- ✅ Causal Affect is main project
- ✅ Control tower is versioned dependency
- ✅ Easy to update control_tower
- ✅ Other projects can use same pattern
- ✅ Independent deployment

**Cons:**
- Slightly more complex Git workflow
- Need to commit submodule updates

---

## Recommended Approach: Option C (Submodule)

### Step-by-Step Setup

#### 1. Clone Business Ventures Repo

```bash
cd /workspaces
git clone https://github.com/YOUR_USERNAME/business-ventures.git
cd business-ventures/causal-affect
```

#### 2. Add Control Tower as Submodule

```bash
# Add control_tower as submodule
git submodule add https://github.com/James-M-Fleming-985/control_tower.git control_tower

# Initialize and update submodule
git submodule init
git submodule update
```

#### 3. Create Feature Specification Structure

```bash
# Create features directory for YAML specs
mkdir -p features/frontend
mkdir -p features/backend
mkdir -p features/database

# Create build wrapper script
cat > build_feature.sh << 'EOF'
#!/bin/bash
# Wrapper to use control_tower build system

FEATURE_YAML="$1"

if [ -z "$FEATURE_YAML" ]; then
    echo "Usage: ./build_feature.sh path/to/feature.yaml"
    exit 1
fi

# Run build_feature.py from control_tower submodule
python control_tower/build_feature.py "$FEATURE_YAML"
EOF

chmod +x build_feature.sh
```

#### 4. Create Your First Feature YAML

```bash
# Example: User Authentication Feature
cat > features/frontend/FEATURE-001_user_authentication.yaml << 'EOF'
feature_id: FEATURE-001
name: User Authentication
description: |
  User registration, login, and session management for Causal Affect platform.
  Supports email/password and social auth (Google, GitHub).

acceptance_criteria:
  - criterion_id: AC-001
    description: Users can register with email and password
    priority: CRITICAL
    
  - criterion_id: AC-002
    description: Users can login and receive JWT token
    priority: CRITICAL
    
  - criterion_id: AC-003
    description: Protected routes require valid authentication
    priority: CRITICAL

layers:
  - layer_id: LAYER-001-01
    name: Authentication Service
    requirement_file: LAYER-001-01_auth_service.yaml
    
  - layer_id: LAYER-001-02
    name: User Session Manager
    requirement_file: LAYER-001-02_session_manager.yaml
    
  - layer_id: LAYER-001-03
    name: Auth API Endpoints
    requirement_file: LAYER-001-03_auth_api.yaml

integration_scenarios:
  - name: End-to-End Registration
    description: User registers, receives verification email, confirms account
    layers: [LAYER-001-01, LAYER-001-02, LAYER-001-03]
    
e2e_scenarios:
  - name: Complete Auth Flow
    description: Register → Login → Access Protected Route → Logout
    flow: Registration → Email Verification → Login → Protected Access → Session Cleanup
EOF
```

---

## Causal Affect Project Structure (Proposed)

```
causal-affect/
├── .git/
├── control_tower/                  (Git submodule)
│   ├── build_feature.py
│   ├── projects/PROJECT-004/
│   └── README.md
│
├── features/                       (YAML specifications)
│   ├── frontend/
│   │   ├── FEATURE-001_user_authentication.yaml
│   │   ├── FEATURE-002_dashboard.yaml
│   │   └── FEATURE-003_data_visualization.yaml
│   │
│   ├── backend/
│   │   ├── FEATURE-001_api_gateway.yaml
│   │   ├── FEATURE-002_data_processing.yaml
│   │   └── FEATURE-003_analytics_engine.yaml
│   │
│   └── database/
│       ├── FEATURE-001_user_schema.yaml
│       └── FEATURE-002_event_schema.yaml
│
├── src/                           (Generated + manual code)
│   ├── frontend/
│   │   ├── FEATURE-001 User Authentication/
│   │   │   ├── LAYER-001-01 Auth Service/
│   │   │   │   ├── src/implementation.py
│   │   │   │   ├── tests/
│   │   │   │   └── Requirements Verification/
│   │   │   └── src/feature_integration.py
│   │   └── components/          (React/Vue components)
│   │
│   ├── backend/
│   │   ├── FEATURE-001 API Gateway/
│   │   └── api/                 (FastAPI/Flask routes)
│   │
│   └── database/
│       └── models/              (SQLAlchemy/Prisma models)
│
├── tests/                        (Integration/E2E tests)
│   ├── e2e/
│   └── integration/
│
├── build_feature.sh              (Wrapper script)
├── package.json                  (Frontend deps)
├── requirements.txt              (Backend deps)
├── docker-compose.yml            (Local dev environment)
└── README.md
```

---

## Web Application Specifics

### Frontend Framework Detection

The build system can adapt to your frontend framework:

**React Example:**
```yaml
# LAYER-001-01_react_auth_component.yaml
layer_id: LAYER-001-01
name: React Authentication Component
framework: react
language: typescript

requirements:
  - req_id: REQ-001
    description: Create reusable Login component with Formik validation
    acceptance_criteria:
      - Uses React hooks (useState, useEffect)
      - Integrates with auth context
      - Displays validation errors
      - Supports loading states
```

**Generated Output:**
```typescript
// src/components/Login/Login.tsx
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { LoginForm } from './LoginForm';

export const Login: React.FC = () => {
  const { login, isLoading, error } = useAuth();
  
  const handleSubmit = async (credentials: LoginCredentials) => {
    await login(credentials);
  };
  
  return (
    <div className="login-container">
      <LoginForm onSubmit={handleSubmit} isLoading={isLoading} />
      {error && <ErrorMessage message={error} />}
    </div>
  );
};
```

### Backend Framework Detection

**FastAPI Example:**
```yaml
# LAYER-001-02_fastapi_auth_routes.yaml
layer_id: LAYER-001-02
name: FastAPI Authentication Routes
framework: fastapi
language: python

requirements:
  - req_id: REQ-001
    description: Create /auth/login endpoint with JWT token generation
    acceptance_criteria:
      - Validates email/password
      - Returns JWT access token
      - Includes refresh token
      - Rate limiting enabled
```

**Generated Output:**
```python
# src/api/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..models import Token, User
from ..services import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])
auth_service = AuthService()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Authenticate user and return JWT tokens.
    
    REQ-001: Create /auth/login endpoint with JWT token generation
    """
    user = await auth_service.authenticate(
        email=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    return await auth_service.create_tokens(user)
```

---

## Visual Validation Strategy

### 1. **Component Preview** (Frontend)

```bash
# Generate component
./build_feature.sh features/frontend/FEATURE-001_user_auth.yaml

# Start dev server
npm run dev

# Open browser
open http://localhost:3000/auth/login
```

**Validation Checklist:**
- ✅ Component renders without errors
- ✅ Form validation works
- ✅ Loading states display correctly
- ✅ Error messages are user-friendly
- ✅ Styling matches design system

### 2. **API Testing** (Backend)

```bash
# Generate API routes
./build_feature.sh features/backend/FEATURE-001_api_gateway.yaml

# Start API server
python -m uvicorn main:app --reload

# Open Swagger docs
open http://localhost:8000/docs
```

**Validation Checklist:**
- ✅ Endpoints are documented
- ✅ Request/response schemas correct
- ✅ Authentication works
- ✅ Error handling proper
- ✅ Tests pass

### 3. **Integration Testing** (Full Stack)

```bash
# Start full stack
docker-compose up

# Run E2E tests
npm run test:e2e

# Manual testing
open http://localhost:3000
```

---

## Example: First Feature to Build

### Feature: Landing Page with Contact Form

**Why This First:**
- Simple, standalone feature
- Visual feedback immediate
- Tests full stack (frontend + backend)
- Low complexity, high confidence

**Components:**
1. **Frontend Layer 1:** React landing page component
2. **Frontend Layer 2:** Contact form with validation
3. **Backend Layer 1:** Contact form API endpoint
4. **Backend Layer 2:** Email service integration

**Time Estimate:** ~6 minutes (4 layers × 90 seconds)

**YAML Spec:**
```yaml
feature_id: FEATURE-LP-001
name: Landing Page with Contact Form
description: |
  Marketing landing page with hero section, features showcase,
  and working contact form that sends emails.

layers:
  - layer_id: LAYER-LP-001-01
    name: Landing Page Component
    requirement_file: landing_page_component.yaml
    
  - layer_id: LAYER-LP-001-02
    name: Contact Form Component
    requirement_file: contact_form_component.yaml
    
  - layer_id: LAYER-LP-001-03
    name: Contact API Endpoint
    requirement_file: contact_api_endpoint.yaml
    
  - layer_id: LAYER-LP-001-04
    name: Email Service
    requirement_file: email_service.yaml

integration_scenarios:
  - name: Contact Form Submission
    description: User fills form, submits, receives confirmation email
    layers: [LAYER-LP-001-02, LAYER-LP-001-03, LAYER-LP-001-04]
```

---

## Quality Metrics for Web App

### Automated Checks
- ✅ **Test Coverage:** ≥80% (enforced)
- ✅ **Type Safety:** TypeScript strict mode
- ✅ **Linting:** ESLint/Prettier passing
- ✅ **Bundle Size:** <500KB initial load
- ✅ **Performance:** Lighthouse score >90

### Manual Validation
- ✅ **Visual Consistency:** Matches design mockups
- ✅ **Responsive:** Works on mobile, tablet, desktop
- ✅ **Accessibility:** WCAG AA compliance
- ✅ **User Flow:** Intuitive navigation
- ✅ **Error Handling:** Graceful degradation

### Verification Artifacts (PROJECT-004 port — Track I)

The `Requirements Verification/` artifact bundle generated per build is **internal learning evidence**, not a user-facing approval gate. Specifically:

- The system MUST NOT require user approval of specs, ACs, or generated code before building.
- The system MUST display verification status as a **read-only badge** ("X/N verified") on each build card.
- The system MUST expose the artifact bundle via a **read-only "View Build Evidence" link** that opens the GitHub `Requirements Verification/` folder for that build.
- Failed verifications trigger an automatic REFACTOR loop (max 2 retries). If still failing, the build is BLOCKED from deployment, the build log row shows "—" instead of a URL, and the failure reason is persisted for telemetry/learning.
- Verification status is bound to telemetry (GA4 engagement + Stripe revenue, keyed by `build_id`) so the system can learn which spec/prompt patterns produce better outcomes.

This preserves the autonomous Discovery → Adapt → Exploit → Monitor → Learn → Optimize loop. See `Causal_Affect_Scaling_Plan.yaml#autonomous_loop` for canonical definitions.

---

## Next Steps

### Immediate (Today)
1. ✅ Clone business-ventures repo
2. ✅ Add control_tower as submodule
3. ✅ Create features/ directory structure
4. ✅ Write first feature YAML (landing page)
5. ✅ Run build_feature.sh
6. ✅ Validate generated code in browser

### Short-term (This Week)
1. Build 3-5 core features
2. Establish visual QA process
3. Document code quality patterns
4. Create design system integration

### Medium-term (This Month)
1. Complete MVP feature set
2. Deploy to staging environment
3. User acceptance testing
4. Production deployment

---

## Success Metrics

**Quantitative:**
- Features built per day: Target 5-10
- Code quality: >80% coverage, >90 Lighthouse
- Time to deploy: <24 hours from feature YAML to production
- Bug rate: <5% features need rework

**Qualitative:**
- Generated code looks hand-written
- Visual design matches mockups
- User flows feel natural
- No "AI smell" in code

---

## The Grand Vision

```
Business Ventures (Multiple Products)
    ↓
Control Tower (Build System - Submodule)
    ↓
Generate → Validate → Deploy
    ↓
Ship Products 10x Faster 🚀
```

**End Game:**
- Use control_tower for ALL business ventures projects
- Prove automation quality with real web apps
- Package control_tower as SaaS product
- Sell automation to other developers

---

## Ready to Start?

Want me to help you:
1. **Clone and setup** the causal-affect repo? ✅
2. **Write the first feature YAML** for landing page? ✅
3. **Generate and review** the first web component? ✅

Let's build something real! 🎯
