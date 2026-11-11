# Fetch PR Diff

*Load and follow the `github` skill to read pull requests and review evidence* using Pull requests, Chore acquisition. Split the current pull request diff into per-file diffs for the chore subagent. Run fresh before each subagent; the diff changes after every push.

## Fetch the diff per file

Read `GH_TOOL pr snapshot REF` immediately before acquisition. Bind HEAD and BASE to the returned SHAs.

```bash
GH_TOOL pr diff-split --pr "{{pullRequestUrl}}" --expected HEAD --base BASE
```

It writes to a fresh temp directory outside `HARNESS_ROOT`, `SOURCE_ROOT`, and `WORKTREE_PATH` (the worktree must stay clean for subagent commits) and prints JSON `{"diff_dir", "manifest", "files"}`. Non-zero exit (provider diff failure, empty diff) → stop that phase and report; never run the subagent without a diff.

## Return to caller

- `@diffDir` — `diff_dir`; pass it as `{{diffDir}}`.
- `@diffDir/_manifest.tsv` — `REAL_PATH<TAB>SANITIZED_FILENAME`; the only source of real repo-relative paths. Never reconstruct a path from a diff filename.
- Remove `@diffDir` after the subagent returns.
