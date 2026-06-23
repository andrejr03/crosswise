# Crosswise — Slice 10B Interactive Reviewer UX Plan (v1.0)

> UX architecture plan written **before** any further Slice 10 implementation. The current
> interactive reviewer is technically correct (data wired from real outputs, single
> self-contained file, no network request) but its interaction model reads more like an
> internal engineering tool than a premium portfolio showcase. This document defines the
> optimal UX architecture only. It implements nothing, writes no code, and creates no
> screenshots. Evaluated through the `werkstudent-recruiter` and founder lenses, against the
> editorial visual language already established by `assets/prototypes/crosswise-showcase.png`
> and `CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`. All Slice 10 scope boundaries from the
> Demonstration Layer Architecture Review remain fixed: vanilla inline JS/CSS, one file,
> offline, no framework, no new reconciliation logic.

---

# Decision

**Adopt the "Hero Case + Quiet Index" model.**

Lead with **one** premium, editorial discrepancy frame above the fold — the same single
side-by-side comparison table, confidence meter, and routing action that already make the
showcase memorable — rendered for a strong **default hero case**. Demote case selection from
three competing navigation controls to **one** primary control plus a small set of curated,
**named** cases. Move the full ten-case enumeration, the raw three-document panels, and the
four-column evidence strip **below the fold** as progressive, opt-in depth.

The current explorer asks the reviewer to *operate a tool*. The target asks them to *read a
story, then explore if curious*. The engine, data wiring, and self-contained-file guarantee
do not change — only what is shown first, what is hidden, and how one navigates.

---

# UX Diagnosis

What is wrong with the current explorer (per `CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png`):

- **Three redundant navigation mechanisms at once.** `← PREV / NEXT →`, a `JUMP TO CASE`
  dropdown, *and* a full row of ten numbered chips all do the same job. This is the single
  clearest "internal tool" tell — it optimizes for an operator paging through records, not a
  visitor being told a story. One job should have one obvious control.
- **All ten cases exposed as raw numbered chips.** `01 clean match … 10 unit price mismatch`
  is an enumeration of a test fixture, not a curated showcase. It signals "test harness" and
  forces a cold visitor to triage ten equally-weighted options with no guidance on where to
  start.
- **Default lands on case 10, an arbitrary index.** The explorer opens on "10 of 10" rather
  than on the canonical, most legible discrepancy. First impression is decided by array order,
  not by editorial intent.
- **Primary view is three raw document panels, not the elegant comparison.** The premium
  artifact is the single Field / Invoice / PO / Δ / Status table with the gold-flagged row.
  The interactive view leads instead with three dense PO/Invoice/Receipt cards plus an inline
  mini-table per panel — more data, less story, more cognitive load. The thing that made the
  showcase memorable is absent from the top of the interactive experience.
- **A four-column "WHAT HAPPENED / WHY FLAGGED / EVIDENCE / ROUTE" strip reads as a debug
  readout.** `purchase_order_invoice_unit_price_difference`, `invoice_unit_price=15.00` exposes
  internal label and evidence keys at the same visual weight as everything else. It is honest
  and valuable — but it is *engineering depth*, and it currently sits at story level.
- **No visual hierarchy of trust.** Every case looks equally important; the explorer never
  uses the one structural advantage Crosswise has — that its cases tell a three-beat trust
  story (does not over-flag → catches the discrepancy → blocks bad data).
- **Aesthetic drift from the showcase.** The discrepancy showcase has generous whitespace, a
  serif headline, and one focal object. The interactive view is denser, more grid-like, more
  dashboard — closer to an admin panel than to the prototype's editorial calm.

Net: the explorer is correct and complete but **leads with breadth (10 cases, 3 panels, 4
evidence columns) instead of depth-on-demand**, and it leads with *controls* instead of *the
story*. That is exactly the tool-like / dashboard-like / engineering-oriented failure the
phase is trying to avoid.

---

# Design Principles

