#!/usr/bin/env python3
"""Run Crosswise Slice 3 deterministic reconciliation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crosswise.reconciliation import reconcile_fixture_files, write_reconciliation_output


def main() -> int:
    synthetic_path = REPO_ROOT / "data" / "synthetic" / "fixtures_v1_0.json"
    ground_truth_path = REPO_ROOT / "data" / "ground_truth" / "ground_truth_v1_0.json"
    output_path = REPO_ROOT / "data" / "reconciliation" / "reconciliation_v1_0.json"

    result = reconcile_fixture_files(synthetic_path, ground_truth_path)
    write_reconciliation_output(result, output_path)

    print("Crosswise deterministic reconciliation")
    print(f"Bundles reconciled: {result['summary']['bundles_reconciled']}")
    print(f"Detected cases: {result['summary']['detected_cases']}")
    print(f"Detected label counts: {result['summary']['label_counts']}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
