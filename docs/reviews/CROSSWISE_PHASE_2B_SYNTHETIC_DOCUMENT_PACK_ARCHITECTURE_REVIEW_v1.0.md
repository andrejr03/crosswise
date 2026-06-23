# Crosswise — Phase 2B Synthetic Document Pack Architecture Review (v1.0)

> Strategic review to choose the architecture for **Synthetic Document Pack Generation**,
> the next demonstration-layer objective after the reviewer and interactive case explorer
> (Foundation, Slices 0–10B) reached strength. The engine, evaluation, evidence, reviewer,
> and interactivity are done. This phase asks one question: *how should Crosswise introduce
> synthetic business documents in a way that increases memorability and recruiter impact
> without damaging scope discipline?* Evaluated through the `werkstudent-recruiter` lens
> (first-glance legibility, memorability, finishability, honest evidence, scope judgment),
> as a startup founder, technical hiring manager, AI/data-science lead, and Werkstudent
> recruiter would read it. This document implements nothing, plans nothing, and modifies no
> existing file — it creates only this file. The Crosswise name, direction, and scope
> boundaries are treated as fixed and are not reopened.

---

# Decision

**PROCEED WITH HTML-ONLY SYNTHETIC DOCUMENTS**

Generate a small, fixed pack of standalone, self-contained synthetic business documents —
`invoice.html`, `purchase_order.html`, `receipt.html` — rendered from the *existing*
synthetic fixture data, with no parsing, no ingestion, no OCR, no dependency, and no network
request. They are honestly framed as **illustrative source-record renders**, not as inputs
the pipeline reads back. This is the smallest change that introduces a genuinely new visual
signal (the *document form factor* — the input side of the story Crosswise has never shown)
at near-zero cost and zero scope risk, while PDF and HTML+PDF add a dependency and the
strongest pull toward OCR, and reviewer-integrated rendering fails to actually introduce a
document at all.

---

# Executive Summary

Crosswise has closed every hard gap the prior two reviews named. The Demonstration Layer
Review moved it from "solid but invisible engine" to a chosen interactivity direction; the
Final Portfolio Audit graded it 8.4/10 and "Ready to show." The interactive reviewer
(Slices 9–10B) now lets a reviewer click any case and watch the flagged field, evidence,
confidence, and route update inline, in one self-contained offline HTML file.

What the project still does **not** show — anywhere — is what a *document* looks like.
Crosswise operates on structured synthetic records and renders them as comparison panels.
The narrative therefore starts mid-stream: a recruiter sees "structured records → flagged
field → route" but never sees the thing the product's own thesis names first
("transform invoices, purchase orders, and receipts into structured records"). The **input
side is invisible.** That is the one remaining memorability lever a bounded document pack
can pull: a tangible "this is a Crosswise synthetic invoice" artifact that completes the arc
*document → structured comparison → route* and gives a recruiter a concrete visual hook.

The decisive constraint is honesty. Because Crosswise has no OCR and no ingestion — and must
not acquire them — any document artifact must be unambiguously framed as an *illustrative
render of the synthetic source record*, never as something the system reads back. With that
single guardrail, **HTML-only** is the clear winner: pure templating over data the project
already generates, zero new dependency, inline-previewable in a README, openable by
double-click, and fully consistent with the established "single self-contained HTML file,
no network request" doctrine. PDF (B) reintroduces a rendering dependency and the exact
OCR/ingestion pull this project has twice rejected; HTML+PDF (C) pays both costs for one
signal; reviewer-integrated (D) keeps rendering panels and so does not introduce a document
at all. HTML-only adds the new signal and nothing else.

---

# Current Demonstration Layer Assessment

What Crosswise already demonstrates well (and Phase 2B must not regress):

- **A complete, honest pipeline** — generation → validation → reconciliation → evaluation →
  reliability routing → evidence report → static reviewer → interactive reviewer — runnable
  from a fresh clone with one command, with checked-in per-label precision/recall/F1 and
  macro-F1 against generated ground truth.
- **A real trust layer** — deterministic confidence scoring and conservative three-way
  routing (`auto_accept` / `needs_review` / `blocked`), confidence held separate from
  severity.
- **A memorable, distinctive visual** — the dark editorial showcase catching a unit-price
  mismatch (€15.00 vs €13.00, +€2.00, flagged `review`, confidence 0.700 below threshold,
  "Route to human review"), now navigable across all ten cases in the interactive reviewer.
- **Exceptional scope discipline** — synthetic-only, no PII, no OCR, no APIs, no model calls,
  no autonomous actions — stated consistently across `AGENTS.md`, `README.md`, and the
  evidence report. This reads as judgment, and it is the project's single strongest
  credibility asset.

