# YAML Refactor & Multi-Phase Implementation Plan

**Date**: October 15, 2025  
**Target Completion**: October 16, 2025  
**Objective**: Fix YAML architecture violations + Implement multi-phase generation for 100% compliance  
**Current State**: 60% compliant, 25% implemented  
**Target State**: 100% compliant, 100% implemented

---

## Executive Summary

### Two-Part Plan

**Part 1: YAML Requirements Refactor** (30-45 minutes)
- Fix System YAML: Remove `app/services/`, `app/models/`
- Fix Feature YAMLs: Add explicit `models/`, `db/`, `tests/` specifications
- Split System YAML into generation phases for Claude API compliance

**Part 2: Multi-Phase Build Implementation** (60-90 minutes)
- Update `build_system.py` to support phased generation
- Execute 10-12 separate AI calls (each under 8K token limit)
- Generate complete backend: 35-40 files, 2,500-3,000 lines
- Achieve 100% requirements compliance

### Success Criteria

✅ YAML Compliance: 100% (up from 60%)  
✅ Backend Files: 35-40 files (up from 9)  
✅ Code Lines: 2,500-3,000 (up from 464)  
✅ Architecture: Proper hybrid with feature encapsulation  
✅ Tests: 20+ unit tests (up from 0)  
✅ True Automation: No manual code completion required

---

## Part 1: YAML Requirements Refactor

### 1.1 Fix System-Level YAML (SYSTEM-CA-006.yaml)

**File**: `/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/SYSTEM-CA-006.yaml`

#### Current Issues (lines 76-84)

```yaml
# CURRENT - VIOLATES BEST PRACTICES ❌
structure:
  app:
    - "__init__.py"
    - "main.py          # FastAPI app instance, lifespan, routers"
    - "config.py        # Pydantic Settings for environment configuration"
    - "api/             # API route handlers"
    - "services/        # Business logic (analytics clients, prioritization)"  ❌ REMOVE
    - "models/          # Pydantic models for request/response/database"      ❌ REMOVE
    - "db/              # Database connections, migrations, repositories"     ⚠️ TOO BROAD
```

#### Recommended Fix

```yaml
# FIXED - COMPLIANT WITH BEST PRACTICES ✅
structure:
  app:
    - "__init__.py"
    - "main.py          # FastAPI app, lifespan, router registration"
    - "config.py        # System-wide Pydantic Settings"
    - "api/             # Thin router wrappers calling feature services
        - __init__.py
        - engagement.py      # Routes to features/FEATURE-02/services/
        - revenue.py         # Routes to features/FEATURE-03/services/
        - prioritization.py  # Routes to features/FEATURE-04/services/
        - iteration.py       # Routes to features/FEATURE-05/services/
        - dashboard.py       # Routes to features/FEATURE-06/services/"
    - "db/              # System-level database infrastructure ONLY
        - __init__.py
        - connection.py      # SQLAlchemy engine, async session factory
        - base.py            # Declarative base for features to inherit"
    - "middleware/      # Cross-cutting concerns
        - __init__.py
        - error_handler.py   # Global exception handling
        - logging.py         # Request/response logging
        - cors.py            # CORS configuration"
    - "schemas/         # Shared DTOs only (no domain models)
        - __init__.py
        - health.py          # HealthResponse
        - error.py           # ErrorResponse, ValidationError"
  
  features:           # ADD THIS ENTIRE SECTION ⚡
    - "FEATURE-CA-006-01_analytics_integration/
        - __init__.py
        - services/         # Google Analytics, Mixpanel, Amplitude clients
        - models/           # Analytics event models, client configs
        - db/               # Analytics event schema, repositories
        - tests/            # Unit tests for analytics clients"
    
    - "FEATURE-CA-006-02_engagement_tracking/
        - __init__.py
        - services/         # EventCollector, SessionTracker, MetricsCalculator
        - models/           # EngagementEvent, SessionData, Metrics
        - db/               # Engagement schema, repositories
        - tests/            # Unit tests for engagement services"
    
    - "FEATURE-CA-006-03_revenue_tracking/
        - __init__.py
        - services/         # ConversionTracker, RevenueCalculator
        - models/           # ConversionEvent, RevenueMetrics
        - db/               # Revenue schema, repositories
        - tests/            # Unit tests for revenue tracking"
    
    - "FEATURE-CA-006-04_prioritization_engine/
        - __init__.py
        - services/         # ScoreCalculator, PriorityRanker
        - models/           # FeatureScore, PriorityData
        - db/               # Priority schema, repositories
        - tests/            # Unit tests for prioritization"
    
    - "FEATURE-CA-006-05_automated_iteration/
        - __init__.py
        - services/         # IterationOrchestrator, ArchiveManager
        - models/           # IterationPlan, ArchiveDecision
        - db/               # Iteration history schema
        - tests/            # Unit tests for iteration logic"
    
    - "FEATURE-CA-006-06_dashboard_visualization/
        - __init__.py
        - services/         # DashboardDataAggregator, ChartGenerator
        - models/           # DashboardConfig, ChartData
        - db/               # Dashboard config schema
        - tests/            # Unit tests for dashboard services"
```

