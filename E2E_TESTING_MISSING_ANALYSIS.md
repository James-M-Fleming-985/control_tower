# E2E Testing Gap Analysis - CA-001 & CA-006

**Date**: October 17, 2025  
**Issue**: Missing dedicated E2E testing tier in system requirements  
**Impact**: Test pyramid incomplete, missing user journey validation

---

## 🔍 **Current State Analysis**

### What We Found

Both CA-001 and CA-006 YAML files mention "end-to-end" testing, but **only within integration tests**, not as a separate testing tier.

**CA-001 Example**:
```yaml
integration_tests:
  required_scenarios:
    end_to_end_ingestion:  # ← This is an integration test, not E2E
      description: "Complete data flow from API to database storage"
```

**CA-006 Example**:
```yaml
integration_tests:
  required_scenarios:
    end_to_end_feedback_loop:  # ← Also integration test, not true E2E
      description: "Complete feedback cycle from MVP to iteration decision"
```

---

## ❌ **Why This is Incorrect**

### Test Pyramid Levels

```
        ╱╲
       ╱  ╲
      ╱ E2E ╲          ← MISSING from both CA-001 and CA-006
     ╱────────╲
    ╱          ╲
   ╱Integration╲       ← Current "end-to-end" tests belong here
  ╱──────────────╲
 ╱                ╲
╱   Unit Tests     ╲   ← Well defined in both
────────────────────
```

### Difference Between Integration and E2E

| Aspect | Integration Tests | E2E Tests |
|--------|-------------------|-----------|
| **Scope** | Component-to-component | User journey, full system |
| **Environment** | Isolated services | Production-like deployment |
| **Data** | Test/mock data | Real or realistic data |
| **User Perspective** | Developer/system view | End-user view |
| **Example (CA-001)** | "API → Database" flow | "User configures source → Data appears in CA-002" |
| **Example (CA-006)** | "Analytics → Metrics → DB" | "User opens dashboard → Sees live MVP metrics" |

---

## ✅ **What E2E Tests Should Cover**

### For CA-001 (Data Ingestion)

**E2E Scenario 1: New Data Source Onboarding**
```
User Action: Admin adds new API source (e.g., Bloomberg API)
Expected: 
1. User enters API key in admin UI
2. System tests connection
3. Data begins flowing within 5 minutes
4. Data appears in CA-002 correlation analysis
5. Dashboard shows new source as "Active"

Verification:
- Navigate admin UI (Selenium/Playwright)
- Add Bloomberg API credentials
- Verify data in TimescaleDB
- Verify downstream systems (CA-002) receive data
- Check monitoring dashboard shows green status
```

**E2E Scenario 2: API Failure Recovery**
```
User Action: External API goes down, then recovers
Expected:
1. Monitoring alerts user (Slack/email)
2. System retries automatically
3. No data loss when API recovers
4. User sees "Degraded" then "Healthy" status

Verification:
- Simulate API downtime (block network)
- Verify alert received
- Restore network
- Confirm data backfilled
- Check audit log shows recovery
```

### For CA-006 (Dashboard)

**E2E Scenario 1: MVP Performance Tracking**
```
User Action: User opens dashboard to check MVP performance
Expected:
1. Dashboard loads in < 3 seconds
2. Shows 10 active MVPs with metrics
3. Metrics updated within 5 minutes
4. User clicks MVP → Drill-down view opens
5. User sees charts, revenue, users

Verification:
- Open browser (Playwright)
- Navigate to https://dashboard.causalaffect.com
- Measure load time
- Verify all MVPs visible
- Click "TaskMaster" MVP
- Verify charts render correctly
```

**E2E Scenario 2: Archive Low-Performer**
```
User Action: User archives underperforming MVP
Expected:
1. User sees red "Archive" flag on MVP
2. User clicks "Archive" button
3. Confirmation modal appears
4. User confirms → MVP shut down within 30 minutes
5. MVP disappears from active list
6. Archived MVP appears in "Archived" tab

Verification:
- Identify low-performing MVP
- Click Archive button
- Confirm action
- Wait for shutdown
- Verify infrastructure destroyed (Railway)
- Verify MVP in archived list
```

---

## 📝 **Proposed E2E Testing Section**

### Template for System Requirements

```yaml
testing_requirements:
  unit_tests:
    # ... existing ...
  
  integration_tests:
    # ... existing ...
  
  e2e_tests:  # ← ADD THIS SECTION
    minimum_count: 5
    coverage_threshold: 0.70
    environment: "production-like deployment"
    runner: "Playwright or Cypress"
    
    philosophy: |
      E2E tests validate complete user journeys across the entire system.
      Tests run against deployed services in production-like environment.
      No mocking - all services, databases, and integrations are real.
      Focus on critical user paths and business workflows.
    
    required_scenarios:
      user_journey_1:
        name: "[Primary User Journey]"
        description: "[What the user is trying to accomplish]"
        steps:
          - step: 1
            action: "[User action in UI or API call]"
            verification: "[What should happen]"
          
          - step: 2
            action: "[Next user action]"
            verification: "[Expected outcome]"
        
        acceptance_criteria:
          - "[Specific success criterion]"
          - "[Performance requirement]"
          - "[Data correctness check]"
      
      user_journey_2:
        # ... additional scenarios ...
    
    deployment_requirements:
      - "Dedicated E2E test environment on Railway"
      - "Real PostgreSQL database (separate from dev/prod)"
      - "Real analytics providers (test accounts)"
      - "Monitoring enabled (to verify alerts)"
    
    ci_cd_integration:
      trigger: "Before production deployment"
      failure_action: "Block deployment"
      execution_time_budget: "15 minutes maximum"
```

---

## 🎯 **Recommendation**

### Immediate Action (Today)

1. ✅ Add E2E testing section to **SYSTEM_REQUIREMENTS_TEMPLATE.yaml**
2. ✅ Update **CA-006** with E2E testing section
3. ✅ Update **CA-001** with E2E testing section (as part of structure upgrade)
4. Document in **SYSTEM_REQUIREMENTS_TEMPLATE_GUIDE.md**

### Why E2E Tests Matter

**For CA-001**:
- Validates data actually flows from external APIs → CA-002
- Tests failure recovery scenarios users will encounter
- Ensures admin UI for managing sources works

**For CA-006**:
- Validates dashboard loads and displays correctly for real users
- Tests entire feedback loop (analytics → metrics → decisions)
- Ensures alerts and notifications work

**For All Systems**:
- Catches integration issues that unit/integration tests miss
- Validates deployment and configuration
- Tests real user workflows, not just technical interfaces
- Provides confidence for production deployments

---

## 📚 **Additional Resources**

- **Martin Fowler - Test Pyramid**: https://martinfowler.com/bliki/TestPyramid.html
- **Playwright E2E Testing**: https://playwright.dev/
- **Cypress Best Practices**: https://docs.cypress.io/guides/references/best-practices

---

**Conclusion**: Both CA-001 and CA-006 have robust unit and integration test requirements, but are **missing the E2E testing tier** that validates complete user journeys. We should add this immediately to ensure production readiness.
