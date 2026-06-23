# Crosswise Demonstration Layer Review (v1.0)

> Strategic review to decide the next demonstration layer after the technical MVP foundation (Slices 0–8). Evaluated through the `werkstudent-recruiter` lens (memorability, credibility, finishability, honest evidence) without being written as a career document. Crosswise name and direction are treated as fixed and are not reopened. This review modifies no code, no README, and creates only this file.

---

# Decision

**PROCEED WITH STATIC REVIEWER UPGRADE**

The smallest next layer that most increases Crosswise's impact is upgrading the existing self-contained static reviewer to render document-like invoice / PO / receipt panels in side-by-side comparison, with the flagged field highlighted and its evidence and route shown inline. It is rendered deterministically from the structured records that already exist — no PDFs, no parsing round-trip, no new runtime dependency.

---

# Executive Summary

Crosswise is already a technically solid, reproducible, honest local system. Its weakness is not engineering; it is **first-glance legibility**. The project's entire thesis is *document reconciliation* — messy invoices/POs/receipts reconciled line by line, mismatches flagged, uncertain cases routed to human review — yet a reviewer never sees a single document or a single mismatch shown across documents. The current static reviewer is a competent metrics dashboard: a hero, scope notices, a pipeline strip, metric panels, example pills, and a case table. It proves the pipeline *ran* and *scored perfectly*, but it does not let a non-technical founder or a time-boxed recruiter *grasp the product* in the first 90 seconds.

The single highest-leverage move is to make the reconciliation **visible and concrete**: show one clean bundle and a few flagged bundles as side-by-side document panels with the mismatched field circled and explained. This converts an abstract `1.0 F1` table into a memorable "oh, I see exactly what it caught and why" moment — the founder-readable signal the foundation document always intended, and the one thing currently missing. It is achievable inside every existing constraint, adds no dependency, and reuses data and routes the pipeline already produces.

Synthetic PDF generation and deterministic re-ingestion are rejected as the *next* layer: PDFs without OCR are decorative (a reviewer must open files that do not feed the pipeline), and re-parsing self-generated documents is tautological and reads as busywork. Demo-pack generation is largely already delivered by `run_full_pipeline.py` and adds little new signal. The reviewer upgrade dominates all four on impact-per-unit-cost.

---

# Current MVP Assessment

What Crosswise already demonstrates well:

- **A complete, honest pipeline.** Generation → validation → reconciliation → evaluation → reliability routing → report → static reviewer, runnable from a fresh clone with one command (`scripts/run_full_pipeline.py`). 69 passing tests.
- **Measurable evaluation against generated ground truth.** Precision/recall/F1 and macro-F1 per discrepancy label, with checked-in results a reviewer can read without running anything.
- **A real trust layer.** Deterministic confidence scoring and conservative three-way routing (`auto_accept` / `needs_review` / `blocked`), with confidence held separate from severity.
- **Scope discipline as a feature.** Synthetic-only data, explicit non-advice language, no OCR, no APIs, no autonomous actions — stated repeatedly and consistently. This reads as judgment, not limitation.
- **Clean repository architecture.** `src/crosswise/` is cleanly modularized (generation, schemas, normalization, matching, reconciliation, evaluation, confidence, routing, reporting, reviewer), data/ground-truth/evidence are separated, and nothing is hidden in notebooks.
- **A bounded, labeled discrepancy taxonomy** with all ten v1 labels represented across ten bundles.

This is already a credible "junior data product, not a notebook." The technical foundation is not the problem.

---

# Gap Analysis

What still prevents Crosswise from being memorable at first glance:

1. **The product is invisible.** The thesis is document reconciliation, but no document is ever shown. The reviewer reads *about* invoices/POs/receipts and sees a case table — they never see the artifacts being reconciled or a mismatch located in context. The most compelling part of the story is the part a viewer cannot see.
2. **Perfect metrics are quietly unconvincing.** A wall of `1.000` precision/recall/F1 on a deterministic baseline can read as "trivially easy" rather than "well engineered." The numbers need a concrete, inspectable case behind them to feel earned. Showing *what* was caught makes the metrics believable; showing only the metrics invites the "of course it's 1.0, it's deterministic" reaction.
3. **No single screenshot tells the story.** A recruiter scanning a README in 30 seconds needs one image that says "this is what it does." The current showcase image is a design prototype, not the working system. There is no real screenshot of Crosswise *catching a discrepancy*.
4. **The "evidence-backed review" claim is told, not shown.** Evidence currently appears as short text summaries in the report. The founder-readable payoff — *here are the two documents, here is the field that disagrees, here is the route* — is asserted rather than rendered.

