# Crosswise — Phase 2B HTML Document Pack Implementation Plan (v1.0)

> Implementation plan translating the approved Phase 2B architecture decision
> (**PROCEED WITH HTML-ONLY SYNTHETIC DOCUMENTS**) into a precise, bounded build. The
> architecture decision is settled and is **not** reopened here. Approved source:
> `docs/reviews/CROSSWISE_PHASE_2B_SYNTHETIC_DOCUMENT_PACK_ARCHITECTURE_REVIEW_v1.0.md`.
> This document plans only; it creates, implements, and modifies no code, no data, no
> tests, and no screenshots. It creates only this file. Paths, modules, fixtures, and
> field names below are grounded in the current repository
> (`data/synthetic/fixtures_v1_0.json`, `src/crosswise/`, `scripts/`, `tests/`). The
> Crosswise name, direction, and scope boundaries are fixed.

---

# Objective

Produce a small, fixed pack of standalone, self-contained synthetic business documents —
`invoice.html`, `purchase_order.html`, `receipt.html` — rendered deterministically from the
**existing** synthetic fixtures, to make the *input side* of Crosswise visible for the first
time. The documents are honest, illustrative renders of generated source records. They are
not parsed, ingested, or read back; there is no OCR and no read path. The deliverable adds
one new visual signal (the document form factor) at zero new dependency, zero network
request, and zero change to existing logic, data, metrics, routes, evidence, or the reviewer.

---

# Approved Architecture

Per the approved architecture review, Phase 2B is **HTML-only**:

- Exactly three standalone, single-file HTML documents, generated from existing fixtures.
- Inline CSS in the reviewer's established aesthetic; **no** external script, font, CSS, CDN,
  or network request; openable by double-click and inline-previewable on a repository page.
- A visible, honest caption on every document marking it synthetic, illustrative, and
  deliberately not-ingested (no OCR).
- Render-only: no new reconciliation/evaluation/confidence/routing logic; no parser; no read
  path of any kind.
- PDF, HTML+PDF, reviewer-only rendering, and "no document phase" were evaluated and rejected
  in the approved review and are not reconsidered here.

---

# Representative Bundle Strategy

**Render exactly one bundle: `bundle_unit_price_mismatch_003`.** Its documents are
`SYN-INV-0003` (invoice `inv_003_a`), purchase order `po_003`, and receipt `rcpt_003`.

Why this bundle:

- **Direct narrative tie to the existing hero.** The published showcase
  (`CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`) is exactly `SYN-INV-0003` vs `PO 003`,
  unit price €15.00 vs €13.00. Rendering this bundle's raw documents shows the recruiter the
  *input* that produces the famous flagged panel — closing the arc *document → comparison →
  evidence → route* with zero new story to learn.
- **The discrepancy is emergent, not annotated.** The unit-price difference lives *between*
  the invoice and the PO; each document on its own is an ordinary, internally-consistent
  business document. The pack therefore stays honest: the documents do not flag anything; the
  reconciler is what finds the difference. This demonstrates exactly why reconciliation is
  needed.
- **One bundle, three internally-consistent documents.** Invoice, PO, and receipt depict the
  same bundle (same supplier, same SKUs, same line structure), satisfying the approved
  consistency requirement.

Rejected alternative: `bundle_clean_match_001`. It is a clean baseline but is disconnected
from the hero showcase and tells no story (all values agree), so it delivers less
memorability for the same cost. It is noted here only to record that the choice was
deliberate; it is not rendered.

Scale boundary: **one bundle only.** Rendering more bundles is out of scope (see
Out-of-Scope) to keep the pack to exactly three files.

---

# Output Structure

Generated artifacts (produced by running the generator during implementation; **not** created
by this plan):

```
docs/evidence/documents/invoice.html
docs/evidence/documents/purchase_order.html
docs/evidence/documents/receipt.html
docs/evidence/CROSSWISE_DOCUMENT_PACK_SHOWCASE.png   (single still, see Screenshot Strategy)
```

Rationale: a dedicated `docs/evidence/documents/` subdirectory keeps the three loose document
files tidy and clearly separated from reports and the reviewer, consistent with the
`AGENTS.md` Documentation Policy (evidence under `docs/evidence/`). The showcase PNG sits at
the `docs/evidence/` root alongside the existing reviewer screenshots for naming consistency.

