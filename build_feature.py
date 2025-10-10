#!/usr/bin/env python3
"""
AI Code Generator - Feature Builder
Single command to build complete features layer by layer
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import yaml
import json


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
        """Find layer specification file."""
        layer_file = layer_info.get('requirement_file')
        if not layer_file:
            raise ValueError(f"No requirement file specified for {layer_info['layer_id']}")
            
        # Search in same directory as feature spec
        # Directory structure: LAYER-XXX-XX-XX-XX LayerName/LAYER-XXX-XX-XX-XX_layer_name.yaml
        layer_dir = f"{layer_info['layer_id']} {layer_info['name']}"
        layer_path = self.feature_path.parent / layer_dir / layer_file
        
        if not layer_path.exists():
            raise FileNotFoundError(f"Layer spec not found: {layer_path}")
            
        return layer_path
        
    def build_layer(self, layer_info: dict, layer_number: int, total_layers: int) -> bool:
        """Build a single layer using AI Code Generator."""
        self.print_header(f"Building Layer {layer_number}/{total_layers}: {layer_info['name']}")
        
        layer_spec = self.find_layer_spec(layer_info)
        self.print_step("✓", f"Layer spec: {layer_spec}")
        
        # Prepare output directory for this layer
        layer_output = self.output_dir / layer_info['layer_id']
        layer_output.mkdir(parents=True, exist_ok=True)
        
        self.print_step("✓", f"Output directory: {layer_output}")
        
        # Import and use the AI Code Generator
        sys.path.insert(0, str(Path("/workspaces/control_tower/projects/PROJECT-004 AI CODE GENERATOR/SYSTEM-004-01 AI CODE GENERATION SYSTEM")))
        
        try:
            from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
            
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
                        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        self.print_header("📊 Feature Build Summary")
        
        print(f"Feature: {feature_name}")
        print(f"Feature ID: {feature_id}")
        print(f"Duration: {duration:.1f} minutes")
        print(f"AI Provider: {self.provider.upper()}")
        print()
        
        print(f"✅ Completed Layers: {len(completed_layers)}/{total_layers}")
        for layer in completed_layers:
            print(f"   - {layer}")
            
        if failed_layers:
            print(f"\n❌ Failed Layers: {len(failed_layers)}")
            for layer in failed_layers:
                print(f"   - {layer}")
                
        print(f"\n📁 Output Directory: {self.output_dir}")
        
        # Overall result
        if len(completed_layers) == total_layers:
            self.print_header("🎉 FEATURE BUILD COMPLETE!")
            print(f"All {total_layers} layers built successfully!")
            print(f"\nYou can find the generated code in:")
            print(f"  {self.output_dir}")
            return True
        else:
            self.print_header("⚠️  FEATURE BUILD INCOMPLETE")
            print(f"{len(completed_layers)}/{total_layers} layers completed")
            return False
            
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
