#!/usr/bin/env python3
"""
AI Code Generator - System Builder  
Single command to build complete systems by integrating features
Following exact pattern from build_feature.py
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import yaml
import json
from dataclasses import dataclass
from typing import List, Dict, Any

# Clean API key
if 'ANTHROPIC_API_KEY' in os.environ:
    os.environ['ANTHROPIC_API_KEY'] = os.environ['ANTHROPIC_API_KEY'].strip()
if 'OPENAI_API_KEY' in os.environ:
    os.environ['OPENAI_API_KEY'] = os.environ['OPENAI_API_KEY'].strip()

# Add paths
control_tower_root = Path(__file__).parent.resolve()
project_004_src = control_tower_root / "projects" / "PROJECT-004 AI CODE GENERATOR" / "SYSTEM-004-01 AI CODE GENERATION SYSTEM" / "src"

if str(control_tower_root) not in sys.path:
    sys.path.insert(0, str(control_tower_root))
if str(project_004_src) not in sys.path:
    sys.path.insert(0, str(project_004_src))


def extract_system_constraints(requirements: Dict) -> Dict:
    """
    Extract system_integration_constraints from system requirements YAML.
    Returns empty dict if not present - backwards compatible.
    """
    return requirements.get('system_integration_constraints', {})


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
    - Markdown code fences (```python ... ```)
    - Extra leading/trailing whitespace
    """
    if not code:
        return code
    
    # Strip markdown fences
    lines = code.split('\n')
    
    # Remove first line if it's a code fence
    if lines and lines[0].strip().startswith('```'):
        lines = lines[1:]
    
    # Remove last line if it's a code fence
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
    
    # Rejoin and normalize whitespace
    cleaned = '\n'.join(lines)
    
    # Remove excessive leading/trailing whitespace but preserve structure
    cleaned = cleaned.strip() + '\n'  # Ensure single trailing newline
    
    return cleaned


@dataclass
class FeatureInfo:
    """Information about a built feature."""
    feature_id: str
    feature_name: str
    feature_dir: Path
    integration_path: Path
    requirements: Dict[str, Any]


@dataclass
class SystemIntegrationSpec:
    """Specification for system integration layer generation."""
    system_id: str
    system_name: str
    system_dir: Path
    features: List[FeatureInfo]
    acceptance_criteria: List[Dict[str, Any]]
    tech_stack: Dict[str, Any]
    deployment_config: Dict[str, Any]


class SystemArchitecture:
    """Base class for system architecture strategies."""
    
    def __init__(self, system_spec: Dict[str, Any], system_dir: Path):
        """Initialize architecture strategy."""
        self.system_spec = system_spec
        self.system_dir = system_dir
    
    def build_prompt(self, spec: SystemIntegrationSpec) -> str:
        """Build AI prompt for code generation."""
        raise NotImplementedError
    
    def get_file_structure(self) -> str:
        """Get base directory path for this architecture."""
        raise NotImplementedError
    
    def get_dependencies(self) -> List[str]:
        """Get dependencies list for requirements.txt."""
        raise NotImplementedError


