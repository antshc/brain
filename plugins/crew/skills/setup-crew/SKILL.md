---
name: setup-crew
description: Manual, user-invoked bootstrap that scaffolds the crew's convention/state files (CODE.md, VERIFY.md, CHORE.md, GOTCHAS.md) from skeleton templates under the resolved Harness Repo Path. Only creates files that don't already exist; never called by Codey or Chorey themselves.
disable-model-invocation: true
---

# Setup Crew

Scaffold the four convention/state files Codey and Chorey resolve during INPUT (`CODE.md`, `VERIFY.md`, `CHORE.md`, `GOTCHAS.md`), seeding any that are missing from skeleton templates. Run only when a person explicitly invokes this skill — never as part of an autonomous `codey` or `chorey` run.

## Resolve Harness Repo Path

Mirror `codey.agent.md`'s own INPUT resolution — do not invent a second resolution scheme:

1. If `/resolve-harness` is available, invoke it from cwd; retain the emitted `HARNESS_REPO_PATH`.
2. If unavailable or it emits `HARNESS_REPO_PATH=` (empty), use cwd as `HARNESS_REPO_PATH`.
3. If available but exits non-zero, stop as blocked.

**Never create or modify `.harness.env`** — only read Harness Settings through the resolver. If none exists, proceed with the cwd fallback and leave the filesystem untouched, per `resolve-harness`'s own "never modify the filesystem" rule.

## Fresh install only — never migrate

If `$HARNESS_REPO_PATH/.droid/` (the old settings folder) exists, **leave it exactly as it is** — do not read from it, copy anything out of it, or delete it. This skill scaffolds `.crew/` fresh; migrating an existing `.droid/` folder is a manual, human step outside this skill's scope.

## Create missing files

For each of the four files below, check whether it already exists at its target path. **Skip silently** if it exists — never overwrite, merge into, or prompt about an existing file. If missing, copy the matching template from `templates/` (in this skill's directory) verbatim, renamed to the target filename.

| File | Target path | Template |
|---|---|---|
| `CODE.md` | `$HARNESS_REPO_PATH/.crew/CODE.md` | `templates/CODE.template.md` |
| `VERIFY.md` | `$HARNESS_REPO_PATH/.crew/VERIFY.md` | `templates/VERIFY.template.md` |
| `CHORE.md` | `$HARNESS_REPO_PATH/.crew/CHORE.md` | `templates/CHORE.template.md` |
| `GOTCHAS.md` | `$HARNESS_REPO_PATH/.crew/GOTCHAS.md` | `templates/GOTCHAS.template.md` |

Substitute `HARNESS_REPO_PATH` literally wherever `$HARNESS_REPO_PATH` appears. Create the `.crew/` directory if it doesn't exist yet. Note: Codey and Chorey also auto-create `GOTCHAS.md` at runtime if missing — running this skill first only matters if you want to seed it ahead of time.

## Fill CODE.md from the repo

After creating `CODE.md` from its template (only when it was just created, never for a pre-existing file), invoke the `Explore` agent to scan `HARNESS_REPO_PATH` and populate each section with this repo's actual, observed conventions:

- **Style** — naming, formatting, and file organization conventions actually used in the codebase.
- **Layer placement** — where different kinds of code live (folders/layers/modules) and how placement is decided, based on the existing structure.
- **Design principles** — design rules the repo demonstrably follows (module depth, dependency direction, allowed/forbidden patterns).
- **Tests** — where tests live, how they're structured/named, and when they're required, based on existing test files.

Ground every line in files the `Explore` agent actually found — never invent conventions, never copy examples from another repo. If a section has no discoverable convention, leave its comment placeholder as-is rather than guessing.

## Hard rules

- Manual invocation only — do not wire this into `codey.agent.md`'s or `chorey.agent.md`'s INPUT step; that step's own rule ("do not create missing `CODE.md`, `VERIFY.md`, or `CHORE.md`") stays in force.
- Never overwrite, merge, or prompt about a file that already exists.
- Never read from, copy out of, or delete an existing `.droid/` folder — a fresh `.crew/` scaffold and a pre-existing `.droid/` folder are unrelated as far as this skill is concerned.
- Never create or modify `.harness.env`. `HARNESS_REPO_PATH` alone is enough — INPUT resolves every file at `$HARNESS_REPO_PATH/.crew/<FILE>`.
- Templates are skeletons only — section headings and instructional comments. Do not fill them with invented, technology-specific example content. The sole exception is a freshly created `CODE.md`, whose sections are filled with real conventions found by the `Explore` agent scan above.

**Emit**: "HARNESS_REPO_PATH=<path> (resolver | fallback cwd). Created: [list]. Skipped (already exist): [list]. Templates: <plugin-relative dir>."
