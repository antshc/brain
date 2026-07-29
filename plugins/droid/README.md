# droid

A technology-agnostic autonomous coding harness. One agent (`droid`) orchestrates a fixed pipeline; skills supply the reusable rules and the entry/exit points.

## Components

- [agents/droid.agent.md](agents/droid.agent.md) — the orchestrator. Fixed phases: INPUT → EXPLORATION → DECISION CONTEXT → IMPLEMENTATION → FEEDBACK LOOPS → RECORD DECISIONS → STATUS REPORT. Resolves Harness Settings and convention/state files once during INPUT, and works in its invocation directory.
- [skills/to-droid/SKILL.md](skills/to-droid/SKILL.md) — entry point. Resolves a task (`<description>` | `@plan` | issue URL), gathers recent git changes, and invokes `droid` via `runSubagent`.
- [skills/droid-implement/SKILL.md](skills/droid-implement/SKILL.md) — implementation rules; consumes the `CODE_PATH` resolved during INPUT.
- [skills/droid-feedback/SKILL.md](skills/droid-feedback/SKILL.md) — verify loop (LSP/build/test/refactor); consumes the `VERIFY_PATH` resolved during INPUT and runs all commands in cwd.
- [skills/droid-memory/SKILL.md](skills/droid-memory/SKILL.md) — reads curated guardrails from `MEMORY.md` at `$HARNESS_ROOT/.droid`.
- [skills/to-commit/SKILL.md](skills/to-commit/SKILL.md) — commits with a `dcode:` prefix, post-task.
- [skills/setup-droid/SKILL.md](skills/setup-droid/SKILL.md) — manual, user-invoked bootstrap that scaffolds missing `CODE.md`/`VERIFY.md`/`MEMORY.md`/`LOG.md` from templates. Not part of the agent's pipeline.

## Environment

During INPUT, Droid independently resolves Harness Settings through `/resolve-harness` when available. When the skill is unavailable or finds no configuration, it uses its current working directory (cwd) as `HARNESS_ROOT`. A failing available resolver blocks the invocation. Droid retains the complete emitted settings only for that invocation, then resolves its convention and state files once.

- `HARNESS_ROOT` — the Harness Settings value that owns all convention/state files, all of which live under `$HARNESS_ROOT/.droid/`. INPUT looks for each file at `$HARNESS_ROOT/.droid/<FILE>` and nowhere else, so running the agent directly (no `.harness.env`, `HARNESS_ROOT` = cwd) reads `.droid/` in the repo it was launched in. Optional `CODE_PATH`, `VERIFY_PATH`, `MEMORY_PATH`, and `LOG_PATH` settings override that default, then the resolved paths are passed to the relevant sub-skills. When no `LOG.md` exists, INPUT creates `.droid/LOG.md`; missing CODE, VERIFY, and MEMORY files use their documented fallbacks. INPUT itself never creates missing `CODE.md`, `VERIFY.md`, or `MEMORY.md` — run [skills/setup-droid/SKILL.md](skills/setup-droid/SKILL.md) manually to scaffold them from the templates the droid plugin owns at [skills/setup-droid/templates](skills/setup-droid/templates).
- **Workspace = cwd** — all code, git, build, test, and exploration commands run in the agent's current working directory. There is no separate workspace variable; callers launch the agent with cwd set to the code repo/worktree.

Harness discovery lives in Droid. Neither `ralph:dev` nor `to-droid` passes Harness Settings to the agent.

## Dependencies

```mermaid
graph TD
    U[User / plan.md / issue URL] --> TD[to-droid skill]
    DEV[ralph:dev skill] -->|runSubagent, cwd=worktree| AG
    TD -->|runSubagent| AG[droid agent]
    AG -->|DECISION CONTEXT & RECORD| MEM[droid-memory skill]
    AG -->|IMPLEMENTATION| IMP[droid-implement skill]
    AG -->|FEEDBACK LOOPS| FB[droid-feedback skill]
    TC[to-commit skill] -.->|reads STATUS REPORT| AG

    AG -.MEMORY_PATH.-> MEM
    AG -.CODE_PATH.-> IMP
    AG -.VERIFY_PATH.-> FB

    AG -.LOG_PATH.-> LOG[droid-log skill]
    AG -.resolves once from $HARNESS_ROOT/.droid/.-> DOCS[CODE.md / VERIFY.md / MEMORY.md / LOG.md]
```

**Nature of each edge**

- **Hard control-flow**: `to-droid` / `ralph:dev` → `droid` → the `droid-*` skills (named literally in the agent prose). Harness discovery lives in Droid, not its callers.
- **Soft/implicit**: `to-commit` depends on the agent's STATUS REPORT format (the `dcode:` convention couples them, but nothing enforces it).
- **Resolution contract**: the agent resolves Harness Settings (or falls back to cwd), resolves the four paths during INPUT, and passes each path to the relevant `droid-*` skill.
- **External file contracts**: each `droid-*` skill consumes only the resolved path the agent supplies; INPUT owns discovery, fallback `LOG.md` creation, and discovery-gap logging.

## Execution sequence

The `droid` agent runs a fixed pipeline. Each phase and the skill it invokes:

```mermaid
sequenceDiagram
    actor User
    participant TD as to-droid skill
    participant AG as droid agent
    participant MEM as droid-memory skill
    participant IMP as droid-implement skill
    participant FB as droid-feedback skill
    participant TC as to-commit skill

    User->>TD: task (<description> | @plan | issue URL)
    TD->>TD: resolve task + gather recent git changes
    TD->>AG: runSubagent(droid, task + recent changes)

    rect rgba(160, 190, 255, 0.08)
    note over AG: INPUT — resolve Harness Settings (or fallback cwd); resolve paths; workspace = cwd
    end

    note over AG: EXPLORATION — read changed + neighboring files, conventions

    rect rgba(160, 190, 255, 0.08)
    note over AG,MEM: DECISION CONTEXT
    AG->>MEM: Read Workflow (match prior decisions)
    MEM-->>AG: matching decision IDs or "none"
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,IMP: IMPLEMENTATION
    AG->>IMP: apply style / layers / tests rules
    IMP-->>AG: docs loaded + code implemented
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,FB: FEEDBACK LOOPS
    AG->>FB: verify (LSP / build / test / refactor)
    FB-->>AG: pass or issues to fix
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,MEM: RECORD DECISIONS
    AG->>MEM: Lookup → Add/Update / Confidence Bump
    MEM-->>AG: decision IDs recorded
    end

    AG-->>User: STATUS REPORT
    TC-->>AG: reads STATUS REPORT (dcode: commit, post-task)
```