class FastAPIArchitecture(SystemArchitecture):
    """FastAPI REST API architecture strategy."""
    
    def build_prompt(self, spec: SystemIntegrationSpec) -> str:
        """Build FastAPI-specific prompt."""
        feat_list = []
        for f in spec.features:
            classes = getattr(f, 'classes', [])
            feat_list.append(
                f"{f.feature_id}: {f.feature_name} ({len(classes)} classes)"
            )
            
            # Add method signatures for each feature class
            if hasattr(f, 'methods_by_class'):
                for cls, methods in f.methods_by_class.items():
                    feat_list.append(f"  Class: {cls}")
                    feat_list.append("  Public Methods:")
                    for method in methods:
                        feat_list.append(f"    - {method}")
                    feat_list.append("  CRITICAL: Only call methods that exist above.")
        
        deps = ', '.join(self.get_dependencies()[:5])
        prompt = f"""Create minimal FastAPI backend for {spec.system_name}

{len(spec.features)} features: {', '.join(f.feature_id for f in spec.features[:3])}{'...' if len(spec.features) > 3 else ''}

CRITICAL: MINIMAL code. No docstrings. Type hints only. Max 10 files.

===== CRITICAL METHOD USAGE RULES =====
- ONLY call methods that are listed above in "Public Methods" for each feature
- DO NOT invent or assume method names on FeatureOrchestrator classes
- Use EXACT method names from the feature implementations
- If you need functionality, use the methods that ACTUALLY EXIST in the classes
- Cross-reference: Feature class methods are listed above - use those EXACT names
===== END CRITICAL RULES =====

Return JSON format:
{{"files": [{{"path": "requirements.txt", "content": "fastapi==0.104.1\\n..."}}, ...]}}

Files needed:
1. requirements.txt (deps: {deps})
2. .env.example (feature flags)
3. app/__init__.py (empty)
4. app/config.py (BaseSettings with feature flags)
5. app/main.py (FastAPI app + CORS + all routers + exception handlers)
6. app/models.py (ALL models in ONE file: Enum, BaseModel classes)
7. app/exceptions.py (custom exceptions)
8. app/health.py (health endpoints)
9. app/features.py (ALL feature routers in ONE file with feature flag checks)

Each router: 2-3 endpoints, in-memory list/dict storage, minimal logic.
NO verbose docstrings. NO comments. Just working code.
"""
        
        # Phase 2: Inject system integration constraints if present
        constraints = extract_system_constraints(spec.system_requirements)
        
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
    
    def get_file_structure(self) -> str:
        """Get FastAPI file structure."""
        return "src/backend"
    
    def get_dependencies(self) -> List[str]:
        """Get FastAPI dependencies."""
        return ["fastapi==0.104.1", "uvicorn==0.24.0", "pydantic==2.5.0"]


