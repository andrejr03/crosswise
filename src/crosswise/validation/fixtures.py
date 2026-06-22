"""Contract validation for generated synthetic fixture payloads."""

from __future__ import annotations

import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from crosswise.normalization import normalize_currency_code, normalize_date
from crosswise.schemas.models import DISCREPANCY_LABELS, ROUTES, SEVERITIES
from crosswise.validation.result import ValidationReport

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "suppliers": ("supplier_id", "canonical_name", "aliases"),
    "skus": ("sku_id", "canonical_name", "aliases", "unit_of_measure"),
    "purchase_orders": (
        "purchase_order_id",
        "bundle_id",
        "supplier_id",
        "issue_date",
        "currency",
        "line_ids",
        "subtotal",
        "total_amount",
    ),
    "purchase_order_lines": (
        "po_line_id",
        "purchase_order_id",
        "line_number",
        "sku_id",
        "quantity_ordered",
        "unit_of_measure",
        "unit_price",
        "line_total",
    ),
    "invoices": (
        "invoice_id",
        "bundle_id",
        "supplier_name_raw",
        "invoice_number",
        "invoice_date",
        "currency",
        "line_ids",
        "subtotal",
        "total_amount",
    ),
    "invoice_lines": (
        "invoice_line_id",
        "invoice_id",
        "line_number",
        "sku_raw",
        "quantity_billed",
        "unit_of_measure",
        "unit_price",
        "line_total",
    ),
    "receipts": ("receipt_id", "bundle_id", "receipt_number", "receipt_date", "line_ids"),
    "receipt_lines": (
        "receipt_line_id",
        "receipt_id",
        "line_number",
        "sku_raw",
        "quantity_received",
        "unit_of_measure",
    ),
    "document_bundles": (
        "bundle_id",
        "fixture_version",
        "generator_version",
        "seed",
        "scenario_name",
        "supplier_id",
        "purchase_order_id",
        "invoice_ids",
        "receipt_ids",
        "discrepancy_labels",
        "expected_route",
    ),
}

ID_FIELDS: dict[str, str] = {
    "suppliers": "supplier_id",
    "skus": "sku_id",
    "purchase_orders": "purchase_order_id",
    "purchase_order_lines": "po_line_id",
    "invoices": "invoice_id",
    "invoice_lines": "invoice_line_id",
    "receipts": "receipt_id",
    "receipt_lines": "receipt_line_id",
    "document_bundles": "bundle_id",
    "discrepancy_labels": "label_id",
}

FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"@",
        r"\biban\b",
        r"\bswift\b",
        r"\bbank account\b",
        r"\btax id\b",
        r"\bvat id\b",
        r"\bpayment\b",
        r"\bacme\b",
        r"\bgoogle\b",
        r"\bmicrosoft\b",
        r"\bamazon\b",
        r"\bapple\b",
        r"\bgmail\b",
        r"\bhotmail\b",
    )
)


def validate_fixture_file(path: Path) -> ValidationReport:
    return validate_fixture_payload(json.loads(path.read_text(encoding="utf-8")))


def validate_fixture_payload(payload: dict[str, Any]) -> ValidationReport:
    report = ValidationReport()
    _validate_top_level(payload, report)
    _validate_required_fields(payload, report)
    _validate_id_uniqueness(payload, report)
    _validate_field_domains(payload, report)
    _validate_references(payload, report)
    _validate_synthetic_only(payload, report)
    _mark_passes(report)
    return report


def _validate_top_level(payload: dict[str, Any], report: ValidationReport) -> None:
    expected = set(REQUIRED_FIELDS) | {"metadata", "discrepancy_labels"}
    for key in expected:
        if key not in payload:
            report.fail("top_level", "missing top-level collection", field=key)
        elif key != "metadata" and not isinstance(payload[key], list):
            report.fail("top_level", "collection must be a list", collection=key)
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        report.fail("metadata", "metadata must be an object", collection="metadata")
    elif metadata.get("synthetic_only") is not True:
        report.fail("metadata", "synthetic_only must be true", collection="metadata", field="synthetic_only")


