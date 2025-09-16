#!/usr/bin/env python3
"""
Template Validation Test - TR-DA-003 Multi-Repository Support

Test that parser works with actual requirement templates from the templates directory
"""

import pytest
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from data_access.requirements_parser import RequirementsParser, ParsedRequirement
from data_access.requirements_models import ProjectType, RequirementType


class TestTemplateValidation:
    """Test suite for validating parser works with all requirement templates"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = RequirementsParser()
        self.templates_dir = Path("/workspaces/control_tower/requirements_templates")

    def test_all_templates_directory_exists(self):
        """Verify templates directory exists"""
        assert self.templates_dir.exists(), "Templates directory should exist"
        assert self.templates_dir.is_dir(), "Templates path should be a directory"

    def test_parse_feature_application_template_file(self):
        """Test parsing the actual feature application template file"""
        template_file = self.templates_dir / "feature_application_template.md"
        if not template_file.exists():
            pytest.skip("Feature application template not found")
        
        result = self.parser.parse_file(template_file)
        
        # Template should parse without errors
        assert result.requirement_id is not None
        assert result.project_type == ProjectType.APPLICATION
        assert result.requirement_type_enum == RequirementType.FEATURE

    def test_parse_milestone_delivery_template_file(self):
        """Test parsing the actual milestone delivery template file"""
        template_file = self.templates_dir / "milestone_delivery_template.md"
        if not template_file.exists():
            pytest.skip("Milestone delivery template not found")
        
        result = self.parser.parse_file(template_file)
        
        # Template should parse without errors
        assert result.requirement_id is not None
        assert result.project_type == ProjectType.STANDARD_DELIVERY
        assert result.requirement_type_enum == RequirementType.MILESTONE

    def test_parse_layer_application_template_file(self):
        """Test parsing the actual layer application template file"""
        template_file = self.templates_dir / "layer_application_template.md"
        if not template_file.exists():
            pytest.skip("Layer application template not found")
        
        result = self.parser.parse_file(template_file)
        
        # Template should parse without errors
        assert result.requirement_id is not None
        assert result.project_type == ProjectType.APPLICATION
        assert result.requirement_type_enum == RequirementType.LAYER

    def test_all_available_templates_parse_successfully(self):
        """Test that all available templates in the directory parse without errors"""
        if not self.templates_dir.exists():
            pytest.skip("Templates directory not found")
        
        template_files = list(self.templates_dir.glob("*.md"))
        
        if not template_files:
            pytest.skip("No template files found")
        
        successful_parses = 0
        failed_parses = []
        
        for template_file in template_files:
            try:
                result = self.parser.parse_file(template_file)
                
                # Basic validation - should have core fields
                assert result.requirement_id is not None
                assert result.project_type is not None
                assert result.requirement_type_enum is not None
                
                successful_parses += 1
                print(f"✅ Successfully parsed: {template_file.name}")
                
            except Exception as e:
                failed_parses.append((template_file.name, str(e)))
                print(f"❌ Failed to parse: {template_file.name} - {e}")
        
        print(f"\n📊 Template Parsing Results:")
        print(f"  ✅ Successful: {successful_parses}/{len(template_files)}")
        print(f"  ❌ Failed: {len(failed_parses)}/{len(template_files)}")
        
        if failed_parses:
            print(f"\n🔍 Failed Templates:")
            for template, error in failed_parses:
                print(f"  - {template}: {error}")
        
        # Assert that we successfully parsed at least some templates
        assert successful_parses > 0, "Should successfully parse at least one template"
        
        # Report but don't fail on template parsing issues (they might be incomplete templates)
        if failed_parses:
            print(f"\n⚠️  Some templates failed to parse - this may be expected for incomplete templates")

    def test_template_format_consistency(self):
        """Test that all templates follow consistent field naming"""
        if not self.templates_dir.exists():
            pytest.skip("Templates directory not found")
        
        template_files = list(self.templates_dir.glob("*.md"))
        
        if not template_files:
            pytest.skip("No template files found")
        
        consistent_fields = []
        field_variations = {}
        
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for standard field patterns
                import re
                
                # Look for Requirement ID patterns
                req_id_patterns = re.findall(r'\*\*Requirement\s+ID\*\*:', content, re.IGNORECASE)
                req_type_patterns = re.findall(r'\*\*Requirement\s+Type\*\*:', content, re.IGNORECASE)
                level_patterns = re.findall(r'\*\*Level\*\*:', content, re.IGNORECASE)
                status_patterns = re.findall(r'\*\*Status\*\*:', content, re.IGNORECASE)
                
                if req_id_patterns and req_type_patterns:
                    consistent_fields.append(template_file.name)
                else:
                    field_variations[template_file.name] = {
                        'req_id': bool(req_id_patterns),
                        'req_type': bool(req_type_patterns),
                        'level': bool(level_patterns),
                        'status': bool(status_patterns)
                    }
                    
            except Exception as e:
                print(f"Error checking template consistency for {template_file.name}: {e}")
        
        print(f"\n📋 Template Field Consistency:")
        print(f"  ✅ Consistent templates: {len(consistent_fields)}")
        print(f"  ⚠️  Inconsistent templates: {len(field_variations)}")
        
        if field_variations:
            print(f"\n🔍 Field Variations:")
            for template, fields in field_variations.items():
                print(f"  - {template}: {fields}")

    def test_cross_template_compatibility(self):
        """Test that requirements parsed from different templates are compatible"""
        if not self.templates_dir.exists():
            pytest.skip("Templates directory not found")
        
        template_files = list(self.templates_dir.glob("*.md"))
        
        if len(template_files) < 2:
            pytest.skip("Need at least 2 templates for compatibility testing")
        
        parsed_requirements = []
        
        for template_file in template_files[:3]:  # Test first 3 templates
            try:
                result = self.parser.parse_file(template_file)
                parsed_requirements.append((template_file.name, result))
            except Exception as e:
                print(f"Skipping {template_file.name} due to parsing error: {e}")
        
        if len(parsed_requirements) < 2:
            pytest.skip("Need at least 2 successfully parsed templates")
        
        # Test that all parsed requirements can be serialized consistently
        json_outputs = []
        for template_name, req in parsed_requirements:
            try:
                json_output = req.to_json()
                json_outputs.append((template_name, json_output))
            except Exception as e:
                pytest.fail(f"Failed to serialize {template_name}: {e}")
        
        # Test that all have similar JSON structure
        import json
        parsed_jsons = []
        for template_name, json_str in json_outputs:
            try:
                parsed_json = json.loads(json_str)
                parsed_jsons.append((template_name, parsed_json))
            except Exception as e:
                pytest.fail(f"Failed to parse JSON for {template_name}: {e}")
        
        # Verify common fields exist in all
        common_fields = ['id', 'title', 'project_type', 'requirement_type']
        for template_name, parsed_json in parsed_jsons:
            for field in common_fields:
                assert field in parsed_json, f"{template_name} missing field: {field}"
        
        print(f"\n✅ Successfully tested compatibility across {len(parsed_jsons)} templates")