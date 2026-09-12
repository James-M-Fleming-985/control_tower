"""Run a Baseline-0 phase's specifications inside a fixed time budget.

Each phase workflow is meant to fit in an unattended 30-60 minute window. A hard
job timeout would kill the run mid-report and tell you nothing, so this stops
cleanly at the soft budget instead and records whatever is left as outstanding.

Usage:
    PYTHONPATH=scripts python -m b0.phase_runner \
        --phase W1 --specs-dir specs/baseline0 --target target_repo \
        --budget-minutes 40 --facts-out phase_facts.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml


def discover_specs(specs_dir: Path, phase: str) -> list[Path]:
    """Specs live in specs/baseline0/<PHASE>/FEATURE-*.yaml and run in filename order."""
    phase_dir = specs_dir / phase
    if not phase_dir.is_dir():
        return []
    return sorted(p for p in phase_dir.glob("FEATURE-*.yaml") if p.is_file())


def spec_meta(path: Path) -> tuple[str, str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return path.stem, ""
    meta = data.get("metadata", {}) if isinstance(data, dict) else {}
    return meta.get("requirement_id", path.stem), meta.get("requirement_name", "")


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 3600) -> tuple[int, str]:
    print(f"$ {' '.join(cmd)}", flush=True)
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
    )
    output = proc.stdout + proc.stderr
    print(output, flush=True)
    return proc.returncode, output


def count_retries(output: str) -> int:
    lowered = output.lower()
    return sum(lowered.count(token) for token in ("retry ", "retrying", "attempt "))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="b0.phase_runner", description=__doc__)
    p.add_argument("--phase", required=True, help="phase folder name, e.g. W1")
    p.add_argument("--specs-dir", default="specs/baseline0")
    p.add_argument("--target", default="target_repo", help="target repo checkout")
    p.add_argument("--control-tower", default=".")
    p.add_argument("--budget-minutes", type=float, default=40.0)
    p.add_argument("--facts-out", default="phase_facts.json")
    p.add_argument("--dry-run", action="store_true",
                   help="validate specs only — no AI generation, no code changes")
    args = p.parse_args(argv)

    control_tower = Path(args.control_tower).resolve()
    specs = discover_specs(Path(args.specs_dir).resolve(), args.phase)
    if not specs:
        print(f"::error title=No specs::nothing found for {args.phase} in {args.specs_dir}",
              file=sys.stderr)
        return 1

    started = time.monotonic()
    budget_s = args.budget_minutes * 60
    records: list[dict] = []
    outstanding: list[str] = []
    failures = 0

    for spec in specs:
        spec_id, spec_name = spec_meta(spec)
        elapsed = time.monotonic() - started

        if elapsed > budget_s:
            outstanding.append(f"{spec_id} — not started, {args.budget_minutes:.0f} min "
                               f"budget exhausted; re-dispatch this phase to continue")
            records.append({"id": spec_id, "name": spec_name, "status": "⏭️ skipped",
                            "path": str(spec), "ai_retries": 0})
            continue

        validate = [sys.executable, "validate_feature_yaml.py", str(spec.resolve())]
        if not args.dry_run:
            validate.append("--require-production-wiring")
        code, _ = run(validate, cwd=control_tower, timeout=120)
        if code != 0:
            failures += 1
            outstanding.append(f"{spec_id} — specification failed validation")
            records.append({"id": spec_id, "name": spec_name, "status": "❌ invalid spec",
                            "path": str(spec), "ai_retries": 0})
            continue

        if args.dry_run:
            records.append({"id": spec_id, "name": spec_name, "status": "✅ valid (dry run)",
                            "path": str(spec), "ai_retries": 0})
            continue

        remaining = max(60, int(budget_s - (time.monotonic() - started)))
        try:
            code, output = run(
                [sys.executable, "build_feature.py", str(spec.resolve()), "--verbose"],
                cwd=control_tower, timeout=remaining,
            )
        except subprocess.TimeoutExpired:
            code, output = 124, ""
            outstanding.append(f"{spec_id} — stopped at the time budget, partially built")

        retries = count_retries(output)
        if code == 0:
            records.append({"id": spec_id, "name": spec_name, "status": "✅ built",
                            "path": str(spec), "ai_retries": retries})
        else:
            failures += 1
            records.append({"id": spec_id, "name": spec_name, "status": "❌ build failed",
                            "path": str(spec), "ai_retries": retries})
            if code != 124:
                outstanding.append(f"{spec_id} — build failed, see the log")

    duration_min = round((time.monotonic() - started) / 60, 1)
    facts = {
        "phase": args.phase,
        "specs": records,
        "duration_min": duration_min,
        "budget_min": args.budget_minutes,
        "outstanding": outstanding,
        "outcome": "clean" if failures == 0 else f"{failures} specification(s) failed",
        "dry_run": args.dry_run,
    }
    Path(args.facts_out).write_text(json.dumps(facts, indent=2), encoding="utf-8")
    print(f"\nPhase {args.phase}: {len(records)} spec(s), {failures} failure(s), "
          f"{duration_min} min")

    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"failures={failures}\n")
            fh.write(f"duration_min={duration_min}\n")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