def _validate_required_fields(payload: dict[str, Any], report: ValidationReport) -> None:
    for collection, fields in REQUIRED_FIELDS.items():
        for record in _records(payload, collection):
            record_id = _record_id(collection, record)
            if not isinstance(record, dict):
                report.fail("required_fields", "record must be an object", collection=collection)
                continue
            for field in fields:
                if field not in record:
                    report.fail("required_fields", "required field missing", collection, record_id, field)
                elif record[field] is None:
                    report.fail("required_fields", "required field is null", collection, record_id, field)
                elif isinstance(record[field], str) and not record[field].strip():
                    report.fail("required_fields", "required string is empty", collection, record_id, field)
            for list_field in ("aliases", "line_ids", "invoice_ids", "receipt_ids", "discrepancy_labels"):
                if list_field in record and not isinstance(record[list_field], list):
                    report.fail("field_types", "field must be a list", collection, record_id, list_field)

    for label in _records(payload, "discrepancy_labels"):
        record_id = _record_id("discrepancy_labels", label)
        for field in (
            "label_id",
            "label_type",
            "bundle_id",
            "affected_document_ids",
            "affected_line_ids",
            "severity_default",
            "expected_evidence",
            "v1_requirement",
        ):
            if field not in label:
                report.fail("required_fields", "required field missing", "discrepancy_labels", record_id, field)


def _validate_id_uniqueness(payload: dict[str, Any], report: ValidationReport) -> None:
    for collection, id_field in ID_FIELDS.items():
        seen: set[str] = set()
        for record in _records(payload, collection):
            record_id = record.get(id_field) if isinstance(record, dict) else None
            if not isinstance(record_id, str) or not record_id.strip():
                report.fail("id_presence", "ID must be a non-empty string", collection, field=id_field)
                continue
            if record_id in seen:
                report.fail("id_uniqueness", "duplicate ID", collection, record_id, id_field)
            seen.add(record_id)


