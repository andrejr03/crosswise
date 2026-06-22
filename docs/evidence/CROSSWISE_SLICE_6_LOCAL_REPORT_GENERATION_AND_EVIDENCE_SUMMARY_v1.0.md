# Crosswise Slice 6 Local Report Generation and Evidence Summary v1.0

## Status

Completed.

Slice 6 adds local Markdown report generation over existing Slice 1-5 generated outputs. It does not introduce Streamlit, a web app, OCR, APIs, model calls, deployment, confidence recalibration, autonomous actions, or changes to reconciliation, evaluation, or reliability logic.

## Implemented Components

- `src/crosswise/reporting/`
  - Loads required generated outputs from `data/synthetic/`, `data/ground_truth/`, `data/reconciliation/`, `data/evaluation/`, and `data/reliability/`.
  - Fails clearly when upstream generated outputs are missing.
  - Renders a deterministic human-readable Markdown evidence report.

- `scripts/generate_report.py`
  - Generates `docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md`.
  - Prints the generated output path.

- `tests/test_reporting.py`
  - Covers script execution, report file creation, required report statements, evaluation metrics, reliability counts, reproduction commands, and deterministic repeated rendering.

- `README.md`
  - Adds Slice 6 status.
  - Adds the local report generation command.
  - Adds a link to the generated local evidence report.

## Report Contents

Generated report:

`docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md`

The report includes:

- project summary;
- synthetic-only statement;
- non-advice statement;
- pipeline summary;
- fixture summary and label coverage;
- reconciliation summary and example cases;
- evaluation metrics and per-label metric table;
- reliability routing counts and average confidence;
- evidence examples;
- limitations;
- reproduction commands.

## Commands Executed

```bash
python3 scripts/generate_report.py
python3 -m pytest tests/test_reporting.py
python3 scripts/generate_synthetic_data.py
python3 scripts/validate_fixtures.py
python3 scripts/run_reconciliation.py
python3 scripts/evaluate_reconciliation.py
python3 scripts/score_reliability.py
python3 scripts/generate_report.py
python3 -m pytest
git status --short
```

## Test Results

Targeted reporting tests:

```text
6 passed
```

Full validation:

```text
Fixture validation passed with 12 passed checks, 0 warnings, and 0 failures.
Reconciliation completed for 10 bundles and 10 detected cases.
Evaluation reported overall precision 1.0, overall recall 1.0, overall F1 1.0, and macro F1 1.0.
Reliability scoring completed for 10 cases: 1 auto_accept, 8 needs_review, 1 blocked, average confidence 0.674.
Full pytest result: 57 passed.
```

## Limitations

- Synthetic data only.
- Deterministic local report generation only.
- No OCR.
- No real documents.
- No live APIs.
- No model calls.
- No Streamlit UI, web app, or interactive dashboard.
- No confidence recalibration.
- No changes to reconciliation, evaluation, or reliability logic.
- No autonomous actions.
- Not accounting, tax, legal, financial, payment, compliance, or business-action advice.

## Next Slice Recommendation

Slice 7 should implement a local review dashboard or static reviewer interface over the existing generated outputs and evidence report, while preserving the synthetic-only, no-OCR, no-API, no-model-call, and human-review boundaries.
