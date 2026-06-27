# Copilot Instructions

## Repository topology

This repository (the **reporoot**) is the **documentation / context repository**, not the codebase.

- **Context and decisions live at the reporoot:**
  - `CONTEXT.md` (and `CONTEXT-MAP.md` when multiple contexts exist) at the root — the domain glossary.
  - Architecture Decision Records under `docs/adr/`.
  - The source code folder structure and architecture in `ARCHITECTURE.md`.
- **Source code and git worktrees live in `workspace/`:**
  - `workspace/` contains the project's source code and any git worktrees.
  - This directory is git-ignored by the reporoot (see `.gitignore`).

## Rules

- **Do all development inside `workspace/`** — the active worktree. Never create or edit source code at the reporoot.
- **Author documentation at the reporoot** — `CONTEXT.md` and ADRs under `docs/adr/` are created and updated here, never inside `workspace/`.
- `CONTEXT.md` is a glossary only. Keep implementation details, specs, and scratch notes out of it.
- `ARCHITECTURE.md` is a high level architecture. Keep implementation details, specs, and scratch notes out of it.
- When cross-referencing the plan against code, look under `workspace/` (including the active worktree), not the reporoot.
