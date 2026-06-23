# Crosswise — Slice 10B Implementation Plan (v1.0)

> Execution plan that translates the **already-approved** UX architecture
> ("Hero Case + Quiet Index") into precise implementation steps. This is not a review, not a
> redesign, and not an implementation — it creates only this file. The UX decision is fixed and
> is not reopened. All Slice 10 scope boundaries remain in force: vanilla inline JS/CSS, one
> self-contained offline HTML file, no framework, no network request, no new
> reconciliation/evaluation/reliability/routing logic, same embedded data.

---

# Objective

Re-architect the **presentation and interaction layer** of the generated reviewer
(`docs/evidence/crosswise_reviewer_v1_0.html`, produced by
`src/crosswise/reviewer/static_html.py`) so it opens as a premium editorial showcase rather
than an enumerated internal tool — **without** changing any value, data source, metric, route,
evidence item, or the self-contained/offline/no-JS guarantees.

Concretely, replace the current "three competing controls (`prev/next` + `jump-to-case`
dropdown + ten numbered chips) over ten always-rendered full document panels" with:

1. One **hero discrepancy frame** above the fold, defaulting to the unit-price-mismatch case.
2. One primary control: a **signature rail** of three named cases (clean / unit price mismatch
   / schema failure) that drives the hero in place.
3. A **quiet, collapsed "Browse all 10 cases" index** below the fold for completeness.
4. Per-case **document panels and evidence** demoted to below-the-fold, opt-in depth.

This is a refactor of rendering functions in one module plus its CSS, inline JS, and tests. No
upstream pipeline code is touched.

---

# Approved UX Direction

Summary of the approved **Hero Case + Quiet Index** model (source of truth: the UX plan):

- **Story first, exploration second, depth third.** The page is comprehensible with zero
  interaction.
- **One job, one control.** Eliminate redundant navigation; the signature rail is the only
  primary control above the fold. `prev/next` and the standalone dropdown leave the top level.
- **Curate, don't enumerate.** Three **named** signature cases visible up top; all ten remain
  available but quiet, below the fold, editorially labeled (not bare numbers).
- **Preserve the premium frame.** The hero stays the showcase comparison table + confidence +
  route; interaction changes the frame's *contents*, not its character.
- **Progressive disclosure of engineering depth.** Raw three-document panels, evidence keys,
  and full taxonomy reveal on demand, below the fold.
- **Default hero = `bundle_unit_price_mismatch_003`** ("Unit price mismatch"): €15.00 vs €13.00,
  +€2.00 Δ, confidence 0.700, `needs_review`.
- **Signature rail spans all three routes** and includes a **clean match** (does not over-flag).
- **Honesty + self-containment preserved:** synthetic-only/non-advice notices, deterministic-
  by-design metrics framing, no-JS fallback, single offline file, zero network requests.

---

# Files To Modify

| File | Nature of change |
|---|---|
| `src/crosswise/reviewer/static_html.py` | Primary work. Refactor `render_static_reviewer` composition; split `_hero_discrepancy_story` into shared chrome + per-case core; replace `_interactive_explorer` (controls/rail/stage) with the signature rail + quiet `<details>` index + synced detail; extend `_css()`; rewrite `_explorer_script()` selection wiring; adjust `INTERACTIVE_EXPLORER_SELECTOR` if the screenshot target id changes. |
| `tests/test_reviewer.py` | Update assertions tied to removed/relocated controls and headings; add tests for the rail, quiet index, per-case hero re-render, and above-the-fold control absence. |
| `docs/evidence/crosswise_reviewer_v1_0.html` | Regenerated artifact (output of the generator; not hand-edited). |
| `docs/evidence/CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png` | Regenerated screenshot of the new above-the-fold hero + rail. |
| `docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png` | Regenerated only if the hero markup/selector changes its framing; otherwise unchanged. |

Optional (only if a constant changes): `src/crosswise/reviewer/__init__.py` re-exports — keep
in sync if any public constant name changes (e.g. `INTERACTIVE_EXPLORER_SELECTOR`). Prefer not
to rename exported names.

---

# Files Not To Modify

Must remain untouched (no logic, data, or contract changes):

