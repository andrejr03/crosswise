# Crosswise Slice 0 Technical Contract and System Specification (v1.0)

## 1. Status and Purpose

This document is a technical contract and system specification for Slice 0 of Crosswise. It is not an implementation plan, not source code, not a repository migration, and not an authorization to build runtime behavior.

Crosswise is the fixed project name and approved project direction. The product direction is not reopened here.

This document supersedes earlier project-selection and comparison material for all Slice 0 technical decisions. Historical exploration documents may still explain where ideas came from, but this contract is the controlling reference for the first implementation slice.

The existing visual prototype is preserved as a separate artifact at `assets/prototypes/crosswise-prototype.zip`. Slice 0 does not extract, modify, regenerate, or depend on the prototype ZIP.

Primary source of truth used for this contract:

- `docs/plans/CROSSWISE_PROJECT_SYNTHESIS_AND_FOUNDATION_v1.0.md`

Slice 0 freezes the decisions required before implementation begins:

- synthetic-only data boundaries;
- required record concepts and validation expectations;
- v1 discrepancy labels;
- matching and reconciliation responsibilities;
- confidence and review-routing semantics;
- offline fixture and evaluation requirements;
- future repository architecture expectations.

## 2. Product Definition

Crosswise is an AI document-reconciliation project that transforms synthetic business documents into structured, typed records, reconciles invoices, purchase orders, and receipts line by line, detects discrepancies and suspicious cases, measures field-level reliability, provides evidence-backed matching decisions, and routes uncertain cases to human review.

The first vertical is invoice / purchase order / receipt reconciliation for synthetic procurement-style document bundles. Each bundle represents one intended commercial transaction or related transaction group containing supplier records, SKU records, one purchase order, one invoice, one receipt, their line items, generated ground truth, and one or more discrepancy labels.

The core public thesis is: Crosswise demonstrates an AI/data product that does not merely "use AI on documents"; it proves reliability field by field, reconciles operational records line by line, exposes evidence for every flagged case, and keeps uncertain or risky outcomes in a human-review workflow. The strongest technical signal is the combination of operational usefulness, typed data modeling, measurable evaluation, and honest scope control.

Crosswise is not:

- an accounting system;
- a tax system;
- a legal, financial, payment, or compliance advisor;
- an autonomous payment approval system;
- a production accounts-payable platform;
- an OCR project in Slice 0;
- a real-company-data ingestion system;
- a generic document-chat tool;
- a fact-checking, attestation, or verification authority;
- a forecasting, support-ticket, CRM, or non-reconciliation product.

## 3. Slice 0 Scope

### In Scope for Slice 0

Slice 0 includes only this technical contract and system specification. It defines the future implementation boundaries for:

- synthetic document bundle concepts;
- supplier, SKU, purchase order, invoice, receipt, field, evidence, reconciliation, review, and evaluation record contracts;
- v1 discrepancy taxonomy;
- deterministic-first matching and reconciliation behavior;
- confidence and review-routing semantics;
- evaluation metric definitions;
- offline fixture and testing expectations;
- future repository architecture expectations;
- future public demo target.

### Out of Scope for Slice 0

Slice 0 excludes all runtime delivery and all application behavior:

- no code implementation;
- no Streamlit app;
- no OCR;
- no live APIs;
- no model calls;
- no real invoices;
- no real company data;
- no PII;
- no deployment;
- no autonomous actions;
- no tests;
- no generated datasets;
- no README, license, packaging, or module scaffolding;
- no extraction or modification of `assets/prototypes/crosswise-prototype.zip`.

### Deferred but Allowed Later

The following are allowed in later slices only if they remain synthetic-first, offline-testable, and human-review-oriented:

- synthetic data generator;
- JSON or CSV fixture generation;
- schema implementation;
- extraction adapter contracts;
- recorded extraction fixtures;
- reconciliation engine;
- confidence scoring implementation;
- evaluation scripts;
- report generation;
- Streamlit or other local review UI;
- optional PDF-like rendering for synthetic documents;
- optional licensed public benchmark documents after explicit license review;
- optional fuzzy matching library after deterministic behavior is defined;
- optional model provider integration behind recorded offline fixtures.

### Explicitly Prohibited

The following are prohibited for Slice 0 and must not be introduced by later slices without a separate written policy decision:

- real invoices, receipts, purchase orders, or customer documents;
- real supplier, customer, employee, address, bank, tax, or payment data;
- PII;
- production accounting decisions;
- accounting, tax, legal, financial, payment, or compliance advice;
- autonomous approvals, payment initiation, supplier contact, email sending, or ledger posting;
- scraping private systems;
- committing secrets, API keys, tokens, account credentials, or live responses containing private data;
- representing Crosswise output as authoritative business truth without human review.

## 4. Synthetic Data Contract

Slice 0 requires a synthetic-only data strategy. All future implementation slices must generate or use artificial records created for Crosswise. No real entities, real documents, real companies, real people, real addresses, real bank details, real tax identifiers, or real payment information may appear in fixtures, examples, screenshots, test data, or committed evidence.

### Document Bundle Concept

A document bundle is the core synthetic unit. It groups the records needed to reconcile one procurement transaction or controlled exception scenario:

- supplier record;
- SKU records;
- purchase order;
- purchase order lines;
- invoice;
- invoice lines;
- receipt;
- receipt lines;
- generated ground truth;
- discrepancy labels;
- expected reconciliation outcome;
- fixture version and deterministic seed.

Each bundle must be independently understandable and reproducible from its declared seed and generator version.

### Supplier Records

Supplier records define synthetic counterparties used across purchase orders, invoices, and receipts. They must support canonical names and controlled aliases so supplier matching can test exact and fuzzy cases without using real company data.

Required supplier strategy:

- synthetic canonical supplier names;
- synthetic supplier IDs;
- optional alias list for spelling, punctuation, abbreviation, or formatting variants;
- explicit prohibition on real business names;
- stable generation under the deterministic seed.

### SKU Records

SKU records define synthetic products or materials. They support line-item matching and controlled mismatches.

Required SKU strategy:

- synthetic SKU IDs;
- synthetic product names;
- optional unit of measure;
- optional category;
- optional allowed aliases;
- no real branded product names unless clearly fictionalized;
- stable generation under the deterministic seed.

### Purchase Orders

Purchase orders represent the buyer's requested items. They are the intended baseline for invoice and receipt comparison.

