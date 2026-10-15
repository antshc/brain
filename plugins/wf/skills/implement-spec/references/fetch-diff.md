# Fetch PR Diff

Split the current pull request diff into per-file diffs for the chore or bug-review subagent. Run fresh before each subagent; the diff changes after every push. Substitute `{{pullRequestUrl}}` with the PR URL; run from any directory.

## Fetch the diff per file

**MUST** write outside `HARNESS_ROOT`, `SOURCE_ROOT`, and `WORKTREE_PATH`; subagents commit from the worktree, which must stay clean.

```bash
diff_dir="$(mktemp -d)" &&
gh pr diff "{{pullRequestUrl}}" | awk -v outdir="$diff_dir" '
/^diff --git / {
  if (outfile) close(outfile)
  match($0, /b\/(.+)$/, arr)
  filepath = arr[1]
  sanitized = filepath
  gsub("/", "_", sanitized)
  outfile = outdir "/" sanitized
  print filepath "\t" sanitized >> (outdir "/_manifest.tsv")
}
outfile { print > outfile }
' && echo "$diff_dir"
```

Requires GNU `awk` (`gawk`; three-argument `match`). If `gh pr diff` fails or `_manifest.tsv` is missing or empty, stop that phase and report; never run the subagent without a diff.

## Return to caller

- `@diffDir` — printed temp directory holding per-file diffs; pass it as `{{diffDir}}`.
- `@diffDir/_manifest.tsv` — `REAL_PATH<TAB>SANITIZED_FILENAME`; the only source of real repo-relative paths. Never reconstruct a path from a diff filename.
- Remove `@diffDir` after the subagent returns.
