# pet

A C# autonomous coding harness. One agent (`csdroid`) orchestrates a fixed pipeline; skills supply the reusable rules and the entry/exit points.

## Components

- [agents/csdroid.agent.md](agents/csdroid.agent.md) — the orchestrator. Fixed phases: ENVIRONMENT SETUP → EXPLORATION → DECISION CONTEXT → IMPLEMENTATION → FEEDBACK LOOPS → RECORD DECISIONS → STATUS REPORT.
- [skills/to-droid/SKILL.md](skills/to-droid/SKILL.md) — entry point. Resolves a task (`<description>` | `@plan` | issue URL), gathers recent git changes, invokes `csdroid` via `runSubagent`.
- [skills/csdroid-setup/SKILL.md](skills/csdroid-setup/SKILL.md) — detects the two paths, persists them to `.csdroid.env` via `detect-env.{sh,ps1}`, and emits them at ENVIRONMENT SETUP; other skills reuse those literal paths.
- [skills/csdroid-implement/SKILL.md](skills/csdroid-implement/SKILL.md) — implementation rules; loads `ARCHITECTURE.md`, `CODE.md`, `TESTS.md` + selected ADR/SDR from `$CSDROID_HARNESS_ROOT`.
- [skills/csdroid-feedback/SKILL.md](skills/csdroid-feedback/SKILL.md) — verify loop (LSP/build/test/refactor); loads `VERIFY.md` from `$CSDROID_HARNESS_ROOT`.
- [skills/csdroid-memory/SKILL.md](skills/csdroid-memory/SKILL.md) — durable decision store `agent/decisions.jsonl` at `$CSDROID_HARNESS_ROOT`.
- [skills/to-commit/SKILL.md](skills/to-commit/SKILL.md) — commits with a `dcode:` prefix, post-task.

## Environment

`csdroid-setup` bundles the detection scripts (in its `scripts/` directory):

- `detect-env.sh` / `detect-env.ps1` — resolve both paths, write `.csdroid.env` at the harness root, and echo the values. Works from the harness root, the workspace source repo, or any of their worktrees. Idempotent: if the file already exists they re-echo it and skip detection. Run once, in the agent's ENVIRONMENT SETUP phase; downstream skills reuse the emitted literal paths.

`.csdroid.env` lives at the **harness root** and is gitignored via `*.env`. Persisting it there (not the current worktree) keeps it consistent and discoverable regardless of which repo/worktree setup runs from. The file is the persistence mechanism — a plain `export` cannot survive because each shell invocation is a fresh process.

- `CSDROID_HARNESS_ROOT` — outermost enclosing repo; owns `agent/decisions.jsonl` and **all** convention docs (`ARCHITECTURE.md`, `CODE.md`, `TESTS.md`, ADR/SDR, `VERIFY.md`).
- `CSDROID_WORKSPACE_ROOT` — the `workspace/` source repo when present, else the harness root; used for source-code operations.

## Dependencies

```mermaid
graph TD
    U[User / plan.md / issue URL] --> TD[to-droid skill]
    TD -->|runSubagent| AG[csdroid agent]
    AG -->|ENVIRONMENT SETUP| SET[csdroid-setup skill]
    AG -->|DECISION CONTEXT & RECORD| MEM[csdroid-memory skill]
    AG -->|IMPLEMENTATION| IMP[csdroid-implement skill]
    AG -->|FEEDBACK LOOPS| FB[csdroid-feedback skill]
    TC[to-commit skill] -.->|reads STATUS REPORT| AG

    SET -.writes + emits paths.-> ENVF[(.csdroid.env @ harness root)]
    MEM -.reuses emitted paths.-> SET
    IMP -.reuses emitted paths.-> SET
    FB -.reuses emitted paths.-> SET

    IMP -.reads.-> DOCS[ARCHITECTURE.md / CODE.md / TESTS.md / docs adr,sdr @ CSDROID_HARNESS_ROOT]
    FB -.reads.-> VER[VERIFY.md @ CSDROID_HARNESS_ROOT]
    MEM -.read/write.-> STORE[(agent/decisions.jsonl @ CSDROID_HARNESS_ROOT)]
```

**Nature of each edge**

- **Hard control-flow**: `to-droid` → `csdroid` → the `csdroid-*` skills (named literally in the agent prose); `csdroid-setup` runs first in ENVIRONMENT SETUP.
- **Soft/implicit**: `to-commit` depends on the agent's STATUS REPORT format (the `dcode:` convention couples them, but nothing enforces it).
- **Environment contract**: `csdroid-setup` writes `.csdroid.env` and emits `$CSDROID_HARNESS_ROOT` / `$CSDROID_WORKSPACE_ROOT` at ENVIRONMENT SETUP; `csdroid-memory`, `csdroid-implement`, and `csdroid-feedback` reuse those literal paths.
- **External file contracts**: `csdroid-implement` and `csdroid-feedback` depend on convention docs living at `$CSDROID_HARNESS_ROOT` (`ARCHITECTURE.md` etc.), each with its own fallback. `csdroid-memory` keeps the store at `$CSDROID_HARNESS_ROOT/agent/decisions.jsonl`.

## Execution sequence

The `csdroid` agent runs a fixed pipeline. Each phase and the skill it invokes:

```mermaid
sequenceDiagram
    actor User
    participant TD as to-droid skill
    participant AG as csdroid agent
    participant SET as csdroid-setup skill
    participant MEM as csdroid-memory skill
    participant IMP as csdroid-implement skill
    participant FB as csdroid-feedback skill
    participant TC as to-commit skill

    User->>TD: task (<description> | @plan | issue URL)
    TD->>TD: resolve task + gather recent git changes
    TD->>AG: runSubagent(csdroid, task + recent changes)

    rect rgba(160, 190, 255, 0.08)
    note over AG,SET: ENVIRONMENT SETUP
    AG->>SET: run detect-env (idempotent)
    SET-->>AG: CSDROID_HARNESS_ROOT / CSDROID_WORKSPACE_ROOT
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
