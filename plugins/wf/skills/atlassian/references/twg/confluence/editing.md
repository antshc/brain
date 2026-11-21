---
description: Safely edit Confluence pages as Markdown through atl with a local body file, comment-anchor checks, and read-back verification.
---

# Confluence Editing

Every body edit is Markdown through `<atl>`:

```text
read Markdown -> copy original -> edit locally -> update from file -> verify
```

## Safe Workflow

1. Fetch: `<atl> confluence content get <page> --output-file tmp/<pageId>/page.md`; copy it to `tmp/<pageId>/original.md`.
2. Edit `page.md` in place without reconstructing unrelated content. Keep every `<!-- adf:comment -->` span and id around text you keep; delete a span only with its text. Keep dialect markers (`<!-- adf:... -->`, `<details>`, panels, status) intact.
3. Compare anchors offline: `<atl> publish-page check-anchors --original tmp/<pageId>/original.md --md-path tmp/<pageId>/page.md`; exit 0 and `removed` lists only intended detachments.
4. Update: `<atl> confluence content update <page> --body-file tmp/<pageId>/page.md --title "<existing title>"`. Pass the existing title, else the first `#` heading renames the page.
5. Verify: `<atl> publish-page verify --page-id <pageId> --expect-anchors <n> [--present <file>] [--absent <file>] --verify-dir tmp/<pageId>/verify`. Pass → delete `tmp/<pageId>/`; fail → keep it and report the failing check.

- Title-only change → `<atl> confluence content update <page> --title "<title>"` (no body; runs on twg).
- Never replace a long existing body with an inline `--body` string unless the user explicitly intends a complete rewrite.
- `--draft`, `--minor-edit`, `--version-message`, `--content-width` are not supported on the Markdown path (exit 2); report them as unsupported instead of switching formats.

## Concurrent edits

- The Markdown update publishes against the live version at write time; `--snapshot-token` is accepted and ignored. Fetch immediately before editing, and update promptly.
- Someone else edited the page since your fetch (version or content differs on a fresh fetch) → refetch, reapply the intended change, re-run the anchor check, then update.
- If the reconciled update also races another edit, report active editing instead of looping.
