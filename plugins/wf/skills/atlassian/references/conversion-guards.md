# Conversion guards

## Contents

- Boundaries
- Lint policy
- Fidelity and degradation
- Conversion errors
- Verification
- Python alternatives

## Boundaries

Confluence fetch, publish, and offline `map-markdown` conversion validate the supported ATL dialect and semantic round trip. Raw converter modules remain pure; Jira's in-process wrappers keep their existing policy. Install `scripts/requirements.txt` before guarded conversion; it pins `pymarkdownlnt==0.9.41`. No Node.js, credentials, network, or Atlassian library is needed for offline mapping.

Publish validates the publishable source, then the converted ADF before any remote mutation. The full pipeline extracts images and Mermaid before converting text. Offline mapping rejects images and unsupported languages; use Publish page for attachments and diagrams. It also rejects reference links, indented code, unsupported HTML/comments, malformed markers, and layout markers with no applicable following block. Errors name a line in the publishable Markdown or a semantic ADF path. Ignored local sections are removed without modifying the source file; code examples of ignore markers remain literal.

Fetch checks ADF before attachment retrieval, then validates assembled Markdown before an atomic UTF-8 replacement. A failure preserves an existing destination. Attachment caches can already have changed; attachment degradation still follows `auto|skip|required`. Offline CLI writes no partial result on validation failure; shell redirection itself can still truncate its destination.

## Lint policy

The packaged `scripts/config/confluence-markdown.json` is the only runtime lint policy. PyMarkdown runs through its Python API in a child process with an empty temporary working directory. Caller config, CWD, and source pragmas cannot weaken the gate. Missing dependency/profile or a worker failure blocks conversion; never install dependencies automatically or bypass validation.

| Rule | Runtime policy |
|---|---|
| MD010 | Reject tabs outside code blocks |
| MD012 | At most two consecutive blank lines |
| All other generic rules | Disabled; conversion checks enforce fidelity and syntax |

The explicit allowlist avoids editorial constraints on valid Confluence exports: fragments need no H1, ordered lists can start at any number, headings can repeat, language-free fences are supported, panels can be adjacent, and `<details>`, `<summary>`, `<br>` and ATL metadata are intentional. The full conversion fixture is tested against this profile. Repository-wide Markdown linting may enforce a stricter authoring style separately.

Validate only. Do not run generic autofix, trim code or hard-break whitespace, rewrite wording, or reformat source files.

## Fidelity and degradation

Compare exact text, code, hard breaks, list structure/order, marks/link targets, table structure/cells, status values, expands, comment IDs/spans, and layout metadata. Canonical render/parse must reach a fixed point after one cycle. Normalize only named defaults, numeric representation, mark order, adjacent equal-mark text segments, generated `localId`, and the existing `shell`/`bash` alias.

Smart cards use a paired `adf:inline-card` marker around a visible URL link and round-trip to `inlineCard`. Heading bookmarks/page-creation buttons and non-comment annotations have no reverse mapping. Headerless tables and merged cells cannot round-trip through this Markdown dialect. Non-reproducible column widths are reported. Offline export warns; Fetch page records each warning as a document-level conversion error (see below).

## Conversion errors

Fetch page and Fetch work never drop the whole file for content they cannot convert. Each failure becomes an `adf:error` tag, the file is still written, exit is 0, and stderr says `warning: <N> conversion error(s) tagged with adf:error in <file>`.

- **Node failure** (unhandled node, extension, inline node; malformed table or card) → the node is replaced in place by one line, valid inside paragraphs, lists, and table cells:
  `<!-- adf:error id="e1" node="<adf type>" -->⚠️ **Conversion error e1:** <reason>`
- **Document failure** (`node="doc"`): lossy-export warnings, round-trip check failure, non-object/invalid ADF body, or Fetch page's final Markdown validation/lint failure → the same line after the body.
- **Details:** a trailing `<!-- adf:ignore:start -->` `## Conversion errors` section lists each id, node type, reason, and the failed node's raw ADF in a ```` ```json ```` fence. Read it to recover lost content.
- **Publishing:** Publish page, Publish work, and offline `md-to-adf` reject any file that still has an `adf:error` tag (`line <n>: unresolved conversion error <id> (adf:error)`), before any remote call. Restore the content in supported Markdown, or accept its loss explicitly, then delete the tag line. **MUST NOT** delete a tag just to make publishing pass without telling the user what was lost.
- REST, auth, and `--attachments required` failures are not conversion errors; they still exit non-zero with no file.

Media/Draw.io use typed metadata and existing attachment extraction/substitution, since pure placeholders have no complete reverse conversion. Unresolved attachment/diagram placeholders block publishing. Final ADF is checked again before update. Failures after uploads or placeholder creation retain existing partial-create reporting; they are not rolled back automatically.

Literal Markdown in ADF is escaped; code spans/fences use safe delimiters; hard breaks and escaped table-cell pipes survive both directions.

## Verification

`publish-page run` returns `manifestPath` next to its `adfPath`. The manifest contains the expected title and ADF, including resolved media identifiers. Extend the existing read-only verify command:

```bash
<atl> publish-page verify \
  --page-id <pageId> --expect-anchors <count> \
  --expected-manifest <manifestPath> --verify-dir <workingDir>/verify
```

Existing anchor/phrase checks remain. Manifest verification fetches raw server ADF, independently of the exported Markdown; it detects structural/mark/media-ID changes even when phrases match. It preserves column widths and media identity, normalizing generated local IDs and media collection metadata. Mismatch returns nonzero and retains artifacts. No test writes or automatic republish.

## Python alternatives

- PyMarkdown: selected for rule validation and a Python API.
- `mdformat`: optional formatter; its Markdown AST check does not prove ATL marker fidelity. Add only after dialect tests demonstrate preservation.
- `markdown-it-py`: optional independent parser for CommonMark comparisons, not a linter or a Confluence-preservation guarantee.

Do not add a second runtime linter without a demonstrated gap.
