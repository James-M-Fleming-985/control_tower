#!/usr/bin/env python3
"""
Requirements Data Models - TR-DA-003 Implementation

This module defines the data structures for representing parsed requirements
from markdown files. Supports both Application and Standard Delivery project types.

Created: 2025-09-14
Phase: Phase 2A - Data Access Layer
Component: Requirements Analysis Engine
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class ProjectType(Enum):
    """Type of project for requirement parsing"""
    APPLICATION = "application"
    STANDARD_DELIVERY = "standard_delivery"


class RequirementType(Enum):
    """Type of requirement being parsed"""
    FEATURE = "feature"
    MILESTONE = "milestone"
    LAYER = "layer"
    TASK = "task"


@dataclass
class AcceptanceCriterion:
    """Individual acceptance criterion extracted from requirements"""
    id: str
    description: str
    criterion_type: str = "bullet_point"  # bullet_point, given_when_then
    given: Optional[str] = None
    when: Optional[str] = None
    then: Optional[str] = None
    testable: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "description": self.description,
            "criterion_type": self.criterion_type,
            "given": self.given,
            "when": self.when,
            "then": self.then,
            "testable": self.testable
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AcceptanceCriterion':
        """Create from dictionary for JSON deserialization"""
        return cls(**data)


@dataclass
class BusinessRequirement:
    """Business requirement extracted from requirements"""
    id: str
    description: str
    value_statement: Optional[str] = None
    success_metric: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "description": self.description,
            "value_statement": self.value_statement,
            "success_metric": self.success_metric
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessRequirement':
        """Create from dictionary for JSON deserialization"""
        return cls(**data)


@dataclass
class LayerRequirement:
    """Layer-specific requirement for Application projects"""
    layer_name: str  # Business Logic, Data Access, UI, Integration
    description: str
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "layer_name": self.layer_name,
            "description": self.description,
            "acceptance_criteria": [ac.to_dict() for ac in self.acceptance_criteria],
            "dependencies": self.dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayerRequirement':
        """Create from dictionary for JSON deserialization"""
        return cls(
            layer_name=data["layer_name"],
            description=data["description"],
            acceptance_criteria=[AcceptanceCriterion.from_dict(ac) for ac in data["acceptance_criteria"]],
            dependencies=data["dependencies"]
        )


@dataclass
class ParsedRequirement:
    """Complete parsed requirement from a markdown file"""
    # Core metadata matching test expectations
    requirement_id: str = ""
    requirement_type: str = ""
    level: Optional[int] = None
    parent_system: Optional[str] = None
    repository: Optional[str] = None
    status: Optional[str] = None
    created: Optional[str] = None
    
    # Timeline information
    duration: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    effort_estimate: Optional[str] = None
    
    # Content sections
    primary_objective: Optional[str] = None
    acceptance_criteria: List[Dict[str, Any]] = field(default_factory=list)  # Changed to match test format
    layer_implementation: Optional[str] = None
    integration_points: Optional[str] = None
    
    # Test expectations - add missing fields
    component_name: Optional[str] = None
    target_layer: Optional[str] = None
    focus_area: Optional[str] = None
    
    # Original fields for compatibility
    id: str = ""
    title: str = ""
    description: str = ""
    file_path: str = ""
    project_type: ProjectType = ProjectType.APPLICATION
    requirement_type_enum: RequirementType = RequirementType.FEATURE
    
    # Extended content sections
    business_requirements: List[BusinessRequirement] = field(default_factory=list)
    layer_requirements: List[LayerRequirement] = field(default_factory=list)
    
    # Detailed requirement tracking by type
    functional_requirements: List[Dict[str, Any]] = field(default_factory=list)
    business_rules: List[Dict[str, Any]] = field(default_factory=list) 
    performance_requirements: List[Dict[str, Any]] = field(default_factory=list)
    quality_requirements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Additional metadata
    dependencies: List[str] = field(default_factory=list)
    parent_requirements: List[str] = field(default_factory=list)
    child_requirements: List[str] = field(default_factory=list)
    
    # Validation
    is_complete: bool = False
    validation_errors: List[str] = field(default_factory=list)
    validation_result: Optional['ValidationResult'] = None
    
    def __post_init__(self):
        """Ensure compatibility between old and new field names"""
        # Sync id and requirement_id
        if self.requirement_id and not self.id:
            self.id = self.requirement_id
        elif self.id and not self.requirement_id:
            self.requirement_id = self.id
    
    def get_target_layer(self) -> Optional[str]:
        """Get the primary layer this requirement targets for Application projects"""
        # First try to get from layer_implementation field (new structured format)
        if self.layer_implementation:
            layer_text = self.layer_implementation.strip()
            # Extract just the layer name from "Integration Layer" format
            for layer in ["Integration", "Business Logic", "Data Access", "UI"]:
                if layer in layer_text:
                    return layer
            return layer_text
        
        # Fallback to layer_requirements (old format)
        if self.project_type == ProjectType.APPLICATION and self.layer_requirements:
            return self.layer_requirements[0].layer_name
        
        return None
    
    def get_testable_criteria(self) -> List[AcceptanceCriterion]:
        """Get all testable acceptance criteria"""
        # Handle both old format (AcceptanceCriterion objects) and new format (dicts)
        if not self.acceptance_criteria:
            return []
        
        # Check if it's the new dict format
        if self.acceptance_criteria and isinstance(self.acceptance_criteria[0], dict):
            # Convert dict format to AcceptanceCriterion objects for compatibility
            return [
                AcceptanceCriterion(
                    id=ac.get("id", f"AC-{i:03d}"),
                    description=ac.get("description", ""),
                    testable=ac.get("completed", True)  # Assume testable if completed is tracked
                )
                for i, ac in enumerate(self.acceptance_criteria)
            ]
        else:
            # Old format with AcceptanceCriterion objects
            return [ac for ac in self.acceptance_criteria if ac.testable]
    
    def validate(self) -> bool:
        """Validate requirement completeness and structure"""
        self.validation_errors.clear()
        
        # Check required fields
        if not self.id:
            self.validation_errors.append("Missing requirement ID")
        if not self.title:
            self.validation_errors.append("Missing requirement title")
        if not self.description:
            self.validation_errors.append("Missing requirement description")
        if not self.acceptance_criteria:
            self.validation_errors.append("No acceptance criteria defined")
        
        # Check project-type specific requirements
        if self.project_type == ProjectType.APPLICATION:
            if not self.layer_requirements:
                self.validation_errors.append("Application projects must define layer requirements")
        
        # Check testable criteria
        testable_count = len(self.get_testable_criteria())
        if testable_count == 0:
            self.validation_errors.append("No testable acceptance criteria found")
        
        self.is_complete = len(self.validation_errors) == 0
        return self.is_complete
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        # Handle acceptance criteria - check if already dicts or AcceptanceCriterion objects
        ac_list = []
        for ac in self.acceptance_criteria:
            if isinstance(ac, dict):
                ac_list.append(ac)  # Already a dict
            elif hasattr(ac, 'to_dict'):
                ac_list.append(ac.to_dict())  # AcceptanceCriterion object
            else:
                # Fallback for other formats
                ac_list.append(str(ac))
        
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "project_type": self.project_type.value if hasattr(self.project_type, 'value') else str(self.project_type),
            "requirement_type": self.requirement_type_enum.value if hasattr(self.requirement_type_enum, 'value') else str(self.requirement_type_enum),
            "acceptance_criteria": ac_list,
            "business_requirements": [br.to_dict() for br in self.business_requirements],
            "layer_requirements": [lr.to_dict() for lr in self.layer_requirements],
            "priority": self.priority,
            "effort_estimate": self.effort_estimate,
            "due_date": self.due_date,
            "dependencies": self.dependencies,
            "parent_requirements": self.parent_requirements,
            "child_requirements": self.child_requirements,
            "is_complete": self.is_complete,
            "validation_errors": self.validation_errors
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedRequirement':
        """Create from dictionary for JSON deserialization"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            file_path=data["file_path"],
            project_type=ProjectType(data["project_type"]),
            requirement_type=RequirementType(data["requirement_type"]),
            acceptance_criteria=[AcceptanceCriterion.from_dict(ac) for ac in data["acceptance_criteria"]],
            business_requirements=[BusinessRequirement.from_dict(br) for br in data["business_requirements"]],
            layer_requirements=[LayerRequirement.from_dict(lr) for lr in data["layer_requirements"]],
            priority=data.get("priority"),
            effort_estimate=data.get("effort_estimate"),
            due_date=data.get("due_date"),
            dependencies=data.get("dependencies", []),
            parent_requirements=data.get("parent_requirements", []),
            child_requirements=data.get("child_requirements", []),
            is_complete=data.get("is_complete", False),
            validation_errors=data.get("validation_errors", [])
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ParsedRequirement':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class RequirementsTraceability:
    """Traceability matrix for requirements coverage"""
    requirement_id: str
    acceptance_criteria_count: int
    generated_tests_count: int
    test_case_mappings: Dict[str, List[str]] = field(default_factory=dict)  # criterion_id -> test_names
    coverage_percentage: float = 0.0
    missing_coverage: List[str] = field(default_factory=list)
    
    def calculate_coverage(self) -> float:
        """Calculate test coverage percentage"""
        if self.acceptance_criteria_count == 0:
            self.coverage_percentage = 0.0
        else:
            covered_criteria = len([k for k, v in self.test_case_mappings.items() if v])
            self.coverage_percentage = (covered_criteria / self.acceptance_criteria_count) * 100
        return self.coverage_percentage
    
    def get_missing_coverage(self) -> List[str]:
        """Get list of acceptance criteria without test coverage"""
        self.missing_coverage = [k for k, v in self.test_case_mappings.items() if not v]
        return self.missing_coverage
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "requirement_id": self.requirement_id,
            "acceptance_criteria_count": self.acceptance_criteria_count,
            "generated_tests_count": self.generated_tests_count,
            "test_case_mappings": self.test_case_mappings,
            "coverage_percentage": self.coverage_percentage,
            "missing_coverage": self.missing_coverage
        }