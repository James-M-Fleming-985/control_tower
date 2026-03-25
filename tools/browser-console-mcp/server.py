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

from playwright.async_api import async_playwright

mcp = FastMCP("browser-console")

# ── Auth credentials from env (for authenticated page checks) ──
APP_EMAIL = os.environ.get("APP_EMAIL", "")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")

# Known app aliases → production URLs
APP_URLS = {
    "project_reporter": "https://web-production-19783.up.railway.app",
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
async def browser_check(
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

        result = await check_page(full_url, wait_seconds=wait_seconds)
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
async def browser_screenshot(
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

        b64 = await take_screenshot(full_url, full_page=full_page)
        return json.dumps({
            "url": full_url,
            "format": "png",
            "encoding": "base64",
            "data": b64,
        })
    except Exception as e:
        return f"Screenshot error: {e}"


@mcp.tool()
async def browser_api_check(
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
        result = await check_api_endpoint(url, method=method, headers=parsed_headers, body=body or None)

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


@mcp.tool()
async def browser_check_authenticated(
    url: str,
    wait_seconds: int = 5,
    path: str = "/dashboard",
) -> str:
    """Navigate to an authenticated page after logging in. Captures console errors, JS exceptions, network failures.

    Logs in via the /login form using APP_EMAIL and APP_PASSWORD env vars,
    then navigates to the target path and collects all browser console output.

    Args:
        url: Full URL or app alias ('project_reporter', 'causal_affect', 'epistemic_platform')
        wait_seconds: Seconds to wait after page load for async JS (default 5)
        path: Path to navigate to after login (default '/dashboard')
    """
    if not APP_EMAIL or not APP_PASSWORD:
        return "Error: APP_EMAIL and APP_PASSWORD environment variables must be set"

    try:
        base = _resolve_url(url)
        login_url = base.rstrip("/") + "/login"
        target_url = base.rstrip("/") + "/" + path.lstrip("/")

        console_messages = []
        js_exceptions = []
        network_failures = []
        request_failures = []
        csp_violations = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="ControlTower-BrowserMCP/1.0",
            )
            page = await context.new_page()

            # Inject CSP violation listener as early as possible
            await context.add_init_script("""
                window.__cspViolations = [];
                document.addEventListener('securitypolicyviolation', function(e) {
                    window.__cspViolations.push({
                        directive: e.violatedDirective,
                        blocked: e.blockedURI,
                        policy: e.originalPolicy ? e.originalPolicy.substring(0, 200) : '',
                        source: e.sourceFile || '',
                        line: e.lineNumber || 0,
                    });
                    console.error('[CSP] Blocked ' + e.blockedURI + ' — violates ' + e.violatedDirective);
                });
            """)

            # Step 1: Navigate to login page
            await page.goto(login_url, timeout=15000, wait_until="networkidle")

            # Step 2: Fill and submit login form
            await page.fill('input[name="email"]', APP_EMAIL)
            await page.fill('input[name="password"]', APP_PASSWORD)
            await page.click('button[type="submit"]')
            await page.wait_for_load_state("networkidle")

            # Check if login succeeded (should redirect away from /login)
            if "/login" in page.url:
                await browser.close()
                return f"Login failed — still on {page.url}. Check APP_EMAIL/APP_PASSWORD."

            # Step 3: Attach ALL listeners before navigating to target
            page.on("console", lambda msg: console_messages.append(
                {"type": msg.type, "text": msg.text}
            ))
            page.on("pageerror", lambda exc: js_exceptions.append(str(exc)))
            page.on("response", lambda resp: (
                network_failures.append({
                    "method": resp.request.method,
                    "url": resp.url,
                    "status": resp.status,
                    "status_text": resp.status_text,
                }) if resp.status >= 400 else None
            ))
            # Capture completely failed requests (DNS, CORS, timeout, connection refused)
            page.on("requestfailed", lambda req: request_failures.append({
                "method": req.method,
                "url": req.url,
                "failure": req.failure,
                "resource_type": req.resource_type,
            }))

            import time
            start = time.monotonic()
            response = await page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
            load_ms = round((time.monotonic() - start) * 1000, 1)
            status = response.status if response else 0
            title = await page.title()

            # Wait for async JS
            if wait_seconds > 0:
                import asyncio as _aio
                await _aio.sleep(wait_seconds)

            # Collect CSP violations from injected listener
            try:
                csp_violations = await page.evaluate("window.__cspViolations || []")
            except Exception:
                csp_violations = []

            await browser.close()

        # Format output
        errors = [m for m in console_messages if m["type"] == "error"]
        warns = [m for m in console_messages if m["type"] == "warning"]

        parts = [f"HTTP {status}"]
        if errors:
            parts.append(f"{len(errors)} console errors")
        if warns:
            parts.append(f"{len(warns)} warnings")
        if js_exceptions:
            parts.append(f"{len(js_exceptions)} JS exceptions")
        if network_failures:
            parts.append(f"{len(network_failures)} network failures (4xx/5xx)")
        if request_failures:
            parts.append(f"{len(request_failures)} failed requests (DNS/CORS/timeout)")
        if csp_violations:
            parts.append(f"{len(csp_violations)} CSP violations")
        if not errors and not js_exceptions and not network_failures and not request_failures and not csp_violations:
            parts.append("clean")

        lines = [
            f"Authenticated Page Check: {target_url}",
            f"Status: HTTP {status} | Title: {title}",
            f"Load time: {load_ms}ms",
            f"Summary: {' | '.join(parts)}",
        ]

        if console_messages:
            lines.append(f"\n--- Console Messages ({len(console_messages)}) ---")
            for msg in console_messages[:80]:
                lines.append(f"  [{msg['type']}] {msg['text'][:300]}")

        if js_exceptions:
            lines.append(f"\n--- JS Exceptions ({len(js_exceptions)}) ---")
            for exc in js_exceptions[:20]:
                lines.append(f"  {exc[:500]}")

        if network_failures:
            lines.append(f"\n--- Network Failures ({len(network_failures)}) ---")
            for nf in network_failures[:30]:
                lines.append(f"  {nf['method']} {nf['url'][:150]} → {nf['status']} {nf['status_text']}")

        if request_failures:
            lines.append(f"\n--- Failed Requests ({len(request_failures)}) ---")
            for rf in request_failures[:30]:
                lines.append(f"  [{rf['resource_type']}] {rf['method']} {rf['url'][:150]} → {rf['failure']}")

        if csp_violations:
            lines.append(f"\n--- CSP Violations ({len(csp_violations)}) ---")
            for cv in csp_violations[:30]:
                lines.append(f"  Blocked: {cv.get('blocked', '?')[:150]} — violates: {cv.get('directive', '?')}")

        return "\n".join(lines)
    except Exception as e:
        return f"Authenticated browser check error: {e}"


@mcp.tool()
async def browser_check_authenticated_interactive(
    url: str,
    path: str = "/dashboard",
    click_selector: str = "",
    click_text: str = "",
    wait_seconds: int = 5,
    post_click_wait: int = 3,
) -> str:
    """Login, navigate to a page, optionally click an element, and capture all errors.

    Use this when errors only appear after user interaction (clicking events,
    opening modals, toggling panels, etc.).

    Args:
        url: Full URL or app alias
        path: Path to navigate to after login (default '/dashboard')
        click_selector: CSS selector of element to click (e.g. '.fc-event', 'button.ai-chat-toggle')
        click_text: Text content of element to click (alternative to selector, e.g. 'View Details')
        wait_seconds: Seconds to wait after page load before clicking (default 5)
        post_click_wait: Seconds to wait after clicking for errors to surface (default 3)
    """
    if not APP_EMAIL or not APP_PASSWORD:
        return "Error: APP_EMAIL and APP_PASSWORD environment variables must be set"

    try:
        base = _resolve_url(url)
        login_url = base.rstrip("/") + "/login"
        target_url = base.rstrip("/") + "/" + path.lstrip("/")

        console_messages = []
        js_exceptions = []
        network_failures = []
        request_failures = []
        csp_violations = []
        click_result = "no click requested"

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="ControlTower-BrowserMCP/1.0",
            )
            page = await context.new_page()

            # Inject CSP violation listener as early as possible
            await context.add_init_script("""
                window.__cspViolations = [];
                document.addEventListener('securitypolicyviolation', function(e) {
                    window.__cspViolations.push({
                        directive: e.violatedDirective,
                        blocked: e.blockedURI,
                        source: e.sourceFile || '',
                        line: e.lineNumber || 0,
                    });
                    console.error('[CSP] Blocked ' + e.blockedURI + ' — violates ' + e.violatedDirective);
                });
            """)

            # Login
            await page.goto(login_url, timeout=15000, wait_until="networkidle")
            await page.fill('input[name="email"]', APP_EMAIL)
            await page.fill('input[name="password"]', APP_PASSWORD)
            await page.click('button[type="submit"]')
            await page.wait_for_load_state("networkidle")

            if "/login" in page.url:
                await browser.close()
                return f"Login failed — still on {page.url}."

            # Attach ALL listeners
            page.on("console", lambda msg: console_messages.append(
                {"type": msg.type, "text": msg.text}
            ))
            page.on("pageerror", lambda exc: js_exceptions.append(str(exc)))
            page.on("response", lambda resp: (
                network_failures.append({
                    "method": resp.request.method,
                    "url": resp.url,
                    "status": resp.status,
                    "status_text": resp.status_text,
                }) if resp.status >= 400 else None
            ))
            page.on("requestfailed", lambda req: request_failures.append({
                "method": req.method,
                "url": req.url,
                "failure": req.failure,
                "resource_type": req.resource_type,
            }))

            # Navigate to target
            import time
            start = time.monotonic()
            response = await page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
            load_ms = round((time.monotonic() - start) * 1000, 1)
            status = response.status if response else 0
            title = await page.title()

            # Wait for page JS to settle
            if wait_seconds > 0:
                import asyncio as _aio
                await _aio.sleep(wait_seconds)

            pre_click_msg_count = len(console_messages)
            pre_click_exc_count = len(js_exceptions)
            pre_click_net_count = len(network_failures)
            pre_click_req_count = len(request_failures)

            # Click interaction
            if click_selector or click_text:
                try:
                    if click_selector:
                        elements = await page.query_selector_all(click_selector)
                        if elements:
                            await elements[0].click()
                            click_result = f"clicked '{click_selector}' ({len(elements)} matches, clicked first)"
                        else:
                            click_result = f"no elements matched '{click_selector}'"
                    elif click_text:
                        locator = page.get_by_text(click_text, exact=False).first
                        await locator.click(timeout=5000)
                        click_result = f"clicked element with text '{click_text}'"
                except Exception as click_err:
                    click_result = f"click failed: {click_err}"

                # Wait for post-click async activity
                if post_click_wait > 0:
                    import asyncio as _aio
                    await _aio.sleep(post_click_wait)

            # Collect CSP violations from injected listener
            try:
                csp_violations = await page.evaluate("window.__cspViolations || []")
            except Exception:
                csp_violations = []

            await browser.close()

        # Format output
        errors = [m for m in console_messages if m["type"] == "error"]
        warns = [m for m in console_messages if m["type"] == "warning"]

        parts = [f"HTTP {status}"]
        if errors:
            parts.append(f"{len(errors)} console errors")
        if warns:
            parts.append(f"{len(warns)} warnings")
        if js_exceptions:
            parts.append(f"{len(js_exceptions)} JS exceptions")
        if network_failures:
            parts.append(f"{len(network_failures)} network failures")
        if request_failures:
            parts.append(f"{len(request_failures)} failed requests")
        if csp_violations:
            parts.append(f"{len(csp_violations)} CSP violations")
        if not errors and not js_exceptions and not network_failures and not request_failures and not csp_violations:
            parts.append("clean")

        lines = [
            f"Interactive Page Check: {target_url}",
            f"Status: HTTP {status} | Title: {title}",
            f"Load time: {load_ms}ms",
            f"Click: {click_result}",
            f"Summary: {' | '.join(parts)}",
        ]

        if click_selector or click_text:
            new_errors = len(console_messages) - pre_click_msg_count
            new_exc = len(js_exceptions) - pre_click_exc_count
            new_net = len(network_failures) - pre_click_net_count
            new_req = len(request_failures) - pre_click_req_count
            lines.append(f"Post-click new messages: {new_errors} console, {new_exc} exceptions, {new_net} network, {new_req} request failures")

        if console_messages:
            lines.append(f"\n--- Console Messages ({len(console_messages)}) ---")
            for msg in console_messages[:100]:
                lines.append(f"  [{msg['type']}] {msg['text'][:300]}")

        if js_exceptions:
            lines.append(f"\n--- JS Exceptions ({len(js_exceptions)}) ---")
            for exc in js_exceptions[:20]:
                lines.append(f"  {exc[:500]}")

        if network_failures:
            lines.append(f"\n--- Network Failures ({len(network_failures)}) ---")
            for nf in network_failures[:30]:
                lines.append(f"  {nf['method']} {nf['url'][:150]} → {nf['status']} {nf['status_text']}")

        if request_failures:
            lines.append(f"\n--- Failed Requests ({len(request_failures)}) ---")
            for rf in request_failures[:30]:
                lines.append(f"  [{rf['resource_type']}] {rf['method']} {rf['url'][:150]} → {rf['failure']}")

        if csp_violations:
            lines.append(f"\n--- CSP Violations ({len(csp_violations)}) ---")
            for cv in csp_violations[:30]:
                lines.append(f"  Blocked: {cv.get('blocked', '?')[:150]} — violates: {cv.get('directive', '?')}")

        return "\n".join(lines)
    except Exception as e:
        return f"Interactive browser check error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
