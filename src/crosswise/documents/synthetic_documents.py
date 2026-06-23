"""Self-contained synthetic source-document HTML generation.

The document pack renders existing Crosswise fixtures only. It does not parse,
ingest, OCR, reconcile, evaluate, route, or read these HTML files back.
"""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path
from typing import Any

REQUIRED_FIXTURE_PATH = Path("data/synthetic/fixtures_v1_0.json")
DOCUMENTS_OUTPUT_DIR = Path("docs/evidence/documents")
DOCUMENT_INDEX_OUTPUT_PATH = DOCUMENTS_OUTPUT_DIR / "index.html"
INVOICE_OUTPUT_PATH = DOCUMENTS_OUTPUT_DIR / "invoice.html"
PURCHASE_ORDER_OUTPUT_PATH = DOCUMENTS_OUTPUT_DIR / "purchase_order.html"
RECEIPT_OUTPUT_PATH = DOCUMENTS_OUTPUT_DIR / "receipt.html"
DOCUMENT_PACK_SCREENSHOT_OUTPUT_PATH = Path("docs/evidence/CROSSWISE_DOCUMENT_PACK_SHOWCASE.png")
DOCUMENT_PACK_INDEX_SCREENSHOT_OUTPUT_PATH = Path("docs/evidence/CROSSWISE_DOCUMENT_PACK_INDEX_SHOWCASE.png")
DOCUMENT_PACK_INVOICE_SCREENSHOT_OUTPUT_PATH = Path("docs/evidence/CROSSWISE_DOCUMENT_PACK_INVOICE_SHOWCASE.png")
DOCUMENT_PACK_PURCHASE_ORDER_SCREENSHOT_OUTPUT_PATH = Path(
    "docs/evidence/CROSSWISE_DOCUMENT_PACK_PURCHASE_ORDER_SHOWCASE.png"
)
DOCUMENT_PACK_RECEIPT_SCREENSHOT_OUTPUT_PATH = Path("docs/evidence/CROSSWISE_DOCUMENT_PACK_RECEIPT_SHOWCASE.png")
REPRESENTATIVE_BUNDLE_ID = "bundle_unit_price_mismatch_003"
BUYER_IDENTITY = {
    "name": "Crosswise Demo Buyer GmbH",
    "address": "SYN Buyer House 001, 00000 Synthetic City, DE",
    "vat_id": "DE-SYN-000000000",
    "contact": "ap@crosswise-demo.synthetic",
}


def load_fixture_payload(repo_root: Path) -> dict[str, Any]:
    fixture_path = repo_root / REQUIRED_FIXTURE_PATH
    if not fixture_path.is_file():
        raise FileNotFoundError(
            "Required upstream Crosswise fixtures are missing. Run the synthetic data pipeline first:\n"
            "python3 scripts/generate_synthetic_data.py\n"
            f"Missing file:\n- {REQUIRED_FIXTURE_PATH}"
        )
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def generate_document_pack(repo_root: Path) -> dict[str, Path]:
    fixtures = load_fixture_payload(repo_root)
    rendered = render_document_pack(fixtures)
    outputs = {
        "index": repo_root / DOCUMENT_INDEX_OUTPUT_PATH,
        "invoice": repo_root / INVOICE_OUTPUT_PATH,
        "purchase_order": repo_root / PURCHASE_ORDER_OUTPUT_PATH,
        "receipt": repo_root / RECEIPT_OUTPUT_PATH,
    }
    for key, output_path in outputs.items():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered[key], encoding="utf-8")
    return outputs


def generate_document_pack_screenshot(
    html_path: Path,
    screenshot_path: Path,
    *,
    viewport_height: int = 960,
) -> Path:
    from playwright.sync_api import sync_playwright

    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": viewport_height}, device_scale_factor=1)
        page.goto(html_path.resolve().as_uri())
        page.screenshot(path=str(screenshot_path), full_page=False)
        browser.close()
    return screenshot_path


