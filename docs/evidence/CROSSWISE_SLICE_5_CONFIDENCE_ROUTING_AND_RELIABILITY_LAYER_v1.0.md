# Crosswise Slice 5 Confidence Routing and Reliability Layer v1.0

## Status

Completed.

Slice 5 adds deterministic confidence scoring and conservative review routing over Slice 3 reconciliation cases. It does not introduce OCR, APIs, model calls, Streamlit, deployment, payment automation, accounting automation, calibration charts, ECE, or reliability diagrams.

## Implemented Components

- `src/crosswise/confidence/`
  - Scores reconciliation cases with deterministic, evidence-based factors.
  - Produces bounded confidence scores from `0.0` to `1.0`.
  - Uses optional Slice 4 evaluation output as a deterministic support signal when present.
  - Explicitly records that model self-reported confidence is not used.

- `src/crosswise/routing/`
  - Assigns conservative reliability routes:
    - `auto_accept`
    - `needs_review`
    - `blocked`
  - Keeps routing limited to human-review workflow support.
  - Includes a fixed non-advice reminder on every output case.

- `scripts/score_reliability.py`
  - Loads `data/reconciliation/reconciliation_v1_0.json`.
  - Loads `data/evaluation/evaluation_v1_0.json` when available.
  - Scores every reconciliation case.
  - Writes `data/reliability/reliability_v1_0.json`.

- `tests/test_reliability.py`
  - Covers script execution, output creation, score bounds, routing behavior, determinism, non-advice reminders, and absence of model-confidence dependency.

## Confidence Scoring Factors

Confidence scores are deterministic and evidence-based. They consider:

- evidence completeness;
- deterministic line-match quality;
- discrepancy labels and severity penalties;
- clean versus non-clean case status;
- simulated extraction issue labels;
- optional Slice 4 per-label F1 support when an evaluation output is present.

The scorer does not use model calls, external APIs, model self-reported confidence, calibration charts, ECE, or reliability diagrams.

## Routing Rules

- `clean_match` with complete deterministic line-level match evidence routes to `auto_accept`.
- `schema_validation_failure` routes to `blocked`.
- `low_confidence_extraction` routes to `needs_review`.
- `duplicate_invoice` routes to `needs_review`.
- `missing_receipt_line` routes to `needs_review`.
- `quantity_mismatch` routes to `needs_review`.
- `unit_price_mismatch` routes to `needs_review`.
- `missing_invoice_line` routes to `needs_review`.
- `supplier_alias_mismatch` routes to `needs_review`.
- `late_receipt` routes to `needs_review`.

No route represents payment approval, accounting correctness, tax correctness, legal correctness, financial advice, compliance advice, or autonomous action.

## Reliability Output

Generated output:

`data/reliability/reliability_v1_0.json`

Each case includes:

- `case_id`;
- `bundle_id`;
- `discrepancy_labels`;
- `original_route`;
- `reliability_route`;
- `confidence_score`;
- `confidence_factors`;
- `evidence_completeness`;
- `review_reason`;
- `blocked_reason`;
- `non_advice_reminder`.

Latest generated summary:

- cases scored: `10`;
- auto accept: `1`;
- needs review: `8`;
- blocked: `1`;
- average confidence: `0.674`.

## Commands Executed

```bash
python3 scripts/generate_synthetic_data.py
python3 scripts/validate_fixtures.py
python3 scripts/run_reconciliation.py
python3 scripts/evaluate_reconciliation.py
python3 scripts/score_reliability.py
python3 -m pytest
```

## Test Results

```text
51 passed in 1.41s
```

Pipeline results:

- fixture generation completed;
- fixture validation passed with `12` passed checks, `0` warnings, and `0` failures;
- reconciliation completed for `10` bundles;
- evaluation reported overall precision `1.0`, overall recall `1.0`, overall F1 `1.0`, and macro F1 `1.0`;
- reliability scoring completed for `10` cases.

## Limitations

- Confidence scoring is deterministic and rule-based only.
- Evaluation support is used only from existing Slice 4 output when available.
- No calibrated confidence, ECE, reliability diagrams, model calls, OCR, live APIs, or UI are implemented.
- `auto_accept` means only that the synthetic fixture case is a deterministic clean match for review workflow purposes; it does not authorize any real-world business action.

## Next Slice Recommendation

Slice 6 should add local report generation and a reviewer-readable evidence summary over the generated reconciliation, evaluation, and reliability outputs.
