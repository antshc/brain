---
name: 'fetch-diff'
description: 'Checks out a PR branch and fetches its diff per file into bin/review_diff/ with a path manifest; invoked by PR-review skills.'
---

# Fetch PR Diff

**MUST** run before analyzing a PR. Substitute `<OWNER>`, `<REPO>`, `<PR_NUMBER>`, `<PR_URL>` for the pull request being reviewed.

## 1. Check out the PR branch

```bash
gh pr checkout <PR_NUMBER> --repo <OWNER>/<REPO>
```

## 2. Fetch the diff per file

```bash
rm -rf bin/review_diff && mkdir -p bin/review_diff &&
gh pr diff "<PR_URL>" | awk -v outdir="bin/review_diff/" '
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
'
```

This writes per-file diffs into `bin/review_diff/` and `bin/review_diff/_manifest.tsv` (`REAL_PATH<TAB>SANITIZED_FILENAME`), preserving the exact repo-relative path (as GitHub expects for `FILE_PATH`) before it gets flattened for the local filename. Never reconstruct or guess this path later (e.g. via search) — always read it from the manifest.

## Return to caller

- `bin/review_diff/` — per-file diffs.
- `bin/review_diff/_manifest.tsv` — maps each diff filename back to its real repo-relative path. Callers MUST report `FILE_PATH` from this manifest, never from a guessed or locally-resolved path.
