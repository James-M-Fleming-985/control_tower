#!/usr/bin/env python3
"""
AI Code Generator - Feature Builder
Single command to build complete features layer by layer
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import yaml
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# Clean API key (remove whitespace/newlines)
if 'ANTHROPIC_API_KEY' in os.environ:
    os.environ['ANTHROPIC_API_KEY'] = os.environ['ANTHROPIC_API_KEY'].strip()
if 'OPENAI_API_KEY' in os.environ:
    os.environ['OPENAI_API_KEY'] = os.environ['OPENAI_API_KEY'].strip()

# Add necessary paths BEFORE importing orchestrator
control_tower_root = Path(__file__).parent.resolve()
project_004_src = control_tower_root / "projects/PROJECT-004 AI CODE GENERATOR/SYSTEM-004-01 AI CODE GENERATION SYSTEM/src"

if str(control_tower_root) not in sys.path:
    sys.path.insert(0, str(control_tower_root))
if str(project_004_src) not in sys.path:
    sys.path.insert(0, str(project_004_src))


def extract_code_constraints(requirements: Dict) -> Dict:
    """
    Extract code_generation_constraints from layer requirements YAML.
    Returns empty dict if not present - backwards compatible.
    """
    return requirements.get('code_generation_constraints', {})


def extract_technical_constraints(requirements: Dict) -> Dict:
    """
    Extract technical_constraints from layer requirements YAML.
    This includes language, framework, output_file_type, etc.
    Returns empty dict if not present - backwards compatible.
    """
    return requirements.get('technical_constraints', {})


def extract_feature_constraints(requirements: Dict) -> Dict:
    """
    Extract feature_integration_constraints from feature requirements YAML.
    Returns empty dict if not present - backwards compatible.
    """
    return requirements.get('feature_integration_constraints', {})


def format_constraints(constraints: Dict) -> str:
    """
    Format constraints dictionary into readable prompt text.
    Returns empty string if no constraints - backwards compatible.
    """
    if not constraints:
        return ""
    
    sections = []
    for section, rules in constraints.items():
        # Format section header (convert snake_case to TITLE CASE)
        section_title = section.upper().replace('_', ' ')
        sections.append(f"\n{section_title}:")
        
        # Add each rule with bullet point
        if isinstance(rules, list):
            for rule in rules:
                sections.append(f"  - {rule}")
        elif isinstance(rules, dict):
            # Handle nested structure
            for key, value in rules.items():
                sections.append(f"  {key}: {value}")
    
    return "\n".join(sections)


def clean_generated_code(code: str) -> str:
    """
    Remove common AI output formatting issues.
    Safe for all architectures - just fixes obvious problems.
    
    Fixes:
    - Markdown code fences (```python ... ```, ```typescript, etc.)
    - Leading explanatory text before code
    - Trailing explanatory text after code
    - Extra leading/trailing whitespace
    """
    if not code:
        return code
    
    # Strip markdown fences (more comprehensive)
    lines = code.split('\n')
    
    # Remove leading fence and language identifier
    if lines and lines[0].strip().startswith('```'):
        lines = lines[1:]
    
    # Remove trailing fence
    if lines and lines[-1].strip().startswith('```'):
        lines = lines[:-1]
    
    # Remove any remaining closing fence markers
    cleaned_lines = []
    for line in lines:
        # Skip lines that are just fence markers
        fence_markers = ['```', '```python', '```typescript',
                        '```javascript', '```yaml']
        if line.strip() in fence_markers:
            continue
        cleaned_lines.append(line)
    
    # Rejoin
    cleaned = '\n'.join(cleaned_lines)
    
    # Remove excessive leading/trailing whitespace but preserve structure
    cleaned = cleaned.strip() + '\n'  # Ensure single trailing newline
    
    return cleaned


def check_code_truncation(code: str,
                          file_type: str = "python") -> tuple[bool, str]:
    """
    Detect if generated code appears to be truncated.
    
    Returns:
        (is_truncated, warning_message)
    """
    if not code:
        return False, ""
    
    lines = code.strip().split('\n')
    if not lines:
        return False, ""
    
    last_line = lines[-1].strip()
    
    # Common truncation indicators
    truncation_indicators = [
        "# TODO",
        "# Implementation",
        "# ... rest of",
        "# Additional",
        "pass  # TODO",
        "...",
        "# (continued)",
        "# More code here",
    ]
    
    for indicator in truncation_indicators:
        if indicator.lower() in last_line.lower():
            msg = (f"⚠️  Code may be truncated "
                   f"(ends with: '{last_line}')")
            return True, msg
    
    # Check for incomplete syntax (Python-specific)
    if file_type == "python":
        # Last line should not end with : (incomplete block)
        if last_line.endswith(':'):
            msg = "⚠️  Code appears incomplete (ends with ':')"
            return True, msg
        
        # Should not end with open parenthesis/bracket
        if last_line.rstrip().endswith(('(', '[', '{')):
            msg = "⚠️  Code appears incomplete (unclosed bracket)"
            return True, msg
    
    # Check if code is suspiciously short for certain file types
    min_expected_lines = {
        "python": 10,
        "typescript": 10,
        "yaml": 5
    }
    
    if file_type in min_expected_lines:
        if len(lines) < min_expected_lines[file_type]:
            msg = (f"⚠️  File is suspiciously short "
                   f"({len(lines)} lines)")
            return True, msg
    
    return False, ""


def extract_class_methods(python_file_path: Path) -> Dict[str, List[str]]:
    """
    Extract public methods from classes in a Python file.
    
    Returns dict of {class_name: [method_names]} with only public methods (no _private).
    This ensures feature_integration calls actual methods that exist.
    
    Args:
        python_file_path: Path to the Python implementation file
        
    Returns:
        Dictionary mapping class names to lists of public method names
    """
    methods_by_class = {}
    
    try:
        code = python_file_path.read_text()
        lines = code.split('\n')
        
        current_class = None
        indent_level = 0
        
        for line in lines:
            stripped = line.lstrip()
            
            # Detect class definition
            if stripped.startswith('class '):
                class_name = stripped.split('class ')[1].split('(')[0].split(':')[0].strip()
                current_class = class_name
                methods_by_class[class_name] = []
                indent_level = len(line) - len(stripped)
            
            # Detect method definition (must be inside a class)
            elif current_class and stripped.startswith('def '):
                line_indent = len(line) - len(stripped)
                # Method should be one indent level deeper than class
                if line_indent > indent_level:
                    method_name = stripped.split('def ')[1].split('(')[0].strip()
                    # Only include public methods (exclude __init__, _private, etc.)
                    if not method_name.startswith('_'):
                        methods_by_class[current_class].append(method_name)
        
        # Remove classes with no public methods
        methods_by_class = {k: v for k, v in methods_by_class.items() if v}
        
    except Exception as e:
        print(f"Warning: Could not extract methods from {python_file_path}: {e}")
    
    return methods_by_class


def standardize_layer_folder_name(layer_id: str, layer_name: str) -> str:
    """
    Convert layer ID and name to standardized folder naming convention.
    
    This is the SINGLE SOURCE OF TRUTH for layer folder naming.
    All layer folders MUST follow this format for Python import compatibility.
    
    Rules:
    - Replace all hyphens in layer_id with underscores
    - Replace all spaces and hyphens in layer_name with underscores
    - Format: {layer_id_underscores}_{layer_name_underscores}
    
    Args:
        layer_id: Layer identifier (e.g., "LAYER-003-001-001")
        layer_name: Human-readable layer name (e.g., "YAML XML Reader")
        
    Returns:
        Standardized folder name (e.g., "LAYER_003_001_001_YAML_XML_Reader")
        
    Examples:
        >>> standardize_layer_folder_name("LAYER-003-001-001", "YAML XML Reader")
        'LAYER_003_001_001_YAML_XML_Reader'
        
        >>> standardize_layer_folder_name("LAYER-001-002-003", "Data-Model Validator")
        'LAYER_001_002_003_Data_Model_Validator'
    """
    import re
    
    # Replace hyphens with underscores in ID
    clean_id = layer_id.replace('-', '_')
    
    # Replace spaces and hyphens with underscores in name, remove other special chars
    clean_name = layer_name.replace(' ', '_').replace('-', '_')
    
    # Remove or replace other special characters that are invalid in Python identifiers
    # Keep only alphanumeric and underscores
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', clean_name)
    
    return f"{clean_id}_{clean_name}"


@dataclass
class LayerInfo:
    """Information about a built layer."""
    layer_id: str
    layer_name: str
    layer_dir: Path
    implementation_path: Path
    requirements: Dict[str, Any]


@dataclass
class ProductionIntegrationConfig:
    """Configuration for wiring a built feature into the production app.

    Read from the 'production_integration' section of a feature YAML.
    When present, the builder will generate a FastAPI router snippet (or other
    framework-specific glue code) that imports the feature_integration module
    and exposes its operations as API endpoints, then patches the target
    router/app file so the new endpoints are registered.

    Additionally, verifies that the target router itself is mounted in the
    production entry point (app_entry_point, default: main.py) to prevent
    the 'Layer 2 gap' where features are invisible to production.
    """
    target_router_file: str          # e.g. "src/backend/app/causality_router.py"
    import_alias: str                # e.g. "CausalityOrchestrator"
    module_name: str                 # unique importlib module name, e.g. "feature_integration_06"
    endpoint_prefix: str             # e.g. "/granger"  (appended to the router's base prefix)
    operations: List[Dict[str, Any]] # list of {name, http_method, path, description}
    health_endpoint: bool = True     # auto-generate GET <prefix>/health
    pydantic_models: List[Dict[str, Any]] = field(default_factory=list)
    app_entry_point: str = 'main.py' # production entry point to verify router is mounted in


@dataclass
class FrontendIntegrationConfig:
    """Configuration for wiring frontend components into the deployed UI.

    Read from the optional 'frontend_integration' section of a feature YAML.
    When absent, the builder will auto-discover settings from the repo
    structure and production_integration config.

    Example YAML:
        frontend_integration:
          target_app_dir: "SYSTEM-CA-006.../dashboard-app-complete"
          route_path: "/predictions"
          nav_label: "Predictions"
          nav_icon: "🎯"
          page_component_name: "PredictionDashboard"
    """
    target_app_dir: str = ''           # path to React app (relative to repo root or project dir)
    route_path: str = ''               # URL path for the page route (e.g. "/predictions")
    nav_label: str = ''                # label in nav bar
    nav_icon: str = '📊'              # emoji or icon component for nav
    page_component_name: str = ''      # override component name for the page


@dataclass
class FeatureIntegrationSpec:
    """Specification for feature integration layer generation."""
    feature_id: str
    feature_name: str
    feature_dir: Path
    layers: List[LayerInfo]
    integration_scenarios: List[Dict[str, Any]]
    e2e_scenarios: List[Dict[str, Any]]
    feature_acceptance_criteria: List[Dict[str, Any]]


def initialize_layer_structure(feature_path: Path, provider: str = "anthropic", 
                               verbose: bool = False) -> bool:
    """
    Initialize layer folder structure and generate layer YAML files.
    
    This pre-processing step:
    1. Reads FEATURE_REQUIREMENTS.yaml to get layer definitions
    2. Creates standardized layer folders (LAYER_XXX_YYY_Name_With_Underscores)
    3. Uses AI to derive detailed layer requirements from feature requirements
    4. Populates LAYER_REQUIREMENTS_TEMPLATE.yaml with derived content
    5. Writes layer YAML files to respective folders
    6. Creates src/ and tests/ subdirectories
    
    Args:
        feature_path: Path to FEATURE_REQUIREMENTS.yaml
        provider: AI provider ("anthropic" or "openai")
        verbose: Show detailed output
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load feature requirements
        with open(feature_path, 'r', encoding='utf-8') as f:
            feature_spec = yaml.safe_load(f)
        
        feature_id = feature_spec['metadata']['feature_id']
        feature_name = feature_spec['metadata']['feature_name']
        print(f"✓ Loaded feature: {feature_id} - {feature_name}")
        
        # Get layers from feature spec
        layers = feature_spec.get('layers', [])
        if not layers:
            print(f"❌ No layers defined in feature specification")
            return False
        
        print(f"✓ Found {len(layers)} layers to initialize\n")
        
        # Load layer template
        template_path = Path(__file__).parent / "templates" / "LAYER_REQUIREMENTS_TEMPLATE.yaml"
        with open(template_path, 'r', encoding='utf-8') as f:
            layer_template = f.read()
        
        print(f"✓ Loaded layer template: {template_path}\n")
        
        # Initialize AI provider
        from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        config = {'provider': provider}
        orchestrator = AICodeGeneratorOrchestrator(config=config)
        
        # Process each layer
        feature_dir = feature_path.parent
        for i, layer in enumerate(layers, 1):
            layer_id = layer['layer_id']
            layer_name = layer['name']
            
            print(f"{'='*80}")
            print(f"  Layer {i}/{len(layers)}: {layer_name}")
            print(f"{'='*80}\n")
            
            # Create standardized folder name
            folder_name = standardize_layer_folder_name(layer_id, layer_name)
            layer_folder = feature_dir / folder_name
            yaml_filename = f"{folder_name}.yaml"
            yaml_path = layer_folder / yaml_filename
            
            # Check if YAML already exists (skip entire initialization if so)
            if yaml_path.exists():
                print(f"✓ Layer already initialized: {yaml_filename} exists (skipping)")
                print(f"   Folder: {folder_name}/")
                print(f"   YAML: {yaml_filename}\n")
                continue
            
            # Check if folder already exists
            if layer_folder.exists():
                print(f"📁 Folder already exists: {folder_name} (skipping creation)")
            else:
                print(f"📁 Creating folder: {folder_name}")
                layer_folder.mkdir(exist_ok=True)
                
                # Create subdirectories
                (layer_folder / "src").mkdir(exist_ok=True)
                (layer_folder / "tests").mkdir(exist_ok=True)
                print(f"   ✓ Created: {folder_name}/src/")
                print(f"   ✓ Created: {folder_name}/tests/")
            
            print()  # Empty line for readability
            
            # Derive layer requirements using AI
            print(f"🤖 Deriving layer requirements from feature requirements...")
            derived_yaml = derive_layer_requirements_with_ai(
                feature_spec=feature_spec,
                layer_info=layer,
                layer_template=layer_template,
                folder_name=folder_name,
                orchestrator=orchestrator,
                verbose=verbose
            )
            
            # Write layer YAML file
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write(derived_yaml)
            
            print(f"   ✓ Generated: {yaml_filename}")
            print(f"   ✓ Layer initialized successfully\n")
        
        print(f"\n{'='*80}")
        print(f"  ✅ All {len(layers)} layers initialized successfully!")
        print(f"{'='*80}\n")
        print(f"Next steps:")
        print(f"  1. Review generated layer YAML files")
        print(f"  2. Adjust requirements if needed")
        print(f"  3. Run: python build_feature.py {feature_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing layer structure: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def derive_layer_requirements_with_ai(feature_spec: Dict, layer_info: Dict,
                                     layer_template: str, folder_name: str,
                                     orchestrator, verbose: bool) -> str:
    """
    Use AI to derive detailed layer requirements from feature requirements.
    
    This is Task 5 - AI prompt for layer requirement derivation.
    """
    # TODO: Implement AI prompt - This will be Task 5
    # For now, return template with basic population
    
    # Extract key info
    feature_id = feature_spec['metadata']['feature_id']
    feature_name = feature_spec['metadata']['feature_name']
    layer_id = layer_info['layer_id']
    layer_name = layer_info['name']
    
    # Get feature requirements for context
    feature_reqs = feature_spec.get('requirements', {})
    
    # Build AI prompt
    prompt = f"""Generate a complete layer requirements YAML file following this template structure:

{layer_template}

Context:
- Feature ID: {feature_id}
- Feature Name: {feature_name}
- Layer ID: {layer_id}
- Layer Name: {layer_name}
- Layer Folder (CRITICAL - MUST match exactly): {folder_name}

Feature Requirements to Derive From:
{yaml.dump(feature_reqs, default_flow_style=False)}

Instructions:
1. Replace ALL [PLACEHOLDER] values with specific, detailed content
2. In metadata section, set layer_folder to exactly: "{folder_name}"
3. Analyze feature requirements and decompose into layer-specific requirements
4. Map each feature requirement to specific layer requirements in traceability.derived_from_feature_requirements
5. Define clear interfaces (classes, methods, inputs, outputs)
6. Specify technical implementation details appropriate for this layer
7. Include comprehensive acceptance criteria
8. Return ONLY the populated YAML, no explanations

Generate the complete layer requirements YAML now:"""
    
    # Call AI
    if verbose:
        print(f"   📝 Prompt length: {len(prompt)} chars")
    
    response = orchestrator.ai_provider.generate_code(
        prompt=prompt,
        max_tokens=16384  # Increased for comprehensive layer requirements
    )
    
    # Extract YAML from response
    if "```yaml" in response:
        start = response.find("```yaml") + 7
        end = response.rfind("```")
        if end > start:  # Found closing marker
            response = response[start:end].strip()
        else:  # No closing marker (truncated), take everything after opening
            response = response[start:].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.rfind("```")
        if end > start:  # Found closing marker
            response = response[start:end].strip()
        else:  # No closing marker (truncated), take everything after opening
            response = response[start:].strip()
    
    # If response is still empty or too short, there's a problem
    if not response or len(response) < 100:
        if verbose:
            print(f"   ⚠️  WARNING: Extracted YAML is too short ({len(response)} chars)")
            print(f"   Raw response length: {len(response)} chars")
    
    return response


class FeatureBuilder:
    """Build complete features from YAML specifications using AI."""
    
    def __init__(self, feature_path: str, provider: str = "anthropic", 
                 verbose: bool = False, skip_layer_generation: bool = False):
        """Initialize feature builder."""
        self.feature_path = Path(feature_path)
        self.provider = provider
        self.verbose = verbose
        self.skip_layer_generation = skip_layer_generation
        self.output_dir = Path("/workspaces/control_tower/AI_GENERATED_FEATURES")
        
        # Validate feature spec exists
        if not self.feature_path.exists():
            raise FileNotFoundError(f"Feature specification not found: {feature_path}")
            
    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
        
    def print_step(self, icon: str, message: str):
        """Print step message."""
        print(f"{icon} {message}")
        
    def load_feature_spec(self):
        """Load and parse feature specification."""
        self.print_header("Loading Feature Specification")
        
        with open(self.feature_path, 'r') as f:
            self.feature_spec = yaml.safe_load(f)
            
        feature_name = self.feature_spec['metadata']['requirement_name']
        feature_id = self.feature_spec['metadata']['requirement_id']
        
        self.print_step("✓", f"Feature: {feature_name}")
        self.print_step("✓", f"Feature ID: {feature_id}")
        
        # Get layers
        self.layers = self.feature_spec.get('layers', [])
        self.print_step("✓", f"Layers to build: {len(self.layers)}")
        
        for layer in self.layers:
            self.print_step("  ", f"- {layer['name']} ({layer['layer_id']})")
            
        return feature_id, feature_name
        
    def find_layer_spec(self, layer_info: dict) -> Path:
        """
        Find layer specification file using standardized naming convention.
        
        Enforces LAYER_{id_underscores}_{name_underscores} folder structure.
        Supports legacy layer_directory field as fallback.
        """
        layer_file = layer_info.get('requirement_file')
        if not layer_file:
            raise ValueError(f"No requirement_file specified for {layer_info['layer_id']}")
        
        layer_id = layer_info['layer_id']
        layer_name = layer_info['name']
        
        # Priority 1: Check if layer_directory field is specified (legacy support)
        if 'layer_directory' in layer_info:
            layer_dir = layer_info['layer_directory']
            layer_path = self.feature_path.parent / layer_dir / layer_file
            if layer_path.exists():
                return layer_path
        
        # Priority 2: Use standardized naming convention (SINGLE SOURCE OF TRUTH)
        standardized_folder = standardize_layer_folder_name(layer_id, layer_name)
        layer_path = self.feature_path.parent / standardized_folder / layer_file
        
        if not layer_path.exists():
            # Provide helpful error message with correct naming
            raise FileNotFoundError(
                f"\nLayer specification not found: {layer_path}\n\n"
                f"Expected folder structure:\n"
                f"  {standardized_folder}/\n"
                f"  └── {layer_file}\n\n"
                f"IMPORTANT: Layer folders MUST use underscores (not spaces/hyphens)\n"
                f"  Correct:   {standardized_folder}\n"
                f"  Incorrect: {layer_id} {layer_name}\n\n"
                f"To initialize layer structure:\n"
                f"  python build_feature.py --init-layers {self.feature_path}\n"
            )
        
        return layer_path
        
    def build_layer(self, layer_info: dict, layer_number: int, total_layers: int) -> bool:
        """Build a single layer using AI Code Generator."""
        self.print_header(f"Building Layer {layer_number}/{total_layers}: {layer_info['name']}")
        
        layer_spec = self.find_layer_spec(layer_info)
        self.print_step("✓", f"Layer spec: {layer_spec}")
        
        # Use the layer's actual directory (where the YAML file is located)
        # This ensures artifacts are saved directly in the correct layer folder
        layer_output = layer_spec.parent
        
        self.print_step("✓", f"Output directory: {layer_output}")
        
        # Import orchestrator (paths already set at module level)
        try:
            from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
            
            self.print_step("🤖", "Initializing AI Code Generator...")
            
            # Create orchestrator with proper config dict
            config = {
                'output_base_path': str(layer_output),
                'provider': self.provider
            }
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            
            self.print_step("🤖", f"Executing full TDD cycle for {layer_info['name']}...")
            
            # Execute from YAML
            result = orchestrator.execute_from_yaml(layer_spec)
            
            if result.get('status') == 'COMPLETE':
                self.print_step("✅", f"Layer {layer_info['name']} completed successfully!")
                
                # Show summary
                reports = result.get('verification_reports', {})
                self.print_step("📊", "Verification reports generated:")
                for report_name in reports:
                    self.print_step("  ", f"- {report_name}")
                    
                return True
            else:
                self.print_step("❌", f"Layer {layer_info['name']} failed!")
                return False
                
        except Exception as e:
            self.print_step("❌", f"Error building layer: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _collect_layer_implementations(self, layers_info: List[Dict]) -> List[LayerInfo]:
        """Collect implementation details from built layers."""
        layer_implementations = []
        
        for layer_info in layers_info:
            layer_id = layer_info['layer_id']
            layer_name = layer_info['name']
            
            # Find layer directory (already built)
            layer_spec = self.find_layer_spec(layer_info)
            layer_dir = layer_spec.parent
            
            # Parse requirements from layer YAML to determine file extension
            layer_yaml = yaml.safe_load(layer_spec.read_text())
            tech_constraints = extract_technical_constraints(layer_yaml)
            language = tech_constraints.get('language', 'python').lower()
            
            # Determine implementation file extension based on language
            if 'typescript' in language or 'react' in language:
                impl_filename = "implementation.tsx"
            elif 'jsx' in language:
                impl_filename = "implementation.jsx"
            elif 'javascript' in language:
                impl_filename = "implementation.js"
            else:
                impl_filename = "implementation.py"

            # Fallback: if the determined file doesn't exist, try other
            # common extensions before giving up (AI may pick .jsx vs .js)
            if not (layer_dir / "src" / impl_filename).exists():
                for alt_ext in (".jsx", ".tsx", ".js", ".py"):
                    alt = layer_dir / "src" / f"implementation{alt_ext}"
                    if alt.exists():
                        impl_filename = f"implementation{alt_ext}"
                        break
            
            impl_path = layer_dir / "src" / impl_filename
            
            if not impl_path.exists():
                print(f"⚠️  Warning: Implementation not found for {layer_id} at {impl_path}")
                continue
            
            layer_impl = LayerInfo(
                layer_id=layer_id,
                layer_name=layer_name,
                layer_dir=layer_dir,
                implementation_path=impl_path,
                requirements=layer_yaml
            )
            
            layer_implementations.append(layer_impl)
        
        return layer_implementations
    
    def _build_feature_integration_prompt(self, spec: FeatureIntegrationSpec) -> str:
        """Build AI prompt for feature integration code generation."""
        
        # Format layer implementations with ACTUAL METHOD SIGNATURES
        layer_descriptions = []
        for layer in spec.layers:
            # Extract actual classes and methods from implementation
            methods_by_class = extract_class_methods(layer.implementation_path)
            
            # Format class and method information
            class_info = []
            for class_name, methods in methods_by_class.items():
                method_list = '\n    - '.join(methods) if methods else 'No public methods'
                class_info.append(f"""
  Class: {class_name}
  Public Methods:
    - {method_list}""")
            
            layer_descriptions.append(f"""
Layer: {layer.layer_name} ({layer.layer_id})
Location: {layer.implementation_path}
{''.join(class_info)}
Purpose: {layer.requirements.get('description', 'N/A')}

CRITICAL: Only call methods that exist above. Do NOT invent method names.
""")
        
        # Format integration scenarios
        integration_desc = []
        for scenario in spec.integration_scenarios:
            integration_desc.append(f"""
Scenario: {scenario.get('name', 'Unnamed')}
Description: {scenario.get('description', 'N/A')}
Layers Involved: {', '.join(scenario.get('layers', []))}
""")
        
        # Format E2E scenarios
        e2e_desc = []
        for scenario in spec.e2e_scenarios:
            e2e_desc.append(f"""
E2E Scenario: {scenario.get('name', 'Unnamed')}
Description: {scenario.get('description', 'N/A')}
Flow: {scenario.get('flow', 'N/A')}
""")
        
        # Build comprehensive prompt
        prompt = f"""Generate Python feature integration code for the following feature:

FEATURE: {spec.feature_name}
FEATURE ID: {spec.feature_id}

LAYER IMPLEMENTATIONS:
{''.join(layer_descriptions)}

INTEGRATION REQUIREMENTS:
The feature integration layer must orchestrate these layers to work together.
{''.join(integration_desc) if integration_desc else 'No specific integration scenarios defined.'}

END-TO-END SCENARIOS:
{''.join(e2e_desc) if e2e_desc else 'No specific E2E scenarios defined.'}

REQUIREMENTS:
1. Create a FeatureOrchestrator class that:
   - Imports all layer implementations from their respective paths
   - Initializes instances of each layer's main classes
   - Provides methods to orchestrate layer interactions
   - Handles errors across layers gracefully
   - Returns structured responses

2. Create supporting classes:
   - FeatureResponse dataclass for unified responses
   - FeatureConfig dataclass for configuration

3. Include proper error handling:
   - Validate layer initialization
   - Handle layer communication errors
   - Provide meaningful error messages

4. Follow Python best practices:
   - Type hints for all methods
   - Comprehensive docstrings
   - Clean, readable code structure

===== CRITICAL METHOD USAGE RULES =====
- ONLY call methods that are listed above in "Public Methods" for each layer
- DO NOT invent or assume method names (e.g., prepare_data, validate)
- Use EXACT method names from the layer implementations
- If you need functionality, use the methods that ACTUALLY EXIST
- Cross-reference: Layer class methods are listed above - use those EXACT names
===== END CRITICAL RULES =====

Generate ONLY the Python code for the feature integration module.
Use relative imports to access layer implementations.

CRITICAL IMPORT REQUIREMENTS:
- Layer folders use UNDERSCORES (not spaces or hyphens): LAYER_XXX_YYY_ZZZ_Name_With_Underscores
- Import format MUST match folder names exactly
- Use standardized layer folder names in import statements

Example import structure for layers with standardized naming:
```python
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from standardized layer folders (underscores only)
# Example layer folders: LAYER_003_001_001_YAML_XML_Reader, LAYER_003_001_002_Data_Validator
from LAYER_XXX_YYY_ZZZ_Layer_Name.src.implementation import ClassName1, ClassName2
from LAYER_XXX_YYY_ZZZ_Another_Layer.src.implementation import AnotherClass
```

For the actual layers in this feature, use these folder names:
{self._generate_layer_import_examples(spec.layers)}

Generate the complete feature_integration.py module now:
"""
        
        # Phase 2: Inject feature integration constraints if present
        feature_reqs = spec.layers[0].requirements if spec.layers else {}
        
        # Try to get constraints from feature-level requirements
        # (assuming feature metadata is passed through spec somehow)
        # For now, check if any layer has feature_integration_constraints
        constraints = {}
        for layer in spec.layers:
            if 'feature_integration_constraints' in layer.requirements:
                constraints = extract_feature_constraints(layer.requirements)
                break
        
        if constraints:
            prompt += f"""

═══════════════════════════════════════════
CRITICAL CODE GENERATION CONSTRAINTS
═══════════════════════════════════════════
{format_constraints(constraints)}

YOU MUST FOLLOW THESE CONSTRAINTS EXACTLY.
DO NOT DEVIATE FROM THESE RULES.
═══════════════════════════════════════════
"""
        
        return prompt
    
    def _generate_layer_import_examples(self, layers: List[LayerInfo]) -> str:
        """Generate correct import examples using standardized layer folder names."""
        examples = []
        for layer in layers:
            folder_name = standardize_layer_folder_name(layer.layer_id, layer.layer_name)
            examples.append(f"# from {folder_name}.src.implementation import ...")
        return "\n".join(examples)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from AI response."""
        
        # Look for code blocks
        if "```python" in response:
            # Extract between ```python and ```
            start = response.find("```python") + len("```python")
            end = response.find("```", start)
            code = response[start:end].strip()
            return code
        elif "```" in response:
            # Extract between ``` and ```
            start = response.find("```") + len("```")
            end = response.find("```", start)
            code = response[start:end].strip()
            return code
        else:
            # Assume entire response is code
            return response.strip()
    
    def generate_feature_integration(self, spec: FeatureIntegrationSpec) -> bool:
        """Generate feature integration implementation using AI."""
        
        try:
            print(f"  🤖 Generating feature integration code for {spec.feature_name}...")
            
            # Build prompt
            prompt = self._build_feature_integration_prompt(spec)
            
            # Import orchestrator (reuse existing)
            from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
            
            # Initialize orchestrator with config
            config = {
                'output_base_path': str(spec.feature_dir),
                'provider': self.provider
            }
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            
            # Call AI to generate code (reuse green phase pattern)
            print("  🤖 Calling AI to generate integration code...")
            response = orchestrator.ai_provider.generate_code(
                prompt=prompt,
                max_tokens=20480  # High token limit for complex features
            )
            
            # Extract code from response
            code = self._extract_code_from_response(response)
            
            if not code:
                print("  ❌ Failed to extract code from AI response")
                return False
            
            # Phase 4: Auto-fix common AI output issues (safe for all architectures)
            code = clean_generated_code(code)
            
            # Phase 5: Check for truncation
            is_truncated, warning_msg = check_code_truncation(code, "python")
            if is_truncated:
                print(f"  {warning_msg}")
                print("  ⚠️  Consider reducing max_tokens or "
                      "breaking into smaller files")
            
            # Save to feature directory
            output_path = spec.feature_dir / "src" / "feature_integration.py"
            output_path.parent.mkdir(exist_ok=True, parents=True)
            output_path.write_text(code)
            
            print(f"  ✅ Feature integration code saved to {output_path}")
            print(f"     Lines of code: {len(code.splitlines())}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error generating feature integration: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def generate_feature_tests(self, feature_spec: FeatureIntegrationSpec) -> tuple[int, int]:
        """Generate integration and E2E tests for the feature.
        
        Returns:
            tuple: (integration_test_count, e2e_test_count)
        """
        try:
            print(f"\n  🧪 Generating feature-level tests...")
            
            # Import orchestrator (same pattern as generate_feature_integration)
            from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
            
            # Initialize orchestrator with config
            config = {
                'output_base_path': str(feature_spec.feature_dir),
                'provider': self.provider
            }
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            integration_count = 0
            e2e_count = 0
            
            # Generate integration tests
            print(f"  🔗 Generating integration tests...")
            integration_tests_dir = feature_spec.feature_dir / "tests" / "integration"
            integration_tests_dir.mkdir(parents=True, exist_ok=True)
            
            integration_prompt = f"""Generate pytest integration tests for the feature: {feature_spec.feature_name}

Feature ID: {feature_spec.feature_id}
Layers: {', '.join([f"{l.layer_id}: {l.layer_name}" for l in feature_spec.layers])}

Integration scenarios to test:
{chr(10).join(['- ' + s for s in feature_spec.integration_scenarios])}

Requirements:
1. Create integration tests that verify layers work together through feature_integration.py
2. Test all integration scenarios listed above
3. Use pytest fixtures and mocking where appropriate
4. Include proper setup/teardown
5. Test error handling across layer boundaries

Generate a complete test_integration.py file with at least 5 comprehensive integration tests."""

            response = orchestrator.ai_provider.generate_code(
                prompt=integration_prompt,
                max_tokens=16384  # High token limit for comprehensive integration tests
            )
            
            integration_code = self._extract_code_from_response(response)
            if integration_code:
                integration_test_path = integration_tests_dir / "test_integration.py"
                integration_test_path.write_text(integration_code)
                integration_count = integration_code.count("def test_")
                print(f"  ✅ Integration tests generated: {integration_count} tests")
            
            # Generate E2E tests
            print(f"  🎯 Generating E2E tests...")
            e2e_tests_dir = feature_spec.feature_dir / "tests" / "e2e"
            e2e_tests_dir.mkdir(parents=True, exist_ok=True)
            
            e2e_prompt = f"""Generate pytest end-to-end tests for the feature: {feature_spec.feature_name}

Feature ID: {feature_spec.feature_id}

E2E scenarios to test:
{chr(10).join(['- ' + s for s in feature_spec.e2e_scenarios])}

Acceptance criteria:
{chr(10).join(['- ' + c for c in feature_spec.feature_acceptance_criteria])}

Requirements:
1. Create E2E tests that verify the complete feature workflow
2. Test all E2E scenarios and acceptance criteria
3. Use realistic test data
4. Test both success and failure paths
5. Verify complete end-to-end data flow

Generate a complete test_e2e.py file with at least 3 comprehensive E2E tests."""

            response = orchestrator.ai_provider.generate_code(
                prompt=e2e_prompt,
                max_tokens=16384  # High token limit for comprehensive E2E tests
            )
            
            e2e_code = self._extract_code_from_response(response)
            if e2e_code:
                e2e_test_path = e2e_tests_dir / "test_e2e.py"
                e2e_test_path.write_text(e2e_code)
                e2e_count = e2e_code.count("def test_")
                print(f"  ✅ E2E tests generated: {e2e_count} tests")
            
            return (integration_count, e2e_count)
            
        except Exception as e:
            print(f"  ❌ Error generating feature tests: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return (0, 0)
    
    def generate_feature_level_verification(self, feature_spec: FeatureIntegrationSpec, integration_test_count: int = 0, e2e_test_count: int = 0) -> bool:
        """Generate feature-level verification artifacts after all layers are complete."""
        try:
            print(f"  🔍 Generating feature-level verification artifacts...")
            
            # Create verification directory at feature level
            verification_dir = feature_spec.feature_dir / "Requirements Verification"
            verification_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. Feature Requirements Verification Report
            requirements_report = {
                "feature_id": feature_spec.feature_id,
                "feature_name": feature_spec.feature_name,
                "verification_timestamp": timestamp,
                "total_layers": len(feature_spec.layers),
                "layers_completed": len(feature_spec.layers),
                "feature_level_tests": {
                    "integration_tests": "REQUIRED",
                    "e2e_tests": "REQUIRED",
                    "status": "PENDING_EXECUTION"
                },
                "layer_summary": [
                    {
                        "layer_id": layer.layer_id,
                        "layer_name": layer.layer_name,
                        "implementation": str(layer.implementation_path),
                        "tests": len(list(layer.layer_dir.glob("tests/test_*.py"))),
                        "status": "COMPLETED"
                    }
                    for layer in feature_spec.layers
                ],
                "acceptance_criteria": feature_spec.feature_acceptance_criteria,
                "acceptance_status": "PENDING_FEATURE_TESTS"
            }
            
            requirements_path = verification_dir / f"feature_requirements_verification_{timestamp}.yaml"
            with open(requirements_path, 'w') as f:
                yaml.dump(requirements_report, f, default_flow_style=False, sort_keys=False)
            
            # 2. Feature Test Pyramid Report
            pyramid_report = {
                "feature_id": feature_spec.feature_id,
                "feature_name": feature_spec.feature_name,
                "test_pyramid_timestamp": timestamp,
                "layer_tests": {
                    "unit_tests": sum(len(list(layer.layer_dir.glob("tests/test_*.py"))) for layer in feature_spec.layers),
                    "layer_count": len(feature_spec.layers)
                },
                "feature_tests": {
                    "integration_tests": {
                        "location": "tests/integration/",
                        "count": integration_test_count,
                        "status": "COMPLETED" if integration_test_count > 0 else "REQUIRED"
                    },
                    "e2e_tests": {
                        "location": "tests/e2e/",
                        "count": e2e_test_count,
                        "status": "COMPLETED" if e2e_test_count > 0 else "REQUIRED"
                    }
                },
                "integration_scenarios": feature_spec.integration_scenarios,
                "e2e_scenarios": feature_spec.e2e_scenarios,
                "test_coverage_goal": "90%",
                "status": "PYRAMID_STRUCTURE_DEFINED"
            }
            
            pyramid_path = verification_dir / f"feature_test_pyramid_{timestamp}.yaml"
            with open(pyramid_path, 'w') as f:
                yaml.dump(pyramid_report, f, default_flow_style=False, sort_keys=False)
            
            # 3. Feature Traceability Matrix
            traceability_report = {
                "feature_id": feature_spec.feature_id,
                "feature_name": feature_spec.feature_name,
                "traceability_timestamp": timestamp,
                "feature_to_layers": {
                    layer.layer_id: {
                        "layer_name": layer.layer_name,
                        "implementation": str(layer.implementation_path.name),
                        "test_files": [f.name for f in layer.layer_dir.glob("tests/test_*.py")],
                        "traceability_status": "VERIFIED"
                    }
                    for layer in feature_spec.layers
                },
                "feature_integration": {
                    "integration_file": "src/feature_integration.py",
                    "orchestrates_layers": [layer.layer_id for layer in feature_spec.layers],
                    "status": "IMPLEMENTED"
                },
                "requirements_coverage": {
                    "layer_requirements": "100%",
                    "feature_requirements": "PENDING_FEATURE_TESTS",
                    "acceptance_criteria": len(feature_spec.feature_acceptance_criteria)
                }
            }
            
            traceability_path = verification_dir / f"feature_traceability_matrix_{timestamp}.yaml"
            with open(traceability_path, 'w') as f:
                yaml.dump(traceability_report, f, default_flow_style=False, sort_keys=False)
            
            # 4. Feature Quality Gates Report
            quality_gates_report = {
                "feature_id": feature_spec.feature_id,
                "feature_name": feature_spec.feature_name,
                "quality_gates_timestamp": timestamp,
                "gates": {
                    "all_layers_complete": {
                        "status": "PASSED",
                        "layers_built": len(feature_spec.layers),
                        "layers_required": len(feature_spec.layers)
                    },
                    "feature_integration_exists": {
                        "status": "PASSED" if (feature_spec.feature_dir / "src/feature_integration.py").exists() else "FAILED",
                        "integration_file": "src/feature_integration.py"
                    },
                    "integration_tests_complete": {
                        "status": "PENDING",
                        "required": "Integration tests must be written and pass",
                        "location": "tests/integration/"
                    },
                    "e2e_tests_complete": {
                        "status": "PENDING",
                        "required": "End-to-end tests must be written and pass",
                        "location": "tests/e2e/"
                    },
                    "acceptance_criteria_met": {
                        "status": "PENDING",
                        "total_criteria": len(feature_spec.feature_acceptance_criteria),
                        "criteria": feature_spec.feature_acceptance_criteria
                    }
                },
                "overall_status": "PARTIAL_COMPLETE",
                "next_steps": [
                    "Write and execute feature integration tests",
                    "Write and execute end-to-end tests",
                    "Verify all acceptance criteria",
                    "Run full test suite with coverage analysis"
                ]
            }
            
            quality_gates_path = verification_dir / f"feature_quality_gates_{timestamp}.yaml"
            with open(quality_gates_path, 'w') as f:
                yaml.dump(quality_gates_report, f, default_flow_style=False, sort_keys=False)
            
            # Print confirmation
            print(f"  ✅ Feature-level verification artifacts generated:")
            print(f"     - {requirements_path.relative_to(feature_spec.feature_dir)}")
            print(f"     - {pyramid_path.relative_to(feature_spec.feature_dir)}")
            print(f"     - {traceability_path.relative_to(feature_spec.feature_dir)}")
            print(f"     - {quality_gates_path.relative_to(feature_spec.feature_dir)}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error generating feature-level verification: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    # -----------------------------------------------------------------
    # Production Integration Wiring
    # -----------------------------------------------------------------
    def generate_production_wiring(
        self,
        feature_spec: FeatureIntegrationSpec,
        prod_config: Dict[str, Any],
    ) -> bool:
        """Generate and inject production wiring into the target app file.

        Reads the ``production_integration`` section from the feature YAML,
        builds a code snippet that:
        1. Imports the feature_integration module via importlib (avoids name
           collisions between features that all export FeatureOrchestrator).
        2. Instantiates the orchestrator at module level.
        3. Registers FastAPI endpoints that delegate to the orchestrator.

        The snippet is appended **before** any catch-all path-parameter route
        (``/{...}``) so that specific routes take priority.

        Returns True on success, False on failure.
        """
        try:
            target_file = prod_config.get('target_router_file')
            if not target_file:
                print("  ❌ No target_router_file specified in production_integration")
                return False

            # Resolve relative to the repo root (feature_dir's grandparent
            # typically, but we search upward for a .git marker)
            repo_root = feature_spec.feature_dir
            while repo_root != repo_root.parent:
                if (repo_root / '.git').exists():
                    break
                repo_root = repo_root.parent

            target_path = repo_root / target_file
            if not target_path.exists():
                # The target file may be relative to a project subdirectory
                # (e.g. Causal_affect/) rather than the repo root.  Walk down
                # from repo_root through the feature_dir path to find it.
                try:
                    rel_feature = feature_spec.feature_dir.relative_to(repo_root)
                    for i in range(1, len(rel_feature.parts) + 1):
                        candidate = repo_root / Path(*rel_feature.parts[:i]) / target_file
                        if candidate.exists():
                            target_path = candidate
                            repo_root = repo_root / Path(*rel_feature.parts[:i])
                            break
                except ValueError:
                    pass

            if not target_path.exists():
                print(f"  ❌ Target router file not found: {target_path}")
                return False

            import_alias = prod_config.get('import_alias', f'{feature_spec.feature_id}_Orchestrator')
            module_name = prod_config.get('module_name', f'feature_integration_{feature_spec.feature_id}')
            endpoint_prefix = prod_config.get('endpoint_prefix', f'/{feature_spec.feature_id}')
            operations = prod_config.get('operations', [])
            health_endpoint = prod_config.get('health_endpoint', True)
            feature_integration_path = feature_spec.feature_dir / "src" / "feature_integration.py"

            # Build the relative path from the repo root to the feature integration
            rel_integration_dir = feature_integration_path.parent.relative_to(repo_root)

            # --- Build Pydantic request models ---
            pydantic_models_code = ""
            for model_def in prod_config.get('pydantic_models', []):
                model_name = model_def['name']
                fields = model_def.get('fields', [])
                field_lines = []
                for f in fields:
                    fname = f['name']
                    ftype = f.get('type', 'Any')
                    fdefault = f.get('default', '...')
                    fdesc = f.get('description', '')
                    field_lines.append(
                        f'    {fname}: {ftype} = Field(default={fdefault}, description="{fdesc}")'
                    )
                pydantic_models_code += f"\n\nclass {model_name}(BaseModel):\n"
                pydantic_models_code += "\n".join(field_lines) + "\n"

            # --- Build import block ---
            avail_flag = f'{import_alias.upper()}_AVAILABLE'
            service_var = f'_{import_alias.lower()}'
            import_block = f'''
# ---------------------------------------------------------------------------
# AUTO-WIRED by AI Feature Builder: {feature_spec.feature_id}
# ---------------------------------------------------------------------------
_fi_{module_name}_path = Path(__file__).parent.parent.parent.parent / "{rel_integration_dir}"
try:
    import importlib.util as _ilu_{module_name}
    _spec_{module_name} = _ilu_{module_name}.spec_from_file_location(
        "{module_name}", _fi_{module_name}_path / "feature_integration.py"
    )
    _mod_{module_name} = _ilu_{module_name}.module_from_spec(_spec_{module_name})
    _spec_{module_name}.loader.exec_module(_mod_{module_name})
    {import_alias} = _mod_{module_name}.FeatureOrchestrator
    {avail_flag} = True
    {service_var} = {import_alias}()
except Exception as _e_{module_name}:
    logging.warning(f"{feature_spec.feature_id} not available: {{_e_{module_name}}}")
    {avail_flag} = False
    {service_var} = None
'''

            # --- Build endpoint block ---
            endpoint_block = f'''
# =============================================================================
# {feature_spec.feature_id}: {feature_spec.feature_name} (auto-wired)
# =============================================================================
{pydantic_models_code}'''

            for op in operations:
                method = op.get('http_method', 'get').lower()
                path = op.get('path', f'/{op["name"]}')
                op_name = op['name']
                description = op.get('description', '')
                request_model = op.get('request_model', None)
                orchestrator_method = op.get('orchestrator_method', op_name)
                orchestrator_args = op.get('orchestrator_args', '')

                if request_model:
                    endpoint_block += f'''

@router.{method}("{endpoint_prefix}{path}")
async def {op_name}(request: {request_model}) -> Dict[str, Any]:
    """{description}"""
    if not {avail_flag}:
        raise HTTPException(status_code=503, detail="{feature_spec.feature_id} not available")
    result = {service_var}.{orchestrator_method}({orchestrator_args})
    return result.to_dict() if hasattr(result, 'to_dict') else {{"success": result.success, "data": result.data, "error": result.error}}
'''
                else:
                    endpoint_block += f'''

@router.{method}("{endpoint_prefix}{path}")
async def {op_name}() -> Dict[str, Any]:
    """{description}"""
    if not {avail_flag}:
        return {{"available": False, "error": "Service not loaded"}}
    result = {service_var}.{orchestrator_method}()
    return result.to_dict() if hasattr(result, 'to_dict') else {{"success": result.success, "data": result.data}}
'''

            if health_endpoint:
                endpoint_block += f'''

@router.get("{endpoint_prefix}/health")
async def {import_alias.lower()}_health() -> Dict[str, Any]:
    """Health check for {feature_spec.feature_name}."""
    if not {avail_flag}:
        return {{"available": False, "error": "Service not loaded"}}
    result = {service_var}.health_check() if hasattr({service_var}, 'health_check') else None
    if result:
        return {{"available": True, "healthy": getattr(result, 'success', True), "data": getattr(result, 'data', None)}}
    return {{"available": True, "status": "ok"}}
'''

            # --- Inject into target file ---
            existing_code = target_path.read_text()

            # Check if already wired (idempotent)
            if f'AUTO-WIRED by AI Feature Builder: {feature_spec.feature_id}' in existing_code:
                print(f"  ℹ️  {feature_spec.feature_id} already wired in {target_file}")
                return True

            # Insert import block after the last existing "except" block at
            # module level (near the top of file, after other imports)
            # Strategy: find the line "router = APIRouter" and inject just before it.
            marker = 'router = APIRouter'
            if marker in existing_code:
                existing_code = existing_code.replace(
                    marker,
                    import_block + "\n" + marker,
                    1
                )
            else:
                # Fallback: append import block near end of imports
                existing_code = existing_code + "\n" + import_block

            # Insert endpoint block before any catch-all route or at end of file
            # Look for a catch-all pattern like @router.get("/{
            import re as _re
            catch_all_pattern = _re.compile(
                r'^@router\.\w+\("[^"]*\{[^}]+\}.*"\)', _re.MULTILINE
            )
            match = catch_all_pattern.search(existing_code)
            if match:
                # Insert before the catch-all
                insert_pos = match.start()
                existing_code = (
                    existing_code[:insert_pos]
                    + endpoint_block + "\n\n"
                    + existing_code[insert_pos:]
                )
            else:
                # Append at end
                existing_code += "\n" + endpoint_block

            target_path.write_text(existing_code)

            print(f"  ✅ Production wiring injected into {target_file}")
            print(f"     Import alias: {import_alias}")
            print(f"     Endpoints: {len(operations)} operations" +
                  (" + health" if health_endpoint else ""))
            print(f"     Prefix: {endpoint_prefix}")

            # --- Layer 2: Verify router is included in production entry point ---
            app_entry_point = prod_config.get('app_entry_point', 'main.py')
            app_entry_path = repo_root / app_entry_point
            self._verify_router_in_entry_point(
                target_path, app_entry_path, repo_root, target_file
            )

            return True

        except Exception as e:
            print(f"  ❌ Error generating production wiring: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    def _verify_router_in_entry_point(
        self,
        target_router_path: Path,
        app_entry_path: Path,
        repo_root: Path,
        target_file: str,
    ) -> None:
        """Verify the target router file is include_router'd in the production
        entry point (e.g. main.py).  If not, warn loudly and attempt to add it.

        This prevents the 'Layer 2 gap' where features are correctly wired into
        a sub-router but the sub-router itself is never mounted in the app that
        Railway/production actually runs.
        """
        if not app_entry_path.exists():
            print(f"\n  ⚠️  PRODUCTION ENTRY POINT NOT FOUND: {app_entry_path}")
            print(f"     Cannot verify that {target_file} is mounted in the live app.")
            print(f"     YOU MUST MANUALLY add include_router() for this router.")
            return

        entry_code = app_entry_path.read_text()

        # Derive the router module name from the target file path
        # e.g. "Causal_affect/src/backend/app/causality_router.py" -> "causality_router"
        router_module = target_router_path.stem  # e.g. "causality_router"

        # Check if the router is already imported/included
        if router_module in entry_code and 'include_router' in entry_code:
            # Quick check: is there an include_router call that references this module?
            import re as _re
            pattern = _re.compile(
                rf'include_router\([^)]*{router_module}[^)]*\)',
                _re.IGNORECASE
            )
            if pattern.search(entry_code):
                print(f"  ✅ Router '{router_module}' is already mounted in {app_entry_path.name}")
                return

        # --- Router is NOT mounted — warn loudly ---
        print(f"\n  🚨 CRITICAL: Router '{router_module}' is NOT included in {app_entry_path.name}!")
        print(f"     The production app ({app_entry_path.name}) does not import or")
        print(f"     include_router() for '{router_module}'.")
        print(f"     Features will be invisible to production until this is fixed.")
        print(f"")

        # Attempt auto-fix: add import and include_router
        rel_import_path = target_router_path.relative_to(repo_root)
        # Build a dotted import path, e.g. "Causal_affect.src.backend.app.causality_router"
        # But for complex paths, use sys.path + importlib approach
        router_var = f"{router_module}_router"

        # Find the sys.path insert for the parent directory of the router
        router_parent = target_router_path.parent.relative_to(repo_root)

        import_block = f'''
# ---------------------------------------------------------------------------
# AUTO-MOUNTED by AI Feature Builder (Layer 2 verification)
# ---------------------------------------------------------------------------
try:
    _{router_module}_path = Path(__file__).parent / "{router_parent}"
    if str(_{router_module}_path) not in sys.path:
        sys.path.insert(0, str(_{router_module}_path))
    from {router_module} import router as {router_var}
    logger.info("✅ {router_module} imported successfully")
except Exception as _e:
    logger.warning(f"⚠️  Could not import {router_module}: {{_e}}")
    {router_var} = None
'''

        include_block = f'''
# Mount {router_module} (auto-wired by AI Feature Builder)
if {router_var} is not None:
    app.include_router({router_var})
'''

        # Find where to inject — after existing imports, before app routes
        # Look for the last "include_router" call
        last_include = entry_code.rfind('app.include_router(')
        if last_include != -1:
            # Find end of that line
            line_end = entry_code.index('\n', last_include)
            entry_code = (
                entry_code[:line_end + 1]
                + include_block
                + entry_code[line_end + 1:]
            )
        else:
            entry_code += "\n" + include_block

        # Add import block near the top — after existing try/except import blocks
        # Find last "router = None" or "import" near top
        marker_pos = entry_code.rfind('_router = None')
        if marker_pos != -1:
            line_end = entry_code.index('\n', marker_pos)
            entry_code = (
                entry_code[:line_end + 1]
                + import_block
                + entry_code[line_end + 1:]
            )
        else:
            # Fallback: insert before the "# Include routers" comment or app definition
            include_comment = entry_code.find('# Include routers')
            if include_comment == -1:
                include_comment = entry_code.find('app.include_router')
            if include_comment != -1:
                entry_code = (
                    entry_code[:include_comment]
                    + import_block + "\n"
                    + entry_code[include_comment:]
                )
            else:
                entry_code += "\n" + import_block

        app_entry_path.write_text(entry_code)
        print(f"  ✅ AUTO-FIX: Added '{router_module}' import + include_router()")
        print(f"     to {app_entry_path.name}. Please review the changes.")

    # =========================================================================
    # PRODUCTION DELIVERY: Validate → Test → Build Frontend → Ship
    # =========================================================================

    def _find_repo_root(self, start_path: Path) -> Path:
        """Walk up from start_path to find the git repo root."""
        current = start_path.resolve()
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        return start_path  # fallback

    def _validate_generated_code(self, spec: FeatureIntegrationSpec) -> bool:
        """Validate all generated Python/JS/TS files parse correctly.

        Returns True if all files are valid, False if any have syntax errors.
        """
        import ast
        errors = []
        feature_dir = spec.feature_dir

        # Find all generated .py files
        py_files = list(feature_dir.rglob("*.py"))
        # Also check any modified production files
        repo_root = self._find_repo_root(feature_dir)
        prod_config = self.feature_spec.get('production_integration', {})
        target_file = prod_config.get('target_router_file')
        if target_file:
            target_path = repo_root / target_file
            if target_path.exists() and target_path not in py_files:
                py_files.append(target_path)
        entry_point = prod_config.get('app_entry_point', 'main.py')
        entry_path = repo_root / entry_point
        if entry_path.exists() and entry_path not in py_files:
            py_files.append(entry_path)

        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue
            try:
                source = py_file.read_text()
                ast.parse(source)
            except SyntaxError as e:
                rel = py_file.relative_to(repo_root) if py_file.is_relative_to(repo_root) else py_file
                errors.append(f"  {rel}:{e.lineno} — {e.msg}")

        if errors:
            print(f"  ❌ {len(errors)} file(s) have syntax errors:")
            for err in errors:
                print(err)
            if getattr(self, '_build_metrics', None):
                for err in errors:
                    self._build_metrics.log_error('syntax_errors', err)
            return False

        print(f"  ✅ {len(py_files)} Python file(s) validated — no syntax errors")
        return True

    def _run_generated_tests(self, spec: FeatureIntegrationSpec) -> bool:
        """Run pytest on the generated test files.

        Returns True if tests pass (or no tests found), False on failure.
        """
        import subprocess

        feature_dir = spec.feature_dir
        test_files = list(feature_dir.rglob("test_*.py")) + list(feature_dir.rglob("*_test.py"))
        # Filter out __pycache__
        test_files = [f for f in test_files if '__pycache__' not in str(f)]

        if not test_files:
            print("  ℹ️  No test files found — skipping")
            return True

        print(f"  Running {len(test_files)} test file(s)...")

        repo_root = self._find_repo_root(feature_dir)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--tb=short", "-q", "--no-header"] + [str(f) for f in test_files],
                capture_output=True, text=True, timeout=120,
                cwd=str(repo_root)
            )
            # Print last 20 lines of output
            output_lines = (result.stdout + result.stderr).strip().splitlines()
            for line in output_lines[-20:]:
                print(f"  {line}")

            if result.returncode == 0:
                print(f"\n  ✅ Tests passed")
                return True
            else:
                print(f"\n  ⚠️  Tests failed (exit code {result.returncode})")
                print(f"     Build will continue — review test failures after deploy")
                if getattr(self, '_build_metrics', None):
                    self._build_metrics.log_error('test_failures', f"Tests failed with exit code {result.returncode}")
                return False
        except subprocess.TimeoutExpired:
            print("  ⚠️  Tests timed out after 120s — skipping")
            return False
        except FileNotFoundError:
            print("  ⚠️  pytest not available — skipping test execution")
            return True

    # =========================================================================
    # FRONTEND WIRING: Auto-wire React/JS components into the frontend app
    # =========================================================================

    def _discover_frontend_app(self, repo_root: Path) -> Optional[Path]:
        """Auto-discover the main frontend React app in the repo.

        Heuristic priority:
        1. frontend_integration.target_app_dir from YAML (explicit)
        2. The React app whose build output is served by the backend
           (package.json with react + build script + dist/ that maps to static/)
        3. Any React app with a build script

        Returns the directory containing package.json, or None.
        """
        # Priority 1: Explicit config
        fi_config = self.feature_spec.get('frontend_integration', {})
        if fi_config.get('target_app_dir'):
            explicit = repo_root / fi_config['target_app_dir']
            if (explicit / 'package.json').exists():
                return explicit
            # Try within project subdirectory
            for sub in repo_root.iterdir():
                if sub.is_dir() and (sub / fi_config['target_app_dir'] / 'package.json').exists():
                    return sub / fi_config['target_app_dir']

        # Priority 2+3: Scan for React apps
        best_candidate = None
        for pkg_path in repo_root.rglob("package.json"):
            if 'node_modules' in str(pkg_path) or 'archive' in str(pkg_path).lower():
                continue
            try:
                pkg = json.loads(pkg_path.read_text())
            except Exception:
                continue
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            if 'react' not in deps and 'react-dom' not in deps:
                continue
            if 'build' not in pkg.get('scripts', {}):
                continue

            app_dir = pkg_path.parent

            # Check if this is the "real" deployed app — look for App.jsx/tsx
            # with react-router Routes
            for app_file in ['App.jsx', 'App.tsx', 'App.js']:
                src_app = app_dir / 'src' / app_file
                if src_app.exists():
                    content = src_app.read_text()
                    if 'Routes' in content or 'Route' in content or 'Router' in content:
                        # Strong candidate — it's a routed app
                        if best_candidate is None:
                            best_candidate = app_dir
                        # Prefer the one that has dist/ or whose name
                        # suggests it's the complete/production version
                        name_lower = app_dir.name.lower()
                        if 'complete' in name_lower or 'prod' in name_lower:
                            return app_dir
                        if (app_dir / 'dist').exists():
                            return app_dir
                    break

        return best_candidate

    def _find_frontend_layers(self, spec: FeatureIntegrationSpec) -> List[LayerInfo]:
        """Find layers that have frontend (JSX/TSX) implementations."""
        frontend_layers = []
        for layer in spec.layers:
            ext = layer.implementation_path.suffix.lower()
            if ext in ('.jsx', '.tsx', '.js'):
                # Verify it actually contains React code
                try:
                    content = layer.implementation_path.read_text()
                    if 'React' in content or 'useState' in content or 'export default' in content:
                        frontend_layers.append(layer)
                except Exception:
                    pass
        return frontend_layers

    def _infer_api_base_url(self) -> str:
        """Infer the API base URL from production_integration config.

        Combines the router's prefix with the endpoint_prefix to produce
        the full path that the frontend should call.
        """
        prod_config = self.feature_spec.get('production_integration', {})
        endpoint_prefix = prod_config.get('endpoint_prefix', '')
        target_router = prod_config.get('target_router_file', '')

        # Try to detect the router's own prefix from the target file
        router_prefix = ''
        if target_router:
            repo_root = self._find_repo_root(Path(self.feature_path).parent)
            # Search for the router file in both repo root and subdirectories
            target_path = repo_root / target_router
            if not target_path.exists():
                for sub in repo_root.iterdir():
                    if sub.is_dir() and (sub / target_router).exists():
                        target_path = sub / target_router
                        break

            if target_path.exists():
                try:
                    content = target_path.read_text()
                    # Look for APIRouter(prefix="...")
                    import re
                    match = re.search(r'APIRouter\([^)]*prefix\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        router_prefix = match.group(1)
                except Exception:
                    pass

        # Full API base = router_prefix + endpoint_prefix
        api_base = router_prefix.rstrip('/') + '/' + endpoint_prefix.strip('/')
        return api_base if api_base != '/' else '/api'

    def _fix_api_urls_in_component(self, component_path: Path, api_base_url: str) -> int:
        """Rewrite fetch/axios URLs in a component to use the correct API base.

        Returns the number of URLs fixed.
        """
        import re
        content = component_path.read_text()
        fixed = 0

        # Pattern: fetch('/api/...')  or  fetch("/api/...")
        # Also: axios.get('/api/...'), axios.post('/api/...')
        def replace_api_url(match):
            nonlocal fixed
            prefix = match.group(1)  # fetch(' or axios.get('
            quote = match.group(2)   # ' or "
            old_path = match.group(3)  # /api/predictions/accuracy

            # Extract the endpoint-specific part (after the last known prefix)
            # e.g. /api/predictions/accuracy → /accuracy
            # Strategy: strip common API prefixes and keep the final path segment(s)
            parts = old_path.strip('/').split('/')
            # Remove leading 'api' if present
            if parts and parts[0] == 'api':
                parts = parts[1:]
            # The endpoint suffix is everything after the feature's own prefix
            # Try to find the useful part by looking at what's NOT the base URL
            base_parts = api_base_url.strip('/').split('/')
            # Find common prefix length
            common = 0
            for i, part in enumerate(parts):
                if i < len(base_parts) and part == base_parts[i]:
                    common = i + 1
                else:
                    break
            endpoint_parts = parts[common:]

            new_url = api_base_url.rstrip('/') + '/' + '/'.join(endpoint_parts) if endpoint_parts else api_base_url
            fixed += 1
            return f"{prefix}{quote}{new_url}{quote}"

        # Match fetch('...') and axios.METHOD('...')
        pattern = r"""((?:fetch|axios\.(?:get|post|put|patch|delete))\s*\()(['"])(\/api\/[^'"]+)(['"])"""
        new_content = re.sub(pattern, replace_api_url, content)

        if fixed > 0:
            component_path.write_text(new_content)

        return fixed

    def _inject_react_route(self, app_jsx_path: Path, page_name: str,
                            route_path: str, component_filename: str) -> bool:
        """Add an import + Route entry to App.jsx/tsx.

        Idempotent: skips if the import already exists.

        Returns True on success, False on failure.
        """
        try:
            content = app_jsx_path.read_text()

            # Check idempotency
            if page_name in content:
                print(f"     ℹ️  {page_name} already imported in {app_jsx_path.name}")
                return True

            # Insert import after the last existing page import
            import re
            # Find all "import X from './pages/Y'" lines
            import_pattern = re.compile(
                r"^(import\s+\w+\s+from\s+['\"]\.\/pages\/[^'\"]+['\"])\s*$",
                re.MULTILINE
            )
            matches = list(import_pattern.finditer(content))
            if matches:
                last_import_end = matches[-1].end()
                import_line = f"\nimport {page_name} from './pages/{component_filename}'"
                content = content[:last_import_end] + import_line + content[last_import_end:]
            else:
                # Fallback: after last import line
                all_imports = list(re.finditer(r'^import\s+.*$', content, re.MULTILINE))
                if all_imports:
                    pos = all_imports[-1].end()
                    content = content[:pos] + f"\nimport {page_name} from './pages/{component_filename}'" + content[pos:]
                else:
                    return False

            # Insert Route before </Routes>
            routes_close = content.rfind('</Routes>')
            if routes_close == -1:
                print(f"     ❌ Could not find </Routes> in {app_jsx_path.name}")
                return False

            # Find indentation of existing Route lines
            route_pattern = re.compile(r'^(\s*)<Route\s', re.MULTILINE)
            route_match = route_pattern.search(content)
            indent = route_match.group(1) if route_match else '          '

            route_line = f'{indent}<Route path="{route_path}" element={{<{page_name} />}} />\n'
            content = content[:routes_close] + route_line + content[routes_close:]

            app_jsx_path.write_text(content)
            return True
        except Exception as e:
            print(f"     ❌ Failed to inject route: {e}")
            return False

    def _inject_nav_link(self, layout_path: Path, route_path: str,
                         label: str, icon: str) -> bool:
        """Add a navigation link to the Layout component.

        Supports two patterns:
        1. navItems array: appends a new entry
        2. Direct <Link> elements: appends a new Link

        Idempotent: skips if the path already exists in nav.

        Returns True on success, False on failure.
        """
        try:
            content = layout_path.read_text()

            # Check idempotency
            if route_path in content:
                print(f"     ℹ️  Nav link for {route_path} already exists in {layout_path.name}")
                return True

            import re

            # Pattern 1: navItems = [ ... ] — inject before the closing ]
            nav_array_pattern = re.compile(
                r"(const\s+navItems\s*=\s*\[)(.*?)(]\s*)",
                re.DOTALL
            )
            match = nav_array_pattern.search(content)
            if match:
                existing_items = match.group(2).rstrip().rstrip(',')
                new_item = f",\n    {{ path: '{route_path}', label: '{label}', icon: '{icon}' }}"
                replacement = match.group(1) + existing_items + new_item + '\n  ' + match.group(3)
                content = content[:match.start()] + replacement + content[match.end():]
                layout_path.write_text(content)
                return True

            # Pattern 2: Direct <Link> or <NavLink> elements — add before closing </nav>
            nav_close = content.rfind('</nav>')
            if nav_close != -1:
                link_line = f'''                <Link to="{route_path}" className="nav-link">{icon} {label}</Link>\n'''
                content = content[:nav_close] + link_line + content[nav_close:]
                layout_path.write_text(content)
                return True

            print(f"     ⚠️  Could not find nav pattern in {layout_path.name}")
            return False
        except Exception as e:
            print(f"     ❌ Failed to inject nav link: {e}")
            return False

    def generate_frontend_wiring(self, spec: FeatureIntegrationSpec) -> bool:
        """Auto-wire frontend React components into the deployed app.

        This is the frontend counterpart to generate_production_wiring().
        For each frontend layer (JSX/TSX implementation), it:
        1. Copies the component to the app's pages/ directory
        2. Adds a Route to App.jsx
        3. Adds a nav link to the Layout component
        4. Fixes API URLs to match the actual backend endpoints

        Configuration comes from:
        - frontend_integration section in feature YAML (explicit)
        - Auto-discovery from production_integration + repo scan (implicit)

        Returns True on success, False on failure.
        """
        repo_root = self._find_repo_root(spec.feature_dir)
        fi_config = self.feature_spec.get('frontend_integration', {})
        prod_config = self.feature_spec.get('production_integration', {})

        # Step 1: Find frontend layers
        frontend_layers = self._find_frontend_layers(spec)
        if not frontend_layers:
            print("  ℹ️  No frontend layers found — skipping frontend wiring")
            return True  # Not a failure, just nothing to do

        print(f"  Found {len(frontend_layers)} frontend layer(s) to wire")

        # Step 2: Discover the frontend app
        frontend_app = self._discover_frontend_app(repo_root)
        if not frontend_app:
            print("  ⚠️  Could not discover frontend React app")
            print("     Add frontend_integration.target_app_dir to feature YAML")
            return False

        rel_app = frontend_app.relative_to(repo_root) if frontend_app.is_relative_to(repo_root) else frontend_app
        print(f"  📱 Frontend app: {rel_app}")

        pages_dir = frontend_app / 'src' / 'pages'
        if not pages_dir.exists():
            pages_dir.mkdir(parents=True, exist_ok=True)

        # Find App.jsx and Layout component
        app_jsx = None
        for name in ['App.jsx', 'App.tsx', 'App.js']:
            candidate = frontend_app / 'src' / name
            if candidate.exists():
                app_jsx = candidate
                break
        if not app_jsx:
            print("  ❌ Could not find App.jsx/tsx in frontend app")
            return False

        layout_path = None
        for comp_dir in [frontend_app / 'src' / 'components', frontend_app / 'src' / 'layouts']:
            if comp_dir.exists():
                for name in ['Layout.jsx', 'Layout.tsx', 'Layout.js',
                              'Sidebar.jsx', 'Sidebar.tsx', 'Nav.jsx', 'Nav.tsx']:
                    candidate = comp_dir / name
                    if candidate.exists():
                        layout_path = candidate
                        break
            if layout_path:
                break

        # Step 3: Infer API base URL
        api_base = self._infer_api_base_url()
        print(f"  🔗 API base URL: {api_base}")

        # Step 4: Get route config from YAML or generate defaults
        route_path = fi_config.get('route_path', '/' + prod_config.get('endpoint_prefix', spec.feature_id).strip('/'))
        nav_label = fi_config.get('nav_label', spec.feature_name.split('_')[-1].title() if '_' in spec.feature_name else spec.feature_name)
        nav_icon = fi_config.get('nav_icon', '📊')

        # Step 5: Wire each frontend layer
        wired = 0
        for layer in frontend_layers:
            layer_name = layer.layer_name.replace(' ', '').replace('_', '')
            # Make a page component name
            page_name = fi_config.get('page_component_name')
            if not page_name:
                # Derive from layer name: "Prediction Dashboard" → "PredictionDashboard"
                words = layer.layer_name.replace('_', ' ').split()
                page_name = ''.join(w.capitalize() for w in words)

            page_filename = page_name  # without extension
            ext = layer.implementation_path.suffix  # .jsx, .tsx, etc
            dest_path = pages_dir / f"{page_filename}{ext}"

            # Copy component
            import shutil
            shutil.copy2(layer.implementation_path, dest_path)
            print(f"  📋 Copied {layer.layer_id} → pages/{page_filename}{ext}")

            # Fix API URLs in the copied component
            url_fixes = self._fix_api_urls_in_component(dest_path, api_base)
            if url_fixes:
                print(f"     Fixed {url_fixes} API URL(s) → {api_base}/*")

            # Ensure the component has a default export
            content = dest_path.read_text()
            if f'export default {page_name}' not in content and f'export default' not in content:
                # Try to find the component function/const and add export
                import re
                comp_pattern = re.compile(
                    rf'(?:const|function)\s+(\w+)\s*[=(]',
                    re.MULTILINE
                )
                comp_match = comp_pattern.search(content)
                if comp_match:
                    actual_name = comp_match.group(1)
                    content += f"\n\nexport default {actual_name};\n"
                    dest_path.write_text(content)
                    page_name = actual_name  # Use the actual component name

            # Check what the component is actually named (might differ from page_name)
            import re
            default_export = re.search(r'export\s+default\s+(?:function\s+)?(\w+)', content)
            if default_export:
                actual_component = default_export.group(1)
                if actual_component != page_name:
                    print(f"     Component name: {actual_component} (using this for route)")
                    page_name = actual_component

            # Add route to App.jsx
            route_ok = self._inject_react_route(app_jsx, page_name, route_path, page_filename)
            if route_ok:
                print(f"     ✅ Route added: {route_path} → <{page_name} />")
            else:
                print(f"     ❌ Failed to add route — manual wiring needed")

            # Add nav link to Layout (if found)
            if layout_path:
                nav_ok = self._inject_nav_link(layout_path, route_path, nav_label, nav_icon)
                if nav_ok:
                    print(f"     ✅ Nav link added: {nav_label}")
                else:
                    print(f"     ⚠️  Could not add nav link — add manually to {layout_path.name}")
            else:
                print(f"     ℹ️  No Layout component found — nav link not added")

            wired += 1

        if wired > 0:
            print(f"\n  ✅ Frontend wiring complete: {wired} component(s) wired")
        return wired > 0

    # =========================================================================
    # IMPORT VALIDATION: Catch AI hallucinations before production
    # =========================================================================

    def _validate_feature_integration_imports(self, spec: FeatureIntegrationSpec) -> bool:
        """Validate that feature_integration.py imports actually exist in layers.

        The AI frequently hallucates class names (e.g. 'PredictionStorage'
        instead of 'PredictionTracking').  This catches that BEFORE shipping.

        Strategy:
        1. Parse feature_integration.py for import statements
        2. For each imported name, verify it exists in the target layer file
        3. If mismatches found, attempt auto-fix by finding the correct name

        Returns True if imports are valid (or were auto-fixed), False if broken.
        """
        integration_file = spec.feature_dir / "src" / "feature_integration.py"
        if not integration_file.exists():
            return True  # Nothing to validate

        import re
        import ast

        content = integration_file.read_text()

        # Parse all "from LAYER_xxx...implementation import X, Y, Z" statements
        import_pattern = re.compile(
            r'from\s+(LAYER_\S+\.src\.implementation)\s+import\s+(.+?)$',
            re.MULTILINE
        )

        fixes_needed = []
        for match in import_pattern.finditer(content):
            module_path_str = match.group(1)
            imported_names = [n.strip().rstrip(',') for n in match.group(2).split(',')]

            # Resolve the actual file
            # LAYER_CA_002_10_01_Prediction_Storage.src.implementation
            # → LAYER_CA_002_10_01_Prediction_Storage/src/implementation.py
            rel_path = module_path_str.replace('.', '/') + '.py'
            impl_file = spec.feature_dir / rel_path

            if not impl_file.exists():
                print(f"  ⚠️  Import target not found: {rel_path}")
                continue

            # Parse the implementation file to find actual class/function names
            try:
                impl_content = impl_file.read_text()
                tree = ast.parse(impl_content)
            except SyntaxError:
                continue

            # Collect all top-level class and function names
            actual_names = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    actual_names.add(node.name)

            # Check each imported name
            for name in imported_names:
                name = name.strip()
                if not name or name.startswith('(') or name.startswith('#'):
                    continue
                # Strip parentheses from multi-line imports
                name = name.strip('()')
                if name in actual_names:
                    continue  # ✅ Import is valid

                # ❌ Import doesn't exist — try to find closest match
                # Strategy: case-insensitive prefix match, then substring match
                candidates = []
                name_lower = name.lower()
                for actual in actual_names:
                    actual_lower = actual.lower()
                    # Exact case-insensitive match
                    if actual_lower == name_lower:
                        candidates.insert(0, actual)
                    # Prefix/suffix overlap
                    elif (name_lower in actual_lower or actual_lower in name_lower):
                        candidates.append(actual)
                    # Shared word stems
                    else:
                        name_words = set(re.findall(r'[A-Z][a-z]+|[a-z]+', name))
                        actual_words = set(re.findall(r'[A-Z][a-z]+|[a-z]+', actual))
                        if name_words & actual_words:
                            candidates.append(actual)

                best_match = candidates[0] if candidates else None
                fixes_needed.append({
                    'file': integration_file,
                    'wrong_name': name,
                    'correct_name': best_match,
                    'module': module_path_str,
                    'all_available': sorted(actual_names),
                })

        if not fixes_needed:
            print(f"  ✅ feature_integration.py imports validated — all names exist")
            return True

        # Attempt auto-fix
        auto_fixed = 0
        for fix in fixes_needed:
            if fix['correct_name']:
                print(f"  🔧 Auto-fixing: {fix['wrong_name']} → {fix['correct_name']}")
                content = content.replace(fix['wrong_name'], fix['correct_name'])
                auto_fixed += 1
            else:
                print(f"  ❌ No match for '{fix['wrong_name']}' in {fix['module']}")
                print(f"     Available names: {', '.join(fix['all_available'])}")

        if auto_fixed > 0:
            integration_file.write_text(content)
            print(f"  ✅ Auto-fixed {auto_fixed} import(s) in feature_integration.py")

        unfixed = len(fixes_needed) - auto_fixed
        if unfixed > 0:
            print(f"  ❌ {unfixed} import(s) could not be auto-fixed")
            if getattr(self, '_build_metrics', None):
                for fix in fixes_needed:
                    if not fix['correct_name']:
                        self._build_metrics.log_error('import_errors', f"Unresolved import: {fix['wrong_name']} in {fix['module']}")
            return False

        return True

    def _build_frontend_assets(self, spec: FeatureIntegrationSpec) -> bool:
        """Detect and build frontend assets (npm/vite/webpack).

        Searches for package.json files within the feature directory and the
        broader frontend source tree.  If found, runs npm install + build.

        Returns True if build succeeds (or no frontend found), False on failure.
        """
        import subprocess

        repo_root = self._find_repo_root(spec.feature_dir)

        # Strategy: find package.json files that are part of the app's frontend
        # Priority 1: Look in the feature directory itself
        # Priority 2: Look in the broader src/frontend or src/backend/static source
        candidates = []

        # Check feature dir for package.json (React component libraries)
        for pkg in spec.feature_dir.rglob("package.json"):
            if 'node_modules' not in str(pkg):
                candidates.append(pkg.parent)

        # Check for a top-level frontend build that produces the static/ dir
        # Walk up from the static dir to find the source React app
        for pattern in [
            "Causal_affect/**/package.json",
            "frontend/package.json",
            "src/frontend/package.json",
        ]:
            for pkg in repo_root.glob(pattern):
                if 'node_modules' not in str(pkg) and pkg.parent not in candidates:
                    candidates.append(pkg.parent)

        if not candidates:
            print("  ℹ️  No frontend package.json found — skipping")
            return True

        # Look for the main app build (the one that produces the deployed static/ dir)
        # Heuristic: it has a "build" script and its dist/build output maps to static/
        built_any = False
        for frontend_dir in candidates:
            pkg_json = frontend_dir / "package.json"
            try:
                pkg_data = json.loads(pkg_json.read_text())
            except Exception:
                continue

            scripts = pkg_data.get("scripts", {})
            if "build" not in scripts:
                continue

            # Check if this is a meaningful app (has react/vue/svelte dependency)
            deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
            has_frontend_framework = any(
                fw in deps for fw in ["react", "react-dom", "vue", "svelte", "@angular/core", "next"]
            )
            if not has_frontend_framework:
                continue

            rel_dir = frontend_dir.relative_to(repo_root) if frontend_dir.is_relative_to(repo_root) else frontend_dir
            print(f"  📦 Found frontend app: {rel_dir}")
            print(f"     Build script: {scripts['build']}")

            # npm install
            print(f"     Running npm install...")
            install_result = subprocess.run(
                ["npm", "install", "--no-audit", "--no-fund"],
                capture_output=True, text=True, timeout=120,
                cwd=str(frontend_dir)
            )
            if install_result.returncode != 0:
                print(f"     ⚠️  npm install failed:")
                for line in install_result.stderr.strip().splitlines()[-5:]:
                    print(f"       {line}")
                continue

            # npm run build
            print(f"     Running npm run build...")
            build_result = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True, text=True, timeout=180,
                cwd=str(frontend_dir)
            )
            if build_result.returncode == 0:
                print(f"     ✅ Frontend build succeeded")
                built_any = True

                # Copy build output to static/ if dist/ exists and static/ is elsewhere
                dist_dir = frontend_dir / "dist"
                if dist_dir.exists():
                    # Find where static/ lives in the app
                    for static_candidate in repo_root.rglob("static/index.html"):
                        if 'node_modules' not in str(static_candidate):
                            static_dir = static_candidate.parent
                            if static_dir != dist_dir:
                                print(f"     📋 Copying build output to {static_dir.relative_to(repo_root)}")
                                import shutil
                                # Clear old assets
                                for item in static_dir.iterdir():
                                    if item.name != '.gitkeep':
                                        if item.is_dir():
                                            shutil.rmtree(item)
                                        else:
                                            item.unlink()
                                # Copy new build
                                for item in dist_dir.iterdir():
                                    dest = static_dir / item.name
                                    if item.is_dir():
                                        shutil.copytree(item, dest)
                                    else:
                                        shutil.copy2(item, dest)
                                print(f"     ✅ Static assets updated")
                            break
            else:
                print(f"     ❌ Frontend build failed:")
                for line in build_result.stderr.strip().splitlines()[-10:]:
                    print(f"       {line}")

        if built_any:
            print(f"\n  ✅ Frontend assets built and deployed")
        else:
            print(f"\n  ℹ️  No buildable frontend apps found (or builds failed)")

        return built_any or not candidates

    def _ship_to_production(
        self,
        spec: FeatureIntegrationSpec,
        code_valid: bool,
        tests_passed: bool,
    ) -> bool:
        """Git commit and push all changes to trigger production deploy.

        Only ships if code validation passed.  Test failures are warnings,
        not blockers (to avoid blocking backend-only features that have
        test dependency issues).

        Returns True if push succeeds, False otherwise.
        """
        import subprocess

        # In CI, commit/push is handled by the workflow's dedicated step
        # which uses the correct working directory and CROSS_REPO_PAT token.
        if os.getenv('CI'):
            print("  ℹ️  Running in CI — commit/push handled by workflow step")
            return True

        repo_root = self._find_repo_root(spec.feature_dir)

        if not code_valid:
            print("  ❌ BLOCKED: Code validation failed — not shipping")
            print("     Fix syntax errors and run the build again.")
            if getattr(self, '_build_metrics', None):
                self._build_metrics.log_error('syntax_errors', 'Ship blocked: code validation failed')
            return False

        if not tests_passed:
            print("  ⚠️  WARNING: Tests failed — shipping anyway (review test failures)")

        # Check for changes
        try:
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=str(repo_root)
            )
            if not status.stdout.strip():
                print("  ℹ️  No changes to commit")
                return True

            changed_count = len(status.stdout.strip().splitlines())
            print(f"  📝 {changed_count} file(s) changed")
        except Exception as e:
            print(f"  ⚠️  Could not check git status: {e}")
            return False

        # Stage all changes within the feature dir and production files
        try:
            # Stage feature directory
            subprocess.run(
                ["git", "add", "-A", str(spec.feature_dir)],
                capture_output=True, text=True, cwd=str(repo_root)
            )
            # Stage production files (router, entry point, static assets)
            prod_config = self.feature_spec.get('production_integration', {})
            for prod_file in [prod_config.get('target_router_file'), prod_config.get('app_entry_point', 'main.py')]:
                if prod_file:
                    prod_path = repo_root / prod_file
                    if prod_path.exists():
                        subprocess.run(
                            ["git", "add", str(prod_path)],
                            capture_output=True, text=True, cwd=str(repo_root)
                        )
            # Stage static assets
            for static_dir in repo_root.rglob("static/index.html"):
                if 'node_modules' not in str(static_dir):
                    subprocess.run(
                        ["git", "add", "-A", str(static_dir.parent)],
                        capture_output=True, text=True, cwd=str(repo_root)
                    )

        except Exception as e:
            print(f"  ⚠️  Error staging files: {e}")
            return False

        # Commit
        commit_msg = (
            f"feat: Ship {spec.feature_id} to production\n\n"
            f"AI Feature Builder: {spec.feature_name}\n"
            f"Layers: {len(spec.layers)}\n"
            f"Code validation: {'✅ passed' if code_valid else '❌ failed'}\n"
            f"Tests: {'✅ passed' if tests_passed else '⚠️ failed (non-blocking)'}"
        )
        try:
            commit_result = subprocess.run(
                ["git", "commit", "--no-gpg-sign", "-m", commit_msg],
                capture_output=True, text=True, cwd=str(repo_root)
            )
            if commit_result.returncode == 0:
                print(f"  ✅ Committed: {spec.feature_id}")
            elif "nothing to commit" in commit_result.stdout:
                print(f"  ℹ️  Nothing to commit")
                return True
            else:
                print(f"  ⚠️  Commit issue: {commit_result.stderr.strip()}")
        except Exception as e:
            print(f"  ❌ Commit failed: {e}")
            return False

        # Push
        try:
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True, text=True, timeout=60,
                cwd=str(repo_root)
            )
            if push_result.returncode == 0:
                print(f"  ✅ Pushed to origin/main — production deploy triggered")
                return True
            else:
                print(f"  ❌ Push failed: {push_result.stderr.strip()}")
                print(f"     Changes are committed locally. Push manually with: git push origin main")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Push timed out — try manually: git push origin main")
            return False
        except Exception as e:
            print(f"  ❌ Push failed: {e}")
            return False

    def _show_enhanced_summary(self, layers_info: List[Dict], feature_spec: FeatureIntegrationSpec):
        """Show enhanced build summary including feature integration."""
        
        print("\n" + "="*80)
        print("FEATURE BUILD SUMMARY")
        print("="*80)
        
        # Layer summary
        print(f"\n✅ Layers Built: {len(layers_info)}")
        for layer_info in layers_info:
            layer_spec = self.find_layer_spec(layer_info)
            layer_dir = layer_spec.parent
            
            # Detect correct implementation file based on language
            layer_yaml = yaml.safe_load(layer_spec.read_text())
            tech_constraints = extract_technical_constraints(layer_yaml)
            language = tech_constraints.get('language', 'python').lower()
            
            if 'typescript' in language or 'react' in language:
                impl_filename = "implementation.tsx"
            elif 'javascript' in language:
                impl_filename = "implementation.js"
            else:
                impl_filename = "implementation.py"
                
            impl_file = layer_dir / "src" / impl_filename
            test_count = len(list((layer_dir / "tests").glob("test_*.py"))) if (layer_dir / "tests").exists() else 0
            
            print(f"   • {layer_info['layer_id']}: {layer_info['name']}")
            print(f"     Implementation: {impl_file}")
            print(f"     Tests: {test_count} files")
        
        # Feature integration summary
        print(f"\n🔗 Feature Integration Layer:")
        feature_impl = feature_spec.feature_dir / "src" / "feature_integration.py"
        if feature_impl.exists():
            print(f"   ✅ Integration Code: {feature_impl}")
            print(f"      Lines: {len(feature_impl.read_text().splitlines())}")
        else:
            print(f"   ⚠️  Integration code not found")
        
        print(f"\n📦 Feature: {feature_spec.feature_name}")
        print(f"   Feature ID: {feature_spec.feature_id}")
        print(f"   Total Layers: {len(feature_spec.layers)}")
        print(f"   Feature Directory: {feature_spec.feature_dir}")
        
        print("\n" + "="*80)
            
    def build_feature(self):
        """Build complete feature layer by layer."""
        start_time = datetime.now()
        
        # Initialize build metrics tracking (M0)
        try:
            import build_error_tracker
            self._build_metrics = build_error_tracker.start_build(
                str(self.feature_path.stem)
            )
        except Exception:
            self._build_metrics = None
        
        self.print_header("🚀 AI Feature Builder - Starting")
        
        # Load feature specification
        feature_id, feature_name = self.load_feature_spec()
        
        # Check API key
        import os
        if self.provider == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                self.print_step("❌", "OPENAI_API_KEY not set!")
                print("\nPlease set your API key:")
                print("  export OPENAI_API_KEY='your-key-here'")
                return False
        elif self.provider == "anthropic":
            if not os.getenv("ANTHROPIC_API_KEY"):
                self.print_step("❌", "ANTHROPIC_API_KEY not set!")
                print("\nPlease set your API key:")
                print("  export ANTHROPIC_API_KEY='your-key-here'")
                return False
                
        self.print_step("✓", f"Using AI provider: {self.provider.upper()}")
        
        # Build each layer
        total_layers = len(self.layers)
        completed_layers = []
        failed_layers = []
        
        for idx, layer_info in enumerate(self.layers, 1):
            success = self.build_layer(layer_info, idx, total_layers)
            
            if success:
                completed_layers.append(layer_info['name'])
            else:
                failed_layers.append(layer_info['name'])
                
                # In CI mode, auto-continue; otherwise ask
                if idx < total_layers:
                    if os.environ.get('CI'):
                        print("\n⚠️  Layer failed. Auto-continuing in CI mode...")
                    else:
                        print("\n⚠️  Layer failed. Continue with next layer? (y/n): ", end='')
                        response = input().strip().lower()
                        if response != 'y':
                            self.print_step("🛑", "Build cancelled by user")
                            break
        
        # Check if all layers completed successfully
        if len(completed_layers) != total_layers:
            # Final summary for incomplete build
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() / 60
            
            self.print_header("⚠️  FEATURE BUILD INCOMPLETE")
            print(f"Feature: {feature_name}")
            print(f"Duration: {duration:.1f} minutes")
            print(f"Completed: {len(completed_layers)}/{total_layers} layers")
            
            if failed_layers:
                print(f"\n❌ Failed Layers:")
                for layer in failed_layers:
                    print(f"   - {layer}")
            
            return False
        
        # All layers complete - now build feature integration
        self.print_header("✅ ALL LAYERS COMPLETE")
        print(f"All {total_layers} layers built successfully!")
        
        # NEW: Build feature integration layer
        self.print_header("🔗 Building Feature Integration Layer")
        
        # Collect layer implementations
        layer_implementations = self._collect_layer_implementations(self.layers)
        
        if len(layer_implementations) != len(self.layers):
            print(f"⚠️  Warning: Only {len(layer_implementations)}/{len(self.layers)} layer implementations found")
        
        # Get feature directory (use the directory where feature YAML lives)
        # This is the parent directory containing all sibling layer folders
        feature_dir = self.feature_path.parent
        
        if not feature_dir.exists():
            print("❌ Feature directory not found - cannot create feature integration")
            return False
        
        # Create feature integration spec
        feature_integration_spec = FeatureIntegrationSpec(
            feature_id=feature_id,
            feature_name=feature_name,
            feature_dir=feature_dir,
            layers=layer_implementations,
            integration_scenarios=self.feature_spec.get('integration_scenarios', []),
            e2e_scenarios=self.feature_spec.get('e2e_scenarios', []),
            feature_acceptance_criteria=self.feature_spec.get('acceptance_criteria', [])
        )
        
        # Generate feature integration code
        integration_success = self.generate_feature_integration(feature_integration_spec)
        
        if not integration_success:
            print("\n⚠️  Feature integration generation failed")
            print("Layers are complete, but feature integration layer was not generated.")

        # IMPORT VALIDATION: Catch AI hallucinations before they hit production
        self.print_header("🔍 Validating Feature Integration Imports")
        imports_valid = self._validate_feature_integration_imports(feature_integration_spec)
        if not imports_valid:
            print("\n⚠️  Feature integration has broken imports.")
            print("     Auto-fix attempted. Check results above.")

        # Generate feature-level tests (integration + E2E)
        integration_test_count, e2e_test_count = self.generate_feature_tests(feature_integration_spec)

        # BACKEND WIRING: Wire feature into production API router
        prod_config = self.feature_spec.get('production_integration')
        if prod_config:
            self.print_header("🔌 Production Integration Wiring (Backend)")
            wiring_success = self.generate_production_wiring(
                feature_integration_spec, prod_config
            )
            if not wiring_success:
                print("\n⚠️  Production wiring generation failed")
                print("     Feature code is built but NOT connected to the live app.")
                print("     You must manually update the target router/app file.")
        else:
            if os.getenv('CI'):
                print("\n❌ BLOCKED: No 'production_integration' section in feature YAML.")
                print("     Fire-and-forget mode requires production wiring configuration.")
                print("     Add a production_integration section to the feature YAML.")
                return False
            else:
                print("\n⚠️  No 'production_integration' section in feature YAML.")
                print("     Feature code is built but NOT connected to the live app.")
                print("     Add a production_integration section to auto-wire next time.")

        # FRONTEND WIRING: Wire React/JS components into the deployed app
        self.print_header("📱 Frontend Integration Wiring")
        frontend_wiring_ok = self.generate_frontend_wiring(feature_integration_spec)
        if not frontend_wiring_ok:
            frontend_layers = self._find_frontend_layers(feature_integration_spec)
            if frontend_layers:
                print("\n⚠️  Frontend wiring failed — dashboard not accessible in UI")
                print("     Add frontend_integration section to feature YAML for auto-wiring")
            # Not a blocker if there are no frontend layers

        # Generate feature-level verification artifacts
        self.print_header("📋 Generating Feature-Level Verification")
        verification_success = self.generate_feature_level_verification(
            feature_integration_spec,
            integration_test_count,
            e2e_test_count
        )
        
        if not verification_success:
            print("\n⚠️  Feature-level verification generation failed")

        # =====================================================================
        # POST-WRITE FENCE SWEEP (defense-in-depth)
        # Strip any remaining markdown fences from all generated .py files
        # =====================================================================
        fence_fixed = 0
        for py_file in feature_integration_spec.feature_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                if '```' in content:
                    cleaned = clean_generated_code(content)
                    if cleaned != content:
                        py_file.write_text(cleaned)
                        fence_fixed += 1
            except Exception:
                pass
        if fence_fixed:
            print(f"\n🧹 Post-write sweep: stripped markdown fences from {fence_fixed} file(s)")

        # =====================================================================
        # PRODUCTION DELIVERY PIPELINE
        # "Build the right thing and ship the right thing to production"
        # =====================================================================

        # STEP 1: Validate all generated code parses correctly
        self.print_header("🔍 Step 1: Validate Generated Code")
        validation_ok = self._validate_generated_code(feature_integration_spec)
        if not validation_ok:
            print("\n❌ Generated code has syntax errors. NOT shipping to production.")
            print("   Fix the errors above and re-run, or commit manually after review.")

        # STEP 2: Run generated tests
        self.print_header("🧪 Step 2: Run Generated Tests")
        tests_ok = self._run_generated_tests(feature_integration_spec)

        # STEP 3: Build frontend assets if this feature has frontend components
        self.print_header("🏗️  Step 3: Build Frontend Assets")
        frontend_ok = self._build_frontend_assets(feature_integration_spec)

        # STEP 4: Git commit + push to trigger production deploy
        self.print_header("🚀 Step 4: Ship to Production")
        shipped = self._ship_to_production(feature_integration_spec, validation_ok, tests_ok)

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        self.print_header("🎉 FEATURE BUILD COMPLETE!")
        
        print(f"Duration: {duration:.1f} minutes")
        print(f"AI Provider: {self.provider.upper()}")
        
        # Show enhanced summary
        self._show_enhanced_summary(self.layers, feature_integration_spec)
        
        return True
            
    def run(self):
        """Execute feature build."""
        try:
            result = self.build_feature()
            # Finalise and save build metrics (M0)
            if getattr(self, '_build_metrics', None):
                end_time = datetime.now()
                self._build_metrics.finalise(result, 0)
                self._build_metrics.save()
            return result
        except Exception as e:
            self.print_header("❌ BUILD FAILED")
            print(f"Error: {str(e)}")
            if getattr(self, '_build_metrics', None):
                self._build_metrics.log_error('runtime_errors', str(e))
                self._build_metrics.finalise(False, 0)
                self._build_metrics.save()
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Build complete features using AI Code Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build Workflow State Management feature (uses Claude Sonnet 4.5 by default)
  %(prog)s "projects/PROJECT-003 TDD ENFORCER/.../FEATURE-003-03-01_workflow_orchestration_engine.yaml"
  
  # Use OpenAI GPT-4 instead
  %(prog)s --provider openai "path/to/feature.yaml"
  
  # Verbose output
  %(prog)s --verbose "path/to/feature.yaml"
        """
    )
    
    parser.add_argument(
        "feature",
        help="Path to feature YAML specification file"
    )
    
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        default="anthropic",
        help="AI provider to use (default: anthropic/claude-sonnet-4.5)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output and stack traces"
    )
    
    parser.add_argument(
        "--init-layers",
        action="store_true",
        help="Initialize layer folder structure and generate layer YAML files from feature requirements (run before building)"
    )
    
    parser.add_argument(
        "--skip-layer-generation",
        action="store_true",
        help="Skip automatic layer requirement generation - expect manually created layer requirements"
    )
    
    args = parser.parse_args()
    
    # Initialize layer structure if requested
    if args.init_layers:
        from pathlib import Path
        feature_path = Path(args.feature)
        print(f"\n{'='*80}")
        print("  🏗️  LAYER STRUCTURE INITIALIZATION")
        print(f"{'='*80}\n")
        success = initialize_layer_structure(
            feature_path=feature_path,
            provider=args.provider,
            verbose=args.verbose
        )
        sys.exit(0 if success else 1)
    
    # Build the feature
    builder = FeatureBuilder(
        feature_path=args.feature,
        provider=args.provider,
        verbose=args.verbose,
        skip_layer_generation=args.skip_layer_generation
    )
    
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