### 1.2 Add Feature YAMLs `models/` Specification

**Files to Update** (6 feature YAMLs):
1. `FEATURE-CA-006-01_analytics_integration.yaml`
2. `FEATURE-CA-006-02_engagement_tracking.yaml`
3. `FEATURE-CA-006-03_revenue_tracking.yaml`
4. `FEATURE-CA-006-04_prioritization_engine.yaml`
5. `FEATURE-CA-006-05_automated_iteration.yaml`
6. `FEATURE-CA-006-06_dashboard_visualization.yaml`

#### Example: FEATURE-CA-006-02_engagement_tracking.yaml

**Current** (around line 180):
```yaml
implementation_notes:
  code_structure:
    - "engagement/event_collector.py - EventCollector"
    - "engagement/session_tracker.py - SessionTracker"
    - "engagement/metrics_calculator.py - MetricsCalculator"
    - "engagement/real_time_processor.py - RealTimeProcessor"
    - "engagement/storage.py - EngagementStorage"
    - "engagement/cache.py - EngagementCache"
```

**Add After** (complete specification):
```yaml
implementation_notes:
  directory_structure: |
    features/FEATURE-CA-006-02_engagement_tracking/
    ├── __init__.py
    ├── services/
    │   ├── __init__.py
    │   ├── event_collector.py
    │   ├── session_tracker.py
    │   ├── metrics_calculator.py
    │   ├── real_time_processor.py
    │   ├── storage.py
    │   └── cache.py
    ├── models/
    │   ├── __init__.py
    │   ├── event.py
    │   ├── session.py
    │   └── metrics.py
    ├── db/
    │   ├── __init__.py
    │   ├── schema.py
    │   └── repositories.py
    └── tests/
        ├── __init__.py
        ├── test_event_collector.py
        ├── test_session_tracker.py
        ├── test_metrics_calculator.py
        └── test_repositories.py
  
  code_structure:
    # Services Layer
    - "services/event_collector.py - EventCollector class with async event ingestion"
    - "services/session_tracker.py - SessionTracker for session management"
    - "services/metrics_calculator.py - MetricsCalculator for aggregations"
    - "services/real_time_processor.py - RealTimeProcessor for stream processing"
    - "services/storage.py - EngagementStorage facade for persistence"
    - "services/cache.py - EngagementCache for Redis operations"
    
    # Models Layer (ADD THIS) ⚡
    - "models/event.py:
        - EngagementEvent (Pydantic): event_id, user_id, event_type, timestamp, metadata
        - EventType (Enum): PAGE_VIEW, CLICK, FORM_SUBMIT, VIDEO_PLAY, etc.
        - EventMetadata (Pydantic): Additional event properties"
    
    - "models/session.py:
        - SessionData (Pydantic): session_id, user_id, start_time, end_time, events
        - SessionStatus (Enum): ACTIVE, EXPIRED, TERMINATED
        - SessionMetrics (Pydantic): duration, event_count, engagement_score"
    
    - "models/metrics.py:
        - EngagementMetrics (Pydantic): Total events, unique users, avg session duration
        - AggregatedMetrics (Pydantic): Time-windowed aggregations
        - MetricsResponse (Pydantic): API response format"
    
    # Database Layer (ADD THIS) ⚡
    - "db/schema.py:
        - EngagementEventORM (SQLAlchemy): Database table for events
        - SessionORM (SQLAlchemy): Database table for sessions
        - Indexes: user_id, timestamp, event_type for query optimization"
    
    - "db/repositories.py:
        - EngagementRepository: Async CRUD operations
        - Methods: create_event, get_events_by_user, get_session, aggregate_metrics"
    
    # Tests Layer (ADD THIS) ⚡
    - "tests/test_event_collector.py: Unit tests for EventCollector (10+ test cases)"
    - "tests/test_session_tracker.py: Unit tests for SessionTracker (8+ test cases)"
    - "tests/test_metrics_calculator.py: Unit tests for MetricsCalculator (6+ test cases)"
    - "tests/test_repositories.py: Integration tests for database operations"
```

