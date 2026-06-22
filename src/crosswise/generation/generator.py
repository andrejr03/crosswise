"""Deterministic synthetic data generator for Slice 1."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from crosswise.schemas.models import (
    DISCREPANCY_LABELS,
    DiscrepancyLabel,
    DocumentBundle,
    Invoice,
    InvoiceLine,
    PurchaseOrder,
    PurchaseOrderLine,
    Receipt,
    ReceiptLine,
    SKU,
    Supplier,
    line_total,
    money,
    quantity,
    to_plain_data,
)

FIXTURE_VERSION = "v1.0"
GENERATOR_VERSION = "crosswise_synthetic_generator_v1"
DEFAULT_SEED = 42017
SCHEMA_CONTRACT_VERSION = "slice_0_v1.0"
DISCREPANCY_TAXONOMY_VERSION = "v1.0"

SCENARIOS: tuple[str, ...] = DISCREPANCY_LABELS


@dataclass(frozen=True)
class FixtureSet:
    metadata: dict[str, Any]
    suppliers: list[Supplier]
    skus: list[SKU]
    purchase_orders: list[PurchaseOrder]
    purchase_order_lines: list[PurchaseOrderLine]
    invoices: list[Invoice]
    invoice_lines: list[InvoiceLine]
    receipts: list[Receipt]
    receipt_lines: list[ReceiptLine]
    document_bundles: list[DocumentBundle]
    discrepancy_labels: list[DiscrepancyLabel]
    ground_truth: dict[str, Any]

    def synthetic_payload(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata,
            "suppliers": to_plain_data(self.suppliers),
            "skus": to_plain_data(self.skus),
            "purchase_orders": to_plain_data(self.purchase_orders),
            "purchase_order_lines": to_plain_data(self.purchase_order_lines),
            "invoices": to_plain_data(self.invoices),
            "invoice_lines": to_plain_data(self.invoice_lines),
            "receipts": to_plain_data(self.receipts),
            "receipt_lines": to_plain_data(self.receipt_lines),
            "document_bundles": to_plain_data(self.document_bundles),
            "discrepancy_labels": to_plain_data(self.discrepancy_labels),
        }

    def ground_truth_payload(self) -> dict[str, Any]:
        return self.ground_truth


def generate_fixture_set(seed: int = DEFAULT_SEED) -> FixtureSet:
    rng = random.Random(seed)
    metadata = {
        "fixture_version": FIXTURE_VERSION,
        "generator_version": GENERATOR_VERSION,
        "seed": seed,
        "schema_contract_version": SCHEMA_CONTRACT_VERSION,
        "discrepancy_taxonomy_version": DISCREPANCY_TAXONOMY_VERSION,
        "synthetic_only": True,
    }

    suppliers: list[Supplier] = []
    skus: list[SKU] = []
    purchase_orders: list[PurchaseOrder] = []
    purchase_order_lines: list[PurchaseOrderLine] = []
    invoices: list[Invoice] = []
    invoice_lines: list[InvoiceLine] = []
    receipts: list[Receipt] = []
    receipt_lines: list[ReceiptLine] = []
    bundles: list[DocumentBundle] = []
    labels: list[DiscrepancyLabel] = []
    truth_bundles: dict[str, Any] = {}

    for index, scenario in enumerate(SCENARIOS, start=1):
        records = _build_scenario(index=index, scenario=scenario, seed=seed, rng=rng)
        suppliers.append(records["supplier"])
        skus.extend(records["skus"])
        purchase_orders.append(records["purchase_order"])
        purchase_order_lines.extend(records["purchase_order_lines"])
        invoices.extend(records["invoices"])
        invoice_lines.extend(records["invoice_lines"])
        receipts.extend(records["receipts"])
        receipt_lines.extend(records["receipt_lines"])
        bundles.append(records["bundle"])
        labels.extend(records["labels"])
        truth_bundles[records["bundle"].bundle_id] = records["ground_truth"]

    ground_truth = {
        "metadata": metadata,
        "bundles": truth_bundles,
    }

    return FixtureSet(
        metadata=metadata,
        suppliers=suppliers,
        skus=skus,
        purchase_orders=purchase_orders,
        purchase_order_lines=purchase_order_lines,
        invoices=invoices,
        invoice_lines=invoice_lines,
        receipts=receipts,
        receipt_lines=receipt_lines,
        document_bundles=bundles,
        discrepancy_labels=labels,
        ground_truth=ground_truth,
    )


def write_fixture_set(
    fixture_set: FixtureSet,
    synthetic_dir: Path,
    ground_truth_dir: Path,
) -> tuple[Path, Path]:
    synthetic_dir.mkdir(parents=True, exist_ok=True)
    ground_truth_dir.mkdir(parents=True, exist_ok=True)
    synthetic_path = synthetic_dir / "fixtures_v1_0.json"
    ground_truth_path = ground_truth_dir / "ground_truth_v1_0.json"
    synthetic_path.write_text(
        json.dumps(fixture_set.synthetic_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    ground_truth_path.write_text(
        json.dumps(fixture_set.ground_truth_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return synthetic_path, ground_truth_path


def _build_scenario(index: int, scenario: str, seed: int, rng: random.Random) -> dict[str, Any]:
    slug = scenario
    bundle_id = f"bundle_{slug}_{index:03d}"
    supplier = Supplier(
        supplier_id=f"sup_{index:03d}",
        canonical_name=f"Synthetic Supplier {index:03d}",
        aliases=[f"Syn Supplier {index:03d}", f"Synth Vendor {index:03d}"],
        country_code="DE",
        tax_region="SYNTHETIC",
        metadata=f"{scenario}_scenario",
    )
    sku_a = SKU(
        sku_id=f"sku_{index:03d}_a",
        canonical_name=f"Synthetic Item {index:03d} Alpha",
        aliases=[f"Item {index:03d} A"],
        unit_of_measure="each",
        category="synthetic_parts",
        standard_unit_price=money(10 + index + rng.randint(0, 5)),
    )
    sku_b = SKU(
        sku_id=f"sku_{index:03d}_b",
        canonical_name=f"Synthetic Item {index:03d} Beta",
        aliases=[f"Item {index:03d} B"],
        unit_of_measure="each",
        category="synthetic_parts",
        standard_unit_price=money(18 + index + rng.randint(0, 5)),
    )

    issue_date = date(2026, 1, 1) + timedelta(days=index + (seed % 11))
    expected_receipt_date = issue_date + timedelta(days=7)
    invoice_date = issue_date + timedelta(days=1)
    receipt_date = issue_date + timedelta(days=5)
    if scenario == "late_receipt":
        receipt_date = expected_receipt_date + timedelta(days=4)

    po_id = f"po_{index:03d}"
    inv_id = f"inv_{index:03d}_a"
    receipt_id = f"rcpt_{index:03d}"

    qty_a = quantity(5 + rng.randint(0, 4))
    qty_b = quantity(2 + rng.randint(0, 3))
    price_a = sku_a.standard_unit_price or money("10.00")
    price_b = sku_b.standard_unit_price or money("18.00")

    po_lines = [
        PurchaseOrderLine(
            po_line_id=f"po_line_{index:03d}_001",
            purchase_order_id=po_id,
            line_number=1,
            sku_id=sku_a.sku_id,
            description=sku_a.canonical_name,
            quantity_ordered=qty_a,
            unit_of_measure="each",
            unit_price=price_a,
            line_total=line_total(qty_a, price_a),
        ),
        PurchaseOrderLine(
            po_line_id=f"po_line_{index:03d}_002",
            purchase_order_id=po_id,
            line_number=2,
            sku_id=sku_b.sku_id,
            description=sku_b.canonical_name,
            quantity_ordered=qty_b,
            unit_of_measure="each",
            unit_price=price_b,
            line_total=line_total(qty_b, price_b),
        ),
    ]
    po_subtotal = sum((line.line_total for line in po_lines), Decimal("0.00"))
    purchase_order = PurchaseOrder(
        purchase_order_id=po_id,
        bundle_id=bundle_id,
        supplier_id=supplier.supplier_id,
        issue_date=issue_date.isoformat(),
        expected_receipt_date=expected_receipt_date.isoformat(),
        currency="EUR",
        status="issued",
        line_ids=[line.po_line_id for line in po_lines],
        subtotal=po_subtotal,
        tax_amount=money("0.00"),
        total_amount=po_subtotal,
    )

    invoice_qty_a = qty_a
    invoice_qty_b = qty_b
    invoice_price_a = price_a
    invoice_price_b = price_b
    invoice_sku_a: str | None = sku_a.sku_id
    invoice_sku_raw_a = sku_a.canonical_name
    invoice_line_specs = [
        (sku_a, invoice_qty_a, invoice_price_a, invoice_sku_a, invoice_sku_raw_a),
        (sku_b, invoice_qty_b, invoice_price_b, sku_b.sku_id, sku_b.canonical_name),
    ]

    receipt_qty_a = qty_a
    receipt_qty_b = qty_b
    receipt_line_specs = [
        (sku_a, receipt_qty_a, sku_a.sku_id, sku_a.canonical_name),
        (sku_b, receipt_qty_b, sku_b.sku_id, sku_b.canonical_name),
    ]

    supplier_name_raw = supplier.canonical_name
    expected_route = "needs_review"
    severity = "medium"
    affected_documents = [po_id, inv_id, receipt_id]
    affected_lines = [po_lines[0].po_line_id]
    expected_evidence = "Generated scenario requires human review."
    explanation = ""

    if scenario == "clean_match":
        expected_route = "auto_accept"
        severity = "none"
        affected_documents = [po_id, inv_id, receipt_id]
        affected_lines = []
        expected_evidence = "PO, invoice, and receipt lines agree exactly."
        explanation = "All generated quantities, prices, suppliers, and receipt lines match."
    elif scenario == "quantity_mismatch":
        invoice_qty_a = qty_a + quantity(1)
        invoice_line_specs[0] = (sku_a, invoice_qty_a, invoice_price_a, invoice_sku_a, invoice_sku_raw_a)
        expected_evidence = "Invoice quantity differs from ordered and received quantity."
        explanation = "Invoice line 1 quantity is intentionally higher than PO and receipt."
    elif scenario == "unit_price_mismatch":
        invoice_price_a = price_a + money("2.00")
        invoice_line_specs[0] = (sku_a, invoice_qty_a, invoice_price_a, invoice_sku_a, invoice_sku_raw_a)
        expected_evidence = "Invoice unit price differs from purchase order unit price."
        explanation = "Invoice line 1 unit price is intentionally higher than PO."
    elif scenario == "missing_invoice_line":
        invoice_line_specs = invoice_line_specs[:1]
        affected_lines = [po_lines[1].po_line_id]
        expected_evidence = "Second PO line has no corresponding invoice line."
        explanation = "The invoice intentionally omits the second ordered SKU."
    elif scenario == "missing_receipt_line":
        receipt_line_specs = receipt_line_specs[:1]
        severity = "high"
        affected_lines = [po_lines[1].po_line_id]
        expected_evidence = "Second PO and invoice line has no corresponding receipt line."
        explanation = "The receipt intentionally omits delivery confirmation for the second SKU."
    elif scenario == "duplicate_invoice":
        severity = "high"
        expected_evidence = "Two invoices share the same invoice number, supplier, totals, and lines."
        explanation = "A second invoice record intentionally duplicates the first invoice."
    elif scenario == "supplier_alias_mismatch":
        supplier_name_raw = supplier.aliases[1]
        severity = "low"
        expected_evidence = "Invoice supplier name uses a controlled synthetic alias."
        explanation = "The invoice supplier name is an alias of the canonical supplier."
    elif scenario == "late_receipt":
        severity = "low"
        expected_evidence = "Receipt date is later than expected receipt date."
        explanation = "The generated receipt date is intentionally later than the PO expected date."
    elif scenario == "low_confidence_extraction":
        expected_evidence = "Synthetic extraction metadata marks invoice unit price as low confidence."
        explanation = "Source records are valid, but ground truth marks one extracted field as low confidence."
    elif scenario == "schema_validation_failure":
        expected_route = "blocked"
        severity = "high"
        expected_evidence = "Ground truth records an invalid extracted required field for later validation."
        explanation = "Source records remain valid; the simulated extraction contract is expected to block."
    else:
        raise ValueError(f"unsupported scenario: {scenario}")

    invoice_lines = _make_invoice_lines(index, inv_id, invoice_line_specs)
    invoice_subtotal = sum((line.line_total for line in invoice_lines), Decimal("0.00"))
    invoice = Invoice(
        invoice_id=inv_id,
        bundle_id=bundle_id,
        supplier_id=supplier.supplier_id,
        supplier_name_raw=supplier_name_raw,
        invoice_number=f"SYN-INV-{index:04d}",
        invoice_date=invoice_date.isoformat(),
        due_date=(invoice_date + timedelta(days=30)).isoformat(),
        currency="EUR",
        line_ids=[line.invoice_line_id for line in invoice_lines],
        subtotal=invoice_subtotal,
        tax_amount=money("0.00"),
        total_amount=invoice_subtotal,
    )
    invoices = [invoice]

    if scenario == "duplicate_invoice":
        duplicate_id = f"inv_{index:03d}_b"
        duplicate_lines = _make_invoice_lines(index, duplicate_id, invoice_line_specs, suffix="dup")
        duplicate = Invoice(
            invoice_id=duplicate_id,
            bundle_id=bundle_id,
            supplier_id=supplier.supplier_id,
            supplier_name_raw=supplier_name_raw,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
            currency="EUR",
            line_ids=[line.invoice_line_id for line in duplicate_lines],
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            total_amount=invoice.total_amount,
            duplicate_of_invoice_id=invoice.invoice_id,
        )
        invoices.append(duplicate)
        invoice_lines.extend(duplicate_lines)
        affected_documents = [po_id, inv_id, duplicate_id, receipt_id]

    receipt_lines = _make_receipt_lines(index, receipt_id, receipt_line_specs, receipt_date.isoformat())
    receipt = Receipt(
        receipt_id=receipt_id,
        bundle_id=bundle_id,
        supplier_id=supplier.supplier_id,
        supplier_name_raw=supplier.canonical_name,
        receipt_number=f"SYN-RCPT-{index:04d}",
        receipt_date=receipt_date.isoformat(),
        related_purchase_order_id=po_id,
        line_ids=[line.receipt_line_id for line in receipt_lines],
    )

    label = DiscrepancyLabel(
        label_id=f"label_{index:03d}_{scenario}",
        label_type=scenario,
        bundle_id=bundle_id,
        affected_document_ids=affected_documents,
        affected_line_ids=affected_lines,
        severity_default=severity,
        expected_evidence=expected_evidence,
        v1_requirement="optional_deferred" if scenario == "late_receipt" else "required_v1",
    )
    bundle = DocumentBundle(
        bundle_id=bundle_id,
        fixture_version=FIXTURE_VERSION,
        generator_version=GENERATOR_VERSION,
        seed=seed,
        scenario_name=scenario.replace("_", " "),
        supplier_id=supplier.supplier_id,
        purchase_order_id=po_id,
        invoice_ids=[item.invoice_id for item in invoices],
        receipt_ids=[receipt_id],
        discrepancy_labels=[scenario],
        expected_route=expected_route,
    )

    ground_truth = {
        "bundle_id": bundle_id,
        "scenario": scenario,
        "expected_route": expected_route,
        "expected_labels": [scenario],
        "severity_default": severity,
        "expected_document_matches": {
            "purchase_order_id": po_id,
            "invoice_ids": [item.invoice_id for item in invoices],
            "receipt_ids": [receipt_id],
            "supplier_id": supplier.supplier_id,
        },
        "expected_line_matches": _expected_line_matches(po_lines, invoice_lines, receipt_lines, scenario),
        "expected_evidence": expected_evidence,
        "explanation": explanation,
        "simulated_extraction_issues": _simulated_extraction_issues(scenario, inv_id),
    }

    return {
        "supplier": supplier,
        "skus": [sku_a, sku_b],
        "purchase_order": purchase_order,
        "purchase_order_lines": po_lines,
        "invoices": invoices,
        "invoice_lines": invoice_lines,
        "receipts": [receipt],
        "receipt_lines": receipt_lines,
        "bundle": bundle,
        "labels": [label],
        "ground_truth": ground_truth,
    }


def _make_invoice_lines(
    index: int,
    invoice_id: str,
    specs: list[tuple[SKU, Decimal, Decimal, str | None, str]],
    suffix: str = "main",
) -> list[InvoiceLine]:
    lines = []
    for line_number, (sku, qty, unit_price, sku_id, sku_raw) in enumerate(specs, start=1):
        lines.append(
            InvoiceLine(
                invoice_line_id=f"inv_line_{index:03d}_{suffix}_{line_number:03d}",
                invoice_id=invoice_id,
                line_number=line_number,
                sku_id=sku_id,
                sku_raw=sku_raw,
                description=sku.canonical_name,
                quantity_billed=qty,
                unit_of_measure=sku.unit_of_measure,
                unit_price=unit_price,
                line_total=line_total(qty, unit_price),
            )
        )
    return lines


def _make_receipt_lines(
    index: int,
    receipt_id: str,
    specs: list[tuple[SKU, Decimal, str | None, str]],
    receipt_date: str,
) -> list[ReceiptLine]:
    lines = []
    for line_number, (sku, qty, sku_id, sku_raw) in enumerate(specs, start=1):
        lines.append(
            ReceiptLine(
                receipt_line_id=f"rcpt_line_{index:03d}_{line_number:03d}",
                receipt_id=receipt_id,
                line_number=line_number,
                sku_id=sku_id,
                sku_raw=sku_raw,
                quantity_received=qty,
                unit_of_measure=sku.unit_of_measure,
                received_date=receipt_date,
            )
        )
    return lines


def _expected_line_matches(
    po_lines: list[PurchaseOrderLine],
    invoice_lines: list[InvoiceLine],
    receipt_lines: list[ReceiptLine],
    scenario: str,
) -> list[dict[str, Any]]:
    invoice_by_sku = {line.sku_id: line.invoice_line_id for line in invoice_lines if line.sku_id}
    receipt_by_sku = {line.sku_id: line.receipt_line_id for line in receipt_lines if line.sku_id}
    matches = []
    for po_line in po_lines:
        matches.append(
            {
                "po_line_id": po_line.po_line_id,
                "invoice_line_id": invoice_by_sku.get(po_line.sku_id),
                "receipt_line_id": receipt_by_sku.get(po_line.sku_id),
                "expected_label": scenario if scenario != "clean_match" else "clean_match",
            }
        )
    return matches


def _simulated_extraction_issues(scenario: str, invoice_id: str) -> list[dict[str, str]]:
    if scenario == "low_confidence_extraction":
        return [
            {
                "source_document_id": invoice_id,
                "field_name": "unit_price",
                "issue_type": "low_confidence_extraction",
                "expected_route": "needs_review",
            }
        ]
    if scenario == "schema_validation_failure":
        return [
            {
                "source_document_id": invoice_id,
                "field_name": "invoice_number",
                "issue_type": "schema_validation_failure",
                "expected_route": "blocked",
            }
        ]
    return []
