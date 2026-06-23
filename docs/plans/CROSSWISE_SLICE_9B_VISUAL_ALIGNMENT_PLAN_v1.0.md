# Crosswise Slice 9B — Visual Alignment Plan (v1.0)

> Short plan to align the Slice 9 static reviewer's visual design with the approved Crosswise showcase, without touching any reconciliation, evaluation, reliability, data, metric, or routing logic. Rendering-only. Slice 9 is not yet committed; this plan refines its presentation before commit.

---

## 1. Why a Plan (Not Direct Implementation)

A direct visual pass was considered and rejected. The gap between the current reviewer and `assets/prototypes/crosswise-showcase.png` is a **redesign**, not a refinement, and triggers all three "plan required" conditions:

- **Layout churn:** the current output stacks six dense, equal-weight, three-column bundle cards; the showcase is a single editorial hero case with generous whitespace and a calm field-comparison layout. Restructuring the story section and rewriting ~500 lines of CSS in `static_html.py` is substantial.
- **Unclear design decisions:** which bundle becomes the hero; how to render document panels in the showcase's restrained editorial style; how to reconcile the showcase's field-comparison-table aesthetic with Slice 9's document-panel mandate; how many cases sit above the fold and how the rest are condensed.
- **Broad redesign:** moving from "operational dashboard" to "premium editorial AI product" is a change of visual language, not a tweak.

These decisions should be fixed on paper before code so the implementer does not improvise layout mid-rewrite.

---

## 2. Goal

Make the static reviewer *feel* like the showcase — premium, restrained, editorial, spacious, strong hierarchy, low clutter, charcoal / warm-neutral / amber — while preserving every Slice 9 function: document panels, evidence, routes, confidence, metrics, and the synthetic-only / non-advice notices. Output stays a single self-contained HTML file with no external fonts, CSS, JS, CDNs, or network requests.

---

## 3. Showcase Design System (extracted from the reference)

| Token | Value (target) | Use |
|---|---|---|
| Background | deep warm charcoal (~`#1a1714`) | page |
| Panel | slightly lifted charcoal (~`#221e19`) with 1px hairline border (~`#332f27`) | cards, confidence/action |
| Accent | amber / brass (~`#c9a24b`) | flagged values, Δ, review flag, primary button, brand mark |
| Text primary | warm off-white (~`#ece7dd`) | headings, matched values |
| Text muted | warm gray (~`#8c857a`) | labels, secondary, `—` |
| Display face | system serif/grotesque already in repo stack (no new font) | "Crosswise", section titles |
| Mono face | existing monospace stack (no new font) | column labels (`FIELD`, `INVOICE`, `PO`, `Δ`, `STATUS`), IDs, money, confidence number |

**Hard rule:** palette and type come only from already-bundled CSS stacks. **No saturated blue.** No external font import.

Editorial cues to reproduce: uppercase letterspaced mono labels; matched rows muted with `—` and `✓ match`; discrepancy rows carrying amber values, a signed `Δ`, and a `▮ review` flag; a large confidence number with a thin amber progress bar; a single amber action affordance; a three-glyph feature row; generous vertical rhythm.

---

## 4. Design Decisions to Fix Before Coding

1. **Hero case = the first reviewable discrepancy story**, chosen deterministically (stable selection — e.g. first `needs_review` case in canonical order, falling back to first non-clean case). Rendered large, with a field-comparison view (FIELD / source columns / Δ / STATUS), confidence number + bar, route/action, and an evidence line. This is the "one discrepancy story" hero.
2. **Remaining cases are condensed**, not deleted: each becomes a compact, lower-density row/card below the hero (label, route chip, confidence, one-line evidence, link-feel into its panels) so all bundles remain present and no information is lost — just re-prioritized.
3. **Document panels are retained but restyled** to the showcase's calm aesthetic (hairline borders, more padding, muted matched fields, amber only on disagreements). The hero's comparison view and the per-bundle panels share one visual language.
4. **Above the fold = hero + notices + a thin metrics strip only.** The condensed case list and command section sit clearly below.
5. **Notices and non-advice text are preserved verbatim** and restyled as quiet editorial captions, not loud banners.

