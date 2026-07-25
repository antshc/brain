# Brain Overview

A collection of GitHub Copilot agent plugins, skills, and Python tooling that automate coding workflows (issue triage, PR review, autonomous implementation) — organized as a flat plugin marketplace with shared Python modules synced into it at commit time.

## Context

See [CONTEXT.md](CONTEXT.md) for the shared language — currently the Ralph Agent Workflow terms (`Harness Root`, `Worktree Path`, `Guardrails`, `Problem Log`).

## Building blocks

### Codebase Structure

- `.githooks/pre-commit` — syncs modules into plugins/skills before each commit
- `plugins/` — Copilot agent plugins, each with its own `plugin.json`, `skills/`, and optional `agents/`
- `skills/` — Copilot agent skills not tied to a specific plugin
- `tools/` — Python CLI tooling
  - `tools/src/modules/` — shared Python modules, source of truth
    - `tools/src/modules/github/` — GitHub domain + infrastructure (`domain/`, `features/`, `infrastructure/`, `shared/`)
  - `tools/src/ralph/` — `ralph` CLI tool
    - `tools/src/ralph/main.py` — orchestrator: arg parsing, delegates to features
    - `tools/src/ralph/features/` — `review_pull_request/`, `review_pull_requests/`
  - `tools/tests/unit/` — unit tests mirroring `tools/src/`
  - `tools/tests/integration/` — integration tests
- `logs/` — runtime logs (daily JSON per repo)

## Architecture Decision Records

| # | Decision | Trigger condition | Summary |
|---|----------|-------------------|---------|
| [0001](docs/adr/0001-ralph-launches-droid-from-worktree.md) | Ralph launches Droid from the worktree | `ralph` to `droid` invocation, Ralph worktree setup, any new `resolve-harness` caller, `.harness.env` creation/modification | Every Ralph caller launches Droid from its worktree without passing harness settings; Droid independently resolves them and operates in its invocation directory without a worktree-specific contract. Every `resolve-harness` caller (including `setup-droid`) follows the same resolve-or-fallback-to-cwd contract and never creates `.harness.env`; `setup-droid` may append missing `*_PATH` keys to an existing one but never overwrites a present key. |
| [0002](docs/adr/0002-droid-uses-its-invocation-directory.md) | Droid uses its invocation directory | `droid` workspace behavior, `droid` command execution | Droid runs in the directory from which it is launched, has no `WORKTREE_PATH` interface, and stays agnostic about whether that directory is a worktree. |
| [0003](docs/adr/0003-droid-is-technology-agnostic.md) | Droid is technology-agnostic | agent/skill naming, `droid-feedback` fallback behavior, adding language/toolchain-specific wording to the agent or its skills | The agent and its `droid-*` skills carry no language/toolchain-specific knowledge; all technology specifics live only in `CODE.md`/`VERIFY.md`/`MEMORY.md`. The `droid-feedback` fallback discovers the toolchain via README + code exploration instead of hardcoding one. |

## Crosscutting Concepts

| # | Concept | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [0001](docs/concepts/0001-resource-access-skill.md) | Resource Access Skill | skill encapsulating access to a ticket tracker, docs backend, or other external infra | Encapsulates access to one infra category behind a skill's documented actions so the backend can be swapped without affecting callers. Examples: `manage-backlog` (GitHub), `manage-docs` (local files). |