The gap is entirely at the demonstration layer. Every fact needed to close it already exists in the generated fixtures and reconciliation output; it is just not surfaced visually.

---

# Candidate Option Review

### 1. Synthetic PDF document generation

- **Expected impact:** Medium-low. "It makes PDFs" sounds impressive for one sentence but the PDFs do nothing in-pipeline without OCR — they are decorative artifacts a reviewer must open separately.
- **Implementation cost:** Medium-high. Introduces a PDF rendering dependency, layout/templating work, and new generated binary-ish artifacts to manage and test.
- **Risk:** High scope-creep and the classic recruiter anti-pattern: polish that implies a capability (document understanding) the system explicitly does not have. Invites the "so does it read PDFs?" question that ends in "no."
- **Recruiter / founder readability:** Medium. A pretty PDF is legible but disconnected from the reconciliation result.
- **Technical credibility:** Mixed. Can read as decorative; risks suggesting OCR ambitions that are out of scope.
- **Scope-control risk:** High — naturally pulls toward OCR and ingestion next.
- **Recommendation:** Reject as the next layer.

### 2. Deterministic synthetic document ingestion

- **Expected impact:** Low. Parsing documents the project just generated is circular; a reviewer immediately sees it proves nothing new.
- **Implementation cost:** Medium, and depends on Option 1 existing first.
- **Risk:** Tautology risk ("I parse exactly what I wrote") undermines credibility rather than building it.
- **Recruiter / founder readability:** Low. Hard to explain why it matters.
- **Technical credibility:** Low-to-negative; reads as engineering for its own sake.
- **Scope-control risk:** Medium.
- **Recommendation:** Reject.

### 3. Static review experience upgrade

- **Expected impact:** High. Directly closes the memorability gap by making reconciliation visible: side-by-side document panels, the mismatched field highlighted, evidence and route inline. Produces the single screenshot the project lacks.
- **Implementation cost:** Low-to-medium. Pure rendering work in the existing `src/crosswise/reviewer/static_html.py` generator, fed by data that already exists. No new dependency, no server, no framework.
- **Risk:** Low. Stays entirely inside the self-contained-HTML constraint already honored in Slice 7.
- **Recruiter / founder readability:** Highest of all options — a founder grasps "messy documents → flagged mismatch → review" instantly.
- **Technical credibility:** High and *increasing* — it makes the perfect metrics believable by showing the concrete cases behind them.
- **Scope-control risk:** Low, if bounded to rendering existing records (must not drift into PDF or interactivity).
- **Recommendation:** **Proceed.** Best impact-per-cost; closes the actual gap.

### 4. Demo pack generation

- **Expected impact:** Low-marginal. `run_full_pipeline.py` plus the README quickstart already deliver a one-command, ready-to-open local demo.
- **Implementation cost:** Low.
- **Risk:** Low, but mostly repackages what exists.
- **Recruiter / founder readability:** Neutral — convenience, not a new signal.
- **Technical credibility:** Neutral.
- **Scope-control risk:** Low.
- **Recommendation:** Reject as a standalone next layer; fold any genuinely missing convenience into the reviewer upgrade's output instead.

### 5. Better bounded alternative

Considered and not adopted as a separate track. The strongest "alternative" is simply ensuring the reviewer upgrade also yields a committed screenshot/evidence image so the README's first impression shows the working system catching a discrepancy. That is treated as part of Option 3's acceptance, not a fifth option.

---

# Recommended Next Slice

**Slice 9 — Document-Panel Reconciliation View (Static Reviewer Upgrade)**

**Objective:** Extend the existing self-contained static reviewer so that, for a curated set of bundles, it renders document-like invoice / PO / receipt panels side by side, visually highlights the field(s) that disagree, and shows the detected label, the evidence, the confidence, and the route inline — turning the abstract case table into an inspectable, founder-readable reconciliation story. Rendered deterministically from existing structured records; no new runtime dependency.

