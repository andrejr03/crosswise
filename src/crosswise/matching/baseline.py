"""Baseline deterministic matching for suppliers and line items."""

from __future__ import annotations

from typing import Any

from crosswise.normalization import (
    normalize_sku_text,
    normalize_supplier_aliases,
    normalize_supplier_name,
)


def supplier_match_basis(supplier: dict[str, Any], raw_supplier_name: str | None, supplier_id: str | None) -> str | None:
    if supplier_id and supplier_id == supplier.get("supplier_id"):
        if _is_known_supplier_alias(supplier, raw_supplier_name):
            return "supplier_id_exact_with_known_alias"
        return "supplier_id_exact"
    if _is_known_supplier_alias(supplier, raw_supplier_name):
        return "known_supplier_alias"
    return None


def build_sku_lookup(skus: list[dict[str, Any]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for sku in skus:
        sku_id = sku["sku_id"]
        lookup[normalize_sku_text(sku["canonical_name"])] = sku_id
        for alias in sku.get("aliases", []):
            lookup[normalize_sku_text(alias)] = sku_id
    return lookup


def match_invoice_line(
    po_line: dict[str, Any],
    invoice_lines: list[dict[str, Any]],
    sku_lookup: dict[str, str],
) -> tuple[dict[str, Any] | None, str]:
    return _match_line(po_line, invoice_lines, "invoice_line_id", "sku_raw", sku_lookup)


def match_receipt_line(
    po_line: dict[str, Any],
    receipt_lines: list[dict[str, Any]],
    sku_lookup: dict[str, str],
) -> tuple[dict[str, Any] | None, str]:
    return _match_line(po_line, receipt_lines, "receipt_line_id", "sku_raw", sku_lookup)


def _match_line(
    po_line: dict[str, Any],
    candidate_lines: list[dict[str, Any]],
    id_field: str,
    raw_field: str,
    sku_lookup: dict[str, str],
) -> tuple[dict[str, Any] | None, str]:
    exact = [line for line in candidate_lines if line.get("sku_id") == po_line.get("sku_id")]
    if len(exact) == 1:
        return exact[0], "sku_id_exact"
    if len(exact) > 1:
        return None, "sku_id_ambiguous"

    po_sku_id = po_line.get("sku_id")
    fallback = [
        line
        for line in candidate_lines
        if line.get("sku_id") in (None, "")
        and sku_lookup.get(normalize_sku_text(str(line.get(raw_field, "")))) == po_sku_id
    ]
    if len(fallback) == 1:
        return fallback[0], "normalized_sku_text_unambiguous"
    if len(fallback) > 1:
        return None, "normalized_sku_text_ambiguous"
    return None, f"no_{id_field}_match"


def _is_known_supplier_alias(supplier: dict[str, Any], raw_supplier_name: str | None) -> bool:
    if not raw_supplier_name:
        return False
    normalized_raw = normalize_supplier_name(raw_supplier_name)
    normalized_canonical = normalize_supplier_name(supplier["canonical_name"])
    normalized_aliases = set(normalize_supplier_aliases(supplier.get("aliases", [])))
    return normalized_raw != normalized_canonical and normalized_raw in normalized_aliases