def _validate_field_domains(payload: dict[str, Any], report: ValidationReport) -> None:
    for sku in _records(payload, "skus"):
        _check_optional_money(report, "skus", sku, "standard_unit_price")
    for po in _records(payload, "purchase_orders"):
        _check_iso_date(report, "purchase_orders", po, "issue_date")
        _check_iso_date(report, "purchase_orders", po, "expected_receipt_date", optional=True)
        _check_currency(report, "purchase_orders", po, "currency")
        _check_money(report, "purchase_orders", po, "subtotal")
        _check_optional_money(report, "purchase_orders", po, "tax_amount")
        _check_money(report, "purchase_orders", po, "total_amount")
        if _valid_dates(po.get("issue_date"), po.get("expected_receipt_date")):
            if date.fromisoformat(po["expected_receipt_date"]) < date.fromisoformat(po["issue_date"]):
                report.fail("date_rules", "expected_receipt_date must be on or after issue_date", "purchase_orders", po.get("purchase_order_id"), "expected_receipt_date")
    for line in _records(payload, "purchase_order_lines"):
        _check_positive_quantity(report, "purchase_order_lines", line, "quantity_ordered")
        _check_money(report, "purchase_order_lines", line, "unit_price")
        _check_money(report, "purchase_order_lines", line, "line_total")
        _check_line_total(report, "purchase_order_lines", line, "quantity_ordered", "unit_price", "line_total")
    for invoice in _records(payload, "invoices"):
        _check_iso_date(report, "invoices", invoice, "invoice_date")
        _check_iso_date(report, "invoices", invoice, "due_date", optional=True)
        _check_currency(report, "invoices", invoice, "currency")
        _check_money(report, "invoices", invoice, "subtotal")
        _check_optional_money(report, "invoices", invoice, "tax_amount")
        _check_money(report, "invoices", invoice, "total_amount")
        if _valid_dates(invoice.get("invoice_date"), invoice.get("due_date")):
            if date.fromisoformat(invoice["due_date"]) < date.fromisoformat(invoice["invoice_date"]):
                report.fail("date_rules", "due_date must be on or after invoice_date", "invoices", invoice.get("invoice_id"), "due_date")
    for line in _records(payload, "invoice_lines"):
        _check_positive_quantity(report, "invoice_lines", line, "quantity_billed")
        _check_money(report, "invoice_lines", line, "unit_price")
        _check_money(report, "invoice_lines", line, "line_total")
        _check_line_total(report, "invoice_lines", line, "quantity_billed", "unit_price", "line_total")
    for receipt in _records(payload, "receipts"):
        _check_iso_date(report, "receipts", receipt, "receipt_date")
    for line in _records(payload, "receipt_lines"):
        _check_non_negative_quantity(report, "receipt_lines", line, "quantity_received")
        _check_iso_date(report, "receipt_lines", line, "received_date", optional=True)
    for bundle in _records(payload, "document_bundles"):
        if bundle.get("expected_route") not in ROUTES:
            report.fail("field_domain", "expected_route is not supported", "document_bundles", bundle.get("bundle_id"), "expected_route")
        labels = bundle.get("discrepancy_labels", [])
        unknown = set(labels) - set(DISCREPANCY_LABELS) if isinstance(labels, list) else set()
        if unknown:
            report.fail("field_domain", f"unsupported discrepancy labels: {sorted(unknown)}", "document_bundles", bundle.get("bundle_id"), "discrepancy_labels")
        if isinstance(labels, list) and "clean_match" in labels and len(labels) > 1:
            report.fail("field_domain", "clean_match cannot be combined with non-clean labels", "document_bundles", bundle.get("bundle_id"), "discrepancy_labels")
    for label in _records(payload, "discrepancy_labels"):
        if label.get("label_type") not in DISCREPANCY_LABELS:
            report.fail("field_domain", "label_type is not supported", "discrepancy_labels", label.get("label_id"), "label_type")
        if label.get("severity_default") not in SEVERITIES:
            report.fail("field_domain", "severity_default is not supported", "discrepancy_labels", label.get("label_id"), "severity_default")

    _validate_parent_totals(payload, report)


def _validate_references(payload: dict[str, Any], report: ValidationReport) -> None:
    ids = {
        collection: {
            record.get(id_field)
            for record in _records(payload, collection)
            if isinstance(record, dict) and isinstance(record.get(id_field), str)
        }
        for collection, id_field in ID_FIELDS.items()
    }
    _require_refs(report, payload, "purchase_orders", "bundle_id", ids["document_bundles"])
    _require_refs(report, payload, "purchase_orders", "supplier_id", ids["suppliers"])
    _require_refs(report, payload, "purchase_order_lines", "purchase_order_id", ids["purchase_orders"])
    _require_refs(report, payload, "purchase_order_lines", "sku_id", ids["skus"])
    _require_refs(report, payload, "invoices", "bundle_id", ids["document_bundles"])
    _require_refs(report, payload, "invoices", "supplier_id", ids["suppliers"], optional=True)
    _require_refs(report, payload, "invoices", "duplicate_of_invoice_id", ids["invoices"], optional=True)
    _require_refs(report, payload, "invoice_lines", "invoice_id", ids["invoices"])
    _require_refs(report, payload, "invoice_lines", "sku_id", ids["skus"], optional=True)
    _require_refs(report, payload, "receipts", "bundle_id", ids["document_bundles"])
    _require_refs(report, payload, "receipts", "supplier_id", ids["suppliers"], optional=True)
    _require_refs(report, payload, "receipts", "related_purchase_order_id", ids["purchase_orders"], optional=True)
    _require_refs(report, payload, "receipt_lines", "receipt_id", ids["receipts"])
    _require_refs(report, payload, "receipt_lines", "sku_id", ids["skus"], optional=True)
    _require_refs(report, payload, "document_bundles", "supplier_id", ids["suppliers"])
    _require_refs(report, payload, "document_bundles", "purchase_order_id", ids["purchase_orders"])
    _require_list_refs(report, payload, "document_bundles", "invoice_ids", ids["invoices"])
    _require_list_refs(report, payload, "document_bundles", "receipt_ids", ids["receipts"])
    _require_refs(report, payload, "discrepancy_labels", "bundle_id", ids["document_bundles"])
    _require_list_refs(report, payload, "purchase_orders", "line_ids", ids["purchase_order_lines"])
    _require_list_refs(report, payload, "invoices", "line_ids", ids["invoice_lines"])
    _require_list_refs(report, payload, "receipts", "line_ids", ids["receipt_lines"])


