"""Self-contained static reviewer HTML generation.

The reviewer summarizes existing Crosswise generated outputs only. It does not
start a server, fetch network assets, call models, run OCR, or modify upstream
reconciliation, evaluation, or reliability logic.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

REQUIRED_OUTPUT_PATHS = {
    "fixtures": Path("data/synthetic/fixtures_v1_0.json"),
    "ground_truth": Path("data/ground_truth/ground_truth_v1_0.json"),
    "reconciliation": Path("data/reconciliation/reconciliation_v1_0.json"),
    "evaluation": Path("data/evaluation/evaluation_v1_0.json"),
    "reliability": Path("data/reliability/reliability_v1_0.json"),
}
DEFAULT_OUTPUT_PATH = Path("docs/evidence/crosswise_reviewer_v1_0.html")
SCREENSHOT_OUTPUT_PATH = Path("docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png")
INTERACTIVE_SCREENSHOT_OUTPUT_PATH = Path("docs/evidence/CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png")
INTERACTIVE_EXPLORER_SELECTOR = "#interactive-case-explorer"
CURATED_STORY_LABELS = [
    ["clean_match"],
    ["quantity_mismatch"],
    ["unit_price_mismatch"],
    ["supplier_alias_mismatch"],
    ["duplicate_invoice"],
    ["low_confidence_extraction"],
]


def load_required_outputs(repo_root: Path) -> dict[str, Any]:
    missing = [str(path) for path in REQUIRED_OUTPUT_PATHS.values() if not (repo_root / path).is_file()]
    if missing:
        joined = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(
            "Required upstream Crosswise outputs are missing. Run the Slice 1-5 pipeline first:\n"
            "python3 scripts/generate_synthetic_data.py\n"
            "python3 scripts/validate_fixtures.py\n"
            "python3 scripts/run_reconciliation.py\n"
            "python3 scripts/evaluate_reconciliation.py\n"
            "python3 scripts/score_reliability.py\n"
            f"Missing files:\n{joined}"
        )

    return {
        name: json.loads((repo_root / path).read_text(encoding="utf-8"))
        for name, path in REQUIRED_OUTPUT_PATHS.items()
    }


def generate_static_reviewer(repo_root: Path, output_path: Path | None = None) -> Path:
    payloads = load_required_outputs(repo_root)
    target = output_path or repo_root / DEFAULT_OUTPUT_PATH
    return write_static_reviewer(payloads, target)


def generate_reviewer_screenshot(
    html_path: Path,
    screenshot_path: Path,
    selector: str = "#document-panel-reconciliation-view",
) -> Path:
    from playwright.sync_api import sync_playwright

    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1500, "height": 1200}, device_scale_factor=1)
        page.goto(html_path.resolve().as_uri())
        page.locator(selector).screenshot(path=str(screenshot_path))
        browser.close()
    return screenshot_path


def write_static_reviewer(payloads: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_static_reviewer(payloads), encoding="utf-8")
    return output_path


def render_static_reviewer(payloads: dict[str, Any]) -> str:
    fixtures = payloads["fixtures"]
    reconciliation = payloads["reconciliation"]
    evaluation = payloads["evaluation"]
    reliability = payloads["reliability"]
    fixture_index = _fixture_index(fixtures)
    cases = sorted(reconciliation.get("cases", []), key=lambda item: item["bundle_id"])
    reliability_cases = {
        case["bundle_id"]: case
        for case in sorted(reliability.get("cases", []), key=lambda item: item["bundle_id"])
    }
    hero_case = _select_hero_case(cases, reliability_cases)

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Crosswise Reviewer</title>",
            f"  <style>{_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            _interactive_explorer(cases, reliability_cases, fixture_index, hero_case["bundle_id"]),
            _metric_sections(evaluation, reliability),
            _reviewer_pillars(),
            _notice_band(),
            _pipeline_summary(),
            _reproduction_commands(),
            "  </main>",
            f"  <script>{_explorer_script()}</script>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _css() -> str:
    return """
:root {
  --page: #171511;
  --ink: #eee8dd;
  --muted: #928a7d;
  --soft: #c8bdad;
  --panel: #211e19;
  --panel-raised: #28231c;
  --panel-quiet: #1c1915;
  --line: #373126;
  --line-soft: #2a261f;
  --amber: #c9a24b;
  --amber-strong: #e0aa4b;
  --amber-wash: rgba(201, 162, 75, 0.12);
  --amber-line: rgba(201, 162, 75, 0.36);
  --ok: #7da069;
  --blocked: #c47a5e;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  background:
    radial-gradient(circle at 50% -10%, rgba(201, 162, 75, 0.07), transparent 34%),
    var(--page);
  color: var(--ink);
  font-family: "Avenir Next", Avenir, "Gill Sans", "Trebuchet MS", sans-serif;
  line-height: 1.5;
}

.shell {
  width: min(1120px, calc(100% - 40px));
  margin: 0 auto;
  padding: 54px 0 58px;
}

#interactive-case-explorer {
  padding: 48px 16px 0 44px;
}

.hero {
  position: relative;
  padding: 26px 0 46px;
}

.kicker {
  color: var(--amber);
  font-family: Menlo, Consolas, monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.26em;
  text-transform: uppercase;
}

h1, h2, h3, p {
  margin: 0;
}

h1 {
  margin-top: 10px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 58px;
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}

.subtitle {
  max-width: 620px;
  margin-top: 18px;
  color: var(--muted);
  font-size: 18px;
}

.hero-note {
  position: absolute;
  top: 0;
  right: 28px;
  color: var(--muted);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-align: right;
  text-transform: uppercase;
}

.notice-band,
.story-section,
.hero-story,
.command-section {
  margin-top: 26px;
}

.notice-band {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 0;
  padding: 16px 0 20px;
  border-top: 1px solid var(--line-soft);
  border-bottom: 1px solid var(--line-soft);
}

.notice,
.metric,
.hero-confidence,
.hero-action,
.story-card,
.doc-panel,
.command-section {
  background: var(--panel);
  border: 1px solid var(--line);
}

.notice {
  background: transparent;
  border-color: transparent;
  padding: 0;
}

.notice strong {
  display: block;
  font-family: Menlo, Consolas, monospace;
  color: var(--amber);
  font-size: 11px;
  letter-spacing: 0.2em;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.notice p {
  max-width: 460px;
  color: var(--muted);
  font-size: 13px;
}

.pipeline {
  margin-top: 46px;
  padding: 20px 0 0;
  border-top: 1px solid var(--line);
}

.pipeline h2,
.command-section h2 {
  margin-bottom: 14px;
  color: var(--soft);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.pipeline ol {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: step;
}

.pipeline li {
  min-height: 72px;
  padding: 12px 10px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
  counter-increment: step;
}

.pipeline li::before {
  content: counter(step, decimal-leading-zero);
  display: block;
  color: var(--amber);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 8px;
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 0;
  margin-top: 32px;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}

.metric {
  min-height: 94px;
  padding: 16px 14px;
  background: transparent;
  border: 0;
  border-right: 1px solid var(--line);
}

.metric:last-child {
  border-right: 0;
}

.metric span,
.doc-panel h4,
.answer strong,
.condensed-label {
  display: block;
}

.metric span,
.comparison-table th,
.mini-table th,
.doc-panel h4,
.answer strong,
.condensed-label {
  font-family: Menlo, Consolas, monospace;
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.metric strong {
  display: block;
  margin-top: 10px;
  color: var(--ink);
  font-family: Menlo, Consolas, monospace;
  font-size: 24px;
  font-weight: 500;
}

.story-section {
  padding: 12px 0 4px;
}

.section-heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 0.42fr);
  gap: 28px;
  align-items: end;
  margin-bottom: 20px;
}

.section-heading h2 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 40px;
  font-weight: 500;
  line-height: 1.05;
}