---

# Files To Create

Source and tooling (the implementing slice creates these):

- `src/crosswise/documents/__init__.py` — small public surface that re-exports the generator
  entrypoints and the output-path constants (mirrors the `src/crosswise/reviewer/` pattern).
- `src/crosswise/documents/synthetic_documents.py` — the document renderer:
  - load existing fixtures from `data/synthetic/fixtures_v1_0.json` (read-only, same loader
    convention as `reviewer/static_html.py`);
  - select `bundle_unit_price_mismatch_003` and assemble its invoice, PO, and receipt records
    plus their line items;
  - render three self-contained HTML strings (inline CSS, no external assets);
  - write them to the paths in **Output Structure**;
  - expose path constants (`DOCUMENTS_OUTPUT_DIR`, `INVOICE_OUTPUT_PATH`,
    `PURCHASE_ORDER_OUTPUT_PATH`, `RECEIPT_OUTPUT_PATH`,
    `DOCUMENT_PACK_SCREENSHOT_OUTPUT_PATH`) and a `REPRESENTATIVE_BUNDLE_ID` constant;
  - provide a `generate_document_pack(repo_root)` function and an optional
    `generate_document_pack_screenshot(...)` reusing the existing Playwright helper pattern
    from the reviewer module.
- `scripts/generate_documents.py` — thin CLI entrypoint mirroring
  `scripts/generate_reviewer.py` (sys.path bootstrap → call generator → print output paths →
  return exit code; `FileNotFoundError` if upstream fixtures are missing, with the same
  "run the pipeline first" guidance).
- `tests/test_documents.py` — tests per the **Test Plan**.

Generated output artifacts (produced by running `scripts/generate_documents.py`, listed for
completeness — not authored by hand): the three HTML files and the one PNG in **Output
Structure**.

---

# Files To Modify

Default: **none required.** The feature is fully additive.

Optional (only if trivially safe; each is independently droppable):

- `scripts/run_full_pipeline.py` — append a single call to the new document generation step so
  the one-command pipeline also emits the document pack. Permitted only if it adds no new
  dependency, no network request, and does not reorder or alter existing steps. If it
  introduces any risk to the existing pipeline, **do not modify it**; running
  `scripts/generate_documents.py` separately is acceptable.
- `docs/evidence/crosswise_reviewer_v1_0.html` generation in
  `src/crosswise/reviewer/static_html.py` — only if the optional reviewer link is adopted
  (see Reviewer Integration Strategy). This is additive (a relative-path hyperlink) and must
  not change any existing reviewer content, values, or the no-network guarantee.

No other existing file is modified. README updates are out of scope (see Out-of-Scope).

---

# Files Not To Modify

- `data/synthetic/fixtures_v1_0.json`, `data/ground_truth/`, `data/reconciliation/`,
  `data/evaluation/`, `data/reliability/` — all existing data preserved unchanged.
- `src/crosswise/` modules for generation, schemas, validation, normalization, matching,
  reconciliation, evaluation, confidence, routing, reporting — no logic touched.
- `docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md` and existing reviewer screenshots.
- Existing tests in `tests/` (unless an additive shared fixture is genuinely required; prefer
  a new test module).
- `README.md` and `AGENTS.md`.
- `assets/prototypes/crosswise-prototype.zip` — never touched.

---

# Document Architecture

All three documents render from the same `bundle_unit_price_mismatch_003` records and line
items already present in the fixtures. Each document is a faithful, ordinary business-document
layout — header block, party block, line-item table, totals — with **no** flags, deltas,
status columns, or reconciliation annotations (those belong to the reviewer, not the source
document). All values are bound directly from fixtures; none are hand-authored.

## Invoice (`invoice.html`, from `inv_003_a` / `SYN-INV-0003`)

- **Header:** document type "Invoice", `invoice_number`, `invoice_date`, `due_date`,
  `currency`.
- **Supplier / bill-to block:** `supplier_name_raw` (and, for honesty, it is the raw name as
  it appears on the synthetic document).
- **Line-item table:** one row per invoice line (`line_number`, `description` / `sku_raw`,
  `quantity_billed`, `unit_of_measure`, `unit_price`, `line_total`).
