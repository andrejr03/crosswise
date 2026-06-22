from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from crosswise.generation import generate_fixture_set
from crosswise.reconciliation import reconcile_fixture_payload


def _result() -> dict:
    fixture_set = generate_fixture_set()
    return reconcile_fixture_payload(
        fixture_set.synthetic_payload(),
        fixture_set.ground_truth_payload(),
    )


def _cases_by_bundle(result: dict) -> dict[str, dict]:
    return {case["bundle_id"]: case for case in result["cases"]}


def test_script_runs_successfully_and_creates_output_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable, "scripts/generate_synthetic_data.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    completed = subprocess.run(
        [sys.executable, "scripts/run_reconciliation.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )

    output_path = repo_root / "data" / "reconciliation" / "reconciliation_v1_0.json"
    assert "Bundles reconciled: 10" in completed.stdout
    assert output_path.is_file()


def test_every_generated_bundle_produces_one_reconciliation_case() -> None:
    fixture_set = generate_fixture_set()
    result = reconcile_fixture_payload(fixture_set.synthetic_payload(), fixture_set.ground_truth_payload())

    assert result["summary"]["bundles_reconciled"] == len(fixture_set.synthetic_payload()["document_bundles"])
    assert len(result["cases"]) == len(fixture_set.synthetic_payload()["document_bundles"])


def test_clean_match_produces_no_non_clean_discrepancy_labels() -> None:
    case = _cases_by_bundle(_result())["bundle_clean_match_001"]

    assert case["discrepancy_labels"] == ["clean_match"]
    assert case["route"] == "auto_accept"
    assert case["evidence"] == []


def test_required_baseline_discrepancies_are_detected() -> None:
    cases = _cases_by_bundle(_result())

    expected = {
        "bundle_quantity_mismatch_002": "quantity_mismatch",
        "bundle_unit_price_mismatch_003": "unit_price_mismatch",
        "bundle_missing_invoice_line_004": "missing_invoice_line",
        "bundle_missing_receipt_line_005": "missing_receipt_line",
        "bundle_duplicate_invoice_006": "duplicate_invoice",
        "bundle_supplier_alias_mismatch_007": "supplier_alias_mismatch",
        "bundle_late_receipt_008": "late_receipt",
        "bundle_low_confidence_extraction_009": "low_confidence_extraction",
        "bundle_schema_validation_failure_010": "schema_validation_failure",
    }

    for bundle_id, label in expected.items():
        assert label in cases[bundle_id]["discrepancy_labels"]


def test_low_confidence_extraction_is_represented_without_confidence_scoring() -> None:
    case = _cases_by_bundle(_result())["bundle_low_confidence_extraction_009"]

    assert case["confidence_score"] is None
    assert case["confidence_note"] == "Slice 3 does not implement confidence scoring."
    assert any(item["label"] == "low_confidence_extraction" for item in case["evidence"])


def test_evidence_exists_for_each_non_clean_detected_discrepancy() -> None:
    for case in _result()["cases"]:
        non_clean = [label for label in case["discrepancy_labels"] if label != "clean_match"]
        for label in non_clean:
            matching = [item for item in case["evidence"] if item["label"] == label]
            assert matching, (case["bundle_id"], label)
            for item in matching:
                assert item["affected_document_ids"]
                assert "observed_values" in item
                assert "normalized_values" in item
                assert item["detection_basis"]
                assert item["explanation"]


def test_routes_follow_deterministic_baseline_defaults() -> None:
    cases = _cases_by_bundle(_result())

    assert cases["bundle_clean_match_001"]["route"] == "auto_accept"
    assert cases["bundle_schema_validation_failure_010"]["route"] == "blocked"
    for bundle_id, case in cases.items():
        if bundle_id not in {"bundle_clean_match_001", "bundle_schema_validation_failure_010"}:
            assert case["route"] == "needs_review"


def test_output_is_deterministic_across_repeated_runs() -> None:
    first = _result()
    second = _result()

    assert first == second


def test_reconciliation_output_file_is_deterministic_across_script_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output_path = repo_root / "data" / "reconciliation" / "reconciliation_v1_0.json"
    subprocess.run([sys.executable, "scripts/generate_synthetic_data.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    first = json.loads(output_path.read_text(encoding="utf-8"))
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    second = json.loads(output_path.read_text(encoding="utf-8"))

    assert first == second
