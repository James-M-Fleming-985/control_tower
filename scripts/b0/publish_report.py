"""Publish a phase/audit report in full, and prove nothing was truncated.

The problem this solves: the audit used to post only a short verdict to the tracking
issue and say "full detail is in the report below" — but nothing below was ever
posted. The full report went only to the step summary and a 30-day artifact, neither
of which is readable in the GitHub mobile app.

What this does instead:
  1. Posts a short verdict comment first, so the phone notification preview is useful.
  2. Publishes the complete report to a secret Gist (renders markdown on mobile, no
     length cap) and links it on line 2 of the verdict.
  3. Posts the complete report into the issue thread, split into labelled parts.
  4. Reads the comments and the gist BACK from GitHub, reassembles them, and fails
     the run if a single byte differs — a truncated report is an alert, never a
     quiet loss.

Limits this is designed against:
  - issue comment body: 65,536 characters (hard API limit)
  - GITHUB_STEP_SUMMARY: 1 MiB per step; over the limit the summary is DROPPED whole
  - the GitHub UI auto-collapses very long comments behind an expander
  - `gh issue comment --body "<huge>"` passes the body as a shell argument

Usage:
    PYTHONPATH=scripts python -m b0.publish_report \
        --repo owner/repo --issue 42 --report BASELINE0_AUDIT_REPORT.md \
        --headline "✅ W0 finished — nothing needs you" \
        --chunk-mode always
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COMMENT_LIMIT = 65_536
# Leaves ~10k of headroom for the part header and any GitHub-side escaping.
CHUNK_LIMIT = 55_000
STEP_SUMMARY_LIMIT = 1_000_000
MARKER = "b0-report"


class PublishError(RuntimeError):
    pass


def gh(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True, timeout=180,
    )
    if check and proc.returncode != 0:
        raise PublishError(f"gh {' '.join(args[:3])} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


# ---------------------------------------------------------------- chunking


def split_report(text: str, limit: int = CHUNK_LIMIT) -> list[str]:
    """Split on `## ` headings so each part starts at a readable boundary.

    A section larger than the limit is hard-split on line boundaries rather than
    dropped — losing content is the one outcome this module exists to prevent.
    """
    if len(text) <= limit:
        return [text]

    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## ") and current:
            blocks.append("".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append("".join(current))

    sized: list[str] = []
    for block in blocks:
        if len(block) <= limit:
            sized.append(block)
            continue
        buf: list[str] = []
        size = 0
        for line in block.splitlines(keepends=True):
            if size + len(line) > limit and buf:
                sized.append("".join(buf))
                buf, size = [], 0
            # A single line longer than the limit is split by raw character count.
            while len(line) > limit:
                sized.append(line[:limit])
                line = line[limit:]
            buf.append(line)
            size += len(line)
        if buf:
            sized.append("".join(buf))

    chunks: list[str] = []
    buf, size = [], 0
    for block in sized:
        if size + len(block) > limit and buf:
            chunks.append("".join(buf))
            buf, size = [], 0
        buf.append(block)
        size += len(block)
    if buf:
        chunks.append("".join(buf))
    return chunks


def part_header(index: int, total: int, run_id: str) -> str:
    return (
        f"<!-- {MARKER} part={index}/{total} run={run_id} -->\n"
        f"**Full report — part {index} of {total}**\n\n"
    )


def strip_header(body: str) -> str:
    """Recover the original chunk from a posted comment body."""
    lines = body.splitlines(keepends=True)
    if lines and lines[0].startswith(f"<!-- {MARKER} part="):
        # header is: marker line, bold label line, blank line
        return "".join(lines[3:])
    return body


# ---------------------------------------------------------------- publishing


def post_comment(repo: str, issue: str, body: str) -> None:
    """Always via --body-file: a long --body would hit the shell argument limit."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(body)
        path = fh.name
    try:
        gh("issue", "comment", issue, "--repo", repo, "--body-file", path)
    finally:
        os.unlink(path)


def create_gist(report: Path, name: str, description: str) -> tuple[str, str]:
    """Secret gist — unlisted URL, renders on mobile, no length cap."""
    tmpdir = Path(tempfile.mkdtemp())
    try:
        staged = tmpdir / name
        shutil.copyfile(report, staged)
        url = gh("gist", "create", str(staged), "--secret", "--desc", description)
        url = url.splitlines()[-1].strip()
        return url, url.rsplit("/", 1)[-1]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def fetch_posted_parts(repo: str, issue: str, run_id: str) -> str:
    """Read the parts back from GitHub and reassemble them."""
    raw = gh(
        "api", "--paginate",
        f"repos/{repo}/issues/{issue}/comments",
        "--jq", ".[] | {body: .body}",
    )
    bodies = [json.loads(line)["body"] for line in raw.splitlines() if line.strip()]
    mine = [b for b in bodies if f"<!-- {MARKER} part=" in b and f"run={run_id} " in b]

    def order(body: str) -> int:
        token = body.split("part=", 1)[1].split("/", 1)[0]
        return int(token)

    return "".join(strip_header(b) for b in sorted(mine, key=order))


