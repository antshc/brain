# crew

A technology-agnostic autonomous coding crew. Two agents — `codey` (implementer) and `chorey` (maintainability reviewer) — share a fixed per-repo settings folder and a five-field report contract; skills supply the reusable rules and the entry/exit points.

## Roster

- **Codey** — implements the assigned task and owns the verdict on whether it succeeded. Its five-field report alone governs `ralph:dev`'s distill, commit, and issue-handling steps.
- **Chorey** — reviews a change set for behavior-preserving cleanup: the checkpoint commit named by a caller-supplied `BASELINE_COMMIT` inside the loop, or Codey's (or any) uncommitted work standalone. Runs only behind a Codey `STATUS: complete` gate inside the loop, but also runs standalone via its own entry point. Reports informationally: it can never turn a successful run into a failed one — if its own cleanup cannot be verified, it discards the cleanup and leaves the prior verified result standing.

## Components

- [agents/codey.agent.md](agents/codey.agent.md) — the implementer. Fixed phases: INPUT → GOTCHAS → BUILD & LSP CHECK → IMPLEMENTATION → FEEDBACK LOOPS → UPDATE GOTCHAS. Resolves convention/state files once during INPUT from a caller-supplied `HARNESS_REPO_PATH`, and works in its invocation directory.
- [agents/chorey.agent.md](agents/chorey.agent.md) — the reviewer. Fixed phases: INPUT → GOTCHAS → REVIEW → VERIFY → UPDATE GOTCHAS. Resolves the same per-repo settings folder as Codey, reviews the checkpoint commit named by an optional caller-supplied `BASELINE_COMMIT` (falling back to the uncommitted work already in its workspace when absent), and self-reverts any cleanup it cannot verify.
- [skills/to-codey/SKILL.md](skills/to-codey/SKILL.md) — Codey's entry point. Resolves Harness Settings, a task (`<description>` | `@plan` | issue URL), gathers recent git changes, and invokes `codey` via `runSubagent` with a `## HARNESS` section carrying `HARNESS_REPO_PATH`.
- [skills/to-chorey/SKILL.md](skills/to-chorey/SKILL.md) — Chorey's standalone entry point. Resolves Harness Settings, gathers uncommitted work into a `## DIFF` section, and invokes `chorey` via `runSubagent` — never supplies `BASELINE_COMMIT`, so Chorey stays on the manual-snapshot revert path.
- [skills/crew-build/SKILL.md](skills/crew-build/SKILL.md) — builds the project and checks LSP availability before implementation (Codey only).
- [skills/crew-implement/SKILL.md](skills/crew-implement/SKILL.md) — implementation rules; consumes the `CODE_PATH` resolved during Codey's INPUT.
- [skills/crew-feedback/SKILL.md](skills/crew-feedback/SKILL.md) — verify loop (LSP/build/test); consumes the `VERIFY_PATH` resolved during INPUT and runs all commands in cwd. Shared by both agents.
- [skills/crew-review/SKILL.md](skills/crew-review/SKILL.md) — Chorey's review procedure; consumes the `CHORE_PATH` and optional `BASELINE_COMMIT` resolved during Chorey's INPUT, applies only behavior-preserving fixes, and owns the revert mechanics Chorey uses when its own edits fail verification — a git-native rollback against `BASELINE_COMMIT` when supplied, otherwise the manual snapshot/restore fallback.
- [skills/crew-gotchas/SKILL.md](skills/crew-gotchas/SKILL.md) — reads gotchas from `GOTCHAS.md` at `$HARNESS_REPO_PATH/.crew` before implementation/review, then distills session friction into new or extended directives and writes them back after feedback loops pass. Shared by both agents.
- [skills/to-commit/SKILL.md](skills/to-commit/SKILL.md) — commits with a `ccode:` prefix, post-task.
- [skills/setup-crew/SKILL.md](skills/setup-crew/SKILL.md) — manual, user-invoked bootstrap that scaffolds missing `CODE.md`/`VERIFY.md`/`CHORE.md`/`GOTCHAS.md` from templates into `$HARNESS_REPO_PATH/.crew/`. Never touches `.harness.env`, never migrates an existing `.droid/` folder. Not part of either agent's pipeline.

## Environment

Neither agent resolves Harness Settings itself. Each receives `HARNESS_REPO_PATH` from its caller in a trusted `## HARNESS` prompt section, validates it (absolute, no `..`, directory exists), and stops as blocked if it is present but invalid. When no `## HARNESS` section is supplied, each falls back to its current working directory (cwd) as `HARNESS_REPO_PATH` and announces the fallback. Harness discovery — calling `/resolve-harness` — is the caller's job (`to-codey`, `to-chorey`, `ralph:dev`).