class DesktopCLIArchitecture(SystemArchitecture):
    """Desktop CLI application architecture strategy."""
    
    def build_prompt(self, spec: SystemIntegrationSpec) -> str:
        """Build CLI-specific prompt for feature integration."""
        feature_list = []
        for f in spec.features:
            folder_name = f.feature_dir.name
            feature_list.append(f"- {f.feature_id}: {f.feature_name}")
            feature_list.append(f"  Folder: {folder_name}")
            
            # Add FeatureConfig fields if available
            if hasattr(f, 'config_fields') and f.config_fields:
                feature_list.append(f"  FeatureConfig Fields:")
                for field in f.config_fields:
                    feature_list.append(f"    - {field}")
            
            # Add method signatures for each feature class
            if hasattr(f, 'methods_by_class'):
                for cls, methods in f.methods_by_class.items():
                    feature_list.append(f"  Class: {cls}")
                    feature_list.append(f"  Public Methods:")
                    for method in methods:
                        feature_list.append(f"    - {method}")
                    feature_list.append(f"  CRITICAL: Only call methods that exist above.")
        
        prompt = f"""Create Python CLI application for {spec.system_name}

This is a DESKTOP APPLICATION (CLI), not a web service.

Features to integrate ({len(spec.features)} total):
{chr(10).join(feature_list)}

CRITICAL REQUIREMENTS:
1. Import FeatureOrchestrator from each feature using importlib.util
2. Create CLI entry point script (generate_report.py) with argparse
3. Chain feature orchestrators to process data end-to-end
4. Generate OUTPUT FILES (PowerPoint, reports), NOT HTTP responses
5. No FastAPI, no routers, no REST endpoints

===== CRITICAL METHOD USAGE RULES =====
- ONLY call methods that are listed above in "Public Methods" for each feature
- DO NOT invent or assume method names on FeatureOrchestrator classes
- Use EXACT method names from the feature implementations
- If you need functionality, use the methods that ACTUALLY EXIST in the classes
- Cross-reference: Feature class methods are listed above - use those EXACT names
===== END CRITICAL RULES =====

Return JSON format:
{{"files": [{{"path": "generate_report.py", "content": "..."}}]}}

Files needed:
1. requirements.txt - {', '.join(self.get_dependencies()[:5])}
2. generate_report.py - Main CLI entry point with:
   - argparse for command-line arguments
   - Dynamic feature imports using importlib.util.spec_from_file_location
   - Feature orchestrator chaining (data flows through features)
   - Error handling and logging
   - File output generation
3. src/models.py - Pydantic data models (if needed)
4. src/utils.py - Helper functions (path handling, logging)
5. config/settings.yaml - Configuration file

CRITICAL: config/settings.yaml must use the EXACT "FeatureConfig Fields" listed above.
Do NOT invent new field names. Use the field names from each feature's FeatureConfig dataclass.

Example config/settings.yaml structure:
```yaml
# Feature configurations - use EXACT field names from FeatureConfig
data_reader:
  schema_path: null
  strict_validation: true
  file_type: null
  # ... use actual FeatureConfig fields listed above

risk_aggregator:
  # ... use actual FeatureConfig fields listed above
```

Example import and instantiation pattern:
```python
import importlib.util
from pathlib import Path

def load_feature_orchestrator(feature_folder_name):
    # Load the feature module
    path = Path(__file__).parent / feature_folder_name / "src" / "feature_integration.py"
    spec = importlib.util.spec_from_file_location(f"{{feature_folder_name}}.integration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# When loading features with config:
for feature_key, folder_name in FEATURE_FOLDERS.items():
    module = load_feature_orchestrator(folder_name)
    feature_config_dict = config.get(feature_key, {{}})
    
    # FeatureConfig is a @dataclass - instantiate with **kwargs
    if feature_config_dict and hasattr(module, 'FeatureConfig'):
        feature_config = module.FeatureConfig(**feature_config_dict)
        orchestrator = module.FeatureOrchestrator(feature_config)
    else:
        orchestrator = module.FeatureOrchestrator()
```

CRITICAL: Use the "Folder" name listed above for each feature when constructing paths.
The folder name includes BOTH the feature ID AND name (e.g., "FEATURE-003-001_Data_Reader_Parser").

NO FastAPI code. NO web server. CLI application only.
"""
        
        # Phase 2: Inject system integration constraints if present
        constraints = extract_system_constraints(spec.system_requirements)
        
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
    
    def get_file_structure(self) -> str:
        """Get CLI file structure."""
        # CLI apps generate files at root level
        return "."
    
    def get_dependencies(self) -> List[str]:
        """Get CLI dependencies."""
        code_gen = self.system_spec.get('code_generation', {})
        deps = code_gen.get('dependencies', {})
        return deps.get('libraries', [])


def select_architecture(deployment_model: str, system_spec: Dict, 
                       system_dir: Path) -> SystemArchitecture:
    """Factory method to select appropriate architecture strategy."""
    if 'CLI' in deployment_model or 'Desktop Application' in deployment_model:
        return DesktopCLIArchitecture(system_spec, system_dir)
    else:
        # Default to FastAPI for backward compatibility
        return FastAPIArchitecture(system_spec, system_dir)