1. **Story first, exploration second, depth third.** A visitor should understand the product
   before they are offered a single control. Exploration is a reward for curiosity, not a
   prerequisite for comprehension.
2. **One job, one control.** Eliminate redundant navigation. A reviewer should never wonder
   which of three widgets to use.
3. **Curate, don't enumerate.** Name cases editorially; surface a few signature ones; keep the
   full ten available but quiet. A showcase chooses; a test harness lists.
4. **Preserve the premium frame.** The default view *is* the showcase: single comparison table,
   confidence meter, routing action. Interactivity changes the *contents* of that frame, not
   its character.
5. **Progressive disclosure of engineering depth.** Raw documents, evidence keys, and the full
   taxonomy are real assets — reveal them on demand, below the fold, for the reviewer who
   leans in. Never at the same weight as the headline.
6. **Calm over dense.** Whitespace, one focal object per viewport, editorial typography. Match
   the prototype's restraint, not an admin dashboard's information density.
7. **Honesty stays visible.** Including a clean match, synthetic-only notices, and the
   "deterministic-by-design" framing is non-negotiable; calm presentation must not hide them.
8. **No regression of substance or scope.** Same data source, same self-contained file, same
   offline guarantee, same no-JS fallback. This is a presentation re-architecture only.

---

# Recommended Interaction Model

**A guided hero with a curated rail and a quiet full index.**

- The page opens on a **hero discrepancy case** rendered in the showcase comparison-table
  frame. No action is required to understand the product.
- Directly beneath the hero sits a **single primary selector**: a small horizontal rail of
  **three named "signature" cases** that tell the trust story end to end —
  *Clean match* (does not over-flag), *Unit price mismatch* (catches the discrepancy),
  *Schema validation failure* (blocks bad data). Selecting one re-renders the hero frame in
  place. This is the only navigation a casual visitor sees.
- A quiet, secondary **"Browse all 10 cases"** affordance (collapsed by default) expands the
  complete, editorially-labeled set below the fold for the reviewer who wants exhaustiveness.
  This is where the full enumeration lives — demoted, not deleted.
- Per-case **engineering depth** (raw invoice/PO/receipt panels, evidence reference keys, exact
  detected-label string) lives in a below-the-fold **"Inspect the documents / evidence"**
  region tied to the currently selected case — opt-in, not default.

This replaces *chips + dropdown + prev/next + three panels + four-column strip shown at once*
with *one hero + one rail of three + one quiet expander + on-demand depth*.

**Answers to the explicit review questions:**

1. **Cards, chips, tabs, or other?** A **curated rail of three named cards/segments** as the
   primary control (story-shaped), with the full set as a **quiet labeled list** behind an
   expander. Not ten raw numbered chips; not a dropdown as the hero control; not prev/next.
2. **Above the fold:** the hero discrepancy frame (comparison table + confidence + route) and
   the three-case signature rail. Nothing else.
3. **Below the fold:** raw document panels, evidence/label internals, the full ten-case index,
   metrics summary, scope/non-advice notices, command/reproduction section.
4. **Ideal default case:** the **Unit price mismatch** (`bundle_unit_price_mismatch_003`) — the
   canonical, already-validated story (€15.00 vs €13.00, +€2.00, confidence 0.700, needs_review).
5. **Visible selectable cases at once:** **three** (the signature rail), plus the hero already on
   screen.
6. **All ten visible immediately?** **No.** Ten at once is the core tool-like tell. Three curated
   up top; ten available but quiet below.
7. **Balance of storytelling / exploration / technical depth:** storytelling owns above the fold,
   exploration owns the rail and expander, technical depth owns the below-the-fold inspect region.
8. **Founder after 30s:** "It catches a price mismatch and sends the doubtful one to a person."
9. **Recruiter after 30s:** "Clean, designed reviewer; line-item reconciliation with evidence and
   conservative human routing — and it doesn't over-flag."