- `HARNESS_REPO_PATH` — owns all convention/state files, all of which live under `$HARNESS_REPO_PATH/.crew/`. INPUT looks for each file at `$HARNESS_REPO_PATH/.crew/<FILE>` and nowhere else, so running either agent directly (no `## HARNESS` section, `HARNESS_REPO_PATH` = cwd) reads `.crew/` in the repo it was launched in. When no `GOTCHAS.md` exists, INPUT creates `.crew/GOTCHAS.md`; missing `CODE.md`/`VERIFY.md`/`CHORE.md` use their documented fallbacks. Neither agent's INPUT ever creates a missing `CODE.md`, `VERIFY.md`, or `CHORE.md` — run [skills/setup-crew/SKILL.md](skills/setup-crew/SKILL.md) manually to scaffold them (and optionally pre-seed `GOTCHAS.md`) from the templates the crew plugin owns at [skills/setup-crew/templates](skills/setup-crew/templates). There is no `.droid/` read-fallback: a repo still on the old folder is left untouched until someone migrates it by hand.
- **Workspace = cwd** — all code, git, build, test, and exploration commands run in the agent's current working directory. There is no separate workspace variable; callers launch each agent with cwd set to the code repo/worktree.

Harness discovery lives in the caller. `ralph:dev`, `to-codey`, and `to-chorey` all call `/resolve-harness` and pass `HARNESS_REPO_PATH` to the relevant agent via `## HARNESS`.

## Dependencies

```mermaid
graph TD
    U[User / plan.md / issue URL] --> TC[to-codey skill]
    U2[User / uncommitted work] --> TH[to-chorey skill]
    DEV[ralph:dev skill] -->|runSubagent, cwd=worktree, HARNESS_REPO_PATH| CO
    TC -->|runSubagent, HARNESS_REPO_PATH| CO[codey agent]
    TH -->|runSubagent, HARNESS_REPO_PATH + DIFF, no BASELINE_COMMIT| CH[chorey agent]
    DEV -->|runSubagent, gated on Codey STATUS:complete, after checkpoint commit, HARNESS_REPO_PATH + DIFF + BASELINE_COMMIT| CH

    CO -->|GOTCHAS read + UPDATE GOTCHAS write| GOT[crew-gotchas skill]
    CO -->|BUILD & LSP CHECK| BC[crew-build skill]
    CO -->|IMPLEMENTATION| IMP[crew-implement skill]
    CO -->|FEEDBACK LOOPS| FB[crew-feedback skill]

    CH -->|GOTCHAS read + UPDATE GOTCHAS write| GOT
    CH -->|REVIEW| REV[crew-review skill]
    CH -->|VERIFY| FB

    TCM[to-commit skill] -.->|reads STATUS REPORT| CO
    TCM -.->|reads STATUS REPORT, informational only| CH

    CO -.GOTCHAS_PATH read+write.-> GOT
    CO -.CODE_PATH.-> IMP
    CO -.VERIFY_PATH.-> FB
    CH -.GOTCHAS_PATH read+write.-> GOT
    CH -.CHORE_PATH.-> REV
    CH -.VERIFY_PATH.-> FB

    CO -.resolves once from $HARNESS_REPO_PATH/.crew/.-> DOCS[CODE.md / VERIFY.md / GOTCHAS.md]
    CH -.resolves once from $HARNESS_REPO_PATH/.crew/.-> DOCS2[VERIFY.md / CHORE.md / GOTCHAS.md]
```

**Nature of each edge**

- **Hard control-flow**: `to-codey`/`to-chorey`/`ralph:dev` → `codey`/`chorey` → the `crew-*` skills (named literally in agent prose). Harness discovery lives in the caller, not either agent.
- **Soft/implicit**: `to-commit` depends on Codey's STATUS REPORT format (the `ccode:` convention couples them, but nothing enforces it) and reads Chorey's report informationally for the commit body only — never for `STATUS`.
- **Resolution contract**: the caller resolves Harness Settings via `/resolve-harness` (or falls back to cwd) and passes `HARNESS_REPO_PATH` via a `## HARNESS` section; each agent validates it, resolves its own set of paths during INPUT, and passes each path to the relevant `crew-*` skill.
- **External file contracts**: each `crew-*` skill consumes only the resolved path the calling agent supplies; each agent's INPUT owns validation and fallback `GOTCHAS.md` creation.
- **Outcome governance**: Codey's `STATUS` alone governs `ralph:dev`'s distill/commit/issue-handling steps. Chorey's `STATUS` never reaches that decision — its findings surface in its own follow-up commit body only, never Codey's.

## Execution sequence

Both agents run a fixed pipeline. Codey's phases and the skill each invokes:

