#!/usr/bin/env python3
"""Generate the static local Crosswise reviewer interface."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crosswise.reviewer import (
    INTERACTIVE_EXPLORER_SELECTOR,
    INTERACTIVE_SCREENSHOT_OUTPUT_PATH,
    SCREENSHOT_OUTPUT_PATH,
    generate_reviewer_screenshot,
    generate_static_reviewer,
)


def main() -> int:
    try:
        output_path = generate_static_reviewer(REPO_ROOT)
        screenshot_path = generate_reviewer_screenshot(output_path, REPO_ROOT / SCREENSHOT_OUTPUT_PATH)
        interactive_screenshot_path = generate_reviewer_screenshot(
            output_path,
            REPO_ROOT / INTERACTIVE_SCREENSHOT_OUTPUT_PATH,
            selector=INTERACTIVE_EXPLORER_SELECTOR,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Output: {output_path}")
    print(f"Screenshot: {screenshot_path}")
    print(f"Interactive screenshot: {interactive_screenshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