Required PO strategy:

- synthetic PO ID;
- supplier reference;
- issue date;
- currency;
- one or more purchase order lines;
- generated totals derived from lines;
- optional expected receipt date.

### Purchase Order Lines

Purchase order lines represent requested SKU, quantity, unit price, and line total.

Required PO line strategy:

- synthetic line ID;
- SKU reference;
- quantity;
- unit price;
- line total;
- unit of measure where relevant;
- deterministic ordering.

### Invoices

Invoices represent supplier billing records to reconcile against the purchase order and receipt.

Required invoice strategy:

- synthetic invoice ID;
- supplier reference or supplier alias;
- invoice date;
- due date only if needed for examples;
- currency;
- one or more invoice lines;
- generated totals;
- optional duplicate invoice relationships.

### Invoice Lines

Invoice lines represent billed items. They are the main location for quantity, unit price, missing line, duplicate, and SKU mismatch scenarios.

Required invoice line strategy:

- synthetic line ID;
- SKU reference or controlled SKU alias;
- billed quantity;
- unit price;
- line total;
- optional source field evidence in later slices;
- deterministic ordering.

### Receipts

Receipts represent delivery or receiving confirmation. They verify whether ordered or invoiced goods were received.

Required receipt strategy:

- synthetic receipt ID;
- supplier reference or alias;
- receipt date;
- currency only if useful for cross-document consistency;
- one or more receipt lines;
- optional expected receipt reference.

### Receipt Lines

Receipt lines represent delivered quantities. They support missing receipt line, late receipt, and quantity mismatch evaluation.

Required receipt line strategy:

- synthetic line ID;
- SKU reference or alias;
- received quantity;
- receipt date when line-level dates differ;
- optional condition/status if later needed;
- deterministic ordering.

### Generated Ground Truth

Ground truth is generated alongside synthetic data. It is the authoritative answer key for evaluation and must not be inferred after reconciliation.

Ground truth must include:

- canonical field values;
- normalized field values where applicable;
- expected document-level matches;
- expected line-level matches;
- expected discrepancy labels;
- expected review-routing class;
- expected severity default;
- fixture seed and generator version;
- explanation fields sufficient for false-positive and false-negative analysis.

### Discrepancy Labels

Each bundle may have zero, one, or multiple discrepancy labels. The clean baseline is represented by `clean_match`.

Label requirements:

- labels must come from the frozen v1 taxonomy in Section 6;
- each non-clean label must identify affected document IDs and line IDs when line-level;
- each label must include expected evidence references;
- labels must be generated intentionally, not discovered accidentally;
- labels must be versioned with the fixture.

### Versioned Fixtures

Fixtures must be versioned so later regressions can be explained. A fixture version identifies the data contract and expected outputs, not merely a filename.

Minimum fixture metadata:

- fixture version;
- generator version;
- deterministic seed;
- scenario name;
- created date or generated-at metadata;
- schema contract version;
- discrepancy taxonomy version.

### Deterministic Seed Requirement

Synthetic generation must be deterministic. Given the same generator version, fixture version, and seed, the same bundle contents and ground truth must be produced. Randomness without recorded seed is not allowed.

### No Real Entities

All names, IDs, addresses, emails, SKUs, product names, and document references must be fictional or mechanically synthetic. Real-world company names, real customer names, real supplier names, real tax identifiers, real bank accounts, real payment references, real email addresses, and real addresses are prohibited.

## 5. Document and Record Schemas

This section defines implementation-ready schema specifications in prose and tables. It does not prescribe a programming language, data validation library, or storage format.

Common schema rules across all records:

- IDs must be stable strings unique within their record type and fixture.
- Dates must use ISO calendar date semantics.
- Currency values must use a consistent ISO-style currency code such as `EUR`.
- Monetary amounts must be decimal values with explicit rounding behavior in implementation.
- Quantities must be numeric and non-negative unless a later return/credit scenario explicitly permits negative values.
- Required fields must be present and non-null.
- Optional fields may be absent, but if present they must pass type and domain validation.
- All records must carry enough references to support evidence-based reconciliation.

### Supplier

Purpose: Represents a synthetic supplier or counterparty used by purchase orders, invoices, and receipts.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| supplier_id | Yes | Stable synthetic supplier identifier | Unique within fixture; non-empty | `sup_001` |
| canonical_name | Yes | Canonical synthetic supplier name | Non-empty; not a real company | `Northstar Components Ltd` |
| aliases | No | Alternative synthetic names | List of non-empty strings; no real entities | `Northstar Components`, `N. Components` |
| country_code | No | Synthetic country context | Two-letter code if present | `DE` |
| tax_region | No | Broad synthetic tax region label | Must not contain real tax ID | `EU_SYNTHETIC` |
| metadata | No | Non-critical scenario notes | Must not contain PII | `alias_test_case` |

Validation rules:

- `supplier_id` must be unique.
- `canonical_name` must not match known real entities used intentionally.
- Aliases must not duplicate the canonical name after normalization unless used to test exact-match behavior.
- No tax ID, bank account, contact person, real email, or real address is allowed.

### SKU

Purpose: Represents a synthetic product or material used for line-item matching.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| sku_id | Yes | Stable synthetic SKU identifier | Unique within fixture; non-empty | `sku_0042` |
| canonical_name | Yes | Canonical synthetic item name | Non-empty; fictionalized | `Modular sensor bracket` |
| aliases | No | Alternative names or abbreviations | List of non-empty strings | `sensor bracket`, `mod bracket` |
| unit_of_measure | Yes | Unit for quantities | Controlled vocabulary | `each` |
| category | No | Synthetic grouping | Non-empty if present | `hardware` |
| standard_unit_price | No | Reference price for generation | Non-negative decimal | `12.50` |

Validation rules:

- `sku_id` must be unique.
- `unit_of_measure` must be consistent across related PO, invoice, and receipt lines unless a mismatch scenario explicitly tests conversion or invalid data.
- Product names must not use real branded products.
- If `standard_unit_price` is present, it must be non-negative.

### PurchaseOrder

