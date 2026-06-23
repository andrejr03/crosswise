# Crosswise Slice 10 — Interactive Document-Panel Reviewer (v1.0)

Presentation-and-interaction slice. Transforms the existing static reviewer into a
self-contained, offline interactive case explorer. No generation, validation,
normalization, reconciliation, evaluation, confidence, routing, generated data, metrics,
or routes were changed. The reviewer reads only existing generated outputs and recomputes
nothing.

## 1. Implemented Components

- **Interactive case explorer** (`#interactive-case-explorer`) added to
  `src/crosswise/reviewer/static_html.py`, rendered below the showcase hero and the metric
  strip. It replaces the former static "Condensed Review Queue" with a browsable set of all
  ten generated cases.
- **Navigation controls**: previous / next buttons with a live "Case N of 10" position
  indicator, a "Jump to case" `<select>` with one option per bundle, and a chip rail with
  one route-colored chip per case.
- **Full per-case panels**: every bundle (including the hero bundle) is rendered as a
  complete document story — side-by-side Purchase Order / Invoice / Receipt panels, the
  highlighted disagreeing field(s), and an inline explanation block carrying the detected
  label, evidence summary, confidence score, and route.
- **Inline navigation script**: a single dependency-free `<script>` using only vanilla DOM
  APIs. It adds a `js-on` class, then shows one pre-rendered panel at a time and keeps the
  selector, chips, and prev/next in sync. The script avoids the `//` sequence entirely
  (block comments only) so the generated HTML keeps zero external-URL substrings.
- **Interactive screenshot generation**: `scripts/generate_reviewer.py` now also captures
  `docs/evidence/CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png` of the explorer with a
  discrepancy case selected, via the new `INTERACTIVE_EXPLORER_SELECTOR` /
  `INTERACTIVE_SCREENSHOT_OUTPUT_PATH` exports.
- **Documentation**: minimal README updates (Slice 10 status line, interactive showcase in
  Generated Outputs and Documentation) and this evidence document; evidence INDEX updated.

## 2. Interaction Model

- The explorer opens on `bundle_unit_price_mismatch_003` (`data-explorer-default`) so the
  default view — and the interactive screenshot — land on a clear field-level discrepancy.
- Selecting a chip, choosing an option, or pressing prev/next activates exactly one panel
  (`.is-active`); all other panels are hidden by CSS scoped to `.js-on`.
- All displayed values are embedded server-side from existing generated outputs. The script
  only toggles visibility — it performs no computation, fetch, or data transformation.

## 3. No-JS Fallback

- Controls (`.explorer-controls`, `.explorer-rail`) are hidden by default and only revealed
  under the `.js-on` class, so a no-JavaScript reviewer sees no dead controls.
- Panel hiding is also gated behind `.js-on` (`.js-on .explorer-stage > .explorer-panel:not(.is-active)`),
  so with scripting disabled **every** case panel remains visible in sequence.
- A fallback note ("JavaScript is disabled, so every generated case is shown in sequence
  below.") is shown only when scripting is off.
- All prior static substance — scope notices, evaluation/reliability metric strip, pipeline
  summary, and reproduction commands — remains rendered server-side and unaffected.

## 4. Commands Executed

```bash
python3 scripts/run_full_pipeline.py
python3 scripts/generate_reviewer.py
python3 -m pytest
git status --short
```

## 5. Validation Results

- `python3 scripts/run_full_pipeline.py` — completed successfully; regenerated all data
  artifacts, the evidence report, the reviewer HTML, and both screenshots (discrepancy +
  interactive).
- `python3 scripts/generate_reviewer.py` — wrote `crosswise_reviewer_v1_0.html`,
  `CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`, and
  `CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png`.
- `python3 -m pytest` — **79 passed** (6 new reviewer tests added) covering: interactive
  controls exist; all ten cases available as panels, chips, and options; per-case panel
  values match source reliability route and confidence; highlights update per case (clean
  match carries none); no-JS fallback content present; the inline script contains no
  external/protocol-relative/`//` sequences; default case is a discrepancy; deterministic
  render preserved; existing notices/metrics/commands intact.
- Metrics and routes unchanged: precision/recall/F1/macro-F1 = 1.000; reliability routing
  1 `auto_accept` / 8 `needs_review` / 1 `blocked`; average confidence 0.674.

## 6. Limitations

- Synthetic data only; deterministic baseline only.
- No OCR, no PDFs, no document ingestion, no APIs, no model calls, no autonomous actions.
- The reviewer is a single self-contained local HTML file with inline CSS and one inline
  vanilla-JavaScript block; it makes no network request and starts no server.
- Interaction is presentation-only progressive enhancement; it toggles visibility of
  pre-rendered panels and never recomputes reconciliation, evaluation, confidence, or
  routing.
- Not accounting, tax, legal, financial, payment, compliance, or business-action advice.

## 7. Next Slice Recommendation

Phase 2B — Synthetic Document Pack Generation: render the existing structured records as
document-style synthetic invoice / purchase order / receipt artifacts (no OCR, no parsing,
no ingestion), strictly bounded to preserve the current synthetic-only, no-network,
no-dependency posture. Evaluate against the interactive reviewer's gains before committing,
since document-style artifacts must add a distinct signal rather than duplicate the panels
the explorer already renders.
