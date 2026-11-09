# Specs and tickets

Pass qualified tracker and source separately. Explicit offline work stays in the caller's local publication path.

- Design publication uses `spec create --profile design --tracker-repository TRACKER --source-repository SOURCE --base-branch BASE --initiative-id ID --summary TITLE --body-file FILE`. Stops on a duplicate initiative for that source and preserves the supplied body.
- Implement Spec uses `spec preflight`, `spec create --source-note NOTE`, `graph read --spec REF --out RUN_DIR` and `ticket create --spec REF --title TITLE --body-file FILE`. Retain the caller's graph and publication contracts.
- Publish Design and Wayfinder child tickets with the [Issues tactic](issues.md). Validate parent and labels, record created IDs, then link and verify.
- For issue artifacts, load [Issue artifacts](../references/issue-artifacts.md).