- **Totals block:** `subtotal`, `tax_amount`, `total_amount`.
- The unit price here is the invoice's value (e.g. the €15.00 side); it is presented plainly,
  not compared.

## Purchase Order (`purchase_order.html`, from `po_003`)

- **Header:** document type "Purchase Order", `purchase_order_id`/number, `issue_date`,
  `expected_receipt_date`, `status`, `currency`.
- **Supplier block:** supplier as carried on the PO.
- **Line-item table:** one row per PO line (`line_number`, `description`, `quantity_ordered`,
  `unit_price`, `line_total`).
- **Totals block:** `subtotal`, `tax_amount`, `total_amount`.
- The PO unit price is its own value (e.g. the €13.00 side), presented plainly.

## Receipt (`receipt.html`, from `rcpt_003`)

- **Header:** document type "Goods Receipt", `receipt_number`, `receipt_date`,
  `related_purchase_order_id`.
- **Supplier block:** `supplier_name_raw`.
- **Line-item table:** one row per receipt line (`line_number`, `sku_raw`,
  `quantity_received`, `received_date`). Receipts carry quantities received, not prices —
  render only the fields that exist; do not invent prices.

If any optional field is absent for a record, omit that row/cell rather than fabricating a
value.

---

# Visual Design Direction

- Reuse the reviewer's existing aesthetic family so the pack reads as part of Crosswise: the
  same CSS custom-property palette already defined in `crosswise_reviewer_v1_0.html`
  (`--page #171511`, `--ink #eee8dd`, `--panel`, `--line`, `--amber #c9a24b`, serif display +
  monospace labels). Define these inline in each document; do **not** import or share an
  external stylesheet.
- Documents should read as documents, not as the reviewer's comparison panel: a calm,
  print-like single-column layout — masthead, party block, ruled line-item table, right-set
  totals — distinct from the side-by-side reviewer view.
- System fonts only (e.g. Georgia/serif for the masthead, Menlo/monospace for labels and
  figures), matching the reviewer. **No** web fonts, no `@font-face` network fetch, no icon
  fonts.
- Self-contained and offline: inline `<style>` only; no `<script>`; no external `src`/`href`
  to any network resource. The file must render fully by double-click with no network access.
- Keep it legible and modest — this is an honest synthetic document, not a marketing mock.

---

# Caption Strategy

Every document carries a visible caption block (header or footer) with synthetic-only,
non-ingestion wording. Required content (exact phrasing finalized in implementation, meaning
fixed):

- It is a **synthetic, illustrative** render of a generated Crosswise source record.
- It is **not a real document** and contains no real company, supplier, payment, tax, or bank
  data.
- It is **not parsed, ingested, or read back** by Crosswise; there is **no OCR**.
- Crosswise output is **not** accounting, tax, legal, financial, payment, or compliance
  advice.

This mirrors the synthetic-only / non-advice posture already stated in
`CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md` and the reviewer, and is asserted by tests (see Test
Plan). The caption is the primary mitigation against the "does it read these back?"
anti-pattern.

---

# Generation Strategy

- **Source of truth:** read `data/synthetic/fixtures_v1_0.json` only, using the same
  read-only loading convention as `src/crosswise/reviewer/static_html.py`. Do not read or
  write any other data file. Do not regenerate fixtures.
- **Selection:** look up `REPRESENTATIVE_BUNDLE_ID = "bundle_unit_price_mismatch_003"`, then
  resolve its `invoice_ids[0]`, `purchase_order_id`, and `receipt_ids[0]`, and gather the
  matching records and their line items from `invoices`/`invoice_lines`,
  `purchase_orders`/`purchase_order_lines`, `receipts`/`receipt_lines`.
- **Rendering:** pure deterministic Python string/template assembly (f-strings or
  `str.format`), HTML-escaping all interpolated values (reuse `html.escape`, as the reviewer
  does). No templating engine dependency.
- **Determinism:** identical fixtures must produce byte-identical HTML across runs (stable
  ordering by `line_number`, fixed formatting of money/quantity strings as they appear in
  fixtures). Re-running the generator is idempotent.
- **Offline guarantee:** the renderer emits no external `src`/`href`, no `<script>`, and no
  network reference; a test asserts this (see Test Plan).
