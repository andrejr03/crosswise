# Crosswise — Final Portfolio Review and Presentation Audit (v1.0)

> Slice 10. Read-only audit to decide whether Crosswise is ready for its first public
> GitHub push and external review. Evaluated through the `werkstudent-recruiter` lens
> (first impression, memorability, technical credibility, finishability, honest evidence),
> as if discovered cold by a startup founder, a technical hiring manager, a data-science
> lead, and a Werkstudent recruiter. This document modifies no code, no documentation,
> and creates only this file. Crosswise name, direction, and scope boundaries are treated
> as fixed and are not reopened.

---

## Executive Verdict

**READY WITH MINOR COSMETIC IMPROVEMENTS.**

Crosswise is a finished, honest, reproducible local system with a clear thesis, a clean
modular architecture, a checked-in evaluation, a real trust/routing layer, and — now —
a genuinely memorable visual that shows the product *catching a discrepancy*. It clears
the bar for a serious public portfolio project. The only things standing between it and a
flawless first impression are cosmetic: a README "Early Development / Slice list" framing
that under-sells a complete pipeline, and a hero image sourced from the design prototype
rather than the real generated screenshot. None of these are blocking. A recruiter or
founder who lands on this repo will understand it and remember it.

---

## 1. First Impression Audit

**Landing page (README):** Strong. The hero image immediately communicates "document
reconciliation with a flagged mismatch and a routing decision," and the one-paragraph
"What Crosswise Does" is concrete and result-first. The fresh-clone quickstart with stated
expected outputs (10 cases; precision/recall/F1 = 1.0; 1 auto_accept / 8 needs_review /
1 blocked) is exactly what a technical reader wants in the first scroll.

**Showcase image:** Excellent and distinctive. The dark, editorial, monospace-meets-serif
aesthetic with the gold "review" highlight on the disagreeing field is well above typical
student-portfolio polish. It reads as designed, not templated.

**Perceived sophistication:** High for a junior/Werkstudent artifact. The vocabulary
(line-item reconciliation, field-level evidence, confidence routing, macro-F1) is used
correctly and backed by artifacts, not sprinkled as buzzwords.

**Perceived originality:** Above average. "Reconciliation + evidence + conservative human
routing, synthetic-only, no OCR/no model calls" is a deliberately scoped, unusual framing
that signals judgment rather than a copied tutorial.

**Perceived engineering quality:** High. Clean `src/crosswise/` package split by concern
(generation, schemas, validation, normalization, matching, reconciliation, evaluation,
confidence, routing, reporting, reviewer), a one-command pipeline, 73 collected tests, a
LICENSE, and a `pyproject.toml`. Nothing important is hidden in notebooks.

**Weakness:** "Current Status: Early Development" plus a 14-line slice changelog is the
first textual block after the thesis. It under-sells a system that is, in fact, an
end-to-end working pipeline. The framing invites "unfinished" when the artifact is finished.

---

## 2. Technical Credibility Audit

- **Architecture — Strong.** Cleanly modularized by pipeline stage; separation of
  `data/`, `data/ground_truth/`, and `docs/evidence/` is disciplined. The reviewer is a
  rendering layer that consumes the same JSON the tests and report use, not a parallel
  source of truth.
- **Testing — Strong for scope.** 73 tests across the stages, including a test that the
  reviewer's displayed values match source outputs and that synthetic-only/non-advice
  statements are retained. Appropriate depth for a deterministic baseline.
- **Reproducibility — Strong.** Fresh-clone path is explicit, single-command
  (`run_full_pipeline.py`) plus a per-stage breakdown, with expected numeric results stated
  in the README so a reviewer can verify without running.
- **Evaluation methodology — Adequate, with one honest caveat.** Precision/recall/F1,
  macro-F1, and per-label TP/FP/FN against generated ground truth is the right shape. The
  caveat (already acknowledged in the demonstration review) is that a wall of `1.000` on a
  deterministic baseline can read as "trivially easy." This is mitigated — not eliminated —
  by the new side-by-side concrete cases that show *what* was caught.
- **Evidence quality — Strong.** The local evidence report ties each case to a route, a
  confidence score, an explanation, and an evidence reference; four worked examples
  (clean / quantity / supplier-alias / schema-failure) are inspectable in Markdown.
- **Scope discipline — Exceptional, and a credibility asset.** Synthetic-only, no PII, no
  OCR, no APIs, no model calls, no autonomous actions — stated consistently across
  AGENTS.md, README, and the evidence report. Confidence is held separate from severity.
  This reads as engineering maturity, not as limitation.

---

## 3. Demonstration Layer Audit

- **Reviewer screenshot — Memorable.** The discrepancy showcase (`SYN-INV-0003` vs `PO 003`,
  unit price €15.00 vs €13.00, +€2.00 delta flagged `review`, model confidence 0.700 below
  threshold, "Route to human review" action) tells the entire product story in one frame.
