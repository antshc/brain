---
name: chorey-diff
description: "Captures Chorey's staged/uncommitted review scope in bin/crew_diff. Use when Chorey discovers changes to review."
---

# Chorey Diff

Run every action from the repository cwd. `bin/crew_diff/_manifest.json` is the authoritative initial review-scope ledger; use its repository paths instead of deriving paths from artifact filenames. Its top-level `stacks` array is the sorted aggregate of recognized stacks in the captured current and previous paths.

## Capture review diff

Run:

```text
python <skill-directory>/scripts/chorey_diff.py capture
```

Capture always reviews whatever is currently staged, unstaged, and untracked in the working tree — the caller (`ralph:dev`, `to-crew`, or another orchestrator) stages the incoming change set with `git add` before invoking Chorey. Neither this helper nor Chorey ever stages.

The helper recreates `bin/crew_diff/`, writes `_manifest.json` and `diffs/`, and records a top-level `stacks` array. It recognizes AI-authoring files, Python files and packaging markers, and C#/.NET files and build markers. Renames and copies contribute both their previous and current paths. Unrecognized paths contribute no stack; therefore an empty array tells `/crew-chore` to load all configured stack files. The helper then emits one of:

- `Reviewing uncommitted files: [files]`
- `No work to review.`

A nonzero exit means capture failed before review; use stderr as the skip reason.

## Discard artifacts

Run before every final Chorey report, after any restore and gotchas update:

```text
python <skill-directory>/scripts/chorey_diff.py discard
```

This removes only `bin/crew_diff/` beneath cwd.

## Gotchas

- **Read patches through `_manifest.json`.** Numbered artifact names are collision-safe identifiers, not encoded repository paths.
- **Pass `stacks` through unchanged.** Chorey passes the manifest array to `/crew-chore` as `STACKS`; it does not repeat stack detection.
- **Treat deleted paths as reviewable.** Their patch carries the review evidence even though no current file exists.
