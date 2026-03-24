#!/usr/bin/env python3
"""
Browser Console MCP Server

Exposes headless browser inspection as MCP tools so agents can check
production pages for JS errors, network failures, and visual issues.

Tools:
  - browser_check      — navigate to URL, return console messages + network errors
  - browser_screenshot — navigate and return a base64 PNG screenshot
  - browser_api_check  — test an API endpoint from browser context (captures CORS)
"""

import asyncio
import json
import os
import sys

# Auto-load .env from workspace root
try:
    from dotenv import load_dotenv
    _ws_env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(os.path.abspath(_ws_env))
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from browser_client import check_page, take_screenshot, check_api_endpoint

mcp = FastMCP("browser-console")

# Known app aliases → production URLs
APP_URLS = {
    "project_reporter": "https://systems3-project-reporter-production.up.railway.app",
    "causal_affect": "https://businessventures-production.up.railway.app",
    "epistemic_platform": "https://epistemic-platform-frontend-production.up.railway.app",
}


def _resolve_url(url_or_alias: str) -> str:
    """Resolve an app alias to its production URL, or return the URL as-is."""
    if url_or_alias in APP_URLS:
        return APP_URLS[url_or_alias]
    if url_or_alias.startswith("http://") or url_or_alias.startswith("https://"):
        return url_or_alias
    # Try partial match
    for alias, url in APP_URLS.items():
        if url_or_alias in alias:
            return url
    return url_or_alias


@mcp.tool()
def browser_check(
    url: str,
    wait_seconds: int = 3,
    path: str = "/",
) -> str:
    """Navigate to a URL and return all console messages, JS exceptions, and network errors.

    Args:
        url: Full URL or app alias ('project_reporter', 'causal_affect', 'epistemic_platform')
        wait_seconds: Seconds to wait after page load for async JS (default 3)
        path: Path to append to the resolved URL (default '/')
    """
    try:
        base = _resolve_url(url)
        if path and path != "/":
            full_url = base.rstrip("/") + "/" + path.lstrip("/")
        else:
            full_url = base

        result = asyncio.run(check_page(full_url, wait_seconds=wait_seconds))
        data = result.to_dict()

        # Format as readable text
        lines = [
            f"Page Check: {data['url']}",
            f"Status: HTTP {data['status']} | Title: {data['page_title']}",
            f"Load time: {data['load_time_ms']}ms",
            f"Summary: {data['summary']}",
        ]

        if data["console_messages"]:
            lines.append(f"\n--- Console Messages ({len(data['console_messages'])}) ---")
            for msg in data["console_messages"][:50]:
                lines.append(f"  [{msg['type']}] {msg['text'][:200]}")

        if data["js_exceptions"]:
            lines.append(f"\n--- JS Exceptions ({len(data['js_exceptions'])}) ---")
            for exc in data["js_exceptions"][:20]:
                lines.append(f"  {exc[:300]}")

        if data["network_failures"]:
            lines.append(f"\n--- Network Failures ({len(data['network_failures'])}) ---")
            for f in data["network_failures"][:20]:
                lines.append(f"  {f['method']} {f['url'][:100]} → {f['status']} {f['status_text']}")

        return "\n".join(lines)
    except Exception as e:
        return f"Browser check error: {e}"


@mcp.tool()
def browser_screenshot(
    url: str,
    path: str = "/",
    full_page: bool = False,
) -> str:
    """Take a screenshot of a page and return it as base64 PNG.

    Args:
        url: Full URL or app alias
        path: Path to append to resolved URL (default '/')
        full_page: Whether to capture the full scrollable page (default False)
    """
    try:
        base = _resolve_url(url)
        if path and path != "/":
            full_url = base.rstrip("/") + "/" + path.lstrip("/")
        else:
            full_url = base

        b64 = asyncio.run(take_screenshot(full_url, full_page=full_page))
        return json.dumps({
            "url": full_url,
            "format": "png",
            "encoding": "base64",
            "data": b64,
        })
    except Exception as e:
        return f"Screenshot error: {e}"


@mcp.tool()
def browser_api_check(
    url: str,
    method: str = "GET",
    headers: str = "{}",
    body: str = "",
) -> str:
    """Test an API endpoint from a browser context to detect CORS issues.

    This makes a fetch() call from within a browser page, which will surface
    CORS errors that wouldn't appear with server-side requests.

    Args:
        url: Full API URL to test
        method: HTTP method (GET, POST, etc.)
        headers: JSON string of headers to include
        body: Request body (for POST/PUT)
    """
    try:
        parsed_headers = json.loads(headers) if headers else {}
    except json.JSONDecodeError:
        return "Error: 'headers' must be a valid JSON string"

    try:
        result = asyncio.run(
            check_api_endpoint(url, method=method, headers=parsed_headers, body=body or None)
        )

        lines = [f"API Check: {method} {url}"]
        if result.get("cors_error"):
            lines.append(f"CORS ERROR: {result.get('error', 'blocked by CORS policy')}")
        else:
            lines.append(f"Status: {result['status']} {result['status_text']}")
            lines.append(f"OK: {result['ok']}")

            resp_headers = result.get("headers", {})
            cors_headers = {k: v for k, v in resp_headers.items() if "access-control" in k.lower()}
            if cors_headers:
                lines.append(f"CORS headers: {json.dumps(cors_headers)}")

            body_text = result.get("body", "")
            if len(body_text) > 1000:
                body_text = body_text[:1000] + "...[truncated]"
            lines.append(f"Body: {body_text}")

        return "\n".join(lines)
    except Exception as e:
        return f"API check error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