- **Reviewer experience — Good.** Side-by-side field comparison with a per-field status
  column, an explicit delta, a confidence meter, and an action panel. A non-technical
  founder grasps "lines compared → mismatch flagged → escalated to a person" in seconds.
- **Discrepancy story clarity — High.** The flagged rows (Unit price, Line total) are
  visually distinct from the matched rows (Vendor, Quantity, Tax); the "Δ" column makes the
  disagreement quantitative and obvious.
- **Confidence / routing presentation — High.** "0.700 — below threshold" with a progress
  bar, paired with "1 discrepancy · evidence linked · needs_review route assigned," makes
  the trust layer concrete rather than asserted.
- **Memorability — High.** The three bottom pillars (Line-item matching / Field-level
  evidence / Human review routing) give a recruiter a one-line summary they can repeat in a
  shortlisting conversation. This is the single biggest improvement over a metrics-only
  dashboard.

---

## 4. Recruiter Readability Audit

Can a reviewer understand the project in 3–5 minutes? **Yes — comfortably.**

- **What it does:** Clear from the hero image + first paragraph (≈30s).
- **Why it exists:** Clear from the thesis and Non-Goals (reconciliation + evidence-backed
  human review, deliberately not accounting/tax/payment automation) (≈1 min).
- **What was built:** Clear from the pipeline section, generated-outputs list, and quickstart
  (≈1–2 min).
- **What is technically interesting:** The confidence/severity separation, the conservative
  three-way routing, the checked-in evaluation, and the deterministic evidence-rendered
  reviewer (≈1 min).

A time-boxed recruiter gets a complete, credible mental model well inside five minutes.

---

## 5. Gap Analysis

**Cosmetic**

- README hero uses the *design prototype* image (`assets/prototypes/crosswise-showcase.png`)
  rather than the real generated screenshot (`CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`).
  The two are near-identical by design, but the working-system image carries more credibility
  for essentially zero cost.
- "Current Status: Early Development" + slice-by-slice changelog under-sells a complete
  pipeline; a one-line "what works today" summary would frame it as finished.
- README status list stops at Slice 9 and does not mention Slice 9B (showcase-aligned design);
  minor staleness only.
- No top-of-README license/Python-version badges. Optional; recruiters notice but do not
  weight heavily.

**Should-fix** (not blocking, but worth doing before or shortly after the push)

- The "perfect 1.0 metrics" perception risk persists for a skeptical data-science lead. One
  or two sentences in the README explicitly framing the baseline as deterministic-by-design
  (so 1.0 is expected and the interesting work is the taxonomy + routing, not the score)
  would pre-empt the "of course it's 1.0" reaction. The evidence already supports this; it is
  a framing gap, not a substance gap.

**Must-fix**

- None. There is no correctness, honesty, reproducibility, or scope defect that blocks a
  first public push.

---

## 6. Portfolio Readiness Decision

**READY WITH MINOR COSMETIC IMPROVEMENTS.**

The substance is push-ready today. The only open items are cosmetic framing and a
one-image swap — improvements that raise an already-strong first impression rather than
fix a defect.

---

## 7. Push Recommendation

**Would you personally recommend pushing the repository publicly now? — Yes.**

The repository is honest, finished, reproducible, and memorable. The remaining items are
cosmetic and can land in a follow-up commit without holding back the first public push.

---

## 8. Scoring (0–10)

| Dimension | Score |
| --- | ---: |
| First Impression | 8 |
| Technical Depth | 8 |
| Demonstration Quality | 9 |
| Reproducibility | 9 |
| Portfolio Strength | 8 |
| **Overall** | **8.4** |

---

## 9. Final Verdict

**Rationale.** Crosswise is the rare junior/Werkstudent portfolio artifact that is both
*finished* and *legible*. It pairs a disciplined, well-tested, reproducible pipeline with a
distinctive, memorable visual that shows the product working — the side-by-side flagged
mismatch with a confidence-driven routing decision. Scope discipline (synthetic-only, no
OCR, no model calls, no autonomous actions) reads as judgment and de-risks the
"impressive-sounding but unfinished" failure mode that sinks most student projects. The
deterministic 1.0 metrics and the "Early Development" framing are the only soft spots, and
both are presentation, not substance.

**Recommended next action.** Before (or immediately after) the first public push, make two
zero-risk cosmetic edits in a single follow-up commit: (1) swap the README hero to the real
generated screenshot `docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`, and
(2) replace "Early Development" with a one-line "what works today" summary plus a single
sentence framing the deterministic baseline so the 1.0 metrics read as expected-by-design.
Then push. Final recommendation: **Ready to show.**

---

*Document version 1.0. Review only — no code, no README, no documentation changes; only this
file created. Crosswise name, direction, and scope boundaries are treated as fixed.*