Purpose: Represents the buyer's requested order and expected baseline for reconciliation.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| purchase_order_id | Yes | Stable PO identifier | Unique within fixture | `po_2026_0007` |
| bundle_id | Yes | Owning document bundle | Must reference a valid bundle | `bundle_clean_001` |
| supplier_id | Yes | Canonical supplier reference | Must reference Supplier | `sup_001` |
| issue_date | Yes | PO issue date | ISO date | `2026-02-10` |
| expected_receipt_date | No | Expected receipt date | ISO date; on or after issue date | `2026-02-17` |
| currency | Yes | Currency code | Consistent across monetary lines | `EUR` |
| status | No | Synthetic PO status | Controlled value if present | `issued` |
| line_ids | Yes | Related PO line IDs | Non-empty list | `po_line_001`, `po_line_002` |
| subtotal | Yes | Sum of line totals before tax | Non-negative decimal | `250.00` |
| tax_amount | No | Synthetic tax amount | Non-negative decimal; non-advisory | `47.50` |
| total_amount | Yes | Synthetic total | Must match subtotal plus allowed additions | `297.50` |

Validation rules:

- `line_ids` must reference existing PurchaseOrderLine records for the same PO.
- `subtotal` must equal the sum of PO line totals within rounding tolerance.
- `total_amount` must be arithmetically consistent with available subtotal and tax fields.
- The record must not imply tax correctness or advice.

### PurchaseOrderLine

Purpose: Represents one requested line item in a purchase order.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| po_line_id | Yes | Stable PO line identifier | Unique within fixture | `po_line_001` |
| purchase_order_id | Yes | Parent PO reference | Must reference PurchaseOrder | `po_2026_0007` |
| line_number | Yes | Human-readable order | Positive integer; unique within PO | `1` |
| sku_id | Yes | Requested SKU | Must reference SKU | `sku_0042` |
| description | No | Display description | Synthetic; may vary from SKU name | `Modular sensor bracket` |
| quantity_ordered | Yes | Ordered quantity | Positive decimal | `20` |
| unit_of_measure | Yes | Unit of measure | Must align with SKU unless scenario says otherwise | `each` |
| unit_price | Yes | Ordered unit price | Non-negative decimal | `12.50` |
| line_total | Yes | Quantity times unit price | Must match within rounding tolerance | `250.00` |

Validation rules:

- `quantity_ordered` must be greater than zero.
- `line_total` must equal `quantity_ordered * unit_price` within rounding tolerance.
- `line_number` must be unique within the parent purchase order.

### Invoice

Purpose: Represents a synthetic supplier invoice to reconcile against PO and receipt records.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| invoice_id | Yes | Stable invoice identifier | Unique within fixture unless duplicate scenario links records | `inv_2026_0007_a` |
| bundle_id | Yes | Owning document bundle | Must reference DocumentBundle | `bundle_price_001` |
| supplier_id | No | Canonical supplier reference when known | Must reference Supplier if present | `sup_001` |
| supplier_name_raw | Yes | Supplier name as extracted or rendered | Synthetic; may be alias | `N. Components` |
| invoice_number | Yes | Display invoice number | Unique unless duplicate scenario | `INV-7001` |
| invoice_date | Yes | Invoice issue date | ISO date | `2026-02-12` |
| due_date | No | Synthetic due date | ISO date; on or after invoice date | `2026-03-13` |
| currency | Yes | Currency code | Must be consistent with invoice lines | `EUR` |
| line_ids | Yes | Related invoice line IDs | Non-empty list | `inv_line_001` |
| subtotal | Yes | Sum of invoice line totals | Non-negative decimal | `260.00` |
| tax_amount | No | Synthetic tax amount | Non-negative decimal; non-advisory | `49.40` |
| total_amount | Yes | Synthetic total | Must be arithmetically consistent | `309.40` |
| duplicate_of_invoice_id | No | Duplicate relationship | Must reference another invoice if present | `inv_2026_0007_original` |

Validation rules:

- `supplier_id` or a resolvable `supplier_name_raw` must be present.
- `line_ids` must reference InvoiceLine records for the same invoice.
- Duplicate invoice scenarios must be explicit in ground truth.
- Totals must match line totals within rounding tolerance.

### InvoiceLine

Purpose: Represents one billed line item on an invoice.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| invoice_line_id | Yes | Stable invoice line identifier | Unique within fixture | `inv_line_001` |
| invoice_id | Yes | Parent invoice reference | Must reference Invoice | `inv_2026_0007_a` |
| line_number | Yes | Human-readable order | Positive integer; unique within invoice | `1` |
| sku_id | No | Canonical SKU if known | Must reference SKU if present | `sku_0042` |
| sku_raw | Yes | Raw displayed SKU or item text | Synthetic | `sensor bracket` |
| description | No | Display description | Synthetic | `Sensor mounting bracket` |
| quantity_billed | Yes | Billed quantity | Positive decimal | `20` |
| unit_of_measure | Yes | Unit of measure | Controlled vocabulary | `each` |
| unit_price | Yes | Billed unit price | Non-negative decimal | `13.00` |
| line_total | Yes | Quantity times unit price | Must match within rounding tolerance | `260.00` |

Validation rules:

- `sku_id` may be absent only when extraction or matching uncertainty is intentional.
- `sku_raw` must be present to support evidence and fuzzy matching.
- `line_total` must equal `quantity_billed * unit_price` within rounding tolerance unless the fixture intentionally tests schema failure.

### Receipt

Purpose: Represents synthetic goods receipt or delivery confirmation.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| receipt_id | Yes | Stable receipt identifier | Unique within fixture | `rcpt_2026_0007` |
| bundle_id | Yes | Owning document bundle | Must reference DocumentBundle | `bundle_late_001` |
| supplier_id | No | Canonical supplier reference when known | Must reference Supplier if present | `sup_001` |
| supplier_name_raw | No | Supplier text on receipt | Synthetic; may be alias | `Northstar Components` |
| receipt_number | Yes | Display receipt number | Unique within fixture | `GR-7001` |
| receipt_date | Yes | Receipt date | ISO date | `2026-02-20` |
| related_purchase_order_id | No | Linked PO if available | Must reference PurchaseOrder | `po_2026_0007` |
| line_ids | Yes | Related receipt line IDs | Non-empty list | `rcpt_line_001` |

Validation rules:

- `line_ids` must reference ReceiptLine records for the same receipt.
- `receipt_date` may be later than expected date in late receipt scenarios.
- Supplier fields must remain synthetic.

### ReceiptLine