10. **UX best supporting "Crosswise detected a discrepancy and explains why":** the hero frame —
    flagged row (what) + Δ column (how much) + confidence/route (what next) + an opt-in evidence
    line (why), in that disclosure order.

---

# Above-the-Fold Structure

Section-by-section wireframe (single column, generous whitespace, prototype typography):

```
┌────────────────────────────────────────────────────────────────────┐
│ ◇ Crosswise            AI DOCUMENT RECONCILIATION   ● DEV BUILD      │  A. Masthead
│                                                     synthetic cases  │
├────────────────────────────────────────────────────────────────────┤
│  Crosswise detected a discrepancy — and shows you why.   (serif H1)  │  B. Editorial lede
│  One line: pick a case to see the flagged field, evidence, route.    │     (1 sentence sub)
├────────────────────────────────────────────────────────────────────┤
│  INVOICE SYN-INV-0003        ⇄ MATCHING            PO 003            │  C. Hero discrepancy
│  ┌──────────────────────────────────────────────────────────────┐  │     frame = the
│  │ FIELD       INVOICE      PO        Δ        STATUS            │  │     SHOWCASE table
│  │ Vendor      Supplier 003 Supplier 003  —    ✓ match          │  │     (default = unit
│  │ Quantity    5            5             —    ✓ match          │  │      price mismatch)
│  │ Unit price  €15.00       €13.00     +€2.00  ⚑ review  ◄ gold │  │
│  │ Line total  €75.00       €65.00    +€10.00  ⚑ review  ◄ gold │  │
│  │ Tax         €0.00        €0.00         —    ✓ match          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌── MODEL CONFIDENCE ─────┐  ┌── ACTION ─────────────────────┐    │  D. Confidence + route
│  │ 0.700  below threshold  │  │ → Route to human review       │    │     (two cards, as in
│  │ ▰▰▰▰▰▰▱▱▱▱               │  │ 1 discrepancy · evidence linked│    │     the showcase)
│  └─────────────────────────┘  └───────────────────────────────┘    │
├────────────────────────────────────────────────────────────────────┤
│  EXPLORE THE TRUST STORY                                            │  E. Signature rail
│  [ ✓ Clean match ] [ ⚑ Unit price mismatch ] [ ⛔ Schema failure ]  │     (THE primary
│        does not       catches the              blocks bad           │      control: 3 named
│       over-flag       discrepancy              data                 │      cases, selected
│                       ▲ selected                                    │      one is hero)
└────────────────────────────────────────────────────────────────────┘
                          ▼ quiet scroll cue / "Browse all 10 cases ▾"
```

- **A. Masthead** — unchanged identity lockup; keeps the `DEV BUILD / synthetic test cases`
  honesty marker.
