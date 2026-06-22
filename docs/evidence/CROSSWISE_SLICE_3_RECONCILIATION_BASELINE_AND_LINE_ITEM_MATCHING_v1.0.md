# Crosswise Slice 3 Reconciliation Baseline and Line-Item Matching Evidence (v1.0)

## Implemented Components

Slice 3 implements the first deterministic reconciliation baseline over validated synthetic fixtures.

Implemented components:

- `src/crosswise/matching/`
  - supplier matching helpers;
  - SKU lookup helpers;
  - invoice line matching;
  - receipt line matching.
- `src/crosswise/reconciliation/`
  - fixture-file reconciliation entry point;
  - fixture-payload reconciliation entry point;
  - per-bundle reconciliation case output;
  - deterministic label detection;
  - JSON output writer.
- `scripts/run_reconciliation.py`
  - loads generated fixtures;
  - loads ground truth for simulated extraction issue metadata;
  - validates fixtures before reconciliation;
  - writes `data/reconciliation/reconciliation_v1_0.json`;
  - prints bundle count, case count, label counts, and output path.
- `tests/test_reconciliation.py`
  - covers script execution, output creation, case coverage, label detection, evidence, routing, and deterministic output.

## Matching Strategy

Supplier matching:

- uses `supplier_id` exact match first;
- supports normalized known supplier aliases;
- flags `supplier_alias_mismatch` when invoice supplier text is a known alias of the canonical supplier.

SKU and line matching:

- matches PO line to invoice line primarily by `sku_id`;
- matches PO line to receipt line primarily by `sku_id`;
- falls back to normalized SKU text only when `sku_id` is absent and the normalized match is unambiguous;
- does not implement fuzzy matching.

Document matching:

- uses the existing `DocumentBundle` references for purchase order, invoice, and receipt IDs;
- validates fixture references before reconciliation through the Slice 2 validation layer.

## Discrepancy Detection Coverage

Slice 3 detects or safely carries through:

- `clean_match`
- `quantity_mismatch`
- `unit_price_mismatch`
- `missing_invoice_line`
- `missing_receipt_line`
- `duplicate_invoice`
- `supplier_alias_mismatch`
- `late_receipt`
- `schema_validation_failure`
- `low_confidence_extraction`

`low_confidence_extraction` is not computed from real confidence logic. It is carried through only when the generated ground truth explicitly encodes a simulated extraction issue.

`schema_validation_failure` is carried through from generated ground truth simulated extraction issue metadata because Slice 1 source records remain schema-valid by design.

## Evidence Structure

Each non-clean detected discrepancy includes JSON-serializable evidence with:

- affected document IDs;
- affected line IDs where applicable;
- compared field names;
- observed values;
- normalized values where available;
- detection basis;
- short human-readable explanation.

The reconciliation case output also includes:

- deterministic route;
- deterministic severity;
- line matches;
- `confidence_score: null`;
- a note that Slice 3 does not implement confidence scoring.

## Commands Executed

```bash
python3 scripts/generate_synthetic_data.py
python3 scripts/validate_fixtures.py
python3 scripts/run_reconciliation.py
python3 -m pytest
```

## Validation and Test Results

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

Test suite:

```text
32 passed
```

## Limitations

- Slice 3 does not implement confidence scoring, calibration, evaluation metrics, UI, OCR, APIs, model calls, or deployment.
- Matching is deterministic and exact-rule based.
- No fuzzy matching is implemented beyond exact normalized alias/SKU-text support.
- Routing uses deterministic defaults only.
- Reconciliation output is a baseline data artifact, not an autonomous business decision.

## Next Slice Recommendation

Slice 4 should implement the evaluation harness and discrepancy metrics against generated ground truth, including per-label precision/recall-style checks and false-positive/false-negative examples. Confidence scoring should remain separate until the evaluation baseline is stable.