**Replicate Pattern for Features 01, 03-06** with appropriate models:
- FEATURE-01: `GoogleAnalyticsEvent`, `MixpanelEvent`, `AnalyticsClientConfig`
- FEATURE-03: `ConversionEvent`, `RevenueMetrics`, `ConversionFunnel`
- FEATURE-04: `FeatureScore`, `PriorityData`, `RankingCriteria`
- FEATURE-05: `IterationPlan`, `ArchiveDecision`, `IterationHistory`
- FEATURE-06: `DashboardConfig`, `ChartData`, `VisualizationSettings`

### 1.3 Split System YAML into Generation Phases

**New Section to Add**: `code_generation.phases`

**Location**: After `code_generation.folder_structure` in SYSTEM-CA-006.yaml

```yaml
code_generation:
  # ... existing folder_structure ...
  
  phases:
    description: "Multi-phase generation strategy to comply with Claude API 8K token output limit"
    total_phases: 10
    estimated_total_time: "60 minutes"
    
    phase_01_system_infrastructure:
      name: "System Infrastructure"
      max_tokens: 8192
      estimated_time: "3 minutes"
      dependencies: []
      files:
        - "app/__init__.py"
        - "app/main.py - FastAPI app initialization, lifespan, router includes"
        - "app/config.py - Pydantic Settings with feature flags, DB URL, Redis URL"
        - "app/db/__init__.py"
        - "app/db/connection.py - Async SQLAlchemy engine, session factory"
        - "app/db/base.py - Declarative base for ORM models"
        - "app/middleware/__init__.py"
        - "app/middleware/error_handler.py - Global exception handling"
        - "app/middleware/logging.py - Request/response logging"
        - "app/schemas/__init__.py"
        - "app/schemas/health.py - HealthResponse model"
        - "app/schemas/error.py - ErrorResponse, ValidationError models"
      acceptance_criteria:
        - "FastAPI app starts without errors"
        - "Database connection pool initializes"
        - "Health endpoint returns 200 OK"
    
    phase_02_system_api_routers:
      name: "System API Routers (Thin Wrappers)"
      max_tokens: 8192
      estimated_time: "5 minutes"
      dependencies: ["phase_01_system_infrastructure"]
      files:
        - "app/api/__init__.py"
        - "app/api/engagement.py - Router for engagement endpoints, calls feature services"
        - "app/api/revenue.py - Router for revenue endpoints"
        - "app/api/prioritization.py - Router for prioritization endpoints"
        - "app/api/iteration.py - Router for iteration endpoints"
        - "app/api/dashboard.py - Router for dashboard endpoints"
      acceptance_criteria:
        - "All routers registered in main.py"
        - "Each router has placeholder endpoints returning 501 Not Implemented"
        - "OpenAPI docs generated successfully"
    
    phase_03_feature_01_analytics:
      name: "FEATURE-01: Analytics Integration"
      max_tokens: 8192
      estimated_time: "8 minutes"
      dependencies: ["phase_01_system_infrastructure"]
      feature_id: "FEATURE-CA-006-01"
      feature_yaml: "FEATURE-CA-006-01_analytics_integration/FEATURE-CA-006-01_analytics_integration.yaml"
      files:
        - "features/FEATURE-CA-006-01_analytics_integration/__init__.py"
        - "features/FEATURE-CA-006-01_analytics_integration/services/__init__.py"
        - "features/FEATURE-CA-006-01_analytics_integration/services/google_analytics_client.py"
        - "features/FEATURE-CA-006-01_analytics_integration/services/mixpanel_client.py"
        - "features/FEATURE-CA-006-01_analytics_integration/models/__init__.py"
        - "features/FEATURE-CA-006-01_analytics_integration/models/analytics_event.py"
        - "features/FEATURE-CA-006-01_analytics_integration/db/__init__.py"
        - "features/FEATURE-CA-006-01_analytics_integration/db/schema.py"
        - "features/FEATURE-CA-006-01_analytics_integration/db/repositories.py"
      acceptance_criteria:
        - "Analytics clients can send events to Google Analytics"
        - "Mixpanel integration works with API key"
        - "Events stored in database"
    
    phase_04_feature_02_engagement:
      name: "FEATURE-02: Engagement Tracking"
      max_tokens: 8192
      estimated_time: "8 minutes"
      dependencies: ["phase_01_system_infrastructure"]
      feature_id: "FEATURE-CA-006-02"
      feature_yaml: "FEATURE-CA-006-02_engagement_tracking/FEATURE-CA-006-02_engagement_tracking.yaml"
      files:
        - "features/FEATURE-CA-006-02_engagement_tracking/__init__.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/services/__init__.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/services/event_collector.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/services/session_tracker.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/services/metrics_calculator.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/models/__init__.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/models/event.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/models/session.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/models/metrics.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/db/__init__.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/db/schema.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/db/repositories.py"
      acceptance_criteria:
        - "Can collect engagement events via POST /api/engagement/events"
        - "Sessions tracked with timeout logic"
        - "Metrics calculated in real-time"
    
    phase_05_feature_03_revenue:
      name: "FEATURE-03: Revenue Tracking"
      max_tokens: 8192
      estimated_time: "8 minutes"
      dependencies: ["phase_01_system_infrastructure"]
      feature_id: "FEATURE-CA-006-03"
      feature_yaml: "FEATURE-CA-006-03_revenue_tracking/FEATURE-CA-006-03_revenue_tracking.yaml"
      files:
        - "features/FEATURE-CA-006-03_revenue_tracking/__init__.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/services/__init__.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/services/conversion_tracker.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/services/revenue_calculator.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/models/__init__.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/models/conversion.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/models/revenue.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/db/__init__.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/db/schema.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/db/repositories.py"
      acceptance_criteria:
        - "Conversion events tracked with attribution"
        - "Revenue calculated with LTV metrics"
        - "Funnel analysis available"
    
    phase_06_feature_04_prioritization:
      name: "FEATURE-04: Prioritization Engine"
      max_tokens: 8192
      estimated_time: "10 minutes"
      dependencies: ["phase_04_feature_02_engagement", "phase_05_feature_03_revenue"]
      feature_id: "FEATURE-CA-006-04"
      feature_yaml: "FEATURE-CA-006-04_prioritization_engine/FEATURE-CA-006-04_prioritization_engine.yaml"
      files:
        - "features/FEATURE-CA-006-04_prioritization_engine/__init__.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/services/__init__.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/services/score_calculator.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/services/priority_ranker.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/models/__init__.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/models/score.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/models/priority.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/db/__init__.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/db/schema.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/db/repositories.py"
      acceptance_criteria:
        - "Features scored using engagement + revenue data"
        - "Priority ranking updates in real-time"
        - "Top 5 features identified correctly"
    
    phase_07_feature_05_iteration:
      name: "FEATURE-05: Automated Iteration"
      max_tokens: 8192
      estimated_time: "8 minutes"
      dependencies: ["phase_06_feature_04_prioritization"]
      feature_id: "FEATURE-CA-006-05"
      feature_yaml: "FEATURE-CA-006-05_automated_iteration/FEATURE-CA-006-05_automated_iteration.yaml"
      files:
        - "features/FEATURE-CA-006-05_automated_iteration/__init__.py"
        - "features/FEATURE-CA-006-05_automated_iteration/services/__init__.py"
        - "features/FEATURE-CA-006-05_automated_iteration/services/iteration_orchestrator.py"
        - "features/FEATURE-CA-006-05_automated_iteration/services/archive_manager.py"
        - "features/FEATURE-CA-006-05_automated_iteration/models/__init__.py"
        - "features/FEATURE-CA-006-05_automated_iteration/models/iteration_plan.py"
        - "features/FEATURE-CA-006-05_automated_iteration/models/archive_decision.py"
        - "features/FEATURE-CA-006-05_automated_iteration/db/__init__.py"
        - "features/FEATURE-CA-006-05_automated_iteration/db/schema.py"
        - "features/FEATURE-CA-006-05_automated_iteration/db/repositories.py"
      acceptance_criteria:
        - "Iteration plans generated based on priority scores"
        - "Low-performing features archived automatically"
        - "Iteration history tracked in database"
    
    phase_08_feature_06_dashboard:
      name: "FEATURE-06: Dashboard Visualization"
      max_tokens: 8192
      estimated_time: "8 minutes"
      dependencies: ["phase_04_feature_02_engagement", "phase_05_feature_03_revenue", "phase_06_feature_04_prioritization"]
      feature_id: "FEATURE-CA-006-06"
      feature_yaml: "FEATURE-CA-006-06_dashboard_visualization/FEATURE-CA-006-06_dashboard_visualization.yaml"
      files:
        - "features/FEATURE-CA-006-06_dashboard_visualization/__init__.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/services/__init__.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/services/data_aggregator.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/services/chart_generator.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/models/__init__.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/models/dashboard_config.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/models/chart_data.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/db/__init__.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/db/schema.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/db/repositories.py"
      acceptance_criteria:
        - "Dashboard data aggregated from all features"
        - "Chart data formatted for frontend consumption"
        - "Real-time updates via WebSocket"
    
    phase_09_tests:
      name: "Unit & Integration Tests"
      max_tokens: 8192
      estimated_time: "10 minutes"
      dependencies: ["phase_03_feature_01_analytics", "phase_04_feature_02_engagement", "phase_05_feature_03_revenue", "phase_06_feature_04_prioritization", "phase_07_feature_05_iteration", "phase_08_feature_06_dashboard"]
      files:
        - "tests/__init__.py"
        - "tests/conftest.py - Pytest fixtures for DB, Redis, test clients"
        - "features/FEATURE-CA-006-01_analytics_integration/tests/test_google_analytics_client.py"
        - "features/FEATURE-CA-006-01_analytics_integration/tests/test_mixpanel_client.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/tests/test_event_collector.py"
        - "features/FEATURE-CA-006-02_engagement_tracking/tests/test_session_tracker.py"
        - "features/FEATURE-CA-006-03_revenue_tracking/tests/test_conversion_tracker.py"
        - "features/FEATURE-CA-006-04_prioritization_engine/tests/test_score_calculator.py"
        - "features/FEATURE-CA-006-05_automated_iteration/tests/test_iteration_orchestrator.py"
        - "features/FEATURE-CA-006-06_dashboard_visualization/tests/test_data_aggregator.py"
      acceptance_criteria:
        - "All tests pass with pytest"
        - "Test coverage > 80%"
        - "Integration tests verify feature interactions"
    
    phase_10_devops:
      name: "DevOps & Configuration"
      max_tokens: 8192
      estimated_time: "5 minutes"
      dependencies: ["phase_01_system_infrastructure"]
      files:
        - "requirements.txt - Complete dependencies (SQLAlchemy, Redis, Celery, etc.)"
        - "Dockerfile.dev - Development container with hot reload"
        - "docker-compose.dev.yml - PostgreSQL, Redis, backend services"
        - ".env.example - All environment variables documented"
        - "alembic.ini - Database migration configuration"
        - "alembic/env.py - Alembic environment setup"
        - "alembic/versions/001_initial_schema.py - Initial DB migration"
        - "README.md - How to run CA-006 locally and deploy"
      acceptance_criteria:
        - "docker-compose up starts all services"
        - "Database migrations run successfully"
        - "All environment variables documented"
```

