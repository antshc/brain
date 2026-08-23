# ADF mapping used by `publish_zdesign.py`

Distilled from [`markdown-to-adf`](../../markdown-to-adf/SKILL.md) and
[`adf-builder-coverage.md`](../../../adf-builder-coverage.md), extended with the nodes a
`to-zdesign` document needs that plain Markdown has no syntax for.

## Block nodes

| Markdown | ADF node |
| --- | --- |
| `#`-`######` | `heading` (`attrs.level` 1-6) |
| paragraph | `paragraph` |
| `- `/`* `/`+ ` list | `bulletList` > `listItem` |
| `1. ` list | `orderedList` > `listItem` |
| `> ` | `blockquote` |
| fenced code block | `codeBlock` (`attrs.language` from an allow-list; omitted if unknown) |
| `---`/`***`/`___` alone on a line | `rule` |
| GFM pipe table | `table` > `tableRow` > `tableHeader`/`tableCell` |
| `<details><summary>Title</summary>…</details>` | `expand` (`attrs.title` = summary text) |
| ` ```mermaid ` fenced block | `mediaSingle` > `media` (rendered to PNG, uploaded as an attachment — **not** a `codeBlock`; ADF has no native diagram node) |
| `<!-- confluence:toc -->` HTML comment | `expand` (title="Table of Contents") wrapping a native `toc` extension macro node — position-based, placed exactly where the comment appears in the source |

## Inline marks

| Markdown | ADF mark |
| --- | --- |
| `**text**` | `strong` |
| `*text*` | `em` |
| `` `text` `` | `code` |
| `~~text~~` | `strike` |
| `[text](url)` | `link` (`attrs.href`) |
| `<br>` inside a table cell or paragraph | `hardBreak` node (splits the text run, not a mark) |

## Media node shape

Confirmed empirically against Confluence Cloud (2026-08-21): the `media.attrs.id` is **not** the
attachment's content id (`att123...`) returned by `attach_file`/`create_page`. It is the
media-services `fileId` (a UUID), only visible by re-fetching the attachment with
`expand=extensions.fileId`. `media.attrs.collection` is the literal string
`contentId-<pageId>`.

```json
{
  "type": "mediaSingle",
  "attrs": { "layout": "center", "width": 768, "widthType": "pixel" },
  "content": [
    {
      "type": "media",
      "attrs": {
        "id": "<extensions.fileId, a UUID>",
        "type": "file",
        "collection": "contentId-<pageId>"
      }
    }
  ]
}
```

Because re-uploading a same-named file creates a new attachment **version** (not a new
attachment), the fileId must be re-read after every upload — never cached across runs, since
Confluence issues a new fileId per version.

Without an explicit `mediaSingle.attrs.width`/`widthType`, Confluence renders the image at its
source pixel dimensions (confirmed: a 1×1 test PNG round-tripped with `width: 1`). The script
fixes this at `--image-width` (default `768`) so every diagram renders at a consistent size
regardless of the PNG's actual rendered resolution (`mmdc -w 1040 -s 2` → ~2048px wide).

## Table of Contents macro

Confirmed empirically (2026-08-21): publishing an `extension` node with only
`extensionType`/`extensionKey`/`parameters.macroParams: {}` is sufficient — Confluence
auto-fills `parameters.macroMetadata` (`macroId`, `schemaVersion`, `title`) on save, so the
script never has to generate a `macroId` itself.

```json
{
  "type": "extension",
  "attrs": {
    "layout": "default",
    "extensionType": "com.atlassian.confluence.macro.core",
    "extensionKey": "toc",
    "parameters": { "macroParams": {} }
  }
}
```

Trigger: a line matching `<!-- confluence:toc -->` (case-insensitive, leading/trailing whitespace
allowed) in the source markdown. The line is replaced with an `expand` node (title="Table of
Contents") wrapping the `toc` extension macro, positioned exactly where the comment appears.
The comment is invisible in GitHub markdown rendering and is never filled by the model — `to-zdesign`
preserves it verbatim from the template.

## Ignored sections

A `<!-- confluence:ignore:start -->` / `<!-- confluence:ignore:end -->` pair marks a markdown
span (tags included) that must never reach Confluence. Unlike `confluence:toc`/`confluence:wide-table`,
which are single-line markers consumed during block parsing, this pair is stripped from the raw
markdown text before mermaid extraction and before block parsing — no ADF node is emitted, and any
```mermaid fence inside the span is never rendered or uploaded. Pairs do not nest; an unterminated
`start` (no matching `end`) raises an error rather than silently dropping the rest of the document
or silently publishing it.

