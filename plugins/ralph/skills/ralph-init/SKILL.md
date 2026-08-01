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

## Gather Evidence

Explore `sourceRepository` before populating coding or verification guidance.

- For `CODE.md`, inspect implementation, tests, and repository instructions for style, placement, design, and testing conventions.
- For `VERIFY.md`, inspect documented commands, CI, manifests, and test configuration for diagnostics, build, tests, and repository checks.
- Record only evidence supported by the repository. Retain the technology-agnostic template default for unsupported sections.

## Populate Missing References

Start each populated reference from its matching template. Initialize `GOTCHAS.md` from its template with no directives; never infer Gotchas from setup evidence. `VERIFY.md` is required guidance for `/ralph-verify` and must be present after successful initialization.

## Report

Emit: "Persona: [confirmed role]. Agents: [created | replaced | unchanged]. Populated from evidence: [list]. Filled from defaults: [list]. Initialized empty: [list]. Preserved: [list]." Include every reference in Initialized empty or Preserved when applicable.

## Hard Rules

- Manual invocation only.
- Write references only when content is absent, empty, or placeholder-only.
- Write only the generated persona block in Codey and Chorey.
- Keep repository-specific detail in these references, not in Ralph's core agent or skill bodies.