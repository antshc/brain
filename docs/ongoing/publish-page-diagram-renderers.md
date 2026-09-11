# Publish Page Diagram Renderers

Status: planned

## Goal

Extend `publish-page` with two Mermaid rendering modes:

- `png` — render Mermaid to PNG with Mermaid CLI.
- `drawio` — render Mermaid to an editable Draw.io diagram and publish it to Confluence.

Renderer selection is configured in `.atlassian`.

## 1. Configuration

Add:

```text
ATLASSIAN_DIAGRAM_RENDERER=png
```

Supported values:

- `png`
- `drawio`

Default to `png` for backward compatibility.

Update `init-atl` to add/prompt this key and document it in `preflight-atl`.

`publish-page` reads the setting through the existing `.atlassian` parser.

## 2. Temporary files

Replace the current default `<md-stem>.artifacts` location with a folder next to the Markdown source:

```text
docs/design.md
docs/design.md.tmp/
  final-adf.json
  00-overview.mmd
  ...
```

The exact convention is `<markdown filename>.tmp`, including the `.md` suffix.

Keep `--assets-dir` and `--out` as explicit overrides if needed.

## 3. Renderer dispatch

Refactor the current PNG-only `render_diagrams()` implementation into renderer-specific paths:

```text
mermaid
  ├─ png renderer
  └─ drawio renderer
```

The pipeline selects the renderer from `ATLASSIAN_DIAGRAM_RENDERER`.

Unknown values fail before creating or updating a Confluence page.

## 4. PNG renderer

Keep the existing behavior:

```text
Mermaid -> mmdc -> PNG
```

Preserve current theme handling, background handling, attachment upload, and ADF `mediaSingle` substitution.

## 5. Draw.io renderer

Add Draw.io Desktop CLI as a prerequisite for `drawio` mode.

Target flow:

```text
Mermaid source
    -> Draw.io CLI/import
    -> .drawio
    -> Draw.io CLI
    -> preview PNG
```

Generated files per diagram:

```text
00-overview.mmd
00-overview.drawio
00-overview.drawio.png
```

Missing Draw.io CLI must fail explicitly and name `drawio` as the missing prerequisite.

Validate the exact Draw.io CLI/import command during implementation against the installed/current CLI version rather than hard-coding an unverified command shape.

## 6. Confluence Draw.io representation

For `drawio` mode upload both:

```text
00-overview.drawio
00-overview.drawio.png
```

Replace each Mermaid marker with an actual Confluence Draw.io macro rather than the existing generic PNG `mediaSingle` node.

Reuse the existing generic recursive marker-substitution mechanism instead of introducing another ADF traversal.

Before hard-coding the macro ADF shape, capture one real Draw.io diagram from Confluence using `body-format=atlas_doc_format`. Draw.io Connect and Forge installations can use different extension/macro representations.

## 7. Attachment layer

Generalize `upload_diagrams()`, which currently assumes one PNG attachment per diagram.

Renderer behavior:

```text
png    -> 1 attachment per diagram
drawio -> .drawio + preview PNG per diagram
```

Return attachment metadata by diagram/index instead of assuming a single `filename` field.

## 8. Pipeline

Keep the existing high-level pipeline:

```text
extract
  -> Markdown to ADF
  -> create/resolve page
  -> render
  -> attach
  -> substitute
  -> publish
```

Add the selected renderer to the result JSON, for example:

```json
{
  "renderer": "drawio",
  "diagrams": 2,
  "attachments": 4
}
```

## 9. Tests

Extend the existing test suite:

- `test_env.py`
  - renderer config
  - default `png`
  - invalid renderer
- `test_mermaid.py`
  - existing PNG behavior unchanged
  - Draw.io CLI invocation
  - generated `.drawio` and preview paths
- `test_attachments.py`
  - one attachment for PNG
  - two attachments for Draw.io
- `test_adf.py`
  - Draw.io macro substitution
  - nested diagram substitution
- `test_cli.py`
  - `<markdown filename>.tmp` defaults
  - missing `mmdc`
  - missing `drawio`
- `test_pipeline.py`
  - PNG renderer branch
  - Draw.io renderer branch
  - invalid renderer fails before publish

Run:

```bash
python -m pytest plugins/atl/skills/publish-page/
```

## 10. Documentation

Update:

- `plugins/atl/skills/publish-page/SKILL.md`
- `plugins/atl/skills/init-atl/SKILL.md`
- `plugins/atl/skills/preflight-atl/SKILL.md`

Document:

- `ATLASSIAN_DIAGRAM_RENDERER`
- supported values
- default behavior
- Mermaid CLI prerequisite for `png`
- Draw.io CLI prerequisite for `drawio`
- `<markdown filename>.tmp` artifact location
- Draw.io attachment/macro behavior

## Design decision

`drawio` means an actual editable Confluence Draw.io diagram, not only a PNG rendered by Draw.io.

This keeps the two renderer modes semantically distinct:

```text
png    -> static Confluence image
drawio -> editable Confluence Draw.io diagram
```