.section-heading p {
  color: var(--muted);
}

.story-list {
  display: grid;
  gap: 14px;
}

.hero-story {
  padding: 54px 56px 44px;
  background: var(--page);
  border: 1px solid var(--line-soft);
}

/* Brand row */
.rev-brand {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.rev-brand-id {
  display: flex;
  align-items: center;
  gap: 18px;
}

.rev-diamond {
  width: 30px;
  height: 30px;
  flex: none;
  transform: rotate(45deg);
  border: 1.5px solid var(--amber);
}

.rev-wordmark {
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 30px;
  font-weight: 600;
  line-height: 1;
}

.rev-tagline {
  margin-top: 7px;
  color: var(--muted);
  font-family: Menlo, Consolas, monospace;
  font-size: 11px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.rev-build {
  text-align: right;
  font-family: Menlo, Consolas, monospace;
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.rev-build-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--amber);
}

.rev-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--amber);
}

.rev-build-sub {
  display: block;
  margin-top: 7px;
  color: var(--muted);
}

/* Document context line */
.rev-context {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 18px;
  margin-top: 56px;
  color: var(--muted);
  font-family: Menlo, Consolas, monospace;
  font-size: 13px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.rev-context-doc-end {
  text-align: right;
}

.rev-context-mid {
  color: var(--amber);
  text-align: center;
}

/* Comparison table */
.comparison-wrap {
  margin-top: 26px;
  border: 1px solid var(--line);
  background: var(--panel);
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
}

.comparison-table th {
  padding: 18px 28px;
  border-bottom: 1px solid var(--line);
  color: var(--muted);
  font-family: Menlo, Consolas, monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.2em;
  text-align: left;
  text-transform: uppercase;
}

.comparison-table td {
  padding: 22px 28px;
  border-bottom: 1px solid var(--line-soft);
  color: var(--soft);
  font-family: Menlo, Consolas, monospace;
  font-size: 15px;
  text-align: left;
}

.comparison-table th.num,
.comparison-table td.num {
  text-align: right;
}

.comparison-table th.status,
.comparison-table td.status {
  text-align: right;
  white-space: nowrap;
}

.comparison-table tbody tr:last-child td {
  border-bottom: 0;
}

.comparison-table td:first-child {
  color: var(--ink);
  font-family: "Avenir Next", Avenir, "Gill Sans", "Trebuchet MS", sans-serif;
  font-size: 17px;
}

.comparison-table tr.is-disagreement {
  background: var(--amber-wash);
}

.comparison-table tr.is-disagreement td,
.comparison-table tr.is-disagreement td:first-child {
  color: #f0d187;
}

.status {
  font-family: Menlo, Consolas, monospace;
  font-size: 13px;
  letter-spacing: 0.04em;
}

.status-review {
  color: var(--amber);
}

.status-match {
  color: var(--muted);
}

/* Decision row: confidence + action */
.rev-decision {
  display: grid;
  grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
  gap: 20px;
  margin-top: 30px;
}

.hero-confidence,
.hero-action {
  padding: 26px 28px;
  background: var(--panel);
  border: 1px solid var(--line);
}

.confidence-number {
  margin-top: 16px;
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 54px;
  font-weight: 500;
  line-height: 1;
}

.confidence-number span {
  margin-left: 12px;
  color: var(--amber);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.confidence-track {
  height: 6px;
  margin-top: 24px;
  background: var(--line-soft);
  overflow: hidden;
}

.confidence-fill {
  display: block;
  height: 100%;
  background: var(--amber);
}

.action-button {
  display: inline-flex;
  margin-top: 16px;
  padding: 14px 22px;
  background: var(--amber-strong);
  color: #171511;
  font-family: Menlo, Consolas, monospace;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.hero-action p {
  margin-top: 18px;
  color: var(--muted);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.04em;
}

/* Feature row */
.rev-features {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
  margin-top: 56px;
  padding-top: 34px;
  border-top: 1px solid var(--line-soft);
}

.rev-glyph {
  display: block;
  margin-bottom: 18px;
  color: var(--amber);
  font-size: 22px;
  line-height: 1;
}

.rev-feature h3 {
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 21px;
  font-weight: 500;
}

.rev-feature p {
  margin-top: 10px;
  color: var(--muted);
  font-size: 14px;
}

/* Footer */
.rev-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 54px;
  padding-top: 26px;
  border-top: 1px solid var(--line-soft);
  color: var(--muted);
}

.rev-foot span:first-child {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 18px;
}

.rev-foot span:last-child {
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.story-card {
  padding: 0;
  background: transparent;
  border-color: var(--line-soft);
}

.story-topline {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, auto);
  gap: 20px;
  align-items: start;
  padding: 18px;
  border-bottom: 1px solid var(--line-soft);
}

.story-title {
  display: grid;
  gap: 4px;
}

.story-title h3 {
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 24px;
  font-weight: 500;
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  align-items: stretch;
  padding: 14px;
}

.doc-panel {
  padding: 16px;
  background: var(--panel-raised);
  border-color: var(--line-soft);
}

.doc-panel h4 {
  margin: 0 0 10px;
  color: var(--amber);
}

.doc-id {
  margin-bottom: 10px;
  color: var(--ink);
  font-family: Menlo, Consolas, monospace;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.doc-meta {
  display: grid;
  gap: 6px;
  margin-bottom: 12px;
}

.meta-row {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr);
  gap: 8px;
  color: var(--muted);
  font-size: 13px;
}

.meta-row span:first-child {
  color: var(--muted);
}

.sub-document {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}

.sub-document:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: 0;
}

.mini-table {
  width: 100%;
  min-width: 0;
  border-collapse: collapse;
}

.mini-table th,
.mini-table td {
  padding: 7px 6px;
  border-bottom: 1px solid var(--line-soft);
  font-size: 12px;
  text-align: left;
}

.mini-table th {
  color: var(--muted);
}

.mini-table td:first-child,
.mini-table td:nth-child(4) {
  color: var(--muted);
  font-family: "Avenir Next", Avenir, "Gill Sans", "Trebuchet MS", sans-serif;
  font-size: 12px;
}

.field-highlight,
.line-highlight td {
  background: var(--amber-wash);
  box-shadow: inset 0 0 0 1px var(--amber-line);
}

.field-highlight {
  color: #f2d28b;
  padding: 2px 4px;
}

.issue-badge {
  display: inline-flex;
  margin-left: 6px;
  padding: 2px 6px;
  border: 1px solid var(--amber-line);
  color: var(--amber);
  font-size: 11px;
}

.explanation-block {
  margin: 0 14px 14px;
  padding: 16px;
  background: var(--panel-quiet);
  border: 1px solid var(--line-soft);
}

.explanation-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.answer {
  color: var(--muted);
  font-size: 13px;
}

.answer strong {
  margin-bottom: 4px;
  color: var(--amber);
}

.bundle {
  font-family: Menlo, Consolas, monospace;
  font-size: 13px;
  color: var(--ink);
  overflow-wrap: anywhere;
}

.explain {
  margin-top: 12px;
  color: var(--muted);
  font-size: 14px;
}

.pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.pill {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 3px 8px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--soft);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  font-weight: 700;
}

