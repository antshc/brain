# Rename page

Rename one exact Confluence page without rewriting from stale Markdown:

```bash
<atl> rename-page <pageId> --title "<title>" --yes
```

Run only when the user explicitly named the target and title; `--yes` confirms that bounded write. The command fetches the current title, version, and ADF body, updates them through REST, and verifies the live title. On a version-only `409`, it re-reads once and retries only when the body and prior title are unchanged. A body or title change aborts instead of overwriting concurrent work.

An already-matching title is read-only and returns `changed: false`.
