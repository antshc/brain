---
name: chorey-diff
description: "Captures Chorey's commit or uncommitted review scope in bin/crew_diff and restores its pre-review state. Use when Chorey discovers changes or reverts unverified cleanup."
---

# Chorey Diff

Run every action from the repository cwd. `bin/crew_diff/_manifest.json` is the authoritative path and restore ledger; use its repository paths instead of deriving paths from artifact filenames.

## Capture review diff

Run:

```text
python <skill-directory>/scripts/chorey_diff.py capture [--baseline <sha>]
```

With `--baseline`, the helper records the commit's per-file changes against its first parent, or the empty tree for a root commit. The resolved commit is the restore source.

Without `--baseline`, the helper records every staged, unstaged, and untracked non-ignored path. Each per-file artifact keeps staged and unstaged patches separate, and untracked files appear as complete additions. `snapshots/` holds each current path's exact content and existence state without changing the index.

The helper recreates `bin/crew_diff/`, writes `_manifest.json`, `diffs/`, and `snapshots/`, then emits one of:

- `Reviewing commit <sha>: [files]`
- `Reviewing uncommitted files: [files]`
- `No work to review.`

A nonzero exit means capture failed before review; use stderr as the skip reason.

## Restore pre-review files

Run once with every path Chorey touched:

```text
python <skill-directory>/scripts/chorey_diff.py restore --path <repo-relative-path> [--path <repo-relative-path> ...]
```

The helper rejects paths absent from the manifest. Commit mode restores only the working tree from the resolved commit; uncommitted mode restores exact snapshots and absence state. The index remains unchanged.

## Discard artifacts

Run before every final Chorey report, after any restore and gotchas update:

```text
python <skill-directory>/scripts/chorey_diff.py discard
```

This removes only `bin/crew_diff/` beneath cwd.

## Gotchas

- **Read patches through `_manifest.json`.** Numbered artifact names are collision-safe identifiers, not encoded repository paths.
- **Keep the bundle through verification.** Uncommitted snapshots are the only byte-exact restore source after Chorey edits a file.
- **Treat deleted paths as reviewable.** Their patch carries the review evidence even though no current file exists.
