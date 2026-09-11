"""Live, read-only probes against production and third-party services.

Nothing here writes to production. Stripe is exercised in test mode only.
"""

from __future__ import annotations

import json
import os
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass

USER_AGENT = "causal-affect-baseline0-audit/1.0"
TIMEOUT = 20


@dataclass
class HttpResult:
    ok: bool
    status: int
    body: str
    error: str | None = None

    @property
    def json(self) -> object | None:
        try:
            return json.loads(self.body)
        except (ValueError, TypeError):
            return None


def http_get(url: str, headers: dict[str, str] | None = None, timeout: int = TIMEOUT) -> HttpResult:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read(500_000).decode("utf-8", errors="ignore")
            return HttpResult(ok=200 <= resp.status < 400, status=resp.status, body=body)
    except urllib.error.HTTPError as exc:
        body = exc.read(50_000).decode("utf-8", errors="ignore") if exc.fp else ""
        return HttpResult(ok=False, status=exc.code, body=body, error=str(exc))
    except Exception as exc:
        return HttpResult(ok=False, status=0, body="", error=f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------------- SEO


SEO_CHECKS: dict[str, str] = {
    "title": r"<title[^>]*>\s*\S",
    "meta_description": r'<meta[^>]+name=["\']description["\'][^>]+content=["\']\s*\S',
    "canonical": r'<link[^>]+rel=["\']canonical["\']',
    "open_graph": r'<meta[^>]+property=["\']og:',
    "twitter_card": r'<meta[^>]+name=["\']twitter:',
    "json_ld": r'<script[^>]+type=["\']application/ld\+json["\']',
    "h1": r"<h1[\s>]",
    "lang_attr": r"<html[^>]+lang=",
    "viewport": r'<meta[^>]+name=["\']viewport["\']',
}


def audit_seo_html(html: str) -> dict[str, bool]:
    return {name: bool(re.search(pattern, html, re.IGNORECASE)) for name, pattern in SEO_CHECKS.items()}


def check_robots_and_sitemap(base_url: str) -> dict[str, bool]:
    base = base_url.rstrip("/")
    robots = http_get(f"{base}/robots.txt")
    sitemap = http_get(f"{base}/sitemap.xml")
    return {
        "robots_txt": robots.ok and "user-agent" in robots.body.lower(),
        "sitemap_xml": sitemap.ok and "<urlset" in sitemap.body.lower(),
    }


GA4_PLACEHOLDERS = {"G-XXXXXXXXXX", "G-ABC123DEF4", "G-0000000000"}


def extract_ga4_ids(html: str) -> list[str]:
    return sorted(set(re.findall(r"G-[A-Z0-9]{6,12}", html)))


def ga4_ids_are_real(ids: list[str]) -> bool:
    real = [i for i in ids if i.upper() not in GA4_PLACEHOLDERS]
    return bool(real)


# ---------------------------------------------------------------- Stripe


def stripe_test_mode_check(api_key: str) -> tuple[bool, str]:
    """List products read-only. Refuses to touch a live key."""
    if not api_key:
        return False, "no key provided"
    if not api_key.startswith(("sk_test_", "rk_test_")):
        return False, "key is not a Stripe TEST key — refusing to call Stripe with it"
    res = http_get(
        "https://api.stripe.com/v1/products?limit=3",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if not res.ok:
        return False, f"Stripe API returned {res.status}: {res.error or res.body[:200]}"
    payload = res.json or {}
    count = len(payload.get("data", [])) if isinstance(payload, dict) else 0
    return True, f"Stripe test mode reachable, {count} product(s) visible"


# ---------------------------------------------------------------- Database


def database_counts(database_url: str, tables: list[str]) -> dict[str, int | str]:
    """Row counts for tables of interest. Returns a message per table if absent."""
    try:
        import psycopg2  # type: ignore
    except ImportError:
        try:
            import psycopg as psycopg2  # type: ignore
        except ImportError:
            return {"_error": "no postgres driver installed (psycopg2/psycopg)"}

    url = database_url.replace("postgresql+asyncpg://", "postgresql://").replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    out: dict[str, int | str] = {}
    try:
        conn = psycopg2.connect(url, connect_timeout=15)
    except Exception as exc:
        return {"_error": f"connection failed: {type(exc).__name__}: {exc}"}
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            )
            present = {row[0].lower() for row in cur.fetchall()}
            out["_tables_present"] = len(present)
            for table in tables:
                if table.lower() not in present:
                    out[table] = "TABLE MISSING"
                    continue
                try:
                    cur.execute(f'SELECT COUNT(*) FROM "{table}"')  # noqa: S608 - name from allowlist
                    out[table] = int(cur.fetchone()[0])
                except Exception as exc:
                    out[table] = f"query failed: {exc}"
    finally:
        conn.close()
    return out


# ---------------------------------------------------------------- GA4


def ga4_realtime_active_users(property_id: str, credentials_json: str) -> tuple[bool, str]:
    """Realtime API is used deliberately: the standard Data API lags 24-48h,
    which makes same-night round-trip verification impossible."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient  # type: ignore
        from google.analytics.data_v1beta.types import RunRealtimeReportRequest, Metric  # type: ignore
        from google.oauth2 import service_account  # type: ignore
    except ImportError:
        return False, "google-analytics-data not installed"

    try:
        info = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(info)
        client = BetaAnalyticsDataClient(credentials=creds)
        request = RunRealtimeReportRequest(
            property=f"properties/{property_id}", metrics=[Metric(name="activeUsers")]
        )
        response = client.run_realtime_report(request)
        total = sum(int(row.metric_values[0].value) for row in response.rows) if response.rows else 0
        return True, f"GA4 realtime reachable, activeUsers={total}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


# ---------------------------------------------------------------- GitHub


def github_repo_info(repo: str, token: str | None) -> HttpResult:
    headers = {"Accept": "application/vnd.github+json"}
    token = token or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return http_get(f"https://api.github.com/repos/{repo}", headers=headers)
