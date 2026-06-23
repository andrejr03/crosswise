"""Synthetic document pack generation for Crosswise evidence artifacts."""

from .synthetic_documents import (
    DOCUMENTS_OUTPUT_DIR,
    DOCUMENT_PACK_SCREENSHOT_OUTPUT_PATH,
    INVOICE_OUTPUT_PATH,
    PURCHASE_ORDER_OUTPUT_PATH,
    RECEIPT_OUTPUT_PATH,
    REPRESENTATIVE_BUNDLE_ID,
    generate_document_pack,
    generate_document_pack_screenshot,
    render_document_pack,
)

__all__ = [
    "DOCUMENTS_OUTPUT_DIR",
    "DOCUMENT_PACK_SCREENSHOT_OUTPUT_PATH",
    "INVOICE_OUTPUT_PATH",
    "PURCHASE_ORDER_OUTPUT_PATH",
    "RECEIPT_OUTPUT_PATH",
    "REPRESENTATIVE_BUNDLE_ID",
    "generate_document_pack",
    "generate_document_pack_screenshot",
    "render_document_pack",
]
