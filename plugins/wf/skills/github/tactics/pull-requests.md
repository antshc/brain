# Pull requests

Use qualified PR references and preserve the source/base repository identity.

- **Draft PR / Read PR initiative** → load [PR format](../references/pr-format.md). For drafts, *apply `writing-style` skill to write PR descriptions and commit messages* using **Write a PR description or commit message** to the prose and preserve the required sections and initiative markers.
- **Read** → `pr snapshot REF [--inline] [--comments]` for metadata and complete paginated comments. `pr find --repo R --head BRANCH` locates an open PR. Implement Spec uses `pr read` for coverage, format, and check verification.
- **Publish** → `pr publish` for the Implement Spec managed draft. Supply the verified head branch, base, initiative, title, rationale, changes, evidence and coverage. Use `pr open --repo R --head HEAD_BRANCH --base BASE_BRANCH --expected HEAD_SHA --title TITLE --body-file FILE [--draft]` or the authorized integration for direct publication with the caller's draft/readiness policy and read back the exact PR. Preserve user-authored text on update.
- **Diff** → load [Fetch PR diff](../references/fetch-diff.md) for Code, HITL and Chore acquisition. Use `pr diff REF --expected HEAD --base BASE` only where a provider diff is sufficient.
- **Conversation** → `pr comment REF --body-file FILE` or `pr upsert-comment REF --marker MARKER --body-file FILE`. Keep top-level comments separate from review findings and replies.
