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
    screenshot_path = repo_root / "docs" / "evidence" / "CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png"

    assert "Output:" in completed.stdout
    assert "Screenshot:" in completed.stdout
    assert output_path.is_file()
    assert screenshot_path.is_file()


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


def test_reviewer_html_contains_hero_story_and_condensed_cases() -> None:
    html = render_static_reviewer(_payloads())

    # The hero leads with the cleanest field-level discrepancy (unit price),
    # presented in the showcase comparison layout.
    assert 'data-hero-case="bundle_unit_price_mismatch_003"' in html
    assert 'data-hero-comparison="true"' in html
    assert "Route to human review" in html
    assert "Condensed Review Queue" in html
    assert html.count('data-condensed-case="') == 9
    assert 'data-condensed-case="bundle_clean_match_001"' in html
    assert 'data-condensed-case="bundle_quantity_mismatch_002"' in html
    assert 'data-condensed-case="bundle_duplicate_invoice_006"' in html
    assert 'data-condensed-case="bundle_supplier_alias_mismatch_007"' in html
    assert 'data-condensed-case="bundle_low_confidence_extraction_009"' in html
    # The hero bundle is featured, not duplicated in the condensed queue.
    assert 'data-condensed-case="bundle_unit_price_mismatch_003"' not in html


def test_reviewer_hero_comparison_shows_field_level_delta() -> None:
    html = render_static_reviewer(_payloads())

    # Invoice vs PO unit price difference rendered with a signed delta.
    assert "€15.00" in html
    assert "€13.00" in html
    assert "+€2.00" in html
    assert "&#9873; review" in html
    assert "&#10003; match" in html


def test_reviewer_html_renders_document_panels_and_highlights() -> None:
    html = render_static_reviewer(_payloads())

    # The hero bundle is shown as the comparison table; the remaining nine
    # bundles keep their full document panels in the condensed queue.
    assert html.count('data-document-panel="Purchase Order"') == 9
    assert html.count('data-document-panel="Invoice"') == 9
    assert html.count('data-document-panel="Receipt"') == 9
    assert 'class="field-highlight">6</span>' in html
    assert 'class="field-highlight">Synth Vendor 007</span>' in html
    assert "duplicate of inv_006_a" in html


def test_reviewer_html_renders_evidence_route_and_explanation_blocks() -> None:
    html = render_static_reviewer(_payloads())

    assert html.count('data-explanation-block="') == 9
    assert "What happened?" in html
    assert "Why flagged?" in html
    assert "Evidence" in html
    assert "Route assigned" in html
    assert "Route to human review" in html
    assert "needs_review route assigned" in html
    assert "duplicate_invoice_number_supplier_date_total" in html


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
