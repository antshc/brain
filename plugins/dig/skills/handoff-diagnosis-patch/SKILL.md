---
name: handoff-diagnosis-patch
description: Persist a finished diagnosis as a replayable repo bundle — repro patch and one rendered diagnosis file with matching signals and scenario — under patches/<slug>/.
disable-model-invocation: true
argument-hint: "[bugSlug]"
---
# Hand off a diagnosis

This is an explicit persistence workflow. Normal diagnosis does not save its rendered root-cause summary.

## 1. Resolve diagnosis

`slug :=` supplied bug slug, or infer the single matching diagnosis folder.

Resolve `logPath` per `diagnosis-session-log`'s Location section, substituting `slug` for `bugSlug`.

Require at least one `confirmed` hypothesis.

Resolve:
- `patchSource :=` diff of present repro/instrumentation changes when applicable;
- `summary :=` root-cause summary already produced in the conversation, otherwise run `draft-root-cause`.

## 2. Create bundle

`bundleDir := repository root/patches/{{slug}}`.

If it already exists, ask whether to overwrite or suffix the slug.

## 3. Persist

Analyze the hypothesis log and `summary` — do not copy either into the bundle verbatim.

Write:
- `$bundleDir/BRIEF-{{slug}}.md` := render `Brief template` filling it from the diagnosis:
  - matching signals distilled from the log and `summary` as grep-able keywords, not a transcript;
  - scenario, when a product flow exists, as the one-liner Given/When/Then — bare code keywords, never file paths.
- optional `$bundleDir/{{slug}}.patch` := repro/instrumentation patch.

Validate an included patch with `git apply --check` or `git apply --check --reverse`, matching the current tree state.

## 4. Redact and report

Replace secrets with `<REDACTED>` in every persisted file.

Report `$bundleDir`. Leave committing to the caller.


# Brief template
```markdown
## Scenario

<!-- @: optional; omit when no product flow is found in code or the flow is one call already named in Components -->

**{{title|one line naming the behavior under test, not the ticket id}}**

{{1-3 lines: what was reported, what the root cause is, what this scenario proves}}

<!-- @: single scenario — one sentence, no bullet; multiple scenarios — one bulleted line each, flow order; reference each code keyword as `` `keyword` `` — bare name, never a file path or link; suffix with **(symptom)** when the outcome is the symptom -->

**Given** {{precondition|state/config, e.g. `AutoAttach` is true}}, **when** {{action|entry point or call, e.g. `CreateVolumeAsync` runs with `SnapshotId`}}, **then** {{outcome|resulting state, e.g. volume lacks `Encrypted`}} **(symptom)**.

## Matching signals

<!-- @: keywords a future root-cause run would grep for; one bullet per signal; prefer stable symbol names and substrings over exact paths or full messages, since both drift across iterations -->
- Symptom: {{user-visible symptom, short}}
- Error signature: `{{exception type plus the stable substring of the error/log line; drop volatile parts like ids, timestamps, counts}}`
- Components: {{class/function/module keywords to grep for; a bare name survives a move or rename better than a hardcoded path}}
- Environment: {{runtime, config, data shape, version the bug needs}}


```