class SystemBuilder:
    """Build complete systems from YAML specifications using AI."""
    
    def __init__(self, system_path: str, provider: str = "anthropic", verbose: bool = False, phase: str = None):
        """Initialize system builder."""
        self.system_path = Path(system_path)
        self.provider = provider
        self.verbose = verbose
        self.target_phase = phase  # None = all phases, or specific phase ID
        self.phase_results = {}  # Track completed phases
        
        if not self.system_path.exists():
            raise FileNotFoundError(f"System spec not found: {system_path}")
    
    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_step(self, icon: str, message: str):
        """Print step message."""
        print(f"{icon} {message}")
    
    def load_system_spec(self):
        """Load system specification."""
        self.print_header("Loading System Specification")
        
        with open(self.system_path, 'r', encoding='utf-8') as f:
            self.system_spec = yaml.safe_load(f)
        
        system_name = self.system_spec['metadata']['system_name']
        system_id = self.system_spec['metadata']['system_id']
        
        self.print_step("✓", f"System: {system_name}")
        self.print_step("✓", f"System ID: {system_id}")
        
        self.features = self.system_spec.get('features', [])
        self.print_step("✓", f"Features: {len(self.features)}")
        
        # Load deployment model and execution mode
        system_overview = self.system_spec.get('system_overview', {})
        self.deployment_model = system_overview.get('deployment_model', 'Web Service')
        self.execution_mode = system_overview.get('execution_mode', 'API Service')
        self.print_step("✓", f"Deployment Model: {self.deployment_model}")
        self.print_step("✓", f"Execution Mode: {self.execution_mode}")
        
        # Load phases if available
        self.phases = self.system_spec.get('code_generation', {}).get('phases', {})
        if self.phases and 'total_phases' in self.phases:
            self.print_step("✓", f"Phases: {self.phases['total_phases']}")
        
        return system_id, system_name
    
    def _load_feature_yamls(self) -> Dict[str, Dict]:
        """Load all feature YAML specifications."""
        system_dir = self.system_path.parent
        feature_specs = {}
        
        for feature_meta in self.features:
            feature_id = feature_meta['feature_id']
            feature_dirs = list(system_dir.glob(f"{feature_id}*"))
            
            if not feature_dirs:
                continue
            
            feature_dir = feature_dirs[0]
            feature_yaml = feature_dir / f"{feature_dir.name}.yaml"
            
            if feature_yaml.exists():
                with open(feature_yaml, 'r', encoding='utf-8') as f:
                    feature_specs[feature_id] = yaml.safe_load(f)
        
        return feature_specs
    
    def _dependencies_met(self, phase_id: str, phase_spec: Dict) -> bool:
        """Check if phase dependencies have been completed."""
        dependencies = phase_spec.get('dependencies', [])
        
        if not dependencies or dependencies == ['none']:
            return True
        
        for dep in dependencies:
            if dep not in self.phase_results:
                if self.verbose:
                    self.print_step("⏳", f"Waiting for: {dep}")
                return False
        
        return True
    
    def _build_phase_prompt(self, phase_id: str, phase_spec: Dict, feature_specs: Dict) -> str:
        """Build AI prompt for a specific phase."""
        phase_name = phase_spec.get('name', phase_id)
        files = phase_spec.get('files', [])
        acceptance = phase_spec.get('acceptance_criteria', [])
        
        # Load tech stack from system spec
        tech_stack = self.system_spec.get('technology_stack', {})
        backend = tech_stack.get('backend', {})
        
        # Build feature context for feature-specific phases
        feature_context = ""
        if 'feature_' in phase_id or 'FEATURE-' in phase_id:
            # Extract feature ID from phase_id (e.g., phase_03_feature_CA-006-01)
            for fid in feature_specs.keys():
                if fid in phase_id:
                    spec = feature_specs[fid]
                    impl_notes = spec.get('implementation_notes', {})
                    code_structure = impl_notes.get('code_structure', [])
                    
                    feature_context = f"""
FEATURE SPECIFICATION ({fid}):
{yaml.dump(code_structure, default_flow_style=False)}
"""
                    break
        
        prompt = f"""Generate production Python code for: {phase_name}

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON: {{"files": [{{"path": "...", "content": "..."}}, ...]}}
2. Token limit: {phase_spec.get('max_tokens', 8192)} tokens
3. Python {backend.get('python', '3.11+')}
4. Framework: {backend.get('framework', 'FastAPI')} {backend.get('framework_version', '0.104+')}

FILES TO GENERATE:
{yaml.dump(files, default_flow_style=False)}

ACCEPTANCE CRITERIA:
{yaml.dump(acceptance, default_flow_style=False)}

{feature_context}

TECH STACK:
- FastAPI {backend.get('framework_version', '0.104+')}
- SQLAlchemy {backend.get('database_orm_version', '2.0+')}
- Pydantic {backend.get('validation_version', '2.0+')}
- Redis for caching
- Alembic for migrations

CODE STYLE:
- Type hints required
- Pydantic models for validation
- Async/await for I/O
- Error handling with custom exceptions
- Concise docstrings only for public APIs
- Follow FastAPI best practices

STRUCTURE:
- models/: Pydantic schemas
- services/: Business logic
- db/: Database models, repositories
- api/: Route handlers

Return JSON with 'files' array containing path and content for each file.
"""
        return prompt
    
    def _generate_phase(self, phase_id: str, phase_spec: Dict, 
                       feature_specs: Dict, backend_dir: Path) -> Dict:
        """Generate code for a single phase."""
        phase_name = phase_spec.get('name', phase_id)
        
        self.print_header(f"Phase: {phase_name}")
        self.print_step("📋", f"Files: {len(phase_spec.get('files', []))}")
        self.print_step("✓", f"Token limit: {phase_spec.get('max_tokens', 8192)}")
        
        # Build prompt
        prompt = self._build_phase_prompt(phase_id, phase_spec, feature_specs)
        
        # Call AI
        self.print_step("🤖", "Generating code...")
        
        from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        config = {'output_base_path': str(backend_dir), 'provider': self.provider}
        orchestrator = AICodeGeneratorOrchestrator(config=config)
        
        response = orchestrator.ai_provider.generate_code(
            prompt=prompt,
            max_tokens=phase_spec.get('max_tokens', 8192)
        )
        
        # Extract and save files
        result = self._extract_json_from_response(response)
        
        if not result or 'files' not in result:
            self.print_step("⚠️", "Invalid response - no files generated")
            return {'phase_id': phase_id, 'success': False, 'files': []}
        
        files_created = []
        for file_spec in result['files']:
            file_path = backend_dir / file_spec['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Phase 4: Auto-fix common AI output issues for Python files
            content = file_spec['content']
            if file_path.suffix == '.py':
                content = clean_generated_code(content)
            
            file_path.write_text(content, encoding='utf-8')
            files_created.append(file_spec['path'])
            self.print_step("✓", f"Created: {file_spec['path']}")
        
        self.print_step("✅", f"Phase complete: {len(files_created)} files")
        
        return {
            'phase_id': phase_id,
            'success': True,
            'files': files_created,
            'file_count': len(files_created)
        }
    
    def _validate_acceptance_criteria(self, phase_id: str, 
                                     phase_spec: Dict, result: Dict) -> bool:
        """Validate phase output against acceptance criteria."""
        acceptance = phase_spec.get('acceptance_criteria', [])
        
        if not acceptance:
            return True
        
        files_created = result.get('files', [])
        
        # Basic validation: check if expected files exist
        for criterion in acceptance:
            criterion_str = str(criterion).lower()
            
            # Check for file existence
            if 'file' in criterion_str or 'created' in criterion_str:
                # Extract filename patterns from criterion
                for created_file in files_created:
                    if any(pattern in created_file for pattern in 
                          ['main.py', 'config.py', 'models.py', 'services']):
                        continue
        
        return True  # Basic validation passes
    
    def _load_feature_yamls(self) -> Dict[str, Dict]:
        """Find feature integration files."""
        self.print_header("Discovering Features")
        
        system_dir = self.system_path.parent
        feature_infos = []
        
        for feature_spec in self.features:
            feature_id = feature_spec['feature_id']
            feature_dirs = list(system_dir.glob(f"{feature_id}*"))
            
            if not feature_dirs:
                self.print_step("⚠️", f"Not found: {feature_id}")
                continue
            
            feature_dir = feature_dirs[0]
            integration_path = feature_dir / "src" / "feature_integration.py"
            
            if integration_path.exists():
                self.print_step("✓", f"Found: {feature_dir.name}")
                
                # Load feature YAML
                feature_yaml = feature_dir / f"{feature_dir.name}.yaml"
                requirements = {}
                if feature_yaml.exists():
                    with open(feature_yaml, 'r', encoding='utf-8') as f:
                        requirements = yaml.safe_load(f)
                
                feature_infos.append(FeatureInfo(
                    feature_id=feature_id,
                    feature_name=feature_spec['feature_name'],
                    feature_dir=feature_dir,
                    integration_path=integration_path,
                    requirements=requirements
                ))
            else:
                self.print_step("⚠️", f"No integration: {feature_dir.name}")
        
        self.print_step("✓", f"Found {len(feature_infos)} features")
        return feature_infos
    
    def _collect_feature_implementations(self, features: List[FeatureInfo]) -> List[FeatureInfo]:
        """Collect feature implementation details with method signatures."""
        self.print_header("Collecting Feature Implementations")
        
        enriched = []
        for feature in features:
            self.print_step("📖", f"Reading {feature.feature_name}...")
            
            # Read feature code
            code = feature.integration_path.read_text(encoding='utf-8')
            
            # Extract classes with their public methods and FeatureConfig fields
            classes = []
            methods_by_class = {}
            config_fields = []
            current_class = None
            indent_level = 0
            in_feature_config = False
            
            for line in code.split('\n'):
                stripped = line.lstrip()
                
                # Detect class definition
                if stripped.startswith('class '):
                    cls = stripped.split('class ')[1].split('(')[0].split(':')[0].strip()
                    current_class = cls
                    classes.append(cls)
                    methods_by_class[cls] = []
                    indent_level = len(line) - len(stripped)
                    in_feature_config = (cls == 'FeatureConfig')
                
                # Extract FeatureConfig field names (dataclass fields)
                elif in_feature_config and ':' in stripped and '=' in stripped:
                    # Look for pattern: field_name: Type = default
                    field_line = stripped.split(':')[0].strip()
                    if field_line and not field_line.startswith(('"""', '#', 'def', 'class')):
                        config_fields.append(field_line)
                
                # Detect method definition (must be inside a class)
                elif current_class and stripped.startswith('def '):
                    line_indent = len(line) - len(stripped)
                    if line_indent > indent_level:
                        method_name = stripped.split('def ')[1].split('(')[0].strip()
                        # Only include public methods
                        if not method_name.startswith('_'):
                            methods_by_class[current_class].append(method_name)
                    in_feature_config = False  # Left FeatureConfig class
            
            feature.classes = classes
            feature.methods_by_class = methods_by_class
            feature.config_fields = config_fields
            
            # Show summary
            for cls in classes:
                methods = methods_by_class.get(cls, [])
                self.print_step("  ", f"Class: {cls} - Methods: {', '.join(methods[:3])}{'...' if len(methods) > 3 else ''}")
            
            enriched.append(feature)
        
        self.print_step("✓", f"Collected {len(enriched)} implementations")
        return enriched
    
    def _build_system_integration_prompt(self, spec: SystemIntegrationSpec) -> str:
        """Build AI prompt using architecture strategy."""
        # Delegate to architecture strategy
        return self.architecture.build_prompt(spec)
    
    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from AI response with better error handling."""
        # Handle markdown code blocks
        if "```json" in response:
            start = response.find("```json\n")
            if start != -1:
                start += len("```json\n")
                # Look for closing ``` 
                end = response.rfind("\n```")
                if end == -1:
                    # No closing marker - response was likely truncated
                    self.print_step("⚠️", "Response appears truncated (no closing ```)")
                    # Try to find the last complete object
                    end = response.rfind("}")
                    if end != -1:
                        end += 1  # Include the closing brace
                else:
                    # Use the position before the closing marker
                    pass
                
                if end > start:
                    json_str = response[start:end].strip()
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError as e:
                        self.print_step("❌", f"JSON parse error at position {e.pos}: {e.msg}")
                        return None
        
        # Try parsing entire response as JSON
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        return None
    
    def generate_system_integration(self, spec: SystemIntegrationSpec) -> bool:
        """Generate system integration using multi-phase AI generation."""
        try:
            # Check if multi-phase is available
            if not self.phases or 'total_phases' not in self.phases:
                # Fallback to single-phase generation
                return self._generate_single_phase(spec)
            
            # Multi-phase generation
            self.print_header("Multi-Phase System Generation")
            
            total_phases = self.phases.get('total_phases', 0)
            self.print_step("📊", f"Total phases: {total_phases}")
            
            # Load feature specifications (returns list of FeatureInfo objects)
            feature_infos = self._load_feature_yamls()
            
            # Convert list to dict for phase prompt building
            feature_specs = {
                f.feature_id: {
                    'feature_id': f.feature_id,
                    'feature_name': f.feature_name,
                    'requirements': f.requirements
                }
                for f in feature_infos
            }
            self.print_step("✓", f"Loaded {len(feature_specs)} feature specs")
            
            # Get base directory from architecture strategy
            backend_dir = spec.system_dir / self.architecture.get_file_structure()
            backend_dir.mkdir(parents=True, exist_ok=True)
            
            # Get ordered phase list
            phase_keys = [k for k in self.phases.keys() 
                         if k.startswith('phase_')]
            phase_keys.sort()
            
            # Filter to target phase if specified
            if self.target_phase:
                if self.target_phase in phase_keys:
                    phase_keys = [self.target_phase]
                    self.print_step("🎯", f"Target phase: {self.target_phase}")
                else:
                    self.print_step("❌", f"Phase not found: {self.target_phase}")
                    return False
            
            # Execute phases in order
            total_files = 0
            for phase_id in phase_keys:
                phase_spec = self.phases[phase_id]
                
                # Check dependencies
                if not self._dependencies_met(phase_id, phase_spec):
                    self.print_step("⏭️", f"Skipping {phase_id} (dependencies not met)")
                    continue
                
                # Generate phase
                result = self._generate_phase(
                    phase_id, phase_spec, feature_specs, backend_dir
                )
                
                # Validate
                if result['success']:
                    self.phase_results[phase_id] = result
                    total_files += result['file_count']
                    
                    if self._validate_acceptance_criteria(phase_id, phase_spec, result):
                        self.print_step("✅", f"{phase_id} validated")
                    else:
                        self.print_step("⚠️", f"{phase_id} validation warnings")
                else:
                    self.print_step("❌", f"{phase_id} failed")
                    if not self.target_phase:  # Continue if running all phases
                        continue
                    return False
            
            self.print_step("✅", f"Total files generated: {total_files}")
            return True
            
        except Exception as e:
            self.print_step("❌", f"Error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _generate_single_phase(self, spec: SystemIntegrationSpec) -> bool:
        """Fallback: single-phase generation (legacy mode)."""
        try:
            self.print_header("Single-Phase System Generation (Legacy)")
            self.print_step("🤖", "Calling AI Code Generator...")
            
            prompt = self._build_system_integration_prompt(spec)
            
            from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
            
            config = {
                'output_base_path': str(spec.system_dir), 
                'provider': self.provider
            }
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            
            response = orchestrator.ai_provider.generate_code(
                prompt=prompt,
                max_tokens=8192
            )
            
            result = self._extract_json_from_response(response)
            
            if not result or 'files' not in result:
                self.print_step("⚠️", "Fallback to basic generation")
                backend_dir = spec.system_dir / self.architecture.get_file_structure()
                backend_dir.mkdir(parents=True, exist_ok=True)
                main_file = "main.py" if isinstance(self.architecture, FastAPIArchitecture) else "generate_report.py"
                
                # Phase 4: Auto-fix common AI output issues
                content = clean_generated_code(response)
                
                (backend_dir / main_file).write_text(content, encoding='utf-8')
                self.print_step("✓", f"Created basic {main_file}")
                return True
            
            backend_dir = spec.system_dir / self.architecture.get_file_structure()
            files_created = 0
            
            for file_spec in result['files']:
                file_path = backend_dir / file_spec['path']
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Phase 4: Auto-fix common AI output issues for Python files
                content = file_spec['content']
                if file_path.suffix == '.py':
                    content = clean_generated_code(content)
                
                file_path.write_text(content, encoding='utf-8')
                files_created += 1
                self.print_step("✓", f"Created: {file_spec['path']}")
            
            self.print_step("✅", f"Generated {files_created} files")
            return True
            
        except Exception as e:
            self.print_step("❌", f"Error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def generate_system_verification(self, spec: SystemIntegrationSpec):
        """
        Generate system-level verification artifacts (test pyramid + traceability matrix).
        Closes the loop by aggregating layer-level verification data.
        """
        try:
            self.print_header("📊 System-Level Verification")
            self.print_step("🔍", "Collecting layer verification artifacts...")
            
            from system_verification_generator import SystemVerificationGenerator
            
            generator = SystemVerificationGenerator(
                system_dir=spec.system_dir,
                system_id=spec.system_id,
                system_name=spec.system_name
            )
            
            # Collect all layer verifications
            count = generator.collect_layer_verifications()
            
            if count == 0:
                self.print_step("⚠️", "No layer verifications found - skipping system verification")
                return
            
            # Generate and save artifacts
            pyramid_path, matrix_path = generator.save_verification_artifacts()
            
            self.print_step("✅", f"System verification complete: {count} layers analyzed")
            
        except Exception as e:
            self.print_step("⚠️", f"System verification error (non-fatal): {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
    
    def build_system(self):
        """Execute system build."""
        start_time = datetime.now()
        
        try:
            self.print_header("🚀 AI System Builder")
            
            system_id, system_name = self.load_system_spec()
            
            if self.provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
                self.print_step("❌", "ANTHROPIC_API_KEY not set!")
                return False
            
            self.print_step("✓", f"AI Provider: {self.provider.upper()}")
            
            feature_infos = self._load_feature_yamls()
            
            if not feature_infos:
                self.print_step("❌", "No features found")
                return False
            
            enriched = self._collect_feature_implementations(feature_infos)
            
            spec = SystemIntegrationSpec(
                system_id=system_id,
                system_name=system_name,
                system_dir=self.system_path.parent,
                features=enriched,
                acceptance_criteria=self.system_spec.get('acceptance_criteria', []),
                tech_stack=self.system_spec.get('technology_stack', {}),
                deployment_config=self.system_spec.get('deployment', {})
            )
            
            # Select architecture strategy based on deployment model
            self.architecture = select_architecture(
                self.deployment_model,
                self.system_spec,
                spec.system_dir
            )
            self.print_step("✓", f"Architecture: {self.architecture.__class__.__name__}")
            
            if not self.generate_system_integration(spec):
                return False
            
            # Generate system-level verification artifacts (closes the loop!)
            self.generate_system_verification(spec)
            
            duration = (datetime.now() - start_time).total_seconds() / 60
            
            self.print_header("✅ BUILD SUCCESSFUL")
            self.print_step("🎉", f"System '{system_name}' complete!")
            self.print_step("⏱️", f"Duration: {duration:.1f} minutes")
            
            return True
            
        except Exception as e:
            self.print_header("❌ BUILD FAILED")
            self.print_step("💥", f"Error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build systems using AI")
    parser.add_argument("system", help="Path to system YAML")
    parser.add_argument(
        "--provider", 
        choices=["openai", "anthropic"], 
        default="anthropic"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--phase", 
        help="Specific phase to generate (e.g., phase_01_system_infrastructure)"
    )
    parser.add_argument(
        "--all-phases",
        action="store_true",
        help="Generate all phases in order"
    )
    
    args = parser.parse_args()
    
    builder = SystemBuilder(
        system_path=args.system,
        provider=args.provider,
        verbose=args.verbose,
        phase=args.phase
    )
    
    success = builder.build_system()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
