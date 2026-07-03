---
name: csdroid-setup
description: Detect the harness root and workspace root once, persist them to a dotenv file, and expose the load snippet other csdroid skills source. Run during the ENVIRONMENT SETUP step, before exploration.
---

# Environment Setup

Single source of truth for the two paths every other csdroid skill needs. Detect both paths, write
them to a dotenv file, and emit the resolved values. Other skills **source** this file (see
[Load environment](#load-environment)) instead of re-deriving paths.

## Variables

- `CSDROID_HARNESS_ROOT` — the **outermost enclosing repo** (owns `agent/decisions.jsonl` and all convention docs). Never a worktree or a nested `workspace/` source repo.
- `CSDROID_WORKSPACE_ROOT` — the **source-code repo**. When a separate `workspace/` source repo exists under the harness, this is that repo; otherwise it **points to the harness root** (harness-only layout).

Two layouts are supported:
- **Harness only** — no source repo under `workspace/`; workspace root equals harness root.
- **Harness + workspace** — source code lives in a separate repo under `workspace/`; the harness still owns the store and docs.

## Dotenv file

The detected values are persisted as `export` lines to a session-stable, gitignored path — the
current worktree top-level:

```
"$(git rev-parse --show-toplevel)/.csdroid.env"
```

`.gitignore` matches `*.env`, so this file is never committed. It is the persistence mechanism:
each shell invocation is a fresh process, so a plain `export` cannot survive between skill calls —
the file can.

## Detect & persist (run once, during ENVIRONMENT SETUP)

Run the bundled detection script for your platform (located next to this `SKILL.md`). It resolves
both paths, writes `.csdroid.env`, and is **idempotent** — if the env file already exists it loads
it and skips detection. It works from inside a worktree by finding the **main** working tree
(`--git-common-dir`) then climbing to the outermost enclosing repo.

Linux/macOS:
```bash
bash "$(dirname "$0")/detect-env.sh"   # or: bash <skill-dir>/detect-env.sh
```

Windows (PowerShell):
```powershell
pwsh <skill-dir>/detect-env.ps1
```

Both print:
```
CSDROID_HARNESS_ROOT=<path>
CSDROID_WORKSPACE_ROOT=<path>
```

**Emit**: "Env: CSDROID_HARNESS_ROOT=<path>, CSDROID_WORKSPACE_ROOT=<path>."

## Load environment

Every other csdroid skill begins by loading the variables. **Source** (do not execute) the bundled
`load-env` script for your platform — it loads `.csdroid.env` if present, else detects inline as a
fallback so the skill still runs standalone. It must be sourced so the exports land in the calling
shell.

Linux/macOS:
```bash
. <skill-dir>/load-env.sh
```

Windows (PowerShell):
```powershell
. <skill-dir>/load-env.ps1
```

After sourcing, `$CSDROID_HARNESS_ROOT` and `$CSDROID_WORKSPACE_ROOT` are set.

## Hard Constraints

- Detection logic lives **only** in this skill. Other skills consume the variables via the Load environment snippet — they do not re-derive paths.
- Write the dotenv file only to `"$(git rev-parse --show-toplevel)/.csdroid.env"`. Never commit it.
- `CSDROID_WORKSPACE_ROOT` falls back to `CSDROID_HARNESS_ROOT` whenever no `workspace/` source repo exists.
- **Must-emit after detection**: emit both resolved values. This is observable output — do not skip silently.
