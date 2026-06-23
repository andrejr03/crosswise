from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from crosswise.confidence import score_reconciliation
from crosswise.evaluation import evaluate_reconciliation
from crosswise.generation import generate_fixture_set
from crosswise.reconciliation import reconcile_fixture_payload
from crosswise.reviewer import render_static_reviewer


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


def test_reviewer_script_runs_and_creates_output() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "scripts/generate_synthetic_data.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/run_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/evaluate_reconciliation.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/score_reliability.py"], cwd=repo_root, check=True)
    completed = subprocess.run(
        [sys.executable, "scripts/generate_reviewer.py"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    output_path = repo_root / "docs" / "evidence" / "crosswise_reviewer_v1_0.html"

    assert "Output:" in completed.stdout
    assert output_path.is_file()


def test_reviewer_html_contains_required_notices() -> None:
    html = render_static_reviewer(_payloads())

    assert "Synthetic-only notice" in html
    assert "No real invoices" in html
    assert "Non-advice notice" in html
    assert "not accounting, tax, legal, financial, payment" in html


def test_reviewer_html_contains_evaluation_metrics() -> None:
    html = render_static_reviewer(_payloads())

    assert "Overall precision" in html
    assert "Overall recall" in html
    assert "Overall F1" in html
    assert "Macro F1" in html
    assert html.count("<strong>1.000</strong>") >= 4


def test_reviewer_html_contains_reliability_counts() -> None:
    html = render_static_reviewer(_payloads())

    assert "auto_accept count" in html
    assert "needs_review count" in html
    assert "blocked count" in html
    assert "Average confidence" in html
    assert "<strong>1</strong>" in html
    assert "<strong>8</strong>" in html
    assert "<strong>0.674</strong>" in html


def test_reviewer_html_contains_at_least_one_case_row() -> None:
    html = render_static_reviewer(_payloads())

    assert "<tbody>" in html
    assert "bundle_clean_match_001" in html
    assert "clean_match" in html
    assert "All deterministic baseline checks passed" in html


def test_reviewer_html_contains_reproduction_commands() -> None:
    html = render_static_reviewer(_payloads())

    assert "python3 scripts/generate_synthetic_data.py" in html
    assert "python3 scripts/validate_fixtures.py" in html
    assert "python3 scripts/run_reconciliation.py" in html
    assert "python3 scripts/evaluate_reconciliation.py" in html
    assert "python3 scripts/score_reliability.py" in html
    assert "python3 scripts/generate_report.py" in html
    assert "python3 scripts/generate_reviewer.py" in html
    assert "python3 -m pytest" in html


def test_reviewer_html_has_no_external_urls() -> None:
    html = render_static_reviewer(_payloads())

    assert re.search(r"https?://|//", html) is None


def test_reviewer_html_output_is_deterministic_across_repeated_renders() -> None:
    payloads = _payloads()

    assert render_static_reviewer(payloads) == render_static_reviewer(payloads)
