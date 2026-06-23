# Crosswise — Demonstration Layer Architecture Review (v1.0)

> Strategic review to choose the next phase after the technical MVP foundation
> (Foundation, Slices 0–9B). The engine is done; this phase is about memorability,
> reviewer engagement, and demonstration quality — not new internal infrastructure —
> while preserving all current technical credibility and scope discipline. Evaluated
> through the `werkstudent-recruiter` lens (first-glance legibility, memorability,
> finishability, honest evidence), as a startup founder, technical hiring manager,
> AI/Data-Science lead, and Werkstudent recruiter would read it. This document modifies
> no code, no documentation, and creates only this file. Crosswise name, direction, and
> scope boundaries are treated as fixed and are not reopened.

---

# Decision

**PROCEED WITH INTERACTIVE REVIEW WORKFLOW**

The highest-impact demonstration layer is to make the existing self-contained static
reviewer *navigable*: let a reviewer click a case, see its side-by-side document panels
with the disagreeing field highlighted, and inspect the evidence, confidence, and route
inline — all as vanilla inline JavaScript inside the single self-contained
`crosswise_reviewer_v1_0.html` file, with no server, no build, no framework, and no
network request. This directly serves the stated purpose of the phase ("reviewer
engagement") and converts a passive scan into an active, memorable exploration of the
exact capability Crosswise claims.

---

# Executive Summary

Crosswise has already closed its hardest gap. The prior two reviews moved it from "solid
but invisible engine" (Demonstration Layer Review) to "finished, honest, memorable, and
push-ready" (Final Portfolio Audit, overall 8.4/10, Yes-to-push). The product is now
*visible*: the discrepancy showcase shows a flagged unit-price mismatch, a below-threshold
confidence meter, and a human-review route in a single frame.

The remaining lever is **engagement**, not visibility. The current reviewer is a static
artifact a reviewer reads top-to-bottom. The one thing it cannot yet do is let a curious
founder or recruiter *poke at it* — pick a case, watch the panels and evidence update, and
discover for themselves that the system flags the right field and routes uncertain cases to
a person. Interactivity is exactly what a recruiter remembers tomorrow and exactly what the
phase brief names ("reviewer engagement").

This wins decisively over the document-generation options. Synthetic HTML or PDF document
packs (A, B) are largely redundant now that Slice 9 already renders document-like panels,
they are decorative without ingestion, and PDFs in particular were already rejected in the
prior review for scope-creep toward OCR. A demo pack (D) is mostly repackaging of what
`run_full_pipeline.py` and the README quickstart already deliver. Interactivity is the only
option that adds a genuinely new signal while staying inside every hard constraint — vanilla
inline JS preserves the Slice 7 "single self-contained file, no network request" rule.

---

# Current MVP Assessment

What Crosswise already demonstrates well (and must not be regressed):

- **A complete, honest pipeline:** generation → validation → reconciliation → evaluation →
  reliability routing → evidence report → static reviewer, runnable from a fresh clone with
  one command; 73 collected tests; clean `src/crosswise/` package split by stage.
- **A checked-in evaluation** with per-label precision/recall/F1 and macro-F1 against
  generated ground truth, readable without running anything.
- **A real trust layer:** deterministic confidence scoring and conservative three-way
  routing (`auto_accept` / `needs_review` / `blocked`), with confidence held separate from
  severity.
- **A memorable first impression:** the showcase image now shows the working system catching
  a discrepancy, not just a metrics table.
- **Exceptional scope discipline:** synthetic-only, no PII, no OCR, no APIs, no model calls,
  no autonomous actions — stated consistently across AGENTS.md, README, and the evidence
  report. This reads as judgment.

What is still missing at the demonstration layer:

- The reviewer is **passive**. A reviewer cannot interact with the cases; they read a fixed
  document. The "evidence-backed review workflow" is *shown* for one curated frame but not
  *experienced*. Engagement — the thing that makes a reviewer linger and remember — is the
  open gap, and it is precisely what this phase is chartered to close.

---

# Candidate Evaluation

### A. Synthetic HTML Document Pack Generation

- **Recruiter impact:** Low-medium. "It generates invoice/PO/receipt HTML" sounds nice for a
  sentence but adds little over the document-like panels Slice 9 already renders.
- **Founder impact:** Low. A standalone HTML invoice that does not feed the pipeline is a
  prop, not a demonstration of reconciliation.
- **Technical credibility:** Mixed. Risks reading as decorative; implies a document-ingestion
  capability the system explicitly does not have, inviting "so does it read these back?" → "no."
- **Implementation cost:** Low-medium (templating + new artifacts to manage/test).
- **Implementation risk:** Medium — naturally pulls toward parsing/ingestion/OCR next.
- **Memorability:** Low-medium; overlaps the existing panels.
- **Recommendation:** Reject as the next phase. Largely redundant with Slice 9.

### B. Synthetic PDF Document Pack Generation

- **Recruiter impact:** Low-medium, surface only.
- **Founder impact:** Low. PDFs without OCR are files a reviewer must open separately; they
  do nothing in-pipeline.
- **Technical credibility:** Mixed-to-negative. The classic recruiter anti-pattern: polish
  implying a capability (document understanding) that is out of scope.
- **Implementation cost:** Medium-high (new PDF rendering dependency, layout work, binary-ish
  artifacts).
- **Implementation risk:** High — adds a dependency and the strongest pull toward OCR/ingestion.
- **Memorability:** Medium but for the wrong reason (decorative).
- **Recommendation:** Reject. Already rejected in the prior Demonstration Layer Review; that
  reasoning still holds.

### C. Interactive Review Workflow

- **Recruiter impact:** High. A reviewer who can click through cases spends more time and
  forms a concrete memory ("I clicked the quantity-mismatch one and watched it flag the line").
- **Founder impact:** High. Lets a non-technical founder *self-serve* the "messy docs →
  flagged field → route to a person" story across multiple cases, not just one frame.
- **Technical credibility:** High and increasing. Navigating real cases backed by real
  evidence makes the deterministic 1.0 metrics read as earned rather than trivial — it shows
  the *variety* of what the taxonomy catches.
- **Implementation cost:** Low-medium. Vanilla inline JS over data already embedded in the
  generated HTML; no new dependency, no server, no build.
- **Implementation risk:** Low **if hard-bounded** to inline vanilla JS in the single
  self-contained file. The risk to watch is scope creep into a framework/server — explicitly
  forbidden below.
- **Memorability:** Highest of all options — interaction is what a recruiter remembers.
- **Recommendation:** **Proceed.** Best engagement-per-unit-cost; uniquely matches the
  phase's stated purpose; respects every constraint.

### D. Demonstration Pack Generation

- **Recruiter impact:** Low-marginal. `run_full_pipeline.py` + README quickstart already
  deliver a one-command, ready-to-open local demo.
- **Founder impact:** Neutral — convenience, not a new signal.
- **Technical credibility:** Neutral.
- **Implementation cost:** Low.
- **Implementation risk:** Low, but mostly repackages what exists.
- **Memorability:** Low.
- **Recommendation:** Reject as a standalone phase; fold any genuinely missing convenience
  into Option C's output instead.

### E. Other Bounded Alternative

Considered and not adopted as a separate track. The strongest "alternative" is simply
ensuring Option C also yields a refreshed committed screenshot/short clip-style stills of
the interactive reviewer for the README — treated as part of C's acceptance, not a fifth
option. No alternative beats interactivity on engagement-per-cost within the constraints.

---

# Recommended Direction

**Next Phase — Interactive Document-Panel Reviewer (Static, Self-Contained).**

Extend `src/crosswise/reviewer/static_html.py` so the generated
`docs/evidence/crosswise_reviewer_v1_0.html` becomes interactive via inline vanilla
JavaScript: a case selector (or navigable list) lets a reviewer choose any bundle and see
its side-by-side invoice / PO / receipt panels, the highlighted disagreeing field(s), and
the detected label, evidence reference, confidence score, and route update inline. All data
is embedded at generation time from the existing reconciliation/reliability outputs; the
file makes no network request and runs by double-clicking it. Retain all current static
content (metrics summaries, scope notices, command section) as a no-JS fallback.

---

# Why This Direction Wins

- **It matches the phase mandate exactly.** The brief names "reviewer engagement"; interaction
  is engagement. No other option moves that needle.
- **It adds a new signal instead of repackaging one.** A, D mostly overlap existing artifacts;
  B is decorative and scope-risky. C lets a reviewer *experience* the workflow Crosswise is
  about.
- **It strengthens credibility rather than risking it.** Browsing the full case set makes the
  deterministic baseline read as engineered (varied, evidence-backed) rather than trivially 1.0.
- **It costs little and stays in scope.** Vanilla inline JS over already-embedded data — no
  dependency, no server, no framework — preserves the Slice 7 self-contained-file guarantee.
- **It produces fresh README-grade stills** of the working system being explored, compounding
  the first-impression gains from the Final Portfolio Audit.

---

# Scope Boundaries

Explicitly out of scope for this phase:

- OCR, document ingestion, or parsing of any kind.
- Synthetic PDF generation, or any binary/print document rendering.
- Standalone synthetic HTML "document pack" files separate from the reviewer.
- APIs, model calls, paid services, or any network request — the reviewer must remain a
  single self-contained local HTML file that runs offline by double-click.
- Web servers and frameworks of any kind: Streamlit, React, Next.js, Flask, FastAPI, Node,
  any build system, bundler, npm/`package.json`, or external frontend dependency, font, CDN,
  or script.
- Deployment, authentication, databases, persistence of reviewer state.
- New reconciliation, evaluation, confidence, or routing **logic** — this is a presentation/
  interaction layer only; it must consume the same outputs the tests and report already use.
- Autonomous accounting / payment / legal / tax workflows, and any change to the non-advice
  or synthetic-only posture.
- Any modification to `assets/prototypes/crosswise-prototype.zip`.

The only new technology permitted is **vanilla inline JavaScript and CSS embedded in the
single generated HTML file**. No external scripts, no modules fetched over the network.

---

# Acceptance Criteria For The Next Phase

The phase is accepted when:

- `scripts/generate_reviewer.py` produces a single self-contained
  `docs/evidence/crosswise_reviewer_v1_0.html` with **no external network dependency**,
  runnable by opening the file directly.
- A reviewer can **select any case** and see its document panels, highlighted disagreeing
  field(s), detected label, evidence reference/summary, confidence score, and route update
  inline — driven by data embedded at generation time.
- At least one **clean match** is selectable to show the system does not over-flag.
- Displayed values **exactly match** the underlying reconciliation/reliability outputs
  (no hand-authored or divergent numbers); a test asserts displayed values equal source values.
- All current static content (metrics summaries, scope notices, command section, non-advice /
  synthetic-only statements) is **retained** as a no-JavaScript fallback — the file remains
  legible with scripting disabled.
- Tests cover the interaction layer's data wiring (each case's embedded values, highlighted
  fields correspond to detected discrepancies, scope/non-advice text retained). Full `pytest`
  continues to pass.