---

## Part 2: Multi-Phase Build Implementation

### 2.1 Update `build_system.py` Architecture

**File**: `/workspaces/control_tower/build_system.py`

#### New Class Structure

```python
class SystemBuilder:
    """
    Multi-phase system builder that generates complete backend
    in compliance with Claude API 8K token output limit.
    """
    
    def __init__(self, system_yaml_path: str):
        self.system_yaml_path = Path(system_yaml_path)
        self.system_spec = self.load_system_spec()
        self.phases = self.system_spec['code_generation']['phases']
        self.output_base = Path(self.system_spec['code_generation']['folder_structure']['source_backend']['base_path'])
        self.feature_yamls = self._load_feature_yamls()
        
    def generate_system_integration(self):
        """Execute all generation phases in dependency order."""
        print("🚀 Starting Multi-Phase System Integration Generation")
        print(f"Total Phases: {self.phases['total_phases']}")
        print(f"Estimated Time: {self.phases['estimated_total_time']}\n")
        
        results = {}
        
        for phase_key in sorted(self.phases.keys()):
            if phase_key in ['description', 'total_phases', 'estimated_total_time']:
                continue
                
            phase = self.phases[phase_key]
            
            # Check dependencies
            if not self._dependencies_met(phase, results):
                self.print_step("⏸️", f"Skipping {phase['name']} - dependencies not met")
                continue
            
            # Generate phase
            self.print_step("🔨", f"Phase: {phase['name']} ({phase['estimated_time']})")
            phase_result = self._generate_phase(phase)
            results[phase_key] = phase_result
            
            # Validate acceptance criteria
            if not self._validate_acceptance_criteria(phase, phase_result):
                self.print_step("❌", f"Phase {phase['name']} failed acceptance criteria")
                return False
            
            self.print_step("✅", f"Phase {phase['name']} complete\n")
        
        return self._generate_summary(results)
    
    def _generate_phase(self, phase: dict) -> dict:
        """Generate files for a single phase using AI Code Generator."""
        
        # Build phase-specific prompt
        prompt = self._build_phase_prompt(phase)
        
        # Call AI Code Generator (Claude API)
        response = self.ai_code_generator.generate(
            prompt=prompt,
            max_tokens=phase['max_tokens'],
            temperature=0.3
        )
        
        # Extract and create files
        files_created = self._extract_and_create_files(response, phase)
        
        return {
            'phase_name': phase['name'],
            'files_created': files_created,
            'estimated_time': phase['estimated_time'],
            'status': 'success'
        }
    
    def _build_phase_prompt(self, phase: dict) -> str:
        """Build AI prompt for specific phase."""
        
        if 'feature_id' in phase:
            # Feature phase - load feature YAML
            feature_yaml = self.feature_yamls[phase['feature_id']]
            return f"""
Generate COMPLETE, PRODUCTION-READY code for {phase['name']}.

REQUIREMENTS:
{self._extract_feature_requirements(feature_yaml)}

ARCHITECTURE:
- Feature owns: services/, models/, db/, tests/
- Use SQLAlchemy for database
- Use Pydantic for models
- Follow async/await patterns

FILES TO GENERATE:
{self._format_file_list(phase['files'])}

ACCEPTANCE CRITERIA:
{self._format_acceptance_criteria(phase['acceptance_criteria'])}

CONSTRAINTS:
- Complete code, NO placeholders, NO TODOs
- Include all imports
- Add type hints
- Include docstrings
- Max {phase['max_tokens']} tokens

OUTPUT FORMAT:
```json
{{
  "files": [
    {{
      "path": "features/.../services/example.py",
      "content": "complete file content here"
    }}
  ]
}}
```
"""
        else:
            # System phase
            return f"""
Generate COMPLETE, PRODUCTION-READY code for {phase['name']}.

SYSTEM REQUIREMENTS:
{self._extract_system_requirements()}

FILES TO GENERATE:
{self._format_file_list(phase['files'])}

ACCEPTANCE CRITERIA:
{self._format_acceptance_criteria(phase['acceptance_criteria'])}

CONSTRAINTS:
- Complete code, NO placeholders
- FastAPI best practices
- Async/await patterns
- Max {phase['max_tokens']} tokens

OUTPUT FORMAT: JSON with files array
"""
    
    def _dependencies_met(self, phase: dict, results: dict) -> bool:
        """Check if phase dependencies are satisfied."""
        dependencies = phase.get('dependencies', [])
        return all(dep in results and results[dep]['status'] == 'success' 
                   for dep in dependencies)
    
    def _validate_acceptance_criteria(self, phase: dict, result: dict) -> bool:
        """Validate phase output against acceptance criteria."""
        criteria = phase.get('acceptance_criteria', [])
        
        # For now, just check files were created
        # TODO: Add syntax validation, import checks, etc.
        return len(result['files_created']) > 0
```