def _validate_synthetic_only(payload: dict[str, Any], report: ValidationReport) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(serialized):
            report.fail("synthetic_only", f"forbidden pattern found: {pattern.pattern}")


def _validate_parent_totals(payload: dict[str, Any], report: ValidationReport) -> None:
    po_line_totals = _sum_children(payload, "purchase_order_lines", "purchase_order_id")
    for po in _records(payload, "purchase_orders"):
        po_id = po.get("purchase_order_id")
        subtotal = _decimal(po.get("subtotal"))
        tax = _decimal(po.get("tax_amount") or "0")
        total = _decimal(po.get("total_amount"))
        if subtotal is not None and po_id in po_line_totals and subtotal != po_line_totals[po_id]:
            report.fail("monetary_rules", "subtotal does not equal child line total sum", "purchase_orders", po_id, "subtotal")
        if subtotal is not None and tax is not None and total is not None and total != subtotal + tax:
            report.fail("monetary_rules", "total_amount does not equal subtotal plus tax_amount", "purchase_orders", po_id, "total_amount")

    invoice_line_totals = _sum_children(payload, "invoice_lines", "invoice_id")
    for invoice in _records(payload, "invoices"):
        invoice_id = invoice.get("invoice_id")
        subtotal = _decimal(invoice.get("subtotal"))
        tax = _decimal(invoice.get("tax_amount") or "0")
        total = _decimal(invoice.get("total_amount"))
        if subtotal is not None and invoice_id in invoice_line_totals and subtotal != invoice_line_totals[invoice_id]:
            report.fail("monetary_rules", "subtotal does not equal child line total sum", "invoices", invoice_id, "subtotal")
        if subtotal is not None and tax is not None and total is not None and total != subtotal + tax:
            report.fail("monetary_rules", "total_amount does not equal subtotal plus tax_amount", "invoices", invoice_id, "total_amount")


def _records(payload: dict[str, Any], collection: str) -> list[dict[str, Any]]:
    value = payload.get(collection, [])
    return value if isinstance(value, list) else []


def _record_id(collection: str, record: dict[str, Any]) -> str | None:
    id_field = ID_FIELDS.get(collection)
    value = record.get(id_field) if id_field else None
    return value if isinstance(value, str) else None


def _decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _check_money(report: ValidationReport, collection: str, record: dict[str, Any], field: str) -> None:
    value = _decimal(record.get(field))
    if value is None:
        report.fail("monetary_rules", "value must be decimal-compatible", collection, _record_id(collection, record), field)
    elif value < 0:
        report.fail("monetary_rules", "value must be non-negative", collection, _record_id(collection, record), field)


def _check_optional_money(report: ValidationReport, collection: str, record: dict[str, Any], field: str) -> None:
    if record.get(field) is not None:
        _check_money(report, collection, record, field)


