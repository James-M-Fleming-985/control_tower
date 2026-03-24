#!/usr/bin/env python3
"""
Discover Railway projects/services/environments and populate app_registry.json.

Usage:
    python3 tools/railway-logs-mcp/discover.py            # interactive
    python3 tools/railway-logs-mcp/discover.py --write     # write to app_registry.json
"""

import json
import os
import sys

# Resolve imports relative to this file's directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from railway_client import RailwayClient

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_registry.json")

# Known domain → alias mappings (extend as needed)
KNOWN_DOMAINS = {
    "systems3-project-reporter": "project_reporter",
    "businessventures": "causal_affect",
    "epistemic-platform": "epistemic_platform",
}


def slugify(name: str) -> str:
    """Turn a project name into a safe alias."""
    return name.lower().replace(" ", "_").replace("-", "_")


def guess_alias(project_name: str) -> str:
    """Try to match a project name to a known alias, else slugify."""
    lower = project_name.lower()
    for fragment, alias in KNOWN_DOMAINS.items():
        if fragment in lower:
            return alias
    return slugify(project_name)


def main():
    write = "--write" in sys.argv

    try:
        client = RailwayClient()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("Fetching projects from Railway...\n")
    projects = client.list_projects()

    if not projects:
        print("No projects found for this token.")
        sys.exit(0)

    registry = {"_comment": "Auto-populated by discover.py", "apps": {}}

    for proj in projects:
        alias = guess_alias(proj["name"])
        prod_env = None
        for env in proj["environments"]:
            if env["name"].lower() == "production":
                prod_env = env
                break
        if not prod_env and proj["environments"]:
            prod_env = proj["environments"][0]

        services_map = {}
        for svc in proj["services"]:
            svc_key = slugify(svc["name"])
            services_map[svc_key] = {
                "service_id": svc["id"],
                "name": svc["name"],
            }

        registry["apps"][alias] = {
            "project_id": proj["id"],
            "project_name": proj["name"],
            "environment_id": prod_env["id"] if prod_env else "",
            "environment_name": prod_env["name"] if prod_env else "",
            "services": services_map,
        }

        # Print summary
        env_name = prod_env["name"] if prod_env else "(none)"
        print(f"  {alias}")
        print(f"    Project:     {proj['name']} ({proj['id'][:12]}...)")
        print(f"    Environment: {env_name}")
        for svc_key, svc in services_map.items():
            print(f"    Service:     {svc_key} → {svc['name']} ({svc['service_id'][:12]}...)")
        print()

    if write:
        with open(REGISTRY_PATH, "w") as f:
            json.dump(registry, f, indent=2)
        print(f"✅ Wrote registry to {REGISTRY_PATH}")
    else:
        print("Run with --write to save to app_registry.json")
        print(json.dumps(registry, indent=2))


if __name__ == "__main__":
    main()
