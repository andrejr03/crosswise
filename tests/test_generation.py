from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from crosswise.generation import DEFAULT_SEED, generate_fixture_set
from crosswise.schemas.models import DISCREPANCY_LABELS, line_total


FORBIDDEN_STRINGS = (
    "gmail",
    "hotmail",
    "iban",
    "swift",
    "bank account",
    "tax id",
    "vat id",
    "acme",
    "google",
    "microsoft",
    "amazon",
    "apple",
)


def payload(seed: int = DEFAULT_SEED) -> dict:
    return generate_fixture_set(seed=seed).synthetic_payload()


def ground_truth(seed: int = DEFAULT_SEED) -> dict:
    return generate_fixture_set(seed=seed).ground_truth_payload()


def test_generation_is_deterministic_for_same_seed() -> None:
    first = generate_fixture_set(seed=1234)
    second = generate_fixture_set(seed=1234)

    assert first.synthetic_payload() == second.synthetic_payload()
    assert first.ground_truth_payload() == second.ground_truth_payload()


def test_different_seed_produces_controlled_different_output() -> None:
    first = payload(seed=1234)
    second = payload(seed=5678)

    assert first["metadata"]["fixture_version"] == second["metadata"]["fixture_version"]
    assert first["metadata"]["generator_version"] == second["metadata"]["generator_version"]
    assert first["metadata"]["seed"] != second["metadata"]["seed"]
    assert first != second


