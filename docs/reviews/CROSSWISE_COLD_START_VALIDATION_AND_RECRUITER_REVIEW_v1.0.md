# Crosswise Cold-Start Validation and Recruiter Review v1.0

Review mode: cold external validation.  
Review lenses: journey-validation-specialist and werkstudent-recruiter.  
Scope: validation only. No implementation, no planning artifact, no branch, no commit, no push.

## Executive Verdict

**Final decision: READY WITH MINOR CHANGES.**

Crosswise works as a repository-backed portfolio artifact. The core claims are supported by generated fixtures, ground truth, reconciliation output, evaluation output, reliability output, a Markdown evidence report, a self-contained reviewer, synthetic document renders, screenshots, and a passing local test suite. The project is credible, reproducible, and memorable.

The reason this is not "READY FOR PUBLIC PUSH" without qualification is not functionality. It is trust framing. A cold reviewer sees three perception risks: the README still says "Early Development"; some reviewer UI labels say "Model confidence" despite the project explicitly having no model calls; and the documentation/evidence index does not make the synthetic document pack as discoverable as the rest of the proof chain. These are small but visible trust issues before public presentation.

Validation performed:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
88 passed in 5.68s
```

## Part A - Reality Validation

Question: Can the claims made in the README be reasonably verified from repository artifacts?

Answer: Mostly yes. The repository proves an end-to-end deterministic, synthetic, offline document-reconciliation workflow. It does not prove real AI extraction, OCR, production document understanding, calibrated model confidence, or real-world accounting correctness, and it mostly avoids claiming those things.

| Claim area | Classification | Validation basis | Notes |
|---|---|---|---|
| Synthetic generation | Proven | `data/synthetic/fixtures_v1_0.json`, `data/ground_truth/ground_truth_v1_0.json`, Slice 1 evidence, tests | Deterministic metadata, seed, fixture version, taxonomy coverage, and synthetic-only policy are present. |
| Structured document records | Proven | Fixtures, schema models, document HTML renders | Supplier, SKU, PO, invoice, receipt, line records, bundles, and ground truth exist as structured data. |
| Validation | Proven | Slice 2 evidence, `scripts/validate_fixtures.py`, tests | Validates structure, required fields, references, arithmetic, dates, currency, taxonomy, routes, and synthetic-only constraints. |
| Normalization | Proven | Slice 2 evidence, normalization module, tests | Deterministic supplier, SKU, date, currency, whitespace, and casing normalization is implemented. |
| Reconciliation | Proven | `data/reconciliation/reconciliation_v1_0.json`, Slice 3 evidence, tests | Produces 10 cases with expected labels and line/document evidence. |
| Line-item matching | Proven | Reconciliation output and reviewer case panels | PO, invoice, and receipt lines are matched and discrepancies are attached to affected fields/lines. |
| Discrepancy detection | Proven | Reconciliation output, evidence report, screenshots | The 10-label taxonomy is represented and detected in the deterministic fixture set. |
| Evaluation | Proven | `data/evaluation/evaluation_v1_0.json`, Slice 4 evidence, tests | Precision, recall, F1, macro F1, per-label metrics, false-positive, false-negative, and confusion structures exist. |
| Field-level reliability | Partially Proven | Reliability output and confidence factors | Evidence-based case confidence and routing are implemented; true calibrated field-level reliability, ECE, or reliability diagrams are explicitly not implemented. |
| Reliability routing | Proven | `data/reliability/reliability_v1_0.json`, Slice 5 evidence | 1 `auto_accept`, 8 `needs_review`, 1 `blocked`; non-advice reminders are present. |
| Evidence generation | Proven | `docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md` | Human-readable report summarizes pipeline, metrics, routes, examples, limitations, and reproduction commands. |
| Reviewer generation | Proven | `docs/evidence/crosswise_reviewer_v1_0.html`, `scripts/generate_reviewer.py`, tests | Static self-contained HTML reviewer exists and is tested for no external URLs and deterministic rendering. |
| Interactive reviewer | Proven | HTML contains interactive controls and all 10 cases; interactive screenshot exists | Interaction is presentation-only and offline, which is honestly stated. |
| Synthetic document pack | Partially Proven | `docs/evidence/documents/*.html`, `CROSSWISE_DOCUMENT_PACK_SHOWCASE.png` | Artifacts exist and are honest render-only documents, but README/evidence index discoverability is weaker than for the reviewer artifacts. |
| Reproduction workflow | Proven | README quickstart, `scripts/run_full_pipeline.py`, reproduction tests, current pytest pass | The path is explicit and locally validated. The full pipeline writes artifacts, but tests pass and no external services are needed. |
| "AI document reconciliation" framing | Partially Proven | Pipeline proves document reconciliation; no OCR/model calls are used | The term "AI" is acceptable as portfolio positioning only because limitations are stated. A skeptical reviewer may consider it over-framed for a deterministic baseline. |

Reality conclusion: The project proves its bounded claims. The strongest proof is the artifact chain from generated data to reviewer UI. The weakest proof is anything implied by the words "AI", "model confidence", or "field-level reliability" if read without the limitations.

## Part B - Journey Validation

Simulated cold visitor path:

```text
Cold visitor -> README -> Showcase -> Reviewer -> Documents -> Decision
```

### Journey Summary

I would continue through the journey. The README explains the project quickly, the showcase creates a strong memory, the reviewer makes the discrepancy concrete, and the generated documents complete the "source record" side of the story. The journey validates, but with friction around status language and confidence wording.

Final journey decision: **JOURNEY_VALIDATED_WITH_FRICTION**.

### Task-Level Findings

#### Task 1: README

- What I expected: A quick explanation, proof it runs, and honest limits.
- What I understood: Crosswise is a synthetic invoice/PO/receipt reconciliation workflow with evidence and human routing.
- What I actually did: Read the first screen, quickstart, generated outputs, pipeline, documentation, and data-policy sections.
- What confused me: "Current Status: Early Development" conflicts with the repo being portfolio-complete and with Slices 1-10 being done.
- What helped me: Exact expected outputs: 10 cases, perfect deterministic metrics, 1/8/1 routing split, tests pass.
- Trust assessment: Mostly trusted.
- Emotional state: Curious. The project has a clear operational story.
- Momentum assessment: Increased. The README gives a direct path to proof.
- Would I continue: Yes.
- Feedback: Replace "Early Development" with a truthful "portfolio-complete local demo" style status before public push.
- ChatGPT leakage assessment: I would not leave for ChatGPT to understand the README, but I might use it to interpret terms like macro F1 or confidence routing if non-technical.
- Language comprehension assessment: MOSTLY_CLEAR.

#### Task 2: Showcase Screenshot

- What I expected: A visual proof of the reconciliation workflow.
- What I understood: Invoice and PO disagree on unit price and line total, confidence is below threshold, and the case routes to human review.
- What I actually did: Inspected `CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`.
- What confused me: "Model confidence" can imply model calls, which the project explicitly excludes.
- What helped me: The highlighted rows, signed deltas, and route action make the product story immediate.
- Trust assessment: Mostly trusted.
- Emotional state: Motivated. It looks like a real finished portfolio artifact.
- Momentum assessment: Increased.
- Would I continue: Yes.
- Feedback: Rename "Model confidence" to "Reliability score" or "Case confidence" before public push.
- ChatGPT leakage assessment: No. The visual explains itself.
- Language comprehension assessment: CLEAR, except "model confidence".

#### Task 3: Reviewer HTML

- What I expected: A self-contained case explorer backed by generated outputs.
- What I understood: The reviewer exposes synthetic cases, routes, confidence, evidence, metrics, limitations, and reproduction commands.
- What I actually did: Inspected the HTML text, case controls, case index, notices, and screenshots.
- What confused me: The default reviewer story is strong, but the page is large enough that some proof sits below the first screenshot.
- What helped me: All 10 cases are present, the selected discrepancy is clear, no-JS fallback exists, and no external dependencies are claimed.
- Trust assessment: Mostly trusted.
- Emotional state: Curious.
- Momentum assessment: Increased.
- Would I continue: Yes.
- Feedback: Keep this as the main public artifact; it is more persuasive than raw metrics.
- ChatGPT leakage assessment: No. The reviewer gives enough context.
- Language comprehension assessment: MOSTLY_CLEAR.

#### Task 4: Synthetic Documents

- What I expected: Some proof of invoice, PO, and receipt source artifacts.
- What I understood: These are illustrative renders of generated source records, not files the system parses.
- What I actually did: Inspected `invoice.html`, `purchase_order.html`, `receipt.html`, and `CROSSWISE_DOCUMENT_PACK_SHOWCASE.png`.
- What confused me: The documents are not as discoverable from the README/evidence index as the reviewer screenshots.
- What helped me: Each document includes a visible synthetic document notice and no-OCR/non-advice boundaries.
- Trust assessment: Mostly trusted.
- Emotional state: Neutral. Useful supporting proof, but less compelling than the reviewer.
- Momentum assessment: Neutral.
- Would I continue: Yes, but I would not lead with this artifact.
- Feedback: Publicly feature the reviewer screenshot; use document pack as supporting evidence.
- ChatGPT leakage assessment: No.
- Language comprehension assessment: MOSTLY_CLEAR.

### Day-Level Findings

- Most useful task: Opening the reviewer screenshot/reviewer HTML.
- Least useful task: Reading old slice-by-slice status in the README.
- Biggest confusion: "Early Development" and "Model confidence" conflict with the intended public perception.
- Biggest friction: The proof chain is broad; a cold reviewer may not know which artifact to inspect first.
- Trust assessment: Mostly trusted.
- Language comprehension assessment: MOSTLY_CLEAR.
- Motivation level: High enough to continue.
- Emotional state: Curious.
- Momentum assessment: Increased.
- Would I return tomorrow: Yes, if I were evaluating the candidate.
- Why: The repo has a memorable working artifact and enough evidence to ask serious interview questions.

### Memory-Anchor Assessment

What I will remember tomorrow:

- The unit-price mismatch: EUR 15.00 vs EUR 13.00, +EUR 2.00, routed to review.
- The conservative 1/8/1 route split: one clean case, eight review cases, one blocked case.
- The synthetic-only/no-OCR/no-model-calls restraint.
- The fact that the project is finished enough to run and inspect locally.

### Trust Assessment

Overall trust: Mostly trusted.

- Why I trust it: Claims are backed by data outputs, evidence reports, screenshots, generated HTML, and tests.
- Why I do not fully trust it: Perfect metrics and "Model confidence" wording can make a skeptical reviewer wonder whether the language is stronger than the implementation.
- Credible evidence: `88 passed`, generated JSON artifacts, self-contained reviewer, non-advice notices, deterministic pipeline script.
- Generic or unsupported elements: "AI" and "field-level reliability" are stronger than the current deterministic baseline if read without limits.
- Would I act without ChatGPT or Google: As a recruiter, yes. As a production user, no, because this is explicitly synthetic and non-production.
- What I would verify externally first: I would clone, run tests, open the HTML reviewer, and ask the candidate to explain why the metrics are all 1.0.

### Retention Assessment

- Why I would return tomorrow: To decide whether to shortlist the candidate and prepare interview questions.
- Why I would not return tomorrow: If I only saw the README "Early Development" status and did not reach the reviewer.
- Return score: 8/10.

### Breakpoint Assessment

Most likely leave point: After reading "Current Status: Early Development" if I am time-boxed.

Why: It undercuts the "portfolio-complete" state and could make a recruiter assume the repository is still unfinished before seeing the proof artifacts.

### ChatGPT Leakage Assessment

Would I leave this product/repo and use ChatGPT? Mostly no.

Reason: The README, reviewer, and evidence report explain the workflow clearly enough. Leakage risk exists only for terms such as macro F1, confidence routing, field-level reliability, and deterministic baseline. A B1-B2 non-native English reader may use ChatGPT to simplify those terms, but not to understand the basic product story.

### Language Comprehension Assessment

Overall assessment: MOSTLY_CLEAR.

- Unclear wording: "confidence routing", "field-level reliability", "macro F1", "deterministic baseline", "model confidence", "autonomous business actions".
- Likely misunderstanding: A reader may think Crosswise uses a live AI model or OCR because the visual says "Model confidence" and the README says "AI Document Reconciliation".
- Simpler suggested wording: "Case reliability score", "routes uncertain cases to review", "tested on synthetic examples", "no OCR or model calls".
- Family-explainable version: "It creates fake invoices, orders, and receipts, compares their line items, finds mismatches, and shows which cases a person should review."
- ChatGPT leakage risk from wording: Low to medium.
- Boundary preservation risk: Low overall, medium for "Model confidence".

### Product Dependency Assessment

If this product disappeared today, could I complete this task using ChatGPT alone?

Partially. ChatGPT could describe how to compare invoices, POs, and receipts, but it would not provide this repository's deterministic fixtures, ground truth, evaluation outputs, reviewer UI, screenshots, and reproducible tests. The unique value is the finished proof artifact, not just the idea.

## Part C - Werkstudent Recruiter Review

### Executive Verdict

Crosswise would increase interview probability for junior AI/data, Python automation, operations analytics, and Werkstudent-style roles. It is more credible than a notebook project because it is modular, reproducible, scoped, visual, and honest about limits.

Recruiter final recommendation: **Show after targeted edits.**

### Would This Increase Interview Probability?

Yes. Interview probability impact: **Moderately increases**.

It shows that Andre can finish a bounded technical product, design synthetic data, define evaluation, build an evidence layer, and communicate limitations. It is not a production system, but it does not pretend to be one.

### What Signals Competence?

- End-to-end local pipeline with clear stages.
- Deterministic synthetic data and generated ground truth.
- Reconciliation output tied to evidence, labels, and routes.
- Evaluation metrics and tests.
- Conservative scope boundaries: no real data, no OCR, no APIs, no autonomous actions.
- Self-contained reviewer UI that makes the product legible in under two minutes.
- Visual polish without losing the technical story.

### What Signals Weakness?

- Perfect 1.0 metrics can look like the task was too controlled.
- "AI" and "Model confidence" may look inflated because the project explicitly has no model calls.
- README "Early Development" undersells the finished state.
- AGENTS.md says only Foundation, Slice 0, and Slice 1 are completed, which conflicts with the README/evidence chain.
- The document pack exists but is not featured as clearly as other generated outputs.

### What Would I Ask In An Interview?

- Why did you choose deterministic synthetic data instead of OCR or real documents?
- How is ground truth generated, and how do you avoid evaluating the system against itself?
- Why do all metrics score 1.0, and what harder test would break the baseline?
- How is confidence calculated if no model confidence is used?
- What is the difference between severity, confidence, and route?
- How would you add one realistic failure mode without using real invoices?
- Which part would you rewrite if this became a production prototype?
- How did you test that the reviewer displays values from the generated outputs rather than hand-authored copy?

### What Would I Remember After One Week?

I would remember the dark reviewer screenshot with a unit price mismatch routed to human review, and I would remember the disciplined "synthetic-only, no OCR, no model calls" boundary.

### What Recruiters Notice

- A clear README.
- The screenshot.
- The quickstart and expected outputs.
- Tests.
- The self-contained reviewer.
- Honest limitations.

### What Recruiters Ignore

- Most slice history.
- Long internal review documents.
- Architecture detail beyond the first 2-3 minutes.
- The full contents of every JSON artifact unless interviewing technically.

### Strongest Signal

The strongest signal is finishability with judgment: Crosswise is complete enough to run, inspect, and discuss, while refusing scope creep into real documents, payment actions, or accounting advice.

### Weakest Signal

The weakest signal is the perfect deterministic evaluation. It is honest, but it invites the question: "Did the candidate build a real evaluator or a controlled demo that cannot fail?"

### Over-Engineered / Under-Sold

- Over-engineered risk: Many review and evidence documents can feel like process volume if the public entry point is not sharply curated.
- Under-sold risk: The README says "Early Development" even though the current repo is a finished local portfolio demo.

### Evaluation Dimensions

| Dimension | Score | Recruiter read | Evidence | Risk | Improvement |
|---|---:|---|---|---|---|
| First Impression | 8 | Clear and polished | README and screenshot | "Early Development" weakens confidence | Update status wording |
| Memorability | 8 | Strong one-frame story | Unit-price mismatch screenshot | Document pack less memorable | Feature reviewer screenshot publicly |
| Technical Credibility | 8 | Solid for a junior portfolio | 88 tests, modular pipeline, artifacts | Perfect metrics look easy | Explain deterministic baseline plainly |
| Product Thinking | 8 | Good workflow judgment | Human review routing and non-advice scope | "AI" may over-frame | Use bounded language |
| Communication Quality | 7 | Generally clear | README, evidence report | Too many artifacts and some jargon | Curate first path |
| Recruiter Signal Strength | 8 | Interview-worthy | Reproducible local pipeline | Status inconsistency | Minor README cleanup |
| Portfolio Differentiation | 8 | More distinctive than typical student demos | Synthetic reconciliation plus reviewer | Could read as UI-polished deterministic rules | Be honest about rule baseline |
| Internship Appeal | 8 | Shows Python, testing, data modeling | Scripts, tests, package structure | No production integration | Keep as portfolio, not production claim |
| Werkstudent Appeal | 8 | Strong practical automation signal | Procurement-style workflow | Needs concise German-style explanation | Add simple two-line portfolio blurb |
| University Admissions Appeal | 7 | Shows independent project maturity | Docs, tests, scope discipline | Domain may be business-specific | Emphasize method and evaluation |

### Memorability Score

8/10.

### Recruiter Appeal Score

8/10.

## Part D - Screenshot Review

Reviewed screenshots:

- `docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`
- `docs/evidence/CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png`
- `docs/evidence/CROSSWISE_DOCUMENT_PACK_SHOWCASE.png`

### Strongest Screenshot

`CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`.

Reason: It is the clearest proof shot. It shows the mismatch, the delta, confidence, and route in one frame without needing scroll context.

### Weakest Screenshot

`CROSSWISE_DOCUMENT_PACK_SHOWCASE.png`.

Reason: It is visually polished and useful, but it proves "synthetic source record render" more than it proves reconciliation. It does not by itself show the product detecting anything.

### Screenshot That Should Be Featured Publicly

Feature `CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png` publicly.

Use the interactive screenshot as secondary proof if a README section wants to show the broader explorer. Use the document pack screenshot as supporting context, not the hero.

## Part E - Failure Analysis

### What Would Make This Project Fail In Public?

- A reader believes "AI document reconciliation" means OCR, live model extraction, or real document ingestion.
- A reader sees "Model confidence" and assumes model calls exist.
- A skeptical data reviewer dismisses the perfect 1.0 metrics as trivial.
- The README status makes the repo look unfinished.
- The public path leads to too many internal review documents instead of the working artifact.
- Generated document renders are mistaken for parsed inputs.
- The project is framed as production accounting, payment, tax, legal, or compliance automation.

### What Would Cause A Recruiter To Lose Trust?

- Inflated claims around AI, confidence, or reliability.
- Hiding the deterministic/synthetic nature of the baseline.
- A mismatch between README claims and generated artifacts.
- Missing or failing reproduction commands.
- Real company, supplier, bank, tax, or payment data appearing anywhere.
- The candidate being unable to explain why perfect metrics are expected.

Current trust state: The repo avoids most failure modes through explicit limitations. The remaining issues are wording/discoverability, not broken substance.

## Part F - Final Decision

**READY WITH MINOR CHANGES**

This is the correct decision because the repository works and is persuasive, but a public push should first remove small trust-framing risks:

1. Replace "Early Development" with a status that reflects a completed local portfolio demo.
2. Replace "Model confidence" with "Case confidence" or "Reliability score".
3. Make the document pack discoverable from README/evidence index if it remains part of the public story.
4. Consider aligning AGENTS.md completed-state wording with the actual finished slice state, or keep it private/out of recruiter path.

## Part G - Proof Score

| Dimension | Score |
|---|---:|
| Technical Credibility | 8 |
| Reproducibility | 9 |
| Demonstration Quality | 8 |
| Recruiter Appeal | 8 |
| Trustworthiness | 8 |
| Overall | 8.2 |

## Part H - Recommended Next Action

Recommended next action: **make minor trust-framing changes, then push publicly.**

Justification: The implementation validates. The reviewer validates. The tests pass. The portfolio signal is already strong. The only issues likely to reduce public trust are wording and first-path curation. These are small changes with high recruiter payoff and low engineering risk.

If choosing only one change before push: rename "Model confidence" to "Case confidence" or "Reliability score" everywhere visible in the reviewer/screenshot path, because it directly removes the most obvious claim/implementation tension.

## Validation Evidence

Read and inspected:

- `README.md`
- `AGENTS.md`
- `docs/plans/CROSSWISE_PROJECT_SYNTHESIS_AND_FOUNDATION_v1.0.md`
- `docs/plans/CROSSWISE_SLICE_0_TECHNICAL_CONTRACT_AND_SYSTEM_SPECIFICATION_v1.0.md`
- `docs/evidence/INDEX.md`
- `docs/evidence/CROSSWISE_LOCAL_EVIDENCE_REPORT_v1.0.md`
- Slice 1-10 evidence documents
- `docs/evidence/crosswise_reviewer_v1_0.html`
- `docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png`
- `docs/evidence/CROSSWISE_REVIEWER_INTERACTIVE_SHOWCASE.png`
- `docs/evidence/CROSSWISE_DOCUMENT_PACK_SHOWCASE.png`
- `docs/evidence/documents/invoice.html`
- `docs/evidence/documents/purchase_order.html`
- `docs/evidence/documents/receipt.html`
- `docs/reviews/CROSSWISE_FINAL_PORTFOLIO_REVIEW_AND_PRESENTATION_AUDIT_v1.0.md`
- `docs/reviews/CROSSWISE_FUTURE_PHASE_VALUE_REVIEW_v1.0.md`

Validation command result:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
88 passed in 5.68s
```

No branch, commit, push, tag, or git staging action was performed.
