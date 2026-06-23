#!/usr/bin/env python3
"""Generate the static Crosswise synthetic document pack."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crosswise.documents import (
    DOCUMENT_PACK_SCREENSHOT_OUTPUT_PATH,
    generate_document_pack,
    generate_document_pack_screenshot,
)


def main() -> int:
    try:
        output_paths = generate_document_pack(REPO_ROOT)
        screenshot_path = generate_document_pack_screenshot(
            output_paths["invoice"],
            REPO_ROOT / DOCUMENT_PACK_SCREENSHOT_OUTPUT_PATH,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Invoice: {output_paths['invoice']}")
    print(f"Purchase order: {output_paths['purchase_order']}")
    print(f"Receipt: {output_paths['receipt']}")
    print(f"Screenshot: {screenshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