Purpose: Represents one received line item.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| receipt_line_id | Yes | Stable receipt line identifier | Unique within fixture | `rcpt_line_001` |
| receipt_id | Yes | Parent receipt reference | Must reference Receipt | `rcpt_2026_0007` |
| line_number | Yes | Human-readable order | Positive integer; unique within receipt | `1` |
| sku_id | No | Canonical SKU if known | Must reference SKU if present | `sku_0042` |
| sku_raw | Yes | Raw receipt item text | Synthetic | `mod sensor bracket` |
| quantity_received | Yes | Received quantity | Non-negative decimal | `18` |
| unit_of_measure | Yes | Unit of measure | Controlled vocabulary | `each` |
| received_date | No | Line-specific received date | ISO date if present | `2026-02-20` |

Validation rules:

- `quantity_received` may be zero only for explicit edge-case fixtures.
- If `received_date` is absent, the parent `receipt_date` is used.
- Missing receipt line scenarios must omit or alter a receipt line intentionally and label it in ground truth.

### DocumentBundle

Purpose: Groups all records and ground truth for one synthetic reconciliation scenario.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| bundle_id | Yes | Stable bundle identifier | Unique across fixture set | `bundle_quantity_001` |
| fixture_version | Yes | Fixture contract version | Non-empty semantic or dated version | `v1.0` |
| generator_version | Yes | Generator version | Non-empty | `generator_v1` |
| seed | Yes | Deterministic generation seed | Recorded string or integer | `42017` |
| scenario_name | Yes | Human-readable scenario | Non-empty | `quantity mismatch on received goods` |
| supplier_id | Yes | Main supplier reference | Must reference Supplier | `sup_001` |
| purchase_order_id | Yes | PO reference | Must reference PurchaseOrder | `po_2026_0007` |
| invoice_ids | Yes | Invoice references | Non-empty list | `inv_2026_0007_a` |
| receipt_ids | Yes | Receipt references | Non-empty list unless scenario explicitly lacks receipt | `rcpt_2026_0007` |
| discrepancy_labels | Yes | Expected labels | Must use v1 taxonomy | `quantity_mismatch` |
| expected_route | Yes | Expected routing class | `auto_accept`, `needs_review`, or `blocked` | `needs_review` |

Validation rules:

- All referenced records must exist in the same fixture set.
- `clean_match` must not appear with contradictory non-clean labels unless a future multi-label policy explicitly allows it.
- The bundle must be reproducible from `generator_version` and `seed`.

### ExtractedField

Purpose: Represents a field extracted from a document, including normalized value, confidence, and evidence references.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| extracted_field_id | Yes | Stable extracted field ID | Unique within extraction fixture | `field_inv_001_total` |
| source_document_id | Yes | Source document reference | Must reference PO, invoice, receipt, or rendered synthetic document | `inv_2026_0007_a` |
| record_id | Yes | Target record reference | Must reference extracted record | `inv_line_001` |
| field_name | Yes | Target schema field | Must be known for record type | `unit_price` |
| raw_value | No | Raw extracted value | May be absent if field missing | `13,00 EUR` |
| normalized_value | No | Parsed canonical value | Required when extraction succeeds | `13.00` |
| value_type | Yes | Field type | Controlled value | `money` |
| confidence_score | Yes | Confidence assigned by Crosswise confidence layer | Range 0.0 to 1.0 | `0.87` |
| evidence_ids | Yes | Evidence references | Non-empty unless unavailable is explicit | `evidence_001` |
| extraction_variant | No | Recorded extraction fixture variant | Non-empty if present | `recorded_baseline_v1` |

Validation rules:

- `confidence_score` must be between 0.0 and 1.0.
- Missing fields must be represented explicitly when needed for coverage metrics.
- `normalized_value` must match `value_type` parsing rules.
- Confidence must not be copied blindly from a model self-report.

### FieldEvidence

Purpose: Captures the source-to-record support for an extracted or reconciled field.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| evidence_id | Yes | Stable evidence identifier | Unique within fixture | `evidence_001` |
| source_document_id | Yes | Source document reference | Must exist | `inv_2026_0007_a` |
| field_name | Yes | Field supported by evidence | Non-empty | `unit_price` |
| evidence_type | Yes | Type of evidence | Controlled value | `synthetic_cell`, `text_span`, `line_reference` |
| locator | No | Human-readable location | Must not require OCR in Slice 0 | `invoice line 1 unit price` |
| observed_text | No | Source text snippet | Synthetic only | `13.00 EUR` |
| normalized_observed_value | No | Parsed value | Must match field type if present | `13.00` |
| reliability_note | No | Explanation of evidence quality | Non-empty if present | `exact synthetic line reference` |

Validation rules:

- Evidence must refer to synthetic source material only.
- `observed_text` must not contain PII or real company data.
- If evidence is unavailable, the linked field or case must explain why.

### ReconciliationCase

Purpose: Represents the result of matching and comparing records within one document bundle.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| case_id | Yes | Stable reconciliation case ID | Unique within fixture | `case_bundle_quantity_001` |
| bundle_id | Yes | Bundle reference | Must reference DocumentBundle | `bundle_quantity_001` |
| matched_supplier_id | No | Resolved supplier | Must reference Supplier if present | `sup_001` |
| purchase_order_id | Yes | PO reference | Must reference PurchaseOrder | `po_2026_0007` |
| invoice_ids | Yes | Invoice references | Non-empty list | `inv_2026_0007_a` |
| receipt_ids | Yes | Receipt references | May be empty only for expected missing receipt cases | `rcpt_2026_0007` |
| line_matches | Yes | Line-level match summaries | Non-empty list unless blocked before line matching | `po_line_001 -> inv_line_001 -> rcpt_line_001` |
| discrepancy_labels | Yes | Detected labels | Must use v1 taxonomy | `quantity_mismatch` |
| severity | Yes | Operational severity | Controlled value | `medium` |
| confidence_score | Yes | Case confidence | Range 0.0 to 1.0 | `0.72` |
| route | Yes | Review route | `auto_accept`, `needs_review`, or `blocked` | `needs_review` |
| evidence_ids | Yes | Evidence references | Non-empty for all non-clean cases | `evidence_001`, `evidence_002` |
| explanation | Yes | Human-readable rationale | Non-empty | `Invoice quantity exceeds received quantity.` |

Validation rules:

