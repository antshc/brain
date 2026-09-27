---
name: chorey-diff
description: "Captures Chorey's commit or uncommitted review scope in bin/crew_diff and restores its selected baseline. Use when Chorey discovers changes or reverts unverified cleanup."
---

# Chorey Diff

Run every action from the repository cwd. `bin/crew_diff/_manifest.json` is the authoritative initial review-scope ledger; use its repository paths instead of deriving paths from artifact filenames.

## Capture review diff

Run:

```text
python <skill-directory>/scripts/chorey_diff.py capture [--baseline <sha>]
```

With `--baseline`, the helper records the commit's per-file changes against its first parent, or the empty tree for a root commit. The resolved commit is the restore source.

Without `--baseline`, Chorey runs `git add -A` immediately before invoking the helper. The helper then records the staged incoming change set, and the Git index becomes its exact defensive revert baseline. The helper can still represent staged, unstaged, and untracked layers independently, but Chorey's pre-capture staging normally leaves only staged patches. Chorey must not stage again during review, so the index remains unchanged while its cleanup stays in the working tree.

The helper recreates `bin/crew_diff/`, writes `_manifest.json` and `diffs/`, then emits one of:

- `Reviewing commit <sha>: [files]`
- `Reviewing uncommitted files: [files]`
- `No work to review.`

A nonzero exit means capture failed before review; use stderr as the skip reason.

## Restore review baseline files

Run once with every path Chorey touched:

```text
python <skill-directory>/scripts/chorey_diff.py restore --path <repo-relative-path> [--path <repo-relative-path> ...]
```

The helper accepts safe repository paths Chorey touched, including minimal rule-required paths outside the initial manifest. With `--baseline`, it restores them from the resolved commit. Without `--baseline`, it restores them directly from the unchanged index; a path absent from the selected source is removed. For an initially captured rename, restoring its manifest path also restores its previous paths. The index remains unchanged.

## Discard artifacts

Run before every final Chorey report, after any restore and gotchas update:

```text
python <skill-directory>/scripts/chorey_diff.py discard
```

This removes only `bin/crew_diff/` beneath cwd.

## Gotchas

- **Read patches through `_manifest.json`.** Numbered artifact names are collision-safe identifiers, not encoded repository paths.
- **Keep the bundle through verification.** Its manifest records the selected rollback source and the previous paths needed to reverse captured renames.
- **Treat deleted paths as reviewable.** Their patch carries the review evidence even though no current file exists.
