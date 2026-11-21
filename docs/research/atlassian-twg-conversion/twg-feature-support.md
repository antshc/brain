# twg-html vs twg-md feature support — combined report

Ticket: [Research: twg-html vs twg-md feature support against the current converter](https://github.com/antshc/brain/issues/397). Baseline: `main` @ `ed9e7ef1`, twg 1.4.2. Status: **partial**. The documentation matrix is complete. The authenticated `body-formats` references and live samples are blocked by a malformed preflight config.

Parts:

- [Baseline capability inventory](twg-feature-support-baseline.md): the 51 matrix rows.
- [twg documentation and CLI help](twg-feature-support-twg-docs.md): what twg documents, with citations.

## Answer

- **Documentation alone cannot establish byte-identical parity for either route.** twg owns its own HTML and Markdown conversions and publishes no per-node contract for them.
- **twg-md** is documented as lossy for most of the ADF-only dialect: panels, status and emoji become text; macros (TOC, Draw.io) become placeholders; layouts may be lost. Byte parity with today's dialect (`> [!INFO]`, `🟢[x]`, `<!-- adf:toc -->`, `<!-- adf:comment -->`) would need post-processing that has to rebuild information twg-md no longer carries. Several rows are therefore expected to be **lost** on twg-md.
- **twg-html** is documented as the lossless editing format, with extension HTML for macros. It is the only route where every ADF construct can in principle be represented. Our dialect would come from a Markdown package plus custom handlers. The prototypes must confirm this.
- **Jira fetch reads ADF from twg**, so it can reuse the current ADF→Markdown converter. Expected verdict for the read side: twg automatic, with no change to the converter.
- **REST-only rows have twg equivalents for attachments and inline comments.** Custom content (Draw.io records) has no twg command found and is a likely candidate for "keep REST fallback".

## Compatibility matrix (documented support)

Cell meanings:

- **doc✔**: documented as supported or preserved.
- **text**: documented to flatten to text.
- **ph**: documented as a macro placeholder.
- **lossy**: documented as possibly lost.
- **undoc**: not documented, so it needs the prototype.
- **ADF**: the current ADF converter can be reused.
- **cmd**: a non-body twg command exists.

"Publish" means Markdown → twg write. "Fetch" means twg read → Markdown.

<!-- adf:wide-table -->
| Row | Construct | twg-html publish | twg-html fetch | twg-md publish | twg-md fetch | Jira publish (html/md) | Jira fetch |
|---|---|---|---|---|---|---|---|
| P01 | Create page/title | doc✔ (`create --title`) | n/a | doc✔ | n/a | doc✔ | n/a |
| P02, R03 | Mermaid diagrams, replace in place | undoc (attachment cmd; custom content: none) | — | lossy | — | n/a | n/a |
| P03, A01, A02 | Attachments, media size | cmd upload; media node form undoc | cmd download; media form undoc | lossy | lossy (media may be missing) | cmd | ADF |
| F01 | Title once | n/a | doc✔ (envelope) | n/a | doc✔ | n/a | ADF |
| F02 | Ignore block | client-side strip | n/a | client-side strip | n/a | client-side | n/a |
| M01, B-10 | TOC | doc✔ (extension HTML `toc`) | undoc form | ph | ph | n/a | n/a |
| M02 | H2–H6 | doc✔ | doc✔ | doc✔ | doc✔ | doc✔ | ADF |
| M03, M05, M06, B-12 | Marks, combined/partial link marks | doc✔ (structural tags) | undoc exact form | undoc | undoc | undoc | ADF |
| M07, M08, B-01 | Status lozenges | undoc form | undoc form | text | text | undoc | ADF |
| L01–L05, B-05 | Lists, table after list | doc✔ structural | undoc exact form | undoc | undoc | undoc | ADF |
| B01 | Blockquote | doc✔ | undoc | undoc | undoc | undoc | ADF |
| B02 | Panels | undoc form | undoc form | text | text | undoc | ADF |
| B03, B-11 | Code language | undoc | undoc | undoc | undoc | undoc | ADF |
| B04 | Rule | doc✔ | undoc | undoc | undoc | undoc | ADF |
| B05 | Expand | doc✔ (`bodied-extension` / expand) | undoc | lossy | lossy | undoc | ADF |
| B06, B07, B-09 | Breakout | undoc | undoc | lossy (layout) | lossy | n/a | n/a |
| T01, T02, B-08 | Tables, `<br>` cells | doc✔ structural | undoc | undoc | undoc | undoc | ADF |
| T03, T04, B-09 | Table layout/width | undoc | undoc | lossy | lossy | n/a | n/a |
| B-07 | Merged cells | undoc | undoc | undoc | undoc | undoc | ADF |
| D01, D02 | Diagram source restored | cmd download sidecar | cmd download sidecar | lossy | lossy | n/a | n/a |
| C01, B-04, R05 | Inline-comment anchor | doc✔ via targeted `--edits` (preserve untouched nodes); full-body form undoc | doc✔ marker `data-annotation-id` present in HTML | lossy | lossy | n/a | n/a |
| C02 | Comments section | cmd `comments list` | cmd | cmd | cmd | twg (already) | twg (already) |
| R01 | Update in place | doc✔ (`update` + snapshot token) | — | doc✔ | — | doc✔ | — |
| R02 | Comment guard (live read) | cmd + html read | — | lossy | — | n/a | — |
| R04 | Idempotent round trip | undoc | undoc | unlikely (lossy) | unlikely | undoc | ADF |
| B-02, B-03 | inlineCard, dropped extensions | — | undoc | — | 1.4.2 preserves some embed links | — | ADF |
| B-06, B-13, B-14 | Validation, detection, error guards | client-side (converter) | client-side | client-side | client-side | client-side | client-side |

## Consequences for the prototypes

1. **Prototype A (twg-html + package)** must observe twg's actual HTML form for:
   - every "undoc" row on the html side, especially status, panel, expand, breakout, table layout and width, code language, media and annotation marks;
   - whether a full-body HTML update keeps comment anchors, or whether only targeted `--edits` do.
2. **Prototype B (twg-md)** is expected to be lost on rows M01, M07, M08, B02, B05, B06, B07, T03, T04 and C01. It should confirm these, and check whether any twg-md output can be post-processed back to the dialect without lost information.
3. **For Jira**, both prototypes can share the fetch side, because twg returns ADF and the current converter applies unchanged. Only the publish side (html vs md description) differs.
4. **[Research: HTML↔Markdown package shortlist for the twg-html route](https://github.com/antshc/brain/issues/398)** needs the `body-formats html` schema to judge whether packages can handle the extension-HTML element set. That retrieval is the blocked gap.

## Gaps

The authenticated twg checks are blocked because `.github/skills/preflight-atlassian/.atlassian.json.user` is invalid JSON (`Extra data: line 15 column 1`). Once it is fixed, rerun:

- `body-formats html` and `body-formats md`;
- a live read of a rich page in both formats;
- `jira workitem get ZIC-5914`.

Then resolve the "undoc" cells on the read side.
