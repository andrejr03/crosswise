"""Deterministic local evidence report rendering.

This module summarizes existing Crosswise generated outputs only. It does not
run OCR, APIs, model calls, reconciliation, evaluation, or reliability scoring.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_OUTPUT_PATHS = {
    "fixtures": Path("data/synthetic/fixtures_v1_0.json"),
    "ground_truth": Path("data/ground_truth/ground_truth_v1_0.json"),
    "reconciliation": Path("data/reconciliation/reconciliation_v1_0.json"),
    "evaluation": Path("data/evaluation/evaluation_v1_0.json"),
    "reliability": Path("data/reliability/reliability_v1_0.json"),
}
DEFAULT_OUTPUT_PATH = Path("docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md")


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


def generate_local_evidence_report(repo_root: Path, output_path: Path | None = None) -> Path:
    payloads = load_required_outputs(repo_root)
    target = output_path or repo_root / DEFAULT_OUTPUT_PATH
    return write_local_evidence_report(payloads, target)


def write_local_evidence_report(payloads: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_local_evidence_report(payloads), encoding="utf-8")
    return output_path


def render_local_evidence_report(payloads: dict[str, Any]) -> str:
    fixtures = payloads["fixtures"]
    reconciliation = payloads["reconciliation"]
    evaluation = payloads["evaluation"]
    reliability = payloads["reliability"]

    bundles = sorted(fixtures.get("document_bundles", []), key=lambda item: item["bundle_id"])
    fixture_label_counts = Counter(
        label
        for bundle in bundles
        for label in bundle.get("discrepancy_labels", [])
    )
    reconciliation_cases = sorted(reconciliation.get("cases", []), key=lambda item: item["bundle_id"])
    reliability_cases = {
        case["bundle_id"]: case for case in sorted(reliability.get("cases", []), key=lambda item: item["bundle_id"])
    }
    detected_labels = sorted(
        {
            label
            for case in reconciliation_cases
            for label in case.get("discrepancy_labels", [])
        }
    )

    sections = [
        "# Crosswise Local Evidence Report",
        _project_summary(),
        _pipeline_summary(),
        _fixture_summary(len(bundles), fixture_label_counts),
        _reconciliation_summary(reconciliation, reconciliation_cases, reliability_cases, detected_labels),
        _evaluation_summary(evaluation),
        _reliability_summary(reliability),
        _evidence_examples(reconciliation_cases, reliability_cases),
        _limitations(),
        _reproduction_commands(),
    ]
    return "\n\n".join(sections) + "\n"


def _project_summary() -> str:
    return "\n".join(
        [
            "## 1. Project Summary",
            "",
            "Crosswise is a local AI document reconciliation project for structured invoice, purchase order, and receipt records. It detects synthetic discrepancy labels, preserves evidence for reviewer decisions, and routes uncertain or risky cases into a human-review workflow.",
            "",
            "Crosswise is synthetic-data-only: this report uses generated fixtures and contains no real invoices, real company data, PII, payment information, bank details, or tax identifiers.",
            "",
            "Crosswise output is not accounting, tax, legal, financial, payment, compliance, or business-action advice.",
        ]
    )


def _pipeline_summary() -> str:
    return "\n".join(
        [
            "## 2. Pipeline Summary",
            "",
            "- Synthetic data generation creates deterministic invoice, purchase order, receipt, fixture, and ground-truth JSON records.",
            "- Schema validation and normalization checks fixture structure, references, arithmetic, dates, currency, taxonomy, and synthetic-only constraints.",
            "- Reconciliation baseline performs deterministic supplier, SKU, document, and line-item matching and emits evidence-backed discrepancy cases.",
            "- Evaluation harness compares detected labels with generated ground truth and reports precision, recall, F1, macro F1, and per-label metrics.",
            "- Reliability routing assigns deterministic confidence scores and conservative routes: `auto_accept`, `needs_review`, or `blocked`.",
        ]
    )


def _fixture_summary(bundle_count: int, label_counts: Counter[str]) -> str:
    label_rows = "\n".join(
        f"| `{label}` | {count} |"
        for label, count in sorted(label_counts.items())
    )
    return "\n".join(
        [
            "## 3. Fixture Summary",
            "",
            f"- Number of bundles: {bundle_count}",
            "- Generated fixture paths:",
            "  - `data/synthetic/fixtures_v1_0.json`",
            "  - `data/ground_truth/ground_truth_v1_0.json`",
            "",
            "| Discrepancy label | Bundle count |",
            "| --- | ---: |",
            label_rows,
        ]
    )


def _reconciliation_summary(
    reconciliation: dict[str, Any],
    cases: list[dict[str, Any]],
    reliability_cases: dict[str, dict[str, Any]],
    detected_labels: list[str],
) -> str:
    clean = _first_case(cases, ["clean_match"])
    review = next(
        (
            case
            for case in cases
            if reliability_cases.get(case["bundle_id"], {}).get("reliability_route") == "needs_review"
        ),
        None,
    )
    blocked = next(
        (
            case
            for case in cases
            if reliability_cases.get(case["bundle_id"], {}).get("reliability_route") == "blocked"
        ),
        None,
    )
    parts = [
        "## 4. Reconciliation Summary",
        "",
        f"- Number of cases: {reconciliation.get('summary', {}).get('detected_cases', len(cases))}",
        f"- Detected labels: {', '.join(f'`{label}`' for label in detected_labels)}",
        f"- Example clean match: {_case_label(clean) if clean else 'Not available'}",
        f"- Example needs-review case: {_case_label(review) if review else 'Not available'}",
        f"- Example blocked case: {_case_label(blocked) if blocked else 'Not available'}",
    ]
    return "\n".join(parts)


def _evaluation_summary(evaluation: dict[str, Any]) -> str:
    summary = evaluation.get("summary", {})
    rows = "\n".join(
        "| `{label}` | {precision} | {recall} | {f1} | {tp} | {fp} | {fn} |".format(
            label=label,
            precision=_format_metric(metrics.get("precision")),
            recall=_format_metric(metrics.get("recall")),
            f1=_format_metric(metrics.get("f1")),
            tp=metrics.get("true_positives", 0),
            fp=metrics.get("false_positives", 0),
            fn=metrics.get("false_negatives", 0),
        )
        for label, metrics in sorted(evaluation.get("per_label_metrics", {}).items())
    )
    return "\n".join(
        [
            "## 5. Evaluation Summary",
            "",
            f"- Overall precision: {_format_metric(summary.get('overall_precision'))}",
            f"- Overall recall: {_format_metric(summary.get('overall_recall'))}",
            f"- Overall F1: {_format_metric(summary.get('overall_f1'))}",
            f"- Macro F1: {_format_metric(summary.get('macro_f1'))}",
            "",
            "| Label | Precision | Recall | F1 | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            rows,
        ]
    )


def _reliability_summary(reliability: dict[str, Any]) -> str:
    summary = reliability.get("summary", {})
    return "\n".join(
        [
            "## 6. Reliability Summary",
            "",
            f"- `auto_accept` count: {summary.get('auto_accept', 0)}",
            f"- `needs_review` count: {summary.get('needs_review', 0)}",
            f"- `blocked` count: {summary.get('blocked', 0)}",
            f"- Average confidence: {_format_metric(summary.get('average_confidence'))}",
            "- Routing policy note: reliability routes support local human review only; they do not approve payments, accounting entries, tax positions, legal conclusions, or autonomous actions.",
        ]
    )


def _evidence_examples(cases: list[dict[str, Any]], reliability_cases: dict[str, dict[str, Any]]) -> str:
    ordered_labels = [
        ["clean_match"],
        ["quantity_mismatch"],
        ["supplier_alias_mismatch"],
        ["schema_validation_failure"],
    ]
    examples: list[dict[str, Any]] = []
    for labels in ordered_labels:
        case = _first_case(cases, labels)
        if case:
            examples.append(case)

    parts = ["## 7. Evidence Examples"]
    for case in examples[:4]:
        reliability = reliability_cases.get(case["bundle_id"], {})
        evidence = case.get("evidence", [])
        parts.extend(
            [
                "",
                f"### {case['bundle_id']}",
                "",
                f"- Detected label: {', '.join(f'`{label}`' for label in case.get('discrepancy_labels', []))}",
                f"- Route: `{reliability.get('reliability_route', case.get('route'))}`",
                f"- Confidence score: {_format_metric(reliability.get('confidence_score')) if reliability else 'Not available'}",
                f"- Explanation: {case.get('explanation', 'Not available')}",
                f"- Evidence summary: {_summarize_evidence(evidence)}",
            ]
        )
    return "\n".join(parts)


def _limitations() -> str:
    return "\n".join(
        [
            "## 8. Limitations",
            "",
            "- Synthetic data only.",
            "- Deterministic baseline only.",
            "- No OCR.",
            "- No real documents.",
            "- No live APIs.",
            "- No model calls.",
            "- No autonomous actions.",
            "- Not accounting, tax, legal, financial, payment, compliance, or business-action advice.",
        ]
    )


def _reproduction_commands() -> str:
    return "\n".join(
        [
            "## 9. Reproduction Commands",
            "",
            "```bash",
            "python3 scripts/generate_synthetic_data.py",
            "python3 scripts/validate_fixtures.py",
            "python3 scripts/run_reconciliation.py",
            "python3 scripts/evaluate_reconciliation.py",
            "python3 scripts/score_reliability.py",
            "python3 scripts/generate_report.py",
            "python3 -m pytest",
            "```",
        ]
    )


def _first_case(cases: list[dict[str, Any]], labels: list[str]) -> dict[str, Any] | None:
    return next((case for case in cases if case.get("discrepancy_labels") == labels), None)


def _case_label(case: dict[str, Any]) -> str:
    labels = ", ".join(f"`{label}`" for label in case.get("discrepancy_labels", []))
    return f"`{case['bundle_id']}` ({labels})"


def _summarize_evidence(evidence: list[dict[str, Any]]) -> str:
    if not evidence:
        return "No discrepancy evidence items; clean case is supported by deterministic line matches."
    first = evidence[0]
    label = first.get("label", "unknown_label")
    basis = first.get("detection_basis", "unknown_basis")
    explanation = first.get("explanation", "No explanation available.")
    return f"{label} via `{basis}`. {explanation}"


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, int):
        return f"{value:.3f}"
    return "Not available"
