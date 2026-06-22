#!/usr/bin/env python3
"""Validate generated Crosswise synthetic fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crosswise.validation import validate_fixture_file


def main() -> int:
    fixture_path = REPO_ROOT / "data" / "synthetic" / "fixtures_v1_0.json"
    report = validate_fixture_file(fixture_path)

    print("Crosswise fixture validation")
    print(f"Fixture: {fixture_path}")
    print(f"Passed checks: {len(report.passed_checks)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Failures: {len(report.failures)}")

    for warning in report.warnings:
        print(f"WARNING: {warning.format()}")
    for failure in report.failures:
        print(f"FAILURE: {failure.format()}")

    if report.is_valid:
        print("Validation passed.")
        return 0
    print("Validation failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