def test_generated_ids_are_unique_where_required() -> None:
    data = payload()
    id_fields = {
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

    for collection, id_field in id_fields.items():
        values = [record[id_field] for record in data[collection]]
        assert len(values) == len(set(values)), collection


def test_references_are_valid() -> None:
    data = payload()
    supplier_ids = {item["supplier_id"] for item in data["suppliers"]}
    sku_ids = {item["sku_id"] for item in data["skus"]}
    po_ids = {item["purchase_order_id"] for item in data["purchase_orders"]}
    po_line_ids = {item["po_line_id"] for item in data["purchase_order_lines"]}
    invoice_ids = {item["invoice_id"] for item in data["invoices"]}
    invoice_line_ids = {item["invoice_line_id"] for item in data["invoice_lines"]}
    receipt_ids = {item["receipt_id"] for item in data["receipts"]}
    receipt_line_ids = {item["receipt_line_id"] for item in data["receipt_lines"]}
    bundle_ids = {item["bundle_id"] for item in data["document_bundles"]}

    for sku in data["skus"]:
        assert sku["standard_unit_price"] is None or Decimal(sku["standard_unit_price"]) >= 0

    for po in data["purchase_orders"]:
        assert po["bundle_id"] in bundle_ids
        assert po["supplier_id"] in supplier_ids
        assert set(po["line_ids"]).issubset(po_line_ids)

    for line in data["purchase_order_lines"]:
        assert line["purchase_order_id"] in po_ids
        assert line["sku_id"] in sku_ids

    for invoice in data["invoices"]:
        assert invoice["bundle_id"] in bundle_ids
        assert invoice["supplier_id"] in supplier_ids
        assert set(invoice["line_ids"]).issubset(invoice_line_ids)
        if invoice["duplicate_of_invoice_id"] is not None:
            assert invoice["duplicate_of_invoice_id"] in invoice_ids

    for line in data["invoice_lines"]:
        assert line["invoice_id"] in invoice_ids
        assert line["sku_id"] is None or line["sku_id"] in sku_ids

    for receipt in data["receipts"]:
        assert receipt["bundle_id"] in bundle_ids
        assert receipt["supplier_id"] in supplier_ids
        assert receipt["related_purchase_order_id"] in po_ids
        assert set(receipt["line_ids"]).issubset(receipt_line_ids)

    for line in data["receipt_lines"]:
        assert line["receipt_id"] in receipt_ids
        assert line["sku_id"] is None or line["sku_id"] in sku_ids

    for bundle in data["document_bundles"]:
        assert bundle["supplier_id"] in supplier_ids
        assert bundle["purchase_order_id"] in po_ids
        assert set(bundle["invoice_ids"]).issubset(invoice_ids)
        assert set(bundle["receipt_ids"]).issubset(receipt_ids)

    for label in data["discrepancy_labels"]:
        assert label["bundle_id"] in bundle_ids


def test_no_forbidden_entity_strings_appear() -> None:
    serialized = json.dumps(payload(), sort_keys=True).lower()

    for forbidden in FORBIDDEN_STRINGS:
        assert forbidden not in serialized
    assert "@" not in serialized


def test_every_generated_bundle_has_ground_truth() -> None:
    data = payload()
    truth = ground_truth()
    bundle_ids = {bundle["bundle_id"] for bundle in data["document_bundles"]}

    assert set(truth["bundles"]) == bundle_ids
    for bundle_id in bundle_ids:
        assert truth["bundles"][bundle_id]["bundle_id"] == bundle_id
        assert truth["bundles"][bundle_id]["expected_labels"]


def test_every_discrepancy_label_uses_frozen_taxonomy() -> None:
    data = payload()
    labels = {label["label_type"] for label in data["discrepancy_labels"]}

    assert labels == set(DISCREPANCY_LABELS)
    for bundle in data["document_bundles"]:
        assert set(bundle["discrepancy_labels"]).issubset(DISCREPANCY_LABELS)


def test_clean_match_bundle_has_no_contradictory_non_clean_labels() -> None:
    data = payload()
    clean_bundles = [
        bundle
        for bundle in data["document_bundles"]
        if "clean_match" in bundle["discrepancy_labels"]
    ]

    assert len(clean_bundles) == 1
    assert clean_bundles[0]["discrepancy_labels"] == ["clean_match"]


def test_generated_monetary_totals_are_arithmetically_valid() -> None:
    data = payload()

    for line in data["purchase_order_lines"]:
        assert Decimal(line["line_total"]) == line_total(
            Decimal(line["quantity_ordered"]),
            Decimal(line["unit_price"]),
        )
    for line in data["invoice_lines"]:
        assert Decimal(line["line_total"]) == line_total(
            Decimal(line["quantity_billed"]),
            Decimal(line["unit_price"]),
        )

    po_line_totals: dict[str, Decimal] = {}
    for line in data["purchase_order_lines"]:
        po_line_totals.setdefault(line["purchase_order_id"], Decimal("0.00"))
        po_line_totals[line["purchase_order_id"]] += Decimal(line["line_total"])
    for po in data["purchase_orders"]:
        assert Decimal(po["subtotal"]) == po_line_totals[po["purchase_order_id"]]
        assert Decimal(po["total_amount"]) == Decimal(po["subtotal"]) + Decimal(po["tax_amount"])

    invoice_line_totals: dict[str, Decimal] = {}
    for line in data["invoice_lines"]:
        invoice_line_totals.setdefault(line["invoice_id"], Decimal("0.00"))
        invoice_line_totals[line["invoice_id"]] += Decimal(line["line_total"])
    for invoice in data["invoices"]:
        assert Decimal(invoice["subtotal"]) == invoice_line_totals[invoice["invoice_id"]]
        assert Decimal(invoice["total_amount"]) == Decimal(invoice["subtotal"]) + Decimal(invoice["tax_amount"])


def test_generated_quantities_are_valid() -> None:
    data = payload()

    for line in data["purchase_order_lines"]:
        assert Decimal(line["quantity_ordered"]) > 0
    for line in data["invoice_lines"]:
        assert Decimal(line["quantity_billed"]) > 0
    for line in data["receipt_lines"]:
        assert Decimal(line["quantity_received"]) >= 0


def test_generated_dates_are_valid() -> None:
    data = payload()

    purchase_orders = {po["purchase_order_id"]: po for po in data["purchase_orders"]}
    for po in data["purchase_orders"]:
        issue_date = date.fromisoformat(po["issue_date"])
        expected_receipt_date = date.fromisoformat(po["expected_receipt_date"])
        assert expected_receipt_date >= issue_date

    for invoice in data["invoices"]:
        invoice_date = date.fromisoformat(invoice["invoice_date"])
        due_date = date.fromisoformat(invoice["due_date"])
        assert due_date >= invoice_date

    for receipt in data["receipts"]:
        receipt_date = date.fromisoformat(receipt["receipt_date"])
        po = purchase_orders[receipt["related_purchase_order_id"]]
        assert receipt_date >= date.fromisoformat(po["issue_date"])


def test_script_runs_successfully_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/generate_synthetic_data.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Wrote synthetic fixtures" in result.stdout
    assert (repo_root / "data" / "synthetic" / "fixtures_v1_0.json").is_file()
    assert (repo_root / "data" / "ground_truth" / "ground_truth_v1_0.json").is_file()