- Non-clean cases must include evidence.
- `route` must follow confidence and blocked-case rules.
- Severity and confidence must be stored separately.
- A case with schema validation failure may be blocked before full matching.

### DiscrepancyLabel

Purpose: Represents a ground-truth or detected discrepancy classification.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| label_id | Yes | Stable label instance ID | Unique within fixture | `label_001` |
| label_type | Yes | Discrepancy type | Must use v1 taxonomy | `unit_price_mismatch` |
| bundle_id | Yes | Owning bundle | Must reference DocumentBundle | `bundle_price_001` |
| affected_document_ids | Yes | Related documents | Non-empty for non-clean labels | `po_2026_0007`, `inv_2026_0007_a` |
| affected_line_ids | No | Related line IDs | Required for line-level discrepancies | `po_line_001`, `inv_line_001` |
| severity_default | Yes | Default severity | Controlled value | `medium` |
| expected_evidence | Yes | Evidence expected for correct detection | Non-empty for non-clean labels | `unit price differs between PO and invoice` |
| v1_requirement | Yes | Required or optional status | `required_v1` or `optional_deferred` | `required_v1` |

Validation rules:

- `label_type` must be one of the frozen v1 labels in Section 6.
- Line-level labels must include affected line IDs.
- `clean_match` should not have affected line IDs unless used to document positive matches.

### ReviewDecision

Purpose: Represents a human review outcome for a routed reconciliation case.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| review_decision_id | Yes | Stable review decision ID | Unique within review fixture | `review_001` |
| case_id | Yes | Reconciliation case reference | Must reference ReconciliationCase | `case_bundle_quantity_001` |
| reviewer_type | Yes | Reviewer class | Controlled value, not real person | `synthetic_human_reviewer` |
| decision | Yes | Review outcome | Controlled value | `confirm_discrepancy` |
| decision_reason | Yes | Human-readable rationale | Non-empty; no advice | `Received quantity is lower than invoiced quantity.` |
| reviewed_at | No | Synthetic review timestamp | ISO-like timestamp if present | `2026-02-21T10:00:00Z` |
| overrides_route | No | Whether route was changed | Boolean | `false` |

Validation rules:

- Review decisions must not approve payment, accounting treatment, tax treatment, or legal action.
- Reviewer identity must be synthetic or role-based, not a real person.
- Decision vocabulary must support evaluation of routing outcomes.

### EvaluationResult

Purpose: Stores metric outputs for extraction, reconciliation, routing, and reproducibility checks.

| Field | Required | Description | Constraints | Example |
|---|---:|---|---|---|
| evaluation_id | Yes | Stable evaluation result ID | Unique per run | `eval_v1_fixture_2026_02_21` |
| fixture_version | Yes | Evaluated fixture version | Must match fixture metadata | `v1.0` |
| run_id | Yes | Evaluation run identifier | Non-empty | `local_offline_run_001` |
| evaluated_at | No | Synthetic or real run timestamp | Must not contain secrets | `2026-02-21T12:00:00Z` |
| metric_name | Yes | Metric name | Must be defined in Section 9 | `discrepancy_precision_by_type` |
| metric_value | Yes | Numeric or structured metric value | Must match metric type | `0.91` |
| metric_scope | Yes | Scope of metric | Field, label type, bundle, or full fixture | `unit_price_mismatch` |
| sample_count | Yes | Number of evaluated items | Non-negative integer | `50` |
| failure_examples | No | False positives or negatives | Synthetic references only | `case_bundle_price_003` |
| reproducibility_status | No | Fresh-clone status | Controlled value | `passed` |

Validation rules:

- Metric names must match the contract.
- Sample counts must be reported for interpretability.
- Failure examples must point to synthetic fixtures.
- Results must be reproducible offline.

## 6. Discrepancy Taxonomy

The v1 discrepancy label set is frozen as:

- `clean_match`
- `quantity_mismatch`
- `unit_price_mismatch`
- `missing_invoice_line`
- `missing_receipt_line`
- `duplicate_invoice`
- `supplier_alias_mismatch`
- `late_receipt`
- `low_confidence_extraction`
- `schema_validation_failure`

| Label | Definition | Detection intent | Severity default | Expected evidence | Evaluation target | V1 status |
|---|---|---|---|---|---|---|
| clean_match | PO, invoice, and receipt agree within contract tolerances. | Confirm that matching does not over-flag correct bundles. | none | Positive line matches, matching totals, valid schema. | High true-negative rate and low false-positive rate. | required_v1 |
| quantity_mismatch | Ordered, billed, or received quantity differs for a matched line. | Detect quantity disagreement across PO, invoice, and receipt. | medium | Compared quantities with document and line IDs. | Precision and recall by line-level quantity cases. | required_v1 |
| unit_price_mismatch | Unit price differs between PO and invoice for a matched SKU line. | Detect price disagreement even when quantity and SKU match. | medium | PO unit price, invoice unit price, line IDs, tolerance used. | Precision and recall by price mismatch cases. | required_v1 |
| missing_invoice_line | A PO or receipt line has no corresponding invoice line when one is expected. | Detect omitted billing lines or incomplete invoice extraction. | medium | Unmatched PO/receipt line and attempted match candidates. | Recall on intentionally omitted invoice lines. | required_v1 |
| missing_receipt_line | A PO or invoice line has no corresponding receipt line when receipt evidence is expected. | Detect missing delivery confirmation. | high | Unmatched PO/invoice line, receipt document evidence, candidate absence. | Recall on missing receipt scenarios. | required_v1 |
| duplicate_invoice | Two invoices represent the same billing event or duplicate invoice number/content. | Detect duplicate supplier billing cases. | high | Matching invoice numbers, supplier, totals, dates, or line fingerprints. | Precision on duplicate detection without over-flagging similar invoices. | required_v1 |
| supplier_alias_mismatch | Supplier names differ but may refer to the same canonical supplier through alias or fuzzy matching. | Test supplier resolution and avoid incorrect hard failures on aliases. | low | Raw supplier names, canonical supplier, alias/fuzzy rationale. | Correct resolution rate and false alias rate. | required_v1 |
| late_receipt | Receipt date is later than expected receipt date or agreed tolerance. | Detect timing exceptions without implying legal breach. | low | PO expected date, receipt date, tolerance rule. | Precision and recall on date-based exceptions. | optional_deferred |
| low_confidence_extraction | Required field exists but confidence is too low for auto-accept. | Route uncertain extraction cases to review. | medium | Field confidence, contributing factors, evidence availability. | Review-routing precision and field-level confidence calibration. | required_v1 |
| schema_validation_failure | Extracted or generated record violates required schema constraints. | Block or review invalid records before reconciliation output is trusted. | high | Failed field name, invalid value, validation rule. | Validation pass rate and correct blocked routing. | required_v1 |

