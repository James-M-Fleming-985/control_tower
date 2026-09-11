"""Core types and shared machinery for the Baseline-0 audit.

Every capability check searches BOTH repos (control_tower + business_ventures)
before recording an absence, because a finding from one repo alone proves nothing.
"""

from __future__ import annotations

import json
import os
import re
import time
import traceback
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Sequence


class Status(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    PARTIAL = "PARTIAL"
    DESIGN_ONLY = "DESIGN_ONLY"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

    @property
    def icon(self) -> str:
        return {
            Status.IMPLEMENTED: "✅",
            Status.PASS: "✅",
            Status.PARTIAL: "🟠",
            Status.DESIGN_ONLY: "📄",
            Status.NOT_IMPLEMENTED: "❌",
            Status.FAIL: "❌",
            Status.SKIPPED: "⏭️",
            Status.ERROR: "💥",
        }[self]

    @property
    def is_blocking(self) -> bool:
        return self in (Status.NOT_IMPLEMENTED, Status.FAIL, Status.ERROR)


EXCLUDE_DIRS = {
    ".git", ".github/workflows/cache", "node_modules", "__pycache__", ".venv", "venv",
    "env", "dist", "build", ".pytest_cache", ".mypy_cache", "site-packages",
    ".next", "coverage", "htmlcov", ".ruff_cache", "vendor", ".cache",
}

CODE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".sql", ".go", ".rb", ".java"}
DOC_EXT = {".md", ".yaml", ".yml", ".txt", ".rst", ".json", ".toml", ".cfg", ".ini"}
TEMPLATE_EXT = {".jinja", ".jinja2", ".j2", ".tpl"}


@dataclass
class Hit:
    repo: str
    path: str
    line_no: int
    line: str
    kind: str  # code | test | doc | template

    def render(self) -> str:
        return f"`{self.repo}` {self.path}:{self.line_no} — {self.line.strip()[:120]}"


@dataclass
class SearchResult:
    """Hits grouped by repo, with convenience rollups."""
    patterns: list[str]
    by_repo: dict[str, list[Hit]] = field(default_factory=dict)

    @property
    def all_hits(self) -> list[Hit]:
        return [h for hits in self.by_repo.values() for h in hits]

    @property
    def repos_with_hits(self) -> list[str]:
        return [r for r, hits in self.by_repo.items() if hits]

    def of_kind(self, *kinds: str) -> list[Hit]:
        return [h for h in self.all_hits if h.kind in kinds]

    @property
    def status(self) -> Status:
        """Objective rating rule: code+tests = implemented, code only = partial,
        docs/templates only = design-only, nothing = not implemented."""
        has_code = bool(self.of_kind("code"))
        has_tests = bool(self.of_kind("test"))
        has_paper = bool(self.of_kind("doc", "template"))
        if has_code and has_tests:
            return Status.IMPLEMENTED
        if has_code:
            return Status.PARTIAL
        if has_paper:
            return Status.DESIGN_ONLY
        return Status.NOT_IMPLEMENTED


@dataclass
class StageResult:
    id: str
    name: str
    status: Status
    summary: str
    evidence: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    repos_found_in: list[str] = field(default_factory=list)
    duration_s: float = 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class AuditContext:
    repos: dict[str, Path]
    output_dir: Path
    prod_url: str
    database_url: str | None = None
    stripe_key: str | None = None
    ga4_property_id: str | None = None
    ga4_credentials: str | None = None
    offline: bool = False

    def repo_available(self, name: str) -> bool:
        return name in self.repos and self.repos[name].is_dir()

    @property
    def missing_repos(self) -> list[str]:
        return [n for n, p in self.repos.items() if not p.is_dir()]

    def search(
        self,
        *patterns: str,
        extensions: Iterable[str] | None = None,
        max_per_repo: int = 20,
        ignore_case: bool = True,
    ) -> SearchResult:
        """Search every configured repo for any of the given regex patterns."""
        flags = re.IGNORECASE if ignore_case else 0
        compiled = [re.compile(p, flags) for p in patterns]
        ext_filter = set(extensions) if extensions else None
        result = SearchResult(patterns=list(patterns))

        for repo_name, root in self.repos.items():
            hits: list[Hit] = []
            if not root.is_dir():
                result.by_repo[repo_name] = hits
                continue
            for file_path in _walk_files(root, ext_filter):
                if len(hits) >= max_per_repo:
                    break
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    if any(c.search(line) for c in compiled):
                        hits.append(
                            Hit(
                                repo=repo_name,
                                path=str(file_path.relative_to(root)),
                                line_no=line_no,
                                line=line,
                                kind=classify_file(file_path),
                            )
                        )
                        break  # one hit per file keeps evidence readable
            result.by_repo[repo_name] = hits
        return result

    def find_files(self, *name_patterns: str) -> list[Hit]:
        """Locate files whose path matches any pattern, across both repos."""
        compiled = [re.compile(p, re.IGNORECASE) for p in name_patterns]
        found: list[Hit] = []
        for repo_name, root in self.repos.items():
            if not root.is_dir():
                continue
            for file_path in _walk_files(root, None):
                rel = str(file_path.relative_to(root))
                if any(c.search(rel) for c in compiled):
                    found.append(
                        Hit(repo=repo_name, path=rel, line_no=0, line="", kind=classify_file(file_path))
                    )
        return found


def _walk_files(root: Path, ext_filter: set[str] | None):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".git")]
        for name in filenames:
            path = Path(dirpath) / name
            suffix = path.suffix.lower()
            if ext_filter is not None and suffix not in ext_filter:
                continue
            if ext_filter is None and suffix not in (CODE_EXT | DOC_EXT | TEMPLATE_EXT):
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            yield path


def classify_file(path: Path) -> str:
    rel = str(path).replace(os.sep, "/").lower()
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in TEMPLATE_EXT or ".jinja" in name:
        return "template"
    if suffix in DOC_EXT:
        return "doc"
    is_test = (
        "/tests/" in rel
        or "/test/" in rel
        or name.startswith("test_")
        or name.endswith(("_test.py", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js"))
    )
    return "test" if is_test else "code"


Stage = Callable[[AuditContext], StageResult]


@dataclass
class StageSpec:
    id: str
    name: str
    phase: str
    run: Stage


def run_stage(spec: StageSpec, ctx: AuditContext) -> StageResult:
    started = time.monotonic()
    try:
        result = spec.run(ctx)
    except Exception as exc:  # a crashed probe must not abort the overnight run
        result = StageResult(
            id=spec.id,
            name=spec.name,
            status=Status.ERROR,
            summary=f"Probe raised {type(exc).__name__}: {exc}",
            evidence=[traceback.format_exc(limit=3)],
        )
    result.duration_s = round(time.monotonic() - started, 2)
    _persist(ctx, result)
    return result


def _persist(ctx: AuditContext, result: StageResult) -> None:
    ctx.output_dir.mkdir(parents=True, exist_ok=True)
    path = ctx.output_dir / f"{result.id}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")


def evidence_from(search: SearchResult, limit: int = 6) -> list[str]:
    lines = [h.render() for h in search.all_hits[:limit]]
    empty = [r for r, hits in search.by_repo.items() if not hits]
    if empty:
        lines.append(f"No match in: {', '.join(empty)}")
    return lines
