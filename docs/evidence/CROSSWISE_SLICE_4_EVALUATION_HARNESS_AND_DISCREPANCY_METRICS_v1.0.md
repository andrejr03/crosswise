# Crosswise Slice 4 Evaluation Harness and Discrepancy Metrics Evidence (v1.0)

## Implemented Components

Slice 4 implements a deterministic evaluation harness for comparing reconciliation output against generated ground truth.

Implemented components:

- `src/crosswise/evaluation/`
  - evaluation entry points;
  - reconciliation-vs-ground-truth label comparison;
  - per-label discrepancy metrics;
  - overall metrics;
  - macro F1;
  - confusion accounting;
  - false-positive and false-negative reporting;
  - JSON output writer.
- `scripts/evaluate_reconciliation.py`
  - loads `data/reconciliation/reconciliation_v1_0.json`;
  - loads `data/ground_truth/ground_truth_v1_0.json`;
  - runs evaluation;
  - writes `data/evaluation/evaluation_v1_0.json`;
  - prints a concise metric summary.
- `tests/test_evaluation.py`
  - covers script execution, output creation, metric ranges, perfect baseline metrics, false-positive accounting, false-negative accounting, per-label metrics, macro F1, confusion information, and deterministic output.

## Metrics Implemented

Slice 4 implements:

- discrepancy precision by type;
- discrepancy recall by type;
- discrepancy F1 by type;
- macro F1;
- overall precision;
- overall recall;
- overall F1.

Metric definitions use per-bundle label comparison:

- true positive: expected label is detected for the same bundle;
- false positive: detected label is not expected for the same bundle;
- false negative: expected label is missing for the same bundle.

Confidence calibration, expected calibration error, reliability diagrams, and confidence scoring are intentionally not implemented in this slice.

## Evaluation Outputs

The evaluation script writes:

- `data/evaluation/evaluation_v1_0.json`

The output includes:

- evaluation metadata;
- metric summary;
- per-label metrics;
- confusion information;
- false positives;
- false negatives.

False-positive and false-negative records include:

- bundle ID;
- expected label;
- detected label;
- short explanation.

## Commands Executed

```bash
python3 scripts/generate_synthetic_data.py
python3 scripts/validate_fixtures.py
python3 scripts/run_reconciliation.py
python3 scripts/evaluate_reconciliation.py
python3 -m pytest
```

## Test Results

Fixture generation:

```text
Wrote synthetic fixtures: /Users/agentisstudio/Documents/crosswise/data/synthetic/fixtures_v1_0.json
Wrote ground truth: /Users/agentisstudio/Documents/crosswise/data/ground_truth/ground_truth_v1_0.json
```

Fixture validation:

```text
Passed checks: 12
Warnings: 0
Failures: 0
Validation passed.
```

Reconciliation:

```text
Bundles reconciled: 10
Detected cases: 10
Detected label counts: {'clean_match': 1, 'duplicate_invoice': 1, 'late_receipt': 1, 'low_confidence_extraction': 1, 'missing_invoice_line': 1, 'missing_receipt_line': 1, 'quantity_mismatch': 1, 'schema_validation_failure': 1, 'supplier_alias_mismatch': 1, 'unit_price_mismatch': 1}
```

Evaluation:

```text
Bundles evaluated: 10
Overall precision: 1.0
Overall recall: 1.0
Overall F1: 1.0
Macro F1: 1.0
```

Test suite:

```text
41 passed
```

## Limitations

- Slice 4 evaluates discrepancy labels only.
- It does not implement confidence scoring, calibration, expected calibration error, reliability diagrams, UI, OCR, APIs, model calls, deployment, or fuzzy matching expansion.
- The current deterministic synthetic baseline is expected to score perfectly because generated fixtures and reconciliation logic are controlled.
- False-positive and false-negative examples are supported structurally and tested through intentionally altered reconciliation outputs.

## Next Slice Recommendation

Slice 5 should implement the confidence routing and reliability layer. It should consume validation, reconciliation, and evaluation outputs, but confidence scoring should remain evidence-based and must not rely only on model self-reported scores.