Severity defaults guide review priority only. They are not financial, legal, accounting, tax, compliance, or payment advice.

## 7. Matching and Reconciliation Contract

Slice 0 defines matching responsibilities and evidence requirements but does not implement algorithms and does not select final libraries.

### Deterministic Matching Rules

Future implementation must attempt deterministic matching before fuzzy fallback.

Required deterministic inputs:

- supplier ID when available;
- purchase order ID;
- invoice number where duplicate detection is relevant;
- receipt ID or receipt-to-PO reference when available;
- SKU ID;
- line number only as supporting evidence, not as the sole match key;
- quantity, unit of measure, unit price, and totals for validation checks.

Deterministic matching must produce explicit match outcomes:

- exact document match;
- exact line match;
- unmatched record;
- duplicate candidate;
- invalid record blocked before matching.

### Fuzzy Fallback Intent

Fuzzy matching is allowed only as fallback when deterministic keys are absent, aliased, or intentionally varied by fixture design.

Fuzzy fallback may consider:

- supplier aliases;
- normalized supplier names;
- SKU aliases;
- normalized SKU descriptions;
- line amount similarity;
- line quantity and unit-of-measure compatibility;
- date proximity;
- document total consistency.

Fuzzy fallback must produce an explanation and evidence. It must not silently convert uncertain matches into clean matches.

### Supplier Alias Handling

Supplier matching must use canonical supplier IDs when present. If only supplier names are available, matching must normalize names and compare against allowed synthetic aliases.

Rules:

- exact canonical supplier match is strongest;
- known alias match is acceptable evidence;
- fuzzy supplier match must lower confidence unless corroborated by document and line evidence;
- conflicting supplier evidence should route to review or block depending on severity and schema validity;
- no real supplier lookup is allowed.

### SKU Matching

SKU matching must prioritize `sku_id`. If `sku_id` is absent, matching may use `sku_raw`, aliases, descriptions, unit of measure, and price/quantity context.

Rules:

- exact SKU ID match supports deterministic line matching;
- alias match supports reviewable or accepted match depending on confidence and other evidence;
- different units of measure must not be treated as equivalent unless a later explicit conversion contract is written;
- ambiguous SKU matches must route to review.

### Line-Item Matching

Line-item matching compares PO lines, invoice lines, and receipt lines.

Expected line matching output:

- matched PO line ID;
- matched invoice line ID or missing invoice line;
- matched receipt line ID or missing receipt line;
- matching basis;
- discrepancy labels;
- evidence references;
- confidence score;
- review route contribution.

Line-item matching must not rely on line number alone. Line number can support a match only when supplier, document, SKU, and value evidence are compatible.

### Document-Level Matching

Document-level matching links purchase orders, invoices, and receipts within a bundle.

Required document-level checks:

- supplier consistency;
- purchase order reference consistency where present;
- invoice duplicate checks;
- receipt relationship to PO where present;
- date consistency;
- currency consistency;
- total consistency;
- schema validity.

### Evidence Requirements

Every non-clean detected discrepancy must include evidence references sufficient for a human reviewer to understand the case without trusting a black-box model.

Minimum evidence for a discrepancy:

- affected document IDs;
- affected line IDs when line-level;
- compared field names;
- observed values;
- normalized values when applicable;
- rule or matching basis;
- confidence score and route;
- concise explanation.

### Blocked and Reviewable Case Rules

A case must be blocked when:

- required schema fields are missing or invalid in a way that prevents trustworthy reconciliation;
- document identity is ambiguous across multiple candidates;
- supplier conflict cannot be resolved;
- evidence is absent for a non-clean severe discrepancy;
- fixture or extraction data violates synthetic-only policy.

A case must be reviewable when:

- fuzzy matching is used without enough corroborating evidence for auto-accept;
- extraction confidence is below the auto-accept threshold but not invalid;
- severity is medium or high and the evidence is present but not decisive;
- duplicate detection is plausible but not deterministic;
- supplier alias resolution is plausible but uncertain.

## 8. Confidence and Review Routing Contract

Confidence represents the system's estimated reliability of a field, line match, document match, or reconciliation case. It is not severity, not financial impact, not legal certainty, not model certainty alone, and not permission to take autonomous action.

Confidence score range:

- minimum: `0.0`
- maximum: `1.0`
- higher means more reliable under the Crosswise evidence and validation contract

Confidence must not rely only on a model self-reported score. Any model-reported confidence, if available later, is only one possible weak input.

Minimum contributing factors for confidence:

- schema validity;
- required field presence;
- deterministic validation checks;
- evidence availability and specificity;
- consistency across related documents;
- consistency across fixtures or extraction variants when recorded variants exist;
- normalized value agreement;
- historical field-level accuracy by field type;
- known ambiguity from fuzzy matching;
- discrepancy type and route history from offline evaluation.

### Schema Validity

Invalid schema records reduce confidence. Critical schema failures can force a blocked route regardless of other signals.

### Field Presence

Required fields that are missing reduce confidence and may trigger `low_confidence_extraction` or `schema_validation_failure`.

### Deterministic Validation Checks

Checks such as line total arithmetic, currency consistency, date ordering, quantity non-negativity, and reference integrity contribute to confidence. Passing checks increases reliability; failing checks lowers confidence or blocks the case.

### Evidence Availability

Confidence must consider whether there is source evidence for the field or case. A value with no evidence should not be auto-accepted.

### Consistency Across Fixtures or Extraction Variants

If multiple recorded extraction variants are used later, consistent values across variants may increase confidence. Conflicting variants must lower confidence or route to review.

### Historical Field-Level Accuracy by Field Type

Confidence must consider measured accuracy by field type from offline evaluation. For example, a field type with historically poor normalized accuracy should not receive high confidence solely because one extraction looks plausible.

### Routing Threshold Concepts

Final threshold values are implementation decisions for later slices, but the conceptual classes are fixed:

