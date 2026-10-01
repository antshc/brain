---
name: handoff-diagnosis-patch
description: Persist a finished diagnosis from session memory into the repo as a replayable bundle — repro patch, investigation log, root-cause summary, and a README with matching signals — under patches/<slug>/, so future root-cause runs find and reuse it. Use when asked to hand off, package, or save a diagnosis, repro, or experiment.
disable-model-invocation: true
argument-hint: "[bugSlug]"
---

# Hand off a diagnosis

Turns a diagnosis in session memory — the `diagnosing-root-cause` investigation log plus its repro patch — into one **bundle** in the repo. A memory-less agent can **replay** it (apply, set up, run the loop, see the same result), and later `diagnosing-root-cause` runs match it through its `## Matching signals` section.

## 1. Confirm there is a diagnosis to hand off

1. List `/memories/session/diagnosis-*.md`. Pick the one matching `[bugSlug]`; several and no argument → ask the user which.
2. Its `Status` **MUST** be `root-cause-found` or `done`. Otherwise stop and report its `Status` and `Next step`.
3. `patchSource :=` diff of the log's `Artifacts` bullets marked `present` — tracked: `git diff HEAD -- <paths>`; untracked: `git diff --no-index /dev/null <path>` per file. None present but `git status --porcelain` non-empty → ask whether the working-tree diff is the repro; else no patch.
4. `summary :=` the root-cause summary printed in this conversation; missing → *run `draft-root-cause` skill to draft the cited root-cause summary from the confirmed diagnosis log*.

Done when the log is chosen and `patchSource` (diff or none) and `summary` are resolved.

## 2. Create the bundle folder

`slug :=` the log's `bugSlug` (kebab-case naming the behavior — prefix a ticket id when one exists); `bundleDir := $(git rev-parse --show-toplevel)/patches/{{slug}}`.

`$bundleDir` already exists → ask: overwrite, or suffix the slug.

Done when `$bundleDir` exists and is empty.

## 3. Write and validate the patch

Skip when `patchSource` is none.

Write `patchSource` to `$bundleDir/{{slug}}.patch`, then validate against the current tree:

| Tree state | Check |
|---|---|
| Repro changes still applied | `git apply --check --reverse "$bundleDir/{{slug}}.patch"` |
| Repro changes already cleaned up | `git apply --check "$bundleDir/{{slug}}.patch"` |

Done when the check exits 0. A failing patch **MUST NOT** be handed off — regenerate it or drop it and say so in the README.

## 4. Persist the log and summary

- `$bundleDir/diagnosis-log.md` := the session log.
- `$bundleDir/root-cause.md` := `summary`.

Re-check both for secrets; replace any with `<REDACTED>`.

Done when both files exist and contain no secret.

## 5. Write the README

Copy `DIAGNOSIS-FORMAT.md` (from this skill's base directory) to `$bundleDir/DIAGNOSIS-{{slug}}.md` and fill every placeholder from the log:

- **Matching signals** — verbatim error strings, symptom words, components, `path`s, environment; what a future run would grep for.
- **Files changed** — one row per file in the patch.
- **Scenario** — one Gherkin `Scenario` per behavior the patch proves, against the real interface (route, CLI, test name). Built but unexercised → titled "not yet exercised".
- **Replay steps** — the log's `Setup` and loop commands in the order run, with the real output observed.
- **Produce a new summary** — what the next session reports back.

Done when no placeholder remains.

## 6. Final check

Reread every replay step. **MUST NOT** keep a step whose output you or the log did not observe — mark it "untested" or drop it.

Report `$bundleDir` to the user. Leave committing to them.

Done when no step claims an unobserved outcome.

## Gotchas

- Optional/manual asides silently go unverified — run them or delete them; a reasoned step reads identically to an executed one.
- `git apply --check --reverse` proves only that the patch matches the current tree, not that it forward-applies on another checkout — record the base commit so a mismatch is diagnosable.
- Session memory is cleared when the conversation ends — hand off before it does.