- All upstream pipeline modules: `src/crosswise/generation`, `schemas`, `validation`,
  `normalization`, `matching`, `reconciliation`, `evaluation`, `confidence`, `routing`,
  `reporting` — and any module that produces the JSON the reviewer consumes.
- All generated data: `data/synthetic/`, `data/ground_truth/`, `data/reconciliation/`,
  `data/evaluation/`, `data/reliability/`. Values are read, never recomputed or rewritten.
- `scripts/generate_synthetic_data.py`, `validate_fixtures.py`, `run_reconciliation.py`,
  `evaluate_reconciliation.py`, `score_reliability.py`, `generate_report.py`,
  `run_full_pipeline.py`. `scripts/generate_reviewer.py` stays as-is unless a public constant
  it imports is renamed (avoid renaming).
- The data-reading helpers in `static_html.py` that map to source outputs:
  `load_required_outputs`, `_fixture_index`, `_select_hero_case`, `_hero_comparison_rows`,
  `_field_highlight`, `_header_highlight`, `_affected_line_ids`, `_evidence_summary`,
  `_format_metric`, `_e`, and the money/number helpers. Selection/layout may change; **the
  values these compute from source must not**.
- `assets/prototypes/crosswise-prototype.zip` (preserved artifact — never regenerate/overwrite).
- README.md (out of scope for this slice unless separately authorized).
- All non-reviewer tests.

---

# Implementation Breakdown

### Phase 1 — Split the hero into shared chrome + per-case core

- **Purpose:** Make the premium hero frame *case-variable* so selection can re-render it in
  place, while rendering the masthead/features/footer only once.
- **Files:** `src/crosswise/reviewer/static_html.py`.
- **Steps:** Refactor `_hero_discrepancy_story` into:
  (a) static chrome rendered once — `rev-brand`, `rev-features`, `rev-foot`;
  (b) a per-case **hero core** factory (context line + `comparison-wrap` table + `rev-decision`
  confidence/action) that accepts any case and is generated for **every** case, each tagged
  `data-hero-core="<bundle_id>"`, with the default (`unit_price_mismatch_003`) marked active.
  Reuse the existing `_hero_comparison_rows`, `_hero_money_row`, `_hero_numeric_row`
  unchanged — same values, just rendered per case.
- **Expected outcome:** N hero cores embedded at generation time (no recompute), default
  visible; chrome appears once. No-JS shows the default core.

### Phase 2 — Build the signature rail (primary control)

- **Purpose:** One curated, named control above the fold.
- **Files:** `static_html.py` (+ `_css()`).
- **Steps:** Add a `_signature_rail(...)` that selects exactly three cases — clean match,
  unit-price mismatch, schema validation failure — via existing label/route lookups
  (`_first_case`, `_first_route_case`). Render three named buttons with a one-word purpose each
  and `data-case="<bundle_id>"`; mark the default active. Place directly under the hero core.
- **Expected outcome:** Three labeled, route-spanning choices including a clean match; selecting
  one sets the active case.

### Phase 3 — Build the quiet index (full ten, collapsed)

- **Purpose:** Preserve full-set access without enumerating ten chips above the fold.
- **Files:** `static_html.py` (+ `_css()`).
- **Steps:** Replace the `.explorer-rail`/`.explorer-controls` block with a below-the-fold
  `<details class="case-index">` (collapsed by default) containing all ten editorially-labeled
  entries (`_story_title`), each `data-case="<bundle_id>"`. `<details>` gives native, JS-free
  expand/collapse, so the no-JS fallback degrades cleanly. Remove `prev/next`, the
  `jump-to-case` `<select>`, and the `.explorer-position` counter from the top level. (Optional:
  a lightweight prev/next *inside* the open index only — never above the fold.)
- **Expected outcome:** All ten cases reachable, named, quiet, collapsible; redundant top-level
  controls gone.

### Phase 4 — Demote document panels + evidence to per-case detail