The curated set should follow the foundation's canonical demo storyboard: one clean match, one quantity mismatch, one unit-price mismatch, one supplier-alias case, one duplicate-invoice case, and one low-confidence or schema-failure case.

---

# Scope Boundaries

Explicitly out of scope for this slice:

- Real documents, real company/supplier data, PII.
- OCR of any kind.
- Synthetic PDF generation or any binary document rendering.
- Document re-ingestion / parsing of generated documents.
- Live APIs, model calls, paid services.
- Streamlit, React, Next.js, Flask, FastAPI, any web server, build system, npm/`package.json`.
- External frontend dependencies, fonts, CDNs, scripts, or any network request — the reviewer must remain a single self-contained local HTML file.
- Deployment, authentication, databases.
- New reconciliation, evaluation, confidence, or routing *logic* — this is a rendering layer only; it must consume the same outputs the tests and report already use.
- Autonomous accounting / payment / legal / tax workflows, and any change to the non-advice or synthetic-only posture.
- Any modification to `assets/prototypes/crosswise-prototype.zip`.

---

# Acceptance Criteria for the Next Slice

The slice is accepted when:

- `scripts/generate_reviewer.py` produces a single self-contained `docs/evidence/crosswise_reviewer_v1_0.html` with **no external network dependency** (preserving the Slice 7 constraint).
- For each curated bundle, the reviewer renders **document-like panels** for the relevant invoice, purchase order, and receipt, laid out **side by side**, populated only from existing generated structured records.
- The **specific disagreeing field(s)** for each flagged bundle are visually highlighted within the panels (e.g., the mismatched quantity, unit price, or supplier name).
- Each flagged bundle shows, inline with its panels: the detected discrepancy label, the evidence reference/summary, the confidence score, and the route (`auto_accept` / `needs_review` / `blocked`).
- At least one **clean match** is shown to demonstrate the system does not over-flag.
- The existing metrics summaries, scope notices, and command section are retained (no regression of current content).
- The rendered values exactly match the underlying reconciliation/reliability outputs (no hand-authored or divergent numbers).
- Tests cover the new rendering: panels exist for curated bundles, highlighted fields correspond to detected discrepancies, and synthetic-only / non-advice statements are retained. Full `pytest` continues to pass.
- A committed evidence image (screenshot) of the upgraded reviewer showing a flagged discrepancy is produced, suitable for use as the README's working-system first impression. (Updating the README itself is out of scope for this slice unless separately authorized.)
- `git status --short` shows only intended additions/modifications; the prototype ZIP is untouched.

---

# Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Rendering layer silently drifts from real outputs, showing values that disagree with the metrics. | Render strictly from the same JSON the report/tests consume; add a test asserting displayed values equal source values. |
| Scope creep toward PDFs, interactivity, or a framework. | Hard boundary: HTML-string generation only, single self-contained file, no new dependency; reuse the Slice 7 pattern. |
| Visual polish hides weak substance (recruiter anti-pattern). | Highlight is tied to *actual* detected evidence; show a clean case and keep honest-limitations text — the panels make limitations more visible, not less. |
| "Perfect 1.0 metrics look trivial" perception persists. | The concrete side-by-side cases are precisely what makes the deterministic baseline read as engineered rather than trivial; pair panels with the existing failure/limitation framing. |
| Layout complexity balloons. | Bound to the six canonical storyboard bundles, not all ten; reuse existing CSS patterns already in the reviewer. |
| README first impression still shows the prototype, not the system. | Produce a committed screenshot as an acceptance artifact so a later, separately-scoped README touch can swap it in. |

---

# Final Recommendation

**Proceed with the Static Reviewer Upgrade as Slice 9 (Document-Panel Reconciliation View).** It is the smallest layer that turns Crosswise from a technically solid local pipeline into a system a reviewer can *see working* — a side-by-side document view that locates a flagged mismatch and explains it, backed by evidence and a routing decision. It closes the one real gap (first-glance legibility), respects every existing constraint, adds no dependency, reuses data the pipeline already emits, and yields the single screenshot the project currently lacks. Synthetic PDF generation, document re-ingestion, and demo-pack repackaging are explicitly deferred or rejected as lower-impact, higher-risk, or already-delivered. Do not add a demonstration layer beyond this one by inertia.

---

*Document version 1.0. Strategic review only — no code, no README changes, no implementation. Crosswise name, direction, and scope boundaries are treated as fixed.*