- `auto_accept`: confidence and validation are high enough for a clean or low-risk case to pass without manual review in the demo workflow.
- `needs_review`: evidence exists, but confidence, severity, fuzzy matching, or discrepancy type requires human inspection.
- `blocked`: schema validity, identity ambiguity, missing evidence, or policy violation prevents trustworthy reconciliation.

Auto-accept never means autonomous payment, accounting, legal, tax, or financial action. It means only that the synthetic demo workflow can mark a case as not needing review.

### Confidence Versus Severity

Confidence and severity are separate:

- confidence estimates reliability of the system's interpretation;
- severity estimates operational importance of the detected issue.

Examples:

- A high-confidence duplicate invoice may have high severity and route to review or blocked.
- A low-confidence supplier alias match may have low severity but still route to review.
- A clean match can have low confidence if evidence is weak.

## 9. Evaluation Metrics Contract

Evaluation must measure both extraction quality and reconciliation quality using synthetic ground truth. Metrics must be reproducible offline and interpretable by a technical reviewer.

| Metric | Measures | Why it matters |
|---|---|---|
| field exact match accuracy | Percentage of extracted field values that exactly match ground truth without normalization. | Shows strict extraction correctness and exposes formatting sensitivity. |
| normalized field accuracy | Percentage of extracted values that match ground truth after approved normalization. | Measures practical correctness for dates, money, supplier names, SKUs, and quantities. |
| fuzzy field accuracy | Percentage of fields accepted as correct under defined fuzzy comparison rules. | Measures resilience to aliases and harmless textual variation while revealing over-permissive matching risk. |
| extraction coverage | Percentage of required fields extracted or explicitly marked missing. | Prevents high accuracy being achieved by skipping hard fields. |
| schema validation pass rate | Percentage of records passing required schema validation. | Shows whether data is structurally usable before reconciliation. |
| discrepancy precision by type | For each discrepancy label, detected true positives divided by all detections of that type. | Measures false alarm risk per discrepancy category. |
| discrepancy recall by type | For each discrepancy label, detected true positives divided by all ground-truth cases of that type. | Measures missed exception risk per discrepancy category. |
| macro-F1 | Average F1 score across discrepancy types with equal label weighting. | Prevents common easy labels from hiding weak performance on rarer labels. |
| confusion matrix | Matrix of ground-truth labels versus detected labels. | Shows which discrepancy types are confused with each other. |
| false-positive examples | Concrete synthetic cases incorrectly flagged. | Makes limitations visible and improves trust. |
| false-negative examples | Concrete synthetic cases missed by reconciliation. | Shows honest failure analysis and safety awareness. |
| review-routing precision | Percentage of cases routed to review or blocked that truly required review/blocking under ground truth. | Measures whether the review queue is useful instead of noisy. |
| fresh-clone reproducibility check | Whether a clean checkout can regenerate or evaluate fixtures offline and produce expected outputs. | Proves the project is inspectable and not dependent on hidden state or live services. |

Metric rules:

- All metrics must report sample counts.
- Per-type metrics must include label names.
- Evaluation must use generated ground truth, not manual after-the-fact interpretation.
- False-positive and false-negative examples must reference synthetic fixture IDs.
- Fresh-clone checks must not require secrets, live APIs, paid services, real documents, or network access.

## 10. Fixture and Offline Testing Contract

Future tests and CI must be offline by default. No live API calls are allowed in tests or CI for core validation.

### Fixture Types

Required fixture categories:

- generated synthetic fixtures;
- ground truth fixtures;
- recorded extraction fixtures;
- expected reconciliation outputs;
- expected evaluation outputs;
- false-positive and false-negative example fixtures where useful.

### Naming Convention

Fixture names must be predictable and scenario-oriented.

Expected naming pattern:

- synthetic bundle fixture: `bundle_<scenario>_<number>`
- ground truth fixture: `ground_truth_<fixture_version>`
- recorded extraction fixture: `extraction_<provider_or_contract>_<variant>_<fixture_version>`
- expected reconciliation output: `expected_reconciliation_<fixture_version>`
- expected evaluation output: `expected_evaluation_<fixture_version>`

Examples:

- `bundle_clean_001`
- `bundle_quantity_mismatch_001`
- `bundle_supplier_alias_001`
- `ground_truth_v1_0`
- `extraction_recorded_baseline_v1_0`
- `expected_reconciliation_v1_0`

### Generated Synthetic Fixtures

Generated synthetic fixtures must be reproducible from seed and generator version. They must contain no real entities and no PII.

### Ground Truth Fixtures

Ground truth fixtures must be generated or checked in alongside synthetic data. They must state expected canonical values, expected labels, expected matches, and expected routes.

### Recorded Extraction Fixtures

Recorded extraction fixtures represent extraction outputs captured for offline evaluation. They must be synthetic-only and must not contain secrets or live provider metadata that could expose credentials.

### Expected Outputs

Expected outputs must define what reconciliation and evaluation should produce for the fixture version. They are used for regression testing.

### No Live API Calls in Tests/CI

Tests and CI must not call live model providers, OCR services, accounting systems, email systems, payment systems, cloud APIs, or external document services. Any later provider integration must be tested through recorded synthetic fixtures by default.

### No Secrets Committed

The repository must never commit API keys, tokens, credentials, account IDs, private endpoints, real invoices, real supplier data, or real company records.

### Deterministic Test Generation

Tests must either use checked-in fixtures or generate fixtures deterministically with explicit seed and generator version.

### Regression Testing Expectations

Regression tests must fail when:

- schema validation behavior changes unexpectedly;
- deterministic fixture generation changes without version update;
- discrepancy labels regress;
- expected line matches change unexpectedly;
- evaluation metrics drop below agreed thresholds;
- live API calls are attempted in offline tests;
- synthetic-only policy is violated.

## 11. Repository Architecture Contract

This section proposes the expected repository structure for future implementation. Slice 0 does not create these files or folders except the target document path already used for this contract.

Expected future structure:

