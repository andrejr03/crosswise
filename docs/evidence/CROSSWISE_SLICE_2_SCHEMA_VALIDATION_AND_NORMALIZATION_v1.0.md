# Crosswise Slice 2 Schema Validation and Normalization Evidence (v1.0)

## Implemented Components

Slice 2 adds a validation and normalization layer over the deterministic Slice 1 fixture output.

Implemented components:

- `src/crosswise/validation/`
  - validation report structures;
  - fixture payload validation;
  - fixture file validation.
- `src/crosswise/normalization/`
  - deterministic text normalization helpers;
  - supplier name and alias normalization;
  - SKU text normalization;
  - date normalization;
  - currency code normalization.
- `scripts/validate_fixtures.py`
  - loads generated JSON fixtures;
  - runs validation checks;
  - prints a summary;
  - exits non-zero on validation failure.
- `tests/test_validation.py`
  - covers valid fixtures and intentionally broken fixture cases.

## Validation Categories

The Slice 2 validator checks:

- top-level fixture structure;
- required fields;
- basic field types;
- ID presence;
- ID uniqueness;
- reference integrity;
- quantity rules;
- monetary rules;
- line-total arithmetic;
- parent subtotal and total arithmetic;
- date parsing and date ordering;
- currency format;
- discrepancy label taxonomy;
- expected route values;
- synthetic-only policy constraints.

The validation report includes:

- passed checks;
- failed checks;
- warnings;
- affected collection, record ID, and field when available.

## Normalization Categories

The normalization layer supports deterministic normalization for:

- general whitespace and casing;
- supplier names;
- supplier aliases;
- SKU text;
- ISO dates;
- currency codes.

No fuzzy matching, reconciliation, confidence scoring, or evaluation metrics are implemented in Slice 2.

## Commands Executed

```bash
python3 scripts/generate_synthetic_data.py
python3 scripts/validate_fixtures.py
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

Test suite:

```text
23 passed
```

## Limitations

- Slice 2 validates generated fixture records only.
- It does not implement reconciliation, line-item matching, confidence scoring, evaluation metrics, OCR, APIs, UI, or deployment.
- Normalization is deterministic and exact-rule based; fuzzy matching is intentionally deferred.
- Validation focuses on schema contract enforcement and reference integrity, not business decision correctness.

## Next Slice Recommendation

Slice 3 should implement the reconciliation baseline and line-item matching over already validated fixtures. It should consume normalized supplier and SKU values but avoid confidence scoring and evaluation harness expansion until later slices.
