#!/usr/bin/env python3
"""
MVP Generator

Generates complete MVP projects from natural language requirements.
Uses Semantic Template Mapper to select templates and renders them with Jinja2.

Usage:
    python mvp_generator.py "SaaS landing page with email capture"
    python mvp_generator.py "REST API for user management" --output ./my-mvp
"""

import os
import sys
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, StrictUndefined

# Import the semantic mapper
from mvp_semantic_mapper import SemanticTemplateMapper, TemplateMatch


class MVPGenerator:
    """Generates MVP projects from requirements"""
    
    def __init__(
        self,
        templates_dir: Path = None,
        output_dir: Path = None
    ):
        self.templates_dir = templates_dir or Path("templates/mvp")
        self.output_dir = output_dir or Path("./generated-mvp")
        self.mapper = SemanticTemplateMapper(templates_dir=self.templates_dir)
        
        # Jinja2 environment for template rendering
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            lstrip_blocks=True,
            trim_blocks=True,
        )
    
    def generate_default_parameters(
        self,
        template_id: str,
        requirement: str
    ) -> Dict[str, Any]:
        """Generate default parameters for a template based on requirement"""
        template = self.mapper.template_index.get(template_id)
        if not template:
            return {}
        
        # Get suggestions from mapper
        suggestions = self.mapper.generate_parameter_suggestions(template, requirement)
        
        # Load example parameters if they exist
        template_path = self.templates_dir / template.path
        example_params_file = template_path / "example_params.yaml"
        
        if example_params_file.exists():
            with open(example_params_file, 'r') as f:
                example_params = yaml.safe_load(f)
            
            # Merge suggestions with example params
            params = {**example_params, **suggestions}
        else:
            params = suggestions
        
        # Add common parameters
        params['generated_at'] = datetime.now().isoformat()
        params['requirement'] = requirement
        
        return params
    
    def render_template_file(
        self,
        template_file: Path,
        variables: Dict[str, Any],
        output_file: Path
    ):
        """Render a single Jinja2 template file"""
        # Get relative path for Jinja2 loader
        rel_path = template_file.relative_to(self.templates_dir)
        
        try:
            template = self.jinja_env.get_template(str(rel_path))
            rendered = template.render(**variables)
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write rendered content
            with open(output_file, 'w') as f:
                f.write(rendered)
            
            return True
        except Exception as e:
            print(f"⚠️  Error rendering {template_file.name}: {e}")
            return False
    
    def render_template(
        self,
        template_match: TemplateMatch,
        requirement: str,
        output_subdir: Path
    ) -> Dict[str, Any]:
        """
        Render a template with all its files.
        
        Returns:
            Dict with rendering results
        """
        template = template_match.template
        template_path = self.templates_dir / template.path
        
        print(f"\n📦 Rendering: {template.name}")
        print(f"   Path: {template_path}")
        print(f"   Confidence: {template_match.confidence:.1f}%")
        
        # Generate parameters
        params = self.generate_default_parameters(template.id, requirement)
        
        # Find all .jinja files in template directory
        jinja_files = list(template_path.glob("*.jinja"))
        
        if not jinja_files:
            print(f"   ⚠️  No .jinja files found in {template_path}")
            return {
                'template_id': template.id,
                'success': False,
                'files_rendered': 0,
            }
        
        rendered_files = []
        for jinja_file in jinja_files:
            # Determine output filename (remove .jinja extension)
            output_filename = jinja_file.stem
            output_file = output_subdir / output_filename
            
            success = self.render_template_file(jinja_file, params, output_file)
            
            if success:
                rendered_files.append(str(output_file.relative_to(self.output_dir)))
                print(f"   ✅ {output_filename}")
            else:
                print(f"   ❌ {output_filename}")
        
        # Save parameters used for rendering
        params_file = output_subdir / f"{template.id}_params.yaml"
        with open(params_file, 'w') as f:
            yaml.dump(params, f, default_flow_style=False, sort_keys=False)
        
        return {
            'template_id': template.id,
            'template_name': template.name,
            'success': len(rendered_files) > 0,
            'files_rendered': len(rendered_files),
            'rendered_files': rendered_files,
            'parameters_file': str(params_file.relative_to(self.output_dir)),
        }
    
    def create_project_structure(self, requirement: str):
        """Create standard MVP project structure"""
        # Create directory structure
        dirs = [
            self.output_dir,
            self.output_dir / "frontend",
            self.output_dir / "backend",
            self.output_dir / "backend" / "app",
            self.output_dir / "backend" / "app" / "routers",
            self.output_dir / "backend" / "app" / "models",
            self.output_dir / "backend" / "app" / "schemas",
            self.output_dir / "backend" / "app" / "middleware",
            self.output_dir / "infra",
            self.output_dir / "docs",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        init_files = [
            self.output_dir / "backend" / "app" / "__init__.py",
            self.output_dir / "backend" / "app" / "routers" / "__init__.py",
            self.output_dir / "backend" / "app" / "models" / "__init__.py",
            self.output_dir / "backend" / "app" / "schemas" / "__init__.py",
            self.output_dir / "backend" / "app" / "middleware" / "__init__.py",
        ]
        
        for init_file in init_files:
            init_file.touch(exist_ok=True)
    
    def generate_readme(
        self,
        requirement: str,
        templates_used: List[Dict[str, Any]]
    ):
        """Generate README.md for the MVP"""
        readme_content = f"""# MVP Project

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Requirement:** {requirement}

## 📋 Overview

This MVP was automatically generated using the Control Tower MVP Generator.

## 🏗️ Templates Used

"""
        for template_info in templates_used:
            if template_info['success']:
                readme_content += f"- ✅ **{template_info['template_name']}** ({template_info['files_rendered']} files)\n"
        
        readme_content += """
## 📁 Project Structure

```
generated-mvp/
├── frontend/           # React frontend components
├── backend/            # FastAPI backend
│   └── app/
│       ├── routers/    # API route handlers
│       ├── models/     # Database models
│       ├── schemas/    # Pydantic schemas
│       └── middleware/ # Custom middleware
├── infra/              # Infrastructure configuration
└── docs/               # Documentation
```

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📝 Next Steps

1. Review the generated code
2. Customize configuration files
3. Add business logic
4. Deploy to Railway (if infra template was used)

## 🔧 Configuration

Check the `*_params.yaml` files in each directory to see the parameters used for generation.

## 📚 Documentation

- See `docs/` folder for additional documentation
- Each template includes inline comments
- Check the Control Tower templates for more details

---

Generated by Control Tower MVP Generator
"""
        
        readme_file = self.output_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"\n📄 Generated: {readme_file}")
    
    def generate_mvp(
        self,
        requirement: str,
        min_confidence: float = 20.0,
        auto_select: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete MVP from requirement.
        
        Args:
            requirement: Natural language requirement
            min_confidence: Minimum confidence threshold for template selection
            auto_select: Automatically select templates (vs manual selection)
        
        Returns:
            Dict with generation results
        """
        print("=" * 80)
        print("🚀 MVP GENERATOR")
        print("=" * 80)
        print(f"\n📋 Requirement: {requirement}\n")
        
        # Analyze requirement and find matching templates
        matches = self.mapper.find_matching_templates(
            requirement,
            min_confidence=min_confidence
        )
        
        if not matches:
            print("❌ No matching templates found. Try rephrasing your requirement.")
            return {
                'success': False,
                'error': 'No matching templates found',
            }
        
        print(f"✅ Found {len(matches)} matching templates\n")
        
        # Display matches
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match.template.name}")
            print(f"   Confidence: {match.confidence:.1f}%")
            print(f"   Layer: {match.template.layer_type}")
            print(f"   Cost: {match.template.cost_estimate_tokens} tokens")
        
        # Create project structure
        print(f"\n📁 Creating project structure in: {self.output_dir}")
        self.create_project_structure(requirement)
        
        # Render each template
        print("\n" + "=" * 80)
        print("📦 RENDERING TEMPLATES")
        print("=" * 80)
        
        templates_used = []
        total_files = 0
        
        for match in matches:
            # Determine output subdirectory based on layer type
            layer_dirs = {
                'ui': 'frontend',
                'api': 'backend/app',
                'infra': 'infra',
                'composite': '',
            }
            
            subdir_name = layer_dirs.get(match.template.layer_type, 'other')
            output_subdir = self.output_dir / subdir_name
            
            # Render template
            result = self.render_template(match, requirement, output_subdir)
            templates_used.append(result)
            
            if result['success']:
                total_files += result['files_rendered']
        
        # Generate README
        self.generate_readme(requirement, templates_used)
        
        # Generate project metadata
        metadata = {
            'requirement': requirement,
            'generated_at': datetime.now().isoformat(),
            'templates_used': templates_used,
            'total_files': total_files,
            'output_directory': str(self.output_dir),
        }
        
        metadata_file = self.output_dir / "mvp_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Summary
        print("\n" + "=" * 80)
        print("✨ MVP GENERATION COMPLETE")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"  • Templates Used: {len([t for t in templates_used if t['success']])}")
        print(f"  • Files Generated: {total_files}")
        print(f"  • Output Directory: {self.output_dir}")
        print(f"\n📁 Project Location: {self.output_dir.absolute()}")
        print(f"\n📖 Next Steps:")
        print(f"  1. cd {self.output_dir}")
        print(f"  2. Review README.md for setup instructions")
        print(f"  3. Customize the generated code")
        print(f"  4. Deploy your MVP!")
        print()
        
        return {
            'success': True,
            'output_directory': str(self.output_dir.absolute()),
            'templates_used': templates_used,
            'total_files': total_files,
            'metadata_file': str(metadata_file),
        }


def main():
    """CLI interface for MVP generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate MVP projects from natural language requirements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mvp_generator.py "SaaS landing page with email capture"
  python mvp_generator.py "REST API for user management" --output ./my-api
  python mvp_generator.py "Deploy FastAPI app to Railway" --min-confidence 30
        """
    )
    
    parser.add_argument(
        'requirement',
        type=str,
        help='Natural language requirement for the MVP'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./generated-mvp',
        help='Output directory for generated MVP (default: ./generated-mvp)'
    )
    
    parser.add_argument(
        '--min-confidence',
        type=float,
        default=20.0,
        help='Minimum confidence threshold for template selection (default: 20.0)'
    )
    
    parser.add_argument(
        '--templates-dir',
        type=str,
        default='templates/mvp',
        help='Templates directory (default: templates/mvp)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite if output directory exists'
    )
    
    args = parser.parse_args()
    
    # Check if output directory exists
    output_path = Path(args.output)
    if output_path.exists() and not args.force:
        print(f"❌ Output directory already exists: {output_path}")
        print(f"   Use --force to overwrite or choose a different output directory")
        sys.exit(1)
    
    # Create generator
    generator = MVPGenerator(
        templates_dir=Path(args.templates_dir),
        output_dir=output_path
    )
    
    # Generate MVP
    result = generator.generate_mvp(
        requirement=args.requirement,
        min_confidence=args.min_confidence
    )
    
    if not result['success']:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