| Path | Purpose |
|---|---|
| `README.md` | Result-first project explanation, reproducible demo path, limitations, screenshots or report links. |
| `LICENSE` | License chosen before public distribution. |
| `pyproject.toml` | Python project metadata, dependencies, tooling, test commands. |
| `assets/prototypes/` | Preserved visual prototypes, including `crosswise-prototype.zip`. |
| `docs/plans/` | Planning, contracts, and implementation plans. |
| `docs/evidence/` | Checked-in evaluation reports, metric snapshots, failure examples, demo evidence. |
| `data/synthetic/` | Generated or checked-in synthetic document data. |
| `data/ground_truth/` | Ground truth records and labels for evaluation. |
| `fixtures/extractions/` | Recorded extraction outputs for offline tests. |
| `src/crosswise/` | Main package for future implementation. |
| `scripts/` | Local generation, evaluation, and report commands. |
| `tests/` | Offline unit, integration, fixture, and regression tests. |

Expected future modules under `src/crosswise/`:

| Module | Responsibility |
|---|---|
| `generation` | Deterministic synthetic supplier, SKU, PO, invoice, receipt, and ground-truth generation. |
| `schemas` | Typed record definitions and validation rules. |
| `normalization` | Supplier, SKU, date, currency, quantity, and text normalization. |
| `extraction_contract` | Provider-agnostic extraction input/output contracts and recorded fixture interfaces. |
| `matching` | Deterministic and fuzzy matching support for suppliers, documents, and lines. |
| `reconciliation` | Cross-document comparison, discrepancy detection, and case construction. |
| `evaluation` | Field metrics, discrepancy metrics, confusion matrix, and reproducibility checks. |
| `confidence` | Confidence scoring based on validation, evidence, history, and consistency. |
| `routing` | Auto-accept, needs-review, and blocked classification. |
| `reporting` | Human-readable reports, failure examples, and demo summaries. |

Architecture rules:

- Repository architecture must keep synthetic data, ground truth, recorded extraction fixtures, source code, tests, and evidence separate.
- Runtime implementation must not be hidden inside notebooks.
- The review UI, if added later, must consume the same reconciliation outputs used by tests and reports.
- The prototype ZIP remains an asset, not a source of executable logic.

## 12. Public Demo Target

The future public demo target is a short, reproducible path that shows Crosswise as a working data product. This is not Slice 0 implementation.

Target future demo flow:

1. Generate synthetic data.
2. Run reconciliation.
3. Run evaluation.
4. Inspect a report with metrics, evidence, and failure examples.
5. Run tests offline.
6. Later launch a local review UI for human inspection.

The target demo should show:

- one clean match;
- one quantity mismatch;
- one unit price mismatch;
- one supplier alias case;
- one duplicate invoice case;
- one low-confidence or schema-failure case;
- evidence for each flagged case;
- field-level and discrepancy-level metrics;
- explicit synthetic-only and non-advice statements.

The first 2-3 minutes should make the technical signal obvious: Crosswise is a finished, bounded, reproducible AI/data reconciliation project with measurable reliability and honest human-review limits.

## 13. Acceptance Criteria for Slice 0

Slice 0 is accepted when this document:

- exists at `docs/plans/CROSSWISE_SLICE_0_TECHNICAL_CONTRACT_AND_SYSTEM_SPECIFICATION_v1.0.md`;
- states that it is a technical contract, not implementation;
- fixes Crosswise name and direction;
- states that it supersedes earlier project-selection material;
- preserves the existence of `assets/prototypes/crosswise-prototype.zip` without extracting or modifying it;
- defines Crosswise, first vertical, public thesis, and non-product boundaries;
- defines in-scope, out-of-scope, deferred, and prohibited Slice 0 items;
- includes all hard Slice 0 exclusions;
- defines the synthetic data contract with deterministic seed and no-real-entities policy;
- defines all required record schemas without Python code;
- freezes the v1 discrepancy taxonomy and required/deferred status;
- defines matching and reconciliation contracts without implementing algorithms or selecting unnecessary libraries;
- defines confidence and review-routing semantics, including the rule that confidence cannot rely only on model self-report;
- defines all required evaluation metrics and why they matter;
- defines fixture and offline testing expectations with no live API calls in tests/CI;
- proposes future repository architecture without creating implementation files or folders;
- defines the future public demo target as future work, not Slice 0 implementation;
- defines inputs to Slice 1;
- includes fixed non-advice and data policy language;
- modifies no files other than this target document.

## 14. Inputs to Slice 1

Slice 1 should use this contract as the controlling input for implementation planning.

Slice 1 needs:

- synthetic data generator scope:
  - suppliers;
  - SKUs;
  - purchase orders;
  - purchase order lines;
  - invoices;
  - invoice lines;
  - receipts;
  - receipt lines;
  - document bundles;
  - deterministic ground truth;
  - controlled discrepancy injection.
- schema definitions:
  - all records listed in Section 5;
  - required/optional fields;
  - validation rules;
  - reference integrity rules.
- discrepancy taxonomy:
  - frozen v1 label names;
  - definitions;
  - default severity;
  - evidence expectations;
  - required or deferred status.
- fixture rules:
  - fixture naming;
  - deterministic seed behavior;
  - version metadata;
  - ground truth structure;
  - expected outputs;
  - recorded extraction fixture policy.
- initial validation rules:
  - required field presence;
  - ID uniqueness;
  - reference integrity;
  - date validity;
  - currency consistency;
  - non-negative quantities and monetary values;
  - line total arithmetic;
  - synthetic-only policy checks;
  - no live API calls in tests/CI.

Slice 1 should not add UI, OCR, live provider calls, real documents, deployment, autonomous actions, or advice workflows unless a later contract explicitly changes scope.

## 15. Non-Advice and Data Policy

Fixed policy language for Crosswise:

Crosswise uses synthetic-only data. It does not use real invoices, real purchase orders, real receipts, real supplier data, real customer data, real company data, real employee data, real bank data, real tax identifiers, real payment references, or PII.

Crosswise output is not accounting advice, tax advice, legal advice, financial advice, payment advice, compliance advice, or an instruction to approve, reject, pay, book, report, or dispute any transaction.

Crosswise is a human-review-only workflow. It may flag synthetic discrepancies, rank synthetic review cases, and explain evidence, but it must not perform autonomous business actions.

Crosswise must not send emails, contact suppliers, approve invoices, initiate payments, update ledgers, file tax records, create legal notices, or represent its output as authoritative business truth.

Any future use beyond synthetic portfolio data requires a separate data, privacy, security, legal, and domain review before implementation.

---

Document version: v1.0. Slice 0 technical contract only. No code, no tests, no Streamlit app, no OCR, no live APIs, no real documents, no deployment, and no autonomous actions are authorized by this document.
