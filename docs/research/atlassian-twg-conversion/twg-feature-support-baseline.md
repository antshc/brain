# Baseline capability inventory — current ADF↔Markdown converter

Part of [Research: twg-html vs twg-md feature support against the current converter](https://github.com/antshc/brain/issues/397). Route: How (focused, Concise). Revision: `main` @ `ed9e7ef1`. Status: complete.

## Answer

The current converter has **37 regression capabilities** (`capabilities.py`) and **14 further converter behaviours** that only the Markdown/ADF converter tests assert. Together these 51 rows are the compatibility-matrix rows. Of them, 18 depend on REST operations beyond body conversion: attachments, comments, custom content, page identity and live-ADF reads for guards. These cannot be decided by twg body format alone.

The catalogue has no `M04` id. The regression README's code-link capability was replaced on `main` by the conversion guard B-12, which degrades linked code to a plain link and warns.

## Regression capabilities

Sources: [capabilities.py](../../../tests/wf/atlassian/regression/scripts/capabilities.py):191-230 (catalogue), [round-trip-page.md](../../../tests/wf/atlassian/regression/fixtures/round-trip-page.md) (fixture). "REST dep" means the check needs a REST operation beyond body conversion.

<!-- adf:wide-table -->
| ID | Area | Construct | Markdown dialect form | ADF form | Product | REST dep |
|---|---|---|---|---|---|---|
| P01 | Publish | Create page, title | `# Title` H1 | page title + body | Confluence | create page, returns `pageId` |
| P02 | Publish | Two Mermaid diagrams | fenced `mermaid` + `%% diagram-id:` | rendered media or Draw.io extension | Confluence | render, upload, custom content |
| P03 | Publish | Diagrams + local files | `![img](assets/…)`, `[file](assets/…)` | media attachments | Confluence | attachment upload |
| F01 | Fetch | Title once | `# <title>` | page title (separate) | Confluence | page read |
| F02 | Fetch | Ignore block removed | `<!-- adf:ignore:start/end -->` | none | Confluence | — |
| M01 | Structure | TOC | `<!-- adf:toc -->` | `expand` + `extension` `toc` | Confluence | — |
| M02 | Structure | H2–H6 | `##`…`######` | `heading.level` | both | — |
| M03 | Marks | strong/em/code/link/strike | `**` `*` `` ` `` `[]()` `~~` | text marks | both | — |
| M05 | Marks | strong + link | `**[t](u)**` | `link`+`strong` on one node | both | — |
| M06 | Marks | partially bold link label | `[a **b** c](u)` | split linked text nodes | both | — |
| M07 | Inline | Six status colours | `⚪🟣🔵🔴🟡🟢[text]` | `status` (text, color) | both | — |
| M08 | Inline | Legacy status | `[STATUS:t\|green]` → `🟢[t]` | `status` | both | — |
| L01 | Lists | Nested bullets | indented `-` | nested `bulletList` | both | — |
| L02 | Lists | Soft-wrapped item | continuation line → joined with space | one paragraph | both | — |
| L03 | Lists | Ordered start ≠ 1 | `3.` | `orderedList.attrs.order` | both | — |
| L04 | Lists | Mixed nesting | bullet in ordered | nested lists | both | — |
| L05 | Lists | Table in list | indented table → emitted after list | table sibling after list | both | — |
| B01 | Blocks | Blockquote | `> …` | `blockquote` | both | — |
| B02 | Blocks | Five panels | `> [!INFO\|NOTE\|WARNING\|SUCCESS\|ERROR]` | `panel.panelType` | both | — |
| B03 | Blocks | Code languages | fences `python`/`bash`/none/`plaintext` | `codeBlock.language` (`bash`↔`shell`) | both | — |
| B04 | Blocks | Rule | `---` | `rule` | both | — |
| B05 | Blocks | Expand | `<details><summary>T</summary>…</details>` | `expand.title` | both | — |
| B06 | Blocks | Expand breakout | `<!-- adf:breakout mode="wide" width="760" -->` | `breakout` mark on `expand` | Confluence | — |
| B07 | Blocks | Code breakout | breakout comment before fence | `breakout` mark on `codeBlock` | Confluence | — |
| T01 | Tables | Header table | pipe table | `table`/`tableHeader`/`tableCell` | both | — |
| T02 | Tables | Multiline cell | `<br>` in cell | `hardBreak` | both | — |
| T03 | Tables | Wide layout | `<!-- adf:wide-table -->` | `table.layout=wide` | Confluence | — |
| T04 | Tables | Layout + width | `<!-- adf:table layout="wide" width="960" -->` | `table.layout`, `table.width` | Confluence | — |
| D01 | Diagrams | Flowchart restored | mermaid fence restored on fetch | attachment + `.source.mmd` sidecar | Confluence | attachment list/download |
| D02 | Diagrams | Sequence restored | as D01 | as D01 | Confluence | attachment list/download |
| A01 | Attachments | Image bytes + size/layout | image link + `<!-- media-size: … -->` | `mediaSingle`/`media` | Confluence | upload, download, byte compare |
| A02 | Attachments | File bytes/link | `[file](ASSETS/file)` | `mediaGroup`/`media` | Confluence | upload, download |
| C01 | Comments | Inline-comment anchor | `<!-- adf:comment id="…" -->text<!-- /adf:comment -->` | `annotation` mark (inlineComment) | Confluence | comment fetch; live-ADF guard |
| C02 | Comments | Page/footer comments section | ignored `## Comments` block | not body ADF | Confluence | comment REST read |
| R01 | Republish | Update in place | same `pageId` | page update | Confluence | REST update |
| R02 | Republish | No detached comments | guard report empty | anchors preserved | Confluence | live-ADF/comment guard |
| R03 | Republish | Diagrams replaced in place | two diagrams | attachment/custom content update | Confluence | custom content, attachments |
| R04 | Republish | Idempotent round trip | fetch-1 ≡ fetch-2 | stable ADF↔MD | Confluence | publish + fetch |
| R05 | Republish | Anchor survives update | C01 regex on fetch-2 | same annotation id | Confluence | fetch + guard |

## Converter-test behaviours beyond the catalogue

Sources: [map-markdown-adf tests](../../../tests/wf/atlassian/map-markdown-adf/), [map-markdown-adf.md](../../../plugins/wf/skills/atlassian/references/map-markdown-adf.md).

<!-- adf:wide-table -->
| ID | Behaviour | Markdown form | ADF form | Direction | Evidence |
|---|---|---|---|---|---|
| B-01 | Status edge cases | emoji before link, variation selector; unknown colour → `[STATUS:t\|c]` | `status` | both | `test_md_to_adf.py`, `test_adf_to_md.py` |
| B-02 | inlineCard normalisation | `[url](url)`; empty url → error | `inlineCard` | ADF→MD | `test_adf_to_md.py` |
| B-03 | Dropped inline extensions | — | `create-from-template`, `anchor` dropped | ADF→MD | `test_adf_to_md.py` |
| B-04 | Nested/wrapping comment anchors | nested tags; literal inside code spans; split by hardBreak | per-node `annotation` | both | `test_inline_comments.py` |
| B-05 | Lists/containers/hard breaks | standard | lists, blockquote, codeBlock, hardBreak | both | `test_adf_to_md.py`, `test_md_to_adf.py` |
| B-06 | Table grid validation | ragged table rejected, no partial output | consistent width after spans | guard | `test_table_validation.py`, `test_conversion_guard.py` |
| B-07 | Merged cells | none (validation only) | `colspan`/`rowspan` | ADF→MD validation | `test_table_validation.py` |
| B-08 | Pipes and `<br>` in cells | escaped pipe, `<br>` | `hardBreak` | both | `test_conversion_guard.py` |
| B-09 | Table layout/breakout placement | `adf:table`, `adf:wide-table`, breakout before details/code only | attrs / `breakout` | both + validation | `test_round_trip.py` |
| B-10 | TOC inside breakout expand | `<!-- adf:toc -->` | `expand`+`toc` with local breakout | both | `test_round_trip.py` |
| B-11 | Fence/dialect rejection | long fences; unsupported language or indented code rejected | `codeBlock.language` | guard | `test_conversion_guard.py`, `test_md_to_adf.py` |
| B-12 | Literal fidelity; linked code | backticks/spaces kept; `` [`x`](u) `` → `[x](u)` + warning | marks | both | `test_conversion_guard.py`, `test_round_trip.py` |
| B-13 | ADF-only detection report | kinds + 1-based line | breakout, expand, inlineComment, panel, status, tableLayout, toc, wideTable | detect | `test_detect.py` |
| B-14 | Unsupported nodes/bad tags | stray/unterminated comment tag rejected | unknown node → error | guard | `test_inline_comments.py`, `test_adf_to_md.py` |

## Not supported today

Mentions, dates, general emoji nodes, task lists, layouts (sections/columns) and arbitrary macros have no converter mapping. An unknown ADF node raises an error. These features don't need parity rows, but a twg route must not silently produce something different for them.

## Product split

- **Shared by Confluence and Jira:** core text, heading, list, table, code, blockquote and mark conversion, plus the status and panel dialect.
- **Confluence only:** title, TOC, breakout and table layout, inline comments, Draw.io and Mermaid diagrams, `media-id` attachment resolution, custom content.
- **Jira only:** Publish work and Fetch work use REST v3 ADF descriptions, resolve attachments by filename, and read comments through twg (`publish_work.py`:82-106, 147-174; `fetch_work/fetch_attachments.py`).
