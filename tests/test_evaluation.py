from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from crosswise.evaluation import evaluate_reconciliation
from crosswise.generation import generate_fixture_set
from crosswise.reconciliation import reconcile_fixture_payload
from crosswise.schemas.models import DISCREPANCY_LABELS


def _inputs() -> tuple[dict, dict]:
    fixture_set = generate_fixture_set()
    ground_truth = fixture_set.ground_truth_payload()
    reconciliation = reconcile_fixture_payload(fixture_set.synthetic_payload(), ground_truth)
    return reconciliation, ground_truth


def test_perfect_synthetic_baseline_yields_expected_values() -> None:
    reconciliation, ground_truth = _inputs()

    result = evaluate_reconciliation(reconciliation, ground_truth)

    assert result["summary"]["bundles_evaluated"] == 10
    assert result["summary"]["overall_precision"] == 1.0
    assert result["summary"]["overall_recall"] == 1.0
    assert result["summary"]["overall_f1"] == 1.0
    assert result["summary"]["macro_f1"] == 1.0
    assert result["false_positives"] == []
    assert result["false_negatives"] == []


def test_metrics_are_within_valid_range() -> None:
    reconciliation, ground_truth = _inputs()

    result = evaluate_reconciliation(reconciliation, ground_truth)

    summary = result["summary"]
    for field in ("overall_precision", "overall_recall", "overall_f1", "macro_f1"):
        assert 0.0 <= summary[field] <= 1.0
    for metrics in result["per_label_metrics"].values():
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
        assert 0.0 <= metrics["f1"] <= 1.0


def test_false_positive_accounting_works() -> None:
    reconciliation, ground_truth = _inputs()
    altered = copy.deepcopy(reconciliation)
    altered["cases"][0]["discrepancy_labels"].append("quantity_mismatch")

    result = evaluate_reconciliation(altered, ground_truth)

    assert result["summary"]["false_positives"] == 1
    assert result["false_positives"] == [
        {
            "bundle_id": "bundle_clean_match_001",
            "expected_label": "clean_match",
            "detected_label": "quantity_mismatch",
            "explanation": "Detected quantity_mismatch but ground truth expected clean_match.",
        }
    ]


def test_false_negative_accounting_works() -> None:
    reconciliation, ground_truth = _inputs()
    altered = copy.deepcopy(reconciliation)
    altered["cases"][1]["discrepancy_labels"] = ["clean_match"]

    result = evaluate_reconciliation(altered, ground_truth)

    assert result["summary"]["false_negatives"] == 1
    assert result["false_negatives"] == [
        {
            "bundle_id": "bundle_quantity_mismatch_002",
            "expected_label": "quantity_mismatch",
            "detected_label": "clean_match",
            "explanation": "Expected quantity_mismatch but reconciliation detected clean_match.",
        }
    ]


def test_per_label_metrics_exist() -> None:
    reconciliation, ground_truth = _inputs()

    result = evaluate_reconciliation(reconciliation, ground_truth)

    assert set(result["per_label_metrics"]) == set(DISCREPANCY_LABELS)
    for label in DISCREPANCY_LABELS:
        assert result["per_label_metrics"][label]["true_positives"] == 1


def test_macro_f1_calculation_works() -> None:
    reconciliation, ground_truth = _inputs()
    altered = copy.deepcopy(reconciliation)
    altered["cases"][1]["discrepancy_labels"] = ["clean_match"]

    result = evaluate_reconciliation(altered, ground_truth)

    per_label_f1 = [metrics["f1"] for metrics in result["per_label_metrics"].values()]
    expected = round(sum(per_label_f1) / len(per_label_f1), 6)
    assert result["summary"]["macro_f1"] == expected
    assert result["summary"]["macro_f1"] < 1.0


def test_confusion_information_is_recorded() -> None:
    reconciliation, ground_truth = _inputs()

    result = evaluate_reconciliation(reconciliation, ground_truth)

    assert result["confusion"]["clean_match"]["clean_match"] == 1
    assert result["confusion"]["quantity_mismatch"]["quantity_mismatch"] == 1


def test_evaluation_script_runs_and_output_file_is_created() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "scripts/generate_synthetic_data.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    completed = subprocess.run(
        [sys.executable, "scripts/evaluate_reconciliation.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    output_path = repo_root / "data" / "evaluation" / "evaluation_v1_0.json"

    assert "Bundles evaluated: 10" in completed.stdout
    assert output_path.is_file()


def test_evaluation_output_is_deterministic_across_repeated_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output_path = repo_root / "data" / "evaluation" / "evaluation_v1_0.json"
    subprocess.run([sys.executable, "scripts/generate_synthetic_data.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/evaluate_reconciliation.py"], cwd=repo_root, check=True)
    first = json.loads(output_path.read_text(encoding="utf-8"))
    subprocess.run([sys.executable, "scripts/evaluate_reconciliation.py"], cwd=repo_root, check=True)
    second = json.loads(output_path.read_text(encoding="utf-8"))

    assert first == second