The open gap relevant to this phase:

- **The document form factor is absent.** Every artifact downstream of generation is shown
  (panels, evidence, metrics, routes), but the *document* — the artifact the thesis leads
  with — is never depicted. A reviewer must infer what "an invoice / PO / receipt" means to
  Crosswise. This is the only place a bounded document pack adds a signal that does not
  already exist.

Standing caution carried from prior reviews: the chief credibility risks are (a) the wall of
deterministic `1.0` metrics reading as "trivially easy," and (b) any polish that *implies a
capability the system does not have*. A document pack does nothing for (a) and actively
courts (b) unless honestly framed. That tension governs the recommendation below.

---

# Candidate Evaluation

### A. HTML-Only Synthetic Documents

Generate `invoice.html`, `purchase_order.html`, `receipt.html` from existing fixtures. No
parsing, no ingestion, no OCR.

- **Recruiter impact:** Medium-high. Adds the one visual the project lacks — the input-side
  document — and a concrete "Crosswise turns documents like *this* into structured records"
  hook a recruiter can repeat in shortlisting. Inline-previewable straight from the README.
- **Founder impact:** Medium-high. Lets a non-technical founder *see* where the workflow
  starts, completing the arc *document → comparison → route* in one read.
- **Technical credibility:** Medium-high **if honestly framed**; mixed if not. Pure
  deterministic templating over already-validated data is honest engineering; the only risk
  is the "so does it read these back?" question, neutralized by explicit illustrative
  labeling.
- **Implementation cost:** Low. String/template rendering in the existing Python toolchain;
  no new dependency; reuses the reviewer's CSS family.
- **Implementation risk:** Low. No dependency, no binary artifacts, no server, no network.
  The residual risk (implying ingestion) is mitigated by labeling, not by code.
- **Memorability:** Medium-high — a new, distinct form factor rather than a repackaged panel.
- **Scope-discipline impact:** Strongly positive when bounded to three fixed files with
  honest framing; it demonstrates restraint (documents that illustrate, deliberately *not*
  ingested) — the same judgment signal the rest of the project trades on.
- **Recommendation:** **Proceed.** Best new-signal-per-unit-cost-and-risk of all options.

### B. PDF-Only Synthetic Documents

Generate `invoice.pdf`, `purchase_order.pdf`, `receipt.pdf` from existing fixtures. No
parsing, no ingestion, no OCR.

- **Recruiter impact:** Low-medium, surface only. "It emits PDFs" sounds tidy but adds
  little over an HTML render and is harder to preview inline on a repo page.
- **Founder impact:** Low. PDFs without ingestion are files a reviewer must open separately;
  they do nothing in-pipeline.
- **Technical credibility:** Mixed-to-negative. The classic recruiter anti-pattern — polish
  implying a capability (document understanding) that is explicitly out of scope. A PDF on
  disk is the strongest possible invitation to "now parse it."
- **Implementation cost:** Medium-high. New PDF rendering dependency, layout work, and
  binary artifacts to manage, diff, and test.
- **Implementation risk:** High. Adds an external dependency and the single strongest pull
  toward OCR/ingestion — the exact boundary `AGENTS.md` forbids crossing without explicit
  authorization.
- **Memorability:** Medium, but for the wrong reason (decorative print polish).
- **Scope-discipline impact:** Negative. Already rejected in the prior Demonstration Layer
  Review; the reasoning (dependency + OCR pull, decorative without ingestion) still holds.
- **Recommendation:** **Reject.**

### C. HTML + PDF Synthetic Documents

Generate both formats.

- **Recruiter impact:** Medium, with sharply diminishing returns — one signal delivered
  twice.
- **Founder impact:** Low-medium; redundant artifacts, no added story.
- **Technical credibility:** Mixed. Inherits every PDF concern (dependency, OCR pull) while
  adding maintenance of two parallel renderers that must stay consistent.
- **Implementation cost:** High — the union of A and B plus cross-format consistency tests.
- **Implementation risk:** High — inherits B's dependency and OCR pull, doubles surface area.
- **Memorability:** Medium; no more memorable than A alone for materially more cost.
- **Scope-discipline impact:** Negative. Pays both costs for the signal A delivers cleanly.
- **Recommendation:** **Reject.**

### D. Reviewer-Integrated Documents

No standalone documents; render document artifacts only inside the reviewer experience.

- **Recruiter impact:** Low-marginal. The reviewer **already** renders document-like panels
  (Slices 9–10B). "Render documents inside the reviewer" largely re-describes what shipped,
  so it adds little new signal.