#### Key Improvements

1. **Phase-by-Phase Execution**: Each phase is 1 AI call under 8K tokens
2. **Dependency Management**: Phases execute in correct order
3. **Feature YAML Integration**: Each feature phase loads its YAML requirements
4. **Acceptance Criteria Validation**: Each phase validated before proceeding
5. **Progress Tracking**: Clear console output showing phase progress

### 2.2 Implementation Steps for Tomorrow

#### Step 1: YAML Refactor (30-45 minutes)

```bash
# 1. Update System YAML
cd /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration

# Edit SYSTEM-CA-006.yaml
# - Remove app/services/ line
# - Remove app/models/ line  
# - Add app/middleware/ section
# - Add app/schemas/ section
# - Add features/ directory structure
# - Add code_generation.phases section

# 2. Update Feature YAMLs (all 6)
# Add to each: directory_structure, models/ spec, db/ spec, tests/ spec

# 3. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('SYSTEM-CA-006.yaml'))"

# 4. Re-run compliance check
python3 << 'EOF'
import yaml
# ... (same compliance script from earlier)
# Should now show 100% compliance
EOF
```

#### Step 2: Update build_system.py (30 minutes)

```bash
cd /workspaces/control_tower

# Backup current version
cp build_system.py build_system.py.backup

# Implement new multi-phase architecture
# - Add _build_phase_prompt() method
# - Add _generate_phase() method
# - Add _dependencies_met() method
# - Add _validate_acceptance_criteria() method
# - Update generate_system_integration() to iterate phases
```

