"""CLI entry point for the Baseline-0 audit. Run from the control_tower root:

    PYTHONPATH=scripts python -m baseline0_audit --list
    PYTHONPATH=scripts python -m baseline0_audit --module recommendation-engine
    PYTHONPATH=scripts python -m baseline0_audit --stage B4 --offline
    PYTHONPATH=scripts python -m baseline0_audit --phase A
    PYTHONPATH=scripts python -m baseline0_audit --issue 42
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .core import AuditContext, Status, run_stage
from .report import build_report
from .stages import MODULES, STAGES, STAGES_BY_ID

DEFAULT_PROD_URL = "https://businessventures-production.up.railway.app"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="baseline0_audit", description=__doc__)
    p.add_argument("--control-tower", default=".", help="path to the control_tower checkout")
    p.add_argument("--business-ventures", default="../business_ventures",
                   help="path to the business_ventures checkout")
    p.add_argument("--output", default="audit_results", help="directory for per-stage JSON results")
    p.add_argument("--report", default="BASELINE0_AUDIT_REPORT.md", help="markdown report path")
    p.add_argument("--prod-url", default=os.environ.get("PROD_URL", DEFAULT_PROD_URL))
    p.add_argument("--module", action="append", choices=sorted(MODULES),
                   help="run a named subsystem, e.g. recommendation-engine")
    p.add_argument("--phase", action="append", choices=["A", "B", "C"], help="run only these phases")
    p.add_argument("--stage", action="append", help="run only these stage ids (e.g. B4)")
    p.add_argument("--offline", action="store_true", help="skip all live network and database probes")
    p.add_argument("--issue", help="GitHub issue number to post progress to")
    p.add_argument("--every-stage", action="store_true",
                   help="comment after every stage instead of only on problems and completion")
    p.add_argument("--label", help="human-readable name for this run, used in notifications")
    p.add_argument("--gate", action="store_true",
                   help="exit non-zero if any selected link is broken (for phase workflows; "
                        "the diagnostic workflow leaves this off so blockers stay a finding)")
    p.add_argument("--verdict-out", help="write the plain-English verdict to this file")
    p.add_argument("--no-verdict-comment", action="store_true",
                   help="do not post the verdict directly; b0.publish_report posts it "
                        "alongside the full report instead")
    p.add_argument("--list", action="store_true", help="list modules and stages, then exit")
    return p.parse_args(argv)


def select_stages(args: argparse.Namespace):
    if args.stage:
        unknown = [s for s in args.stage if s not in STAGES_BY_ID]
        if unknown:
            sys.exit(f"Unknown stage id(s): {', '.join(unknown)}")
        return [STAGES_BY_ID[s] for s in args.stage]
    if args.module:
        wanted = {sid for m in args.module for sid in MODULES[m][1]}
        return [s for s in STAGES if s.id in wanted]
    if args.phase:
        return [s for s in STAGES if s.phase in args.phase]
    return list(STAGES)


def verdict(label: str, results: list) -> str:
    """The first line becomes the phone notification preview, so it must say
    plainly whether the run needs the user or not."""
    broken = [r for r in results if r.status.is_blocking]
    crashed = [r for r in results if r.status is Status.ERROR]

    if crashed:
        headline = f"⚠️ {label} finished — {len(crashed)} check(s) crashed, worth a look"
    elif broken:
        headline = f"🔴 {label} finished — {len(broken)} thing(s) broken, needs fixing"
    else:
        headline = f"✅ {label} finished — nothing broken, nothing needs you"

    lines = [f"## {headline}", "", f"{len(results) - len(broken)} of {len(results)} checks passed."]
    if broken:
        lines += ["", "**What's broken:**", ""]
        lines += [f"- {r.status.icon} {r.name} — {' '.join(r.summary.split())}" for r in broken]
    return "\n".join(lines)


def notify(issue: str | None, body: str) -> None:
    """Progress goes to a GitHub issue so it reaches the GitHub mobile app.

    Always --body-file: a long --body is passed as a shell argument and would be
    rejected or silently mangled once the report grows.
    """
    if not issue:
        return
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(body)
        path = fh.name
    try:
        subprocess.run(
            ["gh", "issue", "comment", issue, "--body-file", path],
            check=True, capture_output=True, timeout=60,
        )
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        print(f"[notify] could not post to issue {issue}: {exc}", file=sys.stderr)
    finally:
        os.unlink(path)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.list:
        print("MODULES")
        for name, (desc, ids) in MODULES.items():
            print(f"  {name:<22} {desc}  [{', '.join(ids)}]")
        print("\nSTAGES")
        for spec in STAGES:
            print(f"  {spec.phase}  {spec.id:<4} {spec.name}")
        return 0

    ctx = AuditContext(
        repos={
            "control_tower": Path(args.control_tower).resolve(),
            "business_ventures": Path(args.business_ventures).resolve(),
        },
        output_dir=Path(args.output).resolve(),
        prod_url=args.prod_url.rstrip("/"),
        database_url=os.environ.get("DATABASE_URL"),
        stripe_key=os.environ.get("STRIPE_TEST_SECRET_KEY"),
        ga4_property_id=os.environ.get("GA4_PROPERTY_ID"),
        ga4_credentials=os.environ.get("GA4_CREDENTIALS_JSON"),
        offline=args.offline,
    )

    if ctx.missing_repos:
        print(f"WARNING: repos not found: {', '.join(ctx.missing_repos)} — "
              f"absence findings will be marked unreliable", file=sys.stderr)

    selected = select_stages(args)
    label = args.label or (", ".join(args.module) if args.module else "Baseline-0 audit")
    notify(args.issue, f"**{label}** started — {len(selected)} check(s) running.\n\n"
                       f"You'll get one more message when it finishes.")

    results = []
    for spec in selected:
        print(f"→ {spec.id} {spec.name}", flush=True)
        result = run_stage(spec, ctx)
        results.append(result)
        print(f"  {result.status.icon} {result.status.value} ({result.duration_s}s)", flush=True)
        # Quiet by default: an overnight run must not buzz the phone once per stage.
        if args.every_stage:
            notify(args.issue, f"{result.status.icon} **{result.id} {result.name}** — "
                               f"`{result.status.value}`\n\n{result.summary}")
        elif result.status is Status.ERROR:
            notify(args.issue, f"⚠️ **Needs you** — the check *{result.name}* crashed, "
                               f"so the audit can't judge it.\n\n{result.summary}")

    report_path = Path(args.report).resolve()
    report_path.write_text(build_report(ctx, results), encoding="utf-8")
    print(f"\nReport written to {report_path}")

    summary = verdict(label, results)
    if args.verdict_out:
        Path(args.verdict_out).resolve().write_text(summary, encoding="utf-8")
    if not args.no_verdict_comment:
        notify(args.issue, summary)

    broken = [r for r in results if r.status.is_blocking]
    if args.gate and broken:
        names = ", ".join(r.id for r in broken)
        print(f"::error title=Gate failed::broken link(s): {names}", file=sys.stderr)
        return 2

    # Blockers are the expected deliverable, not a build failure.
    return 0 if not any(r.status is Status.ERROR for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
