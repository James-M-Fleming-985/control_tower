#!/usr/bin/env python3
"""
Railway Logs MCP Server

Exposes Railway deploy/build logs as MCP tools so agents can inspect
deployment status and logs without manual copy-pasting.

Tools:
  - railway_deploy_logs   — runtime logs from latest (or specific) deployment
  - railway_build_logs    — build/compile output
  - railway_list_deployments — recent deployments with status
  - railway_latest_errors — convenience: ERROR/FATAL lines only
"""

import json
import os
import sys

# Auto-load .env from workspace root so RAILWAY_TOKEN is available
try:
    from dotenv import load_dotenv
    _ws_env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(os.path.abspath(_ws_env))
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from railway_client import RailwayClient

mcp = FastMCP("railway-logs")

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_registry.json")

# Maximum lines to return to avoid blowing up context windows
MAX_LINES = 200


def _load_registry() -> dict:
    """Load app registry; return empty dict on missing/invalid."""
    try:
        with open(REGISTRY_PATH) as f:
            return json.load(f).get("apps", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _resolve_app(app: str, service: str | None = None) -> tuple[str, str]:
    """Resolve app alias + optional service to (service_id, environment_id).

    Returns (service_id, environment_id) or raises ValueError with helpful message.
    """
    registry = _load_registry()
    if not registry:
        raise ValueError(
            "App registry is empty. Run: python3 tools/railway-logs-mcp/discover.py --write"
        )

    app_entry = registry.get(app)
    if not app_entry:
        available = ", ".join(registry.keys())
        raise ValueError(f"Unknown app '{app}'. Available: {available}")

    env_id = app_entry.get("environment_id", "")
    if not env_id:
        raise ValueError(f"No environment configured for '{app}'")

    services = app_entry.get("services", {})
    if not services:
        raise ValueError(f"No services found for '{app}'")

    if service:
        svc = services.get(service)
        if not svc:
            available = ", ".join(services.keys())
            raise ValueError(
                f"Unknown service '{service}' for app '{app}'. Available: {available}"
            )
        return svc["service_id"], env_id

    # Default to first (or only) service
    first_svc = next(iter(services.values()))
    return first_svc["service_id"], env_id


def _get_client() -> RailwayClient:
    return RailwayClient()


def _format_log_lines(logs: list[dict], limit: int) -> str:
    """Format log entries into readable text, truncating if needed."""
    if not logs:
        return "(no logs found)"

    lines = []
    for entry in logs:
        ts = entry.get("timestamp", "")
        sev = entry.get("severity", "")
        msg = entry.get("message", "")
        prefix = f"[{ts}]" if ts else ""
        if sev:
            prefix = f"{prefix} [{sev}]"
        lines.append(f"{prefix} {msg}".strip())

    if len(lines) > limit:
        truncated = len(lines) - limit
        lines = lines[-limit:]
        lines.insert(0, f"[...truncated {truncated} earlier lines, showing last {limit}]")

    return "\n".join(lines)


@mcp.tool()
def railway_deploy_logs(
    app: str,
    service: str | None = None,
    lines: int = 100,
    filter: str | None = None,
) -> str:
    """Get runtime/deploy logs from the latest deployment of a Railway app.

    Args:
        app: App alias from registry (e.g. 'project_reporter', 'causal_affect', 'epistemic_platform')
        service: Optional service name within the app (defaults to first/only service)
        lines: Max lines to return (default 100, max 200)
        filter: Optional text filter — only return lines containing this string
    """
    try:
        service_id, env_id = _resolve_app(app, service)
        client = _get_client()
        deployment_id = client.get_latest_deployment_id(service_id, env_id)
        if not deployment_id:
            return f"No deployments found for {app}"

        logs = client.get_deploy_logs(deployment_id, limit=500)

        if filter:
            filter_lower = filter.lower()
            logs = [l for l in logs if filter_lower in l.get("message", "").lower()]

        limit = min(lines, MAX_LINES)
        return _format_log_lines(logs, limit)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Railway API error: {e}"


@mcp.tool()
def railway_build_logs(
    app: str,
    service: str | None = None,
    lines: int = 100,
) -> str:
    """Get build/compile logs from the latest deployment.

    Args:
        app: App alias from registry
        service: Optional service name within the app
        lines: Max lines to return (default 100, max 200)
    """
    try:
        service_id, env_id = _resolve_app(app, service)
        client = _get_client()
        deployment_id = client.get_latest_deployment_id(service_id, env_id)
        if not deployment_id:
            return f"No deployments found for {app}"

        logs = client.get_build_logs(deployment_id, limit=500)
        limit = min(lines, MAX_LINES)
        return _format_log_lines(logs, limit)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Railway API error: {e}"


@mcp.tool()
def railway_list_deployments(
    app: str,
    service: str | None = None,
    limit: int = 5,
) -> str:
    """List recent deployments for an app with their status.

    Args:
        app: App alias from registry
        service: Optional service name within the app
        limit: Number of deployments to show (default 5, max 20)
    """
    try:
        service_id, env_id = _resolve_app(app, service)
        client = _get_client()
        deploys = client.list_deployments(service_id, env_id, limit=min(limit, 20))

        if not deploys:
            return f"No deployments found for {app}"

        lines = [f"Recent deployments for {app}:\n"]
        for d in deploys:
            status = d["status"]
            created = d["created_at"][:19] if d["created_at"] else "?"
            commit = d["commit_message"][:60] if d["commit_message"] else "(no message)"
            sha = d["commit_hash"][:8] if d["commit_hash"] else ""
            lines.append(f"  {status:12s}  {created}  {sha}  {commit}")

        return "\n".join(lines)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Railway API error: {e}"


@mcp.tool()
def railway_latest_errors(
    app: str,
    service: str | None = None,
) -> str:
    """Get only ERROR/FATAL/Exception lines from the latest deployment's logs.

    A convenience tool for quickly checking if the latest deploy has issues.

    Args:
        app: App alias from registry
        service: Optional service name within the app
    """
    try:
        service_id, env_id = _resolve_app(app, service)
        client = _get_client()
        deployment_id = client.get_latest_deployment_id(service_id, env_id)
        if not deployment_id:
            return f"No deployments found for {app}"

        logs = client.get_deploy_logs(deployment_id, limit=500)

        error_keywords = ("error", "fatal", "exception", "traceback", "critical")
        errors = [
            l for l in logs
            if any(kw in l.get("message", "").lower() for kw in error_keywords)
            or l.get("severity", "").lower() in ("error", "fatal", "critical")
        ]

        if not errors:
            return f"No errors found in latest deployment logs for {app}"

        return _format_log_lines(errors, MAX_LINES)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Railway API error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
