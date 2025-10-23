"""
Enhanced Template Renderer for Control Tower MVP Templates
Supports metadata-driven rendering with JSON Schema validation
"""
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import jsonschema
from jsonschema import validate, ValidationError


class TemplateRenderer:
    """Render MVP templates with metadata and validation"""
    
    def __init__(self, template_dir: Path):
        """Initialize renderer with template directory
        
        Args:
            template_dir: Path to template directory containing meta.yml
        """
        self.template_dir = Path(template_dir)
        self.meta = self._load_metadata()
        self.schema = self._load_schema()
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            lstrip_blocks=True,
            trim_blocks=True,
        )
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load template metadata from meta.yml"""
        meta_path = self.template_dir / "meta.yml"
        if not meta_path.exists():
            raise FileNotFoundError(f"Template metadata not found: {meta_path}")
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Load JSON Schema for variable validation"""
        schema_file = self.meta.get("variables_schema")
        if not schema_file:
            return None
        
        schema_path = self.template_dir / schema_file
        if not schema_path.exists():
            print(f"Warning: Schema file not found: {schema_path}")
            return None
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_variables(self, variables: Dict[str, Any]) -> None:
        """Validate variables against JSON Schema
        
        Args:
            variables: Dictionary of template variables
            
        Raises:
            ValidationError: If variables don't match schema
        """
        if self.schema is None:
            print("Warning: No schema found, skipping validation")
            return
        
        try:
            validate(instance=variables, schema=self.schema)
        except ValidationError as e:
            raise ValidationError(f"Variable validation failed: {e.message}")
    
    def render(self, variables: Dict[str, Any], output_dir: Optional[Path] = None) -> Dict[str, str]:
        """Render all template outputs with variables
        
        Args:
            variables: Dictionary of template variables
            output_dir: Base directory for output files (default: current directory)
            
        Returns:
            Dictionary mapping output paths to rendered content
        """
        # Validate variables
        self.validate_variables(variables)
        
        # Auto-generate snake_case model name if not provided
        if 'model_name' in variables and 'model_name_snake' not in variables:
            model_name = variables['model_name']
            # Convert PascalCase to snake_case
            snake_case = ''.join(['_' + c.lower() if c.isupper() and i > 0 else c.lower() 
                                 for i, c in enumerate(model_name)])
            variables['model_name_snake'] = snake_case
        
        # Render each output
        outputs = {}
        for output_spec in self.meta.get('outputs', []):
            template_file = output_spec['template']
            path_template = output_spec['path']
            
            # Render output path with variables
            env_path = Environment(undefined=StrictUndefined)
            output_path = env_path.from_string(path_template).render(**variables)
            
            # Render template content
            template = self.env.get_template(template_file)
            content = template.render(**variables)
            
            outputs[output_path] = content
        
        # Write to files if output_dir provided
        if output_dir:
            output_dir = Path(output_dir)
            for path, content in outputs.items():
                full_path = output_dir / path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Generated: {path}")
        
        return outputs
    
    def render_to_files(self, variables: Dict[str, Any], output_dir: Path) -> List[Path]:
        """Render templates and write to files
        
        Args:
            variables: Dictionary of template variables
            output_dir: Base directory for output files
            
        Returns:
            List of generated file paths
        """
        outputs = self.render(variables, output_dir)
        return [Path(p) for p in outputs.keys()]
    
    def get_info(self) -> Dict[str, Any]:
        """Get template metadata info"""
        return {
            "id": self.meta.get("id"),
            "name": self.meta.get("name"),
            "version": self.meta.get("version"),
            "layer_type": self.meta.get("layer_type"),
            "frameworks": self.meta.get("frameworks", []),
            "tags": self.meta.get("tags", []),
            "status": self.meta.get("status"),
            "description": self.meta.get("description"),
            "cost_estimate_tokens": self.meta.get("cost_estimate_tokens"),
        }


def render_template_by_id(template_id: str, variables: Dict[str, Any], 
                          output_dir: Optional[Path] = None) -> Dict[str, str]:
    """Render a template by ID from the MVP template registry
    
    Args:
        template_id: Template ID (e.g., "tpl-backend-fastapi-crud")
        variables: Dictionary of template variables
        output_dir: Optional output directory to write files
        
    Returns:
        Dictionary mapping output paths to rendered content
    """
    # Load template registry
    registry_path = Path(__file__).parent / "templates" / "mvp" / "index.yaml"
    
    if not registry_path.exists():
        raise FileNotFoundError(f"Template registry not found: {registry_path}")
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)
    
    # Find template
    template_info = None
    for template in registry.get('templates', []):
        if template['id'] == template_id:
            template_info = template
            break
    
    if template_info is None:
        raise ValueError(f"Template not found: {template_id}")
    
    # Load and render template
    template_dir = registry_path.parent / template_info['path']
    renderer = TemplateRenderer(template_dir)
    
    return renderer.render(variables, output_dir)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Render MVP templates")
    parser.add_argument('template_dir', help='Path to template directory')
    parser.add_argument('--vars', help='YAML file with variables', required=True)
    parser.add_argument('--output', help='Output directory for generated files', default=None)
    parser.add_argument('--info', action='store_true', help='Show template info only')
    
    args = parser.parse_args()
    
    # Load variables
    with open(args.vars, 'r', encoding='utf-8') as f:
        variables = yaml.safe_load(f) or {}
    
    # Create renderer
    renderer = TemplateRenderer(Path(args.template_dir))
    
    if args.info:
        # Show template info
        info = renderer.get_info()
        print(f"\n=== Template Info ===")
        for key, value in info.items():
            print(f"{key}: {value}")
    else:
        # Render template
        print(f"\n=== Rendering {renderer.meta['name']} ===")
        outputs = renderer.render(variables, Path(args.output) if args.output else None)
        
        print(f"\n=== Rendered {len(outputs)} files ===")
        if not args.output:
            for path, content in outputs.items():
                print(f"\n--- {path} ---")
                print(content)