```mermaid
sequenceDiagram
    actor User
    participant TC as to-codey skill
    participant CO as codey agent
    participant GOT as crew-gotchas skill
    participant BC as crew-build skill
    participant IMP as crew-implement skill
    participant FB as crew-feedback skill
    participant TCM as to-commit skill

    User->>TC: task (<description> | @plan | issue URL)
    TC->>TC: resolve Harness Settings + task + gather recent git changes
    TC->>CO: runSubagent(codey, ## HARNESS + task + recent changes)

    rect rgba(160, 190, 255, 0.08)
    note over CO: INPUT — validate supplied HARNESS_REPO_PATH (or fallback cwd); resolve paths; workspace = cwd
    end

    rect rgba(160, 190, 255, 0.08)
    note over CO,GOT: GOTCHAS
    CO->>GOT: Read Workflow (load curated directives)
    GOT-->>CO: gotchas loaded or "none recorded yet"
    end

    rect rgba(160, 190, 255, 0.08)
    note over CO,BC: BUILD & LSP CHECK
    CO->>BC: build project + check LSP availability
    BC-->>CO: pass or blocked
    end

    rect rgba(160, 190, 255, 0.08)
    note over CO,IMP: IMPLEMENTATION
    CO->>IMP: apply style / layers / tests rules
    IMP-->>CO: docs loaded + code implemented
    end

    rect rgba(160, 190, 255, 0.08)
    note over CO,FB: FEEDBACK LOOPS
    CO->>FB: verify (LSP / build / test)
    FB-->>CO: pass or issues to fix
    end

    rect rgba(160, 190, 255, 0.08)
    note over CO,GOT: UPDATE GOTCHAS
    CO->>GOT: Write Workflow (distill session friction)
    GOT-->>CO: gotchas updated or "none to record"
    end

    CO-->>User: STATUS REPORT
    TCM-->>CO: reads STATUS REPORT (ccode: commit, post-task)
```

Chorey follows only when Codey reports `STATUS: complete` (behind the loop's checkpoint-commit gate) or runs standalone via `to-chorey` with no prior Codey run. Both entry points supply `## HARNESS` + `## DIFF`; they differ in whether a `BASELINE_COMMIT` is supplied — `ralph:dev` invokes `chorey` directly (bypassing `to-chorey`) right after committing Codey's checkpoint, passing that commit's SHA alongside its diff; `to-chorey` never supplies one, so Chorey reviews the uncommitted work already in the workspace instead:

```mermaid
sequenceDiagram
    actor User
    participant TH as to-chorey skill
    participant CH as chorey agent
    participant GOT as crew-gotchas skill
    participant REV as crew-review skill
    participant FB as crew-feedback skill

    User->>TH: standalone (no prior Codey run)
    TH->>TH: resolve Harness Settings + gather uncommitted work
    TH->>CH: runSubagent(chorey, ## HARNESS + ## DIFF (uncommitted work), no BASELINE_COMMIT)
    note over CH: ralph:dev instead invokes chorey directly, right after committing Codey's checkpoint,<br/>passing ## HARNESS + ## DIFF (the checkpoint commit's diff) + ## BASELINE_COMMIT (the checkpoint commit's SHA)

    rect rgba(255, 200, 160, 0.08)
    note over CH: INPUT — validate supplied HARNESS_REPO_PATH (or fallback cwd); resolve paths incl. optional BASELINE_COMMIT; workspace = cwd
    end

    rect rgba(255, 200, 160, 0.08)
    note over CH,GOT: GOTCHAS
    CH->>GOT: Read Workflow (load curated directives)
    GOT-->>CH: gotchas loaded or "none recorded yet"
    end

    rect rgba(255, 200, 160, 0.08)
    note over CH,REV: REVIEW
    CH->>REV: identify change set (BASELINE_COMMIT's diff, or uncommitted work) + revert baseline, apply safe fixes, record unsafe findings
    REV-->>CH: files changed (or none) + findings
    end

    rect rgba(255, 200, 160, 0.08)
    note over CH,FB: VERIFY (skipped when REVIEW changed nothing)
    CH->>FB: verify Chorey's own edits
    FB-->>CH: pass, or fail past retry cap / environment blocker
    end

    alt VERIFY failed
    CH->>REV: Revert — restore BASELINE_COMMIT (git-native) or Step 0 snapshot (manual), move discarded edits into Findings
    end

    rect rgba(255, 200, 160, 0.08)
    note over CH,GOT: UPDATE GOTCHAS
    CH->>GOT: Write Workflow (distill session friction)
    GOT-->>CH: gotchas updated or "none to record"
    end

    CH-->>User: STATUS REPORT (informational; never overrides Codey's STATUS)
```