def generate_document_pack_screenshots(document_paths: dict[str, Path], repo_root: Path) -> dict[str, Path]:
    screenshot_paths = {
        "index": repo_root / DOCUMENT_PACK_INDEX_SCREENSHOT_OUTPUT_PATH,
        "invoice": repo_root / DOCUMENT_PACK_INVOICE_SCREENSHOT_OUTPUT_PATH,
        "purchase_order": repo_root / DOCUMENT_PACK_PURCHASE_ORDER_SCREENSHOT_OUTPUT_PATH,
        "receipt": repo_root / DOCUMENT_PACK_RECEIPT_SCREENSHOT_OUTPUT_PATH,
    }
    for key, screenshot_path in screenshot_paths.items():
        viewport_height = 1080 if key == "index" else 960
        generate_document_pack_screenshot(document_paths[key], screenshot_path, viewport_height=viewport_height)
    return screenshot_paths


def render_document_pack(fixtures: dict[str, Any]) -> dict[str, str]:
    source = _representative_source(fixtures)
    return {
        "index": _render_document_index(source),
        "invoice": _render_invoice(source),
        "purchase_order": _render_purchase_order(source),
        "receipt": _render_receipt(source),
    }


def _representative_source(fixtures: dict[str, Any]) -> dict[str, Any]:
    bundle = _find_one(
        fixtures["document_bundles"],
        "bundle_id",
        REPRESENTATIVE_BUNDLE_ID,
    )
    invoice = _find_one(fixtures["invoices"], "invoice_id", bundle["invoice_ids"][0])
    purchase_order = _find_one(
        fixtures["purchase_orders"],
        "purchase_order_id",
        bundle["purchase_order_id"],
    )
    receipt = _find_one(fixtures["receipts"], "receipt_id", bundle["receipt_ids"][0])
    supplier = _find_one(fixtures["suppliers"], "supplier_id", bundle["supplier_id"])

    invoice_lines = _lines_for_ids(
        fixtures["invoice_lines"],
        "invoice_line_id",
        invoice["line_ids"],
    )
    purchase_order_lines = _lines_for_ids(
        fixtures["purchase_order_lines"],
        "po_line_id",
        purchase_order["line_ids"],
    )
    receipt_lines = _lines_for_ids(
        fixtures["receipt_lines"],
        "receipt_line_id",
        receipt["line_ids"],
    )

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


