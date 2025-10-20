# Architecture Decision: Feature-Level vs System-Level Component Generation

**Date:** 2025-10-15  
**Context:** SYSTEM-CA-006 (Feedback Collection & Iteration Orchestrator)  
**Question:** Should routers, services, models be generated at FEATURE level or SYSTEM level?

---

## TL;DR - The Answer

### ✅ **HYBRID APPROACH** (Best Practice)

**Feature-Level (During Feature Build):**
- ✅ Business logic / Services layer
- ✅ Domain models
- ✅ Feature-specific repositories
- ✅ Feature tests

**System-Level (During System Build):**
- ✅ API routers (integration layer)
- ✅ Main FastAPI app
- ✅ System-wide config
- ✅ Database connections
- ✅ Integration tests

**Why?** Features own their domain logic, System owns how they're exposed/integrated.

---

## Deep Analysis

### Architecture Pattern: Clean/Hexagonal Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     SYSTEM LEVEL                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI Routers)                      │  │
│  │  - api/engagement.py                              │  │
│  │  - api/revenue.py                                 │  │
│  │  - api/prioritization.py                          │  │
│  │  These are THIN wrappers calling feature services│  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓ ↓ ↓                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  System Integration Layer                         │  │
│  │  - app/main.py (FastAPI app)                      │  │
│  │  - app/config.py (system settings)                │  │
│  │  - app/dependencies.py (DI setup)                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓ ↓ ↓
┌─────────────────────────────────────────────────────────┐
│                    FEATURE LEVEL                        │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ │
│  │ FEATURE-02     │  │ FEATURE-03     │  │ FEATURE-04│ │
│  │ Engagement     │  │ Revenue        │  │Priority   │ │
│  ├────────────────┤  ├────────────────┤  ├───────────┤ │
│  │ Services:      │  │ Services:      │  │ Services: │ │
│  │ - tracking.py  │  │ - conversion.py│  │ - scorer.py││
│  │ - metrics.py   │  │ - revenue.py   │  │ - ranker.py││
│  ├────────────────┤  ├────────────────┤  ├───────────┤ │
│  │ Models:        │  │ Models:        │  │ Models:   │ │
│  │ - events.py    │  │ - conversion.py│  │ - item.py │ │
│  ├────────────────┤  ├────────────────┤  ├───────────┤ │
│  │ Repository:    │  │ Repository:    │  │Repository:│ │
│  │ - repo.py      │  │ - repo.py      │  │ - repo.py │ │
│  └────────────────┘  └────────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓ ↓ ↓
┌─────────────────────────────────────────────────────────┐
│              SHARED INFRASTRUCTURE (System Level)       │
│  - db/connection.py                                     │
│  - db/base.py (SQLAlchemy base)                         │
│  - core/exceptions.py                                   │
│  - core/logging.py                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Detailed Breakdown by Component

### 1. **API Routers** → SYSTEM LEVEL ✅

**Location:** `src/backend/app/api/engagement.py`  
**Generated:** During system build (build_system.py)  
**Responsibility:** HTTP layer, request/response handling  

**Why System Level?**
- ✅ Routers are the **integration points** - they wire features together
- ✅ System defines the API contract (URLs, methods, responses)
- ✅ Multiple features might share routes (`/metrics` aggregates all features)
- ✅ Authentication/authorization is system-wide concern
- ✅ CORS, middleware, rate limiting are system concerns

**Example:**
```python
# System Level: app/api/engagement.py
from fastapi import APIRouter, Depends
from features.engagement.services import EngagementTrackingService
from app.dependencies import get_engagement_service

router = APIRouter(prefix="/api/v1/engagement", tags=["Engagement"])

@router.post("/events")
async def track_events(
    request: TrackEventsRequest,
    service: EngagementTrackingService = Depends(get_engagement_service)
):
    """System API endpoint that delegates to feature service"""
    return await service.track_events(request.events)
```

---

### 2. **Services / Business Logic** → FEATURE LEVEL ✅

**Location:** `features/FEATURE-CA-006-02_engagement/services/tracking.py`  
**Generated:** During feature build (build_feature.py)  
**Responsibility:** Business rules, domain logic, orchestration  

**Why Feature Level?**
- ✅ Services contain **domain knowledge** specific to the feature
- ✅ Feature owns its business logic (engagement rules, calculation formulas)
- ✅ Can be tested independently of the system
- ✅ Can be reused across different interfaces (REST API, GraphQL, CLI)
- ✅ Feature should be self-contained and deployable as library

