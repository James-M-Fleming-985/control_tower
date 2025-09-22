#!/usr/bin/env python3
"""
Integration Layer Package Initialization

Exports core Integration Layer classes for LAYER-003-01-02-004.

Created: 2025-09-18
Phase: TDD GREEN phase
"""

from .workflow_integration_coordinator import (
    WorkflowIntegrationCoordinator,
    StageGateWorkflowCoordinator,
    TestFrameworkIntegrator,
    WorkflowOrchestrator,
    ExternalSystemEventCoordinator
)

from .integration_models import (
    WorkflowEvent,
    StageGateStatus,
    IntegrationResult,
    ExternalSystemConfig,
    WorkflowState,
    WorkflowPhase,
    StageGateResult,
    IntegrationStatus,
    SystemEventOrder,
    CoordinationRequest,
    PerformanceMetrics,
    SecurityConfiguration
)

from .external_api_client import (
    ExternalAPIClient,
    GitIntegrationClient,
    PyTestIntegrationClient,
    CICDIntegrationClient
)

__all__ = [
    # Core coordinators
    "WorkflowIntegrationCoordinator",
    "StageGateWorkflowCoordinator", 
    "TestFrameworkIntegrator",
    "WorkflowOrchestrator",
    "ExternalSystemEventCoordinator",
    
    # Data models
    "WorkflowEvent",
    "StageGateStatus",
    "IntegrationResult",
    "ExternalSystemConfig",
    "WorkflowState",
    "WorkflowPhase",
    "StageGateResult",
    "IntegrationStatus",
    "SystemEventOrder",
    "CoordinationRequest",
    "PerformanceMetrics",
    "SecurityConfiguration",
    
    # API clients
    "ExternalAPIClient",
    "GitIntegrationClient",
    "PyTestIntegrationClient",
    "CICDIntegrationClient"
]

__version__ = "1.0.0"
__author__ = "TDD Enforcer System"
__description__ = "Integration Layer for TDD workflow coordination and external system integration"