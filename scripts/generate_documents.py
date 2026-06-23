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
    generate_document_pack,
    generate_document_pack_screenshots,
)


def main() -> int:
    try:
        output_paths = generate_document_pack(REPO_ROOT)
        screenshot_paths = generate_document_pack_screenshots(output_paths, REPO_ROOT)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Index: {output_paths['index']}")
    print(f"Invoice: {output_paths['invoice']}")
    print(f"Purchase order: {output_paths['purchase_order']}")
    print(f"Receipt: {output_paths['receipt']}")
    print(f"Index screenshot: {screenshot_paths['index']}")
    print(f"Invoice screenshot: {screenshot_paths['invoice']}")
    print(f"Purchase order screenshot: {screenshot_paths['purchase_order']}")
    print(f"Receipt screenshot: {screenshot_paths['receipt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