**Example:**
```python
# Feature Level: features/FEATURE-CA-006-02/services/tracking.py
from features.engagement.models import EngagementEvent
from features.engagement.repository import EngagementRepository

class EngagementTrackingService:
    """Feature-owned business logic"""
    
    def __init__(self, repo: EngagementRepository):
        self.repo = repo
    
    async def track_events(self, events: List[EngagementEvent]):
        """Feature-specific business rules"""
        validated_events = [self._validate_event(e) for e in events]
        await self.repo.bulk_insert(validated_events)
        await self._update_metrics(validated_events)
        return {"events_tracked": len(validated_events)}
    
    def _validate_event(self, event: EngagementEvent):
        """Feature-specific validation logic"""
        # Business rules for engagement events
        if event.session_duration < 0:
            raise ValueError("Invalid session duration")
        return event
```

---

### 3. **Domain Models** → FEATURE LEVEL ✅

**Location:** `features/FEATURE-CA-006-02_engagement/models/events.py`  
**Generated:** During feature build (build_feature.py)  
**Responsibility:** Domain entities, value objects, business data structures  

**Why Feature Level?**
- ✅ Models represent **domain concepts** owned by the feature
- ✅ Different features have different data structures
- ✅ Feature evolution shouldn't break other features
- ✅ Clear ownership and boundaries

**Example:**
```python
# Feature Level: features/FEATURE-CA-006-02/models/events.py
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class EngagementEventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"

class EngagementEvent(BaseModel):
    """Feature-owned domain model"""
    event_type: EngagementEventType
    user_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}
```

---

### 4. **Database Models (ORM)** → FEATURE LEVEL ✅

**Location:** `features/FEATURE-CA-006-02_engagement/db/models.py`  
**Generated:** During feature build (build_feature.py)  
**Responsibility:** Database table definitions, SQLAlchemy models  

**Why Feature Level?**
- ✅ Each feature owns its **data schema**
- ✅ Feature migrations are isolated
- ✅ Database tables are prefixed by feature (e.g., `engagement_events`)
- ✅ Schema evolution is feature-specific

**Example:**
```python
# Feature Level: features/FEATURE-CA-006-02/db/models.py
from sqlalchemy import Column, String, DateTime, JSON
from app.db.base import Base  # System provides base

class EngagementEventDB(Base):
    """Feature-owned database table"""
    __tablename__ = "engagement_events"  # Feature prefix
    
    id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime, nullable=False)
    metadata = Column(JSON)
```

---

### 5. **Repositories** → FEATURE LEVEL ✅

**Location:** `features/FEATURE-CA-006-02_engagement/repository/engagement_repo.py`  
**Generated:** During feature build (build_feature.py)  
**Responsibility:** Data access layer, CRUD operations  

**Why Feature Level?**
- ✅ Each feature has **specific query patterns**
- ✅ Feature owns how it accesses its data
- ✅ Repository abstracts database from business logic
- ✅ Different features may use different storage (SQL vs Redis vs S3)

**Example:**
```python
# Feature Level: features/FEATURE-CA-006-02/repository/engagement_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from features.engagement.db.models import EngagementEventDB

class EngagementRepository:
    """Feature-owned data access"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def bulk_insert(self, events: List[EngagementEvent]):
        """Feature-specific query"""
        db_events = [EngagementEventDB(**e.dict()) for e in events]
        self.session.add_all(db_events)
        await self.session.commit()
```

---

### 6. **Database Connection / Session** → SYSTEM LEVEL ✅

**Location:** `src/backend/app/db/connection.py`  
**Generated:** During system build (build_system.py)  
**Responsibility:** Database connection pooling, session management  

**Why System Level?**
- ✅ **Shared infrastructure** across all features
- ✅ Connection pooling is system-wide resource
- ✅ Transaction management spans features
- ✅ Configuration (DB URL, pool size) is system concern

**Example:**
```python
# System Level: app/db/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

class DatabaseManager:
    """System-owned infrastructure"""
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, pool_size=20)
    
    async def get_session(self) -> AsyncSession:
        """Provides sessions to all features"""
        async with AsyncSession(self.engine) as session:
            yield session
```

---

### 7. **Configuration** → SYSTEM LEVEL ✅

**Location:** `src/backend/app/config.py`  
**Generated:** During system build (build_system.py)  
**Responsibility:** Environment variables, system settings, feature flags  

**Why System Level?**
- ✅ System orchestrates all features
- ✅ Feature flags are deployment decisions
- ✅ Database URLs, API keys are deployment secrets
- ✅ CORS, allowed origins are system policies

