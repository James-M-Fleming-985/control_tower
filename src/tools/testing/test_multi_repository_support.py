#!/usr/bin/env python3
"""
Multi-Repository Support Tests for Requirements Parser - TR-DA-003

Tests to ensure the parser works across all repository types and requirement templates
Following TDD methodology for comprehensive template validation
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from data_access.requirements_parser import RequirementsParser, ParsedRequirement
from data_access.requirements_models import ProjectType, RequirementType


class TestMultiRepositorySupport:
    """Test suite for multi-repository requirement parsing support"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = RequirementsParser()
        
        # Sample content from different templates
        self.feature_application_content = '''# 🎯 FEATURE REQUIREMENT TEMPLATE - APPLICATION PROJECT

**Requirement ID**: FEA-APP-PORTFOLIO-001  
**Requirement Type**: Application Feature  
**Level**: 4 (Feature)  
**Parent System**: Portfolio Management  
**Created**: 2025-09-14  
**Last Updated**: 2025-09-14  
**Status**: Active

## ⏱️ TIMELINE MANAGEMENT

**Duration**: 10 days  
**Due Date**: 2025-09-24  
**Start Date**: 2025-09-14  
**Priority**: High  
**Effort Estimate**: 8 person-days  
**Dependencies**: Authentication System  
**Progress**: 25% - Initial analysis complete

## 🎯 FEATURE DEFINITION

### **Feature Overview**
Portfolio rebalancing automation for investment management.

### **Acceptance Criteria**
- [x] **AC-001**: User can set target allocations
- [ ] **AC-002**: System calculates rebalancing trades
- [ ] **AC-003**: Automated trade execution

### **Layer Implementation**
**Target Layer**: Business Logic Layer
**Integration Points**: Trading APIs, portfolio data
'''

        self.milestone_delivery_content = '''# 🎯 MILESTONE REQUIREMENT TEMPLATE - DELIVERY PROJECT

**Requirement ID**: MIL-DEL-DATABASE-001  
**Requirement Type**: Delivery Milestone  
**Level**: 4 (Milestone)  
**Parent Workpackage**: Data Migration  
**Created**: 2025-09-14  
**Last Updated**: 2025-09-14  
**Status**: In Progress

## ⏱️ TIMELINE MANAGEMENT

**Duration**: 5 days  
**Due Date**: 2025-09-19  
**Start Date**: 2025-09-15  
**Priority**: Critical  
**Effort Estimate**: 12 person-days  
**Dependencies**: Schema Design Complete  
**Progress**: 60% - Migration scripts ready

## 🎯 MILESTONE DEFINITION

### **Milestone Overview**
Complete migration of legacy database to new schema.

### **Acceptance Criteria**
- [x] **AC-001**: All tables migrated successfully
- [ ] **AC-002**: Data integrity validation complete
- [ ] **AC-003**: Performance benchmarks met
'''

        self.layer_application_content = '''# ⚙️ LAYER REQUIREMENT TEMPLATE - APPLICATION PROJECT

**Requirement ID**: LAY-APP-DATAACCESS-001  
**Requirement Type**: Application Layer  
**Level**: 5 (Layer)  
**Parent Feature**: Portfolio Analytics  
**Created**: 2025-09-14  
**Last Updated**: 2025-09-14  
**Status**: Complete

## ⏱️ TIMELINE MANAGEMENT

**Duration**: 3 days  
**Due Date**: 2025-09-17  
**Start Date**: 2025-09-14  
**Priority**: Medium  
**Effort Estimate**: 4 person-days  
**Dependencies**: Database Schema  
**Progress**: 100% - Implementation complete

## ⚙️ LAYER DEFINITION

### **Layer Overview**
Data access layer for portfolio management system.

### **Acceptance Criteria**
- [x] **AC-001**: Repository pattern implemented
- [x] **AC-002**: Connection pooling configured
- [x] **AC-003**: Caching layer optimized
'''

    def test_parse_feature_application_template(self):
        """Test parsing Feature Application template format"""
        result = self.parser.parse_markdown_content(self.feature_application_content)
        
        assert result.requirement_id == "FEA-APP-PORTFOLIO-001"
        assert result.requirement_type == "Application Feature"
        assert result.level == 4
        assert result.parent_system == "Portfolio Management"
        assert result.status == "Active"
        assert result.project_type == ProjectType.APPLICATION
        assert result.priority == "High"
        assert result.effort_estimate == "8 person-days"
        assert len(result.acceptance_criteria) == 3
        assert result.get_target_layer() == "Business Logic"

    def test_parse_milestone_delivery_template(self):
        """Test parsing Milestone Delivery template format"""
        result = self.parser.parse_markdown_content(self.milestone_delivery_content)
        
        assert result.requirement_id == "MIL-DEL-DATABASE-001"
        assert result.requirement_type == "Delivery Milestone"
        assert result.level == 4
        assert result.status == "In Progress"
        assert result.project_type == ProjectType.STANDARD_DELIVERY
        assert result.priority == "Critical"
        assert result.effort_estimate == "12 person-days"
        assert len(result.acceptance_criteria) == 3

    def test_parse_layer_application_template(self):
        """Test parsing Layer Application template format"""
        result = self.parser.parse_markdown_content(self.layer_application_content)
        
        assert result.requirement_id == "LAY-APP-DATAACCESS-001"
        assert result.requirement_type == "Application Layer"
        assert result.level == 5
        assert result.status == "Complete"
        assert result.project_type == ProjectType.APPLICATION
        assert result.priority == "Medium"
        assert result.effort_estimate == "4 person-days"
        assert len(result.acceptance_criteria) == 3

    def test_detect_requirement_type_from_templates(self):
        """Test that parser correctly identifies requirement types from template formats"""
        # Feature Application
        feature_result = self.parser.parse_markdown_content(self.feature_application_content)
        assert feature_result.requirement_type_enum == RequirementType.FEATURE
        
        # Milestone Delivery  
        milestone_result = self.parser.parse_markdown_content(self.milestone_delivery_content)
        assert milestone_result.requirement_type_enum == RequirementType.MILESTONE
        
        # Layer Application
        layer_result = self.parser.parse_markdown_content(self.layer_application_content)
        assert layer_result.requirement_type_enum == RequirementType.LAYER

    def test_detect_project_type_from_templates(self):
        """Test that parser correctly identifies project types from template formats"""
        # Application templates should be PROJECT_TYPE.APPLICATION
        feature_result = self.parser.parse_markdown_content(self.feature_application_content)
        assert feature_result.project_type == ProjectType.APPLICATION
        
        layer_result = self.parser.parse_markdown_content(self.layer_application_content)
        assert layer_result.project_type == ProjectType.APPLICATION
        
        # Delivery templates should be PROJECT_TYPE.STANDARD_DELIVERY
        milestone_result = self.parser.parse_markdown_content(self.milestone_delivery_content)
        assert milestone_result.project_type == ProjectType.STANDARD_DELIVERY

    def test_parse_all_template_formats_consistently(self):
        """Test that all template formats parse consistently with required fields"""
        templates = [
            ("Feature Application", self.feature_application_content),
            ("Milestone Delivery", self.milestone_delivery_content), 
            ("Layer Application", self.layer_application_content)
        ]
        
        for template_name, content in templates:
            result = self.parser.parse_markdown_content(content)
            
            # All templates should have these core fields
            assert result.requirement_id is not None, f"{template_name} missing requirement_id"
            assert result.requirement_type is not None, f"{template_name} missing requirement_type"
            assert result.level is not None, f"{template_name} missing level"
            assert result.status is not None, f"{template_name} missing status"
            assert result.priority is not None, f"{template_name} missing priority"
            assert result.due_date is not None, f"{template_name} missing due_date"
            assert result.effort_estimate is not None, f"{template_name} missing effort_estimate"
            assert result.acceptance_criteria is not None, f"{template_name} missing acceptance_criteria"
            assert len(result.acceptance_criteria) > 0, f"{template_name} has no acceptance criteria"

    def test_repository_path_handling(self):
        """Test that parser handles different repository path structures"""
        # Test various repository path patterns
        repo_paths = [
            "/workspaces/control_tower/cloned_repos/investment_strategy/projects/PROJECT-001/features/FEATURE-001.md",
            "/workspaces/control_tower/cloned_repos/financial_security/workpackages/WP-002/milestones/MILESTONE-001.md",
            "/workspaces/control_tower/cloned_repos/business_ventures/systems/SYSTEM-003/layers/LAYER-001.md",
            "/workspaces/control_tower/cloned_repos/professional_excellence/tasks/TASK-004.md"
        ]
        
        for repo_path in repo_paths:
            # Parser should handle all path formats without errors
            result = self.parser.parse_markdown_content(self.feature_application_content, repo_path)
            assert result.file_path == repo_path
            # Should still parse content correctly regardless of path
            assert result.requirement_id == "FEA-APP-PORTFOLIO-001"

    def test_cross_repository_compatibility(self):
        """Test that requirements from different repositories are compatible"""
        # Parse requirements from different template types
        feature_req = self.parser.parse_markdown_content(self.feature_application_content)
        milestone_req = self.parser.parse_markdown_content(self.milestone_delivery_content)
        layer_req = self.parser.parse_markdown_content(self.layer_application_content)
        
        # All should serialize/deserialize consistently
        feature_json = feature_req.to_json()
        milestone_json = milestone_req.to_json()
        layer_json = layer_req.to_json()
        
        # Should all be valid JSON
        import json
        assert json.loads(feature_json)
        assert json.loads(milestone_json)
        assert json.loads(layer_json)
        
        # All should have consistent field structure
        feature_dict = json.loads(feature_json)
        milestone_dict = json.loads(milestone_json)
        layer_dict = json.loads(layer_json)
        
        # Common fields should exist in all
        common_fields = ['id', 'title', 'description', 'project_type', 'requirement_type']
        for field in common_fields:
            assert field in feature_dict, f"Feature missing {field}"
            assert field in milestone_dict, f"Milestone missing {field}"
            assert field in layer_dict, f"Layer missing {field}"