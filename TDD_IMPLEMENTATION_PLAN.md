"""
Test-Driven Development Plan: Work Discovery Engine

FEATURE LEVEL REQUIREMENT:
FR-006: Smart Work Discovery Engine
- User runs `make what-next` 
- System shows prioritized work with clear hierarchical context
- Application Projects show: Layer/Feature → System → Project → Repository
- Standard Delivery shows: Task/Milestone → Workpackage → Project → Repository

TESTING PYRAMID LAYERS:

Layer 1 (Unit Tests - RED/GREEN/REFACTOR):
├── test_repository_scanner.py
├── test_priority_calculator.py  
├── test_work_item.py
└── test_clean_output_formatter.py

Layer 2 (Integration Tests):
├── test_discovery_integration.py
└── test_makefile_integration.py

Layer 3 (E2E Tests):
└── test_user_journey_what_next.py

TDD CYCLES:

CYCLE 1: Work Item Model (Unit Layer)
RED:   Write failing test for WorkItem creation
GREEN: Implement minimal WorkItem class  
REFACTOR: Add properties and validation

CYCLE 2: Repository Scanner (Unit Layer)
RED:   Write failing test for scanning single repository
GREEN: Implement basic file scanning
REFACTOR: Add requirement level parsing

CYCLE 3: Priority Calculator (Unit Layer)  
RED:   Write failing test for priority scoring
GREEN: Implement basic urgency calculation
REFACTOR: Add business value, effort, dependencies

CYCLE 4: Output Formatter (Unit Layer)
RED:   Write failing test for clean terminal output
GREEN: Implement basic status messages
REFACTOR: Add hierarchical display formatting

CYCLE 5: Discovery Integration (Integration Layer)
RED:   Write failing test for scanner→calculator→formatter flow
GREEN: Wire components together
REFACTOR: Add error handling and logging

CYCLE 6: Makefile Integration (Integration Layer)
RED:   Write failing test for `make what-next` command
GREEN: Create basic makefile target
REFACTOR: Add parameter passing and output formatting

CYCLE 7: User Journey (E2E Layer)
RED:   Write failing test for complete user workflow
GREEN: Implement end-to-end discovery flow
REFACTOR: Polish UX and performance

VALIDATION AGAINST REQUIREMENTS:
- Each cycle validates against corresponding FR requirement
- Integration tests validate against SR requirements  
- E2E tests validate against overall system requirements
"""