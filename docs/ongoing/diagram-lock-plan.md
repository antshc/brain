# Plan: Diagram lock marker for Confluence publishes

## Goal

Let an author declare a diagram "owned by Confluence" so `/publish-page` never overwrites it — covering both the `drawio` and `png` renderers. A locked diagram is skipped; the rest of the page still publishes.

## Confirmed decisions

- Mechanic: **explicit lock marker**, not auto drift detection.
- Marker lives in the **repo mermaid source**, a sibling to `%% diagram-id:`.
- On lock: **skip that diagram, publish everything else**. No `--force` flag.
- Coverage: **drawio + png** both.

## How a locked diagram stays on the page

The ADF body is rewritten wholesale on every publish, so a "skip" still needs a node at the diagram's marker position. Mechanic: read the live page ADF once, find the node currently occupying that diagram's identity, splice it back verbatim.

Identity keys (from `mermaid.render_diagrams`):

| Renderer | Attachment / custom content title | Live node |
|---|---|---|
| `drawio` | `{name}.drawio` | `extension` node with `attrs.parameters.guestParams.diagramName == "{name}.drawio"` |
| `png` | `{name}.png` | `mediaSingle` whose inner `media` `attrs.id` is that attachment's fileId |

Lookup tries the `.drawio` key then the `.png` key, so a `drawio`-renderer diagram that previously fell back to PNG still matches.

Verbatim reuse also preserves any Confluence-side resize/layout, and avoids needing `width`/`height` — which only exist after a render we deliberately skip.

Locked diagrams must NOT reach `custom_content.upsert_diagram`: bumping the revision is exactly what makes the Draw.io app discard its render and re-read the attachment.

## Phases

### Phase 1 — Source-side marker (pure, no I/O)

1. `patterns.py`: add `DIAGRAM_LOCK_RE` mirroring `DIAGRAM_ID_RE` — whole-line match on `%% diagram-lock: <true|false>`, so stripping it leaves valid mermaid.
2. `mermaid.extract_mermaid`: parse and strip the lock line, set `d["locked"]`; raise naming the diagram when a lock appears without a `%% diagram-id:` — identity would otherwise drift with headings.
3. `mermaid.render_diagrams`: skip locked diagrams — no mmdc/drawio subprocess, `attachments = []`.

Tests: `tests/test_patterns.py`, `tests/test_mermaid.py`.

### Phase 2 — Live-node lookup (I/O; steps 4 and 5 are parallel)

4. `rest_publish.py`: add `get_page_adf(confluence, page_id)` — GET `/api/v2/pages/{id}?body-format=atlas_doc_format`, json-parse `body.atlas_doc_format.value`.
5. `attachments.py`: extract `read_attachment_file_ids(confluence, page_id)` out of `upload_diagrams`; `upload_diagrams` keeps its behaviour but no longer short-circuits to `{}` when the caller still needs the title→fileId map for locked PNGs.
6. New `page_diagrams/locked.py` (pure, given live ADF + fileId map): walk the ADF, index diagram nodes by identity key, expose the per-diagram lookup, raise naming the diagram when no live node exists. Depends on 4 and 5 for its inputs, but is itself offline.

Tests: `tests/test_rest_publish.py`, `tests/test_attachments.py`, new `tests/test_locked.py`.

### Phase 3 — Pipeline wiring (depends on Phases 1–2)

7. `pipeline._publish_with_diagrams`: partition locked/unlocked; pass only unlocked to `render_diagrams` and `upload_diagrams`; fetch live ADF once when any diagram is locked; build the `nodes_by_index` entry for locked diagrams from the reused live node.
8. `pipeline._drawio_nodes_by_index`: skip `upsert_diagram` for locked diagrams.
9. Create path (`page_id` is None) plus any locked diagram: raise before the placeholder page is created, naming the diagram. Keeps the skill's "nothing is half-published" rule.
10. Result payload: add locked diagram names/count so the caller reports what was preserved.
11. `_publish_without_credentials`: a locked diagram gets a "locked" note, not "not rendered".

Tests: `tests/test_pipeline.py`, `tests/test_cli.py`.

### Phase 4 — Docs (parallel with each other, after Phase 3 settles the grammar)

12. `plugins/atl/skills/publish-page/SKILL.md`: new "Diagram lock" subsection under "Diagram ids" — grammar, requires-an-id rule, skip-and-preserve behaviour, create-path error, how to unlock, and that a locked diagram's local assets are not regenerated.
13. `plugins/atl/skills/publish-page/README.md`: mention the marker if it lists markers.
14. The three wf diagram skills' `SKILL.md` — add the lock line beside the "Assign diagram id" step. Parallel, one edit each.
15. Each wf skill's `templates/*.md`: commented example lock line next to the diagram-id line.

## Relevant files

- `plugins/atl/skills/publish-page/scripts/page_diagrams/patterns.py` — `DIAGRAM_ID_RE` is the shape to copy.
- `.../mermaid.py` — `extract_mermaid` (id parse/strip/uniqueness), `render_diagrams` (per-renderer branch; sets `diagram_name`, `filename`, `attachments`).
- `.../pipeline.py` — `_publish_with_diagrams`, `_drawio_nodes_by_index`, `substitute_diagram_notes`, `_publish_without_credentials`.
- `.../attachments.py` — `upload_diagrams` read-back loop.
- `.../custom_content.py` — `find_diagram`, `upsert_diagram` (must not run for locked).
- `.../adf.py` — `drawio_node`, `media_node`, `substitute_drawio`, `substitute_media`, `substitute_markers`.
- `.../rest_publish.py` — `get_page_version`, `update_page_adf`.
- `plugins/atl/skills/publish-page/SKILL.md` — "Diagram ids" section.
- `plugins/wf/skills/{architecture,behavior,code}-diagram/SKILL.md` and their `templates/`.

## Verification

1. `python3 -m pytest plugins/atl/skills/publish-page/tests/ -v` — all green.
2. New unit coverage: lock parsed and stripped; lock without id errors; locked diagram not rendered; locked diagram not uploaded; `upsert_diagram` not called for locked; live extension node reused verbatim; live media node reused verbatim; drawio-name miss falls through to png-name; locked-but-never-published errors; locked on create errors.
3. Manual round trip against a real page: publish two diagrams, edit one in Confluence, add `%% diagram-lock: true` to it in the source, change the other's source, republish — confirm the edited diagram is untouched (custom content revision unchanged) and the other updates.

## Scope boundaries

- **In:** source-declared lock, skip-and-preserve, drawio + png, error paths, docs.
- **Out:** auto drift/checksum detection, Confluence-side lock declaration, `--force` override, orphan pruning, page-prose conflict guards, the `mermaid` renderer (still unusable).

## Open items to confirm

1. Marker grammar: `%% diagram-lock: true` (recommended — toggleable without deleting the line) vs bare `%% diagram-lock` as presence-only.
2. Locked diagram on a create (no pageId, nothing to protect): hard error naming the diagram (recommended) vs publish once, lock applies from then on.
3. Locked diagram's local assets in `<mdPath>.tmp/`: skip writing entirely (recommended) vs still render locally for diffing, just never upload.
