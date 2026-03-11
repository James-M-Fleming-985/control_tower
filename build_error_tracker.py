"""
Build Error Tracker — M0 Baseline Metrics Collection

Tracks build outcomes from build_feature.py runs.
Stores metrics as JSON (M0 — upgrade to database in M1).
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

METRICS_FILE = Path(__file__).parent / "build_metrics_history.json"


@dataclass
class BuildError:
    """A single error encountered during a build."""
    category: str       # syntax, test, frontend, import, wiring, config, runtime
    message: str
    file: Optional[str] = None
    line: Optional[int] = None


@dataclass
class BuildMetrics:
    """Metrics for a single build_feature.py run."""
    build_id: str = ""
    feature_name: str = ""
    timestamp: str = ""
    success: bool = False
    duration_seconds: float = 0.0

    # Error counts by category
    syntax_errors: int = 0
    test_failures: int = 0
    frontend_build_failures: int = 0
    import_errors: int = 0
    wiring_errors: int = 0
    config_errors: int = 0
    runtime_errors: int = 0

    # Detailed error list
    errors: List[Dict] = field(default_factory=list)

    # Computed
    total_errors: int = 0
    error_rate: float = 0.0

    def log_error(self, category: str, message: str,
                  file: Optional[str] = None, line: Optional[int] = None):
        """Record a build error."""
        err = BuildError(category=category, message=message, file=file, line=line)
        self.errors.append(asdict(err))

        # Increment category counter
        counter_map = {
            "syntax": "syntax_errors",
            "test": "test_failures",
            "frontend": "frontend_build_failures",
            "import": "import_errors",
            "wiring": "wiring_errors",
            "config": "config_errors",
            "runtime": "runtime_errors",
        }
        attr = counter_map.get(category, "runtime_errors")
        setattr(self, attr, getattr(self, attr) + 1)
        self.total_errors = sum(
            getattr(self, a) for a in counter_map.values()
        )

    def finalise(self, success: bool, duration_seconds: float = 0.0):
        """Mark the build complete and compute final metrics."""
        self.success = success
        self.duration_seconds = duration_seconds
        self.error_rate = 0.0 if self.total_errors == 0 else 100.0

    def save(self):
        """Append this build's metrics to the JSON history file."""
        history = _load_history()
        history.append(asdict(self))
        with open(METRICS_FILE, "w") as f:
            json.dump(history, f, indent=2, default=str)


def start_build(feature_name: str) -> BuildMetrics:
    """Create a new BuildMetrics instance for a build run."""
    return BuildMetrics(
        build_id=f"build-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        feature_name=feature_name,
        timestamp=datetime.utcnow().isoformat(),
    )


def _load_history() -> List[Dict]:
    """Load existing metrics history from JSON file."""
    if not METRICS_FILE.exists():
        return []
    try:
        with open(METRICS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def get_metrics_summary() -> Dict:
    """Return aggregate metrics for the Programme Baselines dashboard."""
    history = _load_history()
    if not history:
        return {
            "total_builds": 0,
            "successful_builds": 0,
            "failed_builds": 0,
            "error_rate_pct": 0.0,
            "avg_duration_seconds": 0.0,
            "error_breakdown": {
                "syntax": 0, "test": 0, "frontend": 0,
                "import": 0, "wiring": 0, "config": 0, "runtime": 0,
            },
            "trend": [],
        }

    total = len(history)
    successes = sum(1 for b in history if b.get("success"))
    failures = total - successes
    error_rate = (failures / total * 100) if total else 0.0
    avg_duration = (
        sum(b.get("duration_seconds", 0) for b in history) / total
        if total else 0.0
    )

    # Aggregate error counts
    breakdown = {
        "syntax": sum(b.get("syntax_errors", 0) for b in history),
        "test": sum(b.get("test_failures", 0) for b in history),
        "frontend": sum(b.get("frontend_build_failures", 0) for b in history),
        "import": sum(b.get("import_errors", 0) for b in history),
        "wiring": sum(b.get("wiring_errors", 0) for b in history),
        "config": sum(b.get("config_errors", 0) for b in history),
        "runtime": sum(b.get("runtime_errors", 0) for b in history),
    }

    # Trend: last 20 builds, chronologically
    trend = [
        {
            "build_id": b.get("build_id", ""),
            "timestamp": b.get("timestamp", ""),
            "success": b.get("success", False),
            "total_errors": b.get("total_errors", 0),
            "error_rate": 0.0 if b.get("success") else 100.0,
        }
        for b in history[-20:]
    ]

    return {
        "total_builds": total,
        "successful_builds": successes,
        "failed_builds": failures,
        "error_rate_pct": round(error_rate, 1),
        "avg_duration_seconds": round(avg_duration, 1),
        "error_breakdown": breakdown,
        "trend": trend,
    }
