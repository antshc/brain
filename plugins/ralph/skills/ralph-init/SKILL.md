---
name: ralph-init
description: Manually initialize absent Ralph coding, verification, Gotchas, and collaboration guidance from repository evidence without overwriting substantive guidance.
disable-model-invocation: true
---

# Initialize Ralph

Run only when a person explicitly invokes this skill. Never run it as part of Codey or Chorey.

## Inspect References

Classify each reference before writing:

- **Preserve**: substantive content exists.
- **Populate**: the reference is absent, empty, or only contains bundled template comments or placeholders.
- Treat headings, blank lines, and bundled template comments or placeholders as non-substantive.
- Never overwrite, merge, prompt about, or reorder substantive content.

| Reference | Target path | Template |
|---|---|---|
| `CODE.md` | `../ralph-implement/CODE.md` | `templates/CODE.template.md` |
| `VERIFY.md` | `../ralph-verify/VERIFY.md` | `templates/VERIFY.template.md` |
| `GOTCHAS.md` | `../ralph-gotchas/GOTCHAS.md` | `templates/GOTCHAS.template.md` |
| `PERSONALITY.md` | `../../agents/PERSONALITY.md` | `templates/PERSONALITY.template.md` |

## Gather Evidence

Explore the invocation directory before populating coding, verification, or collaboration guidance.

- For `CODE.md`, inspect implementation, tests, and repository instructions for style, placement, design, and testing conventions.
- For `VERIFY.md`, inspect documented commands, CI, manifests, and test configuration for diagnostics, build, tests, and repository checks.
- For `PERSONALITY.md`, inspect repository instructions, README language, and contributor-facing prose for tone and collaboration priorities.
- Record only evidence supported by the repository. Retain the technology-agnostic template default for unsupported sections.

## Populate Missing References

Start each populated reference from its matching template. Initialize `GOTCHAS.md` from its template with no directives; never infer Gotchas from setup evidence.

## Report

Emit: "Populated from evidence: [list]. Filled from defaults: [list]. Initialized empty: [list]. Preserved: [list]." Include every reference in Initialized empty or Preserved when applicable.

## Hard Rules

- Manual invocation only.
- Write only the listed Ralph references when content is absent, empty, or placeholder-only.
- Keep repository-specific detail in these references, not in Ralph's core agent or skill bodies.