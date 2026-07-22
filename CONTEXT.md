# Contexts
## Shared

Location: plugins/

Terms used across more than one plugin — not owned by a single plugin's context.

### Language
**Harness Root**:
The repository that owns the milestone/issues, the convention docs (`CODE.md`, `VERIFY.md`), and the agent state files (`agent/LOG.md`, `agent/MEMORY.md`). Distinct from the `Worktree Path`, though it can be the same repo.
_Avoid_: repo root, home repo
_Plugins_set_: ralph, pet, wf

**Worktree Path**:
The git worktree the agent executes all code, git, build, and test commands in. The agent `cd`s into it as its first action when provided.
_Avoid_: working directory, checkout
_Plugins_set_: ralph, pet, wf

## ralph
### Language

## pet
### Language

**Problem Log**:
An append-only record in `agent/LOG.md` of conflicts, access failures, or other friction an agent hit during a session (convention conflicts, directory/tool access issues). Written by the agent at the end of a session; curated by a human into Guardrails.
_Avoid_: decision log, decisions.jsonl

**Guardrails**:
Curated, human-reviewed directives stored in `agent/MEMORY.md`, distilled from recurring entries in the Problem Log. Read-only from the agent's perspective — applied before implementation, never written by the agent.
_Avoid_: decisions, durable decisions

## wf

### Language

# Relationships

- **ralph → pet**: `ralph`'s `dev` skill resolves `Harness Root` and `Worktree Path` and passes them to the `pet` plugin's `csdroid` agent, which cds into `Worktree Path` and derives all `pet` state paths from `Harness Root`.
- **pet ↔ Shared**: `pet`'s `Guardrails` (`agent/MEMORY.md`) and `Problem Log` (`agent/LOG.md`) are both persisted at fixed paths under `Harness Root`, a `Shared` term.

