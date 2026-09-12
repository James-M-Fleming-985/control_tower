"""Renders the audit results into BASELINE0_AUDIT_REPORT.md."""

from __future__ import annotations

from datetime import datetime, timezone

from .core import AuditContext, StageResult, Status

PHASE_TITLES = {
    "A": "Phase A — Discovery and claim verification",
    "B": "Phase B — The fifteen links of the autonomous loop",
    "C": "Phase C — Canary trace",
}

BASELINE0_DEFINITION = """\
A user reads recommendations, selects one, and Causal Affect builds it, tests it,
ships it to GitHub, deploys it to Railway, wires GA4 and Stripe, optimises it for
search, collects engagement and revenue, displays performance, lets the user iterate
the winner, and learns from the outcome so that the next recommendation, build and
iteration are measurably better."""


def build_report(ctx: AuditContext, results: list[StageResult]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    loop = [r for r in results if r.id.startswith("B")]
    done = [r for r in loop if r.status in (Status.IMPLEMENTED, Status.PASS)]
    percent = round(100 * len(done) / len(loop)) if loop else 0

    lines: list[str] = [
        "# Baseline-0 Audit Report",
        "",
        f"**Generated:** {now}  ",
        f"**Production target:** {ctx.prod_url}  ",
        f"**Repositories audited:** {', '.join(f'`{r}`' for r in ctx.repos)}",
        "",
        "## What Baseline 0 means",
        "",
        BASELINE0_DEFINITION,
        "",
        "## Headline",
        "",
        f"**{len(done)} of {len(loop)} links in the loop are working — {percent}% of Baseline 0.**",
        "",
    ]

    canary = next((r for r in results if r.id == "C1"), None)
    if canary and canary.status is Status.FAIL:
        lines += [f"> **The loop dies at the first broken link.** {canary.summary}", ""]

    if ctx.missing_repos:
        lines += [
            "> ⚠️ **Findings are unreliable.** These repositories were not available during the "
            f"audit: {', '.join(ctx.missing_repos)}. Any `NOT_IMPLEMENTED` result may simply mean "
            "the code lives in a repo that was never searched.",
            "",
        ]

    lines += ["## Scorecard", "", "| # | Link | Status | Found in | Summary |", "|---|---|---|---|---|"]
    for r in results:
        repos = ", ".join(r.repos_found_in) or "—"
        lines.append(
            f"| {r.id} | {r.name} | {r.status.icon} {r.status.value} | {repos} | {_oneline(r.summary)} |"
        )
    lines.append("")

    lines += ["## Critical path to Baseline 0", ""]
    blockers = [r for r in loop if r.status.is_blocking]
    if not blockers:
        lines.append("No blocking links. Remaining work is hardening, not enablement.")
    else:
        lines.append(
            "Fix in this order. Each item is a prerequisite for everything below it — "
            "fixing a later item first cannot be verified."
        )
        lines.append("")
        for n, r in enumerate(blockers, start=1):
            lines.append(f"{n}. **{r.id} {r.name}** — {_oneline(r.summary)}")
            shown = r.missing[:4]
            for gap in shown:
                lines.append(f"   - {gap}")
            if len(r.missing) > len(shown):
                lines.append(
                    f"   - _Showing {len(shown)} of {len(r.missing)} gaps — "
                    f"the full list is under {r.id} below._"
                )
    lines.append("")

    for phase, title in PHASE_TITLES.items():
        phase_results = [r for r in results if r.id.startswith(phase)]
        if not phase_results:
            continue
        lines += [f"## {title}", ""]
        for r in phase_results:
            lines += _stage_section(r)

    lines += [
        "## How to read this report",
        "",
        "| Status | Meaning |",
        "|---|---|",
        "| ✅ IMPLEMENTED / PASS | Code exists and is covered by tests, or a live probe succeeded |",
        "| 🟠 PARTIAL | Code exists but nothing tests it — it may or may not work |",
        "| 📄 DESIGN_ONLY | Only documents, plans or templates — nothing executable |",
        "| ❌ NOT_IMPLEMENTED / FAIL | Nothing found in either repo, or the live probe failed |",
        "| ⏭️ SKIPPED | Not testable — a credential or repository was unavailable |",
        "| 💥 ERROR | The probe itself crashed; treat as unknown, not as a pass |",
        "",
        "No fixes were applied by this audit. It is read-only diagnosis.",
    ]
    return "\n".join(lines)


def _stage_section(r: StageResult) -> list[str]:
    out = [
        f"### {r.status.icon} {r.id} — {r.name}",
        "",
        f"**Status:** {r.status.value} · **Duration:** {r.duration_s}s",
        "",
        r.summary,
        "",
    ]
    if r.evidence:
        out += ["**Evidence**", ""] + [f"- {e}" for e in r.evidence] + [""]
    if r.missing:
        out += ["**Gaps**", ""] + [f"- {m}" for m in r.missing] + [""]
    return out


def _oneline(text: str) -> str:
    return " ".join(text.split()).replace("|", "/")
