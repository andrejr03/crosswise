#!/usr/bin/env python3
"""Score Crosswise reconciliation reliability and assign review routes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crosswise.confidence import score_reconciliation, write_reliability_output


def main() -> int:
    reconciliation_path = REPO_ROOT / "data" / "reconciliation" / "reconciliation_v1_0.json"
    evaluation_path = REPO_ROOT / "data" / "evaluation" / "evaluation_v1_0.json"
    output_path = REPO_ROOT / "data" / "reliability" / "reliability_v1_0.json"

    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    evaluation = None
    if evaluation_path.exists():
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))

    result = score_reconciliation(reconciliation, evaluation)
    write_reliability_output(result, output_path)

    summary = result["summary"]
    print("Crosswise reliability scoring")
    print(f"Cases scored: {summary['cases_scored']}")
    print(f"Auto accept: {summary['auto_accept']}")
    print(f"Needs review: {summary['needs_review']}")
    print(f"Blocked: {summary['blocked']}")
    print(f"Average confidence: {summary['average_confidence']}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
