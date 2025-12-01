#!/usr/bin/env python3
"""
Layer Builder - Generate single layer implementation using AI

Generates code for a single layer with proper directory structure:
  layer_folder/
  ├── src/
  │   └── implementation.py
  └── tests/
      └── test_generated_YYYYMMDD_HHMMSS.py

Matches the structure created by build_feature.py for consistency.
"""
import sys
import os
from pathlib import Path
import yaml
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.layer.ai_provider_abstraction.ai_provider_abstraction import AIProviderFactory


def generate_tests_from_requirements(provider, requirements: Dict[str, Any]) -> str:
    """Generate test code from requirements using AI."""
    
    layer_name = requirements.get('layer_metadata', {}).get('requirement_name', 'Unknown')
    acceptance_criteria = requirements.get('acceptance_criteria', [])
    
    prompt = f"""You are an expert Python test developer practicing Test-Driven Development (TDD).

Generate comprehensive pytest test code for this layer:

Layer: {layer_name}

Acceptance Criteria:
"""
    
    for i, ac in enumerate(acceptance_criteria, 1):
        criterion_id = ac.get('criterion_id', f'AC-{i:03d}')
        criterion = ac.get('criterion', '')
        prompt += f"\n{criterion_id}: {criterion}"
    
    prompt += """

Generate test code that:
1. Includes unit tests for each acceptance criterion
2. Includes integration tests for end-to-end validation
3. Uses pytest framework with clear test names
4. Includes fixtures and mocks as needed
5. Has comprehensive assertions
6. Follows the test pyramid (more unit tests than integration tests)

Output ONLY the Python test code, no explanations.
"""
    
    return provider.generate_code(prompt, max_tokens=4000)


def generate_implementation_from_requirements(provider, requirements: Dict[str, Any], tests: str) -> str:
    """Generate implementation code that passes the tests."""
    
    layer_name = requirements.get('layer_metadata', {}).get('requirement_name', 'Unknown')
    acceptance_criteria = requirements.get('acceptance_criteria', [])
    
    prompt = f"""You are an expert Python developer practicing Test-Driven Development (TDD).

Generate implementation code for this layer:

Layer: {layer_name}

Acceptance Criteria:
"""
    
    for i, ac in enumerate(acceptance_criteria, 1):
        criterion_id = ac.get('criterion_id', f'AC-{i:03d}')
        criterion = ac.get('criterion', '')
        prompt += f"\n{criterion_id}: {criterion}"
    
    prompt += f"""

Here are the tests that must pass:

```python
{tests}
```

Generate production-ready Python code that:
1. Passes ALL the tests above
2. Implements all acceptance criteria
3. Follows Python best practices and PEP 8
4. Includes proper error handling
5. Has clear docstrings
6. Is modular and maintainable

Output ONLY the Python implementation code, no explanations.
"""
    
    return provider.generate_code(prompt, max_tokens=4000)


