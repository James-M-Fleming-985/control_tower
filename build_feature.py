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
from dataclasses import dataclass
from typing import List, Dict, Any

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


@dataclass
class LayerInfo:
    """Information about a built layer."""
    layer_id: str
    layer_name: str
    layer_dir: Path
    implementation_path: Path
    requirements: Dict[str, Any]


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


class FeatureBuilder:
    """Build complete features from YAML specifications using AI."""
    
    def __init__(self, feature_path: str, provider: str = "anthropic", verbose: bool = False):
        """Initialize feature builder."""
        self.feature_path = Path(feature_path)
        self.provider = provider
        self.verbose = verbose
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
        """Find layer specification file with flexible directory pattern matching."""
        layer_file = layer_info.get('requirement_file')
        if not layer_file:
            raise ValueError(f"No requirement file specified for {layer_info['layer_id']}")
            
        layer_id = layer_info['layer_id']
        layer_name = layer_info.get('name', '')
        feature_dir = self.feature_path.parent
        
        # Try multiple directory patterns to support different repos
        # Pattern 1: LAYER-ID LayerName (control_tower pattern with space)
        # Pattern 2: LAYER-ID_LayerName (professional_excellence pattern with underscore)
        # Pattern 3: LAYER-ID (just the ID, if name is empty or matches directory)
        # Pattern 4: Exact match from layer_id (if it contains full dir name)
        
        patterns_to_try = []
        
        # If layer_id already contains separator (underscore or full name), use it directly
        if '_' in layer_id or not layer_name:
            patterns_to_try.append(layer_id)
        
        # Try with space separator (original control_tower pattern)
        if layer_name:
            patterns_to_try.append(f"{layer_id} {layer_name}")
        
        # Try with underscore separator (professional_excellence pattern)
        if layer_name:
            patterns_to_try.append(f"{layer_id}_{layer_name}")
        
        # Try just the layer_id
        patterns_to_try.append(layer_id)
        
        # Try to find the directory
        for pattern in patterns_to_try:
            layer_path = feature_dir / pattern / layer_file
            if layer_path.exists():
                return layer_path
        
        # If not found, try scanning the directory for any match containing layer_id
        try:
            for item in feature_dir.iterdir():
                if item.is_dir() and layer_id in item.name:
                    layer_path = item / layer_file
                    if layer_path.exists():
                        return layer_path
        except Exception:
            pass
        
        # Generate helpful error message with attempted patterns
        error_msg = f"Layer spec not found. Tried patterns:\n"
        for pattern in patterns_to_try:
            error_msg += f"  - {feature_dir / pattern / layer_file}\n"
        raise FileNotFoundError(error_msg)
        
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
            
            # Find implementation file
            impl_path = layer_dir / "src" / "implementation.py"
            
            if not impl_path.exists():
                print(f"⚠️  Warning: Implementation not found for {layer_id}")
                continue
            
            # Parse requirements from layer YAML
            layer_yaml = yaml.safe_load(layer_spec.read_text())
            
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
        
        # Format layer implementations
        layer_descriptions = []
        for layer in spec.layers:
            layer_code = layer.implementation_path.read_text()
            
            # Extract classes from implementation (simple parse)
            classes = []
            for line in layer_code.split('\n'):
                if line.startswith('class '):
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    classes.append(class_name)
            
            layer_descriptions.append(f"""
Layer: {layer.layer_name} ({layer.layer_id})
Location: {layer.implementation_path}
Classes: {', '.join(classes)}
Purpose: {layer.requirements.get('description', 'N/A')}
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

Generate ONLY the Python code for the feature integration module.
Use relative imports to access layer implementations.

Example import structure:
```python
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from {spec.layers[0].layer_id.replace(' ', '_').replace('-', '_').lower()}.src.implementation import ClassName
```

Generate the complete feature_integration.py module now:
"""
        
        return prompt
    
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
                max_tokens=6000
            )
            
            # Extract code from response
            code = self._extract_code_from_response(response)
            
            if not code:
                print("  ❌ Failed to extract code from AI response")
                return False
            
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
            impl_file = layer_dir / "src" / "implementation.py"
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
                
                # Ask if should continue
                if idx < total_layers:
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
        
        # Get feature directory (parent of first layer)
        if layer_implementations:
            feature_dir = layer_implementations[0].layer_dir.parent
        else:
            print("❌ No layer implementations found - cannot create feature integration")
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
            return self.build_feature()
        except Exception as e:
            self.print_header("❌ BUILD FAILED")
            print(f"Error: {str(e)}")
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
    
    args = parser.parse_args()
    
    # Build the feature
    builder = FeatureBuilder(
        feature_path=args.feature,
        provider=args.provider,
        verbose=args.verbose
    )
    
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
