---
name: address-page-comments
description: >-
  Edit a Confluence page in place to settle open review comments and reply to each thread; removed-anchor comments get a page comment. Use for a Confluence page URL or ID with 'address page comments' or 'reply to review comments'. Use fix-confluence-comments to edit without replying.
argument-hint: '<page_id_or_url> (e.g. "123456789" or "https://<site>.atlassian.net/wiki/spaces/<space>/pages/123456789/<title>")'
---

# Address page comments

**Skill base directory:** `{{skillDir}}` = absolute directory holding this `SKILL.md`. Run `scripts/comment_state.py` from there, never via a bare relative path. Keep working files (`comments-*.json`, `draft.html`, `edits.json`, `reply-*.md`) in a temp dir; `cd` there before running twg.

Safe to repeat. Remaining work comes from the Rerun gate, never from memory of an earlier run.

## 1. Preflight

*Run `preflight-atlassian` skill to resolve site, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**. Keep `site`, `twg`, `accountId`. Empty `accountId` → stop and report; it decides which comments are answered.

Parse `{{input}}` → `@pageId`: URL `/pages/<id>/` → `<id>`; bare number → as-is; tiny link or tiny ID → `<twg> confluence content get <site>/wiki/x/<tiny> --detail summary -o json --output-file tiny.json`, `@pageId := data.id`.

Done when `@pageId`, `site`, `twg`, `accountId` are set.

## 2. Rerun gate

1. List open comments, every page:
   ```bash
   <twg> confluence content comments list --id <pageId> --resolution-status open --include-replies true --body-format md --limit 250 -o json --output-file comments-1.json
   ```
   `data.nextCursor` present → repeat with `--cursor <value>` into `comments-2.json`, ... until absent.
2. Fetch the draft body and token:
   ```bash
   <twg> confluence content get <pageId> --draft --detail full --format html --body-only --output-file draft.html -o json > envelope.json
   ```
   `@snapshotToken := data.snapshotToken` from `envelope.json`.
3. Classify:
   ```bash
   python3 {{skillDir}}/scripts/comment_state.py --comments comments-1.json [comments-2.json ...] --html draft.html --account-id <accountId> --site <site> --pretty > state.json
   ```

| `action` | Do |
|---|---|
| `skip` | Report `counts`; no work left; **stop**. |
| `stop` | Report `reason`; **stop**. |
| `proceed` | Work `threads[]`. |

Each thread: `id`, `type` (`inline`/`footer`), `anchor`, `replyTarget`, `markerRef`, `selection` (original highlighted text), `url`, `comments[]` (`author` `me`/`other`, `body`, `createdAt`) in order. Only pending threads are listed. A thread is answered when its latest entry is yours, or, for an orphaned thread, when your footer comment linking `focusedCommentId=<id>` is newer than the latest reviewer entry.

| `anchor` | Meaning | `replyTarget` |
|---|---|---|
| `anchored` | Inline highlight still in the body | `thread` |
| `orphaned` | Inline highlight's `data-annotation-id` no longer in the body | `page` |
| `page` | Footer comment | `thread` |

Done when every pending thread is in hand or the run stopped with counts reported.

## 3. Understand each thread

Read the whole thread; answer the latest reviewer entry in context. Locate target content in `draft.html`: anchored → the element containing `<span class="annotation" data-annotation-id="<markerRef>">`; orphaned or footer → search for `selection` and the concern's subject. Record the nearest ancestor block's `data-local-id` (`p`, `li`, `h1`–`h6`, `td`, `tr`, `table`, panel).

Group threads naming the same underlying problem into one issue; keep per-thread replies.

Classify each issue:

| Class | Comment is | Next |
|---|---|---|
| `edit` | A change request the evidence supports: wording, removal, addition, correction | Edit, then reply |
| `answer` | A question, or a change the evidence shows is wrong or unneeded | Reply only |
| `unclear` | Ambiguous intent, or facts you cannot verify | Ask one focused question |

Verify factual claims before acting: the page itself, Jira/Confluence via `<twg>` search, and the codebase when the page documents code in this workspace. Missing evidence → `unclear`; never invent keys, versions, URLs, or behavior.

Done when each pending thread belongs to one issue with a class, target `localId`s for every `edit`, and cited evidence for every verdict.

## 4. Edit the page in place

Skip when no issue is `edit`.

1. Load the HTML body contract once: `<twg> confluence content body-formats html` (required before `--ack-body-formats`).
2. Write `edits.json`: one JSON array, all `edit` issues. Operations (all `value` fields are HTML strings; `localId` from `draft.html`):

   | Operation | Shape |
   |---|---|
   | `replaceNode` | `{"name":"replaceNode","localId":"<id>","value":"<p>...</p>"}` |
   | `insertNodeAfter` / `insertNodeBefore` | `{"name":"insertNodeAfter","localId":"<id>","value":"<p>...</p>"}` |
   | `deleteNode` | `{"name":"deleteNode","localId":"<id>"}` |
   | `removeNodes` | `{"name":"removeNodes","arguments":{"localIds":["<id>","<id>"]}}` |
   | `moveNode` | `{"name":"moveNode","arguments":{"localId":"<id>","targetLocalId":"<id>","position":"<pos>"}}` |
   | `appendNodeToEnd` | `{"name":"appendNodeToEnd","value":"<p>...</p>"}` |
   | `setAttrs` | `{"name":"setAttrs","localId":"<id>","arguments":{"attrs":{...}}}` |

   `replaceNode` value = the node's full current HTML from `draft.html` with only the requested change applied: keep its tag, `data-local-id`, every attribute, and every `<span class="annotation" ...>` wrapper whose text survives. Change the smallest node that holds the edit.