def build_layer(layer_yaml_path: str, output_dir: str, provider_type: str = 'anthropic'):
    """
    Build a single layer using AI code generation.
    
    Args:
        layer_yaml_path: Path to layer requirements YAML
        output_dir: Directory to save generated files
        provider_type: AI provider to use ('anthropic' or 'openai')
    """
    print(f"\n{'='*80}")
    print(f"Building Layer: {layer_yaml_path}")
    print(f"{'='*80}\n")
    
    # Load requirements
    layer_path = Path(layer_yaml_path)
    if not layer_path.exists():
        raise FileNotFoundError(f"Layer YAML not found: {layer_path}")
    
    with open(layer_path, 'r') as f:
        requirements = yaml.safe_load(f)
    
    layer_id = requirements.get('layer_metadata', {}).get('requirement_id', 'UNKNOWN')
    layer_name = requirements.get('layer_metadata', {}).get('requirement_name', 'Unknown')
    
    print(f"✓ Layer ID: {layer_id}")
    print(f"✓ Layer Name: {layer_name}")
    
    # Create AI provider
    print(f"\n🤖 Initializing {provider_type.upper()} AI provider...")
    provider = AIProviderFactory.create_provider(provider_type)
    
    if not provider.validate_configuration():
        raise RuntimeError(f"{provider_type.upper()} provider not configured. Set API key.")
    
    print(f"✓ AI provider ready")
    
    # Create output directory structure (matching build_feature.py)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create src and tests subdirectories
    src_dir = output_path / "src"
    tests_dir = output_path / "tests"
    src_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)
    
    # RED PHASE: Generate tests
    print(f"\n{'='*80}")
    print("RED PHASE: Generating Tests")
    print(f"{'='*80}\n")
    
    print("🤖 Calling AI to generate tests...")
    test_code = generate_tests_from_requirements(provider, requirements)
    
    # Save test file in tests/ subdirectory with timestamp (matching build_feature.py)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_file = tests_dir / f"test_generated_{timestamp}.py"
    with open(test_file, 'w') as f:
        f.write(test_code)
    
    print(f"✅ Tests generated: {test_file}")
    print(f"   ({len(test_code)} characters, {test_code.count('def test_')} test functions)")
    
    # GREEN PHASE: Generate implementation
    print(f"\n{'='*80}")
    print("GREEN PHASE: Generating Implementation")
    print(f"{'='*80}\n")
    
    print("🤖 Calling AI to generate implementation...")
    impl_code = generate_implementation_from_requirements(provider, requirements, test_code)
    
    # Save implementation in src/implementation.py (matching build_feature.py)
    impl_file = src_dir / "implementation.py"
    with open(impl_file, 'w') as f:
        f.write(impl_code)
    
    print(f"✅ Implementation generated: {impl_file}")
    print(f"   ({len(impl_code)} characters)")
    
    # Save requirements for reference
    req_file = output_path / "requirements.yaml"
    with open(req_file, 'w') as f:
        yaml.dump(requirements, f, default_flow_style=False)
    
    print(f"✓ Requirements saved: {req_file}")
    
    # Generate summary
    summary = {
        'layer_id': layer_id,
        'layer_name': layer_name,
        'files_generated': {
            'tests': str(test_file.relative_to(output_path)),
            'implementation': str(impl_file.relative_to(output_path)),
            'requirements': str(req_file.relative_to(output_path))
        },
        'metrics': {
            'test_code_size': len(test_code),
            'impl_code_size': len(impl_code),
            'test_function_count': test_code.count('def test_')
        }
    }
    
    summary_file = output_path / "build_summary.yaml"
    with open(summary_file, 'w') as f:
        yaml.dump(summary, f, default_flow_style=False)
    
    print(f"\n{'='*80}")
    print("✅ LAYER BUILD COMPLETE!")
    print(f"{'='*80}\n")
    print(f"Output directory: {output_path}")
    print("Files generated:")
    print(f"  - {impl_file.relative_to(output_path.parent)}")
    print(f"  - {test_file.relative_to(output_path.parent)}")
    print("\nStructure:")
    print(f"  {output_path.name}/")
    print("  ├── src/")
    print("  │   └── implementation.py")
    print("  └── tests/")
    print(f"      └── test_generated_{timestamp}.py")
    print("\nNext steps:")
    print(f"1. Review generated code in {output_path}")
    print(f"2. Run tests: pytest {test_file}")
    print("3. Integrate with feature using build_feature.py")
    
    return summary


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python build_layer.py "
              "<layer_yaml_path> [output_dir] [provider]")
        print("\nExample:")
        print('  python build_layer.py '
              '"LAYER_001/LAYER_001.yaml" . anthropic')
        sys.exit(1)
    
    layer_yaml = sys.argv[1]
    # Default to current directory (.) to match build_feature.py structure
    # Creates src/ and tests/ at layer root, not in AI_GENERATED_CODE/
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    provider = sys.argv[3] if len(sys.argv) > 3 else "anthropic"
    
    try:
        build_layer(layer_yaml, output_dir, provider)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
