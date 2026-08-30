"""Baseline tracking and regression detection infrastructure."""

import json
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc  # type: ignore


class BaselineTracker:
    """Baseline tracking for regression detection."""

    REGRESSION_THRESHOLD = -0.1
   
    def __init__(self, baseline_file: str | Path = "baseline.json") -> None:
        """Initialize baseline tracker.
        
        Args:
            baseline_file: Path to baseline.json (git-versioned)
        """
        self.baseline_file = Path(baseline_file)
        self._baseline = self._load_baseline()
    
    def _load_baseline(self) -> dict:
        """Load baseline.json or return empty dict if missing."""
        if not self.baseline_file.exists():
            return {}
        try:
            with open(self.baseline_file) as f:
                return json.load(f)
        except json.JSONDeCOdeError:
            return {}
   
    def compare(
        self,
        current_scores: dict[str, dict[str, float]],
    ) -> tuple[dict[str, dict[str, float]], list[str], bool]:
        """Compare current scores against baseline.
        
        Args:
            current_scores: {test_name: {assertion_type: score}}
            
        Returns:
            (baseline_delta, regressed_tests, regression_detected)
            - baseline_delta: {test: {assertion: delta}}
            - regressed_tests: list of test names with delta < -0.1
            - regression_detected: True if any regression found
        """
        baseline_delta: dict[str, dict[str, float]] = {}
        regressed_tests: set[str] = set()
        regression_detected = False

        for test_name, assertions in current_scores.items():
            baseline_delta[test_name] = {}
            for assertion_type, current_score in assertions.items():
                prior_score = None
                if (
                    test_name in self._baseline
                    and assertion_type in self._baseline[test_name]
                ):
                    prior_score = self._baseline[test_name][assertion_type].get(
                        "score"
                    )

                if prior_score is not None:
                    delta = current_score - prior_score
                    baseline_delta[test_name][assertion_type] = delta
                    if delta < self.REGRESSION_THRESHOLD:
                        regressed_tests.add(test_name)
                        regression_detected = True
                else:
                    baseline_delta[test_name][assertion_type] = 0.0

        return (
            baseline_delta,
            sorted(regressed_tests),
            regression_detected,
        )

    def update(self, current_scores: dict[str, dict[str, float]]) -> None:
        """Update baseline.json with new scores.
        
        Appends scores with timestamp and git commit SHA.
        
        Args:
            current_scores: {test_name: {assertion_type: score}}
        """
        commit_sha = self._get_current_commit()
        timestamp = datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")

        for test_name, assertions in current_scores.items():
            if test_name not in self._baseline:
                self._baseline[test_name] = {}
            for assertion_type, score in assertions.items():
                self._baseline[test_name][assertion_type] = {
                    "score": float(score),
                    "timestamp": timestamp,
                    "commit": commit_sha,
                }

        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_file, "w") as f:
            json.dump(self._baseline, f, indent=2)

    @staticmethod
    def _get_current_commit() -> str:
        """Get current git commit SHA."""
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"