- **Founder impact:** Neutral — the reviewer story is already complete; this mostly restyles
  it.
- **Technical credibility:** Neutral-positive (safe, in-scope) but produces no new artifact a
  reviewer can point to as "the document."
- **Implementation cost:** Low-medium — but spent on reworking an artifact already deemed
  strong, with regression risk to a known-good reviewer.
- **Implementation risk:** Low technically; non-trivial *opportunity* risk — effort that does
  not move the named objective.
- **Memorability:** Low — no distinct form factor emerges; it remains a comparison view.
- **Scope-discipline impact:** Neutral, but it does not satisfy the phase mandate ("introduce
  synthetic business documents"). It keeps rendering panels rather than introducing a
  document.
- **Recommendation:** **Reject as the architecture**, while adopting its safest instinct —
  keep everything self-contained and offline — inside Option A.

### E. Another Bounded Alternative — STOP / No Document Phase

The strongest genuine alternative is *not building a document pack at all* and banking the
8.4/10 "Ready to show" state.

- **Recruiter impact:** Neutral. Nothing gained, nothing risked.
- **Technical credibility / scope discipline:** Positive — saying "no" to a decorative
  feature is itself a judgment signal.
- **Memorability:** No change.
- **Recommendation:** **Respected but not adopted.** It is the correct default *only if* a
  document pack cannot be delivered honestly and cheaply. Option A can — at zero dependency
  and with the input-side gap as a real, specific payoff — so the disciplined "no" is not the
  strongest available move here. No other bounded alternative beats A on
  signal-per-cost-and-risk within the constraints.

---

# Recommended Architecture

**Phase 2B — HTML-Only Synthetic Document Pack (Standalone, Self-Contained, Illustrative).**

- Render exactly three standalone documents — `invoice.html`, `purchase_order.html`,
  `receipt.html` — for one representative synthetic bundle, generated deterministically from
  the **existing** `data/synthetic/fixtures_v1_0.json` records. No new reconciliation,
  evaluation, confidence, or routing logic; this is a presentation layer over data that
  already exists and is already tested.
- Each file is a **single self-contained HTML document**: inline CSS in the reviewer's
  established aesthetic, no external script, font, CDN, or network request; openable by
  double-click and inline-previewable on a repository page.
- Each document carries a **visible, honest caption** stating it is a synthetic,
  illustrative render of a generated source record — not a real document and not an input the
  system parses, ingests, or reads back (no OCR).
- Values shown are drawn directly from the same fixtures the pipeline and tests consume; no
  hand-authored or divergent numbers.
- Generation follows the existing convention: a script under `scripts/` writes the artifacts
  to a documented location under `docs/evidence/` (final path to be fixed in the Phase 2B
  plan, not here), consistent with the Documentation Policy in `AGENTS.md`.

Optional, non-required stretch (only if it adds zero dependency and no network request): a
plain in-page hyperlink from the existing reviewer to each source document — adopting Option
D's "keep it integrated and offline" instinct without reworking the reviewer. This is folded
into acceptance as optional, never as a gate.

---

# Why This Architecture Wins

- **It introduces an actual document.** Of the five options, only A produces the new artifact
  the phase is named for — the input-side form factor the project has never shown — rather
  than restyling an existing panel (D) or doing nothing (E).
- **It adds a new signal instead of repackaging one.** It completes the visual arc
  *document → structured comparison → evidence → route*, giving a recruiter a concrete hook
  that the current artifacts cannot.
- **It is the cheapest honest path.** Pure deterministic templating over already-validated
  data: no dependency, no binary, no server, no build, no network — preserving the
  self-contained-file guarantee that is already a project hallmark.
- **It strengthens rather than risks credibility — when framed honestly.** A document that is
  *explicitly* illustrative and *deliberately not ingested* showcases the same scope judgment
  the rest of Crosswise trades on. The restraint is the signal.
- **It dominates the rejected formats.** PDF (B) and HTML+PDF (C) add a dependency and the
  strongest OCR pull for a signal A delivers more cheaply and more previewably; D does not
  introduce a document; E forgoes a real, low-cost memorability gain.

---

# Risks

| Risk | Mitigation |
|---|---|
| Documents imply an ingestion/OCR capability the system does not have ("does it read these back?"). | Mandatory visible caption on every document: synthetic, illustrative render of a generated source record — not ingested, not parsed, no OCR. Acceptance gates on this text being present. |
| Scope creep toward parsing/OCR because "the documents are right there." | Hard boundary below: render-only, no read path of any kind; no parser, no ingestion entry point; `AGENTS.md` scope rules unchanged. |
| New dependency sneaks in (PDF/print/templating engine, CDN font, web script). | HTML-only, inline CSS, zero external `src`/`href` network fetches; assert no network request in the generated files; no new runtime dependency. |
| Decorative polish hides weak substance (recruiter anti-pattern). | Values are drawn strictly from the same fixtures the tests consume; a test asserts displayed values equal source values; honest-limitations posture retained. |
| Effort balloons into a templating framework or many documents. | Exactly three files for one representative bundle; reuse the reviewer's existing CSS; no per-field layout invention. |
| Regression to the known-good reviewer via the optional link. | The reviewer link is optional and additive only; if it cannot be added without risk or a network request, it is dropped — never a gate. |
| Document pack distracts from the real credibility gap (the "1.0 looks trivial" perception). | Phase 2B is explicitly framed as an *input-visibility* improvement, not a metrics improvement; it must not overstate what it proves. |

---

# Scope Boundaries

Explicitly out of scope for Phase 2B (no exceptions without a future approved planning
document):

- OCR, document ingestion, parsing, or any path that *reads a document back* into the system.
- PDF generation or any binary/print document rendering (Option B/C are rejected).
- APIs, model calls, paid services, or any network request — every document must be a single
  self-contained local HTML file that opens offline by double-click.
- Web servers and frameworks of any kind: Streamlit, React, Next.js, Flask, FastAPI, Node,
  any build system, bundler, `npm`/`package.json`, or external frontend dependency, font,
  CDN, or script.
- Deployment, authentication, databases, persistence.
- New reconciliation, evaluation, confidence, or routing **logic** — presentation only, over
  the same outputs the tests and report already use.
- Real documents, real company data, real supplier data, PII, payment information, tax
  identifiers, or bank details — synthetic-only, unchanged.
- Autonomous accounting / payment / legal / tax workflows, and any change to the non-advice
  or synthetic-only posture.
- Any modification to `assets/prototypes/crosswise-prototype.zip`.
- Any rework of the existing reviewer beyond an optional, additive, offline hyperlink.

The only new technology permitted is **standalone self-contained HTML with inline CSS**,
rendered deterministically from existing fixtures.

---

# Acceptance Criteria For Phase 2B

Phase 2B is accepted when:

- A `scripts/` generator deterministically produces exactly three self-contained documents —
  `invoice.html`, `purchase_order.html`, `receipt.html` — for one representative synthetic
  bundle, from the existing fixtures, with **no external network dependency** and **no new
  runtime dependency**.
- Each document opens correctly by double-click and renders legibly offline; it contains no
  external `src`/`href` network fetch (asserted by a test).
- Each document carries a **visible caption** stating it is a synthetic, illustrative render
  of a generated source record — not a real document and not parsed/ingested/OCR'd — and a
  test asserts that text (or its synthetic-only / non-advice equivalent) is present.
- Displayed values **exactly match** the underlying fixture values for that bundle (no
  hand-authored or divergent numbers); a test asserts displayed values equal source values.
- The three documents are consistent with one another (the invoice, PO, and receipt depict
  the same synthetic bundle).
- The existing pipeline, reviewer, evidence report, and full `pytest` suite continue to pass
  unchanged; no reconciliation/evaluation/confidence/routing logic was modified.
- If the optional reviewer hyperlink is included, it is additive only, adds no dependency and
  no network request, and the reviewer remains a single self-contained offline file.
- `assets/prototypes/crosswise-prototype.zip` is untouched.
- `git status --short` shows only intended additions; no branch, remote, or commit operations
  were performed.

---

# Final Recommendation

**Proceed with HTML-Only Synthetic Documents.** It is the smallest, cheapest, most honest way
to introduce the one artifact Crosswise has never shown — the document itself, the input side
of its own thesis — completing the *document → structured comparison → evidence → route* arc
that today starts mid-stream. Three self-contained, dependency-free, offline HTML renders of
existing synthetic fixtures, each explicitly labeled as illustrative and deliberately
not-ingested, add a genuinely new memorability signal while *reinforcing* the scope judgment
that is already Crosswise's strongest credibility asset. PDF and HTML+PDF are rejected for
adding a dependency and the strongest pull toward OCR; reviewer-integrated rendering is
rejected for not introducing a document at all; and doing nothing is respected but not adopted
because the honest, low-cost win is real and available. Keep the pack to three files, frame
them honestly, and do not let a document on disk become a reason to build a parser.

---

*Document version 1.0. Strategic architecture review only — no implementation, no plan, no
code, no README or documentation changes; only this file created. The Crosswise name,
direction, and scope boundaries are treated as fixed and are not reopened.*
