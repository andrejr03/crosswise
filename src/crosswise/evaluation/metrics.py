"""Discrepancy metric calculations for Slice 4.

This module evaluates reconciliation labels against generated ground truth. It
does not implement confidence scoring, calibration, model evaluation, or UI
reporting.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from crosswise.schemas.models import DISCREPANCY_LABELS


def evaluate_reconciliation_files(reconciliation_path: Path, ground_truth_path: Path) -> dict[str, Any]:
    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
    return evaluate_reconciliation(reconciliation, ground_truth)


def evaluate_reconciliation(reconciliation: dict[str, Any], ground_truth: dict[str, Any]) -> dict[str, Any]:
    cases_by_bundle = {case["bundle_id"]: case for case in reconciliation.get("cases", [])}
    truth_by_bundle = ground_truth.get("bundles", {})

    label_stats = {
        label: {"true_positives": 0, "false_positives": 0, "false_negatives": 0}
        for label in DISCREPANCY_LABELS
    }
    false_positives: list[dict[str, str | None]] = []
    false_negatives: list[dict[str, str | None]] = []
    confusion_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for bundle_id in sorted(set(truth_by_bundle) | set(cases_by_bundle)):
        expected_labels = set(truth_by_bundle.get(bundle_id, {}).get("expected_labels", []))
        detected_labels = set(cases_by_bundle.get(bundle_id, {}).get("discrepancy_labels", []))

        for expected_label in sorted(expected_labels):
            if detected_labels:
                for detected_label in sorted(detected_labels):
                    confusion_counts[expected_label][detected_label] += 1
            else:
                confusion_counts[expected_label]["<missing_case>"] += 1

        for label in sorted(expected_labels & detected_labels):
            label_stats.setdefault(label, {"true_positives": 0, "false_positives": 0, "false_negatives": 0})
            label_stats[label]["true_positives"] += 1
        for label in sorted(detected_labels - expected_labels):
            label_stats.setdefault(label, {"true_positives": 0, "false_positives": 0, "false_negatives": 0})
            label_stats[label]["false_positives"] += 1
            false_positives.append(
                {
                    "bundle_id": bundle_id,
                    "expected_label": _join_labels(expected_labels),
                    "detected_label": label,
                    "explanation": f"Detected {label} but ground truth expected {_join_labels(expected_labels)}.",
                }
            )
        for label in sorted(expected_labels - detected_labels):
            label_stats.setdefault(label, {"true_positives": 0, "false_positives": 0, "false_negatives": 0})
            label_stats[label]["false_negatives"] += 1
            false_negatives.append(
                {
                    "bundle_id": bundle_id,
                    "expected_label": label,
                    "detected_label": _join_labels(detected_labels),
                    "explanation": f"Expected {label} but reconciliation detected {_join_labels(detected_labels)}.",
                }
            )

    per_label_metrics = {
        label: _metrics_for_counts(
            stats["true_positives"],
            stats["false_positives"],
            stats["false_negatives"],
        )
        for label, stats in label_stats.items()
    }
    macro_f1 = _mean([metrics["f1"] for metrics in per_label_metrics.values()])
    totals = {
        "true_positives": sum(stats["true_positives"] for stats in label_stats.values()),
        "false_positives": sum(stats["false_positives"] for stats in label_stats.values()),
        "false_negatives": sum(stats["false_negatives"] for stats in label_stats.values()),
    }
    overall = _metrics_for_counts(
        totals["true_positives"],
        totals["false_positives"],
        totals["false_negatives"],
    )

    return {
        "metadata": {
            "evaluation_version": "slice_4_evaluation_v1",
            "fixture_version": ground_truth.get("metadata", {}).get("fixture_version"),
            "reconciliation_version": reconciliation.get("metadata", {}).get("reconciliation_version"),
            "confidence_calibration": "not_implemented",
        },
        "summary": {
            "bundles_evaluated": len(truth_by_bundle),
            "cases_evaluated": len(cases_by_bundle),
            "overall_precision": overall["precision"],
            "overall_recall": overall["recall"],
            "overall_f1": overall["f1"],
            "macro_f1": macro_f1,
            **totals,
        },
        "per_label_metrics": per_label_metrics,
        "confusion": {expected: dict(detected) for expected, detected in sorted(confusion_counts.items())},
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def write_evaluation_output(result: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _metrics_for_counts(true_positives: int, false_positives: int, false_negatives: int) -> dict[str, float | int]:
    precision = _safe_divide(true_positives, true_positives + false_positives)
    recall = _safe_divide(true_positives, true_positives + false_negatives)
    f1 = _safe_divide(2 * precision * recall, precision + recall)
    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _safe_divide(numerator: float | int, denominator: float | int) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator), 6)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _join_labels(labels: set[str]) -> str | None:
    if not labels:
        return None
    return ",".join(sorted(labels))
