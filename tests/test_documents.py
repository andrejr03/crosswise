from __future__ import annotations

import html
import shutil
from pathlib import Path

from crosswise.documents import (
    DOCUMENTS_OUTPUT_DIR,
    INVOICE_OUTPUT_PATH,
    PURCHASE_ORDER_OUTPUT_PATH,
    RECEIPT_OUTPUT_PATH,
    REPRESENTATIVE_BUNDLE_ID,
    generate_document_pack,
    render_document_pack,
)
from crosswise.documents.synthetic_documents import load_fixture_payload


REPO_ROOT = Path(__file__).resolve().parents[1]


def _fixtures() -> dict:
    return load_fixture_payload(REPO_ROOT)


def _source_records(fixtures: dict) -> dict:
    bundle = _one(fixtures["document_bundles"], "bundle_id", REPRESENTATIVE_BUNDLE_ID)
    invoice = _one(fixtures["invoices"], "invoice_id", bundle["invoice_ids"][0])
    purchase_order = _one(fixtures["purchase_orders"], "purchase_order_id", bundle["purchase_order_id"])
    receipt = _one(fixtures["receipts"], "receipt_id", bundle["receipt_ids"][0])
    supplier = _one(fixtures["suppliers"], "supplier_id", bundle["supplier_id"])
    invoice_lines = _lines(fixtures["invoice_lines"], "invoice_line_id", invoice["line_ids"])
    purchase_order_lines = _lines(
        fixtures["purchase_order_lines"],
        "po_line_id",
        purchase_order["line_ids"],
    )
    receipt_lines = _lines(fixtures["receipt_lines"], "receipt_line_id", receipt["line_ids"])
    return {
        "bundle": bundle,
        "invoice": invoice,
        "invoice_lines": invoice_lines,
        "purchase_order": purchase_order,
        "purchase_order_lines": purchase_order_lines,
        "receipt": receipt,
        "receipt_lines": receipt_lines,
        "supplier": supplier,
    }


def _one(records: list[dict], key: str, value: str) -> dict:
    matches = [record for record in records if record.get(key) == value]
    assert len(matches) == 1
    return matches[0]


def _lines(records: list[dict], key: str, ids: list[str]) -> list[dict]:
    by_id = {record[key]: record for record in records}
    return sorted([by_id[item_id] for item_id in ids], key=lambda item: item["line_number"])


def _escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def test_generate_document_pack_writes_exactly_three_documents(tmp_path: Path) -> None:
    fixture_source = REPO_ROOT / "data" / "synthetic" / "fixtures_v1_0.json"
    fixture_target = tmp_path / "data" / "synthetic" / "fixtures_v1_0.json"
    fixture_target.parent.mkdir(parents=True)
    shutil.copyfile(fixture_source, fixture_target)

    output_paths = generate_document_pack(tmp_path)
    output_dir = tmp_path / DOCUMENTS_OUTPUT_DIR

    assert output_paths == {
        "invoice": tmp_path / INVOICE_OUTPUT_PATH,
        "purchase_order": tmp_path / PURCHASE_ORDER_OUTPUT_PATH,
        "receipt": tmp_path / RECEIPT_OUTPUT_PATH,
    }
    assert sorted(path.name for path in output_dir.iterdir()) == [
        "invoice.html",
        "purchase_order.html",
        "receipt.html",
    ]


