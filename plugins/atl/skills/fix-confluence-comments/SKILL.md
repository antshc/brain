---
name: fix-confluence-comments
description: >-
  Edit a Confluence page's Markdown and republish so every inline comment stays attached or is removed on purpose, never lost. Use when asked to fix, address, or resolve Confluence page comments, or apply review feedback to a page. Use address-page-comments to also reply to threads.
argument-hint: '<page_id_or_url>'
---

# Fix Confluence Comments

Flow over `fetch-page` and `publish-page` skills. Goal: every inline comment keeps its anchor unless its text is removed on purpose.

## Workflow

1. **Fetch.** *Run `fetch-page` skill to fetch the Confluence page as Markdown from its ID or URL, with inline-comment anchors and a Comments section* into `tmp/<pageId>/page.md`. List each comment: anchor id, selection, thread, author. Done when the list matches `## Comments`.
2. **Shared anchors.** From this skill's directory: `python3 scripts/shared_anchors.py tmp/<pageId>/page.md` → `@sharedIds` (`<id>\t<blocks>` per line). Done when listed or empty.
3. **Decide per comment** (`kept` \| `removed` \| `ambiguous`):
   - Text stays → edit the text, keep the `adf:comment` span and id unchanged; the span moves with the text.
   - Text removed → delete the span with its text. Id in `@sharedIds` → remove every span with that id.
   - Ambiguous (unclear story, release, or bug reference) → collect; ask the user once, batched, before any edit.
   Done when every comment has a decision.
4. **Jira context** only when a comment names bugs, stories, or releases: *run `preflight-atlassian` skill to resolve the credentialed twg command from `.atlassian.json.user` config*, then read-only lookups through it. Never write to Jira.
5. **Edit** `tmp/<pageId>/page.md`. Re-run step 2: each `@sharedIds` id has all spans or none. Record `@expectedAnchors` (span count), `@presentPhrases` (edited text), `@absentPhrases` (removed text) as one-phrase-per-line files in `tmp/<pageId>/`.
6. **Publish.** *Run `publish-page` skill to update the Confluence page from a local Markdown file, keeping inline comments attached via adf:comment anchors* with the page id and the existing title. Publish posts at most one detached-comment notice. Done when stdout JSON has `pageId`; `partialCommentRemovals` present → fix the Markdown, republish.
7. **Verify.** `publish-page` skill **Action: Verify** with `--expect-anchors @expectedAnchors`, the phrase files, `--verify-dir tmp/<pageId>/verify`. Pass → delete `tmp/<pageId>/`. Fail → keep `tmp/<pageId>/`, report the failing check name, stop.
8. **Report:** kept, removed, ambiguous answers, open questions, detached comments (`orphanedComments`), verification result.

## Rules

- Never resolve or reply to threads; comments stay for their authors.
- Never print credentials.
- Never delete `tmp/<pageId>/` before verification passes.
