# Crosswise — Project Synthesis and Foundation (v1.0)

> **Status:** Crosswise is the approved project direction. This document does **not** revisit project selection, ranking, or naming. It treats the two source files as historical exploration material and extracts only what remains strategically useful for building Crosswise.

**Source files (historical exploration):**
- `docs/plans/ANDRE_AI_DATA_SCIENCE_REMOTE_PART_TIME_PROJECT_SELECTION_v1.0.md` — origin of the **ExtractEval** direction (Claude-derived).
- `docs/plans/ANDRE_AI_DATA_SCIENCE_REMOTE_PART_TIME_PROJECT_SELECTION_v1.1.md` — origin of the **InvoiceGuard AI** direction (Codex-derived).

**Evaluation lens carried forward:** `werkstudent-recruiter` (paid-work signal, founder-readability, finishability, honest evidence).

---

# Executive Summary

Crosswise is the fusion of two complementary halves that each appeared, separately and incompletely, in the prior exploration:

- **ExtractEval** contributed the **trust layer**: document → structured records with *measured* field-level accuracy, calibrated confidence, confidence-based human routing, and an offline, regression-tested evaluation harness.
- **InvoiceGuard AI** contributed the **operational loop**: synthetic invoices/POs/receipts, line-item cross-checking across document types, discrepancy detection with severity, an exception/review queue, and an evidence-based dashboard.

Neither source on its own is a strong paid-work signal. ExtractEval risked reading as a developer library (mechanism without an operational outcome); InvoiceGuard risked reading as a vertical-specific demo (operational outcome without provable reliability). **Crosswise is exactly the bridge between them**: an operational document-reconciliation product whose every decision is backed by measurable extraction reliability and routed to human review when uncertain.

This document fixes which concepts cross over, which are discarded, and what inputs must be decided before any "Slice 0" technical contract is written. It deliberately produces **no** implementation plan, code, schemas, or repository structure.

---

# ExtractEval Contributions

Concepts that originated in the ExtractEval (v1.0) direction and are strategically useful for Crosswise:

1. **Schema-constrained extraction** — documents parsed into validated structured records (Pydantic-style typed targets) rather than free text.
2. **Field-level accuracy harness** — exact / normalized / fuzzy match scored *per field*, not just per document.
3. **Confidence calibration** — confidence scores that are *calibrated* (reliability diagram, expected calibration error), so a confidence number is trustworthy.
4. **Confidence routing** — auto-accept above a threshold; otherwise route to human review.
5. **Provider-agnostic model adapter** — never locked to one fragile/paid API; swappable backend.
6. **Offline regression testing** — versioned prompts plus recorded-response fixtures so CI runs without a live API and fails on accuracy regressions.
7. **Checked-in evidence** — accuracy results committed to the repo so a reviewer sees them without running anything.
8. **Result-first, honest-limitations framing** — lead with the accuracy table, disclose weaknesses.

---

# InvoiceGuard AI Contributions

Concepts that originated in the InvoiceGuard AI (v1.1) direction and are strategically useful for Crosswise:

1. **Synthetic business-document generation** — invoices, purchase orders, delivery receipts, suppliers, SKUs, quantities, unit prices, dates, IDs (no PII, no real company data).
2. **Controlled discrepancy injection with ground truth** — a labeled discrepancy taxonomy (quantity mismatch, unit-price mismatch, missing line item, duplicate invoice, supplier-alias mismatch, late receipt, clean match, etc.).
3. **Cross-document, line-item matching** — linking invoice ↔ PO ↔ receipt via deterministic keys with fuzzy fallback (entity resolution).
4. **Discrepancy detection + severity scoring** — separating "needs review" from "blocked," with a rule baseline plus an optional lightweight anomaly layer.
5. **Exception/review queue workflow** — ranked exceptions with drill-down and side-by-side evidence.
6. **Operational evaluation** — precision/recall/F1 and confusion matrix *by discrepancy type*, with false-positive/false-negative review.
7. **Auditable, evidence-based dashboard** — review queue, document match view, metrics, and data-lineage/no-PII statement.
8. **"Operations reconciliation, not advice" framing** — explicit non-advice (no accounting/tax/legal/financial/payment advice).
9. **Reproducibility discipline** — fresh-clone run path, test suite, synthetic-data versioning.

---

# Preserved Concepts

The concepts below become part of Crosswise. Grouped to answer the strategic identification questions directly.

**Recruiter-facing positioning to preserve**
- Operational, founder-readable pain point (messy documents → flagged mismatches → review queue).
- "Junior data product, not a notebook" maturity signal.
- Directly monetizable, scoped remote-service framing.
- Honest limitations + explicit non-advice disclaimer.
- A 3-minute, credentials-free, reproducible recruiter demo.