def test_document_values_match_representative_bundle_fixtures() -> None:
    fixtures = _fixtures()
    source = _source_records(fixtures)
    rendered = render_document_pack(fixtures)

    invoice_html = rendered["invoice"]
    invoice = source["invoice"]
    for value in [
        invoice["invoice_number"],
        invoice["invoice_date"],
        invoice["due_date"],
        invoice["currency"],
        invoice["supplier_name_raw"],
        invoice["subtotal"],
        invoice["tax_amount"],
        invoice["total_amount"],
    ]:
        assert _escaped(value) in invoice_html
    for line in source["invoice_lines"]:
        for field in [
            "line_number",
            "description",
            "sku_raw",
            "quantity_billed",
            "unit_of_measure",
            "unit_price",
            "line_total",
        ]:
            assert _escaped(line[field]) in invoice_html

    purchase_order_html = rendered["purchase_order"]
    purchase_order = source["purchase_order"]
    for value in [
        purchase_order["purchase_order_id"],
        purchase_order["issue_date"],
        purchase_order["expected_receipt_date"],
        purchase_order["status"],
        purchase_order["currency"],
        purchase_order["subtotal"],
        purchase_order["tax_amount"],
        purchase_order["total_amount"],
    ]:
        assert _escaped(value) in purchase_order_html
    for line in source["purchase_order_lines"]:
        for field in [
            "line_number",
            "description",
            "quantity_ordered",
            "unit_of_measure",
            "unit_price",
            "line_total",
        ]:
            assert _escaped(line[field]) in purchase_order_html

    receipt_html = rendered["receipt"]
    receipt = source["receipt"]
    for value in [
        receipt["receipt_number"],
        receipt["receipt_date"],
        receipt["related_purchase_order_id"],
        receipt["supplier_name_raw"],
    ]:
        assert _escaped(value) in receipt_html
    for line in source["receipt_lines"]:
        for field in [
            "line_number",
            "sku_raw",
            "quantity_received",
            "unit_of_measure",
            "received_date",
        ]:
            assert _escaped(line[field]) in receipt_html


def test_documents_are_internally_consistent_for_same_source_bundle() -> None:
    fixtures = _fixtures()
    source = _source_records(fixtures)
    rendered = render_document_pack(fixtures)
    combined = "\n".join(rendered.values())

    assert source["bundle"]["bundle_id"] == REPRESENTATIVE_BUNDLE_ID
    assert source["invoice"]["invoice_id"] == "inv_003_a"
    assert source["purchase_order"]["purchase_order_id"] == "po_003"
    assert source["receipt"]["receipt_id"] == "rcpt_003"
    assert combined.count(_escaped(source["supplier"]["canonical_name"])) >= 3

    invoice_skus = [line["sku_id"] for line in source["invoice_lines"]]
    purchase_order_skus = [line["sku_id"] for line in source["purchase_order_lines"]]
    receipt_skus = [line["sku_id"] for line in source["receipt_lines"]]
    assert invoice_skus == purchase_order_skus == receipt_skus
    assert len(source["invoice_lines"]) == len(source["purchase_order_lines"]) == len(source["receipt_lines"])


def test_documents_are_offline_self_contained_and_script_free() -> None:
    for document_html in render_document_pack(_fixtures()).values():
        lowered = document_html.lower()
        assert lowered.startswith("<!doctype html>")
        assert lowered.count("<style>") == 1
        assert lowered.count("</style>") == 1
        assert "</html>" in lowered
        assert "<script" not in lowered
        assert "http://" not in lowered
        assert "https://" not in lowered
        assert "src=" not in lowered
        assert "href=" not in lowered
        assert "@font-face" not in lowered
        assert "url(" not in lowered
        assert "package.json" not in lowered


def test_documents_include_required_caption_wording() -> None:
    required_phrases = [
        "synthetic, illustrative",
        "not a real document",
        "no real company, supplier, payment, tax, or bank data",
        "not parsed, ingested, or read back",
        "no OCR",
        "not accounting, tax, legal, financial, payment, or compliance advice",
    ]
    for document_html in render_document_pack(_fixtures()).values():
        for phrase in required_phrases:
            assert phrase in document_html


def test_documents_do_not_render_reconciliation_annotations() -> None:
    combined = "\n".join(render_document_pack(_fixtures()).values()).lower()

    assert "field-highlight" not in combined
    assert "status-review" not in combined
    assert "route to human review" not in combined
    assert "discrepancy" not in combined
    assert "mismatch" not in combined


def test_document_html_output_is_deterministic_across_repeated_renders() -> None:
    fixtures = _fixtures()

    assert render_document_pack(fixtures) == render_document_pack(fixtures)


def test_generate_document_pack_output_is_deterministic(tmp_path: Path) -> None:
    fixture_source = REPO_ROOT / "data" / "synthetic" / "fixtures_v1_0.json"
    fixture_target = tmp_path / "data" / "synthetic" / "fixtures_v1_0.json"
    fixture_target.parent.mkdir(parents=True)
    shutil.copyfile(fixture_source, fixture_target)

    first_paths = generate_document_pack(tmp_path)
    first = {key: path.read_text(encoding="utf-8") for key, path in first_paths.items()}
    second_paths = generate_document_pack(tmp_path)
    second = {key: path.read_text(encoding="utf-8") for key, path in second_paths.items()}

    assert first == second