**Example:**
```python
# System Level: app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """System-wide configuration"""
    DATABASE_URL: str
    REDIS_URL: str
    
    # Feature flags (system decides what's enabled)
    ENABLE_ENGAGEMENT_TRACKING: bool = True
    ENABLE_REVENUE_TRACKING: bool = True
    ENABLE_PRIORITIZATION: bool = True
```

---

### 8. **Tests**

#### Unit Tests → FEATURE LEVEL ✅
**Location:** `features/FEATURE-CA-006-02_engagement/tests/test_tracking.py`  
**Why:** Test feature business logic in isolation

#### Integration Tests → SYSTEM LEVEL ✅
**Location:** `tests/integration/test_engagement_api.py`  
**Why:** Test system integration (API → Service → DB)

---

## Current CA-006 Architecture Analysis

### What YAML Specifies

```yaml
source_backend:
  base_path: "src/feedback_iteration/backend"
  structure:
    app:
      - "main.py"
      - "config.py"
      - "api/"           # ← System level
      - "services/"      # ← WAIT - This is WRONG!
      - "models/"        # ← WAIT - This is WRONG!
      - "db/"            # ← Partially system (connection), partially feature (models)
```

### The Problem with Current YAML

**The YAML mixes feature-level and system-level concerns!**

❌ `app/services/` - Should be in `features/FEATURE-XX/services/`  
❌ `app/models/` - Should be in `features/FEATURE-XX/models/`  
✅ `app/api/` - Correct (system integration layer)  
⚠️ `app/db/` - Should have connection (system) but not models (feature)  

---

## Recommended Architecture for CA-006

### Correct Structure

```
SYSTEM-CA-006_feedback_iteration/
├── SYSTEM-CA-006.yaml
│
├── FEATURE-CA-006-01_analytics_integration/
│   ├── FEATURE-CA-006-01.yaml
│   ├── feature_integration.py          # Feature orchestrator
│   ├── services/
│   │   ├── google_analytics_client.py  # Feature-owned
│   │   ├── mixpanel_client.py          # Feature-owned
│   │   └── amplitude_client.py         # Feature-owned
│   ├── models/
│   │   └── analytics.py                # Feature-owned
│   └── tests/
│       └── test_analytics.py
│
├── FEATURE-CA-006-02_engagement_tracking/
│   ├── FEATURE-CA-006-02.yaml
│   ├── feature_integration.py
│   ├── services/
│   │   ├── tracking_service.py         # Feature-owned business logic
│   │   └── metrics_service.py
│   ├── models/
│   │   ├── events.py                   # Feature-owned domain models
│   │   └── metrics.py
│   ├── db/
│   │   ├── models.py                   # Feature-owned DB schema
│   │   └── repository.py               # Feature-owned data access
│   └── tests/
│       └── test_engagement.py
│
├── FEATURE-CA-006-03_revenue_tracking/
│   ├── services/
│   │   └── revenue_service.py          # Feature-owned
│   ├── models/
│   │   └── conversion.py               # Feature-owned
│   └── db/
│       └── models.py                   # Feature-owned
│
└── src/feedback_iteration/backend/     # ← SYSTEM LEVEL
    ├── app/
    │   ├── main.py                     # System: FastAPI app
    │   ├── config.py                   # System: Configuration
    │   ├── dependencies.py             # System: DI container
    │   │
    │   ├── api/                        # System: Integration layer
    │   │   ├── __init__.py
    │   │   ├── analytics.py            # Thin wrapper → calls FEATURE-01 service
    │   │   ├── engagement.py           # Thin wrapper → calls FEATURE-02 service
    │   │   ├── revenue.py              # Thin wrapper → calls FEATURE-03 service
    │   │   └── dashboard.py            # Aggregates multiple features
    │   │
    │   ├── db/                         # System: Shared infrastructure
    │   │   ├── connection.py           # System-owned
    │   │   └── base.py                 # Base class for all feature models
    │   │
    │   └── core/                       # System: Shared utilities
    │       ├── exceptions.py
    │       ├── logging.py
    │       └── middleware.py
    │
    ├── requirements.txt
    ├── .env.example
    └── docker-compose.yml
```

---

## Build Strategy Implications

### With Correct Architecture

#### 1. Feature Build (build_feature.py)
```bash
# For each feature:
python build_feature.py FEATURE-CA-006-02.yaml

# Generates IN feature directory:
features/FEATURE-CA-006-02_engagement/
  ├── services/tracking_service.py     # Business logic
  ├── models/events.py                 # Domain models
  ├── db/models.py                     # DB schema
  ├── db/repository.py                 # Data access
  └── feature_integration.py           # Orchestrator
```

