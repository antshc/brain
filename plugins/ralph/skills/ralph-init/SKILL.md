---
name: ralph-init
description: Use when explicitly asked to initialize Ralph guidance and confirmed agent personas from repository evidence.
disable-model-invocation: true
---

# Initialize Ralph

Run only when a person explicitly invokes this skill. Never run it as part of Codey or Chorey.

## Resolve persona

Set `HARNESS_ROOT` to the invocation directory. Resolve `sourceRepository` without creating a worktree:

```bash
sourceRepository=$(<ralph-worktree-skill-directory>/scripts/resolve_source_repository.sh "$HARNESS_ROOT")
```

Inspect `sourceRepository` to infer a primary technology. Prefer manifests and configuration files over source-file extensions. Record evidence for each inferred technology. Examples: `*.csproj` or `*.sln` infers C#, `pyproject.toml` infers Python, and `package.json` infers TypeScript or JavaScript from its configured source and tooling.

Propose `Senior <technology> developer` for the highest-ranked evidence. When equally ranked evidence identifies multiple technologies, ask the user to choose one proposed role. When no technology is inferred, ask the user to provide a role. Ask the user to confirm the selected role. When the user declines, exit without writing any reference or agent file.

Generate this exact block for both agents, replacing `<role>` with the confirmed role:

```md
<!-- ralph-init:persona:start -->
## Persona

**Expertise:** <role>

**Working style:** Be specific about expertise. Define the working style: concise, practical, and clear about assumptions, evidence, and verification.
<!-- ralph-init:persona:end -->
```

When an agent already contains a generated persona block that differs, ask before replacing it. Preserve all content outside the generated block. When no block exists, insert it after the title and before the workflow.

## Decide Build Gate

Inspect `sourceRepository` for documented build commands and build-system evidence. Present the evidence, or state that none was found, then ask whether Codey needs the early Build & LSP Check step. Do not infer the answer from the evidence.

When the user confirms the build gate, generate these exact `ralph-init`-owned blocks in Codey, replacing prior generated build blocks without changing content outside the markers. Renumber Codey's remaining checklist items to accommodate the BUILD step.

```md
<!-- ralph-init:build-checklist:start -->
- [ ] Step 3: BUILD & LSP CHECK
<!-- ralph-init:build-checklist:end -->
```

```md
<!-- ralph-init:build-section:start -->
## BUILD & LSP CHECK

Follow `/ralph-build` skill.
<!-- ralph-init:build-section:end -->
```

When the user declines the build gate, remove both generated blocks, including their markers. Renumber Codey's remaining checklist items to stay consecutive. Preserve all content outside the generated blocks.

## Inspect References

Classify each reference before writing:

- **Preserve**: substantive content exists.
- **Populate**: the reference is absent, empty, or only contains bundled template comments or placeholders.
- Treat headings, blank lines, and bundled template comments or placeholders as non-substantive.
- Never overwrite, merge, prompt about, or reorder substantive content.

| Reference | Target path | Template |
|---|---|---|
| `CODE.md` | `../ralph-implement/CODE.md` | `templates/CODE.template.md` |
| `FEEDBACK-LOOPS.md` | `../ralph-feedback-loops/FEEDBACK-LOOPS.md` | `templates/FEEDBACK-LOOPS.template.md` |
| `CHORE.md` | `../ralph-chore/CHORE.md` | `templates/CHORE.template.md` |
| `BUILD.md` | `../ralph-build/BUILD.md` | `templates/BUILD.template.md` |

Classify `BUILD.md` only when the user confirms the build gate. Do not create, classify, or report it when the user declines.

## Gather Evidence

Explore `sourceRepository` before populating coding or verification guidance.

- For `CODE.md`, inspect implementation, tests, and repository instructions for style, placement, design, and testing conventions.
- For `FEEDBACK-LOOPS.md`, inspect documented commands, CI, manifests, and test configuration for diagnostics, build, tests, and repository checks.
- For `CHORE.md`, inspect repository instructions and changed-code conventions for review rules that are supported by evidence.
- For `BUILD.md`, inspect documented build commands, CI, manifests, and project configuration.
- Record only evidence supported by the repository. Retain the technology-agnostic template default for unsupported sections.

## Populate Missing References

Start each populated reference from its matching template. Enrich `CHORE.md` only with review rules supported by repository evidence. `FEEDBACK-LOOPS.md` is required guidance for `/ralph-feedback-loops` and must be present after successful initialization. `/ralph-gotchas` initializes `GOTCHAS.md` on its first run; never infer Gotchas from setup evidence.

## Report

Emit: "Persona: [confirmed role]. Build gate: [enabled | declined]. Agents: [created | replaced | unchanged]. Populated from evidence: [list]. Filled from defaults: [list]. Preserved: [list]." Include every classified reference in Filled from defaults or Preserved when applicable.

## Hard Rules

- Manual invocation only.
- Write references only when content is absent, empty, or placeholder-only.
- Write only the generated persona block in Codey and Chorey.
- Keep repository-specific detail in these references, not in Ralph's core agent or skill bodies.