**Technical differentiators to preserve**
- The **fusion itself**: provable extraction reliability *inside* an operational reconciliation loop.
- Cross-document line-item matching (deterministic + fuzzy entity resolution).
- A measurable trust layer (field-level accuracy + calibrated confidence) gating operational decisions.
- Provider-agnostic model adapter (no fragile/paid-API lock-in).

**Evaluation concepts to preserve**
- Ground-truth-driven measurement end to end (extraction *and* reconciliation).
- Field-level accuracy (exact / normalized / fuzzy).
- Discrepancy-type precision/recall/F1 with confusion matrix.
- False-positive and false-negative review examples.
- Regression testing that fails on quality drops.
- Checked-in evaluation evidence.

**Confidence / reliability concepts to preserve**
- Calibrated confidence (reliability diagram, ECE).
- Severity scoring distinct from confidence ("needs review" vs "blocked").
- Confidence/severity-based routing to human review.

**Document-processing concepts to preserve**
- Schema-constrained extraction into typed, validated records.
- Normalization of supplier names, dates, currency, SKUs, line items.
- CSV/JSON as the core data path; rendered/PDF-like documents optional, not load-bearing.

**Reconciliation concepts to preserve**
- Invoice ↔ PO ↔ receipt matching at the line-item level.
- A bounded discrepancy taxonomy with ground-truth labels.
- Exception queue with side-by-side, evidence-backed drill-down.
- Audit-trail / source-to-record traceability for every flagged item.

**Testing / reproducibility concepts to preserve**
- Offline, recorded-response fixtures so CI needs no live API.
- Test suite covering generation, normalization, matching, detection, evaluation, and demo readiness.
- Fresh-clone reproduction check.
- Synthetic data + ground truth held in versioned fixtures.

**Synthetic-data concepts to preserve**
- Fully synthetic, in-repo generation with controlled discrepancy labels.
- No real company names, invoices, PII, scraping, OCR services, or paid ingestion.
- Optional licensed public benchmark documents only after license review (secondary, not required).

**Demo concepts to preserve**
- Streamlit review-queue cockpit.
- Side-by-side invoice/PO/receipt with highlighted mismatches.
- Per-field confidence color-coding (auto-accept vs review).
- Metrics/evaluation view with honest failure cases.
- A scripted, repeatable 3-minute walkthrough.

---

# Rejected Concepts

Explicitly discarded so they do not creep back into Crosswise:

- **OpsTriage AI** (support-ticket triage) and **DemandPulse AI** (demand forecasting) from v1.1 — out of scope; Crosswise is document reconciliation, not ticket triage or forecasting.
- **The "ExtractEval" name and library/CLI positioning** — rejected earlier; Crosswise is a product, not an eval library. (Name is settled; not reopened here.)
- **Invoice-only narrowness** — keep invoices/POs/receipts as the first vertical but design concepts to generalize to other line-item document reconciliation.
- **Fact-checking / verification / attestation framing** — rejected during naming; Crosswise is operational reconciliation, not fact-checking or legal attestation.
- **OCR as a core dependency** — excluded from the foundation; CSV/JSON is the spine, PDF/image rendering is optional.
- **Heavy model machinery as the headline** — no fashionable-model-as-centerpiece; the differentiator is ground truth + measurable quality, not model novelty. An anomaly model stays optional and cuttable.
- **Anything implying accounting/tax/legal/financial/payment advice** — permanently out.
- **Real PII, real invoices, scraping, email ingestion, paid APIs required to reproduce the core result** — permanently out.
- **Autonomous action** (auto-sending, auto-approving payments) — out; Crosswise assists a human reviewer only.

---

# Crosswise Core Thesis

Crosswise is an **AI document-reconciliation product** that:

1. Transforms business documents (invoices, purchase orders, receipts) into structured, typed records;
2. Cross-checks them line by line across document types;
3. Detects discrepancies and suspicious cases with severity;
4. Measures field-level extraction reliability and calibrates its own confidence;
5. Provides evidence-based, source-to-record traceability for every decision;
6. Routes uncertain cases to a human review queue.

**Why this is the right thesis (recruiter-severe):** It is the only framing in which the prior two explorations stop being a "library" and a "demo" and become a *trustworthy operational tool*. The paid-work signal is the combination — an operational outcome a founder understands in 3 minutes, backed by reliability evidence a technical reviewer can verify. That combination is rare from an 18-year-old and is the entire reason to build Crosswise rather than either source project alone.

---

# Crosswise Technical Foundation

Foundational pillars (conceptual, not an implementation plan):

