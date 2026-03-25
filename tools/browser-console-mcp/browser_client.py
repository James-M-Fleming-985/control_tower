"""
Playwright-based browser client for headless console/network inspection.

Launches Chromium headless, navigates to URLs, and captures:
- Console messages (log, warn, error, info)
- JavaScript exceptions
- Network failures (4xx, 5xx responses)
- Screenshots (PNG, base64-encoded)
"""

import asyncio
import base64
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Page, BrowserContext

logger = logging.getLogger(__name__)

DEFAULT_WAIT = 3  # seconds to wait after navigation for JS to execute
DEFAULT_TIMEOUT = 15000  # ms for navigation timeout


@dataclass
class ConsoleEntry:
    type: str  # log, warn, error, info, debug
    text: str


@dataclass
class NetworkFailure:
    url: str
    status: int
    method: str
    status_text: str


@dataclass
class PageCheckResult:
    url: str
    status: int
    console_messages: List[ConsoleEntry] = field(default_factory=list)
    js_exceptions: List[str] = field(default_factory=list)
    network_failures: List[NetworkFailure] = field(default_factory=list)
    page_title: str = ""
    load_time_ms: float = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "page_title": self.page_title,
            "load_time_ms": round(self.load_time_ms, 1),
            "console_messages": [
                {"type": m.type, "text": m.text} for m in self.console_messages
            ],
            "js_exceptions": self.js_exceptions,
            "network_failures": [
                {"url": f.url, "status": f.status, "method": f.method, "status_text": f.status_text}
                for f in self.network_failures
            ],
            "summary": self._summary(),
        }

    def _summary(self) -> str:
        errors = [m for m in self.console_messages if m.type == "error"]
        warns = [m for m in self.console_messages if m.type == "warning"]
        parts = [f"HTTP {self.status}"]
        if errors:
            parts.append(f"{len(errors)} console errors")
        if warns:
            parts.append(f"{len(warns)} warnings")
        if self.js_exceptions:
            parts.append(f"{len(self.js_exceptions)} JS exceptions")
        if self.network_failures:
            parts.append(f"{len(self.network_failures)} network failures")
        if not errors and not self.js_exceptions and not self.network_failures:
            parts.append("clean")
        return " | ".join(parts)


async def _setup_auth(context: BrowserContext, auth: Optional[Dict] = None):
    """Apply authentication if provided."""
    if not auth:
        return
    if "cookie_name" in auth and "cookie_value" in auth:
        await context.add_cookies([{
            "name": auth["cookie_name"],
            "value": auth["cookie_value"],
            "domain": auth.get("domain", ""),
            "path": "/",
        }])


async def check_page(
    url: str,
    wait_seconds: int = DEFAULT_WAIT,
    auth: Optional[Dict] = None,
) -> PageCheckResult:
    """Navigate to URL and collect console output, errors, and network failures."""
    result = PageCheckResult(url=url, status=0)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="ControlTower-BrowserMCP/1.0",
        )

        # Inject CSP violation listener before any page loads
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

        await _setup_auth(context, auth)
        page = await context.new_page()

        # Collect console messages
        page.on("console", lambda msg: result.console_messages.append(
            ConsoleEntry(type=msg.type, text=msg.text)
        ))

        # Collect JS exceptions
        page.on("pageerror", lambda exc: result.js_exceptions.append(str(exc)))

        # Collect network failures (4xx/5xx responses)
        page.on("response", lambda resp: (
            result.network_failures.append(
                NetworkFailure(
                    url=resp.url,
                    status=resp.status,
                    method=resp.request.method,
                    status_text=resp.status_text,
                )
            ) if resp.status >= 400 else None
        ))

        # Collect completely failed requests (DNS, CORS, timeout, connection refused)
        page.on("requestfailed", lambda req: result.network_failures.append(
            NetworkFailure(
                url=req.url,
                status=0,
                method=req.method,
                status_text=req.failure or "request failed",
            )
        ))

        try:
            import time
            start = time.monotonic()
            response = await page.goto(url, timeout=DEFAULT_TIMEOUT, wait_until="networkidle")
            result.load_time_ms = (time.monotonic() - start) * 1000
            result.status = response.status if response else 0
            result.page_title = await page.title()

            # Wait extra time for async JS to fire
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

            # Collect CSP violations from injected listener
            try:
                csp = await page.evaluate("window.__cspViolations || []")
                for v in csp:
                    result.js_exceptions.append(
                        f"[CSP] Blocked {v.get('blocked', '?')} — violates {v.get('directive', '?')}"
                    )
            except Exception:
                pass
        except Exception as e:
            result.js_exceptions.append(f"Navigation error: {e}")
        finally:
            await browser.close()

    return result


async def take_screenshot(
    url: str,
    auth: Optional[Dict] = None,
    full_page: bool = False,
) -> str:
    """Navigate to URL and return a base64-encoded PNG screenshot."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="ControlTower-BrowserMCP/1.0",
        )
        await _setup_auth(context, auth)
        page = await context.new_page()

        try:
            await page.goto(url, timeout=DEFAULT_TIMEOUT, wait_until="networkidle")
            await asyncio.sleep(1)  # brief wait for rendering
            screenshot_bytes = await page.screenshot(full_page=full_page)
            return base64.b64encode(screenshot_bytes).decode("utf-8")
        finally:
            await browser.close()


async def check_api_endpoint(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[str] = None,
) -> Dict[str, Any]:
    """Make an HTTP request from a browser context to test CORS and API endpoints."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to a blank page first (needed for evaluate context)
        await page.goto("about:blank")

        # Build fetch options  
        fetch_opts = {"method": method, "headers": headers or {}}
        if body and method.upper() != "GET":
            fetch_opts["body"] = body

        try:
            result = await page.evaluate(
                """async ([url, opts]) => {
                    try {
                        const resp = await fetch(url, opts);
                        const text = await resp.text();
                        return {
                            status: resp.status,
                            status_text: resp.statusText,
                            headers: Object.fromEntries(resp.headers.entries()),
                            body: text.substring(0, 5000),
                            ok: resp.ok,
                            cors_error: false
                        };
                    } catch (e) {
                        return {
                            status: 0,
                            status_text: '',
                            headers: {},
                            body: '',
                            ok: false,
                            cors_error: true,
                            error: e.message
                        };
                    }
                }""",
                [url, fetch_opts],
            )
            return result
        finally:
            await browser.close()
