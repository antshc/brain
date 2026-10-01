---
name: handoff-diagnosis-patch
description: Persist a finished diagnosis as a replayable repo bundle — repro patch, hypothesis log, rendered root-cause summary, and matching signals — under patches/<slug>/.
disable-model-invocation: true
argument-hint: "[bugSlug]"
---
# Hand off a diagnosis

This is an explicit persistence workflow. Normal diagnosis does not save its rendered root-cause summary.

## 1. Resolve diagnosis

`slug :=` supplied bug slug, or infer the single matching diagnosis folder.

Default hypothesis log:
`repository root/docs/tmp/{{slug}}/diagnosis.md`.

Require at least one `confirmed` hypothesis.

Resolve:
- `patchSource :=` diff of present repro/instrumentation changes when applicable;
- `summary :=` root-cause summary already produced in the conversation, otherwise run `draft-root-cause`.

## 2. Create bundle

`bundleDir := repository root/patches/{{slug}}`.

If it already exists, ask whether to overwrite or suffix the slug.

## 3. Persist

Write:
- `$bundleDir/diagnosis-log.md` := shared hypothesis log;
- `$bundleDir/root-cause.md` := rendered summary;
- optional `$bundleDir/{{slug}}.patch` := repro/instrumentation patch.

Validate an included patch with `git apply --check` or `git apply --check --reverse`, matching the current tree state.

## 4. README

Copy `DIAGNOSIS-FORMAT.md` from this skill's base directory to `$bundleDir/DIAGNOSIS-{{slug}}.md`.

Fill it from the diagnosis and observed replay evidence:
- matching symptom/error/component/path/environment signals;
- changed files;
- real-interface scenario;
- commands that were actually run;
- actual observed outputs;
- instructions to produce a new summary.

MUST NOT claim an unobserved replay result.

## 5. Redact and report

Replace secrets with `<REDACTED>` in every persisted file.

Report `$bundleDir`. Leave committing to the caller.
