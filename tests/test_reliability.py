from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from crosswise.confidence import score_reconciliation
from crosswise.evaluation import evaluate_reconciliation
from crosswise.generation import generate_fixture_set
from crosswise.reconciliation import reconcile_fixture_payload
from crosswise.routing import NON_ADVICE_REMINDER


def _result() -> dict:
    fixture_set = generate_fixture_set()
    reconciliation = reconcile_fixture_payload(
        fixture_set.synthetic_payload(),
        fixture_set.ground_truth_payload(),
    )
    evaluation = evaluate_reconciliation(reconciliation, fixture_set.ground_truth_payload())
    return score_reconciliation(reconciliation, evaluation)


def _cases_by_bundle(result: dict) -> dict[str, dict]:
    return {case["bundle_id"]: case for case in result["cases"]}


def test_reliability_script_runs_and_creates_output() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "scripts/generate_synthetic_data.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/evaluate_reconciliation.py"], cwd=repo_root, check=True)
    completed = subprocess.run(
        [sys.executable, "scripts/score_reliability.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    output_path = repo_root / "data" / "reliability" / "reliability_v1_0.json"

    assert "Cases scored: 10" in completed.stdout
    assert output_path.is_file()


def test_every_case_receives_confidence_score_within_range() -> None:
    result = _result()

    assert result["summary"]["cases_scored"] == 10
    for case in result["cases"]:
        assert isinstance(case["confidence_score"], float)
        assert 0.0 <= case["confidence_score"] <= 1.0


def test_clean_match_routes_to_auto_accept_when_evidence_is_present() -> None:
    case = _cases_by_bundle(_result())["bundle_clean_match_001"]

    assert case["reliability_route"] == "auto_accept"
    assert case["evidence_completeness"]["complete"] is True


def test_schema_validation_failure_routes_to_blocked() -> None:
    case = _cases_by_bundle(_result())["bundle_schema_validation_failure_010"]

    assert case["reliability_route"] == "blocked"
    assert case["blocked_reason"] == "schema_validation_failure"


def test_low_confidence_extraction_routes_to_needs_review() -> None:
    case = _cases_by_bundle(_result())["bundle_low_confidence_extraction_009"]

    assert case["reliability_route"] == "needs_review"
    assert "low_confidence_extraction" in case["discrepancy_labels"]


def test_mismatch_and_reviewable_labels_route_to_needs_review() -> None:
    cases = _cases_by_bundle(_result())
    reviewable = {
        "bundle_quantity_mismatch_002",
        "bundle_unit_price_mismatch_003",
        "bundle_missing_invoice_line_004",
        "bundle_missing_receipt_line_005",
        "bundle_duplicate_invoice_006",
        "bundle_supplier_alias_mismatch_007",
        "bundle_late_receipt_008",
    }

    for bundle_id in reviewable:
        assert cases[bundle_id]["reliability_route"] == "needs_review"


def test_confidence_scoring_is_deterministic() -> None:
    first = _result()
    second = _result()

    assert first == second


def test_confidence_scoring_does_not_require_model_calls() -> None:
    case = _result()["cases"][0]
    factor = next(item for item in case["confidence_factors"] if item["name"] == "model_self_reported_confidence")

    assert factor["value"] == "not_used"


def test_reliability_output_includes_non_advice_reminder() -> None:
    for case in _result()["cases"]:
        assert case["non_advice_reminder"] == NON_ADVICE_REMINDER


def test_reliability_output_is_deterministic_across_script_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output_path = repo_root / "data" / "reliability" / "reliability_v1_0.json"
    subprocess.run([sys.executable, "scripts/generate_synthetic_data.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/evaluate_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/score_reliability.py"], cwd=repo_root, check=True)
    first = json.loads(output_path.read_text(encoding="utf-8"))
    subprocess.run([sys.executable, "scripts/score_reliability.py"], cwd=repo_root, check=True)
    second = json.loads(output_path.read_text(encoding="utf-8"))

    assert first == second
