# Publish HLD

Publish only on explicit request. Consume an existing HLD; do not launch Wayfinder, regenerate diagrams, push branches or create PRs. Atlassian owns all Confluence body transport, hierarchy/attachment operations and verification.

## Inputs and state

Read the canonical HLD, revision and both appendices. Resolve the existing target page ID or destination space/parent for creation; reuse configured or persisted targets. Missing or ambiguous destination → ask for that decision, never guess a page from its title alone.

Keep `<hld-path>.publication.json` outside disposable staging. Store source identity/hash → page ID/URL or attachment name/ID/URL/hash, target HLD ID, space/parent, source revision, completed operations and pending step. No credentials. Save each confirmed identity immediately; preserve mappings for removed sources without deleting remote resources. Local paths/SHAs are identifiers, not remote URLs.

| Field | Content |
| --- | --- |
| `hld` | Canonical source path, revision, target page ID/URL, space and parent; null target before creation |
| `artifacts` | Source-path keyed mapping; each value has kind, source hash, published-body hash when applicable, page or attachment identity, verified URL and status; empty object before publication |
| `pending` | First unconfirmed operation or null after verified completion |

```json
{"hld":{"source":"docs/ongoing/cache.md","revision":"abc123","pageId":"100","url":"https://example.atlassian.net/wiki/pages/100","spaceId":"10","parentId":null},"artifacts":{"docs/research/cache/limits.md":{"kind":"research","hash":"sha256:...","publishedHash":"sha256:...","pageId":"101","url":"https://example.atlassian.net/wiki/pages/101","status":"verified"}},"pending":null}
```

On failure retain confirmed mappings, set `pending` to the failed operation and report known remote changes; never infer absence from a failed read. The example URLs are illustrative; actual output uses verified provider URLs.

## Procedure

1. **Inventory.** Read the HLD and every indexed report/sketch. Check Requirements and every Mermaid fence have an expand ancestor; each Question has an answer or specific blocker/next step; risk Answers retain mitigation, selected method/reason, actual result/reproduction, evidence link and residual risk or reason unproved. Confirm all local artifact targets exist; deduplicate by canonical source. Drafts may publish with named gaps, never a readiness claim. Done when the complete source inventory and missing inputs are explicit.
2. **Resolve Atlassian.** *Load and follow the `atlassian` skill to publish Markdown to Confluence content* using Publish page and, for metadata/hierarchy/attachments, Query or operate with TWG. Read its full body, selected tactics and required preflight/rules resources before operations; retain supported rendering and comment protections. Resolve destination space instructions and parent identity. Done when target page/space/parent and required tools are verified.
3. **Ensure parent.** Reuse the recorded HLD page ID, fetching its current body and anchors before updates. For a new HLD publish the HLD with appendix destinations replaced by explicit publication-pending text, retaining other content and valid links; persist its returned ID immediately. Use the supplied parent ID when creating. An error naming a placeholder page requires resuming that ID. An ambiguous/lost create response requires hierarchy/title/source reconciliation before another create. Done when one known HLD page exists.
4. **Research children.** For each Appendix A report, compare its source hash with the verified live mapping; skip unchanged content. Otherwise call Atlassian Publish page once with its known ID or creation space plus `--parent-id` equal to the HLD ID. Verify actual parent and source mapping; preserve existing titles/anchors on updates. Persist child ID/URL/hash after success. An existing mapped page under another parent blocks that item; do not silently move it. Done when each consumed report has one verified direct child page or a precise pending operation.
5. **Prototype and sketch attachments.** Preserve proof reports and decision-bearing logs/patches. For each accepted sketch run the router-disclosed `scripts/package_sketch.py --source <package-root> --out <staging>/<initiative>-<sketch>.zip`; capture its file inventory and SHA-256. Include rationale, module map and language-native source files, never raw Arena candidates or build products. Give distinct artifact identities unique stable filenames. Done when every Appendix B artifact has a file/package and content hash.
6. **Upload and map.** Use Atlassian's attachment operations, discovering current supported TWG commands through its tactic; otherwise use Publish page's standalone local-file references in a staging copy. Reuse unchanged attachments only after live identity/existence verification; upload changed content under its recorded stable name. Retrieve attachment IDs and download/web URLs through Atlassian metadata, not guessed media-service IDs. Persist every confirmed mapping. Done when each required attachment exists on the HLD page and has a verified destination.
7. **Rewrite publication copies.** Keep canonical repository Markdown unchanged. Appendix A links become research child URLs; Appendix B links become verified attachment URLs. Rewrite all other local links in the HLD and reports using the same mapping, retaining fragments only when the target anchor is verified; embed/upload local images through Atlassian. Unknown local targets block final publication. Cross-linked child reports may need a second update after all destination IDs exist. Compare each final publication-copy hash with its verified published-body hash; a mapping/link change requires an update even when source bytes are unchanged. Done when no unresolved local file links remain in any publication copy.
8. **Publish final bodies.** Update each changed child and the HLD through Atlassian Publish page, with mapped IDs. Merge live inline-comment anchors into staged content and apply its check-anchors procedure; preserve unrelated remote edits or report conflicts. Do not attach files again when final copies use already verified remote URLs. Done when intended body changes and target identities are read back.
9. **Verify and retain state.** Run Atlassian's read-only verification. Inspect live ADF: Requirements table and every diagram media/extension retain expand ancestry; verify every child parent ID and appendix attachment target. Record final hashes/revisions and clear pending only after all checks pass. Failure retains staging and known remote state; resume the first missing operation without duplicate pages/uploads. Done when HLD URL, research child pages and every prototype/sketch attachment are verified.

## Completion criteria

- One verified HLD page; every consumed research is its direct child; every retained prototype/sketch is attached and indexed in its proper appendix.
- Both appendices link verified destinations; all publication copies have resolved links, retained expands and protected comment anchors. Ignored Source Material remains excluded.
- Repeated publication reuses identities; unchanged content skips writes after verification. Removed sources never trigger automatic remote deletion.
- Return HLD URL, child pages, attachment outcomes, draft gaps and precise pending work. No GitHub publication.
