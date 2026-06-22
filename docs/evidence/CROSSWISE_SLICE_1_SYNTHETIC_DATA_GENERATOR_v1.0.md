# Crosswise Slice 1 Synthetic Data Generator Evidence (v1.0)

## What Was Implemented

Slice 1 implements the first runtime layer for Crosswise: a deterministic synthetic data generator for invoice, purchase order, receipt, document bundle, and ground truth fixtures.

Implemented components:

- Python project scaffold with `pyproject.toml`.
- `src/crosswise` package.
- Dataclass schema models for:
  - Supplier
  - SKU
  - PurchaseOrder
  - PurchaseOrderLine
  - Invoice
  - InvoiceLine
  - Receipt
  - ReceiptLine
  - DocumentBundle
  - DiscrepancyLabel
- Frozen discrepancy taxonomy from the Slice 0 contract.
- Deterministic generator with fixture version, generator version, and seed metadata.
- JSON fixture output under `data/synthetic/`.
- JSON ground truth output under `data/ground_truth/`.
- Local generation script at `scripts/generate_synthetic_data.py`.
- Tests for determinism, reference integrity, taxonomy validity, arithmetic validity, date validity, synthetic-only policy, and script execution.

## Generated Fixture Policy

The generator writes:

- `data/synthetic/fixtures_v1_0.json`
- `data/ground_truth/ground_truth_v1_0.json`

The fixture set is bounded and deterministic. Given the same generator version and seed, the generated supplier, SKU, purchase order, invoice, receipt, bundle, discrepancy label, and ground truth records are stable.

Generated bundles cover the frozen v1 discrepancy taxonomy:

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

`late_receipt` remains marked as optional/deferred in the taxonomy metadata, matching the Slice 0 contract, but Slice 1 still generates a safe synthetic fixture for it.

## Synthetic-Only Guarantees

The generator uses mechanically synthetic identifiers and names only. It does not generate:

- real invoices;
- real purchase orders;
- real receipts;
- real company names;
- real people;
- real addresses;
- email addresses;
- bank or payment data;
- tax identifiers;
- PII.

The tests scan generated payloads for known forbidden entity and payment-related strings.

## Commands Run

The requested command failed because this shell does not provide a `python` executable:

```bash
python scripts/generate_synthetic_data.py
```

Successful validation commands:

```bash
python3 scripts/generate_synthetic_data.py
python3 -m pytest
```

## Test Result Summary

Test command:

```bash
python3 -m pytest
```

Result:

```text
12 passed
```

Covered validation areas:

- deterministic output for the same seed;
- controlled output difference for a different seed;
- generated ID uniqueness;
- reference integrity;
- synthetic-only policy checks;
- ground truth coverage for every bundle;
- frozen discrepancy taxonomy usage;
- clean-match label consistency;
- monetary total arithmetic;
- quantity validity;
- date validity;
- script execution from repository root.

## Limitations

- Slice 1 does not implement reconciliation, matching, confidence scoring, evaluation metrics, OCR, model calls, APIs, UI, or deployment.
- `low_confidence_extraction` and `schema_validation_failure` are represented as ground-truth simulated extraction issues while keeping generated source records schema-valid.
- The generator writes JSON fixtures only; rendered document formats are deferred.
- No real documents or external data sources are supported.

## Next Slice Recommendation

Slice 2 should implement schema validation and normalization checks over the generated fixtures before adding reconciliation logic. That keeps the next layer focused on data correctness and contract enforcement before matching behavior is introduced.
