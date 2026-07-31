---
name: setup-droid
description: Manual, user-invoked bootstrap that scaffolds Droid's convention/state files (CODE.md, VERIFY.md, GOTCHAS.md) from skeleton templates under the resolved Harness Root. Only creates files that don't already exist; never called by the droid agent itself.
disable-model-invocation: true
---

# Setup Droid

Scaffold the three convention/state files Droid resolves during INPUT (`CODE.md`, `VERIFY.md`, `GOTCHAS.md`), seeding any that are missing from skeleton templates. Run only when a person explicitly invokes this skill — never as part of an autonomous `droid` implementation run.

## Resolve Harness Root

Mirror `droid.agent.md`'s own INPUT resolution — do not invent a second resolution scheme:

1. If `/resolve-harness` is available, invoke it from cwd; retain the emitted `HARNESS_ROOT`.
2. If unavailable or it emits `HARNESS_ROOT=` (empty), use cwd as `HARNESS_ROOT`.
3. If available but exits non-zero, stop as blocked.

**Never create or modify `.harness.env`** — only read Harness Settings through the resolver. If none exists, proceed with the cwd fallback and leave the filesystem untouched, per `resolve-harness`'s own "never modify the filesystem" rule.

## Create missing files

For each of the three files below, check whether it already exists at its target path. **Skip silently** if it exists — never overwrite, merge into, or prompt about an existing file. If missing, copy the matching template from `templates/` (in this skill's directory) verbatim, renamed to the target filename.

| File | Target path | Template |
|---|---|---|
| `CODE.md` | `$HARNESS_ROOT/.droid/CODE.md` | `templates/CODE.template.md` |
| `VERIFY.md` | `$HARNESS_ROOT/.droid/VERIFY.md` | `templates/VERIFY.template.md` |
| `GOTCHAS.md` | `$HARNESS_ROOT/.droid/GOTCHAS.md` | `templates/GOTCHAS.template.md` |

Substitute `HARNESS_ROOT` literally wherever `$HARNESS_ROOT` appears. Create the `.droid/` directory if it doesn't exist yet. Note: the `droid` agent itself also auto-creates `GOTCHAS.md` at runtime if missing — running this skill first only matters if you want to seed it ahead of time.

## Fill CODE.md from the repo

After creating `CODE.md` from its template (only when it was just created, never for a pre-existing file), invoke the `Explore` agent to scan `HARNESS_ROOT` and populate each section with this repo's actual, observed conventions:

- **Style** — naming, formatting, and file organization conventions actually used in the codebase.
- **Layer placement** — where different kinds of code live (folders/layers/modules) and how placement is decided, based on the existing structure.
- **Design principles** — design rules the repo demonstrably follows (module depth, dependency direction, allowed/forbidden patterns).
- **Tests** — where tests live, how they're structured/named, and when they're required, based on existing test files.

Ground every line in files the `Explore` agent actually found — never invent conventions, never copy examples from another repo. If a section has no discoverable convention, leave its comment placeholder as-is rather than guessing.

## Hard rules

- Manual invocation only — do not wire this into `droid.agent.md`'s INPUT step; that step's own rule ("do not create missing `CODE.md` or `VERIFY.md`") stays in force.
- Never overwrite, merge, or prompt about a file that already exists.
- Never create or modify `.harness.env`. `HARNESS_ROOT` alone is enough — INPUT resolves every file at `$HARNESS_ROOT/.droid/<FILE>` by default; the `*_PATH` keys exist only to point a file somewhere else.
- Templates are skeletons only — section headings and instructional comments. Do not fill them with invented, technology-specific example content. The sole exception is a freshly created `CODE.md`, whose sections are filled with real conventions found by the `Explore` agent scan above.

**Emit**: "HARNESS_ROOT=<path> (resolver | fallback cwd). Created: [list]. Skipped (already exist): [list]. Templates: <plugin-relative dir>."