.route-auto_accept {
  border-color: rgba(125, 160, 105, 0.36);
  color: var(--ok);
}

.route-needs_review {
  border-color: var(--amber-line);
  color: var(--amber);
}

.route-blocked {
  border-color: rgba(196, 122, 94, 0.36);
  color: var(--blocked);
}

.command-section {
  padding: 20px;
}

.condensed-case-grid {
  display: grid;
  gap: 10px;
}

.condensed-case {
  display: grid;
  grid-template-columns: minmax(170px, 0.8fr) minmax(0, 1.2fr) minmax(220px, 1fr);
  gap: 18px;
  align-items: start;
  padding: 16px 0;
  border-top: 1px solid var(--line-soft);
}

.condensed-case:first-child {
  border-top: 0;
}

.condensed-case p {
  color: var(--muted);
  font-size: 13px;
}

.condensed-case .pills {
  margin-top: 0;
}

.condensed-evidence {
  font-family: Menlo, Consolas, monospace;
  overflow-wrap: anywhere;
}

code {
  color: var(--ink);
  font-family: Menlo, Consolas, monospace;
}

.command-list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.command-list li {
  padding: 11px 12px;
  background: var(--panel-quiet);
  border: 1px solid var(--line);
  overflow-x: auto;
}

.utility-link {
  margin-top: 16px;
  color: var(--muted);
  font-size: 13px;
}

.utility-link a {
  color: var(--amber);
  text-decoration-color: var(--amber-line);
  text-underline-offset: 3px;
}

/* Interactive case reviewer */
.explorer {
  margin-top: 26px;
}

.hero-core {
  display: block;
}

.js-on .hero-core:not(.is-active),
.js-on .case-detail:not(.is-active) {
  display: none;
}

.signature-rail {
  margin-top: 34px;
  padding-top: 28px;
  border-top: 1px solid var(--line-soft);
}

.signature-rail-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 22px;
  margin-bottom: 14px;
}

.signature-rail-header p {
  max-width: 420px;
  color: var(--muted);
  font-size: 13px;
}