- **B. Editorial lede** — one serif headline naming the exact promise ("detected a discrepancy —
  and shows you why") and one quiet sub-line. Replaces the current "Browse Every Reconciliation
  Case / Interactive Case Explorer" framing, which advertises the mechanism over the value.
- **C. Hero discrepancy frame** — the single comparison table, gold-flagged disagreeing rows, Δ
  column. This is the prototype's focal object, now driven by the selected case.
- **D. Confidence + Action cards** — verbatim showcase pattern; the trust layer made concrete.
- **E. Signature rail** — three named cases with a one-word purpose each. The *only* control a
  casual visitor needs. Selecting re-renders C and D in place.

Everything above is comprehensible with **zero interaction** and on a single laptop viewport.

---

# Below-the-Fold Structure

Section-by-section wireframe (revealed by scroll / opt-in expanders):

```
┌────────────────────────────────────────────────────────────────────┐
│  INSPECT THE DOCUMENTS            (for the currently selected case)  │  F. Raw documents
│  ┌ PURCHASE ORDER ┐ ┌ INVOICE ┐ ┌ RECEIPT ┐                        │     (the 3-panel
│  │ po_003 …        │ │ inv_…   │ │ rcpt_…  │  highlighted line item │     view, demoted to
│  └─────────────────┘ └─────────┘ └─────────┘                        │     opt-in depth)
├────────────────────────────────────────────────────────────────────┤
│  WHY IT FLAGGED            (collapsed by default, per case)          │  G. Evidence detail
│  Detected label · plain-English reason · evidence reference ·       │     (the 4-col strip,
│  route reason. Internal keys shown small, secondary.                │     reframed + quieted)
├────────────────────────────────────────────────────────────────────┤
│  BROWSE ALL 10 CASES  ▾    (collapsed expander)                     │  H. Full index
│  01 Clean match  02 Duplicate invoice  03 Late receipt  …  10 …     │     (full enumeration
│  editorially labeled list; selecting drives the hero above          │     lives here, quiet)
├────────────────────────────────────────────────────────────────────┤
│  WHAT THE NUMBERS SAY                                               │  I. Metrics + honesty
│  10 cases · P/R/F1 = 1.0 (deterministic by design) ·               │     (deterministic-by-
│  1 auto_accept · 8 needs_review · 1 blocked                        │     design framing)
├────────────────────────────────────────────────────────────────────┤
│  ◇ Line-item matching   ▢ Field-level evidence   ○ Human routing   │  J. Three pillars
│  (the showcase's repeatable one-liners)                            │     (kept verbatim)
├────────────────────────────────────────────────────────────────────┤
│  Synthetic data only · no OCR · no model calls · not advice ·      │  K. Scope + reproduce
│  reproduce: python3 scripts/generate_reviewer.py                    │     (no-JS fallback safe)
└────────────────────────────────────────────────────────────────────┘
```

- **F. Inspect the documents** — the current three-panel PO/Invoice/Receipt view, now a
  *secondary* detail for the selected case rather than the primary surface.
- **G. Why it flagged** — the four-column evidence strip, reframed as a single calm "Why" block
  with internal keys (`…_unit_price_difference`, `invoice_unit_price=15.00`) shown at reduced
  weight. Honest depth, no longer at story altitude.
- **H. Browse all 10 cases** — collapsed expander holding the full editorially-labeled set; this
  is the only place the complete enumeration appears.
- **I. Metrics + honesty** — the deterministic-by-design framing the Final Audit asked for, so
  `1.0` reads as expected, not trivial.
- **J. Three pillars** and **K. Scope/reproduce** — kept verbatim from the showcase; these are
  the repeatable one-liners and the credibility/scope guarantees, and they double as the no-JS
  fallback content.

---

# Navigation Model

- **One primary control:** the three-case **signature rail** above the fold. Click → hero (C/D)
  and depth (F/G) re-render for that case. This is the default, casual-visitor path.
- **One secondary control:** the **"Browse all 10 cases"** expander below the fold for
  exhaustiveness. Selecting any case there also drives the hero and scrolls focus back to it.
- **Removed:** `← PREV / NEXT →` and the standalone `JUMP TO CASE` dropdown as top-level
  controls. Paging is an operator pattern, not a showcase pattern. (Optional: keep lightweight
  prev/next *inside* the expanded full-index for power browsing, never above the fold.)
- **State model:** a single "selected case" id drives every region (hero table, confidence,
  action, documents, evidence). One source of truth; selecting anywhere updates everywhere.
- **No-JS fallback:** with scripting off, the page renders the default hero case statically plus
  all below-the-fold content (metrics, pillars, scope, full case list as plain text). Content is
  never gated by JS — interaction only *enhances* selection.
- **Keyboard/focus:** rail and expander items are real focusable controls with visible selected
  state; selection is reachable without a pointer.

---

# Case Selection Strategy

- **Curate three signature cases** as the visible, story-shaped choices:
  - **Clean match** → proves the system does **not over-flag** (the recruiter anti-pattern guard).
  - **Unit price mismatch** → the canonical **caught discrepancy** (default hero).
  - **Schema validation failure** → the conservative **blocked / bad-data-stopped** beat.
  These three span the full route taxonomy (`auto_accept` / `needs_review` / `blocked`) and
  read as a deliberate trust narrative rather than a fixture dump.
- **Keep all ten** available and labeled editorially in the quiet expander — completeness is a
  credibility asset, but it belongs below the fold.
- **Name, don't number, in visible surfaces.** "Unit price mismatch", not "10". Numbers may
  remain as small secondary identifiers inside the full index.
- **Visible-at-once count: three** (rail) + the hero on screen. Never ten at once above the fold.

---

# Default Case Recommendation

**Default to `bundle_unit_price_mismatch_003` — "Unit price mismatch".**

Rationale:

- It is the **already-validated canonical story** used by both `CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`
  and the prototype, so the interactive default matches the README hero a reviewer just saw —
  continuity, not a context switch.
- It exercises **every part of the frame at once**: two flagged rows with a clear Δ, matched
  rows for contrast, a sub-threshold confidence (0.700), and a `needs_review` route — the
  complete "detected → explains why → routes to a person" arc in one viewport.
- It is **quantitative and obvious** (€15.00 vs €13.00, +€2.00), which a non-technical founder
  grasps in seconds.

A clean match is the wrong default (nothing flagged ⇒ weak first impression); a blocked/schema
case is the wrong default (leads with a failure, not the core reconciliation value).

---

# Storytelling Strategy

- **Three-beat trust arc**, made the spine of the experience: *does not over-flag* (clean) →
  *catches what matters* (mismatch) → *stops bad data and escalates to a human* (blocked). The
  signature rail **is** this arc, left to right.
- **Lead with the promise, not the mechanism.** Headline names the value ("detected a
  discrepancy — and shows you why"); the word "explorer/browse every case" is demoted to the
  quiet expander.
- **Disclosure order mirrors how a human reasons:** *what* (flagged row) → *how much* (Δ) →
  *what now* (confidence + route) → *why* (evidence, on demand). Never open with internal keys.
- **One focal object per viewport.** The hero owns the first screen; documents and evidence get
  their own space below. Calm beats dense.
- **Honesty as part of the story, not a disclaimer footnote.** The clean case and the
  deterministic-by-design line are positioned as *features of judgment*, reinforcing rather
  than undercutting the narrative.

---

# Recruiter Impact Analysis

*(werkstudent-recruiter lens: first-glance legibility, memorability, finishability, honesty.)*

- **First glance:** a single designed discrepancy frame, not a wall of ten chips and a dropdown.
  Reads as *product*, not *test harness* — the exact upgrade this phase exists to deliver.
- **Memorability (30s):** "Clean, designed reviewer; line-item reconciliation with evidence and
  conservative human routing — and it deliberately doesn't over-flag." The named three-case arc
  gives a repeatable shortlisting sentence.
- **Anti-pattern guard:** demoting raw evidence keys and the ten-fixture list below the fold
  removes the "internal tool screenshot" tell that makes juniors look unfinished; surfacing a
  clean match pre-empts "does it just flag everything?".
- **Finishability:** progressive disclosure signals someone who knows what to lead with — a
  judgment signal recruiters weight heavily.
- **Risk avoided:** the current explorer's redundant-controls density could read as "engineer
  who didn't design the front door." The hero model removes that read.

---

# Founder Impact Analysis

- **30-second takeaway:** "It catches a price mismatch and routes the uncertain one to a
  person." Delivered with zero clicks by the default hero.
- **Self-serve depth:** a curious founder clicks the three-case rail and *experiences* the trust
  story (over-flag guard → catch → block) without reading docs — the engagement signal the
  architecture review chartered.
- **Non-technical legibility:** quantitative Δ and a plain confidence meter beat raw document
  panels for a business reader; the dense PO/Invoice/Receipt view is available but no longer the
  first thing they must parse.
- **Trust:** seeing a *clean* case and a *blocked* case (not only flags) communicates a system
  with judgment — which is what a founder evaluating reliability actually wants.

---

# Risks

| Risk | Mitigation |
|---|---|
| Curating three cases hides the full set / looks like cherry-picking. | Keep all ten in the quiet "Browse all 10" expander; the curation is presentation order, not data filtering — every case remains selectable. |
| Re-architecture drifts into new logic or new dependencies. | Presentation-only; same embedded JSON, same vanilla inline JS/CSS, one self-contained offline file. No framework, no network, no new reconciliation code. |
| Hiding documents/evidence below the fold reads as "less substance." | Depth is *demoted, not removed*; the inspect/why regions retain full raw documents and evidence keys for the leaning-in reviewer. |
| No-JS users lose the experience. | Default hero + all below-the-fold content render statically without JS; interaction only enhances selection. |
| Calm/whitespace reads as "empty" on large screens. | One focal object per viewport is intentional editorial restraint matching the prototype; metrics, pillars, and scope fill the scroll with substance. |
| Removing prev/next frustrates a power browser. | Optional lightweight prev/next *inside* the expanded full index only — never above the fold. |
| Default-case change desyncs from README hero. | Default stays `unit_price_mismatch_003`, identical to the existing showcase hero — continuity preserved. |
| Scope creep into redesigning the engine or adding cases. | Ten cases, taxonomy, routes, and data are fixed; this plan touches only what is shown, hidden, and how one navigates. |

---

# Acceptance Criteria

A future implementation of this UX is accepted when:

- The page **opens on the unit-price-mismatch hero** in the showcase comparison-table frame,
  comprehensible with **zero interaction** on one laptop viewport.
- **Exactly one primary control** (the three-case signature rail) is visible above the fold;
  `prev/next` and a standalone `jump-to-case` dropdown are **not** above the fold.
- **No more than three** selectable cases are visible above the fold; the **full ten** are
  reachable only via a quiet below-the-fold expander, **editorially named** (not bare numbers).
- The signature rail spans all three routes (`auto_accept`, `needs_review`, `blocked`) and
  includes a **clean match** proving the system does not over-flag.
- Raw three-document panels and evidence/label internals render **below the fold** for the
  selected case, at clearly secondary visual weight.
- Selecting any case (rail or full index) updates the hero table, confidence, action, documents,
  and evidence from a **single selected-case source of truth**, with displayed values still
  **exactly equal to** the underlying reconciliation/reliability outputs.
- The deterministic-by-design metrics framing, three pillars, synthetic-only/non-advice notices,
  and reproduce command are **retained** and serve as the **no-JS fallback**.
- The artifact remains a **single self-contained offline HTML file** with **no network request**,
  vanilla inline JS/CSS only — no framework, server, build, or external font/script.
- Aesthetic parity with `crosswise-showcase.png` / `CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`:
  serif headline, generous whitespace, one focal object per viewport, gold flag on disagreeing
  rows.

---

# Final Recommendation

**Re-architect the interactive reviewer to the Hero Case + Quiet Index model before touching
code again.** The engine, data, scope, and self-contained guarantee are already right; the only
gap is that the explorer currently *leads with controls and breadth* (three nav widgets, ten raw
chips, three document panels, a four-column evidence strip) instead of *leading with the story*.

Lead with one premium discrepancy frame on the unit-price-mismatch default. Offer one curated
rail of three named cases that walk the trust arc — *does not over-flag → catches the
discrepancy → blocks bad data*. Demote the full ten-case enumeration, the raw documents, and the
evidence internals to opt-in, below-the-fold depth. This converts a correct internal tool into a
calm, editorial, recruiter- and founder-memorable showcase **without** changing a single number,
adding a dependency, or breaking the offline single-file guarantee.

Implement nothing from this document yet. This is the UX architecture; a subsequent Slice 10B
implementation plan should execute it under the existing Slice 10 scope boundaries.

---

*Document version 1.0. UX architecture plan only — no code, no implementation, no screenshots;
only this file created. Crosswise name, direction, scope boundaries, dataset, taxonomy, and
self-contained-file constraints are treated as fixed and are not reopened.*
