# Crosswise Local Evidence Report

## 1. Project Summary

Crosswise is a local AI document reconciliation project for structured invoice, purchase order, and receipt records. It detects synthetic discrepancy labels, preserves evidence for reviewer decisions, and routes uncertain or risky cases into a human-review workflow.

Crosswise is synthetic-data-only: this report uses generated fixtures and contains no real invoices, real company data, PII, payment information, bank details, or tax identifiers.

Crosswise output is not accounting, tax, legal, financial, payment, compliance, or business-action advice.

## 2. Pipeline Summary

- Synthetic data generation creates deterministic invoice, purchase order, receipt, fixture, and ground-truth JSON records.
- Schema validation and normalization checks fixture structure, references, arithmetic, dates, currency, taxonomy, and synthetic-only constraints.
- Reconciliation baseline performs deterministic supplier, SKU, document, and line-item matching and emits evidence-backed discrepancy cases.
- Evaluation harness compares detected labels with generated ground truth and reports precision, recall, F1, macro F1, and per-label metrics.
- Reliability routing assigns deterministic confidence scores and conservative routes: `auto_accept`, `needs_review`, or `blocked`.

## 3. Fixture Summary

- Number of bundles: 10
- Generated fixture paths:
  - `data/synthetic/fixtures_v1_0.json`
  - `data/ground_truth/ground_truth_v1_0.json`

| Discrepancy label | Bundle count |
| --- | ---: |
| `clean_match` | 1 |
| `duplicate_invoice` | 1 |
| `late_receipt` | 1 |
| `low_confidence_extraction` | 1 |
| `missing_invoice_line` | 1 |
| `missing_receipt_line` | 1 |
| `quantity_mismatch` | 1 |
| `schema_validation_failure` | 1 |
| `supplier_alias_mismatch` | 1 |
| `unit_price_mismatch` | 1 |

## 4. Reconciliation Summary

- Number of cases: 10
- Detected labels: `clean_match`, `duplicate_invoice`, `late_receipt`, `low_confidence_extraction`, `missing_invoice_line`, `missing_receipt_line`, `quantity_mismatch`, `schema_validation_failure`, `supplier_alias_mismatch`, `unit_price_mismatch`
- Example clean match: `bundle_clean_match_001` (`clean_match`)
- Example needs-review case: `bundle_duplicate_invoice_006` (`duplicate_invoice`)
- Example blocked case: `bundle_schema_validation_failure_010` (`schema_validation_failure`)

## 5. Evaluation Summary

- Overall precision: 1.000
- Overall recall: 1.000
- Overall F1: 1.000
- Macro F1: 1.000

| Label | Precision | Recall | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `clean_match` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `duplicate_invoice` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `late_receipt` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `low_confidence_extraction` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `missing_invoice_line` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `missing_receipt_line` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `quantity_mismatch` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `schema_validation_failure` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `supplier_alias_mismatch` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| `unit_price_mismatch` | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## 6. Reliability Summary

- `auto_accept` count: 1
- `needs_review` count: 8
- `blocked` count: 1
- Average confidence: 0.674
- Routing policy note: reliability routes support local human review only; they do not approve payments, accounting entries, tax positions, legal conclusions, or autonomous actions.

## 7. Evidence Examples

### bundle_clean_match_001

- Detected label: `clean_match`
- Route: `auto_accept`
- Confidence score: 0.980
- Explanation: All deterministic baseline checks passed for the bundle.
- Evidence summary: No discrepancy evidence items; clean case is supported by deterministic line matches.

### bundle_quantity_mismatch_002

- Detected label: `quantity_mismatch`
- Route: `needs_review`
- Confidence score: 0.700
- Explanation: Deterministic baseline reconciliation detected one or more reviewable discrepancies.
- Evidence summary: quantity_mismatch via `ordered_billed_received_quantity_difference`. Ordered, billed, and received quantities are not identical.

### bundle_supplier_alias_mismatch_007

- Detected label: `supplier_alias_mismatch`
- Route: `needs_review`
- Confidence score: 0.830
- Explanation: Deterministic baseline reconciliation detected one or more reviewable discrepancies.
- Evidence summary: supplier_alias_mismatch via `supplier_id_exact_with_known_alias`. Invoice supplier name is a known normalized alias of the canonical supplier.

### bundle_schema_validation_failure_010

- Detected label: `schema_validation_failure`
- Route: `blocked`
- Confidence score: 0.250
- Explanation: Deterministic baseline reconciliation detected one or more reviewable discrepancies.
- Evidence summary: schema_validation_failure via `simulated_extraction_issue_from_ground_truth`. Slice 3 carries through a fixture-encoded simulated extraction issue without confidence scoring.

## 8. Limitations

- Synthetic data only.
- Deterministic baseline only.
- No OCR.
- No real documents.
- No live APIs.
- No model calls.
- No autonomous actions.
- Not accounting, tax, legal, financial, payment, compliance, or business-action advice.

## 9. Reproduction Commands

```bash
python3 scripts/generate_synthetic_data.py
python3 scripts/validate_fixtures.py
python3 scripts/run_reconciliation.py
python3 scripts/evaluate_reconciliation.py
python3 scripts/score_reliability.py
python3 scripts/generate_report.py
python3 -m pytest
```
