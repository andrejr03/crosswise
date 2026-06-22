#!/usr/bin/env python
"""Generate deterministic Crosswise Slice 1 synthetic fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crosswise.generation import DEFAULT_SEED, generate_fixture_set, write_fixture_set


def main() -> int:
    fixture_set = generate_fixture_set(seed=DEFAULT_SEED)
    synthetic_path, ground_truth_path = write_fixture_set(
        fixture_set=fixture_set,
        synthetic_dir=REPO_ROOT / "data" / "synthetic",
        ground_truth_dir=REPO_ROOT / "data" / "ground_truth",
    )
    print(f"Wrote synthetic fixtures: {synthetic_path}")
    print(f"Wrote ground truth: {ground_truth_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
