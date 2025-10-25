# Feature Enhancement Requirements - Anonymous Feedback Collector v2

**Date**: 2024-10-24  
**Sprint**: Iteration 2  
**Status**: Requirements Definition

## 📋 User Feedback Summary

From initial MVP review, user identified three key enhancements:

### 1. Professional Branding & UI Polish
**Current State**: Generic "MVPBuilder" placeholder branding  
**Required**:
- Give application a proper name
- Professional header/logo design
- Improve overall visual presentation
- Remove scaffolding artifacts

**Priority**: HIGH (blocks credibility)

### 2. Request-Based Feedback Model
**Current State**: Simple anonymous feedback form  
**Required**: Transform into feedback REQUEST system where:
- User selects recipients (colleagues, friends, family)
- System sends email invitations to provide feedback
- Two feedback modes:
  - **Free Text**: Open-ended feedback (current capability)
  - **Objective Prompts**: Structured feedback with predefined questions
- Recipients click link, provide feedback anonymously
- Requestor receives aggregated feedback

**Use Cases**:
- Professional: 360 reviews, peer feedback, team dynamics
- Personal: Self-improvement, relationship feedback, life coaching

**Priority**: HIGH (core product pivot)

### 3. Context Toggles & Modes
**Required UI Controls**:
- Toggle: Personal / Professional context
- Toggle: Free Text / Objective Prompts
- Dynamic form that adapts based on selections
- Keep single-page simplicity

**Priority**: MEDIUM (enhances UX)

---

## 🏗️ Architecture Decision

### Option A: Quick Iteration (Recommended for Now)
**Approach**: Build directly in MVP, no template updates yet
- ✅ Fast iteration cycle
- ✅ Validate features before templating
- ✅ Avoid premature abstraction
- ❌ Not reusable yet

**When to use**: Early feature exploration, unclear requirements

### Option B: Update Templates & Scaffold
**Approach**: Create new templates for these patterns
- ✅ Reusable for future projects
- ✅ Maintains scaffold system value
- ❌ Slower iteration
- ❌ Over-engineering risk if features change

**When to use**: Proven patterns, stable requirements, 3+ similar projects

### Option C: Hybrid (Best for This Case)
**Approach**: 
1. Build features directly in MVP (fast iteration)
2. Track "template-worthy" patterns in `TEMPLATE_CANDIDATES.md`
3. After 2-3 iterations, extract stable patterns into templates

**Benefits**:
- Fast now, organized later
- Evidence-based template creation
- No premature optimization

---

## 📝 Recommended Next Steps

### Immediate (This Session)
1. **Create Feature Requirements Document** (this file)
2. **Design New Component Structure**:
   - `RequestFeedbackWizard.tsx` - Main flow
   - `RecipientSelector.tsx` - Email input with validation
   - `FeedbackModeSelector.tsx` - Free text vs prompts toggle
   - `ContextToggle.tsx` - Personal/Professional switch
   - `ObjectivePromptBuilder.tsx` - For structured feedback

3. **Update Backend API**:
   - POST `/api/feedback-request` - Create request, send emails
   - GET `/api/feedback/:token` - Anonymous feedback submission
   - POST `/api/feedback/:token` - Submit feedback anonymously
   - GET `/api/my-requests` - View sent requests & responses

4. **Branding**:
   - Name: "FeedbackLoop" or "InsightRequest" or "ClearVoice"
   - Professional color scheme
   - Clean logo/header

### Short-term (Next 1-2 Sessions)
1. Implement email sending (SendGrid/Resend)
2. Build recipient management
3. Create objective prompt library
4. Add authentication for requestors (not recipients)

### Medium-term (Before Public Launch)
1. Add database (PostgreSQL via Railway)
2. Implement proper email templates
3. Add dashboard for viewing requests
4. Security audit
5. Analytics verification

### Long-term (After Launch)
1. Extract stable patterns into templates
2. Create `tpl-feedback-request-flow` template
3. Create `tpl-email-invitation-system` template
4. Update scaffold system with learnings

---

## 🎨 Design System Requirements

### Branding
- **Name**: TBD (user to decide)
- **Tagline**: "Get honest feedback, anonymously"
- **Colors**: Professional (blues/grays), Trust-building
- **Typography**: Modern, readable (Inter or similar)

### UI Components Needed
- [ ] Professional header with logo
- [ ] Stepper/wizard for request flow
- [ ] Email input with validation
- [ ] Toggle switches (animated)
- [ ] Card-based layouts
- [ ] Success/confirmation screens
- [ ] Email templates (invitation, reminder)

---

## 🔄 Development Workflow

### For This Iteration (Recommended)
```
1. Requirements Doc (this file) ✓
2. Update existing MVP directly
3. Test with real email flow
4. Get user feedback
5. Iterate
6. Document what worked → template candidates
```

### NOT Recommended Yet
```
❌ Create new templates
❌ Update scaffold generator
❌ Rebuild from scratch
❌ Deploy to production
```

**Why**: Features are still evolving, requirements may change after testing

---

## 📊 Success Criteria

### Iteration 2 Complete When:
- [ ] Application has professional name & branding
- [ ] User can input recipient emails
- [ ] System sends email invitations (mockup OK for now)
- [ ] Personal/Professional toggle works
- [ ] Free Text/Objective Prompts modes implemented
- [ ] Basic objective prompts library created
- [ ] UI feels cohesive and professional

### Ready for Templates When:
- [ ] Feature set stable for 2+ weeks
- [ ] User feedback positive
- [ ] Patterns clearly reusable
- [ ] Similar need in 2+ other projects

---

## 💡 Template Candidate Tracking

As we build, track patterns that could become templates:

### Potential Templates
1. **Request-Response Flow Pattern**
   - Send invitation → Anonymous response → Aggregation
   - Reusable for: Surveys, Reviews, Assessments

2. **Email Invitation System**
   - Token-based anonymous links
   - Reminder system
   - Response tracking

3. **Toggle-Based Form Adaptation**
   - Forms that change based on context
   - Reusable for: Multi-mode apps, wizards

4. **Professional Branding Kit**
   - Header, footer, color schemes
   - Reusable for: Any SaaS landing page

**Document these in**: `TEMPLATE_CANDIDATES.md` as we build

---

## 🚀 Deployment Strategy

### Current: NOT READY
- Missing core features
- No email system
- No authentication
- Branding incomplete

### Staging Deployment (After Iteration 2)
- Deploy to Railway with `/staging` subdomain
- Invite beta testers
- Collect feedback

### Production Deployment (After Iteration 3-4)
- Full feature set
- Security hardened
- Analytics validated
- Email templates polished

---

## Next Session Plan

**User to decide**:
1. Pick application name
2. Approve or refine feature requirements above
3. Start building OR refine requirements first

**Then**:
1. Update branding (Hero, title, colors)
2. Build recipient selector
3. Add toggles (Personal/Professional, Free/Prompts)
4. Implement basic request flow

**Time estimate**: 30-45 minutes for visual improvements + basic flow
