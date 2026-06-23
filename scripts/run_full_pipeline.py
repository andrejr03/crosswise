#!/usr/bin/env python3
"""Run the complete local Crosswise artifact generation pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PIPELINE_STEPS = [
    ("Generate synthetic data", "scripts/generate_synthetic_data.py"),
    ("Validate fixtures", "scripts/validate_fixtures.py"),
    ("Run reconciliation", "scripts/run_reconciliation.py"),
    ("Evaluate reconciliation", "scripts/evaluate_reconciliation.py"),
    ("Score reliability", "scripts/score_reliability.py"),
    ("Generate evidence report", "scripts/generate_report.py"),
    ("Generate static reviewer", "scripts/generate_reviewer.py"),
]


def main() -> int:
    print("Crosswise full local pipeline", flush=True)
    for index, (label, script) in enumerate(PIPELINE_STEPS, start=1):
        command = [sys.executable, script]
        print(f"\n[{index}/{len(PIPELINE_STEPS)}] {label}", flush=True)
        print(f"$ python3 {script}", flush=True)
        subprocess.run(command, cwd=REPO_ROOT, check=True)

    print("\nCrosswise full local pipeline completed successfully.", flush=True)
    print("Generated outputs:", flush=True)
    print("- data/synthetic/fixtures_v1_0.json", flush=True)
    print("- data/ground_truth/ground_truth_v1_0.json", flush=True)
    print("- data/reconciliation/reconciliation_v1_0.json", flush=True)
    print("- data/evaluation/evaluation_v1_0.json", flush=True)
    print("- data/reliability/reliability_v1_0.json", flush=True)
    print("- docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md", flush=True)
    print("- docs/evidence/crosswise_reviewer_v1_0.html", flush=True)
    print("- docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
