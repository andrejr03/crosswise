#!/usr/bin/env python3
"""Evaluate Crosswise reconciliation output against generated ground truth."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crosswise.evaluation import evaluate_reconciliation_files, write_evaluation_output


def main() -> int:
    reconciliation_path = REPO_ROOT / "data" / "reconciliation" / "reconciliation_v1_0.json"
    ground_truth_path = REPO_ROOT / "data" / "ground_truth" / "ground_truth_v1_0.json"
    output_path = REPO_ROOT / "data" / "evaluation" / "evaluation_v1_0.json"

    result = evaluate_reconciliation_files(reconciliation_path, ground_truth_path)
    write_evaluation_output(result, output_path)

    summary = result["summary"]
    print("Crosswise reconciliation evaluation")
    print(f"Bundles evaluated: {summary['bundles_evaluated']}")
    print(f"Overall precision: {summary['overall_precision']}")
    print(f"Overall recall: {summary['overall_recall']}")
    print(f"Overall F1: {summary['overall_f1']}")
    print(f"Macro F1: {summary['macro_f1']}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
