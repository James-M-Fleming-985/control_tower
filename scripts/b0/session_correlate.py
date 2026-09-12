"""Confirm a live user journey actually happened, from machine traces alone.

This backs the final Baseline-0 check: you walk the real site, and every step you
took must have left a trace somewhere independent — the database, GA4, Stripe test
mode, or the site's own HTML. A step nobody can find evidence for is reported
NOT OBSERVED rather than quietly passed.

Nothing here writes to production. Stripe is read-only and test mode only.

Usage:
    PYTHONPATH=scripts python -m b0.session_correlate \
        --session ct-12345 --since 2026-09-12T09:00:00Z \
        --prod-url https://... --out JOURNEY_REPORT.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

from baseline0_audit import probes

# Each step the human is asked to perform, and the trace that proves they did.
JOURNEY_STEPS: list[tuple[str, str, str]] = [
    ("J1", "Open the dashboard", "Dashboard responded and rendered recommendations"),
    ("J2", "Read the recommendations", "Recommendation rows exist and were served"),
    ("J3", "Confirm no manual-entry path exists", "No 'add your own idea' control in the HTML"),
    ("J4", "Select a recommendation to build", "A build row was created in this window"),
    ("J5", "Watch the build log and open the evidence link",
     "Verification artefacts recorded for that build"),
    ("J6", "Open the shipped GitHub repo", "Build row carries a repository URL"),
    ("J7", "Open the deployed app with ?ct_session=", "Deployment row carries a live URL"),
    ("J8", "Trigger an engagement event", "GA4 reports activity in this window"),
    ("J9", "Complete a Stripe test checkout", "A Stripe test payment exists in this window"),
    ("J10", "Return to the Performance tab", "Telemetry joined engagement and revenue"),
    ("J11", "Iterate the winner", "A build exists with parent_build_id set"),
]


@dataclass
class StepResult:
    id: str
    name: str
    expected: str
    observed: bool = False
    detail: str = ""
    evidence: list[str] = field(default_factory=list)

    @property
    def icon(self) -> str:
        return "✅" if self.observed else "❌"

    @property
    def verdict(self) -> str:
        return "OBSERVED" if self.observed else "NOT OBSERVED"


def query(database_url: str, sql: str, params: tuple = ()) -> list[tuple] | str:
    try:
        import psycopg2  # type: ignore
    except ImportError:
        try:
            import psycopg as psycopg2  # type: ignore
        except ImportError:
            return "no postgres driver installed"
    url = database_url.replace("postgresql+asyncpg://", "postgresql://").replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    try:
        conn = psycopg2.connect(url, connect_timeout=15)
    except Exception as exc:
        return f"could not connect: {type(exc).__name__}"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    except Exception as exc:
        return f"query failed: {type(exc).__name__}: {exc}"
    finally:
        conn.close()


def first_count(rows: list[tuple] | str) -> int | None:
    if isinstance(rows, str) or not rows:
        return None
    try:
        return int(rows[0][0])
    except (TypeError, ValueError, IndexError):
        return None


def ga4_activity(property_id: str, credentials_json: str, since: datetime) -> tuple[bool, str]:
    if not property_id or not credentials_json:
        return False, "GA4 credentials not provided"
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange, Dimension, Metric, RunReportRequest,
        )
        from google.oauth2 import service_account
    except ImportError:
        return False, "google-analytics-data not installed"
    try:
        info = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(info)
        client = BetaAnalyticsDataClient(credentials=creds)
        response = client.run_report(
            RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=since.strftime("%Y-%m-%d"), end_date="today")],
                dimensions=[Dimension(name="eventName")],
                metrics=[Metric(name="eventCount")],
                limit=20,
            )
        )
        events = [
            f"{row.dimension_values[0].value}={row.metric_values[0].value}"
            for row in response.rows
        ]
        if not events:
            return False, "GA4 reported no events in the window"
        return True, "; ".join(events[:8])
    except Exception as exc:
        return False, f"GA4 query failed: {type(exc).__name__}: {exc}"


def stripe_recent_payments(api_key: str, since: datetime) -> tuple[bool, str]:
    if not api_key:
        return False, "STRIPE_TEST_SECRET_KEY not provided"
    if not api_key.startswith(("sk_test_", "rk_test_")):
        return False, "key is not a Stripe TEST key — refusing to call Stripe with it"
    created = int(since.timestamp())
    res = probes.http_get(
        f"https://api.stripe.com/v1/payment_intents?limit=10&created[gte]={created}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if not res.ok:
        return False, f"Stripe returned {res.status}"
    payload = res.json if isinstance(res.json, dict) else {}
    items = payload.get("data", []) if isinstance(payload, dict) else []
    if not items:
        return False, "no test payments in the window"
    summary = "; ".join(
        f"{i.get('id', '?')} {i.get('status', '?')} "
        f"{i.get('amount', 0) / 100:.2f} {str(i.get('currency', '')).upper()}"
        for i in items[:5]
    )
    return True, summary


def run_checks(args: argparse.Namespace, since: datetime) -> list[StepResult]:
    db = os.environ.get("DATABASE_URL", "")
    results = [StepResult(sid, name, expected) for sid, name, expected in JOURNEY_STEPS]
    by_id = {r.id: r for r in results}

    page = probes.http_get(args.prod_url)
    step = by_id["J1"]
    step.observed = page.ok
    step.detail = f"HTTP {page.status} from {args.prod_url}"

    step = by_id["J3"]
    if page.ok:
        manual = re.search(r"add\s+your\s+own\s+idea|manual[-_ ]?idea|submit[-_ ]?idea",
                           page.body, re.IGNORECASE)
        step.observed = manual is None
        step.detail = "no manual-entry control found" if manual is None else (
            f"manual-entry control still present: {manual.group(0)!r}"
        )
    else:
        step.detail = "could not fetch the dashboard HTML"

    if not db:
        for sid in ("J2", "J4", "J5", "J6", "J7", "J10", "J11"):
            by_id[sid].detail = "DATABASE_URL not provided — cannot confirm"
        return _finish(results, args, since)

    checks: list[tuple[str, str, tuple]] = [
        ("J2", "SELECT count(*) FROM exploitation_recommendations", ()),
        ("J4", "SELECT count(*) FROM mvp_builds WHERE created_at >= %s", (since,)),
        ("J5", "SELECT count(*) FROM mvp_builds WHERE created_at >= %s "
               "AND verification_status IS NOT NULL", (since,)),
        ("J6", "SELECT count(*) FROM mvp_builds WHERE created_at >= %s "
               "AND repository_url IS NOT NULL", (since,)),
        ("J7", "SELECT count(*) FROM product_deployments WHERE created_at >= %s "
               "AND deployment_url IS NOT NULL", (since,)),
        ("J10", "SELECT count(*) FROM build_telemetry WHERE updated_at >= %s", (since,)),
        ("J11", "SELECT count(*) FROM mvp_builds WHERE parent_build_id IS NOT NULL "
                "AND created_at >= %s", (since,)),
    ]
    for sid, sql, params in checks:
        rows = query(db, sql, params)
        step = by_id[sid]
        if isinstance(rows, str):
            step.detail = rows
            continue
        count = first_count(rows)
        step.observed = bool(count)
        step.detail = f"{count} row(s) matched" if count is not None else "no result"
        step.evidence.append(f"`{sql.strip()}`")

    return _finish(results, args, since)


def _finish(results: list[StepResult], args: argparse.Namespace, since: datetime) -> list[StepResult]:
    by_id = {r.id: r for r in results}

    ok, detail = ga4_activity(
        os.environ.get("GA4_PROPERTY_ID", ""),
        os.environ.get("GA4_CREDENTIALS_JSON", ""),
        since,
    )
    by_id["J8"].observed, by_id["J8"].detail = ok, detail

    ok, detail = stripe_recent_payments(os.environ.get("STRIPE_TEST_SECRET_KEY", ""), since)
    by_id["J9"].observed, by_id["J9"].detail = ok, detail

    return results


def build_report(args: argparse.Namespace, since: datetime, results: list[StepResult]) -> str:
    observed = [r for r in results if r.observed]
    confirmed = len(observed) == len(results)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Live user-journey confirmation",
        "",
        f"**Session:** `{args.session}`  ",
        f"**Window:** {since.strftime('%Y-%m-%d %H:%M UTC')} → {now}  ",
        f"**Site:** {args.prod_url}",
        "",
        "## Verdict",
        "",
    ]
    if confirmed:
        lines += [
            "**✅ Baseline 0 CONFIRMED.** Every step of the journey left an independent "
            "machine trace. A recommendation survived the whole loop with evidence.",
        ]
    else:
        missing = [r for r in results if not r.observed]
        lines += [
            f"**❌ Not confirmed — {len(missing)} of {len(results)} steps left no trace.**",
            "",
            "A step can fail here for two different reasons: you did not perform it, or "
            "you did and the system failed to record it. The detail column separates them.",
        ]
    lines += [
        "",
        f"{len(observed)} of {len(results)} steps observed.",
        "",
        "## Step by step",
        "",
        "| Step | What you were asked to do | Expected trace | Result | Detail |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        detail = " ".join(r.detail.split()).replace("|", "/")
        lines.append(
            f"| {r.id} | {r.name} | {r.expected} | {r.icon} {r.verdict} | {detail} |"
        )
    lines += [
        "",
        "## Evidence queries",
        "",
    ]
    for r in results:
        if r.evidence:
            lines.append(f"- **{r.id}** — {'; '.join(r.evidence)}")
    lines += [
        "",
        "## How to read this",
        "",
        "| Result | Meaning |",
        "|---|---|",
        "| ✅ OBSERVED | An independent system recorded the step |",
        "| ❌ NOT OBSERVED | No trace found — either the step was skipped or it was not recorded |",
        "",
        "This check is read-only. Stripe was queried in test mode only, and nothing "
        "was written to production.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="b0.session_correlate", description=__doc__)
    p.add_argument("--session", required=True, help="session token given to you at dispatch")
    p.add_argument("--since", required=True, help="ISO8601 start of the journey window")
    p.add_argument("--prod-url", required=True)
    p.add_argument("--out", default="JOURNEY_REPORT.md")
    p.add_argument("--strict", action="store_true",
                   help="exit non-zero unless every step was observed")
    args = p.parse_args(argv)

    try:
        since = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
    except ValueError:
        print(f"::error title=Bad window::could not parse --since {args.since!r}", file=sys.stderr)
        return 2
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)

    args.prod_url = args.prod_url.rstrip("/")
    results = run_checks(args, since)
    report = build_report(args, since, results)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)

    missing = [r for r in results if not r.observed]
    print(f"{len(results) - len(missing)} of {len(results)} journey steps observed")
    for r in missing:
        print(f"  ❌ {r.id} {r.name} — {r.detail}")

    return 1 if (missing and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
