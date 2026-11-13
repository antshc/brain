# Publish HLD

Publish only the requested HLD Confluence page, on explicit request. Consume the supported design; do not launch Wayfinder, regenerate diagrams, push branches or create PRs. Research reports, proof reports and retained sketch packages remain local: no artifact appendices, research subpages, package generation or artifact attachments. Atlassian owns body transport, rendering and verification.

## Inputs and state

Read canonical HLD/revision and resolve existing target page ID or creation space/parent; reuse persisted targets. Ambiguous destination requires the user's decision, never a guessed title match. Preserve `<hld-path>.publication.json` outside disposable staging; record each confirmed operation immediately. Never infer absence from a failed read.

| Field | Content |
| --- | --- |
| `hld` | Canonical path/revision, target page ID/URL, creation space/parent; null target before creation |
| `publishedHash` | Last verified publication-copy hash, null before publication |
| `pending` | First unconfirmed operation or null after verified completion |

```json
{"hld":{"source":"docs/ongoing/cache.md","revision":"abc123","pageId":"100","url":"https://example.atlassian.net/wiki/pages/100","spaceId":"10","parentId":null},"publishedHash":"sha256:...","pending":null}
```

Failure retains known identities and precise pending operation. Legacy artifact mappings are historical metadata, not an upload/subpage queue. Never automatically delete existing remote children/attachments.

## Procedure

1. **Prepare copy.** Read the HLD; preserve user Open Questions verbatim, including blanks. Exclude ignored Source Material and legacy research/proof/sketch appendices, local evidence links and package inventories from the publication copy. Repair former appendix references; keep supported conclusions in normal sections. Reports stay local. Confirm Requirements and every Mermaid fence retain expand ancestry. Draft gaps remain explicit; no readiness claim from publication. Done when the copy stands alone without artifact publication or broken links.
2. **Resolve transport.** *Load and follow the `atlassian` skill to publish Markdown to Confluence content* using Publish page; read full body, tactic and preflight/rules. Supply the prepared HLD copy and page/space/parent. Limit this route to HLD body create/update and read-only verification; no research/proof/sketch subpage creation or attachment uploads. Required diagram rendering remains part of the HLD body transport, not evidence package publication. If transport cannot honor the requested boundary, report the exact blocker before writing. Done when target identity and supported rendering are verified.
3. **Create or update.** Fetch the target body/anchors before update; preserve inline-comment anchors and unrelated remote edits through Atlassian's check-anchors procedure. On creation persist returned page ID immediately. Reconcile ambiguous/lost responses by source/target identity before retrying. Verify live identity before skipping unchanged content. Done when one known HLD page has the intended copy and no evidence publication operations occurred.
4. **Verify and retain.** Run Atlassian read-only verification; check live body, Requirements/diagram expand ancestry, excluded source/artifact sections and preserved user presentation questions. Record verified publication hash/revision; clear pending only after checks pass. Retain staging on failure; resume first missing operation without duplicate pages. Done when the HLD URL and body are verified or a precise pending step is recorded.

## Completion criteria

- One verified HLD page with supported design content, preserved expands/comment anchors and user presentation questions.
- No research/proof/sketch appendices, subpages, report/package uploads or artifact URL rewriting; evidence files remain local and existing remote artifacts untouched.
- Return HLD URL, draft gaps and pending work. No GitHub publication.
