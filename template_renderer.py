"""Template renderer for control_tower templates

This small utility loads a template by path and renders it with variables from a YAML file or dict.
"""
from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def render_template(template_path: Path, variables: Dict[str, Any]) -> str:
    template_dir = template_path.parent
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        lstrip_blocks=True,
        trim_blocks=True,
    )
    template = env.get_template(template_path.name)
    return template.render(**variables)


def render_from_yaml(template_path: str, yaml_path: str) -> str:
    tpl = Path(template_path)
    vars_path = Path(yaml_path)
    with open(vars_path, 'r', encoding='utf-8') as f:
        variables = yaml.safe_load(f) or {}
    return render_template(tpl, variables)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('template', help='Path to Jinja2 template')
    parser.add_argument('--vars', help='YAML file with variables', default=None)
    args = parser.parse_args()

    if args.vars:
        out = render_from_yaml(args.template, args.vars)
    else:
        out = render_template(Path(args.template), {})

    print(out)
