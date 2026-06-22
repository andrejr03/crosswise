"""Deterministic reliability scoring for Slice 5.

Scores are evidence-based and never use model self-reported confidence.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from crosswise.routing import route_case

RELIABILITY_VERSION = "slice_5_reliability_v1"

LABEL_PENALTIES = {
    "schema_validation_failure": 0.7,
    "low_confidence_extraction": 0.35,
    "duplicate_invoice": 0.3,
    "missing_receipt_line": 0.3,
    "missing_invoice_line": 0.25,
    "quantity_mismatch": 0.25,
    "unit_price_mismatch": 0.25,
    "supplier_alias_mismatch": 0.12,
    "late_receipt": 0.12,
}


def score_case(case: dict[str, Any], evaluation: dict[str, Any] | None = None) -> dict[str, Any]:
    labels = list(case.get("discrepancy_labels", []))
    evidence_profile = _evidence_profile(case)
    match_quality = _match_quality(case)
    evaluation_support = _evaluation_support(labels, evaluation)

    score = 0.95
    factors: list[dict[str, Any]] = [
        {
            "name": "model_self_reported_confidence",
            "value": "not_used",
            "impact": 0.0,
            "explanation": "Slice 5 does not use model calls or model-reported confidence.",
        },
        {
            "name": "evidence_completeness",
            "value": evidence_profile,
            "impact": _evidence_impact(evidence_profile),
            "explanation": "Clean cases require complete deterministic line matches; non-clean labels require structured evidence.",
        },
        {
            "name": "deterministic_match_quality",
            "value": match_quality,
            "impact": -round((1.0 - match_quality["score"]) * 0.2, 6),
            "explanation": "Exact SKU line matches support reliability; missing or weaker match bases reduce it.",
        },
        {
            "name": "evaluation_support",
            "value": evaluation_support,
            "impact": -round((1.0 - evaluation_support["average_label_f1"]) * 0.15, 6),
            "explanation": "Existing Slice 4 per-label F1 is used only as deterministic support when available.",
        },
    ]

    score += factors[1]["impact"]
    score += factors[2]["impact"]
    score += factors[3]["impact"]

    if labels == ["clean_match"]:
        factors.append(
            {
                "name": "clean_case",
                "value": True,
                "impact": 0.03,
                "explanation": "No non-clean discrepancy labels were detected.",
            }
        )
        score += 0.03
    else:
        penalty = max((LABEL_PENALTIES.get(label, 0.2) for label in labels), default=0.2)
        factors.append(
            {
                "name": "discrepancy_severity",
                "value": {"labels": labels, "max_penalty": penalty},
                "impact": -penalty,
                "explanation": "Reviewable or blocked discrepancy labels reduce reliability confidence.",
            }
        )
        score -= penalty

    if "low_confidence_extraction" in labels:
        factors.append(
            {
                "name": "simulated_extraction_issue",
                "value": "low_confidence_extraction",
                "impact": -0.05,
                "explanation": "The fixture explicitly encodes an extraction issue; no model confidence is inferred.",
            }
        )
        score -= 0.05

    bounded_score = round(min(1.0, max(0.0, score)), 6)
    routing = route_case(case)

    return {
        "case_id": case["case_id"],
        "bundle_id": case["bundle_id"],
        "discrepancy_labels": labels,
        "original_route": case.get("route"),
        "reliability_route": routing["reliability_route"],
        "confidence_score": bounded_score,
        "confidence_factors": factors,
        "evidence_completeness": evidence_profile,
        "review_reason": routing["review_reason"],
        "blocked_reason": routing["blocked_reason"],
        "non_advice_reminder": routing["non_advice_reminder"],
    }


def score_reconciliation(reconciliation: dict[str, Any], evaluation: dict[str, Any] | None = None) -> dict[str, Any]:
    cases = [score_case(case, evaluation) for case in reconciliation.get("cases", [])]
    route_counts = Counter(case["reliability_route"] for case in cases)
    average_confidence = _average([case["confidence_score"] for case in cases])
    return {
        "metadata": {
            "reliability_version": RELIABILITY_VERSION,
            "reconciliation_version": reconciliation.get("metadata", {}).get("reconciliation_version"),
            "evaluation_version": (evaluation or {}).get("metadata", {}).get("evaluation_version"),
            "confidence_basis": "deterministic_evidence_validation_reconciliation_and_optional_evaluation_support",
            "model_self_reported_confidence": "not_used",
        },
        "summary": {
            "cases_scored": len(cases),
            "auto_accept": route_counts.get("auto_accept", 0),
            "needs_review": route_counts.get("needs_review", 0),
            "blocked": route_counts.get("blocked", 0),
            "average_confidence": average_confidence,
        },
        "cases": cases,
    }


def write_reliability_output(result: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _evidence_profile(case: dict[str, Any]) -> dict[str, Any]:
    labels = [label for label in case.get("discrepancy_labels", []) if label != "clean_match"]
    if not labels:
        strong_clean = _strong_clean_line_matches(case)
        return {
            "complete": strong_clean,
            "ratio": 1.0 if strong_clean else 0.0,
            "missing_labels": [] if strong_clean else ["clean_match_line_evidence"],
        }

    evidence = case.get("evidence", [])
    evidence_labels = {item.get("label") for item in evidence}
    missing = sorted(label for label in labels if label not in evidence_labels)
    complete_count = len(labels) - len(missing)
    ratio = round(complete_count / len(labels), 6) if labels else 1.0
    return {"complete": not missing, "ratio": ratio, "missing_labels": missing}


def _evidence_impact(profile: dict[str, Any]) -> float:
    ratio = profile["ratio"]
    if ratio >= 1.0:
        return 0.0
    return -round((1.0 - ratio) * 0.25, 6)


def _strong_clean_line_matches(case: dict[str, Any]) -> bool:
    line_matches = case.get("line_matches", [])
    return bool(line_matches) and all(
        match.get("labels") == ["clean_match"]
        and match.get("invoice_line_id")
        and match.get("receipt_line_id")
        and match.get("invoice_match_basis") in {"sku_id_exact", "sku_raw_normalized_exact"}
        and match.get("receipt_match_basis") in {"sku_id_exact", "sku_raw_normalized_exact"}
        for match in line_matches
    )


def _match_quality(case: dict[str, Any]) -> dict[str, Any]:
    line_matches = case.get("line_matches", [])
    if not line_matches:
        return {"score": 0.0, "exact_matches": 0, "total_match_slots": 0}

    total_slots = 0
    exact_slots = 0
    for match in line_matches:
        for field in ("invoice_match_basis", "receipt_match_basis"):
            total_slots += 1
            if match.get(field) in {"sku_id_exact", "sku_raw_normalized_exact"}:
                exact_slots += 1
    score = round(exact_slots / total_slots, 6) if total_slots else 0.0
    return {"score": score, "exact_matches": exact_slots, "total_match_slots": total_slots}


def _evaluation_support(labels: list[str], evaluation: dict[str, Any] | None) -> dict[str, Any]:
    if not evaluation:
        return {"available": False, "average_label_f1": 1.0}
    per_label = evaluation.get("per_label_metrics", {})
    values = [float(per_label.get(label, {}).get("f1", 0.0)) for label in labels]
    return {
        "available": True,
        "average_label_f1": _average(values) if values else 1.0,
    }


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)