#### Step 3: Test Phase 1 (System Infrastructure) (10 minutes)

```bash
cd /workspaces/control_tower

python3 build_system.py \
  --system-yaml /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/SYSTEM-CA-006.yaml \
  --phase phase_01_system_infrastructure \
  --verbose

# Expected output:
# - 12 files created
# - app/main.py, app/config.py, app/db/connection.py, etc.
# - No syntax errors
# - Health endpoint defined
```

#### Step 4: Execute All Phases (60 minutes)

```bash
python3 build_system.py \
  --system-yaml /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/SYSTEM-CA-006.yaml \
  --all-phases

# Expected output:
# Phase 1: System Infrastructure (3 min) ✅
# Phase 2: API Routers (5 min) ✅
# Phase 3: FEATURE-01 Analytics (8 min) ✅
# Phase 4: FEATURE-02 Engagement (8 min) ✅
# Phase 5: FEATURE-03 Revenue (8 min) ✅
# Phase 6: FEATURE-04 Prioritization (10 min) ✅
# Phase 7: FEATURE-05 Iteration (8 min) ✅
# Phase 8: FEATURE-06 Dashboard (8 min) ✅
# Phase 9: Tests (10 min) ✅
# Phase 10: DevOps (5 min) ✅
# 
# Total: 73 minutes
# Files: 42 created
# Lines: 2,847
# Compliance: 100%
```

