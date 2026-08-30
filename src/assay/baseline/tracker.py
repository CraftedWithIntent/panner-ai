import json
import subprocess
from pathlib import Path
from datetime import datetime

class BaselineTracker:
    REGRESSION_THRESHOLD = -0.1
    
    def __init__(self, baseline_file="baseline.json"):
        self.baseline_file = Path(baseline_file)
        self._baseline = self._load_baseline()
    
    def _load_baseline(self):
        if not self.baseline_file.exists():
            return {}
        try:
            with open(self.baseline_file) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def compare(self, current_scores):
        baseline_delta = {}
        regressed_tests = set()
        regression_detected = False
        
        for test_name, assertions in current_scores.items():
            baseline_delta[test_name] = {}
            for assertion_type, current_score in assertions.items():
                prior_score = None
                if test_name in self._baseline and assertion_type in self._baseline[test_name]:
                    prior_score = self._baseline[test_name][assertion_type].get("score")
                
                if prior_score is not None:
                    delta = current_score - prior_score
                    baseline_delta[test_name][assertion_type] = delta
                    if delta < self.REGRESSION_THRESHOLD:
                        regressed_tests.add(test_name)
                        regression_detected = True
                else:
                    baseline_delta[test_name][assertion_type] = 0.0
        
        return baseline_delta, sorted(list(regressed_tests)), regression_detected
    
    def update(self, current_scores):
        commit_sha = self._get_current_commit()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
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
    def _get_current_commit():
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        except:
            return "unknown"