def _check_positive_quantity(report: ValidationReport, collection: str, record: dict[str, Any], field: str) -> None:
    value = _decimal(record.get(field))
    if value is None:
        report.fail("quantity_rules", "quantity must be decimal-compatible", collection, _record_id(collection, record), field)
    elif value <= 0:
        report.fail("quantity_rules", "quantity must be positive", collection, _record_id(collection, record), field)


def _check_non_negative_quantity(report: ValidationReport, collection: str, record: dict[str, Any], field: str) -> None:
    value = _decimal(record.get(field))
    if value is None:
        report.fail("quantity_rules", "quantity must be decimal-compatible", collection, _record_id(collection, record), field)
    elif value < 0:
        report.fail("quantity_rules", "quantity must be non-negative", collection, _record_id(collection, record), field)


def _check_line_total(report: ValidationReport, collection: str, record: dict[str, Any], qty_field: str, price_field: str, total_field: str) -> None:
    qty = _decimal(record.get(qty_field))
    price = _decimal(record.get(price_field))
    total = _decimal(record.get(total_field))
    if qty is None or price is None or total is None:
        return
    expected = (qty * price).quantize(Decimal("0.01"))
    if total != expected:
        report.fail("monetary_rules", "line_total does not equal quantity times unit_price", collection, _record_id(collection, record), total_field)


def _check_iso_date(report: ValidationReport, collection: str, record: dict[str, Any], field: str, optional: bool = False) -> None:
    value = record.get(field)
    if value is None and optional:
        return
    if not isinstance(value, str):
        report.fail("date_rules", "date must be a string", collection, _record_id(collection, record), field)
        return
    try:
        normalize_date(value)
    except ValueError:
        report.fail("date_rules", "date must be ISO format", collection, _record_id(collection, record), field)


def _check_currency(report: ValidationReport, collection: str, record: dict[str, Any], field: str) -> None:
    value = record.get(field)
    if not isinstance(value, str) or normalize_currency_code(value) != value or len(value) != 3:
        report.fail("field_domain", "currency must be a three-letter uppercase code", collection, _record_id(collection, record), field)


def _valid_dates(first: Any, second: Any) -> bool:
    try:
        if first is None or second is None:
            return False
        date.fromisoformat(first)
        date.fromisoformat(second)
        return True
    except (TypeError, ValueError):
        return False


def _sum_children(payload: dict[str, Any], collection: str, parent_field: str) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for record in _records(payload, collection):
        parent_id = record.get(parent_field)
        total = _decimal(record.get("line_total"))
        if isinstance(parent_id, str) and total is not None:
            totals[parent_id] = totals.get(parent_id, Decimal("0.00")) + total
    return totals


def _require_refs(
    report: ValidationReport,
    payload: dict[str, Any],
    collection: str,
    field: str,
    valid_ids: set[str],
    optional: bool = False,
) -> None:
    for record in _records(payload, collection):
        value = record.get(field)
        if value is None and optional:
            continue
        if value not in valid_ids:
            report.fail("reference_integrity", "reference does not exist", collection, _record_id(collection, record), field)


def _require_list_refs(
    report: ValidationReport,
    payload: dict[str, Any],
    collection: str,
    field: str,
    valid_ids: set[str],
) -> None:
    for record in _records(payload, collection):
        values = record.get(field)
        if not isinstance(values, list):
            continue
        for value in values:
            if value not in valid_ids:
                report.fail("reference_integrity", f"reference does not exist: {value}", collection, _record_id(collection, record), field)


def _mark_passes(report: ValidationReport) -> None:
    checks = (
        "top_level",
        "required_fields",
        "field_types",
        "id_presence",
        "id_uniqueness",
        "field_domain",
        "quantity_rules",
        "monetary_rules",
        "date_rules",
        "reference_integrity",
        "synthetic_only",
        "metadata",
    )
    failed_checks = {issue.check for issue in report.failures}
    for check in checks:
        if check not in failed_checks:
            report.pass_check(check)