- A refreshed committed screenshot (or set of stills) of the interactive reviewer is produced,
  suitable for the README's working-system first impression. (Updating the README itself is
  out of scope unless separately authorized.)
- `git status --short` shows only intended additions/modifications; the prototype ZIP is
  untouched.

---

# Risks

| Risk | Mitigation |
|---|---|
| Scope creep into a framework, bundler, or local web server. | Hard boundary: vanilla inline JS/CSS in one self-contained file only; no dependency, no server, no build; reuse the Slice 7 pattern. |
| Interactive layer drifts from real outputs (shows values that disagree with the metrics). | Embed strictly from the same JSON the report/tests consume; add a test asserting displayed values equal source values. |
| Reviewer breaks for no-JS / strict environments. | Keep all current static content as a no-JS fallback; JS only enhances navigation, never gates content. |
| "Interactivity hides weak substance" (recruiter anti-pattern). | Highlights tie to *actual* detected evidence; include a clean case and keep honest-limitations text — interaction makes limitations more visible, not less. |
| Network request sneaks in via a CDN font/script. | Acceptance requires zero network requests; assert no external `src`/`href` fetches in the generated HTML. |
| Effort balloons across all ten bundles. | Reuse existing panel CSS; the interaction is selection over already-rendered records, not new per-case layout work. |

---

# Final Recommendation

**Proceed with the Interactive Review Workflow as the next phase.** It is the smallest layer
that turns Crosswise from a system a reviewer *reads* into one a reviewer *explores* —
clicking through cases, watching the flagged field and its evidence and route update, and
discovering for themselves that the engine is honest and conservative. It is the only option
that serves the phase's stated purpose (reviewer engagement), adds a genuinely new signal,
strengthens rather than risks technical credibility, and stays inside every hard constraint
using nothing but vanilla inline JavaScript in the existing self-contained file. Synthetic
HTML/PDF document packs and demo-pack repackaging are rejected as redundant, decorative, or
scope-risky. Do not add a demonstration layer beyond this one by inertia.

---

*Document version 1.0. Strategic review only — no code, no README changes, no implementation;
only this file created. Crosswise name, direction, and scope boundaries are treated as fixed.*