.signature-options {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.signature-case,
.case-index-button {
  border: 1px solid var(--line);
  color: var(--soft);
  cursor: pointer;
  text-align: left;
}

.signature-case {
  display: grid;
  gap: 7px;
  min-height: 96px;
  padding: 16px;
  background: var(--panel-quiet);
}

.signature-case:hover,
.case-index-button:hover {
  border-color: var(--amber-line);
  color: var(--ink);
}

.signature-case.is-active {
  background: var(--amber-wash);
  border-color: var(--amber);
  color: var(--amber);
}

.signature-case-title,
.case-index-title {
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 19px;
  line-height: 1.08;
}

.signature-case.is-active .signature-case-title {
  color: #f0d187;
}

.signature-case-purpose,
.case-index-meta {
  color: var(--muted);
  font-family: Menlo, Consolas, monospace;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.case-detail-region,
.case-index {
  margin-top: 28px;
}

.case-detail-region {
  padding-top: 26px;
  border-top: 1px solid var(--line);
}

.case-detail-region .section-heading {
  margin-bottom: 14px;
}

.case-detail {
  display: block;
}

.case-detail .story-card {
  opacity: 0.88;
}

.case-detail .explanation-block {
  margin-top: 0;
}

.case-index {
  background: transparent;
  border-top: 1px solid var(--line-soft);
  border-bottom: 1px solid var(--line-soft);
}

.case-index summary {
  padding: 18px 0;
  color: var(--soft);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  cursor: pointer;
}

.case-index-list {
  display: grid;
  gap: 8px;
  padding: 0 0 18px;
}

.case-index-button {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  padding: 12px;
  background: var(--panel-quiet);
}

.case-index-button.is-active {
  border-color: var(--amber);
  background: var(--amber-wash);
}

.case-index-number {
  color: var(--muted);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.18em;
}

.case-index-button.is-active .case-index-title,
.case-index-button.is-active .case-index-number {
  color: var(--amber);
}

.explorer-fallback-note {
  margin-top: 14px;
  color: var(--muted);
  font-size: 13px;
}

.js-on .explorer-fallback-note {
  display: none;
}

@media (max-width: 880px) {
  .hero,
  .notice-band,
  .summary-strip,
  .section-heading,
  .rev-decision,
  .rev-features,
  .document-grid,
  .explanation-grid,
  .pipeline ol,
  .signature-options,
  .case-index-button,
  .condensed-case {
    grid-template-columns: 1fr;
  }

  .hero-story {
    padding: 32px 22px 28px;
  }

  #interactive-case-explorer {
    padding: 30px 24px 0;
  }

  .hero-note {
    position: static;
    margin-top: 22px;
    text-align: left;
  }

  h1 {
    font-size: 42px;
  }

  .section-heading h2 {
    font-size: 30px;
  }
}
""".strip()


def _hero() -> str:
    return """
    <section class="hero">
      <div>
        <div class="kicker">Crosswise Reviewer</div>
        <h1>Crosswise detected a discrepancy &mdash; and shows you why.</h1>
        <p class="subtitle">Pick a synthetic case to see the flagged field, the evidence, and the route without changing the underlying reconciliation output.</p>
      </div>
      <p class="hero-note">Synthetic test cases<br>Generated outputs only</p>
    </section>
""".rstrip()


def _notice_band() -> str:
    return """
    <section class="notice-band" aria-label="Scope notices">
      <div class="notice">
        <strong>Synthetic-only notice</strong>
        <p>Uses generated Crosswise fixtures only. No real invoices, real company data, PII, bank details, tax identifiers, payment information, or real supplier data.</p>
      </div>
      <div class="notice">
        <strong>Non-advice notice</strong>
        <p>Outputs support human review only and are not accounting, tax, legal, financial, payment, compliance, or autonomous-action advice.</p>
      </div>
    </section>
""".rstrip()


def _pipeline_summary() -> str:
    steps = [
        "Synthetic data generation",
        "Schema validation and normalization",
        "Reconciliation baseline",
        "Evaluation harness",
        "Reliability routing",
    ]
    items = "\n".join(f"        <li>{_e(step)}</li>" for step in steps)
    return f"""
    <section class="pipeline" aria-labelledby="pipeline-title">
      <h2 id="pipeline-title">Pipeline Summary</h2>
      <ol>
{items}
      </ol>
    </section>
""".rstrip()


def _metric_sections(evaluation: dict[str, Any], reliability: dict[str, Any]) -> str:
    evaluation_summary = evaluation.get("summary", {})
    reliability_summary = reliability.get("summary", {})
    return f"""
    <section class="summary-strip" aria-label="Evaluation summary and reliability summary">
      {_metric("Overall precision", evaluation_summary.get("overall_precision"))}
      {_metric("Overall recall", evaluation_summary.get("overall_recall"))}
      {_metric("Overall F1", evaluation_summary.get("overall_f1"))}
      {_metric("Macro F1", evaluation_summary.get("macro_f1"))}
      {_metric("auto_accept count", reliability_summary.get("auto_accept"))}
      {_metric("needs_review count", reliability_summary.get("needs_review"))}
      {_metric("blocked count", reliability_summary.get("blocked"))}
      {_metric("Average confidence", reliability_summary.get("average_confidence"))}
    </section>
""".rstrip()


def _reviewer_pillars() -> str:
    return """
    <section class="reviewer-pillars" aria-label="Reviewer pillars">
      <div class="rev-features">
        <div class="rev-feature">
          <span class="rev-glyph" aria-hidden="true">&#9671;</span>
          <h3>Line-item matching</h3>
          <p>Every line compared &mdash; not just document totals.</p>
        </div>
        <div class="rev-feature">
          <span class="rev-glyph" aria-hidden="true">&#9723;</span>
          <h3>Field-level evidence</h3>
          <p>Each result traces back to its source field.</p>
        </div>
        <div class="rev-feature">
          <span class="rev-glyph" aria-hidden="true">&#9711;</span>
          <h3>Human review routing</h3>
          <p>Low-confidence cases escalate to a person.</p>
        </div>
      </div>
      <footer class="rev-foot">
        <span>AI Document Reconciliation</span>
        <span>invoices &middot; purchase orders &middot; receipts</span>
      </footer>
    </section>
""".rstrip()


def _example_cards(cases: list[dict[str, Any]], reliability_cases: dict[str, dict[str, Any]]) -> str:
    examples = [
        ("Clean Match", _first_case(cases, ["clean_match"])),
        ("Needs Review", _first_route_case(cases, reliability_cases, "needs_review")),
        ("Blocked", _first_route_case(cases, reliability_cases, "blocked")),
    ]
    cards = "\n".join(
        _example_card(title, case, reliability_cases.get(case["bundle_id"], {}))
        for title, case in examples
        if case is not None
    )
    return f"""
    <section class="example-grid" aria-label="Highlighted examples">
{cards}
    </section>
""".rstrip()


def _example_card(title: str, case: dict[str, Any], reliability: dict[str, Any]) -> str:
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    labels = _label_pills(case.get("discrepancy_labels", []))
    return f"""
      <article class="example-card">
        <h3>{_e(title)}</h3>
        <p class="bundle">{_e(case["bundle_id"])}</p>
        <div class="pills">
          <span class="pill route-{_class_token(route)}">{_e(route)}</span>
          <span class="pill">{_e(_format_confidence(reliability.get("confidence_score")))}</span>
        </div>
        <div class="pills">{labels}</div>
        <p class="explain">{_e(case.get("explanation", "Not available"))}</p>
      </article>
""".rstrip()


def _case_table(cases: list[dict[str, Any]], reliability_cases: dict[str, dict[str, Any]]) -> str:
    rows = "\n".join(_case_row(case, reliability_cases.get(case["bundle_id"], {})) for case in cases)
    return f"""
    <section class="case-section" aria-labelledby="cases-title">
      <h2 id="cases-title">Case Table</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Bundle ID</th>
              <th>Detected labels</th>
              <th>Route</th>
              <th>Confidence score</th>
              <th>Explanation</th>
            </tr>
          </thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </section>
""".rstrip()


def _hero_discrepancy_story(
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
    fixture_index: dict[str, dict[str, Any]],
    default_bundle_id: str,
) -> str:
    hero_cores = "\n".join(
        _hero_core(case, reliability_cases.get(case["bundle_id"], {}), fixture_index, default_bundle_id)
        for case in cases
    )
    rail = _signature_rail(cases, reliability_cases, default_bundle_id)
    return f"""
      <section class="hero-story" id="document-panel-reconciliation-view" aria-label="Hero reconciliation case" data-hero-case="{_e(default_bundle_id)}">
        <header class="rev-brand">
          <div class="rev-brand-id">
            <span class="rev-diamond" aria-hidden="true"></span>
            <div>
              <div class="rev-wordmark">Crosswise</div>
              <div class="rev-tagline">AI Document Reconciliation</div>
            </div>
          </div>
          <div class="rev-build">
            <span class="rev-build-line"><span class="rev-dot" aria-hidden="true"></span>Dev build</span>
            <span class="rev-build-sub">synthetic test cases</span>
          </div>
        </header>
{hero_cores}
{rail}
      </section>
""".rstrip()


def _hero_core(
    case: dict[str, Any],
    reliability: dict[str, Any],
    fixture_index: dict[str, dict[str, Any]],
    default_bundle_id: str,
) -> str:
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    confidence = reliability.get("confidence_score")
    confidence_pct = max(0, min(100, int(float(confidence or 0) * 100)))
    po = fixture_index["purchase_orders"][case["purchase_order_id"]]
    invoice = fixture_index["invoices"][case.get("invoice_ids", [""])[-1]]
    discrepancy_count = len(case.get("discrepancy_labels", []))
    discrepancy_word = "discrepancy" if discrepancy_count == 1 else "discrepancies"
    po_label = _strip_prefix(po.get("purchase_order_id", "—"), "po_")
    invoice_label = invoice.get("invoice_number", invoice.get("invoice_id", "—"))
    active = " is-active" if case["bundle_id"] == default_bundle_id else ""
    return f"""
        <div class="hero-core{active}" data-hero-core="{_e(case['bundle_id'])}" data-hero-case="{_e(case['bundle_id'])}">
      <div class="rev-context">
        <span class="rev-context-doc">Invoice {_e(invoice_label)}</span>
        <span class="rev-context-mid">&#8644; Matching</span>
        <span class="rev-context-doc rev-context-doc-end">PO {_e(po_label)}</span>
      </div>

      <div class="comparison-wrap">
        <table class="comparison-table" data-hero-comparison="true">
          <thead>
            <tr>
              <th>Field</th>
              <th class="num">Invoice</th>
              <th class="num">PO</th>
              <th class="num">&#916;</th>
              <th class="status">Status</th>
            </tr>
          </thead>
          <tbody>
{_hero_comparison_body(case, fixture_index)}
          </tbody>
        </table>
      </div>

      <div class="rev-decision">
        <section class="hero-confidence" aria-label="Case confidence">
          <div class="condensed-label">Case confidence</div>
          <div class="confidence-number">{_e(_format_confidence(confidence))}<span>{_e(_confidence_note(route))}</span></div>
          <div class="confidence-track"><span class="confidence-fill" style="width: {confidence_pct}%"></span></div>
        </section>
        <section class="hero-action" aria-label="Route action">
          <div class="condensed-label">Action</div>
          <div class="action-button">&#8594; {_e(_route_action_label(route))}</div>
          <p>{discrepancy_count} {discrepancy_word} &middot; evidence linked &middot; {_e(route)} route assigned</p>
        </section>
      </div>
        </div>
""".rstrip()


def _hero_comparison_body(case: dict[str, Any], fixture_index: dict[str, dict[str, Any]]) -> str:
    return "\n".join(_hero_comparison_row(*row) for row in _hero_comparison_rows(case, fixture_index))


def _hero_comparison_row(
    field: str,
    invoice_value: str,
    po_value: str,
    delta: str,
    is_disagreement: bool,
) -> str:
    row_class = ' class="is-disagreement"' if is_disagreement else ""
    if is_disagreement:
        status_cell = '<td class="status status-review">&#9873; review</td>'
    else:
        status_cell = '<td class="status status-match">&#10003; match</td>'
    delta_cell = _e(delta) if is_disagreement else "&mdash;"
    return f"""
            <tr{row_class}>
              <td>{_e(field)}</td>
              <td class="num">{_e(invoice_value)}</td>
              <td class="num">{_e(po_value)}</td>
              <td class="num">{delta_cell}</td>
              {status_cell}
            </tr>
""".rstrip()


def _hero_comparison_rows(
    case: dict[str, Any],
    fixture_index: dict[str, dict[str, Any]],
) -> list[tuple[str, str, str, str, bool]]:
    """Build the lead comparison as an Invoice-vs-PO field table.

    Values are read straight from the generated fixtures and the discrepant
    line match already produced by reconciliation; nothing is recomputed.
    """
    po = fixture_index["purchase_orders"][case["purchase_order_id"]]
    invoice = fixture_index["invoices"][case.get("invoice_ids", [""])[-1]]
    supplier = fixture_index["suppliers"][po["supplier_id"]]
    currency = invoice.get("currency", po.get("currency", "EUR"))

    line_matches = case.get("line_matches", [])
    discrepant = next(
        (match for match in line_matches if match.get("labels") and match.get("labels") != ["clean_match"]),
        line_matches[0] if line_matches else {},
    )
    po_line = fixture_index["purchase_order_lines"].get(discrepant.get("po_line_id", ""))
    invoice_line = fixture_index["invoice_lines"].get(discrepant.get("invoice_line_id", ""))

    inv_vendor = invoice.get("supplier_name_raw", supplier.get("canonical_name"))
    po_vendor = supplier.get("canonical_name")
    rows: list[tuple[str, str, str, str, bool]] = [
        ("Vendor", str(inv_vendor), str(po_vendor), "", str(inv_vendor) != str(po_vendor)),
    ]

    if po_line and invoice_line:
        rows.append(_hero_numeric_row(
            "Quantity",
            invoice_line.get("quantity_billed"),
            po_line.get("quantity_ordered"),
        ))
        rows.append(_hero_money_row(
            "Unit price",
            invoice_line.get("unit_price"),
            po_line.get("unit_price"),
            currency,
        ))
        rows.append(_hero_money_row(
            "Line total",
            invoice_line.get("line_total"),
            po_line.get("line_total"),
            currency,
        ))

    rows.append(_hero_money_row(
        "Tax",
        invoice.get("tax_amount"),
        po.get("tax_amount"),
        currency,
    ))
    return rows


def _hero_numeric_row(field: str, invoice_value: Any, po_value: Any) -> tuple[str, str, str, str, bool]:
    inv = _to_float(invoice_value)
    pov = _to_float(po_value)
    is_disagreement = inv is not None and pov is not None and inv != pov
    delta = ""
    if is_disagreement:
        diff = inv - pov
        delta = f"{'+' if diff >= 0 else '−'}{abs(diff):g}"
    return (field, _trim_number(invoice_value), _trim_number(po_value), delta, is_disagreement)


def _hero_money_row(field: str, invoice_value: Any, po_value: Any, currency: str) -> tuple[str, str, str, str, bool]:
    inv = _to_float(invoice_value)
    pov = _to_float(po_value)
    is_disagreement = inv is not None and pov is not None and inv != pov
    delta = ""
    if is_disagreement:
        diff = inv - pov
        delta = f"{'+' if diff >= 0 else '−'}{_eur(abs(diff), currency)}"
    return (
        field,
        _eur(invoice_value, currency),
        _eur(po_value, currency),
        delta,
        is_disagreement,
    )


def _interactive_explorer(
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
    fixture_index: dict[str, dict[str, Any]],
    default_bundle_id: str,
) -> str:
    """Render the Slice 10B hero case plus quiet index reviewer.

    Every case is still embedded at generation time. Inline JavaScript only
    toggles which pre-rendered hero core and detail block is active.
    """
    details = "\n".join(
        _case_detail(case, reliability_cases.get(case["bundle_id"], {}), fixture_index, default_bundle_id)
        for case in cases
    )
    quiet_index = _case_index(cases, reliability_cases, default_bundle_id)
    return f"""
    <section class="explorer" data-explorer data-explorer-default="{_e(default_bundle_id)}" aria-labelledby="explorer-title">
      <div id="interactive-case-explorer">
{_hero()}
{_hero_discrepancy_story(cases, reliability_cases, fixture_index, default_bundle_id)}
      </div>
      <div class="case-detail-region" aria-labelledby="detail-title">
        <div class="section-heading">
          <div>
            <div class="kicker">Inspect the documents</div>
            <h2 id="detail-title">Document evidence for the selected case</h2>
          </div>
          <p>Raw purchase order, invoice, receipt, detected label, evidence key, confidence, and route remain available below the hero frame.</p>
        </div>
{details}
      </div>
{quiet_index}
      <p class="explorer-fallback-note">JavaScript is disabled, so the pre-rendered cases and the native full index remain readable without interaction scripting.</p>
    </section>
""".rstrip()


def _case_detail(
    case: dict[str, Any],
    reliability: dict[str, Any],
    fixture_index: dict[str, dict[str, Any]],
    default_bundle_id: str,
) -> str:
    bundle_id = case["bundle_id"]
    active = " is-active" if bundle_id == default_bundle_id else ""
    return f"""
        <div class="case-detail{active}" data-detail="{_e(bundle_id)}">
{_document_story(case, reliability, fixture_index)}
        </div>
""".rstrip()


def _signature_rail(
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
    default_bundle_id: str,
) -> str:
    buttons = "\n".join(
        _signature_button(case, title, purpose, reliability_cases.get(case["bundle_id"], {}), default_bundle_id)
        for case, title, purpose in _signature_cases(cases, reliability_cases)
    )
    return f"""
        <section class="signature-rail" aria-labelledby="signature-title">
          <div class="signature-rail-header">
            <div>
              <div class="kicker">Explore the trust story</div>
              <h2 id="signature-title" class="condensed-label">Signature cases</h2>
            </div>
            <p>Three curated synthetic cases show the full route arc: no over-flag, discrepancy caught, bad data blocked.</p>
          </div>
          <div class="signature-options" role="group" aria-label="Signature cases">
{buttons}
          </div>
        </section>
""".rstrip()


def _signature_cases(
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
) -> list[tuple[dict[str, Any], str, str]]:
    selected: list[tuple[dict[str, Any], str, str]] = []
    definitions = [
        (_first_case(cases, ["clean_match"]), "Clean match", "does not over-flag"),
        (_first_case(cases, ["unit_price_mismatch"]), "Unit price mismatch", "catches the discrepancy"),
        (_first_case(cases, ["schema_validation_failure"]), "Schema validation failure", "blocks bad data"),
    ]
    for case, title, purpose in definitions:
        if case is not None:
            selected.append((case, title, purpose))

    if len(selected) < 3:
        for fallback in (
            _first_route_case(cases, reliability_cases, "auto_accept"),
            _first_route_case(cases, reliability_cases, "needs_review"),
            _first_route_case(cases, reliability_cases, "blocked"),
        ):
            if fallback is not None and all(item[0]["bundle_id"] != fallback["bundle_id"] for item in selected):
                selected.append((fallback, _story_title(fallback.get("discrepancy_labels", [])), "route example"))
            if len(selected) == 3:
                break

    return selected[:3]


def _signature_button(
    case: dict[str, Any],
    title: str,
    purpose: str,
    reliability: dict[str, Any],
    default_bundle_id: str,
) -> str:
    bundle_id = case["bundle_id"]
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    active = " is-active" if bundle_id == default_bundle_id else ""
    pressed = "true" if active else "false"
    return f"""            <button type="button" class="signature-case route-{_class_token(route)}{active}" data-case="{_e(bundle_id)}" data-signature-case="{_e(bundle_id)}" aria-pressed="{pressed}">
              <span class="signature-case-title">{_e(title)}</span>
              <span class="signature-case-purpose">{_e(purpose)}</span>
              <span class="pill route-{_class_token(route)}">{_e(route)}</span>
            </button>""".rstrip()


def _case_index(
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
    default_bundle_id: str,
) -> str:
    entries = "\n".join(
        _case_index_entry(index, case, reliability_cases.get(case["bundle_id"], {}), default_bundle_id)
        for index, case in enumerate(cases)
    )
    return f"""
      <details class="case-index" data-case-index>
        <summary>Browse all {len(cases)} cases</summary>
        <div class="case-index-list">
{entries}
        </div>
      </details>
""".rstrip()


def _case_index_entry(
    index: int,
    case: dict[str, Any],
    reliability: dict[str, Any],
    default_bundle_id: str,
) -> str:
    bundle_id = case["bundle_id"]
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    active = " is-active" if bundle_id == default_bundle_id else ""
    current = ' aria-current="true"' if active else ""
    return f"""          <button type="button" class="case-index-button route-{_class_token(route)}{active}" data-case="{_e(bundle_id)}" data-index-case="{_e(bundle_id)}"{current}>
            <span class="case-index-number">{index + 1:02d}</span>
            <span>
              <span class="case-index-title">{_e(_story_title(case.get("discrepancy_labels", [])))}</span>
              <span class="case-index-meta">{_e(bundle_id)}</span>
            </span>
            <span class="pill route-{_class_token(route)}">{_e(route)}</span>
          </button>""".rstrip()


def _chip_label(labels: list[str]) -> str:
    if not labels or labels == ["clean_match"]:
        return "clean match"
    return ", ".join(label.replace("_", " ") for label in labels)


def _document_story(
    case: dict[str, Any],
    reliability: dict[str, Any],
    fixture_index: dict[str, dict[str, Any]],
) -> str:
    bundle_id = case["bundle_id"]
    labels = case.get("discrepancy_labels", [])
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    return f"""
        <article class="story-card" data-curated-case="{_e(bundle_id)}">
          <div class="story-topline">
            <div class="story-title">
              <h3>{_e(_story_title(labels))}</h3>
              <p class="bundle">{_e(bundle_id)}</p>
            </div>
            <div class="pills">
              <span class="pill route-{_class_token(route)}">{_e(route)}</span>
              <span class="pill">{_e(_format_confidence(reliability.get("confidence_score")))}</span>
            </div>
          </div>
          <div class="document-grid">
            {_purchase_order_panel(case, fixture_index)}
            {_invoice_panel(case, fixture_index)}
            {_receipt_panel(case, fixture_index)}
          </div>
          {_explanation_block(case, reliability)}
        </article>
""".rstrip()


def _explorer_script() -> str:
    """Inline, dependency-free selection logic for the reviewer.

    Avoids the ``/``-``/`` comment sequence so the generated HTML stays free of
    any substring matching the reviewer's no-external-URL guard. It merely
    toggles which pre-rendered case is visible.
    """
    return """
(function () {
  var root = document.documentElement;
  root.classList.add('js-on');
  var explorer = document.querySelector('[data-explorer]');
  if (!explorer) { return; }
  var heroCores = Array.prototype.slice.call(explorer.querySelectorAll('[data-hero-core]'));
  var details = Array.prototype.slice.call(explorer.querySelectorAll('[data-detail]'));
  var controls = Array.prototype.slice.call(explorer.querySelectorAll('[data-case]'));
  var startId = explorer.getAttribute('data-explorer-default');
  if (!heroCores.length || !details.length || !controls.length) { return; }
  function matches(element, name, id) {
    return element.getAttribute(name) === id;
  }
  function setActive(id) {
    heroCores.forEach(function (core) {
      core.classList.toggle('is-active', matches(core, 'data-hero-core', id));
    });
    details.forEach(function (detail) {
      detail.classList.toggle('is-active', matches(detail, 'data-detail', id));
    });
    controls.forEach(function (control) {
      var active = matches(control, 'data-case', id);
      control.classList.toggle('is-active', active);
      if (control.hasAttribute('data-signature-case')) {
        control.setAttribute('aria-pressed', active ? 'true' : 'false');
      }
      if (control.hasAttribute('data-index-case')) {
        if (active) {
          control.setAttribute('aria-current', 'true');
        } else {
          control.removeAttribute('aria-current');
        }
      }
    });
  }
  controls.forEach(function (control) {
    control.addEventListener('click', function () {
      setActive(control.getAttribute('data-case'));
    });
  });
  setActive(startId);
})();
""".strip()


def _purchase_order_panel(case: dict[str, Any], fixture_index: dict[str, dict[str, Any]]) -> str:
    po = fixture_index["purchase_orders"][case["purchase_order_id"]]
    supplier = fixture_index["suppliers"][po["supplier_id"]]
    lines = [fixture_index["purchase_order_lines"][line_id] for line_id in po.get("line_ids", [])]
    return f"""
            <section class="doc-panel" data-document-panel="Purchase Order">
              <h4>Purchase Order</h4>
              <p class="doc-id">{_e(po["purchase_order_id"])}</p>
              <div class="doc-meta">
                {_meta_row("Supplier", supplier["canonical_name"], _header_highlight(case, po["purchase_order_id"], "supplier"))}
                {_meta_row("Date", po["issue_date"], False)}
                {_meta_row("Expected", po["expected_receipt_date"], False)}
                {_meta_row("Total", _money(po["total_amount"], po["currency"]), False)}
              </div>
              {_line_table("PO", lines, case)}
            </section>
""".rstrip()


def _invoice_panel(case: dict[str, Any], fixture_index: dict[str, dict[str, Any]]) -> str:
    invoices = [fixture_index["invoices"][invoice_id] for invoice_id in case.get("invoice_ids", [])]
    blocks = []
    for invoice in invoices:
        lines = [fixture_index["invoice_lines"][line_id] for line_id in invoice.get("line_ids", [])]
        duplicate_badge = ""
        if invoice.get("duplicate_of_invoice_id"):
            duplicate_badge = f'<span class="issue-badge">duplicate of {_e(invoice["duplicate_of_invoice_id"])}</span>'
        blocks.append(
            f"""
              <div class="sub-document">
                <p class="doc-id">{_field_span(invoice["invoice_id"], _header_highlight(case, invoice["invoice_id"], "invoice_id"))}{duplicate_badge}</p>
                <div class="doc-meta">
                  {_meta_row("Supplier", invoice["supplier_name_raw"], _header_highlight(case, invoice["invoice_id"], "supplier"))}
                  {_meta_row("Number", invoice["invoice_number"], _header_highlight(case, invoice["invoice_id"], "invoice_number"))}
                  {_meta_row("Date", invoice["invoice_date"], _header_highlight(case, invoice["invoice_id"], "invoice_date"))}
                  {_meta_row("Total", _money(invoice["total_amount"], invoice["currency"]), _header_highlight(case, invoice["invoice_id"], "total_amount"))}
                </div>
                {_line_table("Invoice", lines, case)}
              </div>
""".rstrip()
        )
    return f"""
            <section class="doc-panel" data-document-panel="Invoice">
              <h4>Invoice</h4>
{chr(10).join(blocks)}
            </section>
""".rstrip()


def _receipt_panel(case: dict[str, Any], fixture_index: dict[str, dict[str, Any]]) -> str:
    receipts = [fixture_index["receipts"][receipt_id] for receipt_id in case.get("receipt_ids", [])]
    blocks = []
    for receipt in receipts:
        supplier = fixture_index["suppliers"][receipt["supplier_id"]]
        lines = [fixture_index["receipt_lines"][line_id] for line_id in receipt.get("line_ids", [])]
        blocks.append(
            f"""
              <div class="sub-document">
                <p class="doc-id">{_e(receipt["receipt_id"])}</p>
                <div class="doc-meta">
                  {_meta_row("Supplier", receipt.get("supplier_name_raw", supplier["canonical_name"]), _header_highlight(case, receipt["receipt_id"], "supplier"))}
                  {_meta_row("Number", receipt["receipt_number"], False)}
                  {_meta_row("Date", receipt["receipt_date"], _header_highlight(case, receipt["receipt_id"], "receipt_date"))}
                  {_meta_row("PO", receipt["related_purchase_order_id"], False)}
                </div>
                {_line_table("Receipt", lines, case)}
              </div>
""".rstrip()
        )
    return f"""
            <section class="doc-panel" data-document-panel="Receipt">
              <h4>Receipt</h4>
{chr(10).join(blocks)}
            </section>
""".rstrip()


def _line_table(kind: str, lines: list[dict[str, Any]], case: dict[str, Any]) -> str:
    if kind == "PO":
        headers = ["Item", "Qty", "Unit", "Total"]
        rows = [
            [
                line["description"],
                line["quantity_ordered"],
                line["unit_price"],
                line["line_total"],
                line["po_line_id"],
            ]
            for line in sorted(lines, key=lambda item: item["line_number"])
        ]
    elif kind == "Invoice":
        headers = ["Item", "Qty", "Unit", "Total"]
        rows = [
            [
                line["description"],
                line["quantity_billed"],
                line["unit_price"],
                line["line_total"],
                line["invoice_line_id"],
            ]
            for line in sorted(lines, key=lambda item: item["line_number"])
        ]
    else:
        headers = ["Item", "Qty", "Unit", "Received"]
        rows = [
            [
                line["sku_raw"],
                line["quantity_received"],
                line["unit_of_measure"],
                line["received_date"],
                line["receipt_line_id"],
            ]
            for line in sorted(lines, key=lambda item: item["line_number"])
        ]

    header_html = "".join(f"<th>{_e(header)}</th>" for header in headers)
    row_html = "\n".join(_line_row(kind, row, case) for row in rows)
    return f"""
              <table class="mini-table">
                <thead><tr>{header_html}</tr></thead>
                <tbody>
{row_html}
                </tbody>
              </table>
""".rstrip()


def _line_row(kind: str, row: list[str], case: dict[str, Any]) -> str:
    item, qty, unit, total_or_date, line_id = row
    line_class = ' class="line-highlight"' if _line_highlight(case, line_id) else ""
    qty_highlight = _field_highlight(case, line_id, _quantity_field(kind))
    unit_highlight = _field_highlight(case, line_id, _unit_field(kind))
    return f"""
                  <tr{line_class}>
                    <td>{_e(item)}</td>
                    <td>{_field_span(qty, qty_highlight)}</td>
                    <td>{_field_span(unit, unit_highlight)}</td>
                    <td>{_e(total_or_date)}</td>
                  </tr>
""".rstrip()


def _explanation_block(case: dict[str, Any], reliability: dict[str, Any]) -> str:
    evidence = case.get("evidence", [])
    labels = case.get("discrepancy_labels", [])
    first_evidence = evidence[0] if evidence else {}
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    return f"""
          <section class="explanation-block" data-explanation-block="{_e(case['bundle_id'])}">
            <div class="pills">
              {_label_pills(labels)}
              <span class="pill route-{_class_token(route)}">{_e(route)}</span>
              <span class="pill">confidence {_e(_format_confidence(reliability.get("confidence_score")))}</span>
            </div>
            <div class="explanation-grid">
              <p class="answer"><strong>What happened?</strong>{_e(_story_title(labels))}</p>
              <p class="answer"><strong>Why flagged?</strong>{_e(first_evidence.get("explanation", case.get("explanation", "No discrepancy evidence items; deterministic line matches are clean.")))}</p>
              <p class="answer"><strong>Evidence</strong>{_e(_evidence_summary(first_evidence))}</p>
              <p class="answer"><strong>Route assigned</strong>{_e(route)} for local human-review workflow support.</p>
            </div>
          </section>
""".rstrip()


def _case_row(case: dict[str, Any], reliability: dict[str, Any]) -> str:
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    return f"""
            <tr>
              <td>{_e(case["bundle_id"])}</td>
              <td>{_label_pills(case.get("discrepancy_labels", []))}</td>
              <td><span class="pill route-{_class_token(route)}">{_e(route)}</span></td>
              <td>{_e(_format_confidence(reliability.get("confidence_score")))}</td>
              <td>{_e(case.get("explanation", "Not available"))}</td>
            </tr>
""".rstrip()


def _reproduction_commands() -> str:
    commands = [
        "python3 scripts/generate_synthetic_data.py",
        "python3 scripts/validate_fixtures.py",
        "python3 scripts/run_reconciliation.py",
        "python3 scripts/evaluate_reconciliation.py",
        "python3 scripts/score_reliability.py",
        "python3 scripts/generate_report.py",
        "python3 scripts/generate_reviewer.py",
        "python3 -m pytest",
    ]
    items = "\n".join(f"        <li><code>{_e(command)}</code></li>" for command in commands)
    return f"""
    <section class="command-section" aria-labelledby="commands-title">
      <h2 id="commands-title">Reproduction Commands</h2>
      <ul class="command-list">
{items}
      </ul>
      <p class="utility-link"><a href="documents/index.html">View the synthetic source document pack</a></p>
    </section>
""".rstrip()


def _metric(label: str, value: Any) -> str:
    return f"""
          <div class="metric">
            <span>{_e(label)}</span>
            <strong>{_e(_format_metric(value))}</strong>
          </div>
""".rstrip()


def _fixture_index(fixtures: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "suppliers": {item["supplier_id"]: item for item in fixtures.get("suppliers", [])},
        "purchase_orders": {item["purchase_order_id"]: item for item in fixtures.get("purchase_orders", [])},
        "purchase_order_lines": {item["po_line_id"]: item for item in fixtures.get("purchase_order_lines", [])},
        "invoices": {item["invoice_id"]: item for item in fixtures.get("invoices", [])},
        "invoice_lines": {item["invoice_line_id"]: item for item in fixtures.get("invoice_lines", [])},
        "receipts": {item["receipt_id"]: item for item in fixtures.get("receipts", [])},
        "receipt_lines": {item["receipt_line_id"]: item for item in fixtures.get("receipt_lines", [])},
    }


def _story_title(labels: list[str]) -> str:
    if labels == ["clean_match"]:
        return "Clean match across PO, invoice, and receipt"
    return ", ".join(label.replace("_", " ") for label in labels).title()


def _meta_row(label: str, value: Any, highlight: bool) -> str:
    return f"""
                  <div class="meta-row">
                    <span>{_e(label)}</span>
                    <span>{_field_span(value, highlight)}</span>
                  </div>
""".rstrip()


def _field_span(value: Any, highlight: bool) -> str:
    css_class = ' class="field-highlight"' if highlight else ""
    return f"<span{css_class}>{_e(value)}</span>"


def _money(amount: Any, currency: str) -> str:
    return f"{amount} {currency}"


def _strip_prefix(value: str, prefix: str) -> str:
    text = str(value)
    if text.lower().startswith(prefix.lower()):
        return text[len(prefix):]
    return text


_CURRENCY_SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£"}


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _trim_number(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return str(value)
    if number == int(number):
        return str(int(number))
    return f"{number:g}"


def _eur(amount: Any, currency: str) -> str:
    number = _to_float(amount)
    symbol = _CURRENCY_SYMBOLS.get(currency, "")
    if number is None:
        return f"{amount} {currency}".strip()
    formatted = f"{number:,.2f}"
    if symbol:
        return f"{symbol}{formatted}"
    return f"{formatted} {currency}".strip()


def _confidence_note(route: str) -> str:
    if route == "auto_accept":
        return "above threshold"
    if route == "blocked":
        return "blocked route"
    return "below threshold"


def _route_action_label(route: str) -> str:
    if route == "auto_accept":
        return "No review needed"
    if route == "blocked":
        return "Block for manual review"
    return "Route to human review"


def _line_highlight(case: dict[str, Any], line_id: str) -> bool:
    affected = _affected_line_ids(case)
    labels = set(case.get("discrepancy_labels", []))
    return bool(affected and line_id in affected and labels & {"quantity_mismatch", "unit_price_mismatch"})


def _field_highlight(case: dict[str, Any], line_id: str, field_name: str) -> bool:
    labels = set(case.get("discrepancy_labels", []))
    if "quantity_mismatch" in labels and line_id in _affected_line_ids(case):
        return field_name in {"quantity_ordered", "quantity_billed", "quantity_received"}
    if "unit_price_mismatch" in labels and line_id in _affected_line_ids(case):
        return field_name in {"po_line.unit_price", "invoice_line.unit_price"}
    if "low_confidence_extraction" in labels:
        source_document = _first_evidence(case).get("observed_values", {}).get("source_document_id")
        if source_document and line_id.startswith("inv_line_"):
            return field_name == "invoice_line.unit_price"
    return False


def _header_highlight(case: dict[str, Any], document_id: str, field_name: str) -> bool:
    labels = set(case.get("discrepancy_labels", []))
    evidence = _first_evidence(case)
    affected_documents = set(evidence.get("affected_document_ids", []))
    compared_fields = set(evidence.get("compared_fields", []))
    observed = evidence.get("observed_values", {})

    if "supplier_alias_mismatch" in labels:
        return document_id in affected_documents and field_name == "supplier"
    if "duplicate_invoice" in labels:
        return document_id in affected_documents and field_name in {"invoice_id", "invoice_number", "invoice_date", "total_amount"}
    if "low_confidence_extraction" in labels:
        return observed.get("source_document_id") == document_id and field_name in compared_fields
    if "schema_validation_failure" in labels:
        return observed.get("source_document_id") == document_id and field_name in compared_fields
    return False


def _affected_line_ids(case: dict[str, Any]) -> set[str]:
    return {
        line_id
        for evidence in case.get("evidence", [])
        for line_id in evidence.get("affected_line_ids", [])
    }


def _first_evidence(case: dict[str, Any]) -> dict[str, Any]:
    evidence = case.get("evidence", [])
    return evidence[0] if evidence else {}


def _quantity_field(kind: str) -> str:
    return {
        "PO": "quantity_ordered",
        "Invoice": "quantity_billed",
        "Receipt": "quantity_received",
    }[kind]


def _unit_field(kind: str) -> str:
    return {
        "PO": "po_line.unit_price",
        "Invoice": "invoice_line.unit_price",
        "Receipt": "receipt_line.unit_of_measure",
    }[kind]


def _evidence_summary(evidence: dict[str, Any]) -> str:
    if not evidence:
        return "Clean deterministic line matches across purchase order, invoice, and receipt."
    basis = evidence.get("detection_basis", "unknown_basis")
    values = evidence.get("observed_values", {})
    value_summary = ", ".join(f"{key}={value}" for key, value in sorted(values.items()))
    if value_summary:
        return f"{basis}: {value_summary}"
    return basis


def _label_pills(labels: list[str]) -> str:
    return "".join(f'<span class="pill">{_e(label)}</span>' for label in labels)


def _first_case(cases: list[dict[str, Any]], labels: list[str]) -> dict[str, Any] | None:
    return next((case for case in cases if case.get("discrepancy_labels") == labels), None)


def _first_route_case(
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
    route: str,
) -> dict[str, Any] | None:
    return next(
        (
            case
            for case in cases
            if reliability_cases.get(case["bundle_id"], {}).get("reliability_route") == route
        ),
        None,
    )


def _select_hero_case(
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    # Presentation-only hero selection. Prefer the discrepancy types that read
    # most clearly as a field-level comparison (unit price, then quantity), so
    # the lead story communicates "Crosswise found a discrepancy and explains
    # why" at a glance. This does not change reconciliation, evaluation,
    # reliability, routing, or generated data.
    preferred_labels = (["unit_price_mismatch"], ["quantity_mismatch"])
    for labels in preferred_labels:
        match = next((case for case in cases if case.get("discrepancy_labels") == labels), None)
        if match is not None:
            return match

    needs_review = next(
        (
            case
            for case in cases
            if reliability_cases.get(case["bundle_id"], {}).get("reliability_route") == "needs_review"
        ),
        None,
    )
    if needs_review is not None:
        return needs_review

    non_clean = next(
        (case for case in cases if case.get("discrepancy_labels") != ["clean_match"]),
        None,
    )
    if non_clean is not None:
        return non_clean

    if not cases:
        raise ValueError("Static reviewer requires at least one reconciliation case.")
    return cases[0]


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, int):
        return str(value)
    return "Not available"


def _format_confidence(value: Any) -> str:
    if isinstance(value, (float, int)):
        return f"{float(value):.2f}"
    return "Not available"


def _class_token(value: Any) -> str:
    return "".join(char if char.isalnum() or char == "_" else "_" for char in str(value))


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)
