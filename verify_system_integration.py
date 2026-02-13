#!/usr/bin/env python3
"""
System Integration Verifier
=============================
Post-build verification that all AI-built features are wired into the
production application. Runs after ALL_IN_ORDER builds to catch
features that were generated but not connected.

Usage:
    python verify_system_integration.py <target_path> [--app-entry-point PATH]

    target_path          Path to the system directory containing FEATURE-* folders
    --app-entry-point    Path to the FastAPI main.py (relative to repo root)

Exit codes:
    0  All features are wired
    1  One or more features are unwired or have import errors
    2  Configuration error
"""

import argparse
import ast
import sys
from pathlib import Path
import yaml


def find_feature_dirs(system_path: Path) -> list[Path]:
    """Find all FEATURE-* directories under the system path."""
    return sorted([
        d for d in system_path.iterdir()
        if d.is_dir() and d.name.startswith('FEATURE-')
    ])


def load_feature_yaml(feature_dir: Path) -> dict | None:
    """Load the feature YAML from a feature directory."""
    # Find the YAML that matches FEATURE-*.yaml (not layer YAMLs)
    for f in feature_dir.glob("FEATURE-*.yaml"):
        if 'LAYER-' not in f.name:
            try:
                with open(f) as fh:
                    return yaml.safe_load(fh)
            except Exception:
                pass
    return None


def find_feature_integration(feature_dir: Path) -> Path | None:
    """Find the feature_integration.py file in a feature directory."""
    candidates = [
        feature_dir / 'feature_integration.py',
        feature_dir / 'src' / 'feature_integration.py',
    ]
    # Also search recursively
    for f in feature_dir.rglob('feature_integration*.py'):
        candidates.append(f)

    for c in candidates:
        if c.exists():
            return c
    return None


def check_syntax(py_file: Path) -> tuple[bool, str]:
    """Check if a Python file parses without syntax errors."""
    try:
        source = py_file.read_text()
        ast.parse(source)
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def check_router_mounting(app_entry_point: Path, router_file: str) -> tuple[bool, str]:
    """Check if a router file is referenced in the app entry point."""
    if not app_entry_point.exists():
        return False, f"App entry point not found: {app_entry_point}"

    content = app_entry_point.read_text()

    # Extract the module name from the router file path
    # e.g., "src/backend/app/causality_router.py" -> "causality_router"
    router_module = Path(router_file).stem

    if router_module in content:
        return True, f"'{router_module}' found in {app_entry_point.name}"
    else:
        return False, f"'{router_module}' NOT found in {app_entry_point.name}"


def verify_system(system_path: Path, repo_root: Path,
                  app_entry_point_rel: str | None = None) -> bool:
    """
    Verify all features under system_path are wired into production.

    Returns True if all features pass verification.
    """
    feature_dirs = find_feature_dirs(system_path)

    if not feature_dirs:
        print(f"❌ No FEATURE-* directories found in {system_path}")
        return False

    print(f"\n🔍 System Integration Verification")
    print(f"   System path: {system_path}")
    print(f"   Features found: {len(feature_dirs)}")
    print()

    results = []

    for feature_dir in feature_dirs:
        feature_name = feature_dir.name
        feature_yaml = load_feature_yaml(feature_dir)
        feature_id = feature_yaml.get('metadata', {}).get('requirement_id', feature_name) if feature_yaml else feature_name

        status = {
            'feature_id': feature_id,
            'dir': feature_name,
            'has_yaml': feature_yaml is not None,
            'has_integration': False,
            'syntax_ok': False,
            'has_prod_config': False,
            'router_wired': False,
            'issues': [],
        }

        # Check feature_integration.py exists
        fi_path = find_feature_integration(feature_dir)
        if fi_path:
            status['has_integration'] = True
            ok, err = check_syntax(fi_path)
            status['syntax_ok'] = ok
            if not ok:
                status['issues'].append(f"Syntax error in {fi_path.name}: {err}")
        else:
            status['issues'].append("No feature_integration.py found")

        # Check production_integration config
        if feature_yaml:
            prod_config = feature_yaml.get('production_integration')
            if prod_config:
                status['has_prod_config'] = True

                # Check if the router is mounted in app entry point
                entry_point_path = app_entry_point_rel or prod_config.get('app_entry_point', 'main.py')
                entry_point = repo_root / entry_point_path
                router_file = prod_config.get('target_router_file', '')

                if router_file and entry_point.exists():
                    wired, msg = check_router_mounting(entry_point, router_file)
                    status['router_wired'] = wired
                    if not wired:
                        status['issues'].append(msg)
                elif not entry_point.exists():
                    status['issues'].append(f"App entry point not found: {entry_point}")
            else:
                status['issues'].append("No production_integration section in YAML")

        results.append(status)

    # Print results table
    print(f"  {'Feature':<22} {'YAML':>6} {'Integ':>6} {'Syntax':>7} {'ProdCfg':>8} {'Wired':>6}")
    print(f"  {'─' * 22} {'─' * 6} {'─' * 6} {'─' * 7} {'─' * 8} {'─' * 6}")

    all_ok = True
    for r in results:
        yaml_icon = "✅" if r['has_yaml'] else "❌"
        integ_icon = "✅" if r['has_integration'] else "❌"
        syntax_icon = "✅" if r['syntax_ok'] else ("❌" if r['has_integration'] else "➖")
        prod_icon = "✅" if r['has_prod_config'] else "⚠️ "
        wired_icon = "✅" if r['router_wired'] else ("❌" if r['has_prod_config'] else "➖")

        print(f"  {r['feature_id']:<22} {yaml_icon:>6} {integ_icon:>6} {syntax_icon:>7} {prod_icon:>8} {wired_icon:>6}")

        # A feature fails if it has integration code but syntax errors or is unwired
        if r['has_integration'] and not r['syntax_ok']:
            all_ok = False
        if r['has_prod_config'] and not r['router_wired']:
            all_ok = False

    # Print issues
    issues_found = False
    for r in results:
        if r['issues']:
            if not issues_found:
                print(f"\n  Issues:")
                issues_found = True
            for issue in r['issues']:
                print(f"    ⚠️  {r['feature_id']}: {issue}")

    print()
    if all_ok:
        print(f"✅ System integration verification passed")
    else:
        print(f"❌ System integration verification FAILED — see issues above")

    return all_ok


def main():
    parser = argparse.ArgumentParser(
        description='Verify AI-built features are wired into the production app')
    parser.add_argument('target_path',
                        help='Path to the system directory (e.g., Causal_affect/SYSTEM-CA-002_...)')
    parser.add_argument('--app-entry-point',
                        help='Path to app main.py relative to repo root')
    parser.add_argument('--repo-root',
                        help='Path to the repo root (default: auto-detect from target_path)')
    args = parser.parse_args()

    system_path = Path(args.target_path).resolve()
    if not system_path.exists():
        print(f"❌ System path not found: {system_path}")
        sys.exit(2)

    # Auto-detect repo root (walk up to find .git)
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        repo_root = system_path
        while repo_root != repo_root.parent:
            if (repo_root / '.git').exists():
                break
            repo_root = repo_root.parent
        else:
            # No .git found, use system_path parent
            repo_root = system_path.parent

    ok = verify_system(system_path, repo_root, args.app_entry_point)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
