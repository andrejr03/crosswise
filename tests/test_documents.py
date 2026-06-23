from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

from crosswise.documents import (
    DOCUMENTS_OUTPUT_DIR,
    DOCUMENT_INDEX_OUTPUT_PATH,
    INVOICE_OUTPUT_PATH,
    PURCHASE_ORDER_OUTPUT_PATH,
    RECEIPT_OUTPUT_PATH,
    REPRESENTATIVE_BUNDLE_ID,
    generate_document_pack,
    render_document_pack,
)
from crosswise.documents.synthetic_documents import load_fixture_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_KEYS = ("invoice", "purchase_order", "receipt")
BUYER_IDENTITY = {
    "name": "Crosswise Demo Buyer GmbH",
    "address": "SYN Buyer House 001, 00000 Synthetic City, DE",
    "vat_id": "DE-SYN-000000000",
    "contact": "ap@crosswise-demo.synthetic",
}
ALLOWED_DOCUMENT_HREFS = {
    "index.html",
    "invoice.html",
    "purchase_order.html",
    "receipt.html",
    "../crosswise_reviewer_v1_0.html",
}
ALLOWED_INDEX_HREFS = {
    "invoice.html",
    "purchase_order.html",
    "receipt.html",
    "../crosswise_reviewer_v1_0.html",
}
CURRENT_DOCUMENT_LINKS = {
    "invoice": ("Invoice", "invoice.html"),
    "purchase_order": ("Purchase order", "purchase_order.html"),
    "receipt": ("Receipt", "receipt.html"),
}


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


def _hrefs(document_html: str) -> list[str]:
    return re.findall(r'href="([^"]+)"', document_html)


def _supplier_identity(supplier: dict) -> dict[str, str]:
    supplier_number = "".join(character for character in supplier["supplier_id"] if character.isdigit()).zfill(3)
    country_code = supplier.get("country_code") or "SYN"
    legal_form = "GmbH" if country_code == "DE" else "Ltd"
    return {
        "name": f"{supplier['canonical_name']} {legal_form}",
        "address": f"SYN Supplier Campus {supplier_number}, 000{supplier_number} Synthetic City, {country_code}",
        "vat_id": f"{country_code}-SYN-{int(supplier_number):09d}",
        "contact": f"accounts@supplier-{supplier_number}.synthetic",
    }