- **Purpose:** Engineering depth below the fold, synced to the selected case.
- **Files:** `static_html.py` (+ `_css()`).
- **Steps:** Keep `_document_story` / `_purchase_order_panel` / `_invoice_panel` /
  `_receipt_panel` / `_explanation_block` and their highlight logic **unchanged in value**, but
  render each case's detail in a below-the-fold "Inspect the documents / Why it flagged" region
  tagged `data-detail="<bundle_id>"`, default active, secondary visual weight. Reframe the
  four-column `explanation-grid` as a calmer "Why" block (CSS only; same content/keys).
- **Expected outcome:** Documents + evidence present for every case, opt-in, at lower altitude.

### Phase 5 — Unify selection state and inline JS

- **Purpose:** One selected-case id drives hero core, detail, rail, and index.
- **Files:** `static_html.py` (`_explorer_script`, `_css()`).
- **Steps:** Rewrite `_explorer_script` to read a single active `data-case` id, toggle
  `.is-active` on every `[data-hero-core]`, `[data-detail]`, rail button, and index entry
  sharing that id, and set `aria-pressed`/`aria-current`. Rail and index clicks call one
  `setActive(id)`. Keep the script free of `//`, `src=`, `import`, `fetch(` (the existing
  no-external-URL guard). Gate visibility with the existing `.js-on` pattern so no-JS shows the
  default case fully.
- **Expected outcome:** Clicking any rail or index entry re-renders hero + detail in place;
  offline, dependency-free, no-JS safe.

### Phase 6 — Editorial lede copy

- **Purpose:** Lead with the promise, not the mechanism.
- **Files:** `static_html.py` (`_hero` and the explorer section heading).
- **Steps:** Update the lede to a value headline (e.g. "Crosswise detected a discrepancy — and
  shows you why") with one quiet sub-line. Demote/replace the "Browse Every Reconciliation
  Case / Interactive case explorer" heading; "browse all cases" language moves onto the quiet
  index. No data changes.
- **Expected outcome:** First textual block names the value; mechanism language is demoted.

### Phase 7 — Tests, regeneration, screenshots

- **Purpose:** Lock the new structure and refresh artifacts.
- **Files:** `tests/test_reviewer.py`, then regenerate HTML + PNGs via
  `scripts/generate_reviewer.py`.
- **Steps:** Update/add tests per the Test Plan; run `python3 -m pytest`; regenerate the
  reviewer and screenshots; confirm `git status --short`.
- **Expected outcome:** Green suite, refreshed artifacts, no out-of-scope diffs.

---

# Hero Section Changes

**What remains:**

- The showcase frame: `rev-brand` masthead, `comparison-wrap` Field/Invoice/PO/Δ/Status table
  with the gold `is-disagreement` rows, `rev-decision` confidence meter + "Route to human
  review" action, the three `rev-features` pillars, and `rev-foot`.
- The default hero case stays `bundle_unit_price_mismatch_003` (€15.00 vs €13.00, +€2.00,
  confidence 0.700, `needs_review`) via the unchanged `_select_hero_case` preference order.
- All comparison values come from `_hero_comparison_rows` — unchanged.

**What changes:**

- The case-variable part of the hero (context line + comparison table + confidence/action) is
  rendered **per case** and toggled by selection (Phase 1), instead of a single static case.
- The masthead, features, and footer render once as shared chrome, not per case.
- The lede headline above the frame becomes value-first (Phase 6).

---

# Signature Rail Implementation

- **Three curated cases:**
  1. **Clean match** — `clean_match` (route `auto_accept`) — purpose word: *does not over-flag*.
  2. **Unit price mismatch** — `unit_price_mismatch` (route `needs_review`) — *catches the
     discrepancy*; this is the **default**.
  3. **Schema validation failure** — `schema_validation_failure` (route `blocked`) — *blocks
     bad data*.
  Selected via existing lookups (`_first_case` for clean, label/route lookups for the others);
  the three span `auto_accept` / `needs_review` / `blocked`.
- **Visual behavior:** a single calm row of three named segments/cards directly beneath the hero
  core; editorial labels + one-word purpose; the active one is visibly selected (amber, matching
  the existing `is-active` chip styling). Not numbered. No more than three above the fold.
- **Selection behavior:** clicking a rail item calls `setActive(bundle_id)`, which toggles the
  matching `[data-hero-core]` and `[data-detail]` to `.is-active`, updates `aria-pressed`, and
  syncs the quiet index's current marker. The hero re-renders in place; no scroll jump.

---

# Quiet Index Implementation

- **Full 10-case access:** a below-the-fold `<details class="case-index">` whose summary reads
  e.g. "Browse all 10 cases", containing ten entries — one per reconciliation case, ordered by
  `bundle_id`, each labeled editorially via `_story_title` and carrying `data-case` plus a small
  secondary numeric identifier (number allowed *here*, not in the rail).
- **Expand/collapse behavior:** native HTML `<details>/<summary>` — works without JavaScript.
  When open, selecting any entry calls the same `setActive(id)` as the rail and (optionally)
  collapses the index. The default/active entry is marked.
- **No-JS fallback:** with scripting off, `<details>` still expands/collapses natively; the
  default hero core and the default detail remain visible (gated by the existing `.js-on`
  pattern so non-active cores/details only hide when JS is present). Every case's title and
  route stay readable. The "JavaScript is disabled…" note is retained/adapted.

---

# Case Detail Area

For the currently selected case, below the fold, at secondary weight:

- **Document panels:** `_purchase_order_panel`, `_invoice_panel`, `_receipt_panel` rendered via
  `_document_story` — the three-column PO/Invoice/Receipt view with `data-document-panel`
  attributes and per-field/per-line highlights from `_field_highlight` / `_header_highlight` /
  `_line_highlight`. Values and highlight logic unchanged.
- **Evidence:** `_explanation_block` retained — detected label(s), plain-English reason, the
  `_evidence_summary` reference (e.g. `…unit_price_difference: invoice_unit_price=15.00,
  po_unit_price=13.00`), shown at reduced visual weight (CSS only).
- **Confidence:** the case's `confidence_score` via `_format_metric` (e.g. `0.700`), consistent
  with the hero meter.
- **Route:** the case's `reliability_route` pill (`route-auto_accept` / `route-needs_review` /
  `route-blocked`), styling unchanged.
