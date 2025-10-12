#!/usr/bin/env python3
"""
Single command to run complete TDD cycle on a layer
"""
import sys
import os
from pathlib import Path

# Clean the API key (remove any whitespace/newlines)
if 'ANTHROPIC_API_KEY' in os.environ:
    os.environ['ANTHROPIC_API_KEY'] = os.environ['ANTHROPIC_API_KEY'].strip()

# Add PROJECT-004 src to path
project_004_src = Path('projects/PROJECT-004 AI CODE GENERATOR/SYSTEM-004-01 AI CODE GENERATION SYSTEM/src')
sys.path.insert(0, str(project_004_src))

from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator

# Get layer YAML path from command line
if len(sys.argv) < 2:
    print("Usage: python run_layer_generation.py <path/to/layer.yaml>")
    sys.exit(1)

layer_yaml = Path(sys.argv[1])
if not layer_yaml.exists():
    print(f"❌ Layer YAML not found: {layer_yaml}")
    sys.exit(1)

# Configuration
config = {
    'provider': 'anthropic',
    'output_base_path': str(layer_yaml.parent)
}

print(f"🚀 Starting TDD cycle for layer: {layer_yaml.name}")
print(f"📁 Output directory: {layer_yaml.parent}")
print(f"🤖 AI Provider: Anthropic Claude")
print()

# Create orchestrator
orchestrator = AICodeGeneratorOrchestrator(config=config)

# Execute complete cycle from YAML
result = orchestrator.execute_from_yaml(layer_yaml)

if result.get('status') == 'COMPLETE':
    print()
    print("✅ TDD CYCLE COMPLETE!")
    print()
    print("📊 Generated Reports:")
    for report in result.get('verification_reports', []):
        print(f"   - {report}")
    print()
    print("�� Layer implementation complete with full test coverage!")
else:
    print()
    print("❌ TDD cycle failed")
    sys.exit(1)
