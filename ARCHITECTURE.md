# Brain Overview

A collection of GitHub Copilot agent plugins, skills, and Python tooling that automate coding workflows (issue triage, PR review, autonomous implementation) — organized as a flat plugin marketplace with shared Python modules synced into it at commit time.

## Context

See [CONTEXT.md](CONTEXT.md) for the shared language.

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
| [0001](docs/adr/0001-ralph-is-agent-agnostic.md) | Ralph is agent-agnostic | Ralph agent-handoff logic, any new Ralph-to-agent launch path, hardcoding agent-specific behavior into Ralph, `HARNESS_REPO_PATH`/`CODEBASE_REPO_PATH` resolution, resolving ambient location more than once, a component re-deriving or guessing a caller-supplied path | Ralph does not hardcode Droid-specific behavior and could launch any agent that honors the same invocation-directory contract. Ralph's worktree-creation and task-handoff logic carries no agent-specific naming, prompts, or assumptions about the launched agent's internals. Ambient location (`HARNESS_REPO_PATH`, `CODEBASE_REPO_PATH`) is resolved exactly once, by the entry-point skill (`resolve-harness`/`setup-harness`/`ralph:dev`/`ralph:fix`), and passed explicitly downstream through trusted channels (`## HARNESS`, worktree-skill arguments) rather than re-derived by each component; a component handed a present-but-invalid value stops as blocked instead of guessing or searching the filesystem itself. |
| [0002](docs/adr/0002-droid-is-agnostic.md) | Droid is run-location- and technology-agnostic | `droid` workspace behavior, `droid` command execution, `HARNESS_REPO_PATH` resolution, agent/skill naming, `droid-feedback` fallback behavior, adding language/toolchain-specific wording to the agent or its skills | Droid runs in the directory from which it is launched, has no `WORKTREE_PATH` interface, and stays agnostic about whether that directory is a worktree. It resolves `CODE.md`/`VERIFY.md`/`GOTCHAS.md` at `$HARNESS_REPO_PATH/.droid/<FILE>`, where `HARNESS_REPO_PATH` is supplied by its caller via a trusted `## HARNESS` prompt section rather than discovered by Droid itself, falling back to cwd only when no path is supplied. The agent and its `droid-*` skills carry no language/toolchain-specific knowledge; all technology specifics live only in those per-repo files, and the `droid-feedback` fallback discovers the toolchain via README + code exploration instead of hardcoding one. |
| [0003](docs/adr/0003-trigger-indexer-is-resource-agnostic.md) | Trigger-indexer is resource-agnostic | `trigger-indexer` skill changes, adding a new indexed table or record type, hardcoding table shape or location into `trigger-indexer` | `trigger-indexer` receives table/column/row metadata from callers, generates conversational trigger phrases, matches clauses semantically against touched-surface and grilling context, and preserves columns callers did not name. |

## Crosscutting Concepts

| # | Concept | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [0001](docs/concepts/0001-resource-access-skill.md) | Resource Access Skill | skill encapsulating access to a ticket tracker, docs backend, or other external infra, index-table read/write ownership | Encapsulates access to one infra category behind a skill's documented actions so the backend can be swapped without affecting callers. Examples: `manage-backlog` (GitHub), `manage-docs` (local files). Exception: `trigger-indexer` writes index tables directly. |
| [0002](docs/concepts/0002-ledger.md) | Ledger | session tracking of opened Concept/ADR/service records, grilling/domain-modeling session state, avoiding duplicate index re-scans | A session-scoped record, persisted via the memory tool at `/memories/session/domain-model-ledger.md`, of every record opened so far — checked before any re-scope decision instead of relying on recall over a long context window. |
| [0003](docs/concepts/0003-trigger-indexer.md) | Trigger Indexer | adding a new indexed table or row type, trigger phrases missing domain language, index rows drifting out of sync, a caller re-implementing matching inline | Generates concise conversational trigger phrases and centralizes semantic scan/match plus add/supersede/retire synchronization for any markdown table with a Trigger condition column, with caller-supplied metadata and preservation of unknown columns. |
| [0004](docs/concepts/0004-completeness-sweep.md) | Completeness Sweep | designing a skill's closing/completion step, declaring a task complete, reviewing whether a change covers every requirement | A final, systematic pass run after implementation that maps every explicit and implied obligation (requirements, tests, docs, config/migrations, error/security/observability cases) to implementation evidence, resolving anything without evidence as a fix, a question, or an explicit deferral before completion is declared. |
| [0005](docs/concepts/0005-checklist-workflow.md) | Checklist-Driven Workflow | authoring a skill with a sequential multi-step procedure, a step that can fail and require returning to an earlier step, a task needing resumable progress tracking | Embeds a literal Markdown checklist in a skill's instructions that the agent copies into its working notes at task start and checks off step by step, so ordered, resumable, multi-step procedures survive context resets and failures without drifting off sequence. |
| [0006](docs/concepts/0006-progressive-disclosure.md) | Progressive Disclosure | SKILL.md growing past core every-run instructions, deciding what belongs in a skill's references folder, skill authoring size limits, bulky or rarely-used reference material, splitting a skill's format templates or extended tables out of SKILL.md | Keeps `SKILL.md` limited to the core instructions an agent needs on every run, moving bulky or rarely-needed reference material (extended formats, large tables, edge cases) into separate files such as `references/` that are read on demand. |
| [0007](docs/concepts/0007-agent-persona-design.md) | Agent Persona Design | writing or reviewing an `.agent.md` or a `SKILL.md` role section, a vague or generic persona description, an agent drifting into inconsistent behavior across invocations | Every agent/skill persona defines specific (not generic) expertise, a stated working style, explicit **never** guardrails for irreversible or out-of-scope actions, and a concrete output-format example, keeping behavior predictable and reviewable. |