- **No logic reuse leakage:** the document module must not import reconciliation, evaluation,
  confidence, or routing logic; it only reads fixture records and formats them.

---

# Reviewer Integration Strategy

**Optional and additive only.** A single relative-path hyperlink may be added from the
existing reviewer (`crosswise_reviewer_v1_0.html`) to each generated document
(`documents/invoice.html`, etc.), letting a reviewer click "view source document."

Constraints if adopted:

- Relative `href` only (e.g. `documents/invoice.html`); the link resolves over `file://` with
  no network request.
- Purely additive: no existing reviewer content, value, layout, or the no-network guarantee
  may change; the reviewer remains a single self-contained offline file.
- Gated by the existing reviewer test that displayed values equal source values — that must
  still pass unchanged.

If the link cannot be added without risk, a network request, or reviewer rework, **drop it.**
It is never an acceptance gate; the standalone documents are the deliverable.

---

# Test Plan

Add `tests/test_documents.py` (new module; existing tests untouched unless genuinely
required). Run against generated output and/or the in-memory render:

**Tests to add**

1. **Generation succeeds & files exist** — `generate_document_pack(repo_root)` writes exactly
   `invoice.html`, `purchase_order.html`, `receipt.html` to `docs/evidence/documents/`.
2. **Values match fixtures** — for each document, asserted key values (invoice number, dates,
   supplier name, each line's quantity/unit price/line total, subtotal/tax/total; PO ordered
   quantities and prices; receipt received quantities and dates) **exactly equal** the
   `bundle_unit_price_mismatch_003` fixture values. No hand-authored or divergent numbers.
3. **Internal consistency** — all three documents reference the same bundle (same supplier,
   same SKU descriptions, same line structure).
4. **No network / no script** — generated HTML contains no `<script>`, no `http://`/`https://`
   reference, no external `src`/`href`, no `@font-face`/web-font fetch, no `package.json`
   coupling. (Assert by scanning the output strings.)
5. **Caption present** — each document contains the synthetic-only / not-ingested / no-OCR /
   non-advice caption wording (assert on the required phrases).
6. **Self-contained validity** — each output is a single complete HTML document (has
   `<!doctype html>`, one inline `<style>`, well-formed enough to open standalone).
7. **Determinism** — generating twice yields byte-identical output.
8. **(If reviewer link adopted)** — reviewer contains the relative document links and remains
   network-free; the existing reviewer value-parity test still passes.

**Tests to update**

- None expected. Only if the optional `run_full_pipeline.py` change is made and an existing
  pipeline/reproduction test (`tests/test_reproduction_path.py`) needs the new step
  acknowledged — additive assertion only, never weakening an existing check.

**Validation expectations**

- Full `python3 -m pytest` continues to pass (the existing suite plus the new module).
- Existing metrics (precision/recall/F1 = 1.0, macro-F1 = 1.0), routes
  (1 `auto_accept` / 8 `needs_review` / 1 `blocked`), evidence, and reviewer outputs are
  **unchanged**.

---

# Screenshot Strategy

- **Screenshots required:** one still — `docs/evidence/CROSSWISE_DOCUMENT_PACK_SHOWCASE.png`.
- **Capture target:** the rendered `invoice.html` (the most recognizable of the three and the
  one tied to the `SYN-INV-0003` hero), captured full-document via the existing Playwright
  screenshot helper pattern already used by the reviewer module
  (`generate_reviewer_screenshot`). Generate it through the new
  `generate_document_pack_screenshot(...)` function so the dependency footprint is unchanged
  (Playwright is already a dev-time tool in this repo).
- This still is for an eventual README "input side" first impression; **updating the README
  is out of scope** for Phase 2B and is not part of this plan.
- The plan does not create this screenshot; the implementing slice does.

---

# Acceptance Criteria

Phase 2B is accepted when:

1. `scripts/generate_documents.py` deterministically produces exactly three self-contained
   files — `docs/evidence/documents/invoice.html`, `purchase_order.html`, `receipt.html` —
   from the existing fixtures, with **no new runtime dependency** and **no network request**.
2. All three documents render the `bundle_unit_price_mismatch_003` records (`SYN-INV-0003`,
   `po_003`, `rcpt_003`) and are internally consistent (same supplier, SKUs, line structure).
