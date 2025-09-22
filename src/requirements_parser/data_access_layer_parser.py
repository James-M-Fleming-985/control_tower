"""
Data Access Layer Requirements Parser
LAYER-003-01-02-001 Requirements Analysis

Parses the layer requirements document to extract specific functional and quality requirements
for Test Generation Verification System Data Access Layer.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FunctionalRequirement:
    """Represents a functional requirement"""
    id: str
    description: str
    category: str
    priority: str
    verification_method: str


@dataclass
class QualityRequirement:
    """Represents a quality/performance requirement"""
    id: str
    metric: str
    target: str
    measurement_method: str
    category: str  # performance, reliability, security


@dataclass
class LayerRequirements:
    """Complete layer requirements"""
    layer_id: str
    layer_name: str
    functional_requirements: List[FunctionalRequirement]
    quality_requirements: List[QualityRequirement]
    dependencies: List[str]
    interfaces: Dict[str, List[str]]


class DataAccessLayerRequirementsParser:
    """Parser for Data Access Layer requirements document"""
    
    def __init__(self, requirements_file: str):
        self.requirements_file = Path(requirements_file)
        self.content = self._load_content()
    
    def _load_content(self) -> str:
        """Load requirements document content"""
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise FileNotFoundError(f"Could not load requirements file: {e}")
    
    def parse_requirements(self) -> LayerRequirements:
        """Parse complete layer requirements"""
        return LayerRequirements(
            layer_id=self._extract_layer_id(),
            layer_name=self._extract_layer_name(),
            functional_requirements=self._extract_functional_requirements(),
            quality_requirements=self._extract_quality_requirements(),
            dependencies=self._extract_dependencies(),
            interfaces=self._extract_interfaces()
        )
    
    def _extract_layer_id(self) -> str:
        """Extract layer ID from document"""
        match = re.search(r'\*\*Requirement ID\*\*:\s*([A-Z0-9-]+)', self.content)
        return match.group(1) if match else "LAY-003-01-02-001"
    
    def _extract_layer_name(self) -> str:
        """Extract layer name from document"""
        match = re.search(r'# ⚙️ LAYER REQUIREMENT - (.+)', self.content)
        return match.group(1) if match else "DATA ACCESS LAYER"
    
    def _extract_functional_requirements(self) -> List[FunctionalRequirement]:
        """Extract functional requirements from Core Functionality section"""
        functional_reqs = []
        
        # Extract primary functions
        functions_section = self._extract_section("Primary Functions:")
        if functions_section:
            function_matches = re.findall(
                r'├── Function (\d+): (.+?)(?=├──|\└──|\n\n|$)', 
                functions_section, re.DOTALL
            )
            
            for func_id, description in function_matches:
                functional_reqs.append(FunctionalRequirement(
                    id=f"F{func_id}",
                    description=description.strip(),
                    category="core_functionality",
                    priority="high",
                    verification_method="automated_testing"
                ))
        
        # Extract data processing requirements
        processing_section = self._extract_section("Data Processing:")
        if processing_section:
            processing_matches = re.findall(
                r'├── ([^:]+): (.+?)(?=├──|\└──|\n\n|$)', 
                processing_section, re.DOTALL
            )
            
            for i, (category, description) in enumerate(processing_matches, 5):
                functional_reqs.append(FunctionalRequirement(
                    id=f"F{i}",
                    description=f"{category}: {description.strip()}",
                    category="data_processing",
                    priority="medium",
                    verification_method="unit_testing"
                ))
        
        # Extract integration requirements
        integration_section = self._extract_section("Integration Points:")
        if integration_section:
            integration_matches = re.findall(
                r'├── ([^:]+): (.+?)(?=├──|\└──|\n\n|$)', 
                integration_section, re.DOTALL
            )
            
            for i, (category, description) in enumerate(integration_matches, 9):
                functional_reqs.append(FunctionalRequirement(
                    id=f"F{i}",
                    description=f"{category}: {description.strip()}",
                    category="integration",
                    priority="high",
                    verification_method="integration_testing"
                ))
        
        return functional_reqs
    
    def _extract_quality_requirements(self) -> List[QualityRequirement]:
        """Extract quality/performance requirements"""
        quality_reqs = []
        
        # Extract performance requirements
        performance_section = self._extract_section("Performance:")
        if performance_section:
            perf_matches = re.findall(
                r'├── ([^:]+): (.+?)(?=├──|\└──|\n\n|$)', 
                performance_section, re.DOTALL
            )
            
            for i, (metric, target) in enumerate(perf_matches, 1):
                quality_reqs.append(QualityRequirement(
                    id=f"Q{i}",
                    metric=metric.strip(),
                    target=target.strip(),
                    measurement_method="performance_testing",
                    category="performance"
                ))
        
        # Extract reliability requirements
        reliability_section = self._extract_section("Reliability:")
        if reliability_section:
            rel_matches = re.findall(
                r'├── ([^:]+): (.+?)(?=├──|\└──|\n\n|$)', 
                reliability_section, re.DOTALL
            )
            
            for i, (metric, target) in enumerate(rel_matches, 5):
                quality_reqs.append(QualityRequirement(
                    id=f"Q{i}",
                    metric=metric.strip(),
                    target=target.strip(),
                    measurement_method="reliability_testing",
                    category="reliability"
                ))
        
        # Extract security requirements
        security_section = self._extract_section("Security:")
        if security_section:
            sec_matches = re.findall(
                r'├── ([^:]+): (.+?)(?=├──|\└──|\n\n|$)', 
                security_section, re.DOTALL
            )
            
            for i, (metric, target) in enumerate(sec_matches, 9):
                quality_reqs.append(QualityRequirement(
                    id=f"Q{i}",
                    metric=metric.strip(),
                    target=target.strip(),
                    measurement_method="security_testing",
                    category="security"
                ))
        
        return quality_reqs
    
    def _extract_dependencies(self) -> List[str]:
        """Extract layer dependencies"""
        dependencies = []
        
        # Look for dependencies in various sections
        dep_patterns = [
            r'\*\*Dependencies\*\*:\s*(.+?)(?=\n\*\*|\n\n|$)',
            r'└── Dependencies:\s*(.+?)(?=\n\n|$)'
        ]
        
        for pattern in dep_patterns:
            matches = re.findall(pattern, self.content, re.DOTALL)
            for match in matches:
                # Split on common separators
                deps = re.split(r'[,;]\s*', match.strip())
                dependencies.extend([dep.strip() for dep in deps if dep.strip()])
        
        return list(set(dependencies))  # Remove duplicates
    
    def _extract_interfaces(self) -> Dict[str, List[str]]:
        """Extract interface definitions"""
        interfaces = {"input": [], "output": []}
        
        # Extract input interfaces
        input_section = self._extract_section("Input Interfaces:")
        if input_section:
            input_matches = re.findall(
                r'├── ([^:]+): (.+?)(?=├──|\└──|\n\n|$)', 
                input_section, re.DOTALL
            )
            interfaces["input"] = [f"{name}: {desc.strip()}" for name, desc in input_matches]
        
        # Extract output interfaces
        output_section = self._extract_section("Output Interfaces:")
        if output_section:
            output_matches = re.findall(
                r'├── ([^:]+): (.+?)(?=├──|\└──|\n\n|$)', 
                output_section, re.DOTALL
            )
            interfaces["output"] = [f"{name}: {desc.strip()}" for name, desc in output_matches]
        
        return interfaces
    
    def _extract_section(self, section_header: str) -> str:
        """Extract content of a specific section"""
        # Look for section header and extract content until next major section
        pattern = rf'{re.escape(section_header)}(.+?)(?=```|\n##|\n###|\n\*\*[A-Z]|\Z)'
        match = re.search(pattern, self.content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def generate_test_specifications(self) -> Dict[str, Any]:
        """Generate test specifications based on parsed requirements"""
        requirements = self.parse_requirements()
        
        test_specs = {
            "layer_id": requirements.layer_id,
            "functional_tests": [],
            "quality_tests": [],
            "integration_tests": [],
            "coverage_target": 75  # B grade target
        }
        
        # Generate functional test specifications
        for req in requirements.functional_requirements:
            test_specs["functional_tests"].append({
                "requirement_id": req.id,
                "test_name": f"test_{req.id.lower()}_{req.category}",
                "description": req.description,
                "verification_method": req.verification_method,
                "priority": req.priority,
                "test_type": "unit" if req.category == "core_functionality" else "integration"
            })
        
        # Generate quality test specifications
        for req in requirements.quality_requirements:
            test_specs["quality_tests"].append({
                "requirement_id": req.id,
                "test_name": f"test_{req.id.lower()}_{req.category}",
                "metric": req.metric,
                "target": req.target,
                "measurement_method": req.measurement_method,
                "test_type": "performance" if req.category == "performance" else req.category
            })
        
        # Generate integration test specifications
        for interface_type, interfaces in requirements.interfaces.items():
            for i, interface in enumerate(interfaces):
                test_specs["integration_tests"].append({
                    "test_name": f"test_{interface_type}_interface_{i+1}",
                    "interface_type": interface_type,
                    "description": interface,
                    "test_type": "integration"
                })
        
        return test_specs


def main():
    """Main function to parse requirements and generate test specifications"""
    requirements_file = "/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/FEATURE-003-01-02 TEST GENERATION VERIFICATION SYSTEM/DATA ACCESS LAYER/LAYER-003-01-02-001_data_access_requirements.md"
    
    parser = DataAccessLayerRequirementsParser(requirements_file)
    requirements = parser.parse_requirements()
    test_specs = parser.generate_test_specifications()
    
    print("📋 DATA ACCESS LAYER REQUIREMENTS PARSED")
    print("=" * 50)
    print(f"Layer ID: {requirements.layer_id}")
    print(f"Layer Name: {requirements.layer_name}")
    print(f"Functional Requirements: {len(requirements.functional_requirements)}")
    print(f"Quality Requirements: {len(requirements.quality_requirements)}")
    print(f"Dependencies: {len(requirements.dependencies)}")
    print()
    
    print("🧪 TEST SPECIFICATIONS GENERATED")
    print("=" * 50)
    print(f"Functional Tests: {len(test_specs['functional_tests'])}")
    print(f"Quality Tests: {len(test_specs['quality_tests'])}")
    print(f"Integration Tests: {len(test_specs['integration_tests'])}")
    print(f"Coverage Target: {test_specs['coverage_target']}%")
    
    return requirements, test_specs


if __name__ == "__main__":
    main()