- **Explanation:** the "What happened / Why flagged / Evidence / Route assigned" content,
  reframed visually into a calmer "Why it flagged" block — same text, same keys, lower altitude.

Each case's detail is tagged `data-detail="<bundle_id>"`, default active, toggled by the same
selection state as the hero and rail.

---

# Interaction Architecture

- **Selected-case state:** a single active `bundle_id`. The DOM is the store: regions carry
  `data-hero-core`, `data-detail`, `data-case` (rail/index) attributes keyed by `bundle_id`; the
  active one(s) hold `.is-active`. Default = `data-explorer-default` (or equivalent) =
  `bundle_unit_price_mismatch_003`.
- **Event flow:** rail button click and index entry click → `setActive(id)` → toggle
  `.is-active` on all elements whose `data-*` id matches; update `aria-pressed` (rail) /
  `aria-current` (index); optionally collapse the index. No prev/next, no `<select>` change
  handler at the top level.
- **Rendering strategy:** **render everything at generation time, toggle visibility with JS.**
  Every hero core and every detail block is embedded from source outputs (no client-side
  recompute, no fetch). JS only flips which pre-rendered case is shown — preserving "displayed
  values exactly equal source values" and the offline guarantee. CSS gates non-active
  cores/details behind `.js-on` so the no-JS path shows the default case fully and the rest via
  the native `<details>` list. Script stays inline, dependency-free, and free of `//`, `src=`,
  `import`, `fetch(`.

---

# Test Plan

**Tests to update** (`tests/test_reviewer.py`):