def test_generate_document_pack_writes_exactly_four_documents(tmp_path: Path) -> None:
    fixture_source = REPO_ROOT / "data" / "synthetic" / "fixtures_v1_0.json"
    fixture_target = tmp_path / "data" / "synthetic" / "fixtures_v1_0.json"
    fixture_target.parent.mkdir(parents=True)
    shutil.copyfile(fixture_source, fixture_target)

    output_paths = generate_document_pack(tmp_path)
    output_dir = tmp_path / DOCUMENTS_OUTPUT_DIR

    assert output_paths == {
        "index": tmp_path / DOCUMENT_INDEX_OUTPUT_PATH,
        "invoice": tmp_path / INVOICE_OUTPUT_PATH,
        "purchase_order": tmp_path / PURCHASE_ORDER_OUTPUT_PATH,
        "receipt": tmp_path / RECEIPT_OUTPUT_PATH,
    }
    assert sorted(path.name for path in output_dir.iterdir()) == [
        "index.html",
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


def test_document_index_values_match_representative_bundle_fixtures() -> None:
    fixtures = _fixtures()
    source = _source_records(fixtures)
    index_html = render_document_pack(fixtures)["index"]

    assert _escaped(source["bundle"]["bundle_id"]) in index_html
    assert _escaped(source["invoice"]["invoice_number"]) in index_html
    assert _escaped(source["purchase_order"]["purchase_order_id"]) in index_html
    assert _escaped(source["receipt"]["receipt_number"]) in index_html


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


def test_documents_render_two_party_identity_blocks() -> None:
    fixtures = _fixtures()
    source = _source_records(fixtures)
    rendered = render_document_pack(fixtures)
    supplier_identity = _supplier_identity(source["supplier"])

    expected_labels = {
        "invoice": ("Issuer / seller", "Bill-to / buyer"),
        "purchase_order": ("Buyer / orderer", "Supplier / seller"),
        "receipt": ("Receiving party / buyer", "Supplier / seller"),
    }
    for key, document_html in ((key, rendered[key]) for key in DOCUMENT_KEYS):
        assert document_html.count('class="party-card"') == 2
        for label in expected_labels[key]:
            assert f'<span class="label">{label}</span>' in document_html
        for value in supplier_identity.values():
            assert _escaped(value) in document_html
        for value in BUYER_IDENTITY.values():
            assert _escaped(value) in document_html


def test_synthetic_identity_markers_are_visible_and_non_real_looking() -> None:
    rendered = render_document_pack(_fixtures())
    combined = "\n".join(rendered[key] for key in DOCUMENT_KEYS)

    assert "Synthetic City" in combined
    assert "SYN Supplier Campus" in combined
    assert "SYN Buyer House" in combined

    vat_ids = re.findall(r"[A-Z]{2}-SYN-\d{9}", combined)
    assert vat_ids
    for vat_id in vat_ids:
        assert "SYN" in vat_id
        assert re.fullmatch(r"[A-Z]{2}\d{9}", vat_id) is None

    contacts = re.findall(r"[\w.-]+@[\w.-]+", combined)
    assert contacts
    assert all(contact.endswith(".synthetic") for contact in contacts)
    assert re.search(r"@[A-Za-z0-9.-]+\.(com|de|eu|net|org)\b", combined) is None


def test_buyer_identity_is_consistent_across_all_documents() -> None:
    rendered = render_document_pack(_fixtures())

    for key in DOCUMENT_KEYS:
        document_html = rendered[key]
        for value in BUYER_IDENTITY.values():
            assert document_html.count(_escaped(value)) == 1


def test_document_specific_two_party_metadata_is_present() -> None:
    rendered = render_document_pack(_fixtures())

    assert "Payment terms" in rendered["invoice"]
    assert "Net 30 - due 2026-02-12" in rendered["invoice"]
    assert "PO reference" in rendered["invoice"]
    assert "po_003" in rendered["invoice"]

    assert "Issue date" in rendered["purchase_order"]
    assert "Expected receipt" in rendered["purchase_order"]
    assert "Status" in rendered["purchase_order"]

    assert "Receipt number" in rendered["receipt"]
    assert "Receipt date" in rendered["receipt"]
    assert "Related PO" in rendered["receipt"]


def test_documents_do_not_include_forbidden_realism_theatre() -> None:
    rendered = render_document_pack(_fixtures())
    combined = "\n".join(rendered.values()).lower()

    forbidden_terms = [
        "iban",
        "swift",
        "bic",
        "bank account",
        "account number",
        "remit to",
        "signature",
        "signed by",
        "stamp",
        "seal",
        "qr code",
        "qrcode",
        "barcode",
        "logo",
        "e-invoice",
        "zugferd",
        "xrechnung",
    ]
    for term in forbidden_terms:
        assert term not in combined
    assert "http://" not in combined
    assert "https://" not in combined
    assert "mailto:" not in combined


def test_documents_are_offline_self_contained_and_script_free() -> None:
    for key, document_html in render_document_pack(_fixtures()).items():
        lowered = document_html.lower()
        assert lowered.startswith("<!doctype html>")
        assert lowered.count("<style>") == 1
        assert lowered.count("</style>") == 1
        assert "</html>" in lowered
        assert "<script" not in lowered
        assert "http://" not in lowered
        assert "https://" not in lowered
        assert "//" not in lowered
        assert "src=" not in lowered
        assert "@font-face" not in lowered
        assert "url(" not in lowered
        assert "package.json" not in lowered
        allowed = ALLOWED_INDEX_HREFS if key == "index" else ALLOWED_DOCUMENT_HREFS
        for href in _hrefs(document_html):
            assert href in allowed
            assert not href.startswith(("/", "http:", "https:", "mailto:", "file:"))
            assert "//" not in href


def test_documents_include_required_caption_wording() -> None:
    required_phrases = [
        "synthetic, illustrative",
        "no real company, supplier, payment, tax, or bank data",
        "not parsed, ingested, or read back",
        "no OCR",
        "not accounting, tax, legal, financial, payment, or compliance advice",
    ]
    rendered = render_document_pack(_fixtures())
    for document_html in rendered.values():
        for phrase in required_phrases:
            assert phrase in document_html
    assert "not real documents" in rendered["index"]
    for key in DOCUMENT_KEYS:
        assert "not a real document" in rendered[key]


def test_index_links_to_documents_and_reviewer() -> None:
    index_html = render_document_pack(_fixtures())["index"]

    assert set(_hrefs(index_html)) == ALLOWED_INDEX_HREFS
    assert 'href="invoice.html"' in index_html
    assert 'href="purchase_order.html"' in index_html
    assert 'href="receipt.html"' in index_html
    assert 'href="../crosswise_reviewer_v1_0.html"' in index_html


def test_documents_link_to_index_peers_and_reviewer_with_current_marker() -> None:
    rendered = render_document_pack(_fixtures())

    for key in DOCUMENT_KEYS:
        document_html = rendered[key]
        current_label, current_href = CURRENT_DOCUMENT_LINKS[key]
        expected_hrefs = ALLOWED_DOCUMENT_HREFS - {current_href}
        assert set(_hrefs(document_html)) == expected_hrefs
        assert 'href="index.html"' in document_html
        assert 'href="../crosswise_reviewer_v1_0.html"' in document_html
        assert f'href="{current_href}"' not in document_html
        assert f'<span aria-current="page">{current_label}</span>' in document_html


def test_all_document_pack_links_are_approved_relative_paths() -> None:
    rendered = render_document_pack(_fixtures())

    for key, document_html in rendered.items():
        allowed = ALLOWED_INDEX_HREFS if key == "index" else ALLOWED_DOCUMENT_HREFS
        hrefs = _hrefs(document_html)
        assert hrefs
        assert set(hrefs) <= allowed
        for href in hrefs:
            assert re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", href) is None
            assert not href.startswith("/")
            assert "//" not in href


def test_documents_do_not_render_reconciliation_annotations() -> None:
    rendered = render_document_pack(_fixtures())
    combined = "\n".join(rendered[key] for key in DOCUMENT_KEYS).lower()

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