---

## 5. Scope — Files

Allowed to modify (rendering only):

- `src/crosswise/reviewer/static_html.py` — restructure story section + rewrite CSS to the design system above.
- `tests/test_reviewer.py` — update/extend assertions for the new structure (hero present, condensed cases present, notices/evidence/route still rendered, no external URLs).
- `docs/evidence/crosswise_reviewer_v1_0.html` — regenerated output.
- `docs/evidence/CROSSWISE_REVIEWER_DISCREPANCY_SHOWCASE.png` — regenerated screenshot.
- `docs/evidence/CROSSWISE_SLICE_9_DOCUMENT_PANEL_RECONCILIATION_VIEW_v1.0.md` — note the visual-alignment refinement.

**Out of scope (must not change):** reconciliation, evaluation, reliability, generation/data, metrics, routes; the prototype ZIP; any external font/CSS/JS/CDN/network dependency; any framework, server, or `package.json`.

---

## 6. Implementation Steps

1. Define CSS custom properties for the showcase tokens (Section 3); remove dashboard-era density rules.
2. Add a deterministic hero-case selector helper (presentation-only; reads existing reconciliation/reliability outputs, computes nothing new).
3. Render the hero: field-comparison view + confidence (number + amber bar) + route/action + evidence line.
4. Restyle document panels (hairline borders, padding, muted matched fields, amber-only discrepancies) shared by hero and condensed cases.
5. Render the condensed case list for all remaining bundles (compact, lossless).
6. Restyle notices/metrics/commands as quiet editorial elements; preserve synthetic-only and non-advice text verbatim.
7. Update `tests/test_reviewer.py` to the new structure and re-assert "no external URLs."
8. Regenerate `crosswise_reviewer_v1_0.html` and the screenshot.

---

## 7. Acceptance Criteria

- Reviewer still generated by `python3 scripts/generate_reviewer.py`.
- Screenshot regenerated and visually closer to `assets/prototypes/crosswise-showcase.png` (one hero discrepancy story, more whitespace, stronger hierarchy, fewer cases above the fold).
- Charcoal / warm-neutral / amber palette; no saturated blue; no dashboard clutter.
- Synthetic-only and non-advice notices preserved; evidence and route information preserved for every bundle.
- Self-contained HTML; no external fonts, CSS, JS, CDNs, or network requests; no external URLs.
- No logic changes beyond rendering.
- `python3 -m pytest tests/test_reviewer.py tests/test_reproduction_path.py` passes.
- `git status --short` reported.

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| CSS rewrite causes layout regressions in condensed cases. | Keep one shared panel style; verify all ten bundles still render via tests + screenshot. |
| Hero selection becomes non-deterministic and breaks reproducibility. | Select hero by stable canonical ordering; assert the chosen hero in tests. |
| "Premium" polish hides or drops evidence/route detail. | Acceptance requires evidence + route preserved for every bundle; condensed cards are lossless, not truncated. |
| Drift toward a field-comparison table that abandons Slice 9's document panels. | Retain document panels; the hero comparison view supplements, does not replace, the panel language. |
| Accidental external dependency (font/icon/CDN) sneaks in. | Glyphs via Unicode/CSS only; test re-asserts no external URLs. |

---

## 9. Validation (post-implementation)

```bash
python3 scripts/generate_reviewer.py
python3 -m pytest tests/test_reviewer.py tests/test_reproduction_path.py
git status --short
```

---

*Document version 1.0. Plan only — no code changes in this artifact. Visual-alignment (rendering) scope only; reconciliation, evaluation, reliability, data, metrics, and routes are out of scope. Crosswise name, direction, and scope boundaries are fixed.*
