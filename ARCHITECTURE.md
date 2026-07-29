# Brain Overview

A collection of GitHub Copilot agent plugins, skills, and Python tooling that automate coding workflows (issue triage, PR review, autonomous implementation) — organized as a flat plugin marketplace with shared Python modules synced into it at commit time.

## Context

See [CONTEXT.md](CONTEXT.md) for the shared language;

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
| [0001](docs/adr/0001-ralph-is-agent-agnostic.md) | Ralph is agent-agnostic | Ralph agent-handoff logic, any new Ralph-to-agent launch path, hardcoding agent-specific behavior into Ralph | Ralph does not hardcode Droid-specific behavior and could launch any agent that honors the same invocation-directory contract. Ralph's worktree-creation and task-handoff logic carries no agent-specific naming, prompts, or assumptions about the launched agent's internals. |
| [0002](docs/adr/0002-droid-is-run-location-agnostic.md) | Droid is run-location-agnostic | `droid` workspace behavior, `droid` command execution, `.harness.env`/`resolve-harness` resolution | Droid runs in the directory from which it is launched, has no `WORKTREE_PATH` interface, and stays agnostic about whether that directory is a worktree. It resolves `CODE.md`/`VERIFY.md`/`MEMORY.md` from its current directory, falling back to discovering the Harness Root via `resolve-harness`/`.harness.env` when they aren't present there. |
| [0003](docs/adr/0003-droid-is-technology-agnostic.md) | Droid is technology-agnostic | agent/skill naming, `droid-feedback` fallback behavior, adding language/toolchain-specific wording to the agent or its skills | The agent and its `droid-*` skills carry no language/toolchain-specific knowledge; all technology specifics live only in `CODE.md`/`VERIFY.md`/`MEMORY.md`. The `droid-feedback` fallback discovers the toolchain via README + code exploration instead of hardcoding one. |

## Crosscutting Concepts

| # | Concept | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [0001](docs/concepts/0001-resource-access-skill.md) | Resource Access Skill | skill encapsulating access to a ticket tracker, docs backend, or other external infra, index-table read/write ownership | Encapsulates access to one infra category behind a skill's documented actions so the backend can be swapped without affecting callers. Examples: `manage-backlog` (GitHub), `index-docs` (local files). |
| [0002](docs/concepts/0002-ledger.md) | Ledger | session tracking of opened Concept/ADR/service records, touched-surface accumulation, staging decisions and assumptions that are not yet durable, avoiding duplicate index re-scans | A session-scoped record, persisted via the memory tool at `/memories/session/domain-model-ledger.md`, of every record opened so far, the surface touched so far, and every decision/assumption taken so far — checked before any re-scope decision or conflict classification instead of relying on recall over a long context window. |
| [0004](docs/concepts/0004-completeness-sweep.md) | Completeness Sweep | designing a skill's closing/completion step, declaring a task complete, reviewing whether a change covers every requirement | A final, systematic pass run after implementation that maps every explicit and implied obligation (requirements, tests, docs, config/migrations, error/security/observability cases) to implementation evidence, resolving anything without evidence as a fix, a question, or an explicit deferral before completion is declared. |
| [0005](docs/concepts/0005-checklist-workflow.md) | Checklist-Driven Workflow | authoring a skill with a sequential multi-step procedure, a step that can fail and require returning to an earlier step, a task needing resumable progress tracking | Embeds a literal Markdown checklist in a skill's instructions that the agent copies into its working notes at task start and checks off step by step, so ordered, resumable, multi-step procedures survive context resets and failures without drifting off sequence. |
| [0006](docs/concepts/0006-terminology-consistency.md) | Terminology Consistency | naming a rule/behavior that other skills or later turns need to reference, reviewing whether a cross-reference actually matches its source's wording | A term is defined once, in exact wording, at its authoritative source; every other reference to it \u2014 in another skill, another document, or a later turn of the same session \u2014 reuses that exact wording instead of paraphrasing or inventing a new label, so references stay traceable and the model doesn't fragment one idea into several. |
| [0007](docs/concepts/0007-skill-naming-convention.md) | Skill Naming Convention | creating a new skill, renaming an existing skill, reviewing a skill's `name` field | A skill's `name` uses lowercase letters, numbers, and hyphens only, preferring gerund form (`processing-pdfs`) or an acceptable noun-phrase/action-oriented alternative, and avoids vague, generic, reserved, or pattern-inconsistent names, so skills stay easy to reference, search, and organize across the collection. |
