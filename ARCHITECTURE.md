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
| [0001](docs/adr/0001-ralph-owns-its-agent-pipeline.md) | Ralph owns its agent pipeline | Ralph agent-handoff logic, Codey or Chorey orchestration, Ralph plugin agent packaging, adding or changing an agent pipeline stage | Ralph packages and directly orchestrates Codey followed by Chorey as one installed workflow. Codey implements each task; Chorey reviews and refactors the uncommitted changes, then reruns feedback before Ralph commits. |
| [0002](docs/adr/0002-ralph-agents-are-run-location-agnostic.md) | Ralph agents are run-location-agnostic | Codey or Chorey workspace behavior, agent command execution, invocation-directory guidance | Codey and Chorey use their invocation directory as the workspace and never receive or discover a `WORKTREE_PATH`. Callers establish the execution location before invoking either agent. |
| [0003](docs/adr/0003-ralph-agents-are-technology-agnostic.md) | Ralph agents are technology-agnostic | agent/skill naming, `ralph-feedback` fallback behavior, adding language/toolchain-specific wording to Ralph agents or their skills | Codey, Chorey, and their supporting skills carry no language- or toolchain-specific knowledge. Repository specifics live in skill-owned guidance, while fallbacks discover the toolchain from repository evidence. |
| [0004](docs/adr/0004-trigger-indexer-is-resource-agnostic.md) | Trigger-indexer is resource-agnostic | `trigger-indexer` skill changes, adding a new indexed table or record type, hardcoding table shape or location into `trigger-indexer` | `trigger-indexer` receives table/column/row metadata from callers, generates conversational trigger phrases, matches clauses semantically against touched-surface and grilling context, and preserves columns callers did not name. |

## Crosscutting Concepts

| # | Concept | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [0001](docs/concepts/0001-resource-access-skill.md) | Resource Access Skill | skill encapsulating access to a ticket tracker, docs backend, or other external infra, index-table read/write ownership | Encapsulates access to one infra category behind a skill's documented actions so the backend can be swapped without affecting callers. Examples: `manage-backlog` (GitHub), `manage-docs` (local files). Exception: `trigger-indexer` writes index tables directly. |
| [0002](docs/concepts/0002-ledger.md) | Ledger | session tracking of opened Concept/ADR/service records, grilling/domain-modeling session state, avoiding duplicate index re-scans | A session-scoped record, persisted via the memory tool at `/memories/session/domain-model-ledger.md`, of every record opened so far — checked before any re-scope decision instead of relying on recall over a long context window. |
| [0003](docs/concepts/0003-trigger-indexer.md) | Trigger Indexer | adding a new indexed table or row type, trigger phrases missing domain language, index rows drifting out of sync, a caller re-implementing matching inline | Generates concise conversational trigger phrases and centralizes semantic scan/match plus add/supersede/retire synchronization for any markdown table with a Trigger condition column, with caller-supplied metadata and preservation of unknown columns. |
| [0004](docs/concepts/0004-completeness-sweep.md) | Completeness Sweep | designing a skill's closing/completion step, declaring a task complete, reviewing whether a change covers every requirement | A final, systematic pass run after implementation that maps every explicit and implied obligation (requirements, tests, docs, config/migrations, error/security/observability cases) to implementation evidence, resolving anything without evidence as a fix, a question, or an explicit deferral before completion is declared. |
| [0005](docs/concepts/0005-checklist-workflow.md) | Checklist-Driven Workflow | authoring a skill with a sequential multi-step procedure, a step that can fail and require returning to an earlier step, a task needing resumable progress tracking | Embeds a literal Markdown checklist in a skill's instructions that the agent copies into its working notes at task start and checks off step by step, so ordered, resumable, multi-step procedures survive context resets and failures without drifting off sequence. |
| [0006](docs/concepts/0006-progressive-disclosure.md) | Progressive Disclosure | SKILL.md growing past core every-run instructions, deciding what belongs in a skill's references folder, skill authoring size limits, bulky or rarely-used reference material, splitting a skill's format templates or extended tables out of SKILL.md | Keeps `SKILL.md` limited to the core instructions an agent needs on every run, moving bulky or rarely-needed reference material (extended formats, large tables, edge cases) into separate files such as `references/` that are read on demand. |
