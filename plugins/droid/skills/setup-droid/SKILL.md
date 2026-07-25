---
name: setup-droid
description: Manual, user-invoked bootstrap that scaffolds Droid's convention/state files (CODE.md, VERIFY.md, MEMORY.md, LOG.md) from skeleton templates under the resolved Harness Root. Only creates files that don't already exist; never called by the droid agent itself.
---

# Setup Droid

Scaffold the four convention/state files Droid resolves during INPUT (`CODE.md`, `VERIFY.md`, `MEMORY.md`, `LOG.md`), seeding any that are missing from skeleton templates. Run only when a person explicitly invokes this skill — never as part of an autonomous `droid` implementation run.

## Resolve Harness Root

Mirror `droid.agent.md`'s own INPUT resolution — do not invent a second resolution scheme:

1. If `/resolve-harness` is available, invoke it from cwd; retain the emitted `HARNESS_ROOT`.
2. If unavailable or it emits `HARNESS_ROOT=` (empty), use cwd as `HARNESS_ROOT`.
3. If available but exits non-zero, stop as blocked.

**Never create or modify `.harness.env`** — only read Harness Settings through the resolver. If none exists, proceed with the cwd fallback and leave the filesystem untouched, per `resolve-harness`'s own "never modify the filesystem" rule.

## Create missing files

For each of the four files below, check whether it already exists at its target path. **Skip silently** if it exists — never overwrite, merge into, or prompt about an existing file. If missing, copy the matching template from `templates/` (in this skill's directory) verbatim, renamed to the target filename.

| File | Target path | Template |
|---|---|---|
| `CODE.md` | `$HARNESS_ROOT/CODE.md` | `templates/CODE.template.md` |
| `VERIFY.md` | `$HARNESS_ROOT/VERIFY.md` | `templates/VERIFY.template.md` |
| `MEMORY.md` | `$HARNESS_ROOT/MEMORY.md` | `templates/MEMORY.template.md` |
| `LOG.md` | `$HARNESS_ROOT/.droid/LOG.md` | `templates/LOG.template.md` |

Substitute `HARNESS_ROOT` literally wherever `$HARNESS_ROOT` appears. Create the `.droid/` directory if it doesn't exist yet.

## Hard rules

- Manual invocation only — do not wire this into `droid.agent.md`'s INPUT step; that step's own rule ("do not create missing `CODE.md`, `VERIFY.md`, or `MEMORY.md`") stays in force.
- Never overwrite, merge, or prompt about a file that already exists.
- Never create or modify `.harness.env`.
- Templates are skeletons only — section headings and instructional comments. Do not fill them with invented, technology-specific example content.

**Emit**: "HARNESS_ROOT=<path> (resolver | fallback cwd). Created: [list]. Skipped (already exist): [list]. Templates: <plugin-relative dir>."
