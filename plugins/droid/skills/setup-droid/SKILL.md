---
name: setup-droid
description: Manual, user-invoked setup that tailors missing Droid guidance and personality references from repository evidence. Never called by the droid agent itself.
disable-model-invocation: true
---

# Setup Droid

Tailor Droid's missing skill-owned guidance and agent personality to the repository in the invocation directory. Run only when a person explicitly invokes this skill — never as part of an autonomous `droid` implementation run.

## Inspect references

For each reference below, classify it before writing:

- **Preserve** when it contains substantive content.
- **Populate** when it is absent, empty, or contains only its bundled template comments/placeholders.
- Treat headings, blank lines, and bundled template comments/placeholders as non-substantive.
- Never overwrite, merge, prompt about, or reorder substantive content.

| Reference | Target path | Template |
|---|---|---|
| `CODE.md` | `../droid-implement/CODE.md` | `templates/CODE.template.md` |
| `VERIFY.md` | `../droid-feedback/VERIFY.md` | `templates/VERIFY.template.md` |
| `GOTCHAS.md` | `../droid-gotchas/GOTCHAS.md` | `templates/GOTCHAS.template.md` |
| `PERSONALITY.md` | `../../agents/PERSONALITY.md` | `templates/PERSONALITY.template.md` |

## Explore repository evidence

Explore the invocation directory before populating `CODE.md`, `VERIFY.md`, or `PERSONALITY.md`.

- For `CODE.md`, inspect neighboring implementation and test files plus repository instructions for observed style, placement, design, and testing conventions.
- For `VERIFY.md`, inspect documented commands, CI/build configuration, manifests, and test configuration for diagnostics, build, test, and repository-specific checks.
- For `PERSONALITY.md`, inspect repository instructions, README language, and contributor-facing prose for grounded tone, priorities, and collaboration style.
- Record only conventions directly supported by the repository evidence; do not infer history, architecture, friction, or preferences.

## Populate missing content

Start each populated reference from its matching template, then replace each relevant default section with observed evidence.

- When evidence supports only part of `CODE.md`, `VERIFY.md`, or `PERSONALITY.md`, retain the bundled technology-agnostic default for each unsupported section.
- `CODE.md` must cover style, placement, design, and testing guidance.
- `VERIFY.md` must cover diagnostics, build, test, and repository-specific checks; list commands exactly when repository evidence provides them.
- `PERSONALITY.md` must give the Droid agent actionable tone and collaboration guidance grounded in repository language; use its bundled technology-agnostic default when no language is available.
- Initialize `GOTCHAS.md` from its template with no directives. Never infer Gotchas from repository structure, documentation, or setup friction.

## Report

Emit this deterministic summary in reference-table order: "Populated from evidence: [list]. Filled from defaults: [list]. Initialized empty: [list]. Preserved: [list]." Name the reference and section in the first two lists; a partially supported reference can appear in both. Include every reference in `Initialized empty` or `Preserved` when applicable.


## Hard rules

- Manual invocation only — do not wire this into `droid.agent.md`'s INPUT step.
- Do not create or modify repository files, Harness Settings, or `.droid/`.
- Write only the listed Droid references and only when their content is absent, empty, or placeholder-only.
- Keep generated detail in these references; do not expand Droid's core skill or agent bodies with repository-specific guidance.