3. Apply:
   ```bash
   <twg> confluence content update <pageId> --snapshot-token "<snapshotToken>" --edits-file edits.json --ack-body-formats --version-message "Address review comments" -y -o json > update.json
   ```
   Publishes by default; add `--draft` only when the user asks for a draft.
4. Stale or missing token → refetch `draft.html` and token (step 2.2), revalidate every `localId` and annotation, rebuild `edits.json`, retry once. Second stale → report active editing; **stop** before replying. A target deleted or changed incompatibly → carry its issue as `unclear`.
5. Read back: refetch the body (`--draft` only if you saved a draft) to `after.html`. Confirm each edited node holds the intended text and every `data-annotation-id` present before the edit is still present, except highlights whose text the edit removed on purpose.

An annotation lost by an edit makes its thread orphaned: answer it at page level in step 5.

Done when `update.json` reports success and read-back confirms every edit, or each failed edit's issue is carried as `unclear` with the reason.

## 5. Reply

Draft each reply per *Reply style*. Claim a change only after step 4 read-back confirmed it.

| Target | Command |
|---|---|
| `thread` (anchored inline or footer) | `<twg> confluence content comments reply --comment-id <thread id> --body-file reply-<id>.md --body-format md -o json` |
| `page` (orphaned, or lost by this run's edit) | One footer comment for the run: `<twg> confluence content comments create --id <pageId> --comment-type footer --body-file reply-page.md --body-format md -o json` |

`--comment-id` is always the top-level thread `id`, never a reply id.

Page-level body: one lead sentence, then a table, one row per orphaned thread:

```markdown
These comments lost their highlighted text, so the answers are here:

| Removed text | Comment | Answer |
| --- | --- | --- |
| {{selection}} | [{{author name or "Comment"}}: {{short paraphrase}}]({{url}}) | {{reply}} |
```

The link **MUST** be the thread `url` (it carries `focusedCommentId=<id>`); the Rerun gate uses it to detect the answer.

Read back each posted comment (`<twg> confluence content comments get --comment-id <new id> --body-format md -o json`); confirm the body. Failed or uncertain post → leave the thread pending; rerun the gate before retrying to avoid duplicates.

**MUST NOT** resolve or reopen comments; the reviewer closes threads. Rationale: reviewer and agent may share credentials.

Done when every pending thread has one confirmed reply (thread or page table row) or a reported blocker.

## Reply style

1–3 short sentences, more only when needed. Outcome → decisive reason → focused question when needed. Common words, active voice, the thread's register. Address the latest concern; do not repeat the reviewer or an earlier answer.

| Situation | Reply |
|---|---|
| Edited | Name the change briefly; a typo may need only `Fixed.` |
| No change needed | Give the decisive reason with evidence. |
| Unclear | Ask one focused question that unblocks the decision. |
| Earlier mistake | Acknowledge briefly; give the correction. |
| Deferral proposed | Ask whether to track it separately; claim no ticket exists. |
| Existing ticket supplied | Name the supplied key; invent none. |

No praise, apologies, headings, canned wording, or labels (`Bug:`, `Nit:`, `Note:`). Prefer "use" over "utilize"/"leverage". Name exact sections, Jira keys, or URLs when needed to assess the answer. **MUST NOT** create Jira tickets or follow-up pages; ask whether separate tracking is wanted.

## 6. Report

| Section | Contents |
|---|---|
| Gate | `counts` from step 2. |
| Issues | One row per issue: class, threads, edits (`localId`s) or `none`, reply target. |
| Page | Version message and whether published or saved as draft; annotations lost by edits. |
| Open | `unclear` questions and blockers awaiting the reviewer. |

## Gotchas

- **Targeted twg edits are the only body write here.** This overrides Preflight's Markdown-only and REST-only body rules: `--edits-file` preserves untouched nodes exactly (macros, diagrams, annotations), while `publish-page` full republish or `--body-file` replacement can drop or rewrite inline-comment anchors. **MUST NOT** use `--body`/`--body-file`.
- `localId`s come from the latest `content get --detail full`; `data.metadata.localIdsDurable: false` → refetch immediately before `update`.
- Classic pages (`type=page`) need the `--draft` read's `snapshotToken`; never retry with `data.currentSnapshot.token` from an error.
- `--resolution-status open` includes inline comments whose highlighted text an edit removed; `comment_state.py` marks them `orphaned` by checking `data-annotation-id` in the body.
- `-o json --output-file` files are unredacted; read only needed fields with Python.
- `<twg>` exits `127` → report missing twg CLI; auth error → report `email`/`apiToken` in `.atlassian.json.user`. **MUST NOT** run `twg login`.

## Completion criteria

- Rerun gate on the same page returns `skip`, or lists only threads reported as `unclear`/blocked.
- Every edited node and every surviving annotation verified in the read-back body.
- No comment resolved, reopened, or answered twice.