def _find_one(records: list[dict[str, Any]], key: str, value: Any) -> dict[str, Any]:
    matches = [record for record in records if record.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {key}={value!r}, found {len(matches)}.")
    return matches[0]


def _lines_for_ids(
    records: list[dict[str, Any]],
    id_key: str,
    ids: list[str],
) -> list[dict[str, Any]]:
    by_id = {record[id_key]: record for record in records}
    lines = [by_id[line_id] for line_id in ids]
    return sorted(lines, key=lambda line: line["line_number"])


def _render_document_index(source: dict[str, Any]) -> str:
    bundle = source["bundle"]
    invoice = source["invoice"]
    purchase_order = source["purchase_order"]
    receipt = source["receipt"]
    supplier_identity = _supplier_identity(source["supplier"])
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Crosswise Synthetic Document Pack</title>",
            f"  <style>{_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="document-page pack-index">',
            '    <header class="masthead">',
            "      <div>",
            '        <div class="kicker">Crosswise synthetic document pack</div>',
            "        <h1>Document Pack</h1>",
            "      </div>",
            '      <div class="brand-mark" aria-hidden="true"></div>',
            "    </header>",
            '    <section class="identity-strip" aria-label="Document pack identity">',
            "      <div>",
            '        <span class="label">Source bundle</span>',
            f"        <strong>{_e(bundle['bundle_id'])}</strong>",
            "      </div>",
            "      <div>",
            '        <span class="label">Records</span>',
            "        <strong>"
            f"{_e(invoice['invoice_number'])} &middot; "
            f"{_e(purchase_order['purchase_order_id'])} &middot; "
            f"{_e(receipt['receipt_number'])}"
            "</strong>",
            "      </div>",
            "    </section>",
            '    <section class="pack-intro" aria-label="Pack summary">',
            "      <p>These source-record renders show a synthetic transaction between "
            f"{_e(supplier_identity['name'])} and {_e(BUYER_IDENTITY['name'])}.</p>",
            "    </section>",
            '    <section class="pack-links" aria-label="Pack contents">',
            f"      {_pack_link('invoice.html', 'Invoice', invoice['invoice_number'], 'Synthetic invoice source-record render')}",
            f"      {_pack_link('purchase_order.html', 'Purchase Order', purchase_order['purchase_order_id'], 'Synthetic purchase order source-record render')}",
            f"      {_pack_link('receipt.html', 'Goods Receipt', receipt['receipt_number'], 'Synthetic receipt source-record render')}",
            "    </section>",
            '    <p class="reviewer-link"><a href="../crosswise_reviewer_v1_0.html">Open the Crosswise reviewer</a></p>',
            '    <footer class="caption">',
            "      <strong>Synthetic document notice</strong>",
            "      <p>These are synthetic, illustrative renders of generated Crosswise source records. "
            "They are not real documents and contain no real company, supplier, payment, tax, or bank data. "
            "They are not parsed, ingested, or read back by Crosswise; there is no OCR. "
            "Crosswise output is not accounting, tax, legal, financial, payment, or compliance advice.</p>",
            "    </footer>",
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _render_invoice(source: dict[str, Any]) -> str:
    invoice = source["invoice"]
    purchase_order = source["purchase_order"]
    supplier_identity = _supplier_identity(source["supplier"])
    lines = source["invoice_lines"]
    meta = [
        ("Invoice number", invoice["invoice_number"]),
        ("Invoice date", invoice["invoice_date"]),
        ("Due date", invoice.get("due_date")),
        ("Payment terms", _payment_terms(invoice["invoice_date"], invoice.get("due_date"))),
        ("PO reference", purchase_order["purchase_order_id"]),
        ("Currency", invoice["currency"]),
    ]
    table_head = ["Line", "Description", "SKU", "Qty billed", "Unit", "Unit price", "Line total"]
    table_rows = [
        [
            line["line_number"],
            line.get("description"),
            line["sku_raw"],
            line["quantity_billed"],
            line["unit_of_measure"],
            _money(invoice["currency"], line["unit_price"]),
            _money(invoice["currency"], line["line_total"]),
        ]
        for line in lines
    ]
    totals = [
        ("Subtotal", _money(invoice["currency"], invoice["subtotal"])),
        ("Tax amount", _money(invoice["currency"], invoice.get("tax_amount"))),
        ("Total", _money(invoice["currency"], invoice["total_amount"])),
    ]
    return _document_shell(
        title=f"Crosswise Synthetic Invoice - {invoice['invoice_number']}",
        document_type="Invoice",
        current_document="invoice",
        document_id=invoice["invoice_number"],
        record_note="Generated source record render",
        meta=meta,
        parties=[
            ("Issuer / seller", supplier_identity),
            ("Bill-to / buyer", BUYER_IDENTITY),
        ],
        table_head=table_head,
        table_rows=table_rows,
        totals=totals,
    )


def _render_purchase_order(source: dict[str, Any]) -> str:
    purchase_order = source["purchase_order"]
    supplier = source["supplier"]
    supplier_identity = _supplier_identity(supplier)
    lines = source["purchase_order_lines"]
    meta = [
        ("Purchase order", purchase_order["purchase_order_id"]),
        ("Issue date", purchase_order["issue_date"]),
        ("Expected receipt", purchase_order.get("expected_receipt_date")),
        ("Status", purchase_order.get("status")),
        ("Currency", purchase_order["currency"]),
    ]
    table_head = ["Line", "Description", "Qty ordered", "Unit", "Unit price", "Line total"]
    table_rows = [
        [
            line["line_number"],
            line.get("description"),
            line["quantity_ordered"],
            line["unit_of_measure"],
            _money(purchase_order["currency"], line["unit_price"]),
            _money(purchase_order["currency"], line["line_total"]),
        ]
        for line in lines
    ]
    totals = [
        ("Subtotal", _money(purchase_order["currency"], purchase_order["subtotal"])),
        ("Tax amount", _money(purchase_order["currency"], purchase_order.get("tax_amount"))),
        ("Total", _money(purchase_order["currency"], purchase_order["total_amount"])),
    ]
    return _document_shell(
        title=f"Crosswise Synthetic Purchase Order - {purchase_order['purchase_order_id']}",
        document_type="Purchase Order",
        current_document="purchase_order",
        document_id=purchase_order["purchase_order_id"],
        record_note="Generated source record render",
        meta=meta,
        parties=[
            ("Buyer / orderer", BUYER_IDENTITY),
            ("Supplier / seller", supplier_identity),
        ],
        table_head=table_head,
        table_rows=table_rows,
        totals=totals,
    )


def _render_receipt(source: dict[str, Any]) -> str:
    receipt = source["receipt"]
    supplier_identity = _supplier_identity(source["supplier"])
    lines = source["receipt_lines"]
    meta = [
        ("Receipt number", receipt["receipt_number"]),
        ("Receipt date", receipt["receipt_date"]),
        ("Related PO", receipt.get("related_purchase_order_id")),
    ]
    table_head = ["Line", "SKU", "Qty received", "Unit", "Received date"]
    table_rows = [
        [
            line["line_number"],
            line["sku_raw"],
            line["quantity_received"],
            line["unit_of_measure"],
            line.get("received_date"),
        ]
        for line in lines
    ]
    totals = [
        ("Receipt lines", str(len(lines))),
        ("Related PO", receipt.get("related_purchase_order_id")),
    ]
    return _document_shell(
        title=f"Crosswise Synthetic Goods Receipt - {receipt['receipt_number']}",
        document_type="Goods Receipt",
        current_document="receipt",
        document_id=receipt["receipt_number"],
        record_note="Generated source record render",
        meta=meta,
        parties=[
            ("Receiving party / buyer", BUYER_IDENTITY),
            ("Supplier / seller", supplier_identity),
        ],
        table_head=table_head,
        table_rows=table_rows,
        totals=totals,
    )


def _document_shell(
    *,
    title: str,
    document_type: str,
    current_document: str,
    document_id: str,
    record_note: str,
    meta: list[tuple[str, Any]],
    parties: list[tuple[str, dict[str, str]]],
    table_head: list[str],
    table_rows: list[list[Any]],
    totals: list[tuple[str, Any]],
) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{_e(title)}</title>",
            f"  <style>{_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="document-page">',
            '    <header class="masthead">',
            '      <div>',
            '        <div class="kicker">Crosswise synthetic source record</div>',
            f"        <h1>{_e(document_type)}</h1>",
            "      </div>",
            '      <div class="brand-mark" aria-hidden="true"></div>',
            "    </header>",
            f"    {_document_nav(current_document)}",
            '    <section class="identity-strip" aria-label="Document identity">',
            '      <div>',
            '        <span class="label">Document ID</span>',
            f"        <strong>{_e(document_id)}</strong>",
            "      </div>",
            '      <div>',
            '        <span class="label">Record note</span>',
            f"        <strong>{_e(record_note)}</strong>",
            "      </div>",
            "    </section>",
            f"    {_meta_grid(meta)}",
            f"    {_party_grid(parties)}",
            '    <section class="lines-section" aria-label="Line items">',
            '      <div class="section-rule">',
            '        <span>Line items</span>',
            "      </div>",
            f"      {_line_table(table_head, table_rows)}",
            "    </section>",
            f"    {_totals_block(totals)}",
            "    <footer class=\"caption\">",
            "      <strong>Synthetic document notice</strong>",
            "      <p>This is a synthetic, illustrative render of a generated Crosswise source record. "
            "It is not a real document and contains no real company, supplier, payment, tax, or bank data. "
            "It is not parsed, ingested, or read back by Crosswise; there is no OCR. "
            "Crosswise output is not accounting, tax, legal, financial, payment, or compliance advice.</p>",
            "    </footer>",
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _supplier_identity(supplier: dict[str, Any]) -> dict[str, str]:
    supplier_number = "".join(character for character in supplier["supplier_id"] if character.isdigit()).zfill(3)
    country_code = supplier.get("country_code") or "SYN"
    legal_form = "GmbH" if country_code == "DE" else "Ltd"
    return {
        "name": f"{supplier['canonical_name']} {legal_form}",
        "address": f"SYN Supplier Campus {supplier_number}, 000{supplier_number} Synthetic City, {country_code}",
        "vat_id": f"{country_code}-SYN-{int(supplier_number):09d}",
        "contact": f"accounts@supplier-{supplier_number}.synthetic",
    }


def _payment_terms(invoice_date: str, due_date: str | None) -> str | None:
    if due_date is None:
        return None
    days = (date.fromisoformat(due_date) - date.fromisoformat(invoice_date)).days
    return f"Net {days} - due {due_date}"


def _document_nav(current_document: str) -> str:
    items = [
        ("index", "Pack index", "index.html"),
        ("invoice", "Invoice", "invoice.html"),
        ("purchase_order", "Purchase order", "purchase_order.html"),
        ("receipt", "Receipt", "receipt.html"),
        ("reviewer", "Reviewer", "../crosswise_reviewer_v1_0.html"),
    ]
    rendered = []
    for key, label, href in items:
        if key == current_document:
            rendered.append(f'      <span aria-current="page">{_e(label)}</span>')
        else:
            rendered.append(f'      <a href="{_e(href)}">{_e(label)}</a>')
    return "\n".join(
        [
            '    <nav class="document-nav" aria-label="Document pack navigation">',
            *rendered,
            "    </nav>",
        ]
    )


def _party_grid(parties: list[tuple[str, dict[str, str]]]) -> str:
    rows = []
    for label, identity in parties:
        rows.extend(
            [
                '      <article class="party-card">',
                f'        <span class="label">{_e(label)}</span>',
                f"        <h2>{_e(identity['name'])}</h2>",
                f"        <p>{_e(identity['address'])}</p>",
                f"        <p><span>VAT ID</span> {_e(identity['vat_id'])}</p>",
                f"        <p><span>Contact</span> {_e(identity['contact'])}</p>",
                "      </article>",
            ]
        )
    return "\n".join(['    <section class="party-grid" aria-label="Document parties">', *rows, "    </section>"])


def _pack_link(href: str, title: str, record_id: str, description: str) -> str:
    return (
        f'<a class="pack-link" href="{_e(href)}">'
        f'<span>{_e(title)} - <code>{_e(record_id)}</code></span>'
        f'<strong>{_e(description)}</strong>'
        "</a>"
    )


def _meta_grid(items: list[tuple[str, Any]]) -> str:
    rows = []
    for label, value in items:
        if value is None:
            continue
        card_class = "meta-card meta-card-wide" if label == "Payment terms" else "meta-card"
        rows.extend(
            [
                f'      <div class="{card_class}">',
                f"        <span>{_e(label)}</span>",
                f"        <strong>{_e(value)}</strong>",
                "      </div>",
            ]
        )
    return "\n".join(['    <section class="meta-grid" aria-label="Document metadata">', *rows, "    </section>"])


def _line_table(headers: list[str], rows: list[list[Any]]) -> str:
    head = "".join(f"<th>{_e(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{_cell(value)}</td>" for value in row)
        body_rows.append(f"          <tr>{cells}</tr>")
    return "\n".join(
        [
            '      <table class="line-table">',
            f"        <thead><tr>{head}</tr></thead>",
            "        <tbody>",
            *body_rows,
            "        </tbody>",
            "      </table>",
        ]
    )


def _totals_block(totals: list[tuple[str, Any]]) -> str:
    rows = []
    for label, value in totals:
        if value is None:
            continue
        rows.append(
            "      <div class=\"total-row\">"
            f"<span>{_e(label)}</span><strong>{_cell(value)}</strong>"
            "</div>"
        )
    return "\n".join(['    <section class="totals-block" aria-label="Document totals">', *rows, "    </section>"])


def _money(currency: str, amount: Any) -> str | None:
    if amount is None:
        return None
    return f'<span class="money"><span>{_e(currency)}</span> {_e(amount)}</span>'


def _cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.startswith("<span"):
        return text
    return _e(text)


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _css() -> str:
    return """
:root {
  --page: #171511;
  --paper: #eee8dd;
  --paper-warm: #e5d9c5;
  --ink: #211e19;
  --muted: #726a5d;
  --soft: #9c907e;
  --panel: #211e19;
  --line: #cdbf9f;
  --line-strong: #8b7854;
  --amber: #c9a24b;
  --amber-soft: rgba(201, 162, 75, 0.16);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  background:
    radial-gradient(circle at 50% -8%, rgba(201, 162, 75, 0.08), transparent 32%),
    var(--page);
  color: var(--ink);
  font-family: "Avenir Next", Avenir, "Gill Sans", "Trebuchet MS", sans-serif;
  line-height: 1.5;
}

.document-page {
  width: min(980px, calc(100% - 36px));
  margin: 38px auto;
  padding: 54px 58px 42px;
  background:
    linear-gradient(90deg, rgba(33, 30, 25, 0.055) 1px, transparent 1px) 0 0 / 32px 32px,
    linear-gradient(180deg, rgba(201, 162, 75, 0.10), transparent 210px),
    var(--paper);
  border: 1px solid rgba(201, 162, 75, 0.42);
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.34);
}

.masthead,
.identity-strip,
.section-rule,
.total-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.masthead {
  padding-bottom: 34px;
  border-bottom: 2px solid var(--ink);
}

.kicker,
.label,
.meta-card span,
.document-nav,
.pack-link span,
.reviewer-link,
.section-rule,
.line-table th,
.caption strong {
  font-family: Menlo, Consolas, monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.kicker,
.document-nav a,
.document-nav span,
.pack-link span,
.reviewer-link a,
.section-rule,
.caption strong {
  color: var(--amber);
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  margin-top: 8px;
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 64px;
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
}

h2 {
  margin-top: 8px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 31px;
  font-weight: 500;
  line-height: 1.05;
}

a {
  color: inherit;
}

.brand-mark {
  width: 36px;
  height: 36px;
  flex: none;
  transform: rotate(45deg);
  border: 2px solid var(--amber);
  box-shadow: 11px 11px 0 rgba(201, 162, 75, 0.12);
}

.identity-strip {
  margin-top: 28px;
  padding: 18px 0;
  border-bottom: 1px solid var(--line);
}

.document-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--line);
}

.document-nav a,
.document-nav span {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 9px 12px;
  border: 1px solid var(--line);
  background: rgba(33, 30, 25, 0.035);
  text-decoration: none;
}

.document-nav span {
  background: var(--ink);
  border-color: var(--ink);
}

.pack-intro {
  margin-top: 30px;
  padding: 24px 0 0;
}

.pack-intro p {
  max-width: 650px;
  color: var(--muted);
  font-size: 18px;
}

.pack-links {
  display: grid;
  gap: 12px;
  margin-top: 26px;
}

.pack-link {
  display: block;
  padding: 20px 22px;
  border: 1px solid var(--line);
  background: rgba(33, 30, 25, 0.045);
  text-decoration: none;
}

.pack-link strong {
  display: block;
  margin-top: 8px;
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 24px;
  font-weight: 500;
  line-height: 1.1;
}

.pack-link code {
  color: var(--ink);
  font-family: Menlo, Consolas, monospace;
  font-size: 12px;
}

.reviewer-link {
  margin-top: 24px;
}

.identity-strip div:last-child {
  text-align: right;
}

.label,
.meta-card span {
  display: block;
  color: var(--soft);
}

.identity-strip strong,
.meta-card strong,
.total-row strong {
  display: block;
  margin-top: 6px;
  color: var(--ink);
  font-family: Menlo, Consolas, monospace;
  font-size: 15px;
  font-weight: 600;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 30px;
  border-top: 1px solid var(--line);
  border-left: 1px solid var(--line);
}

.meta-card {
  min-height: 92px;
  padding: 17px 16px;
  border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}

.meta-card-wide {
  grid-column: span 2;
}

.meta-card-wide strong {
  white-space: nowrap;
}

.party-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 34px;
}

.party-card {
  min-height: 220px;
  padding: 26px 28px;
  background: rgba(33, 30, 25, 0.045);
  border-left: 5px solid var(--amber);
}

.party-card p {
  margin-top: 8px;
  color: var(--muted);
  font-size: 14px;
}

.party-card p span {
  color: var(--soft);
  font-family: Menlo, Consolas, monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.lines-section {
  margin-top: 38px;
}

.section-rule {
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--ink);
}

.section-rule::after {
  content: "";
  height: 1px;
  flex: 1;
  background: var(--line);
}

.line-table {
  width: 100%;
  margin-top: 18px;
  border-collapse: collapse;
}

.line-table th {
  padding: 0 12px 11px;
  color: var(--soft);
  text-align: left;
  vertical-align: bottom;
}

.line-table td {
  padding: 17px 12px;
  border-top: 1px solid var(--line);
  color: var(--ink);
  font-size: 15px;
  vertical-align: top;
}

.line-table th:first-child,
.line-table td:first-child {
  width: 58px;
  padding-left: 0;
  color: var(--amber);
  font-family: Menlo, Consolas, monospace;
}

.line-table th:nth-last-child(-n + 2),
.line-table td:nth-last-child(-n + 2) {
  text-align: right;
}

.money {
  white-space: nowrap;
  font-family: Menlo, Consolas, monospace;
}

.money span {
  color: var(--soft);
}

.totals-block {
  width: min(360px, 100%);
  margin: 30px 0 0 auto;
  border-top: 2px solid var(--ink);
}

.total-row {
  padding: 13px 0;
  border-bottom: 1px solid var(--line);
}

.total-row span {
  color: var(--muted);
}

.total-row:last-child strong {
  color: var(--ink);
  font-size: 20px;
}

.caption {
  margin-top: 44px;
  padding-top: 22px;
  border-top: 1px solid var(--line-strong);
}

.caption p {
  max-width: 820px;
  margin-top: 8px;
  color: var(--muted);
  font-size: 13px;
}

@media (max-width: 760px) {
  .document-page {
    width: min(100% - 20px, 980px);
    margin: 10px auto;
    padding: 30px 20px;
  }

  h1 {
    font-size: 42px;
  }

  .masthead,
  .identity-strip {
    display: grid;
  }

  .identity-strip div:last-child {
    text-align: left;
  }

  .meta-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .meta-card-wide strong {
    white-space: normal;
  }

  .party-grid {
    grid-template-columns: 1fr;
  }

  .lines-section {
    overflow-x: auto;
  }

  .line-table {
    min-width: 680px;
  }
}
""".strip()
