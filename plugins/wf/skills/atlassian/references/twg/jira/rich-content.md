---
description: Write Jira descriptions, comments, transition comments, mentions, and links as Markdown through atl, with raw ADF only for rich custom fields.
---

# Jira Rich Content

Write every description and comment as Markdown through `<atl>`.

- **Descriptions** default to Markdown: `--description` / `--description-file` on `<atl> jira workitem create|update` route through the skill's Markdown → ADF converter (panels, `<details>`, status, TOC, wide tables survive). Never pass `--description-format html|plain`.
- **Comments** run on twg, which defaults to HTML; always pass the Markdown flag:
  - `<atl> jira workitem comment create --issue-id <KEY> --body-file <comment.md> --body-format markdown` (twg has no `--body-file`; `<atl>` reads the UTF-8 file and sends it as an inline `--body`) or `--body "<md>" --body-format markdown`. `<atl> jira workitem comment update --id <commentId> --issue-id <KEY> --body-file <comment.md> --body-format markdown` edits one the same way; `comment delete --id <commentId> --issue-id <KEY>` runs on twg unchanged and is permanent, so confirm first. Show files inline with `--attach <path>` (repeatable) on `comment create|update`: `<atl> jira workitem comment create --issue-id <KEY> --body-file <comment.md> --body-format markdown --attach <shot.png> --attach <report.pdf>` uploads each file to the work item, then posts the comment with an image preview per image and one file card per other file, appended after the text. On `update`, the new body and files replace the old ones. If any file cannot be read, uploaded, or shown inline, nothing is posted. Output is JSON `{key, commentId, url, attached:[{id, filename, inline: preview|card}]}`; `--internal` and other twg flags are not accepted with `--attach`. To reference a file already on the item, link it: `[name](https://<site>/secure/attachment/<id>/<name>)`. Remove a file with `<atl> jira workitem attachment delete --attachment-id <id> --yes`; the comment's card then shows a missing file. `--body-file` without `--body-format markdown` exits 2; `-o json` and other flags pass through.
  - `<atl> jira workitem update --id <KEY> --comment "<md>" --comment-format markdown`
  - `<atl> jira workitem transition ... --transition-comment "<md>" --transition-comment-format markdown` (same on `update --status`)
- Do not pass Jira wiki markup such as `h2. Heading`, `[label|url]`, or `*bold*`.
- Use a body file for long or structured content.
- Format flags convert only their matching description/comment flag, not values passed through `--field` or `--fields-json`. Rich custom fields there need raw ADF: produce it with `<atl> map-markdown md-to-adf < field.md`.
- Compact summaries can omit descriptions/comments; inspect referenced output before treating prose as empty.
- Jira descriptions and comments read back as ADF documents, not strings; read descriptions as Markdown with `<atl> jira workitem get <KEY> --output-file work.md`.

## Mentions

Get the person's account ID first with `<atl> user get "<exact name or email>"`. Never invent an account ID.

- **Comments** (`--body-format markdown` / `--comment-format markdown` on twg): write `[~accountId:AAID]`; twg converts it to an ADF mention when the write path supports the compatibility form.
- **Descriptions** (the skill's converter): no mention form; `[~accountId:...]` publishes as literal text. Put the mention in a comment instead, or report that the description cannot carry it.

Read back the resulting comment and confirm the mention node when it matters.
