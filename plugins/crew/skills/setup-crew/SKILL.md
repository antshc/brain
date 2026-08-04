---
name: setup-crew
description: Manual, user-invoked bootstrap that scaffolds the crew's convention/state files (CODE.md, VERIFY.md, CHORE.md, GOTCHAS.md) from skeleton templates under the resolved Harness Repo Path. Only creates files that don't already exist; never called by Codey or Chorey themselves.
disable-model-invocation: true
---

# Setup Crew

Scaffold the four convention/state files Codey and Chorey resolve during INPUT, seeding any that are missing from skeleton templates. Run only on explicit human invocation — never inside an autonomous `codey` or `chorey` run.

## Resolve Harness Repo Path

Mirror `codey.agent.md`'s INPUT resolution — never invent a second scheme:

1. `/resolve-harness` available → run it from cwd; retain the emitted `HARNESS_REPO_PATH`.
2. Unavailable or empty value → `HARNESS_REPO_PATH` := cwd.
3. Available but exits non-zero → stop as blocked.

## Create missing files

For each file below, skip silently if it already exists — never overwrite, merge, or prompt. If missing, copy the matching template from `templates/` (this skill's directory) verbatim, renamed to the target filename. Create `.crew/` if needed.

| File | Target path | Template |
|---|---|---|
| `CODE.md` | `$HARNESS_REPO_PATH/.crew/CODE.md` | `templates/CODE.template.md` |
| `VERIFY.md` | `$HARNESS_REPO_PATH/.crew/VERIFY.md` | `templates/VERIFY.template.md` |
| `CHORE.md` | `$HARNESS_REPO_PATH/.crew/CHORE.md` | `templates/CHORE.template.md` |
| `GOTCHAS.md` | `$HARNESS_REPO_PATH/.crew/GOTCHAS.md` | `templates/GOTCHAS.template.md` |

## Fill CODE.md from the repo

Only when `CODE.md` was just created (never for a pre-existing one), run the `Explore` agent over `HARNESS_REPO_PATH` and populate each section with this repo's observed conventions:

- **Style** — naming, formatting, and file organization actually used.
- **Layer placement** — where each kind of code lives and how placement is decided.
- **Design principles** — rules the repo demonstrably follows (module depth, dependency direction, allowed/forbidden patterns).
- **Tests** — where tests live, how they're structured/named, when they're required.

Ground every line in files `Explore` actually found — never invent conventions or copy them from another repo. A section with no discoverable convention keeps its placeholder comment.

## Hard rules

- Manual invocation only — never wire this into either agent's INPUT step.
- Never overwrite, merge, or prompt about an existing file.
- Never read from, copy out of, or delete an existing `.droid/` folder — migration is a manual human step outside this skill.
- Never create or modify `.harness.env` — read Harness Settings only through the resolver.
- Templates are skeletons: headings and instructional comments only. Do not fill them with invented, technology-specific content; the sole exception is the freshly created `CODE.md` above.

**Emit**: "HARNESS_REPO_PATH=<path> (resolver | fallback cwd). Created: [list]. Skipped (already exist): [list]. Templates: <plugin-relative dir>."