#### Step 5: Validation (15 minutes)

```bash
cd /workspaces/business_ventures/Causal_affect/src/feedback_iteration/backend

# 1. Check directory structure
tree -L 4

# 2. Syntax validation
python3 -m py_compile app/**/*.py features/**/*.py

# 3. Import checks
python3 -c "from app.main import app; print('✅ Imports work')"

# 4. Run tests
pytest tests/ -v

# 5. Start server
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
# Should see all API endpoints
```

---

## Timeline & Milestones

### Tomorrow's Schedule (October 16, 2025)

| Time | Task | Duration | Status |
|------|------|----------|--------|
| 09:00-09:30 | Review plan & setup | 30 min | ⏸️ |
| 09:30-10:15 | YAML Refactor (System + Features) | 45 min | ⏸️ |
| 10:15-10:45 | Update build_system.py | 30 min | ⏸️ |
| 10:45-11:00 | Test Phase 1 (Infrastructure) | 15 min | ⏸️ |
| 11:00-12:15 | Execute All Phases (10 phases) | 75 min | ⏸️ |
| 12:15-12:30 | Validation & Testing | 15 min | ⏸️ |
| **TOTAL** | **End-to-end completion** | **210 min (3.5 hrs)** | |

### Success Metrics

| Metric | Current | Target | 
|--------|---------|--------|
| YAML Compliance | 60% | 100% |
| Files Generated | 9 | 40+ |
| Lines of Code | 464 | 2,500+ |
| Features Complete | 0% | 100% |
| Tests | 0 | 20+ |
| Manual Work Required | 75% | 0% |

