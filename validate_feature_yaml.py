#!/usr/bin/env python3
"""
Feature YAML Schema Validator
==============================
Pre-flight validation for feature YAML files before AI code generation.
Ensures all required fields, layer references, and production integration
configuration are present and correct.

Usage:
    python validate_feature_yaml.py <yaml_path> [--strict] [--require-production-wiring]
    
    --strict                     Fail on warnings (layer file not found, etc.)
    --require-production-wiring  Require production_integration section (for CI fire-and-forget)

Exit codes:
    0  All validations passed
    1  Validation failed (missing/invalid fields)
    2  File not found or parse error
"""

import argparse
import sys
import re
from pathlib import Path
import yaml


class ValidationError:
    """A single validation failure."""
    def __init__(self, field: str, message: str, severity: str = "ERROR"):
        self.field = field
        self.message = message
        self.severity = severity  # ERROR or WARNING

    def __str__(self):
        icon = "❌" if self.severity == "ERROR" else "⚠️ "
        return f"  {icon} [{self.field}] {self.message}"


class FeatureYAMLValidator:
    """Validates feature YAML files against the expected schema."""

    FEATURE_ID_PATTERN = re.compile(r'^FEATURE-[A-Z]{2,}-\d{3}-\d{2}$')
    LAYER_ID_PATTERN = re.compile(r'^LAYER-[A-Z]{2,}-\d{3}-\d{2}-\d{2}$')

    def __init__(self, yaml_path: str, strict: bool = False,
                 require_production_wiring: bool = False):
        self.yaml_path = Path(yaml_path).resolve()
        self.strict = strict
        self.require_production_wiring = require_production_wiring
        self.errors: list[ValidationError] = []
        self.data: dict = {}

    def validate(self) -> bool:
        """Run all validations. Returns True if no errors."""
        # Load YAML
        if not self._load_yaml():
            return False

        # Run all checks
        self._validate_metadata()
        self._validate_acceptance_criteria()
        self._validate_layers()

        if self.require_production_wiring:
            self._validate_production_integration()

        # Report results
        return self._report()

    def _load_yaml(self) -> bool:
        """Load and parse the YAML file."""
        if not self.yaml_path.exists():
            print(f"❌ File not found: {self.yaml_path}")
            return False

        try:
            with open(self.yaml_path) as f:
                self.data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ YAML parse error: {e}")
            return False

        if not isinstance(self.data, dict):
            print(f"❌ YAML root must be a mapping, got {type(self.data).__name__}")
            return False

        return True

    def _validate_metadata(self):
        """Validate the metadata section."""
        meta = self.data.get('metadata')
        if not meta:
            self.errors.append(ValidationError(
                'metadata', 'Missing required section: metadata'))
            return

        if not isinstance(meta, dict):
            self.errors.append(ValidationError(
                'metadata', f'metadata must be a mapping, got {type(meta).__name__}'))
            return

        # requirement_id
        req_id = meta.get('requirement_id')
        if not req_id:
            self.errors.append(ValidationError(
                'metadata.requirement_id', 'Missing required field'))
        elif not self.FEATURE_ID_PATTERN.match(req_id):
            self.errors.append(ValidationError(
                'metadata.requirement_id',
                f'Must match pattern FEATURE-XX-NNN-NN, got: {req_id}'))

        # requirement_name
        req_name = meta.get('requirement_name')
        if not req_name or not str(req_name).strip():
            self.errors.append(ValidationError(
                'metadata.requirement_name', 'Missing or empty required field'))

    def _validate_acceptance_criteria(self):
        """Validate acceptance_criteria exist (top-level or under overview)."""
        # Check top-level first
        ac = self.data.get('acceptance_criteria')

        # Also check under overview (common pattern)
        if not ac:
            overview = self.data.get('overview', {})
            if isinstance(overview, dict):
                ac = overview.get('acceptance_criteria')

        if not ac:
            self.errors.append(ValidationError(
                'acceptance_criteria',
                'Missing required field: acceptance_criteria (top-level or under overview)'))
            return

        if not isinstance(ac, list):
            self.errors.append(ValidationError(
                'acceptance_criteria',
                f'Must be a list, got {type(ac).__name__}'))
            return

        if len(ac) == 0:
            self.errors.append(ValidationError(
                'acceptance_criteria', 'Must have at least one criterion'))
            return

        # Acceptance criteria can be strings or dicts with criterion_id
        for i, criterion in enumerate(ac):
            if isinstance(criterion, str):
                if not criterion.strip():
                    self.errors.append(ValidationError(
                        f'acceptance_criteria[{i}]', 'Empty criterion string'))
            elif isinstance(criterion, dict):
                if not criterion.get('criterion_id') and not criterion.get('description'):
                    self.errors.append(ValidationError(
                        f'acceptance_criteria[{i}]',
                        'Dict criterion must have criterion_id or description'))

    def _validate_layers(self):
        """Validate the layers section."""
        layers = self.data.get('layers')
        if not layers:
            self.errors.append(ValidationError(
                'layers', 'Missing required section: layers'))
            return

        if not isinstance(layers, list):
            self.errors.append(ValidationError(
                'layers', f'Must be a list, got {type(layers).__name__}'))
            return

        if len(layers) == 0:
            self.errors.append(ValidationError(
                'layers', 'Must have at least one layer'))
            return

        feature_dir = self.yaml_path.parent
        for i, layer in enumerate(layers):
            if not isinstance(layer, dict):
                self.errors.append(ValidationError(
                    f'layers[{i}]', f'Must be a mapping, got {type(layer).__name__}'))
                continue

            # layer_id
            layer_id = layer.get('layer_id')
            if not layer_id:
                self.errors.append(ValidationError(
                    f'layers[{i}].layer_id', 'Missing required field'))
            elif not self.LAYER_ID_PATTERN.match(layer_id):
                self.errors.append(ValidationError(
                    f'layers[{i}].layer_id',
                    f'Must match pattern LAYER-XX-NNN-NN-NN, got: {layer_id}'))

            # requirement_file
            req_file = layer.get('requirement_file')
            if not req_file:
                self.errors.append(ValidationError(
                    f'layers[{i}].requirement_file', 'Missing required field'))
            else:
                # Try to find the layer YAML file
                layer_folder = layer.get('folder', '')
                candidates = [
                    feature_dir / layer_folder / req_file,
                    feature_dir / req_file,
                ]
                found = any(c.exists() for c in candidates)
                if not found:
                    severity = "ERROR" if self.strict else "WARNING"
                    self.errors.append(ValidationError(
                        f'layers[{i}].requirement_file',
                        f'Layer YAML not found: {req_file} '
                        f'(searched in {feature_dir / layer_folder})',
                        severity=severity))

    def _validate_production_integration(self):
        """Validate the production_integration section."""
        prod = self.data.get('production_integration')
        if not prod:
            self.errors.append(ValidationError(
                'production_integration',
                'Missing required section (--require-production-wiring is set). '
                'Add a production_integration section to enable automated deployment.'))
            return

        if not isinstance(prod, dict):
            self.errors.append(ValidationError(
                'production_integration',
                f'Must be a mapping, got {type(prod).__name__}'))
            return

        # target_router_file
        router = prod.get('target_router_file')
        if not router or not str(router).strip():
            self.errors.append(ValidationError(
                'production_integration.target_router_file',
                'Missing required field'))

        # import_alias
        alias = prod.get('import_alias')
        if not alias or not str(alias).strip():
            self.errors.append(ValidationError(
                'production_integration.import_alias',
                'Missing required field'))

        # module_name
        module = prod.get('module_name')
        if not module or not str(module).strip():
            self.errors.append(ValidationError(
                'production_integration.module_name',
                'Missing required field'))

        # endpoint_prefix
        prefix = prod.get('endpoint_prefix')
        if not prefix or not str(prefix).strip():
            self.errors.append(ValidationError(
                'production_integration.endpoint_prefix',
                'Missing required field'))

        # operations
        ops = prod.get('operations')
        if not ops:
            self.errors.append(ValidationError(
                'production_integration.operations',
                'Missing required field: at least one operation needed'))
            return

        if not isinstance(ops, list) or len(ops) == 0:
            self.errors.append(ValidationError(
                'production_integration.operations',
                'Must be a non-empty list'))
            return

        valid_methods = {'get', 'post', 'put', 'delete', 'patch'}
        for i, op in enumerate(ops):
            if not isinstance(op, dict):
                self.errors.append(ValidationError(
                    f'production_integration.operations[{i}]',
                    f'Must be a mapping, got {type(op).__name__}'))
                continue

            if not op.get('name'):
                self.errors.append(ValidationError(
                    f'production_integration.operations[{i}].name',
                    'Missing required field'))

            method = op.get('http_method', '').lower()
            if method not in valid_methods:
                self.errors.append(ValidationError(
                    f'production_integration.operations[{i}].http_method',
                    f'Must be one of {valid_methods}, got: {method!r}'))

            if not op.get('path'):
                self.errors.append(ValidationError(
                    f'production_integration.operations[{i}].path',
                    'Missing required field'))

            if not op.get('orchestrator_method'):
                self.errors.append(ValidationError(
                    f'production_integration.operations[{i}].orchestrator_method',
                    'Missing required field'))

    def _report(self) -> bool:
        """Print results and return True if no errors."""
        errors = [e for e in self.errors if e.severity == "ERROR"]
        warnings = [e for e in self.errors if e.severity == "WARNING"]

        feature_id = self.data.get('metadata', {}).get('requirement_id', 'UNKNOWN')

        if not errors and not warnings:
            print(f"✅ Valid: {feature_id} ({self.yaml_path.name})")
            return True

        if errors:
            print(f"\n❌ VALIDATION FAILED: {feature_id} ({self.yaml_path.name})")
            print(f"   {len(errors)} error(s), {len(warnings)} warning(s)\n")
            for e in errors:
                print(str(e))
        else:
            print(f"\n⚠️  WARNINGS: {feature_id} ({self.yaml_path.name})")

        if warnings:
            print()
            for w in warnings:
                print(str(w))

        print()
        return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate feature YAML files for the AI Feature Builder pipeline')
    parser.add_argument('yaml_path', help='Path to feature YAML file')
    parser.add_argument('--strict', action='store_true',
                        help='Treat warnings as errors')
    parser.add_argument('--require-production-wiring', action='store_true',
                        help='Require production_integration section')
    args = parser.parse_args()

    validator = FeatureYAMLValidator(
        yaml_path=args.yaml_path,
        strict=args.strict,
        require_production_wiring=args.require_production_wiring,
    )

    if validator.validate():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