#### 2. System Build (build_system.py)
```bash
# Once all features built:
python build_system.py SYSTEM-CA-006.yaml

# Generates IN system directory:
src/feedback_iteration/backend/app/
  ├── main.py                          # Wires all features
  ├── config.py                        # System config
  ├── dependencies.py                  # DI setup
  ├── api/                             # Integration layer
  │   ├── engagement.py                # Calls FEATURE-02
  │   └── revenue.py                   # Calls FEATURE-03
  └── db/
      └── connection.py                # Shared infrastructure
```

---

## Decision Matrix

| Component | Level | Generated By | Reason |
|-----------|-------|--------------|--------|
| **Business Logic / Services** | Feature | build_feature.py | Domain knowledge owned by feature |
| **Domain Models** | Feature | build_feature.py | Feature-specific data structures |
| **DB Models (SQLAlchemy)** | Feature | build_feature.py | Feature owns its schema |
| **Repositories** | Feature | build_feature.py | Feature-specific queries |
| **Feature Tests** | Feature | build_feature.py | Test feature in isolation |
| **API Routers** | System | build_system.py | Integration points, wiring |
| **FastAPI App** | System | build_system.py | Orchestrates all features |
| **Configuration** | System | build_system.py | Deployment decisions |
| **DB Connection** | System | build_system.py | Shared infrastructure |
| **Middleware** | System | build_system.py | Cross-cutting concerns |
| **Integration Tests** | System | build_system.py | Test end-to-end flows |
| **Exceptions (base)** | System | build_system.py | Shared error handling |
| **Feature Exceptions** | Feature | build_feature.py | Domain-specific errors |

---

## Benefits of Hybrid Approach

### 1. **Clear Ownership**
- ✅ Features own domain logic
- ✅ System owns integration
- ✅ No confusion about where code lives

### 2. **Independent Development**
- ✅ Features can be developed in parallel
- ✅ Feature changes don't break system
- ✅ System changes don't break features (if contracts maintained)

### 3. **Reusability**
- ✅ Feature services can be used from API, CLI, GraphQL, etc.
- ✅ Features can be deployed as libraries
- ✅ Different systems can reuse same features

### 4. **Testing**
- ✅ Unit test features independently (fast)
- ✅ Integration test system assembly (comprehensive)
- ✅ Clear test boundaries

### 5. **Scalability**
- ✅ Can split features into microservices later
- ✅ Clear service boundaries already defined
- ✅ Each feature has its own database tables

### 6. **Build Process**
- ✅ `build_feature.py` builds feature components (5-7 times)
- ✅ `build_system.py` builds integration layer (1 time)
- ✅ Clear separation of concerns in build tools

---

## Recommendation for CA-006

### Update YAML Structure

```yaml
# SYSTEM-CA-006.yaml
source_backend:
  base_path: "src/feedback_iteration/backend"
  structure:
    app:
      - "main.py"
      - "config.py"
      - "dependencies.py"
      - "api/"              # System integration layer
      - "core/"             # Shared utilities
      - "db/connection.py"  # Shared infrastructure only
    
# Each feature YAML should specify:
# FEATURE-CA-006-02.yaml
source:
  base_path: "FEATURE-CA-006-02_engagement"
  structure:
    - "feature_integration.py"
    - "services/"          # Feature business logic
    - "models/"            # Feature domain models
    - "db/models.py"       # Feature database schema
    - "db/repository.py"   # Feature data access
    - "tests/"             # Feature unit tests
```

### Update build_system.py

System build should:
1. ✅ Read all `feature_integration.py` files
2. ✅ Generate `app/api/*.py` routers that import from features
3. ✅ Generate `app/main.py` that wires routers
4. ✅ Generate `app/dependencies.py` that instantiates feature services
5. ✅ Generate `app/db/connection.py` for shared session
6. ❌ NOT generate services, models, repositories (those are feature-owned)

---

## Conclusion

**Best Practice: HYBRID APPROACH**

- **Feature Level:** Services, Models, Repositories, DB Schema, Domain Logic
- **System Level:** API Routers, Main App, Config, DB Connection, Integration

This gives you:
- ✅ Clean separation of concerns
- ✅ Independent feature development
- ✅ Clear build process
- ✅ Testability
- ✅ Scalability

**For CA-006 specifically:**
- Features 01-06 should each own their services/models/repos
- System build should generate ONLY the integration layer (api/, main.py, config.py)
- Total files: ~40 (35 in features, 5 in system integration)

This architecture makes the build process simpler and more maintainable!
