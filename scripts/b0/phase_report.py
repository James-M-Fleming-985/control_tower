"""Render the "what was done" section that heads every phase report.

The audit report answers "what is broken". This answers "what did this run change",
which is the half you cannot reconstruct afterwards from the repo alone.

Facts are supplied by the workflow as JSON; git history is read directly from the
target checkout so the file list and SHAs cannot drift from reality.

Usage:
    PYTHONPATH=scripts python -m b0.phase_report \
        --phase W1 --title "Test Gate & Verification" \
        --repo-path target_repo --base-sha "$BASE" --head-sha "$HEAD" \
        --facts phase_facts.json --out PHASE_REPORT.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=120,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def changed_files(repo: Path, base: str, head: str) -> list[str]:
    out = git(repo, "diff", "--numstat", f"{base}..{head}")
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            added, removed, path = parts
            rows.append(f"| `{path}` | +{added} | −{removed} |")
    return rows


def commits(repo: Path, base: str, head: str) -> list[str]:
    out = git(repo, "log", "--no-merges", "--format=%h %s", f"{base}..{head}")
    return [f"- `{line.split(' ', 1)[0]}` {line.split(' ', 1)[1]}"
            for line in out.splitlines() if " " in line]


def _table(header: str, rows: list[str], empty: str) -> list[str]:
    if not rows:
        return [empty, ""]
    return [header, *rows, ""]


def build(args: argparse.Namespace) -> str:
    facts = json.loads(Path(args.facts).read_text(encoding="utf-8")) if args.facts else {}
    repo = Path(args.repo_path)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# {args.phase} — {args.title}",
        "",
        f"**Finished:** {now}  ",
        f"**Outcome:** {facts.get('outcome', 'unknown')}  ",
        f"**Duration:** {facts.get('duration_min', '?')} min of a "
        f"{facts.get('budget_min', '?')} min budget",
        "",
        "## What this run did",
        "",
    ]

    specs = facts.get("specs", [])
    if specs:
        lines += ["**Specifications executed**", ""]
        for spec in specs:
            status = spec.get("status", "?")
            retries = spec.get("ai_retries", 0)
            lines.append(f"- {status} `{spec.get('id', spec.get('path', '?'))}` — "
                         f"{spec.get('name', '')} ({retries} AI retr"
                         f"{'y' if retries == 1 else 'ies'})")
        lines.append("")

    lines += ["### Code changed", ""]
    if args.base_sha and args.head_sha and repo.is_dir():
        rows = changed_files(repo, args.base_sha, args.head_sha)
        lines += _table("| File | Added | Removed |\n|---|---|---|", rows,
                        "_No files changed._")
        log = commits(repo, args.base_sha, args.head_sha)
        if log:
            lines += ["**Commits**", "", *log, ""]
        lines += [f"**Range:** `{args.base_sha[:8]}..{args.head_sha[:8]}`", ""]
    else:
        lines += ["_No diff range supplied._", ""]

    tests = facts.get("tests", {})
    lines += ["### Tests", ""]
    if tests:
        lines += [
            f"- Ran **{tests.get('run', '?')}**, passed **{tests.get('passed', '?')}**, "
            f"failed **{tests.get('failed', '?')}**",
        ]
        for name in tests.get("failures", []):
            lines.append(f"  - ❌ `{name}`")
        lines.append("")
    else:
        lines += ["_No test results recorded._", ""]

    gate = facts.get("gate", [])
    lines += ["### Baseline-0 links", ""]
    rows = [f"| {g.get('link')} | {g.get('name', '')} | {g.get('before', '?')} | "
            f"{g.get('after', '?')} | {g.get('verdict', '')} |" for g in gate]
    lines += _table(
        "| Link | Name | Before | After | Gate |\n|---|---|---|---|---|",
        rows, "_No links were gated in this phase._",
    )

    lines += ["### Shipping", ""]
    merge = facts.get("merge", {})
    deploy = facts.get("deploy", {})
    lines += [
        f"- **Merge:** {merge.get('decision', 'not attempted')}"
        + (f" (`{merge['sha'][:8]}`)" if merge.get("sha") else ""),
        f"- **Pre-merge SHA (rollback point):** `{merge.get('base_sha', '—')[:8]}`",
        f"- **Deploy:** {deploy.get('status', 'not attempted')}",
        f"- **Health probe:** {deploy.get('health', 'not run')}",
        f"- **Rollback:** {facts.get('rollback', 'not triggered')}",
        "",
    ]

    cost = facts.get("cost", {})
    if cost:
        lines += [
            "### Cost",
            "",
            f"- Tokens: {cost.get('tokens', '?')}  ",
            f"- Estimated spend: {cost.get('estimate', '?')}",
            "",
        ]

    outstanding = facts.get("outstanding", [])
    lines += ["### Still outstanding after this phase", ""]
    if outstanding:
        lines += [f"- {item}" for item in outstanding] + [""]
    else:
        lines += ["Nothing — this phase completed everything in its scope.", ""]

    if facts.get("next"):
        lines += [f"**Next:** {facts['next']}", ""]

    lines += ["---", ""]
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="b0.phase_report", description=__doc__)
    p.add_argument("--phase", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--repo-path", default="target_repo")
    p.add_argument("--base-sha", default="")
    p.add_argument("--head-sha", default="")
    p.add_argument("--facts", help="JSON file of run facts")
    p.add_argument("--out", required=True)
    p.add_argument("--append", help="append this report after the generated section")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    text = build(args)
    if args.append and Path(args.append).is_file():
        text += Path(args.append).read_text(encoding="utf-8")
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"Phase report written to {args.out} ({len(text):,} characters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
