from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

from crosswise.generation import generate_fixture_set
from crosswise.normalization import (
    normalize_currency_code,
    normalize_date,
    normalize_sku_text,
    normalize_supplier_aliases,
    normalize_supplier_name,
    normalize_text,
)
from crosswise.validation import validate_fixture_payload


def valid_payload() -> dict:
    return generate_fixture_set().synthetic_payload()


def test_valid_fixture_set_passes() -> None:
    report = validate_fixture_payload(valid_payload())

    assert report.is_valid
    assert report.passed_checks
    assert not report.failures


def test_broken_required_field_fails() -> None:
    data = valid_payload()
    del data["suppliers"][0]["canonical_name"]

    report = validate_fixture_payload(data)

    assert not report.is_valid
    assert any(issue.check == "required_fields" and issue.field == "canonical_name" for issue in report.failures)


def test_duplicate_ids_fail() -> None:
    data = valid_payload()
    data["suppliers"][1]["supplier_id"] = data["suppliers"][0]["supplier_id"]

    report = validate_fixture_payload(data)

    assert not report.is_valid
    assert any(issue.check == "id_uniqueness" for issue in report.failures)


def test_invalid_references_fail() -> None:
    data = valid_payload()
    data["purchase_order_lines"][0]["sku_id"] = "sku_missing"

    report = validate_fixture_payload(data)

    assert not report.is_valid
    assert any(issue.check == "reference_integrity" and issue.field == "sku_id" for issue in report.failures)


def test_invalid_quantities_fail() -> None:
    data = valid_payload()
    data["invoice_lines"][0]["quantity_billed"] = "0"

    report = validate_fixture_payload(data)

    assert not report.is_valid
    assert any(issue.check == "quantity_rules" and issue.field == "quantity_billed" for issue in report.failures)


def test_invalid_monetary_values_fail() -> None:
    data = valid_payload()
    data["purchase_order_lines"][0]["unit_price"] = "-1.00"

    report = validate_fixture_payload(data)

    assert not report.is_valid
    assert any(issue.check == "monetary_rules" and issue.field == "unit_price" for issue in report.failures)


def test_invalid_dates_fail() -> None:
    data = valid_payload()
    data["purchase_orders"][0]["expected_receipt_date"] = "2020-99-99"

    report = validate_fixture_payload(data)

    assert not report.is_valid
    assert any(issue.check == "date_rules" and issue.field == "expected_receipt_date" for issue in report.failures)


def test_normalization_behavior() -> None:
    assert normalize_text("  Alpha\t Beta  ") == "alpha beta"
    assert normalize_supplier_name("  Example Components, Ltd. ") == "example components"
    assert normalize_supplier_aliases([" Vendor LLC ", "vendor"]) == ["vendor"]
    assert normalize_sku_text(" Sensor-Bracket / A ") == "sensor bracket a"
    assert normalize_currency_code(" eur ") == "EUR"
    assert normalize_date("2026-02-03") == "2026-02-03"


def test_synthetic_only_policy_checks() -> None:
    data = valid_payload()
    data["suppliers"][0]["canonical_name"] = "Example Gmail Supplier"

    report = validate_fixture_payload(data)

    assert not report.is_valid
    assert any(issue.check == "synthetic_only" for issue in report.failures)


def test_script_runs_successfully_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable, "scripts/generate_synthetic_data.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    result = subprocess.run(
        [sys.executable, "scripts/validate_fixtures.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Validation passed." in result.stdout


def test_validation_does_not_mutate_payload() -> None:
    data = valid_payload()
    before = copy.deepcopy(data)

    validate_fixture_payload(data)

    assert data == before
