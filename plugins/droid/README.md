# droid

A technology-agnostic autonomous coding harness. One agent (`droid`) orchestrates a fixed pipeline; skills supply the reusable rules and the entry/exit points.

## Components

- [agents/droid.agent.md](agents/droid.agent.md) — the orchestrator. Fixed phases: INPUT → GOTCHAS → BUILD & LSP CHECK → IMPLEMENTATION → FEEDBACK LOOPS → UPDATE GOTCHAS → STATUS REPORT. Resolves convention/state files once during INPUT from a caller-supplied `HARNESS_REPO_PATH`, and works in its invocation directory.
- [skills/to-droid/SKILL.md](skills/to-droid/SKILL.md) — entry point. Resolves Harness Settings, a task (`<description>` | `@plan` | issue URL), gathers recent git changes, and invokes `droid` via `runSubagent` with a `## HARNESS` section carrying `HARNESS_REPO_PATH`.
- [skills/droid-build-check/SKILL.md](skills/droid-build-check/SKILL.md) — builds the project and checks LSP availability before implementation.
- [skills/droid-implement/SKILL.md](skills/droid-implement/SKILL.md) — implementation rules; consumes the `CODE_PATH` resolved during INPUT.
- [skills/droid-feedback/SKILL.md](skills/droid-feedback/SKILL.md) — verify loop (LSP/build/test); consumes the `VERIFY_PATH` resolved during INPUT and runs all commands in cwd.
- [skills/droid-gotchas/SKILL.md](skills/droid-gotchas/SKILL.md) — reads gotchas from `GOTCHAS.md` at `$HARNESS_REPO_PATH/.droid` before implementation, then distills session friction into new or extended directives and writes them back after feedback loops pass.
- [skills/to-commit/SKILL.md](skills/to-commit/SKILL.md) — commits with a `dcode:` prefix, post-task.
- [skills/setup-droid/SKILL.md](skills/setup-droid/SKILL.md) — manual, user-invoked bootstrap that scaffolds missing `CODE.md`/`VERIFY.md`/`GOTCHAS.md` from templates into `$HARNESS_REPO_PATH/.droid/`. Never touches `.harness.env`. Not part of the agent's pipeline.

## Environment

Droid never resolves Harness Settings itself. It receives `HARNESS_REPO_PATH` from its caller in a trusted `## HARNESS` prompt section, validates it (absolute, no `..`, directory exists), and stops as blocked if it is present but invalid. When no `## HARNESS` section is supplied, it falls back to its current working directory (cwd) as `HARNESS_REPO_PATH` and announces the fallback. Harness discovery — calling `/resolve-harness` — is the caller's job (`to-droid`, `ralph:dev`).

- `HARNESS_REPO_PATH` — owns all convention/state files, all of which live under `$HARNESS_REPO_PATH/.droid/`. INPUT looks for each file at `$HARNESS_REPO_PATH/.droid/<FILE>` and nowhere else, so running the agent directly (no `## HARNESS` section, `HARNESS_REPO_PATH` = cwd) reads `.droid/` in the repo it was launched in. When no `GOTCHAS.md` exists, INPUT creates `.droid/GOTCHAS.md`; missing CODE and VERIFY files use their documented fallbacks. INPUT itself never creates missing `CODE.md` or `VERIFY.md` — run [skills/setup-droid/SKILL.md](skills/setup-droid/SKILL.md) manually to scaffold them (and optionally pre-seed `GOTCHAS.md`) from the templates the droid plugin owns at [skills/setup-droid/templates](skills/setup-droid/templates).
- **Workspace = cwd** — all code, git, build, test, and exploration commands run in the agent's current working directory. There is no separate workspace variable; callers launch the agent with cwd set to the code repo/worktree.

Harness discovery lives in the caller. Both `ralph:dev` and `to-droid` call `/resolve-harness` and pass `HARNESS_REPO_PATH` to the agent via `## HARNESS`.

## Dependencies

```mermaid
graph TD
    U[User / plan.md / issue URL] --> TD[to-droid skill]
    DEV[ralph:dev skill] -->|runSubagent, cwd=worktree, HARNESS_REPO_PATH| AG
    TD -->|runSubagent, HARNESS_REPO_PATH| AG[droid agent]
    AG -->|GOTCHAS read + UPDATE GOTCHAS write| GOT[droid-gotchas skill]
    AG -->|BUILD & LSP CHECK| BC[droid-build-check skill]
    AG -->|IMPLEMENTATION| IMP[droid-implement skill]
    AG -->|FEEDBACK LOOPS| FB[droid-feedback skill]
    TC[to-commit skill] -.->|reads STATUS REPORT| AG

    AG -.GOTCHAS_PATH read+write.-> GOT
    AG -.CODE_PATH.-> IMP
    AG -.VERIFY_PATH.-> FB

    AG -.resolves once from $HARNESS_REPO_PATH/.droid/.-> DOCS[CODE.md / VERIFY.md / GOTCHAS.md]
```

**Nature of each edge**

- **Hard control-flow**: `to-droid` / `ralph:dev` → `droid` → the `droid-*` skills (named literally in the agent prose). Harness discovery lives in the caller, not `droid`.
- **Soft/implicit**: `to-commit` depends on the agent's STATUS REPORT format (the `dcode:` convention couples them, but nothing enforces it).
- **Resolution contract**: the caller resolves Harness Settings via `/resolve-harness` (or falls back to cwd) and passes `HARNESS_REPO_PATH` via a `## HARNESS` section; the agent validates it, resolves the three paths during INPUT, and passes each path to the relevant `droid-*` skill.
- **External file contracts**: each `droid-*` skill consumes only the resolved path the agent supplies; INPUT owns validation and fallback `GOTCHAS.md` creation.

## Execution sequence

The `droid` agent runs a fixed pipeline. Each phase and the skill it invokes:

```mermaid
sequenceDiagram
    actor User
    participant TD as to-droid skill
    participant AG as droid agent
    participant GOT as droid-gotchas skill
    participant BC as droid-build-check skill
    participant IMP as droid-implement skill
    participant FB as droid-feedback skill
    participant TC as to-commit skill

    User->>TD: task (<description> | @plan | issue URL)
    TD->>TD: resolve Harness Settings + task + gather recent git changes
    TD->>AG: runSubagent(droid, ## HARNESS + task + recent changes)

    rect rgba(160, 190, 255, 0.08)
    note over AG: INPUT — validate supplied HARNESS_REPO_PATH (or fallback cwd); resolve paths; workspace = cwd
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,GOT: GOTCHAS
    AG->>GOT: Read Workflow (load curated directives)
    GOT-->>AG: gotchas loaded or "none recorded yet"
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,BC: BUILD & LSP CHECK
    AG->>BC: build project + check LSP availability
    BC-->>AG: pass or blocked
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,IMP: IMPLEMENTATION
    AG->>IMP: apply style / layers / tests rules
    IMP-->>AG: docs loaded + code implemented
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,FB: FEEDBACK LOOPS
    AG->>FB: verify (LSP / build / test)
    FB-->>AG: pass or issues to fix
    end

    rect rgba(160, 190, 255, 0.08)
    note over AG,GOT: UPDATE GOTCHAS
    AG->>GOT: Write Workflow (distill session friction)
    GOT-->>AG: gotchas updated or "none to record"
    end

    AG-->>User: STATUS REPORT
    TC-->>AG: reads STATUS REPORT (dcode: commit, post-task)
```
