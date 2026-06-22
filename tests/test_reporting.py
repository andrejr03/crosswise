from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from crosswise.generation import generate_fixture_set
from crosswise.evaluation import evaluate_reconciliation
from crosswise.reconciliation import reconcile_fixture_payload
from crosswise.confidence import score_reconciliation
from crosswise.reporting import render_local_evidence_report


def _payloads() -> dict:
    fixture_set = generate_fixture_set()
    fixtures = fixture_set.synthetic_payload()
    ground_truth = fixture_set.ground_truth_payload()
    reconciliation = reconcile_fixture_payload(fixtures, ground_truth)
    evaluation = evaluate_reconciliation(reconciliation, ground_truth)
    reliability = score_reconciliation(reconciliation, evaluation)
    return {
        "fixtures": fixtures,
        "ground_truth": ground_truth,
        "reconciliation": reconciliation,
        "evaluation": evaluation,
        "reliability": reliability,
    }


def test_report_script_runs_and_creates_output() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "scripts/generate_synthetic_data.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/evaluate_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/score_reliability.py"], cwd=repo_root, check=True)
    completed = subprocess.run(
        [sys.executable, "scripts/generate_report.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    output_path = repo_root / "docs" / "evidence" / "CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md"

    assert "Output:" in completed.stdout
    assert output_path.is_file()


def test_report_includes_required_summary_statements() -> None:
    report = render_local_evidence_report(_payloads())

    assert "# Crosswise Local Evidence Report" in report
    assert "## 1. Project Summary" in report
    assert "synthetic-data-only" in report
    assert "not accounting, tax, legal, financial, payment" in report


def test_report_includes_evaluation_metrics() -> None:
    report = render_local_evidence_report(_payloads())

    assert "## 5. Evaluation Summary" in report
    assert "Overall precision: 1.000" in report
    assert "Overall recall: 1.000" in report
    assert "Overall F1: 1.000" in report
    assert "Macro F1: 1.000" in report
    assert "| `quantity_mismatch` | 1.000 | 1.000 | 1.000 |" in report


def test_report_includes_reliability_counts() -> None:
    report = render_local_evidence_report(_payloads())

    assert "## 6. Reliability Summary" in report
    assert "`auto_accept` count: 1" in report
    assert "`needs_review` count: 8" in report
    assert "`blocked` count: 1" in report
    assert "Average confidence: 0.674" in report


def test_report_includes_reproduction_commands() -> None:
    report = render_local_evidence_report(_payloads())

    assert "python3 scripts/generate_synthetic_data.py" in report
    assert "python3 scripts/validate_fixtures.py" in report
    assert "python3 scripts/run_reconciliation.py" in report
    assert "python3 scripts/evaluate_reconciliation.py" in report
    assert "python3 scripts/score_reliability.py" in report
    assert "python3 scripts/generate_report.py" in report
    assert "python3 -m pytest" in report


def test_report_output_is_deterministic_across_repeated_renders() -> None:
    payloads = _payloads()

    assert render_local_evidence_report(payloads) == render_local_evidence_report(payloads)
