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


def _detail_slice(html: str, bundle_id: str) -> str:
    """Return the detail markup for a single bundle.

    Slices the rendered HTML between consecutive detail openings so each
    case can be inspected in isolation.
    """
    starts = [match.start() for match in re.finditer(r'<div class="case-detail', html)]
    assert starts, "no case details rendered"
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(html)
        chunk = html[start:end]
        if f'data-detail="{bundle_id}"' in chunk:
            return chunk
    raise AssertionError(f"detail for {bundle_id} not found")


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
    assert "Screenshot:" not in completed.stdout
    assert "Interactive screenshot:" not in completed.stdout
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


def test_reviewer_html_contains_hero_story_and_interactive_explorer() -> None:
    html = render_static_reviewer(_payloads())

    # The hero leads with the cleanest field-level discrepancy (unit price),
    # presented in the showcase comparison layout.
    assert 'data-hero-case="bundle_unit_price_mismatch_003"' in html
    assert 'data-hero-core="bundle_unit_price_mismatch_003"' in html
    assert 'data-hero-comparison="true"' in html
    assert "Route to human review" in html

    # The interactive reviewer holds every generated case as a pre-rendered
    # hero core and a below-the-fold detail block.
    assert 'id="interactive-case-explorer"' in html
    assert "Browse all 10 cases" in html
    assert html.count('data-hero-core="') == 10
    assert html.count('data-detail="') == 10
    assert 'data-detail="bundle_clean_match_001"' in html
    assert 'data-detail="bundle_quantity_mismatch_002"' in html
    assert 'data-detail="bundle_unit_price_mismatch_003"' in html
    assert 'data-detail="bundle_duplicate_invoice_006"' in html
    assert 'data-detail="bundle_supplier_alias_mismatch_007"' in html
    assert 'data-detail="bundle_low_confidence_extraction_009"' in html
    assert 'data-detail="bundle_schema_validation_failure_010"' in html


def test_reviewer_interactive_controls_exist() -> None:
    html = render_static_reviewer(_payloads())

    assert "data-explorer" in html
    assert "data-explorer-prev" not in html
    assert "data-explorer-next" not in html
    assert "data-explorer-select" not in html
    assert "data-explorer-position" not in html
    assert "Jump to case" not in html
    # Three signature cases are visible up top; all ten live in the quiet index.
    assert html.count('data-signature-case="') == 3
    assert html.count('data-index-case="') == 10
    assert html.count("<option value=") == 0
    # Inline navigation script is present and enables progressive enhancement.
    assert "<script>" in html
    assert "data-explorer-default" in html
    assert "classList.add('js-on')" in html


def test_reviewer_signature_rail_spans_routes_and_includes_clean_match() -> None:
    html = render_static_reviewer(_payloads())

    rail = html.split('<div class="signature-options"', 1)[1].split("</div>", 1)[0]
    assert rail.count('data-signature-case="') == 3
    assert 'data-signature-case="bundle_clean_match_001"' in rail
    assert 'data-signature-case="bundle_unit_price_mismatch_003"' in rail
    assert 'data-signature-case="bundle_schema_validation_failure_010"' in rail
    assert "Clean match" in rail
    assert "Unit price mismatch" in rail
    assert "Schema validation failure" in rail
    assert "route-auto_accept" in rail
    assert "route-needs_review" in rail
    assert "route-blocked" in rail


def test_reviewer_interactive_default_case_is_a_discrepancy() -> None:
    html = render_static_reviewer(_payloads())

    # The explorer opens on a clear field-level discrepancy so the interactive
    # showcase screenshot lands on a flagged case, not the clean match.
    assert 'data-explorer-default="bundle_unit_price_mismatch_003"' in html
    assert '<div class="hero-core is-active" data-hero-core="bundle_unit_price_mismatch_003"' in html
    default_detail = _detail_slice(html, "bundle_unit_price_mismatch_003")
    assert default_detail.startswith('<div class="case-detail is-active"')
    clean_detail = _detail_slice(html, "bundle_clean_match_001")
    assert clean_detail.startswith('<div class="case-detail"')


def test_reviewer_interactive_panels_match_source_outputs() -> None:
    payloads = _payloads()
    html = render_static_reviewer(payloads)
    reliability_cases = {
        case["bundle_id"]: case for case in payloads["reliability"]["cases"]
    }

    for bundle_id, reliability in reliability_cases.items():
        panel = _detail_slice(html, bundle_id)
        route = reliability["reliability_route"]
        confidence = f"{reliability['confidence_score']:.2f}"
        assert route in panel, f"route {route} missing for {bundle_id}"
        assert confidence in panel, f"confidence {confidence} missing for {bundle_id}"


def test_reviewer_interactive_highlights_update_per_case() -> None:
    html = render_static_reviewer(_payloads())

    # Each flagged case highlights its own disagreeing field inside its own
    # panel; the clean match carries no highlight.
    quantity_panel = _detail_slice(html, "bundle_quantity_mismatch_002")
    assert "field-highlight" in quantity_panel

    supplier_panel = _detail_slice(html, "bundle_supplier_alias_mismatch_007")
    assert 'class="field-highlight">Synth Vendor 007</span>' in supplier_panel

    clean_panel = _detail_slice(html, "bundle_clean_match_001")
    assert "field-highlight" not in clean_panel


def test_reviewer_no_js_fallback_content_present() -> None:
    html = render_static_reviewer(_payloads())

    # Hero core and detail visibility are gated behind a js-on class, so with
    # scripting disabled the static content remains rendered server-side.
    assert ".js-on .hero-core:not(.is-active)" in html
    assert ".js-on .case-detail:not(.is-active)" in html
    assert "JavaScript is disabled" in html
    assert "<details class=\"case-index\"" in html
    # The static substance is still rendered server-side (no JS required).
    assert "Synthetic-only notice" in html
    assert "Overall precision" in html
    assert "python3 -m pytest" in html
    assert html.count('data-detail="') == 10


def test_reviewer_script_has_no_external_or_unsafe_sequences() -> None:
    html = render_static_reviewer(_payloads())

    script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    # No external URLs, no protocol-relative or comment-style double slashes.
    assert re.search(r"https?://|//", script) is None
    assert "src=" not in script
    assert "import" not in script
    assert "fetch(" not in script


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

    # The hero bundle is shown as the comparison table; every bundle (including
    # the hero bundle) keeps full document panels inside the interactive explorer.
    assert html.count('data-document-panel="Purchase Order"') == 10
    assert html.count('data-document-panel="Invoice"') == 10
    assert html.count('data-document-panel="Receipt"') == 10
    assert 'class="field-highlight">6</span>' in html
    assert 'class="field-highlight">Synth Vendor 007</span>' in html
    assert "duplicate of inv_006_a" in html


def test_reviewer_html_renders_evidence_route_and_explanation_blocks() -> None:
    html = render_static_reviewer(_payloads())

    assert html.count('data-explanation-block="') == 10
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


def test_reviewer_links_to_synthetic_document_pack() -> None:
    html = render_static_reviewer(_payloads())

    assert 'href="documents/index.html"' in html


def test_reviewer_html_has_no_external_urls() -> None:
    html = render_static_reviewer(_payloads())

    assert re.search(r"https?://|//", html) is None


def test_reviewer_html_output_is_deterministic_across_repeated_renders() -> None:
    payloads = _payloads()

    assert render_static_reviewer(payloads) == render_static_reviewer(payloads)
