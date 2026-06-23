# Crosswise Slice 9 Document-Panel Reconciliation View v1.0

## Status

Completed.

Slice 9 upgrades the existing static reviewer with a document-panel reconciliation view. The upgrade renders curated purchase order, invoice, and receipt panels from existing structured records and highlights discrepancy evidence inline. It does not introduce PDFs, OCR, document ingestion, APIs, model calls, Streamlit, React, Next.js, Flask, FastAPI, a web server, deployment, authentication, fuzzy matching expansion, or changes to reconciliation, evaluation, or reliability logic.

## Implemented Components

- `src/crosswise/reviewer/static_html.py`
  - Adds `Document-Panel Reconciliation View`.
  - Renders curated reviewer stories from existing generated JSON outputs.
  - Renders document-style panels for purchase order, invoice, and receipt records.
  - Highlights evidence-backed discrepancy fields.
  - Adds inline explanation blocks answering what happened, why it was flagged, what evidence supports it, and what route was assigned.
  - Adds screenshot generation helper for the document-panel section.

- `scripts/generate_reviewer.py`
  - Regenerates `docs/evidence/crosswise_reviewer_v1_0.html`.
  - Generates `docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`.
  - Prints both output paths.

- `tests/test_reviewer.py`
  - Covers reviewer generation, curated cases, document panels, discrepancy highlights, explanation blocks, screenshot creation, self-contained HTML, no external URLs, and deterministic output.

- `README.md`
  - Adds Slice 9 completion status.
  - Links the reviewer discrepancy showcase screenshot.

- `docs/evidence/INDEX.md`
  - Adds Slice 8, Slice 9, and the reviewer discrepancy showcase screenshot.

## Curated Cases

The document-panel section renders exactly six curated reviewer stories:

- `bundle_clean_match_001` — `clean_match`
- `bundle_quantity_mismatch_002` — `quantity_mismatch`
- `bundle_unit_price_mismatch_003` — `unit_price_mismatch`
- `bundle_supplier_alias_mismatch_007` — `supplier_alias_mismatch`
- `bundle_duplicate_invoice_006` — `duplicate_invoice`
- `bundle_low_confidence_extraction_009` — `low_confidence_extraction`

It intentionally does not render every bundle in the document-panel section. The full detailed case table remains available below the curated stories.

## Panel Design

Each curated case renders side-by-side HTML panels for:

- Purchase Order
- Invoice
- Receipt

The panels are document-like HTML views populated from existing structured fixture records. They show document IDs, suppliers, dates, relevant line items, quantities, unit prices or units, and totals where relevant. No PDFs are generated and no document parsing is introduced.

## Discrepancy Highlighting Approach

Highlights are restrained and use the existing charcoal / warm neutral / amber visual language.

Highlighted evidence includes:

- quantity mismatches across PO, invoice, and receipt line quantities;
- unit price mismatches between PO and invoice unit price fields;
- supplier alias fields in supplier-alias cases;
- duplicate invoice IDs, numbers, dates, and totals;
- low-confidence unit price indicators for the simulated extraction issue.

The highlighted fields are derived from reconciliation evidence and generated fixture records, not hand-authored values.

## Screenshot Generation

Generated screenshot:

`docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`

The screenshot is generated from the upgraded local HTML reviewer using Playwright browser automation and captures the document-panel reconciliation section with discrepancy examples.

## Slice 9B Visual Alignment Note

Before commit, Slice 9 received a rendering-only visual alignment pass against `assets/prototypes/crosswise-showcase.png`. The goal was to make the static reviewer feel more premium, restrained, editorial, spacious, and aligned with the approved Crosswise charcoal / warm-neutral / amber showcase language.

The pass changed presentation only. The reviewer hero (`#document-panel-reconciliation-view`, the section captured in the showcase screenshot) was rebuilt to mirror the approved showcase almost exactly:

- a brand row (diamond mark, `Crosswise`, `AI Document Reconciliation`) with a `Dev build / synthetic test cases` marker;
- an `Invoice ⇄ Matching ⇄ PO` document-context line;
- a single calm Invoice-vs-PO field-comparison table (Field / Invoice / PO / Δ / Status) with matched rows muted (`✓ match`, `—`) and the genuinely disagreeing rows carried in amber with a signed delta and `⚑ review`;
- a two-up decision row: a large model-confidence number with a thin amber progress bar, and an amber `Route to human review` action with the discrepancy count, evidence note, and assigned route;
- a three-feature row (line-item matching, field-level evidence, human review routing) and an editorial footer.

To match the showcase's restraint, the dense per-document mini-panels and the inline evidence line were **removed from the hero** rather than adding new elements; the hero bundle is now told entirely through the comparison table. The hero case is selected deterministically and now prefers the cleanest field-level story (`unit_price_mismatch`, then `quantity_mismatch`) so the lead communicates "Crosswise detected a discrepancy and explains why" within seconds. All other bundles keep their full document panels, evidence, routes, confidence, and explanation blocks in the condensed review queue below the hero. Every value — vendor, quantities, unit prices, line totals, tax, deltas, confidence, route — is read straight from the existing generated fixtures and reconciliation/reliability outputs; nothing is recomputed or hand-authored. No reconciliation, evaluation, reliability, routing, metrics, generated data, APIs, OCR, model calls, fonts, or external assets were introduced, and the output remains a single self-contained HTML file with no external URLs.

Validation for the visual alignment pass:

```text
python3 scripts/generate_reviewer.py
python3 -m pytest tests/test_reviewer.py tests/test_reproduction_path.py
```

The regenerated reviewer HTML and screenshot are:

- `docs/evidence/crosswise_reviewer_v1_0.html`
- `docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`

## Commands Executed

```bash
python3 scripts/generate_reviewer.py
python3 -m pytest tests/test_reviewer.py tests/test_reproduction_path.py
python3 scripts/run_full_pipeline.py
python3 scripts/generate_reviewer.py
python3 -m pytest
git status --short
```

## Validation Results

Targeted reviewer and reproduction tests:

```text
16 passed
```

Full validation:

```text
Full pipeline completed successfully.
Fixture validation passed with 12 passed checks, 0 warnings, and 0 failures.
Reconciliation completed for 10 bundles and 10 detected cases.
Evaluation reported overall precision 1.0, overall recall 1.0, overall F1 1.0, and macro F1 1.0.
Reliability scoring completed for 10 cases: 1 auto_accept, 8 needs_review, 1 blocked, average confidence 0.674.
Full pytest result: 73 passed.
```

## Limitations

- Static local HTML only.
- Structured-record rendering only.
- No PDFs.
- No OCR.
- No document ingestion.
- No APIs.
- No model calls.
- No Streamlit, React, Next.js, Flask, FastAPI, web server, npm, or build system.
- No deployment or authentication.
- No fuzzy matching expansion.
- No changes to generation, validation, reconciliation, evaluation, reliability, or routing logic.
- Synthetic data only.
- No real documents, real supplier data, PII, payment information, tax identifiers, or bank details.
- No autonomous actions.
- Not accounting, tax, legal, financial, payment, compliance, or business-action advice.

## Next Slice Recommendation

Slice 10 should perform final portfolio review and presentation audit: verify the README, evidence report, static reviewer, screenshot, scope boundaries, generated artifacts, and tests from the perspective of a technical reviewer before final repository presentation.
