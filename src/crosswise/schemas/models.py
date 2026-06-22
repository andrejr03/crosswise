"""Dataclass models for Slice 1 synthetic fixtures.

The models intentionally stay small. They validate local field shape and keep
cross-record integrity checks in the generator/test layer where all records are
available together.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from decimal import Decimal
from typing import Any


DISCREPANCY_LABELS: tuple[str, ...] = (
    "clean_match",
    "quantity_mismatch",
    "unit_price_mismatch",
    "missing_invoice_line",
    "missing_receipt_line",
    "duplicate_invoice",
    "supplier_alias_mismatch",
    "late_receipt",
    "low_confidence_extraction",
    "schema_validation_failure",
)

REQUIRED_V1_LABELS: tuple[str, ...] = (
    "clean_match",
    "quantity_mismatch",
    "unit_price_mismatch",
    "missing_invoice_line",
    "missing_receipt_line",
    "duplicate_invoice",
    "supplier_alias_mismatch",
    "low_confidence_extraction",
    "schema_validation_failure",
)

OPTIONAL_DEFERRED_LABELS: tuple[str, ...] = ("late_receipt",)

ROUTES: tuple[str, ...] = ("auto_accept", "needs_review", "blocked")
SEVERITIES: tuple[str, ...] = ("none", "low", "medium", "high")


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_non_negative(value: Decimal, field_name: str) -> None:
    if value < Decimal("0"):
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive(value: Decimal, field_name: str) -> None:
    if value <= Decimal("0"):
        raise ValueError(f"{field_name} must be positive")


def money(value: str | int | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def quantity(value: str | int | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.001")).normalize()


def line_total(qty: Decimal, unit_price: Decimal) -> Decimal:
    return (qty * unit_price).quantize(Decimal("0.01"))


def to_plain_data(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if is_dataclass(value):
        return {key: to_plain_data(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [to_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain_data(item) for key, item in value.items()}
    return value


@dataclass(frozen=True)
class Supplier:
    supplier_id: str
    canonical_name: str
    aliases: list[str] = field(default_factory=list)
    country_code: str | None = None
    tax_region: str | None = None
    metadata: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.supplier_id, "supplier_id")
        _require_non_empty(self.canonical_name, "canonical_name")
        for alias in self.aliases:
            _require_non_empty(alias, "alias")


@dataclass(frozen=True)
class SKU:
    sku_id: str
    canonical_name: str
    aliases: list[str] = field(default_factory=list)
    unit_of_measure: str = "each"
    category: str | None = None
    standard_unit_price: Decimal | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.sku_id, "sku_id")
        _require_non_empty(self.canonical_name, "canonical_name")
        _require_non_empty(self.unit_of_measure, "unit_of_measure")
        if self.standard_unit_price is not None:
            _require_non_negative(self.standard_unit_price, "standard_unit_price")


@dataclass(frozen=True)
class PurchaseOrderLine:
    po_line_id: str
    purchase_order_id: str
    line_number: int
    sku_id: str
    description: str
    quantity_ordered: Decimal
    unit_of_measure: str
    unit_price: Decimal
    line_total: Decimal

    def __post_init__(self) -> None:
        _require_non_empty(self.po_line_id, "po_line_id")
        _require_non_empty(self.purchase_order_id, "purchase_order_id")
        _require_non_empty(self.sku_id, "sku_id")
        _require_positive(Decimal(self.line_number), "line_number")
        _require_positive(self.quantity_ordered, "quantity_ordered")
        _require_non_negative(self.unit_price, "unit_price")
        if self.line_total != line_total(self.quantity_ordered, self.unit_price):
            raise ValueError("purchase order line_total must equal quantity * unit_price")


@dataclass(frozen=True)
class PurchaseOrder:
    purchase_order_id: str
    bundle_id: str
    supplier_id: str
    issue_date: str
    expected_receipt_date: str | None
    currency: str
    status: str
    line_ids: list[str]
    subtotal: Decimal
    tax_amount: Decimal | None
    total_amount: Decimal

    def __post_init__(self) -> None:
        _require_non_empty(self.purchase_order_id, "purchase_order_id")
        _require_non_empty(self.bundle_id, "bundle_id")
        _require_non_empty(self.supplier_id, "supplier_id")
        _require_non_empty(self.issue_date, "issue_date")
        _require_non_empty(self.currency, "currency")
        if not self.line_ids:
            raise ValueError("purchase order must contain line_ids")
        _require_non_negative(self.subtotal, "subtotal")
        if self.tax_amount is not None:
            _require_non_negative(self.tax_amount, "tax_amount")
        _require_non_negative(self.total_amount, "total_amount")


@dataclass(frozen=True)
class InvoiceLine:
    invoice_line_id: str
    invoice_id: str
    line_number: int
    sku_id: str | None
    sku_raw: str
    description: str
    quantity_billed: Decimal
    unit_of_measure: str
    unit_price: Decimal
    line_total: Decimal

    def __post_init__(self) -> None:
        _require_non_empty(self.invoice_line_id, "invoice_line_id")
        _require_non_empty(self.invoice_id, "invoice_id")
        _require_positive(Decimal(self.line_number), "line_number")
        _require_non_empty(self.sku_raw, "sku_raw")
        _require_positive(self.quantity_billed, "quantity_billed")
        _require_non_negative(self.unit_price, "unit_price")
        if self.line_total != line_total(self.quantity_billed, self.unit_price):
            raise ValueError("invoice line_total must equal quantity * unit_price")


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    bundle_id: str
    supplier_id: str | None
    supplier_name_raw: str
    invoice_number: str
    invoice_date: str
    due_date: str | None
    currency: str
    line_ids: list[str]
    subtotal: Decimal
    tax_amount: Decimal | None
    total_amount: Decimal
    duplicate_of_invoice_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.invoice_id, "invoice_id")
        _require_non_empty(self.bundle_id, "bundle_id")
        _require_non_empty(self.supplier_name_raw, "supplier_name_raw")
        _require_non_empty(self.invoice_number, "invoice_number")
        _require_non_empty(self.invoice_date, "invoice_date")
        _require_non_empty(self.currency, "currency")
        if not self.line_ids:
            raise ValueError("invoice must contain line_ids")
        _require_non_negative(self.subtotal, "subtotal")
        if self.tax_amount is not None:
            _require_non_negative(self.tax_amount, "tax_amount")
        _require_non_negative(self.total_amount, "total_amount")


@dataclass(frozen=True)
class ReceiptLine:
    receipt_line_id: str
    receipt_id: str
    line_number: int
    sku_id: str | None
    sku_raw: str
    quantity_received: Decimal
    unit_of_measure: str
    received_date: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.receipt_line_id, "receipt_line_id")
        _require_non_empty(self.receipt_id, "receipt_id")
        _require_positive(Decimal(self.line_number), "line_number")
        _require_non_empty(self.sku_raw, "sku_raw")
        _require_non_negative(self.quantity_received, "quantity_received")


@dataclass(frozen=True)
class Receipt:
    receipt_id: str
    bundle_id: str
    supplier_id: str | None
    supplier_name_raw: str | None
    receipt_number: str
    receipt_date: str
    related_purchase_order_id: str | None
    line_ids: list[str]

    def __post_init__(self) -> None:
        _require_non_empty(self.receipt_id, "receipt_id")
        _require_non_empty(self.bundle_id, "bundle_id")
        _require_non_empty(self.receipt_number, "receipt_number")
        _require_non_empty(self.receipt_date, "receipt_date")
        if not self.line_ids:
            raise ValueError("receipt must contain line_ids")


@dataclass(frozen=True)
class DiscrepancyLabel:
    label_id: str
    label_type: str
    bundle_id: str
    affected_document_ids: list[str]
    affected_line_ids: list[str]
    severity_default: str
    expected_evidence: str
    v1_requirement: str

    def __post_init__(self) -> None:
        _require_non_empty(self.label_id, "label_id")
        if self.label_type not in DISCREPANCY_LABELS:
            raise ValueError(f"unsupported discrepancy label: {self.label_type}")
        _require_non_empty(self.bundle_id, "bundle_id")
        if self.severity_default not in SEVERITIES:
            raise ValueError(f"unsupported severity: {self.severity_default}")
        if self.v1_requirement not in {"required_v1", "optional_deferred"}:
            raise ValueError("v1_requirement must be required_v1 or optional_deferred")
        _require_non_empty(self.expected_evidence, "expected_evidence")


@dataclass(frozen=True)
class DocumentBundle:
    bundle_id: str
    fixture_version: str
    generator_version: str
    seed: int
    scenario_name: str
    supplier_id: str
    purchase_order_id: str
    invoice_ids: list[str]
    receipt_ids: list[str]
    discrepancy_labels: list[str]
    expected_route: str

    def __post_init__(self) -> None:
        _require_non_empty(self.bundle_id, "bundle_id")
        _require_non_empty(self.fixture_version, "fixture_version")
        _require_non_empty(self.generator_version, "generator_version")
        _require_non_empty(self.scenario_name, "scenario_name")
        _require_non_empty(self.supplier_id, "supplier_id")
        _require_non_empty(self.purchase_order_id, "purchase_order_id")
        if not self.invoice_ids:
            raise ValueError("bundle must contain invoice_ids")
        if not self.discrepancy_labels:
            raise ValueError("bundle must contain discrepancy_labels")
        if self.expected_route not in ROUTES:
            raise ValueError(f"unsupported expected route: {self.expected_route}")
        unknown = set(self.discrepancy_labels) - set(DISCREPANCY_LABELS)
        if unknown:
            raise ValueError(f"unsupported discrepancy labels: {sorted(unknown)}")
        if "clean_match" in self.discrepancy_labels and len(self.discrepancy_labels) > 1:
            raise ValueError("clean_match cannot be combined with non-clean labels")
