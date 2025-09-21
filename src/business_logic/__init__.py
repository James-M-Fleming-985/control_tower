"""
Business Logic Package for LAYER-003-01-02-002 Business Logic Requirements
===========================================================================

This package implements the complete business logic layer including:
- TDD cycle enforcement and phase validation
- Stage gate management and compliance verification  
- Performance optimization and reliability components
- Security management and testability frameworks
"""

# Original TDD cycle enforcement components
from .tdd_cycle_enforcer import TDDCycleEnforcer
from .phase_enforcement import (
    RedPhaseEnforcer,
    GreenPhaseEnforcer,
    RefactorPhaseEnforcer,
    PhaseEnforcementResult
)
from .stage_gate_manager import StageGateManager, StageGateDecision
from .compliance_validator import ComplianceValidator, ComplianceResult

# New business logic components for LAYER-003-01-02-002
# BLR - Functional Requirements
from .verification_algorithms import TestVerificationAlgorithm, TestGenerationVerifier
from .stage_gate_validator import StageGateValidator, TDDPhaseController, FailurePreventionSystem
from .tdd_compliance_checker import TDDComplianceChecker, VerificationResultValidator, TDDCycleEnforcer as NewTDDCycleEnforcer
from .test_quality_scorer import TestQualityScorer, QualityAssessmentEngine

# BLRP - Performance Requirements
from .verification_service import (
    VerificationService, BatchVerificationService, HighThroughputVerificationService,
    ConcurrentVerificationProcessor, SustainedVerificationService, MemoryEfficientVerificationService
)
from .verification_cache import VerificationCacheManager, OptimizedVerificationCache

# BLRR - Reliability Requirements
from .error_recovery import ErrorRecoverySystem, AvailabilityMonitor, BusinessLogicClustering

# BLRS - Security Requirements
from .security_manager import AccessControlManager, EncryptionService, AuthenticationService

# BLRT - Testability Requirements
from .testability_framework import CoverageAnalyzer, IntegrationTestRunner, TestAutomationFramework

__all__ = [
    # Original TDD components
    'TDDCycleEnforcer',
    'RedPhaseEnforcer',
    'GreenPhaseEnforcer', 
    'RefactorPhaseEnforcer',
    'PhaseEnforcementResult',
    'StageGateManager',
    'StageGateDecision',
    'ComplianceValidator',
    'ComplianceResult',
    
    # BLR - Functional Requirements
    'TestVerificationAlgorithm', 'TestGenerationVerifier',
    'StageGateValidator', 'TDDPhaseController', 'FailurePreventionSystem',
    'TDDComplianceChecker', 'VerificationResultValidator', 'NewTDDCycleEnforcer',
    'TestQualityScorer', 'QualityAssessmentEngine',
    
    # BLRP - Performance Requirements
    'VerificationService', 'BatchVerificationService', 'HighThroughputVerificationService',
    'ConcurrentVerificationProcessor', 'SustainedVerificationService', 'MemoryEfficientVerificationService',
    'VerificationCacheManager', 'OptimizedVerificationCache',
    
    # BLRR - Reliability Requirements
    'ErrorRecoverySystem', 'AvailabilityMonitor', 'BusinessLogicClustering',
    
    # BLRS - Security Requirements
    'AccessControlManager', 'EncryptionService', 'AuthenticationService',
    
    # BLRT - Testability Requirements
    'CoverageAnalyzer', 'IntegrationTestRunner', 'TestAutomationFramework'
]

__version__ = '1.0.0'
__author__ = 'TDD Cycle Enforcer Team'