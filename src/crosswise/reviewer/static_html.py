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


def write_static_reviewer(payloads: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_static_reviewer(payloads), encoding="utf-8")
    return output_path


def render_static_reviewer(payloads: dict[str, Any]) -> str:
    reconciliation = payloads["reconciliation"]
    evaluation = payloads["evaluation"]
    reliability = payloads["reliability"]
    cases = sorted(reconciliation.get("cases", []), key=lambda item: item["bundle_id"])
    reliability_cases = {
        case["bundle_id"]: case
        for case in sorted(reliability.get("cases", []), key=lambda item: item["bundle_id"])
    }

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
            _hero(),
            _notice_band(),
            _pipeline_summary(),
            _metric_sections(evaluation, reliability),
            _example_cards(cases, reliability_cases),
            _case_table(cases, reliability_cases),
            _reproduction_commands(),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _css() -> str:
    return """
:root {
  --ink: #f4efe6;
  --muted: #bdb1a1;
  --paper: #211f1b;
  --panel: #2a2721;
  --panel-strong: #332f27;
  --line: #514838;
  --amber: #d8a441;
  --amber-soft: #5c4724;
  --ok: #9eb77e;
  --review: #d8a441;
  --blocked: #d47663;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  background: var(--paper);
  color: var(--ink);
  font-family: Avenir, "Gill Sans", "Trebuchet MS", sans-serif;
  line-height: 1.5;
}

.shell {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 34px 0 48px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(260px, 0.6fr);
  gap: 24px;
  align-items: end;
  padding: 28px 0 22px;
  border-bottom: 1px solid var(--line);
}

.kicker {
  color: var(--amber);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

h1, h2, h3, p {
  margin: 0;
}

h1 {
  margin-top: 8px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(42px, 8vw, 84px);
  font-weight: 500;
  line-height: 0.95;
}

.subtitle {
  margin-top: 14px;
  color: var(--muted);
  font-size: 18px;
}

.hero-note {
  color: var(--muted);
  border-left: 3px solid var(--amber);
  padding: 2px 0 2px 16px;
}

.notice-band,
.summary-grid,
.example-grid,
.case-section,
.command-section {
  margin-top: 22px;
}

.notice-band {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.notice,
.panel,
.example-card,
.case-section,
.command-section {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.notice {
  padding: 16px;
}

.notice strong {
  display: block;
  color: var(--amber);
  margin-bottom: 5px;
}

.pipeline {
  margin-top: 22px;
  padding: 18px 0;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}

.pipeline h2,
.case-section h2,
.command-section h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
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
  min-height: 92px;
  padding: 12px;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--muted);
  counter-increment: step;
}

.pipeline li::before {
  content: counter(step, decimal-leading-zero);
  display: block;
  color: var(--amber);
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 8px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  padding: 18px;
}

.panel h2 {
  font-size: 18px;
  margin-bottom: 14px;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.metric {
  padding: 14px;
  background: #1c1a17;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.metric span {
  display: block;
  color: var(--muted);
  font-size: 13px;
}

.metric strong {
  display: block;
  margin-top: 4px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 30px;
  font-weight: 500;
}

.example-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.example-card {
  padding: 18px;
}

.example-card h3 {
  font-size: 15px;
  color: var(--amber);
  margin-bottom: 10px;
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
  margin-top: 12px;
}

.pill {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--amber-soft);
  color: var(--ink);
  font-size: 12px;
  font-weight: 700;
}

.route-auto_accept {
  background: rgba(158, 183, 126, 0.18);
  color: var(--ok);
}

.route-needs_review {
  background: rgba(216, 164, 65, 0.18);
  color: var(--review);
}

.route-blocked {
  background: rgba(212, 118, 99, 0.18);
  color: var(--blocked);
}

.case-section,
.command-section {
  padding: 18px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 860px;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 10px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}

th {
  color: var(--amber);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

td {
  color: var(--muted);
  font-size: 14px;
}

td:first-child,
td:nth-child(4) {
  color: var(--ink);
  font-family: Menlo, Consolas, monospace;
  font-size: 13px;
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
  background: #1c1a17;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow-x: auto;
}

@media (max-width: 880px) {
  .hero,
  .notice-band,
  .summary-grid,
  .example-grid,
  .pipeline ol {
    grid-template-columns: 1fr;
  }

  .metrics {
    grid-template-columns: 1fr;
  }
}
""".strip()


def _hero() -> str:
    return """
    <section class="hero">
      <div>
        <div class="kicker">Crosswise Reviewer</div>
        <h1>Crosswise Reviewer</h1>
        <p class="subtitle">AI Document Reconciliation</p>
      </div>
      <p class="hero-note">Static local reviewer interface for generated reconciliation, evaluation, and reliability outputs.</p>
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
    <section class="summary-grid" aria-label="Metrics summaries">
      <div class="panel">
        <h2>Evaluation Summary</h2>
        <div class="metrics">
          {_metric("Overall precision", evaluation_summary.get("overall_precision"))}
          {_metric("Overall recall", evaluation_summary.get("overall_recall"))}
          {_metric("Overall F1", evaluation_summary.get("overall_f1"))}
          {_metric("Macro F1", evaluation_summary.get("macro_f1"))}
        </div>
      </div>
      <div class="panel">
        <h2>Reliability Summary</h2>
        <div class="metrics">
          {_metric("auto_accept count", reliability_summary.get("auto_accept"))}
          {_metric("needs_review count", reliability_summary.get("needs_review"))}
          {_metric("blocked count", reliability_summary.get("blocked"))}
          {_metric("Average confidence", reliability_summary.get("average_confidence"))}
        </div>
      </div>
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
          <span class="pill">{_e(_format_metric(reliability.get("confidence_score")))}</span>
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


def _case_row(case: dict[str, Any], reliability: dict[str, Any]) -> str:
    route = reliability.get("reliability_route", case.get("route", "unknown"))
    return f"""
            <tr>
              <td>{_e(case["bundle_id"])}</td>
              <td>{_label_pills(case.get("discrepancy_labels", []))}</td>
              <td><span class="pill route-{_class_token(route)}">{_e(route)}</span></td>
              <td>{_e(_format_metric(reliability.get("confidence_score")))}</td>
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
    </section>
""".rstrip()


def _metric(label: str, value: Any) -> str:
    return f"""
          <div class="metric">
            <span>{_e(label)}</span>
            <strong>{_e(_format_metric(value))}</strong>
          </div>
""".rstrip()


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


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, int):
        return str(value)
    return "Not available"


def _class_token(value: Any) -> str:
    return "".join(char if char.isalnum() or char == "_" else "_" for char in str(value))


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)