def fetch_gist(gist_id: str, name: str) -> str:
    return gh("gist", "view", gist_id, "--filename", name, "--raw")


def write_step_summary(report: str, gist_url: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    # Over the 1 MiB cap GitHub drops the summary entirely, so link out instead.
    body = report if len(report) < STEP_SUMMARY_LIMIT else (
        f"Report is {len(report):,} characters — too large for the run summary.\n\n"
        f"Full report: {gist_url}\n"
    )
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(body + "\n")


def set_output(**values: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        for key, value in values.items():
            fh.write(f"{key}={value}\n")


# ---------------------------------------------------------------- entry point


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="b0.publish_report", description=__doc__)
    p.add_argument("--report", required=True, help="markdown report to publish in full")
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    p.add_argument("--issue", help="tracking issue number (omit to publish gist only)")
    p.add_argument("--headline", default="Run finished",
                   help="first line of the verdict — becomes the phone notification preview")
    p.add_argument("--verdict", help="file with the verdict body to post above the report")
    p.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "local"))
    p.add_argument("--run-url", default="")
    p.add_argument("--gist-name", default="report.md")
    p.add_argument("--chunk-mode", choices=["always", "on-failure", "never"], default="always",
                   help="when to post the full report into the issue thread")
    p.add_argument("--failed", action="store_true", help="this run found problems")
    p.add_argument("--no-verify", action="store_true",
                   help="skip the read-back check (testing only)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report_path = Path(args.report)
    if not report_path.is_file():
        print(f"::error title=No report::{report_path} does not exist", file=sys.stderr)
        return 1

    report = report_path.read_text(encoding="utf-8")
    print(f"Report is {len(report):,} characters")

    try:
        gist_url, gist_id = create_gist(
            report_path, args.gist_name,
            f"{args.headline} (run {args.run_id})",
        )
        print(f"Gist: {gist_url}")
    except PublishError as exc:
        print(f"::warning title=Gist failed::{exc}", file=sys.stderr)
        gist_url, gist_id = "", ""

    chunks = split_report(report)
    should_chunk = args.chunk_mode == "always" or (
        args.chunk_mode == "on-failure" and args.failed
    )

    if not args.issue:
        write_step_summary(report, gist_url)
        set_output(gist_url=gist_url, parts="0", verified="skipped")
        print("No issue number given — published to gist and step summary only")
        return 0

    verdict_body = Path(args.verdict).read_text(encoding="utf-8") if args.verdict else ""
    header = [f"## {args.headline}", ""]
    if gist_url:
        header.append(f"📄 **[Read the full report]({gist_url})** — complete, nothing trimmed.")
    if should_chunk:
        header.append(
            f"It is also posted in full below in {len(chunks)} "
            f"part{'s' if len(chunks) != 1 else ''}."
        )
    else:
        header.append("Use the link above for the detail — this run had nothing broken to list.")
    if args.run_url:
        header.append(f"\n[Open the run log]({args.run_url})")
    if verdict_body:
        header += ["", "---", "", verdict_body]

    post_comment(args.repo, args.issue, "\n".join(header))

    posted = 0
    if should_chunk:
        for index, chunk in enumerate(chunks, start=1):
            body = part_header(index, len(chunks), args.run_id) + chunk
            if len(body) > COMMENT_LIMIT:
                print(f"::error title=Chunk too large::part {index} is {len(body)} chars",
                      file=sys.stderr)
                return 1
            post_comment(args.repo, args.issue, body)
            posted += 1
        print(f"Posted {posted} report part(s) to issue #{args.issue}")

    write_step_summary(report, gist_url)

    if args.no_verify:
        set_output(gist_url=gist_url, parts=str(posted), verified="skipped")
        return 0

    problems: list[str] = []
    if should_chunk:
        reassembled = fetch_posted_parts(args.repo, args.issue, args.run_id)
        if reassembled != report:
            problems.append(
                f"issue thread holds {len(reassembled):,} of {len(report):,} characters"
            )
    if gist_id:
        try:
            if fetch_gist(gist_id, args.gist_name) != report:
                problems.append("gist content does not match the generated report")
        except PublishError as exc:
            problems.append(f"could not read the gist back: {exc}")

    if problems:
        detail = "; ".join(problems)
        print(f"::error title=Report truncated::{detail}", file=sys.stderr)
        post_comment(
            args.repo, args.issue,
            "## ⚠️ Needs you — the report did not publish in full\n\n"
            f"{detail}.\n\nThe run itself is unaffected, but do not trust the report "
            "above as complete. The artifact on the run page is the authoritative copy.",
        )
        set_output(gist_url=gist_url, parts=str(posted), verified="false")
        return 1

    print("Verified: published report matches the generated report byte for byte")
    set_output(gist_url=gist_url, parts=str(posted), verified="true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