3. Each document opens by double-click and renders fully offline; no `<script>`, no external
   `src`/`href`, no web font, no CDN (asserted by tests).
4. Displayed values **exactly equal** the underlying fixture values (asserted by tests); no
   hand-authored numbers.
5. Each document carries the required synthetic-only / not-ingested / no-OCR / non-advice
   caption (asserted by tests).
6. `docs/evidence/CROSSWISE_DOCUMENT_PACK_SHOWCASE.png` is produced from the rendered invoice.
7. Existing logic, data, metrics, routes, evidence, and the reviewer are **unchanged**; full
   `python3 -m pytest` passes (existing suite + new `tests/test_documents.py`).
8. If the optional reviewer link is included, it is additive, relative-path, network-free, and
   the reviewer remains a single self-contained offline file with its value-parity test
   passing.
9. `assets/prototypes/crosswise-prototype.zip` is untouched.
10. `git status --short` shows only intended additions (and, at most, the optional
    `run_full_pipeline.py` / reviewer additive edits); no branch, remote, or commit operations
    were performed.

---

# Risks

| Risk | Mitigation |
|---|---|
| Documents imply an ingestion/OCR capability. | Mandatory visible caption (synthetic, not parsed/ingested, no OCR); asserted by a test. |
| Scope creep toward parsing/OCR ("the documents are right there"). | Render-only module; no parser, no read path; document module forbidden from importing reconciliation/evaluation/routing logic. |
| A network dependency sneaks in (web font, CDN, script). | Inline CSS only, no `<script>`, system fonts; test scans output for any external reference and fails on one. |
| Decorative polish hiding weak substance. | Every value bound from fixtures; value-parity test; documents carry no fabricated flags or numbers. |
| Effort balloons across many bundles/documents. | Exactly one bundle, exactly three files; more is out of scope. |
| Regression to the known-good reviewer via the optional link. | Link is optional, additive, relative-path; dropped if it risks the reviewer or adds a network request; reviewer value-parity test must still pass. |
| Money/quantity formatting drifts from fixtures. | Render the fixture string values as-is; determinism test guards byte-identical output. |
| Pipeline regression from the optional `run_full_pipeline.py` edit. | Optional and droppable; only a single appended step, no reordering; existing pipeline/reproduction tests must still pass. |

---

# Out-of-Scope

- OCR, parsing, ingestion, or any path that reads a document back into the system.
- PDF or any binary/print rendering; HTML+PDF; reviewer-only rendering as the deliverable.
- APIs, model calls, deployment, authentication, databases, network requests of any kind.
- Streamlit, React, Next.js, Flask, FastAPI, web servers, npm, `package.json`, external JS,
  external CSS, external fonts, CDNs.
- New reconciliation/evaluation/confidence/routing logic; any change to existing data,
  metrics, routes, or evidence.
- Rendering more than the one approved bundle, or more than three documents.
- README changes, prototype ZIP changes, and any reopening of the architecture decision.
- Real documents, real company/supplier data, PII, payment, tax, or bank data.

---

# Recommended Commit Boundary

Per `AGENTS.md`, the implementing agent stops after implementation, validation, evidence, and
`git status --short`; it does **not** run `git add`/`commit`/`push`/`tag` or touch branches or
remotes. When the repository owner commits, the recommended single, self-contained commit
includes:

- `src/crosswise/documents/__init__.py`, `src/crosswise/documents/synthetic_documents.py`
- `scripts/generate_documents.py`
- `tests/test_documents.py`
- generated `docs/evidence/documents/invoice.html`, `purchase_order.html`, `receipt.html`
- generated `docs/evidence/CROSSWISE_DOCUMENT_PACK_SHOWCASE.png`
- (optional) the additive `scripts/run_full_pipeline.py` and reviewer-link edits, only if
  adopted

Suggested message theme: *"Add Phase 2B HTML synthetic document pack (illustrative,
self-contained)"*. README updates, if any, belong to a separate follow-up commit and are out
of scope here.

---

*Document version 1.0. Implementation plan only — no code, no data, no tests, no screenshots,
no existing-file changes; only this file created. The approved architecture
(HTML-only synthetic documents) is fixed and not reopened.*
