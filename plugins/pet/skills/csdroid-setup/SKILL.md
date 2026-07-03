---
name: csdroid-setup
description: Detect the harness root and workspace root once, persist them to a dotenv file, and expose the load snippet other csdroid skills source. Run during the ENVIRONMENT SETUP step, before exploration.
---

# Environment Setup

Single source of truth for the two paths every other csdroid skill needs. Detect both paths, write
them to a dotenv file, and emit the resolved values. Within the `csdroid` agent, downstream skills
**reuse the literal paths emitted at ENVIRONMENT SETUP** rather than re-deriving them.

## Variables

- `CSDROID_HARNESS_ROOT` — the **outermost enclosing repo** (owns `agent/decisions.jsonl` and all convention docs). Never a worktree or a nested `workspace/` source repo.
- `CSDROID_WORKSPACE_ROOT` — the **source-code repo**. When a separate `workspace/` source repo exists under the harness, this is that repo; otherwise it **points to the harness root** (harness-only layout).

Two layouts are supported:
- **Harness only** — no source repo under `workspace/`; workspace root equals harness root.
- **Harness + workspace** — source code lives in a separate repo under `workspace/`; the harness still owns the store and docs.

## Dotenv file

The detected values are persisted as `export` lines to a session-stable, gitignored path — the
**harness root**:

```
"$CSDROID_HARNESS_ROOT/.csdroid.env"
```

The harness root's `.gitignore` matches `*.env`, so this file is never committed. Persisting it at
the harness root (rather than the current worktree) keeps it consistent and discoverable regardless
of which repo/worktree the skill runs from. It is the persistence mechanism: each shell invocation
is a fresh process, so a plain `export` cannot survive between skill calls — the file can.

## Detect & persist (run once, during ENVIRONMENT SETUP)

Run the bundled detection script for your platform (in the `scripts/` directory next to this
`SKILL.md`). It resolves both paths, writes `.csdroid.env` at the harness root, and is **idempotent**
— if the env file already exists it loads it and skips detection.

It works from **anywhere in the harness or the workspace** — the harness root, the workspace source
repo, or any of their linked worktrees:

1. Resolve the current repo's **main** working tree (`--git-common-dir`), then climb parents to the
   **outermost** enclosing repo → `CSDROID_HARNESS_ROOT`.
2. If the current repo differs from the harness (i.e. detection started inside a nested repo), that
   repo **is** the workspace source → `CSDROID_WORKSPACE_ROOT`.
3. Otherwise, look for a source repo under `workspace/` (`find -maxdepth 2 -name .git`, matching the
   `worktree` skill); if none, fall back to the harness root.

Linux/macOS:
```bash
bash "$(dirname "$0")/scripts/detect-env.sh"   # or: bash <skill-dir>/scripts/detect-env.sh
```

Windows (PowerShell):
```powershell
pwsh <skill-dir>/scripts/detect-env.ps1
```

Both print:
```
CSDROID_HARNESS_ROOT=<path>
CSDROID_WORKSPACE_ROOT=<path>
```

**Emit**: "Env: CSDROID_HARNESS_ROOT=<path>, CSDROID_WORKSPACE_ROOT=<path>."

## Hard Constraints

- Detection logic lives **only** in this skill. Other skills consume the paths resolved at ENVIRONMENT SETUP — they do not re-derive paths.
- Write the dotenv file only to `"$CSDROID_HARNESS_ROOT/.csdroid.env"` (the harness root). Never commit it.
- `CSDROID_WORKSPACE_ROOT` falls back to `CSDROID_HARNESS_ROOT` whenever no `workspace/` source repo exists.
- **Must-emit after detection**: emit both resolved values. This is observable output — do not skip silently.
