"""Conservative routing rules for Slice 5.

Routes indicate review workflow handling only. They do not approve payments,
accounting treatment, tax treatment, legal conclusions, or autonomous action.
"""

from __future__ import annotations

from typing import Any

AUTO_ACCEPT = "auto_accept"
NEEDS_REVIEW = "needs_review"
BLOCKED = "blocked"

NON_ADVICE_REMINDER = (
    "Crosswise output is synthetic-only reconciliation support and is not accounting, "
    "tax, legal, financial, payment, compliance, or autonomous approval advice."
)

REVIEW_REASONS = {
    "duplicate_invoice": "Possible duplicate invoice requires human review before any downstream workflow.",
    "missing_receipt_line": "Receipt evidence is incomplete for at least one purchase order line.",
    "quantity_mismatch": "Ordered, billed, or received quantities differ.",
    "unit_price_mismatch": "Invoice unit price differs from purchase order unit price.",
    "missing_invoice_line": "Invoice evidence is incomplete for at least one purchase order line.",
    "supplier_alias_mismatch": "Supplier alias requires review even when deterministic alias evidence exists.",
    "late_receipt": "Receipt timing differs from the purchase order expectation.",
    "low_confidence_extraction": "Fixture encodes a simulated extraction reliability issue.",
}


def route_case(case: dict[str, Any]) -> dict[str, str | None]:
    labels = set(case.get("discrepancy_labels", []))

    if "schema_validation_failure" in labels:
        return {
            "reliability_route": BLOCKED,
            "review_reason": "Schema validation failure prevents reliable automated handling.",
            "blocked_reason": "schema_validation_failure",
            "non_advice_reminder": NON_ADVICE_REMINDER,
        }

    if labels == {"clean_match"} and _has_strong_clean_evidence(case):
        return {
            "reliability_route": AUTO_ACCEPT,
            "review_reason": "Deterministic clean match with complete line-level match evidence.",
            "blocked_reason": None,
            "non_advice_reminder": NON_ADVICE_REMINDER,
        }

    reason = _review_reason_for(labels)
    return {
        "reliability_route": NEEDS_REVIEW,
        "review_reason": reason,
        "blocked_reason": None,
        "non_advice_reminder": NON_ADVICE_REMINDER,
    }


def _has_strong_clean_evidence(case: dict[str, Any]) -> bool:
    line_matches = case.get("line_matches", [])
    if not line_matches:
        return False
    for match in line_matches:
        if match.get("labels") != ["clean_match"]:
            return False
        if match.get("invoice_match_basis") not in {"sku_id_exact", "sku_raw_normalized_exact"}:
            return False
        if match.get("receipt_match_basis") not in {"sku_id_exact", "sku_raw_normalized_exact"}:
            return False
        if not match.get("invoice_line_id") or not match.get("receipt_line_id"):
            return False
    return True


def _review_reason_for(labels: set[str]) -> str:
    for label, reason in REVIEW_REASONS.items():
        if label in labels:
            return reason
    return "Case requires review because it is not a deterministic clean match."