## Table column widths

Requirements-style tables (`#`, `Priority`, `Source`, `Details`/`Description` columns) get
explicit `tableCell`/`tableHeader.attrs.colwidth` so the narrow identifier/metadata columns don't
crowd out the prose columns. Detection is header-name-based (case-insensitive, `**bold**` marks
stripped) and only activates when at least one of `#`/`priority`/`source` is present — tables
without those headers are left to Confluence's auto-sizing. `#`/`no` get 60px, `priority`/`source`
get 110px, and `details`/`description` columns claim ~70% of the remaining 1400px budget, with any
other columns splitting the rest. Confirmed round-trip on the Requirements table: `[60, 336, 110,
784, 110]` for `[#, Requirement, Priority, Details, Source]`.

## Wide table layout marker

A `<!-- confluence:wide-table -->` HTML comment (same convention as `<!-- confluence:toc -->`),
placed on its own line immediately before a table (blank lines in between are tolerated), sets
that table's `attrs.layout` to `"wide"` instead of the default `"default"`. Confluence's
`"default"` table layout confines a table to the normal content column (~760px), so a table whose
summed `colwidth` is close to or exceeds that (e.g. the ~1400px Requirements-table budget above)
would otherwise render squeezed/scrolled even though its per-column widths are set correctly.

This is deliberately independent of `compute_colwidths`'s header-name heuristic:

- A table can have the marker without any recognized headers — it renders in the wide layout with
  Confluence auto-sizing its columns (no `colwidth` attrs emitted).
- A table can have recognized headers (so `colwidth` is set) without the marker — it stays in
  `"default"` layout; this is discouraged since the colwidth budget assumes wide-layout space, but
  the script does not force it, since a doc author may want a narrower table to display an
  explicit column-width ratio without spilling into the page margins.

The marker line is consumed like the TOC marker (produces no ADF node). It applies only to the
very next table encountered; if the next non-blank construct after the marker isn't a table, the
marker is silently dropped rather than erroring or leaking onto a later table.

## Publish call

`atlassian-python-api` (installed version 4.0.7, confirmed — no `ADFBuilder`/`raw_node` class
exists in this version, unlike the `master`-branch API `adf-builder-coverage.md` documents; nodes
here are assembled as plain `dict`s instead):

```python
body = json.dumps(adf_doc)  # adf_doc = {"version": 1, "type": "doc", "content": [...]}
confluence.update_page(
    page_id=page_id,
    title=title,
    body=body,
    representation="atlas_doc_format",
    always_update=True,  # bypass the storage-format content-equality short-circuit
)
```

`update_page` auto-fetches and increments `version.number` internally — callers never pass a
version. `always_update=True` is required because `is_page_content_is_already_updated` compares
against the page's `storage` body, which never matches an ADF payload, but forcing the flag makes
the "every run updates the page" contract explicit rather than accidental.

## Known limitations (documented, not solved)

- **Nested marks** (e.g. a link inside bold text) are not supported — the inline tokenizer picks
  one mark per run, matching what the source documents actually use (`to-zdesign` templates use
  bold-then-plain-text, not bold-containing-a-link).
- **Code block language allow-list**: `language` is set to a Confluence-recognized value
  (`text`, `json`, `xml`, `yaml`, `bash`, `python`, `javascript`, `typescript`, `java`, `csharp`,
  `sql`, `html`, `css`, `diff`, `none`) and omitted otherwise, so an unrecognized fence language
  doesn't fail the publish call.