- **Synthetic-data spine** — in-repo generation of supplier/SKU/PO/invoice/receipt records with injected, ground-truth-labeled discrepancies; CSV/JSON first; PDF optional.
- **Extraction + normalization layer** — schema-constrained, typed records; normalized suppliers, dates, currency, SKUs, line items.
- **Reconciliation engine** — deterministic key matching with fuzzy fallback at the line-item level across the three document types.
- **Discrepancy + severity layer** — bounded discrepancy taxonomy; rule baseline; optional, cuttable anomaly score; severity that separates review from blocked.
- **Trust layer** — field-level accuracy (exact/normalized/fuzzy), calibrated confidence (reliability diagram/ECE), confidence-based routing.
- **Evaluation harness** — ground-truth metrics for both extraction and reconciliation; discrepancy-type precision/recall/F1; false-positive/negative examples; checked-in results; regression tests.
- **Reproducibility layer** — provider-agnostic adapter; offline recorded-response fixtures; fresh-clone run path; versioned fixtures.
- **Demo surface** — Streamlit review-queue cockpit with side-by-side evidence, per-field confidence color-coding, and a metrics/failure view.

These pillars are the *what*, intentionally leaving the *how* (schemas, module layout, build order) to a later, separately authorized technical contract.

---

# Crosswise Recruiter Positioning

Positioning signals to carry into all outreach (kept consistent with the approved name and hook; not re-deriving naming):

- **Target paid roles:** remote AI automation assistant, junior AI/data science assistant, operations analytics assistant, document-AI intern, part-time Python automation developer; future Werkstudent.
- **Employer archetypes:** small e-commerce/ops teams, accounting/procurement automation startups, agencies building internal AI tools for SMEs, remote-first operations teams.
- **Core message:** "I build AI that reconciles documents line by line — flags discrepancies, queues exceptions for human review, and proves its accuracy field by field."
- **Credibility moves preserved:** result-first README with checked-in accuracy, reproducible fresh-clone demo, explicit non-advice + synthetic-data-only statement, honest limitations.
- **Monetization angle:** scoped remote service — turn a client's sample CSV exports of invoices/POs/receipts into a tested local reconciliation prototype with a review dashboard, without claiming production accounting correctness.

---

# Scope Boundaries

**In scope (v1 foundation)**
- Synthetic invoices, purchase orders, receipts (first vertical).
- Line-item cross-document reconciliation with a bounded discrepancy taxonomy.
- Field-level accuracy, calibrated confidence, confidence/severity routing.
- Ground-truth evaluation for extraction and reconciliation.
- Local Streamlit review-queue demo.
- Offline, reproducible tests.

**Out of scope (hard boundaries)**
- OCR as a required dependency; real documents; real company data/PII.
- Accounting/tax/legal/financial/payment advice or decisions.
- Autonomous actions (sending, approving, paying).
- Forecasting, ticket triage, or any non-reconciliation workflow.
- Paid APIs required to reproduce the core result; scraping; email ingestion.
- Deployment/infrastructure, accounts, billing, auth.
- Verification/fact-checking/attestation framing.

**Generalization stance**
- Build invoice/PO/receipt first, but keep concepts general enough to extend to other line-item document reconciliation later — without committing to that extension in v1.

---

# Inputs To Slice 0 Technical Contract

> These are the **decisions to freeze before** a Slice 0 technical contract is authored. This section lists inputs and open questions only — it deliberately does **not** define schemas, module structure, build order, or code.

Decisions required as inputs:

1. **Discrepancy taxonomy freeze** — confirm the exact bounded set of discrepancy types (including "clean match") and which are v1 vs deferred.
2. **Document set scope** — confirm the three document types and the synthetic volume range (portfolio-scale, e.g. a bounded number of bundles), plus whether PDF rendering is included as optional.
3. **Record/field inventory** — agree the conceptual list of fields that matter for matching and for field-level accuracy (suppliers, SKUs, quantities, unit prices, dates, IDs, line items) — as inputs, not as a schema.
4. **Ground-truth format intent** — decide that ground truth is generated alongside synthetic data and versioned; defer the concrete file format to the contract.
5. **Matching strategy inputs** — confirm deterministic-key-first with fuzzy fallback, and which fields drive each.
6. **Trust-layer metric set** — confirm field-level accuracy variants (exact/normalized/fuzzy) and calibration measures (reliability diagram/ECE) to be reported.
7. **Reconciliation metric set** — confirm discrepancy-type precision/recall/F1 + confusion matrix + false-positive/negative review.
8. **Routing policy inputs** — confirm confidence- and severity-based routing concept (auto-accept / review / blocked); defer threshold values to the contract.
9. **Reproducibility policy** — confirm provider-agnostic adapter + offline recorded-response fixtures + fresh-clone run as non-negotiable inputs.
10. **Demo storyboard** — confirm the canonical 3-minute path (one clean bundle, one severe mismatch, one fuzzy-alias case, one duplicate case, one false-positive/limitation case) as the acceptance narrative.
11. **Non-advice + data-policy statements** — confirm the synthetic-only and non-advice language as fixed inputs.
12. **Optional/cuttable elements** — confirm what is explicitly optional (anomaly model, PDF rendering, licensed public dataset) so the contract can scope-cut cleanly.

---

*Document version 1.0. Synthesis and foundation only — no implementation plan, no code, no schemas, no repository structure, no ranking revisited, no rename. Crosswise name and direction are treated as approved and fixed.*
