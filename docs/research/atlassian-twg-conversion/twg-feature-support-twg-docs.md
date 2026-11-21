# twg body-format support — documentation and CLI help

Part of [Research: twg-html vs twg-md feature support against the current converter](https://github.com/antshc/brain/issues/397). Routes: How (focused, installed `twg` 1.4.2 help and repository references) and Web (Atlassian primary sources). Status: **partial**. The authenticated runtime checks are blocked (see Gaps).

## Answer

twg 1.4.2 documents two Confluence body formats, `html` (the default) and `md`. HTML is the format it calls lossless for editing. Markdown is documented as lossy:

- panels, status lozenges and emoji become plain text;
- other macros become placeholders;
- layouts and ADF-only nodes may be lost.

No source documents byte-identical Markdown output, or any per-node mapping for twg's HTML.

For Jira, twg **writes** descriptions from HTML, Markdown or plain text, but **reads them back as raw ADF**. A twg Jira fetch can therefore feed the current ADF→Markdown converter unchanged.

Attachments (upload and download) and inline comments (list, and create with a text selection) have their own twg commands. So none of the REST-only rows is ruled out on documentation grounds.

## Confluence body formats

- **Read.** `twg confluence content get --help` (line 25) lists the formats: `html (default), md (alias: markdown; panels, status and emoji render as text, other macros as placeholders)`. `--detail full` returns the body in the requested format, and `--body-only` emits the body without the metadata envelope. The help examples include `content get 12345 --detail full --format html --body-only --output-file ./page.html -o json`.
- **Write.** `content create` and `content update` take `--body`/`--body-file` with `--format html|md` and `--ack-body-formats`. The help says to "Strongly prefer --format html: Markdown is lossy for rich Confluence content (macros, layouts, panels, ADF-only nodes)", and to use md only for pages originally authored in Markdown. Classic pages need the `--snapshot-token` from a `--draft --detail full` read. The targeted `--edits`/`--edits-file` options take HTML node values keyed by `localId` and "preserve untouched nodes exactly". `--dry-run` validates input but does not preview the converted result.
- **HTML dialect.** The repository reference [body-formats.md](../../../plugins/wf/skills/atlassian/references/twg/confluence/body-formats.md):9-12 calls HTML "the preferred lossless editing format". Lines 29-35 of the same file say macros are written as extension HTML, for example `<div data-type="extension" data-extension-key="toc" …>`, never `<ac:structured-macro>`. They also cover `bodied-extension` for body macros and `inline-extension` for inline macros such as `anchor`. The full compact schema comes from `twg confluence content body-formats html`, which requires authentication and is **not retrieved** (see Gaps).
- **Markdown.** Lines 39-50 of the same file say Markdown "may not preserve every macro or storage-format construct during round trips". The routing note in [twg.md](../../../plugins/wf/skills/atlassian/references/twg.md):28-30 says Markdown page reads can lose diagrams, media, attachments and comments.
- **Upstream conversion.** Confluence REST documents only `atlas_doc_format ↔ storage` and editor/view conversions, with no HTML or Markdown representation ([Content body API, supported conversions](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content-body/)). twg's HTML and Markdown are therefore twg-owned conversions, and no public contract specifies them. The public changelog lists only narrow fixes to Markdown reads, such as embedded-content links (1.4.2) and inline attachment media (1.4.3) ([TWG CLI changelog](https://atlassian.github.io/twg-cli/changelog/)).

## Jira

- **Write.** `twg jira workitem create --help` and `update --help` accept `--description` with `--description-format html|markdown|plain`. HTML is the default and Jira wiki markup is rejected.
- **Read.** `twg jira workitem get --help` has no format selector. [rich-content.md](../../../plugins/wf/skills/atlassian/references/twg/jira/rich-content.md):14-20 says descriptions and comments "read back as ADF documents, not strings". Rich custom fields need raw ADF through `--field`/`--fields-json`.
- **Platform.** Jira REST v3 accepts descriptions only as ADF ([Jira REST v3 Issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)). twg converts HTML or Markdown to ADF on write, and that conversion is undocumented.

## Non-body operations

| Capability | twg command | Evidence |
|---|---|---|
| Confluence attachment upload/download/list | `confluence content attachments list/get/upload/download/delete` | `twg confluence content attachments --help` |
| Jira attachment upload/download | `jira` attachment query/get/download/upload/delete | `twg help attach` |
| Inline comments, read | `content comments list` returns footer and inline comments; inline ones carry `inlineOriginalSelection` and `inlineMarkerRef` (the highlight's `data-annotation-id`) | [content.md](../../../plugins/wf/skills/atlassian/references/twg/confluence/content.md):212-225 |
| Inline comments, write | `comments create --comment-type inline --text-selection …` | `twg confluence content comments create --help` |
| Labels | `content labels add/list/remove` | `twg confluence content labels --help` |
| Custom content (Draw.io records) | not found in help | `twg help confluence content` |

## Gaps

- **Blocked.** Every authenticated check failed in the preflight launcher with `error: unreadable or malformed Atlassian config`. The config file `.github/skills/preflight-atlassian/.atlassian.json.user` does not parse (`JSONDecodeError: Extra data: line 15 column 1`). As a result, these were not retrieved:
  - `content body-formats html` and `content body-formats md`, which are the authoritative markup references;
  - live `content get 3159687231` in both formats, plus the child-page tree;
  - live `jira workitem get ZIC-5914`.
- **Next check after the config is fixed.** Run `twg_cred.py confluence content body-formats html` and the same for `md`. Read one rich page in both formats, then `jira workitem get ZIC-5914 -o json`.
- **Undocumented everywhere.** No checked source gives the per-construct twg HTML or Markdown form for expand, breakout, table layout and width, merged cells, code-block language, mentions, dates, media sizing, or annotation marks. These cells stay "undocumented" until a body-formats retrieval or a prototype observes them.
