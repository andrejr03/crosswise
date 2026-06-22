"""Slice 3 deterministic reconciliation baseline.

This module intentionally avoids confidence scoring, statistical evaluation, UI
concerns, OCR, APIs, and model calls.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from crosswise.matching import (
    build_sku_lookup,
    match_invoice_line,
    match_receipt_line,
    supplier_match_basis,
)
from crosswise.normalization import normalize_supplier_name
from crosswise.schemas.models import DISCREPANCY_LABELS
from crosswise.validation import validate_fixture_payload

LABEL_ORDER = tuple(DISCREPANCY_LABELS)

ROUTE_DEFAULTS = {
    "clean_match": "auto_accept",
    "schema_validation_failure": "blocked",
    "duplicate_invoice": "needs_review",
    "missing_receipt_line": "needs_review",
    "quantity_mismatch": "needs_review",
    "unit_price_mismatch": "needs_review",
    "supplier_alias_mismatch": "needs_review",
    "late_receipt": "needs_review",
    "low_confidence_extraction": "needs_review",
    "missing_invoice_line": "needs_review",
}

SEVERITY_DEFAULTS = {
    "clean_match": "none",
    "schema_validation_failure": "high",
    "duplicate_invoice": "high",
    "missing_receipt_line": "high",
    "quantity_mismatch": "medium",
    "unit_price_mismatch": "medium",
    "missing_invoice_line": "medium",
    "low_confidence_extraction": "medium",
    "supplier_alias_mismatch": "low",
    "late_receipt": "low",
}


def reconcile_fixture_files(synthetic_path: Path, ground_truth_path: Path | None = None) -> dict[str, Any]:
    payload = json.loads(synthetic_path.read_text(encoding="utf-8"))
    ground_truth = None
    if ground_truth_path and ground_truth_path.exists():
        ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
    return reconcile_fixture_payload(payload, ground_truth)


def reconcile_fixture_payload(payload: dict[str, Any], ground_truth: dict[str, Any] | None = None) -> dict[str, Any]:
    validation_report = validate_fixture_payload(payload)
    if not validation_report.is_valid:
        failures = [issue.format() for issue in validation_report.failures]
        raise ValueError("fixture validation failed before reconciliation: " + "; ".join(failures))

    context = _build_context(payload, ground_truth or {})
    cases = [_reconcile_bundle(bundle, context) for bundle in payload["document_bundles"]]
    label_counts = dict(sorted(Counter(label for case in cases for label in case["discrepancy_labels"]).items()))
    return {
        "metadata": {
            "fixture_version": payload.get("metadata", {}).get("fixture_version"),
            "generator_version": payload.get("metadata", {}).get("generator_version"),
            "reconciliation_version": "slice_3_baseline_v1",
            "confidence_scoring": "not_implemented",
            "matching_strategy": "deterministic_sku_supplier_baseline",
        },
        "summary": {
            "bundles_reconciled": len(cases),
            "detected_cases": len(cases),
            "label_counts": label_counts,
        },
        "cases": cases,
    }


def write_reconciliation_output(result: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _build_context(payload: dict[str, Any], ground_truth: dict[str, Any]) -> dict[str, Any]:
    return {
        "suppliers": {record["supplier_id"]: record for record in payload["suppliers"]},
        "skus": {record["sku_id"]: record for record in payload["skus"]},
        "purchase_orders": {record["purchase_order_id"]: record for record in payload["purchase_orders"]},
        "purchase_order_lines": _group_by(payload["purchase_order_lines"], "purchase_order_id"),
        "invoices": {record["invoice_id"]: record for record in payload["invoices"]},
        "invoice_lines": _group_by(payload["invoice_lines"], "invoice_id"),
        "receipts": {record["receipt_id"]: record for record in payload["receipts"]},
        "receipt_lines": _group_by(payload["receipt_lines"], "receipt_id"),
        "sku_lookup": build_sku_lookup(payload["skus"]),
        "ground_truth_bundles": ground_truth.get("bundles", {}),
    }


def _group_by(records: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(record[field], []).append(record)
    return grouped


def _reconcile_bundle(bundle: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    po = context["purchase_orders"][bundle["purchase_order_id"]]
    supplier = context["suppliers"][bundle["supplier_id"]]
    invoices = [context["invoices"][invoice_id] for invoice_id in bundle["invoice_ids"]]
    receipts = [context["receipts"][receipt_id] for receipt_id in bundle["receipt_ids"]]
    po_lines = context["purchase_order_lines"][po["purchase_order_id"]]
    primary_invoices = [invoice for invoice in invoices if not invoice.get("duplicate_of_invoice_id")]
    invoice_lines = [line for invoice in primary_invoices for line in context["invoice_lines"][invoice["invoice_id"]]]
    receipt_lines = [line for receipt in receipts for line in context["receipt_lines"][receipt["receipt_id"]]]
    truth = context["ground_truth_bundles"].get(bundle["bundle_id"], {})

    labels: set[str] = set()
    evidence: list[dict[str, Any]] = []
    line_matches: list[dict[str, Any]] = []

    _detect_supplier_aliases(labels, evidence, supplier, invoices, po, receipts)
    _detect_duplicate_invoices(labels, evidence, invoices, po, receipts)
    _detect_late_receipt(labels, evidence, po, receipts)

    for po_line in sorted(po_lines, key=lambda item: item["line_number"]):
        invoice_line, invoice_basis = match_invoice_line(po_line, invoice_lines, context["sku_lookup"])
        receipt_line, receipt_basis = match_receipt_line(po_line, receipt_lines, context["sku_lookup"])
        line_labels = _detect_line_discrepancies(
            labels=labels,
            evidence=evidence,
            po=po,
            invoices=invoices,
            receipts=receipts,
            po_line=po_line,
            invoice_line=invoice_line,
            receipt_line=receipt_line,
        )
        line_matches.append(
            {
                "po_line_id": po_line["po_line_id"],
                "invoice_line_id": invoice_line["invoice_line_id"] if invoice_line else None,
                "receipt_line_id": receipt_line["receipt_line_id"] if receipt_line else None,
                "invoice_match_basis": invoice_basis,
                "receipt_match_basis": receipt_basis,
                "labels": _ordered_labels(line_labels) or ["clean_match"],
            }
        )

    _carry_simulated_extraction_issues(labels, evidence, truth, po, invoices, receipts)

    if not labels:
        labels.add("clean_match")

    ordered = _ordered_labels(labels)
    route = _route_for(ordered)
    severity = _severity_for(ordered)
    return {
        "case_id": f"case_{bundle['bundle_id']}",
        "bundle_id": bundle["bundle_id"],
        "matched_supplier_id": supplier["supplier_id"],
        "purchase_order_id": po["purchase_order_id"],
        "invoice_ids": [invoice["invoice_id"] for invoice in invoices],
        "receipt_ids": [receipt["receipt_id"] for receipt in receipts],
        "line_matches": line_matches,
        "discrepancy_labels": ordered,
        "severity": severity,
        "route": route,
        "confidence_score": None,
        "confidence_note": "Slice 3 does not implement confidence scoring.",
        "evidence": evidence,
        "explanation": _explanation_for(ordered),
    }


def _detect_supplier_aliases(
    labels: set[str],
    evidence: list[dict[str, Any]],
    supplier: dict[str, Any],
    invoices: list[dict[str, Any]],
    po: dict[str, Any],
    receipts: list[dict[str, Any]],
) -> None:
    for invoice in invoices:
        basis = supplier_match_basis(supplier, invoice.get("supplier_name_raw"), invoice.get("supplier_id"))
        if basis == "supplier_id_exact_with_known_alias" or basis == "known_supplier_alias":
            labels.add("supplier_alias_mismatch")
            evidence.append(
                _evidence(
                    label="supplier_alias_mismatch",
                    affected_document_ids=[po["purchase_order_id"], invoice["invoice_id"], *[r["receipt_id"] for r in receipts]],
                    affected_line_ids=[],
                    compared_fields=["supplier.canonical_name", "invoice.supplier_name_raw"],
                    observed_values={
                        "canonical_name": supplier["canonical_name"],
                        "supplier_name_raw": invoice["supplier_name_raw"],
                    },
                    normalized_values={
                        "canonical_name": normalize_supplier_name(supplier["canonical_name"]),
                        "supplier_name_raw": normalize_supplier_name(invoice["supplier_name_raw"]),
                    },
                    detection_basis=basis,
                    explanation="Invoice supplier name is a known normalized alias of the canonical supplier.",
                )
            )


def _detect_duplicate_invoices(
    labels: set[str],
    evidence: list[dict[str, Any]],
    invoices: list[dict[str, Any]],
    po: dict[str, Any],
    receipts: list[dict[str, Any]],
) -> None:
    seen: dict[tuple[Any, ...], dict[str, Any]] = {}
    for invoice in invoices:
        key = (
            invoice.get("supplier_id"),
            invoice.get("invoice_number"),
            invoice.get("invoice_date"),
            invoice.get("subtotal"),
            invoice.get("total_amount"),
        )
        duplicate_of = invoice.get("duplicate_of_invoice_id")
        if key in seen or duplicate_of:
            original = seen.get(key)
            labels.add("duplicate_invoice")
            evidence.append(
                _evidence(
                    label="duplicate_invoice",
                    affected_document_ids=[po["purchase_order_id"], invoice["invoice_id"], *[r["receipt_id"] for r in receipts]],
                    affected_line_ids=[],
                    compared_fields=["invoice_number", "supplier_id", "invoice_date", "total_amount"],
                    observed_values={
                        "invoice_id": invoice["invoice_id"],
                        "duplicate_of_invoice_id": duplicate_of,
                        "original_invoice_id": original["invoice_id"] if original else duplicate_of,
                        "invoice_number": invoice["invoice_number"],
                        "total_amount": invoice["total_amount"],
                    },
                    normalized_values={"duplicate_key": "|".join(str(part) for part in key)},
                    detection_basis="duplicate_invoice_number_supplier_date_total",
                    explanation="Invoice shares deterministic duplicate identifiers and totals with another invoice.",
                )
            )
        else:
            seen[key] = invoice


def _detect_late_receipt(
    labels: set[str],
    evidence: list[dict[str, Any]],
    po: dict[str, Any],
    receipts: list[dict[str, Any]],
) -> None:
    expected = po.get("expected_receipt_date")
    if not expected:
        return
    expected_date = date.fromisoformat(expected)
    for receipt in receipts:
        receipt_date = date.fromisoformat(receipt["receipt_date"])
        if receipt_date > expected_date:
            labels.add("late_receipt")
            evidence.append(
                _evidence(
                    label="late_receipt",
                    affected_document_ids=[po["purchase_order_id"], receipt["receipt_id"]],
                    affected_line_ids=[],
                    compared_fields=["purchase_order.expected_receipt_date", "receipt.receipt_date"],
                    observed_values={"expected_receipt_date": expected, "receipt_date": receipt["receipt_date"]},
                    normalized_values={"expected_receipt_date": expected_date.isoformat(), "receipt_date": receipt_date.isoformat()},
                    detection_basis="receipt_date_after_expected_receipt_date",
                    explanation="Receipt date is later than the purchase order expected receipt date.",
                )
            )


def _detect_line_discrepancies(
    labels: set[str],
    evidence: list[dict[str, Any]],
    po: dict[str, Any],
    invoices: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
    po_line: dict[str, Any],
    invoice_line: dict[str, Any] | None,
    receipt_line: dict[str, Any] | None,
) -> set[str]:
    line_labels: set[str] = set()
    document_ids = [po["purchase_order_id"], *[i["invoice_id"] for i in invoices], *[r["receipt_id"] for r in receipts]]
    if invoice_line is None:
        labels.add("missing_invoice_line")
        line_labels.add("missing_invoice_line")
        evidence.append(
            _evidence(
                label="missing_invoice_line",
                affected_document_ids=document_ids,
                affected_line_ids=[po_line["po_line_id"]],
                compared_fields=["po_line.sku_id", "invoice_line.sku_id"],
                observed_values={"po_line_sku_id": po_line["sku_id"], "invoice_line_id": None},
                normalized_values={"po_line_sku_id": po_line["sku_id"]},
                detection_basis="no_invoice_line_for_po_sku",
                explanation="No invoice line matched the purchase order line SKU.",
            )
        )
    if receipt_line is None:
        labels.add("missing_receipt_line")
        line_labels.add("missing_receipt_line")
        evidence.append(
            _evidence(
                label="missing_receipt_line",
                affected_document_ids=document_ids,
                affected_line_ids=[po_line["po_line_id"], *( [invoice_line["invoice_line_id"]] if invoice_line else [] )],
                compared_fields=["po_line.sku_id", "receipt_line.sku_id"],
                observed_values={"po_line_sku_id": po_line["sku_id"], "receipt_line_id": None},
                normalized_values={"po_line_sku_id": po_line["sku_id"]},
                detection_basis="no_receipt_line_for_po_sku",
                explanation="No receipt line matched the purchase order line SKU.",
            )
        )
    if invoice_line is not None and receipt_line is not None:
        quantities = {
            "quantity_ordered": po_line["quantity_ordered"],
            "quantity_billed": invoice_line["quantity_billed"],
            "quantity_received": receipt_line["quantity_received"],
        }
        if Decimal(quantities["quantity_ordered"]) != Decimal(quantities["quantity_billed"]) or Decimal(quantities["quantity_ordered"]) != Decimal(quantities["quantity_received"]):
            labels.add("quantity_mismatch")
            line_labels.add("quantity_mismatch")
            evidence.append(
                _evidence(
                    label="quantity_mismatch",
                    affected_document_ids=document_ids,
                    affected_line_ids=[po_line["po_line_id"], invoice_line["invoice_line_id"], receipt_line["receipt_line_id"]],
                    compared_fields=["quantity_ordered", "quantity_billed", "quantity_received"],
                    observed_values=quantities,
                    normalized_values=quantities,
                    detection_basis="ordered_billed_received_quantity_difference",
                    explanation="Ordered, billed, and received quantities are not identical.",
                )
            )
        prices = {
            "po_unit_price": po_line["unit_price"],
            "invoice_unit_price": invoice_line["unit_price"],
        }
        if Decimal(prices["po_unit_price"]) != Decimal(prices["invoice_unit_price"]):
            labels.add("unit_price_mismatch")
            line_labels.add("unit_price_mismatch")
            evidence.append(
                _evidence(
                    label="unit_price_mismatch",
                    affected_document_ids=document_ids,
                    affected_line_ids=[po_line["po_line_id"], invoice_line["invoice_line_id"]],
                    compared_fields=["po_line.unit_price", "invoice_line.unit_price"],
                    observed_values=prices,
                    normalized_values=prices,
                    detection_basis="purchase_order_invoice_unit_price_difference",
                    explanation="Invoice unit price differs from purchase order unit price.",
                )
            )
    return line_labels


def _carry_simulated_extraction_issues(
    labels: set[str],
    evidence: list[dict[str, Any]],
    truth: dict[str, Any],
    po: dict[str, Any],
    invoices: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
) -> None:
    for issue in truth.get("simulated_extraction_issues", []):
        issue_type = issue.get("issue_type")
        if issue_type not in {"low_confidence_extraction", "schema_validation_failure"}:
            continue
        labels.add(issue_type)
        evidence.append(
            _evidence(
                label=issue_type,
                affected_document_ids=[po["purchase_order_id"], *[i["invoice_id"] for i in invoices], *[r["receipt_id"] for r in receipts]],
                affected_line_ids=[],
                compared_fields=[issue.get("field_name")],
                observed_values=issue,
                normalized_values=issue,
                detection_basis="simulated_extraction_issue_from_ground_truth",
                explanation="Slice 3 carries through a fixture-encoded simulated extraction issue without confidence scoring.",
            )
        )


def _ordered_labels(labels: set[str]) -> list[str]:
    return [label for label in LABEL_ORDER if label in labels]


def _route_for(labels: list[str]) -> str:
    if "schema_validation_failure" in labels:
        return "blocked"
    if labels == ["clean_match"]:
        return "auto_accept"
    return "needs_review"


def _severity_for(labels: list[str]) -> str:
    if "schema_validation_failure" in labels or "duplicate_invoice" in labels or "missing_receipt_line" in labels:
        return "high"
    if any(label in labels for label in ("quantity_mismatch", "unit_price_mismatch", "missing_invoice_line", "low_confidence_extraction")):
        return "medium"
    if any(label in labels for label in ("supplier_alias_mismatch", "late_receipt")):
        return "low"
    return "none"


def _explanation_for(labels: list[str]) -> str:
    if labels == ["clean_match"]:
        return "All deterministic baseline checks passed for the bundle."
    return "Deterministic baseline reconciliation detected one or more reviewable discrepancies."


def _evidence(
    label: str,
    affected_document_ids: list[str],
    affected_line_ids: list[str],
    compared_fields: list[str | None],
    observed_values: dict[str, Any],
    normalized_values: dict[str, Any],
    detection_basis: str,
    explanation: str,
) -> dict[str, Any]:
    return {
        "label": label,
        "affected_document_ids": affected_document_ids,
        "affected_line_ids": affected_line_ids,
        "compared_fields": [field for field in compared_fields if field],
        "observed_values": observed_values,
        "normalized_values": normalized_values,
        "detection_basis": detection_basis,
        "explanation": explanation,
    }
