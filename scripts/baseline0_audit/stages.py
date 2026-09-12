"""The Baseline-0 audit stages.

Phase A  discovery + claim-vs-reality ledger
Phase B  the fifteen links of the autonomous loop, one stage each
Phase C  canary trace — where does the loop actually die?
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

import yaml

from . import probes
from .core import AuditContext, StageResult, StageSpec, Status, evidence_from

LiveProbe = Callable[[AuditContext, StageResult], None]


def capability(
    stage_id: str,
    name: str,
    phase: str,
    patterns: list[str],
    expectation: str,
    live: LiveProbe | None = None,
) -> StageSpec:
    """A stage that rates code presence across both repos, then optionally
    confirms the behaviour against the live system."""

    def run(ctx: AuditContext) -> StageResult:
        search = ctx.search(*patterns)
        result = StageResult(
            id=stage_id,
            name=name,
            status=search.status,
            summary=expectation,
            evidence=evidence_from(search),
            repos_found_in=search.repos_with_hits,
        )
        if search.status is Status.NOT_IMPLEMENTED:
            result.missing.append(f"No implementation of: {expectation}")
        elif search.status is Status.DESIGN_ONLY:
            result.missing.append("Only documentation/templates found — no executable code")
        elif search.status is Status.PARTIAL:
            result.missing.append("Code exists but no tests cover it")
        if live is not None:
            live(ctx, result)
        return result

    return StageSpec(id=stage_id, name=name, phase=phase, run=run)


# ============================================================ PHASE A


def _repo_inventory(ctx: AuditContext) -> StageResult:
    result = StageResult(
        id="A1",
        name="Two-repo inventory",
        status=Status.PASS,
        summary="Both repositories must be present before any absence can be trusted.",
    )
    for repo_name, root in ctx.repos.items():
        if not root.is_dir():
            result.status = Status.FAIL
            result.missing.append(
                f"{repo_name} not checked out at {root} — every NOT_IMPLEMENTED "
                f"finding in this report is UNRELIABLE without it"
            )
            continue
        py = len(list(root.rglob("*.py")))
        ts = len(list(root.rglob("*.ts"))) + len(list(root.rglob("*.tsx")))
        tests = len([p for p in root.rglob("test_*.py")]) + len(list(root.rglob("*.test.ts")))
        result.evidence.append(
            f"`{repo_name}` at {root}: {py} python, {ts} ts/tsx, {tests} test files"
        )
    return result


_COMPLETE_WORDS = {"complete", "completed", "done", "implemented", "shipped", "✅"}
_STATUS_KEYS = {"status", "state", "completion", "progress"}

# Paths whose whole purpose is to carry a placeholder — flagging them is noise.
_PLACEHOLDER_BY_DESIGN = re.compile(
    r"(^|/)(templates?|specs?|examples?|fixtures?|generated-mvp|docs?)/", re.IGNORECASE
)


def _claim_ledger(ctx: AuditContext) -> StageResult:
    """Every 'COMPLETE' claim in the planning YAML is verified against code."""
    result = StageResult(
        id="A2",
        name="Claim-vs-reality ledger",
        status=Status.PASS,
        summary="Planning documents claim work is complete; each claim is checked against code.",
    )
    control = ctx.repos.get("control_tower")
    if not control or not control.is_dir():
        result.status = Status.SKIPPED
        result.missing.append("control_tower not available")
        return result

    sources = [
        control / "causal_affect_outstanding_items.yaml",
        control / "Causal_Affect_Scaling_Plan.yaml",
        control / "CAUSAL_AFFECT_GOALS_IMPLEMENTATION_PLAN.yaml",
    ]
    claims: list[tuple[str, str]] = []  # (identifier, source file)
    for src in sources:
        if not src.is_file():
            continue
        try:
            data = yaml.safe_load(src.read_text(encoding="utf-8", errors="ignore"))
        except yaml.YAMLError as exc:
            result.evidence.append(f"Could not parse {src.name}: {exc}")
            continue
        for ident in _walk_claims(data):
            claims.append((ident, src.name))

    if not claims:
        result.status = Status.SKIPPED
        result.missing.append("No machine-readable COMPLETE claims found in planning YAML")
        return result

    verified, unverified = [], []
    for ident, source in claims[:60]:
        token = re.escape(ident.strip())
        if len(token) < 4:
            continue
        found = ctx.search(token, max_per_repo=2)
        if found.of_kind("code", "test"):
            verified.append(f"{ident} ({source}) → code found in {', '.join(found.repos_with_hits)}")
        else:
            unverified.append(f"{ident} ({source}) → claimed COMPLETE, no code found in either repo")

    result.evidence.append(f"{len(verified)} of {len(verified) + len(unverified)} claims backed by code")
    if len(claims) > len(verified) + len(unverified):
        result.evidence.append(
            f"Checked {len(verified) + len(unverified)} of {len(claims)} COMPLETE claims "
            f"found in planning YAML"
        )
    result.evidence.extend(verified)
    result.missing.extend(unverified)
    if unverified:
        result.status = Status.PARTIAL if verified else Status.FAIL
        result.summary = (
            f"{len(unverified)} item(s) marked COMPLETE have no corresponding code in either repo."
        )
    return result


def _walk_claims(node, depth: int = 0):
    if depth > 8:
        return
    if isinstance(node, dict):
        status_val = next(
            (str(v) for k, v in node.items() if str(k).lower() in _STATUS_KEYS and v is not None),
            None,
        )
        if status_val and any(w in status_val.lower() for w in _COMPLETE_WORDS):
            ident = next(
                (
                    str(node[k])
                    for k in ("id", "feature_id", "item_id", "name", "title", "task")
                    if node.get(k)
                ),
                None,
            )
            if ident:
                yield ident
        for value in node.values():
            yield from _walk_claims(value, depth + 1)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_claims(item, depth + 1)


def _static_health(ctx: AuditContext) -> StageResult:
    """Placeholder credentials shipped to production are a live defect, not a nit."""
    result = StageResult(
        id="A3",
        name="Static health — placeholders and secrets",
        status=Status.PASS,
        summary="Production code must not contain placeholder IDs or hard-coded secrets.",
    )
    placeholders = ctx.search(
        r"G-XXXXXXXXXX", r"G-ABC123DEF4", r"your[-_]api[-_]key", r"REPLACE[-_]ME",
        r"sk_live_[A-Za-z0-9]", max_per_repo=30,
    )

    # Baseline 0 says "no placeholders in PRODUCTION". Three things legitimately
    # contain them and are not defects: the tooling repo, files whose job is to
    # document the format, and prose describing the rule itself.
    defects = [
        h for h in placeholders.all_hits
        if h.repo != "control_tower"
        and h.kind == "code"
        and not _PLACEHOLDER_BY_DESIGN.search(h.path)
    ]
    excused = len(placeholders.all_hits) - len(defects)

    if defects:
        result.status = Status.FAIL
        result.missing = [h.render() for h in defects]
        result.summary = (
            f"{len(defects)} placeholder/secret-shaped value(s) found in production code."
        )
    else:
        result.evidence.append("No placeholder analytics IDs or live-key literals in production code")
    if excused:
        result.evidence.append(
            f"{excused} match(es) ignored: templates, specs, docs or the tooling repo, "
            f"where a placeholder is the intended content"
        )
    return result


# ============================================================ PHASE B live probes


def _probe_deploy(ctx: AuditContext, result: StageResult) -> None:
    if ctx.offline:
        result.evidence.append("Live probe skipped (offline mode)")
        return
    res = probes.http_get(ctx.prod_url)
    if res.ok:
        result.evidence.append(f"LIVE: {ctx.prod_url} returned HTTP {res.status}")
        result.status = Status.PASS if result.status is not Status.NOT_IMPLEMENTED else result.status
    else:
        result.status = Status.FAIL
        result.missing.append(f"LIVE: {ctx.prod_url} unreachable — {res.error or res.status}")


def _probe_ga4(ctx: AuditContext, result: StageResult) -> None:
    if ctx.offline:
        result.evidence.append("Live probe skipped (offline mode)")
        return
    page = probes.http_get(ctx.prod_url)
    if page.ok:
        ids = probes.extract_ga4_ids(page.body)
        has_gtag = "googletagmanager.com/gtag" in page.body or "gtag(" in page.body
        result.evidence.append(f"LIVE: gtag snippet present={has_gtag}, measurement IDs={ids or 'none'}")
        if not ids or not probes.ga4_ids_are_real(ids):
            result.status = Status.FAIL
            result.missing.append(
                "LIVE: deployed page carries no real GA4 measurement ID — no engagement data can flow"
            )
    else:
        result.missing.append(f"LIVE: could not fetch {ctx.prod_url} to inspect GA4 tag")

    if ctx.ga4_property_id and ctx.ga4_credentials:
        ok, detail = probes.ga4_realtime_active_users(ctx.ga4_property_id, ctx.ga4_credentials)
        (result.evidence if ok else result.missing).append(f"GA4 Realtime API: {detail}")
    else:
        result.evidence.append(
            "GA4 Realtime API NOT TESTED — GA4_PROPERTY_ID/GA4_CREDENTIALS_JSON not provided"
        )


def _probe_stripe(ctx: AuditContext, result: StageResult) -> None:
    if ctx.offline:
        result.evidence.append("Live probe skipped (offline mode)")
        return
    if not ctx.stripe_key:
        result.evidence.append("Stripe NOT TESTED — STRIPE_TEST_SECRET_KEY not provided")
        return
    ok, detail = probes.stripe_test_mode_check(ctx.stripe_key)
    (result.evidence if ok else result.missing).append(f"Stripe: {detail}")
    if not ok:
        result.status = Status.FAIL


def _probe_seo(ctx: AuditContext, result: StageResult) -> None:
    if ctx.offline:
        result.evidence.append("Live probe skipped (offline mode)")
        return
    page = probes.http_get(ctx.prod_url)
    if not page.ok:
        result.missing.append(f"LIVE: could not fetch {ctx.prod_url} for SEO audit")
        result.status = Status.FAIL
        return
    checks = probes.audit_seo_html(page.body)
    checks.update(probes.check_robots_and_sitemap(ctx.prod_url))
    passed = [k for k, v in checks.items() if v]
    failed = [k for k, v in checks.items() if not v]
    result.evidence.append(f"LIVE SEO passed ({len(passed)}/{len(checks)}): {', '.join(passed) or 'none'}")
    if failed:
        result.missing.append(f"LIVE SEO missing: {', '.join(failed)}")
        result.status = Status.FAIL if len(failed) > len(passed) else Status.PARTIAL


def _db_probe(tables: list[str], label: str) -> LiveProbe:
    def probe(ctx: AuditContext, result: StageResult) -> None:
        if ctx.offline or not ctx.database_url:
            result.evidence.append(f"{label} NOT TESTED — DATABASE_URL not provided")
            return
        counts = probes.database_counts(ctx.database_url, tables)
        if "_error" in counts:
            result.missing.append(f"DB: {counts['_error']}")
            return
        result.evidence.append(f"DB: {counts.pop('_tables_present', '?')} public tables")
        for table, value in counts.items():
            if value == "TABLE MISSING":
                result.status = Status.FAIL
                result.missing.append(f"DB: table `{table}` does not exist — {label} cannot persist")
            elif isinstance(value, int) and value == 0:
                result.missing.append(f"DB: table `{table}` exists but is EMPTY — nothing collected yet")
            else:
                result.evidence.append(f"DB: `{table}` rows={value}")

    return probe


# ---------------------------------------------------------------- test gate


_PUSH_RE = re.compile(r"git\s+push|gh\s+release|peter-evans/create-pull-request", re.IGNORECASE)
_TEST_RE = re.compile(r"^\s*(python\s+-m\s+)?pytest\b|npm\s+(run\s+)?test|jest\b", re.MULTILINE)


def _test_gate(ctx: AuditContext) -> StageResult:
    """Negative check: the pipeline must REFUSE to ship code that fails its tests.
    A pipeline that pushes before testing has no gate, however many tests exist."""
    result = StageResult(
        id="B4",
        name="Test gate — pipeline refuses to ship failing code",
        status=Status.PASS,
        summary="Tests must execute and must block the push step on failure.",
    )
    workflows: list[Path] = []
    for root in ctx.repos.values():
        if root.is_dir():
            workflows.extend(sorted((root / ".github" / "workflows").glob("*.yml")))

    if not workflows:
        result.status = Status.NOT_IMPLEMENTED
        result.missing.append("No GitHub Actions workflows found in either repo")
        return result

    gated, ungated = [], []
    for wf in workflows:
        text = wf.read_text(encoding="utf-8", errors="ignore")
        if not _PUSH_RE.search(text):
            continue  # workflow never ships anything
        push_at = _PUSH_RE.search(text).start()
        test_match = _TEST_RE.search(text)
        installs_pytest = re.search(r"pip install[^\n]*pytest", text) is not None
        if test_match and test_match.start() < push_at:
            gated.append(f"{wf.name}: test step precedes push")
        else:
            detail = "installs pytest but never runs it" if installs_pytest else "no test execution at all"
            ungated.append(f"{wf.name}: SHIPS WITHOUT TESTING — {detail}")

    result.evidence.extend(gated)
    result.missing.extend(ungated)
    if ungated:
        result.status = Status.FAIL
        result.summary = (
            f"{len(ungated)} shipping workflow(s) push generated code without running tests first. "
            "Any broken app the generator produces reaches production."
        )
    elif not gated:
        result.status = Status.NOT_IMPLEMENTED
        result.missing.append("No workflow both tests and ships — the loop has no gate")
    return result


# ---------------------------------------------------------------- scoring


SCORING_SPEC = (
    "score = 0.40*revenue + 0.30*engagement + 0.20*conversion + 0.10*retention (normalised)"
)


def _scoring(ctx: AuditContext) -> StageResult:
    """The 'best performing app' decision drives every iteration. If the maths is
    wrong or absent, the whole learning loop optimises against noise."""
    result = StageResult(
        id="B13",
        name="Performance scoring correctness",
        status=Status.NOT_IMPLEMENTED,
        summary=f"Expected model: {SCORING_SPEC}",
    )
    search = ctx.search(
        r"def\s+\w*(score|rank)\w*\s*\(",
        r"performance_score|composite_score|opportunity_score|best_performing",
        r"0\.4\d*\s*\*.*revenue",
    )
    result.status = search.status
    result.evidence = evidence_from(search)
    result.repos_found_in = search.repos_with_hits

    weight_hits = ctx.search(r"revenue_weight|engagement_weight|WEIGHTS\s*=", max_per_repo=5)
    if weight_hits.all_hits:
        result.evidence.append("Weight configuration found: " + weight_hits.all_hits[0].render())
    else:
        result.missing.append("No named weight constants — weights cannot be audited or tuned")

    edge_tests = ctx.search(
        r"(divide|zero_division|all_zero|single_app|empty).*(score|rank)",
        r"(score|rank).*(divide by zero|zero denominator)",
        max_per_repo=5,
    )
    if edge_tests.of_kind("test"):
        result.evidence.append("Edge-case tests present for scoring")
    else:
        result.missing.extend(
            [
                "No edge-case tests for scoring: all-zero metrics, single app, division by zero",
                "No monotonicity test: raising revenue must never lower the score",
                "No test asserting weights sum to 1.0",
                "No ranking-stability test across repeated runs",
            ]
        )
        if result.status is Status.IMPLEMENTED:
            result.status = Status.PARTIAL
    return result


def _learning_loop(ctx: AuditContext) -> StageResult:
    """The claim is that the system learns. Learning means parameters change in
    response to outcomes and accuracy improves on held-out data."""
    result = StageResult(
        id="B15",
        name="Learning loop — does it actually learn?",
        status=Status.NOT_IMPLEMENTED,
        summary="Model weights must update from observed outcomes and improve on a holdout set.",
    )
    search = ctx.search(
        r"def\s+\w*(train|fit|retrain|update_weights|backtest)\w*\s*\(",
        r"holdout|train_test_split|cross_val|backtest",
        r"model_version|weights_history|parameter_update",
    )
    result.status = search.status
    result.evidence = evidence_from(search)
    result.repos_found_in = search.repos_with_hits

    for requirement, patterns in {
        "Persisted model versions (so a change is observable)": [r"model_version|ModelVersion"],
        "Replay/backtest harness with a fixed seed": [r"backtest|replay.*seed|random_state\s*="],
        "Holdout accuracy metric recorded over time": [r"holdout|validation_score|accuracy_history"],
        "Feedback from build outcomes into recommendations": [
            r"feedback.*recommend|recommend.*outcome|outcome.*weight"
        ],
    }.items():
        found = ctx.search(*patterns, max_per_repo=3)
        if found.of_kind("code"):
            result.evidence.append(f"{requirement}: found")
        else:
            result.missing.append(f"{requirement}: NOT FOUND in either repo")
    return result


# ============================================================ PHASE C


def _canary(ctx: AuditContext) -> StageResult:
    """Walk the loop in order and report the first link that breaks. That link,
    not the longest list of gaps, is the real Baseline-0 blocker."""
    result = StageResult(
        id="C1",
        name="Canary trace — where the loop dies",
        status=Status.PASS,
        summary="A recommendation must survive all fifteen links to close the loop.",
    )
    ordered = [s for s in STAGES if s.phase == "B"]
    death_point = None
    for spec in ordered:
        path = ctx.output_dir / f"{spec.id}.json"
        if not path.is_file():
            result.evidence.append(f"{spec.id} {spec.name}: not run")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        status = Status(data["status"])
        marker = "  ↑ LOOP DIES HERE" if (death_point is None and status.is_blocking) else ""
        result.evidence.append(f"{status.icon} {spec.id} {spec.name}{marker}")
        if death_point is None and status.is_blocking:
            death_point = (spec, data)

    if death_point is None:
        result.summary = "All fifteen links reported non-blocking status."
        return result

    spec, data = death_point
    result.status = Status.FAIL
    result.summary = (
        f"The loop breaks at {spec.id} — {spec.name}. Everything downstream is untestable "
        f"until this is fixed, so later failures in this report may be symptoms, not causes."
    )
    result.missing = [f"{spec.id}: {m}" for m in data.get("missing", [])]
    return result


# ============================================================ REGISTRY


STAGES: list[StageSpec] = [
    StageSpec("A1", "Two-repo inventory", "A", _repo_inventory),
    StageSpec("A2", "Claim-vs-reality ledger", "A", _claim_ledger),
    StageSpec("A3", "Static health — placeholders and secrets", "A", _static_health),

    capability(
        "B1", "Recommendation surfacing", "B",
        [r"recommendation", r"def\s+\w*recommend\w*\s*\(", r"/api/.*recommend"],
        "The user can see a list of build recommendations.",
    ),
    capability(
        "B2", "Select-to-build trigger", "B",
        [r"(trigger|start|launch|dispatch).*build", r"build_request|BuildRequest|queue_build",
         r"workflow_dispatch.*build"],
        "Selecting a recommendation starts a build.",
    ),
    capability(
        "B3", "Build — code generation", "B",
        [r"anthropic|claude", r"generate_code|build_feature|code_generator"],
        "Causal Affect generates a working application from the recommendation.",
    ),
    StageSpec("B4", "Test gate — pipeline refuses to ship failing code", "B", _test_gate),
    capability(
        "B5", "Ship to GitHub", "B",
        [r"git\s+push", r"create_pull_request|GITHUB_TOKEN|CROSS_REPO_PAT"],
        "The generated app is committed and pushed to GitHub.",
    ),
    capability(
        "B6", "Railway deployment", "B",
        [r"railway", r"railway\.(json|toml)|nixpacks|Procfile"],
        "The pushed app is deployed to Railway and serves traffic.",
        live=_probe_deploy,
    ),
    capability(
        "B7", "GA4 wiring", "B",
        [r"gtag|google.?analytics|measurement_id|GA4"],
        "The deployed app reports engagement to GA4.",
        live=_probe_ga4,
    ),
    capability(
        "B8", "Stripe wiring", "B",
        [r"stripe", r"checkout\.session|webhook.*stripe|stripe.*webhook"],
        "The deployed app can take a subscription payment.",
        live=_probe_stripe,
    ),
    capability(
        "B9", "SEO optimisation", "B",
        [r"meta.*description|og:title|canonical|sitemap|structured.?data|json-ld"],
        "The deployed app is optimised for search.",
        live=_probe_seo,
    ),
    capability(
        "B10", "Engagement collection", "B",
        [r"engagement", r"ProductMetrics|product_metrics|analytics_event|track_event"],
        "Engagement data flows back from the deployed app into storage.",
        live=_db_probe(["product_metrics", "engagement_events", "analytics_events"], "Engagement storage"),
    ),
    capability(
        "B11", "Revenue attribution", "B",
        [r"revenue", r"subscription.*revenue|mrr|webhook.*invoice"],
        "Payments are attributed back to the app that earned them.",
        live=_db_probe(["subscriptions", "stripe_events", "revenue_events"], "Revenue storage"),
    ),
    capability(
        "B12", "Performance dashboard", "B",
        [r"dashboard.*performance|performance.*tab|PerformanceDashboard",
         r"/api/.*(performance|metrics)"],
        "The user can see how each deployed app is performing.",
    ),
    StageSpec("B13", "Performance scoring correctness", "B", _scoring),
    capability(
        "B14", "Iteration on the winner", "B",
        [r"parent_build_id|iteration_id|iterate.*build|build.*iteration",
         r"def\s+\w*iterat\w*\s*\("],
        "The best-performing app can be iterated, with lineage preserved.",
    ),
    StageSpec("B15", "Learning loop — does it actually learn?", "B", _learning_loop),

    StageSpec("C1", "Canary trace — where the loop dies", "C", _canary),
]

STAGES_BY_ID = {s.id: s for s in STAGES}

# Named slices of the loop, so a single subsystem can be audited on its own.
MODULES: dict[str, tuple[str, list[str]]] = {
    "everything": ("Full audit — all stages", [s.id for s in STAGES]),
    "discovery": ("Repo inventory, claim ledger, placeholder scan", ["A1", "A2", "A3"]),
    "recommendation-engine": ("Recommendations and select-to-build", ["B1", "B2"]),
    "build-pipeline": ("Generate, test-gate, ship, deploy", ["B3", "B4", "B5", "B6"]),
    "integrations": ("GA4, Stripe, SEO on the live site", ["B7", "B8", "B9"]),
    "measurement": ("Engagement, revenue, performance dashboard", ["B10", "B11", "B12"]),
    "learning": ("Scoring, iteration, ML feedback loop", ["B13", "B14", "B15"]),
    "canary": ("Trace the loop and find where it dies", ["C1"]),

    # One slice per Baseline-0 phase workflow, so a phase gates only on what it fixed.
    "phase-0": ("W0 preflight and anti-drift", ["A1", "A2", "A3"]),
    "phase-1": ("W1 test gate and verification", ["B3", "B4"]),
    "phase-2": ("W2 ship and deploy", ["B2", "B5", "B6"]),
    "phase-3": ("W3 GA4, Stripe and SEO wiring", ["B7", "B8", "B9"]),
    "phase-4": ("W4 telemetry and revenue attribution", ["B10", "B11"]),
    "phase-5": ("W5 performance dashboard and scoring", ["B12", "B13"]),
    "phase-6": ("W6 iteration lineage and the learning loop", ["B14", "B15"]),
}