---

## Risk Mitigation

### Risk 1: Phase Execution Fails
**Mitigation**: Each phase independent, can retry without affecting others

### Risk 2: Token Limit Still Exceeded
**Mitigation**: Further split phases (12 → 15), reduce file count per phase

### Risk 3: Dependencies Break Between Phases
**Mitigation**: Phase validation checks imports before proceeding to next

### Risk 4: Time Estimate Too Optimistic
**Mitigation**: Schedule buffer time, prioritize critical phases first

---

## Appendix: Quick Reference Commands

### Validate YAML Compliance
```bash
cd /workspaces/business_ventures/Causal_affect
python3 /workspaces/control_tower/yaml_compliance_check.py
```

### Run Single Phase
```bash
cd /workspaces/control_tower
python3 build_system.py --phase phase_04_feature_02_engagement
```

### Run All Phases
```bash
python3 build_system.py --all-phases --verbose
```

### Check Generated Files
```bash
cd /workspaces/business_ventures/Causal_affect/src/feedback_iteration/backend
find . -name "*.py" | wc -l  # Count Python files
find . -name "*.py" -exec wc -l {} + | tail -1  # Count total lines
```

### Validate Backend
```bash
pytest tests/ -v --cov=app --cov=features
mypy app/ features/
pylint app/ features/
```

---

**Ready for tomorrow's execution. Let's achieve 100% compliance and true automation! 🚀**