- `test_reviewer_html_contains_hero_story_and_interactive_explorer` — keep the hero assertions
  (`data-hero-case`/core for `bundle_unit_price_mismatch_003`, `data-hero-comparison`, "Route to
  human review"); replace the "Browse Every Reconciliation Case" heading string and the
  `data-explorer-panel` count with the new quiet-index structure (ten `data-case` entries).
- `test_reviewer_interactive_controls_exist` — remove assertions for `data-explorer-prev`,
  `data-explorer-next`, `data-explorer-select`, `data-explorer-position`, the 10 chips, and 10
  `<option>`s; replace with: signature rail has exactly three `data-case` items, quiet index has
  ten, inline `<script>` present, `js-on` toggling present, default attribute present.
- `test_reviewer_interactive_default_case_is_a_discrepancy` — keep default =
  `bundle_unit_price_mismatch_003`; retarget the active-panel assertion to the active hero core
  / detail markers; confirm the clean match is not the default.
- `test_reviewer_interactive_panels_match_source_outputs` — keep value-equality intent; retarget
  the slicer from `explorer-panel` to the new per-case detail/hero-core blocks; still assert each
  case's route + `:.3f` confidence appear in its block.
- `test_reviewer_interactive_highlights_update_per_case` — retarget slices to the new detail
  blocks; keep quantity/supplier-alias highlight + clean-match-no-highlight assertions.
- `test_reviewer_no_js_fallback_content_present` — update to the new `.js-on` gating and
  `<details>` index; keep notices/metrics/`python3 -m pytest` and the ten-case presence.
- `test_reviewer_html_renders_document_panels_and_highlights` — keep the 10×
  `data-document-panel` counts and highlight assertions (panels now live in the detail region).

**Tests to keep unchanged:** `test_reviewer_html_contains_required_notices`,
`…_evaluation_metrics`, `…_reliability_counts`, `…_at_least_one_case_row`,
`test_reviewer_script_has_no_external_or_unsafe_sequences`,
`test_reviewer_hero_comparison_shows_field_level_delta`,
`…_evidence_route_and_explanation_blocks` (adjust only if container names change),
`…_reproduction_commands`, `test_reviewer_html_has_no_external_urls`,
`…_output_is_deterministic_across_repeated_renders`, `test_reviewer_script_runs_and_creates_output`.

**Tests to add:**

- Signature rail contains **exactly three** named cases and includes the clean match; the three
  routes present are `auto_accept`, `needs_review`, `blocked`.
- No top-level `prev`/`next`/`jump-to-case` controls remain above the fold (assert their former
  hooks are absent or only inside the index).
- A per-case **hero core** is embedded for every case (`data-hero-core` count == case count),
  default = `bundle_unit_price_mismatch_003` is active.
- Quiet index is a `<details>` containing all ten editorially-labeled cases.
- Selection wiring: `setActive` toggles a single id across rail/index/hero/detail (assert shared
  `data-case` ids line up).

**Validation expectations:** full `python3 -m pytest` green; displayed values still equal source
outputs; zero network requests / no external URLs (existing guards stay green); deterministic
render; reviewer opens by double-click and is legible with JS disabled.

---

# Screenshot Strategy

- **Screenshot target:** the **above-the-fold hero region on the default case** — the hero core
  (comparison table + confidence + action) **plus** the signature rail — captured via
  `generate_reviewer_screenshot` into
  `docs/evidence/CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png`. Point the interactive selector
  (currently `INTERACTIVE_EXPLORER_SELECTOR = "#interactive-case-explorer"`) at the element that
  wraps hero core + rail; rename the constant only if necessary and keep
  `__init__.py`/`generate_reviewer.py` imports consistent. Regenerate the discrepancy showcase
  (`#document-panel-reconciliation-view`) only if hero markup framing changes.
- **What should be visible:** the editorial lede headline; the gold-flagged unit-price/line-total
  rows with the Δ column; the `0.700 below threshold` confidence meter; the "Route to human
  review" action; the three named signature cases with the unit-price one selected.
- **What should NOT be visible:** the ten-item enumeration, `prev/next`, the `jump-to-case`
  dropdown, raw evidence keys, and the three raw document panels — all of which now live below
  the fold and must be outside the captured frame.

---

# Acceptance Criteria

- The reviewer **opens on the unit-price-mismatch hero** (showcase comparison frame), legible
  with **zero interaction** on one laptop viewport.
- **Exactly one** primary control above the fold (the three-case signature rail); no top-level
  `prev/next` or `jump-to-case` dropdown.
- **At most three** selectable cases above the fold; **all ten** reachable only via the
  below-the-fold `<details>` index, **editorially named**.
- Signature rail spans `auto_accept` / `needs_review` / `blocked` and includes a **clean match**.
- Raw document panels + evidence render **below the fold** for the selected case at secondary
  weight; selecting a rail or index item re-renders hero **and** detail in place.
- **Displayed values exactly equal** the underlying reconciliation/reliability outputs; a test
  asserts equality; nothing is recomputed client-side.
- Synthetic-only/non-advice notices, deterministic-by-design metrics, three pillars, and
  reproduce commands are **retained** and serve as the **no-JS fallback**; the page is legible
  with scripting disabled (native `<details>` + default case visible).
- The artifact is a **single self-contained offline HTML file**, vanilla inline JS/CSS only, with
  **no external URL and no network request** (existing guard tests stay green).
- `python3 -m pytest` passes; reviewer + both screenshots regenerated.
- `git status --short` shows only intended changes; the prototype ZIP is untouched.

---

# Risks

| Risk | Mitigation |
|---|---|
| Per-case hero cores duplicate masthead/features/footer ten times. | Split into shared chrome (rendered once) + per-case core (rendered N times); only the core toggles. |
| Removing `prev/next`/dropdown breaks tests that assert them. | Update those tests deliberately (Test Plan); add tests asserting their absence above the fold. |
| Selection desyncs hero vs detail vs index. | Single `setActive(id)` toggling all `data-case`/`data-hero-core`/`data-detail` by shared id; test the ids line up. |
| Client-side rendering would risk value drift. | Render-all-at-generation, JS toggles visibility only; keep the value-equality test. |
| Inline JS introduces a forbidden sequence (`//`, `src=`, `import`, `fetch(`, external URL). | Keep `test_reviewer_script_has_no_external_or_unsafe_sequences` and `…_has_no_external_urls` green; reuse the block-comment-only style. |
| No-JS users lose navigation. | Native `<details>` index + default case visible without JS; `.js-on` gates only enhancement. |
| Screenshot captures below-the-fold clutter. | Target only the hero-core + rail wrapper element; verify the enumeration/panels are outside the frame. |
| Scope creep into engine/data. | Touch only `static_html.py`, its CSS/JS, and `test_reviewer.py`; data-reading helpers keep computing from source. |

---

# Out-of-Scope

- OCR, PDFs, document ingestion/parsing, real documents.
- APIs, model calls, network requests, CDNs, external JS/CSS/fonts.
- Web servers/frameworks (Streamlit, React, Next.js, Flask, FastAPI, Node), npm, `package.json`,
  bundlers, build systems.
- Deployment, authentication, databases, persisted reviewer state.
- Any change to reconciliation, evaluation, confidence, reliability, routing, or generation
  **logic**, or to generated data/metrics/routes/evidence.
- README.md edits (separate authorization required).
- Regenerating or overwriting `assets/prototypes/crosswise-prototype.zip`.
- Adding cases, changing the taxonomy, or reopening the approved UX decision.
- Any git branch/remote/commit/push/tag operation.

---

# Recommended Commit Boundary

A single, self-contained commit on the current branch (staged/committed only when the owner
explicitly instructs — not by this plan), scoped to:

- `src/crosswise/reviewer/static_html.py` — hero split, signature rail, quiet `<details>` index,
  demoted detail region, unified selection JS, CSS, lede copy.
- `src/crosswise/reviewer/__init__.py` — only if a re-exported constant name changed.
- `tests/test_reviewer.py` — updated + added tests per the Test Plan.
- `docs/evidence/crosswise_reviewer_v1_0.html` — regenerated artifact.
- `docs/evidence/CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png` — regenerated screenshot;
  `CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png` only if hero framing changed.

Suggested message: `Slice 10B: hero + signature rail + quiet index reviewer UX`. Exclude any
data/, pipeline, README, AGENTS, or prototype changes from this commit. Stop after
implementation, `python3 -m pytest`, artifact regeneration, and `git status --short`.

---

*Document version 1.0. Execution plan only — no code, no implementation, no screenshots; only
this file created. The approved Hero Case + Quiet Index UX, the Crosswise name, direction, and
all Slice 10 scope boundaries are treated as fixed and are not reopened.*
