# Plan: Make `csdroid` a stateless, environment-agnostic implementation agent

> Status: approved, not yet implemented. This document is self-contained so a fresh session can
> implement it end-to-end without the original conversation.

## 1. Problem & goal

### Current state (before this refactor)

The `csdroid` agent is a C# autonomous implementation agent living at
`plugins/pet/agents/csdroid.agent.md`. It is **environment-aware and stateful**:

- Its first step, **ENVIRONMENT SETUP**, runs the `csdroid-setup` skill, which executes
  `detect-env.sh` / `detect-env.ps1` to climb the git tree, resolve `CSDROID_HARNESS_ROOT`
  (outermost enclosing repo) and `CSDROID_WORKSPACE_ROOT` (source repo), and **persist** them to
  `$CSDROID_HARNESS_ROOT/.csdroid.env`.
- Downstream skills reuse those literal paths:
  - `csdroid-implement` reads `ARCHITECTURE.md` / `CODE.md` / `TESTS.md` (+ selected ADR/SDR) from
    `$CSDROID_HARNESS_ROOT`.
  - `csdroid-feedback` reads `VERIFY.md` from `$CSDROID_HARNESS_ROOT` (else a fallback loop).
  - `csdroid-memory` reads/writes/commits the durable decision store at
    `$CSDROID_HARNESS_ROOT/agent/decisions.jsonl`.

The agent is invoked from two callers today:
- **`ralph:dev`** (`plugins/ralph/skills/dev/SKILL.md`) — the AFK orchestrator loop (primary target).
- **`to-droid`** (`plugins/pet/skills/to-droid/SKILL.md`) — **explicitly OUT OF SCOPE** here.

### Goal

Make `csdroid` **stateless and environment-unaware**. The caller (`ralph:dev`) resolves the whole
environment and passes explicit absolute paths + selected context to the agent **as path pointers**.
The agent runs in **YOLO mode (full filesystem access)**, so it reads any path it is pointed at but
**detects nothing itself**. It must work whether launched against a repo root or a
workspace/worktree — the caller decides by passing the right `WORKSPACE_ROOT`.

"Stateless" here means the agent holds no implicit knowledge of its environment and performs no
detection or persistence. It does **not** mean features (docs, decisions, verify) are removed — they
are delivered by the caller as pointers.

## 2. Target design

### 2.1 Task-instructions contract (built by `ralph:dev`, consumed by the agent)

```
## WORKSPACE
- WORKSPACE_ROOT: <abs path>          # run ALL git/build/test/exploration here

## TASK
- Title / Body / Comments

## RELEVANT CONVENTIONS                # dev-written pointers: "read <abs path> §X + ADR-003 and apply"
## APPLICABLE DECISIONS                # pointer to <harness>/agent/decisions.jsonl + the relevant IDs
## VERIFY STEPS                        # pointer to <harness>/VERIFY.md path (agent reads it), else "use fallback"
## RECENT CHANGES                      # last 5 commits
```

Key rule: **every context section is a path pointer — nothing is inlined.**
- RELEVANT CONVENTIONS: pointers to specific doc files/sections (+ selected ADR/SDR rows).
- APPLICABLE DECISIONS: a pointer to `<harness>/agent/decisions.jsonl` **plus the specific decision
  IDs** dev selected as relevant. The agent reads the file and applies those IDs.
- VERIFY STEPS: a pointer to `<harness>/VERIFY.md`. If absent, the agent uses its fallback loop.
- The agent (YOLO fs access) can read harness-root paths even though the harness root is resolved by
  dev, not the agent.

### 2.2 Agent (`plugins/pet/agents/csdroid.agent.md`)

- **Remove** the ENVIRONMENT SETUP step and all path-detection / `CSDROID_HARNESS_ROOT` /
  `CSDROID_WORKSPACE_ROOT` / `.csdroid.env` prose.
- Revised step flow:
  1. **EXPLORATION** — read the code files being modified + neighbors in `WORKSPACE_ROOT`, plus the
     convention/decision files dev pointed at.
  2. **Apply pointed decisions** — read the specific `decisions.jsonl` entries dev pointed at (via
     the `<harness>/agent/decisions.jsonl` path + the listed IDs) and apply them. (Replaces the old
     DECISION CONTEXT step / `csdroid-memory` Read Workflow.)
  3. **IMPLEMENTATION** — apply the generic C# rules (folded in from the retired `csdroid-implement`)
     plus the pointed conventions. Implement in `WORKSPACE_ROOT`.
  4. **FEEDBACK** — run the `csdroid-feedback` skill; it reads the `VERIFY.md` dev pointed at, else
     uses the fallback loop, all in `WORKSPACE_ROOT`.
  5. **Report candidate decisions** — the agent judges durability itself and lists new reusable
     decisions in its output. It **never writes the store**.
- **Status report** — keep `STATUS / SUMMARY / FILES / NOTES` and add a `CANDIDATE DECISIONS` list.
  Drop the old `DECISIONS APPLIED` / `DECISIONS RECORDED` store-commit fields.
- The agent stays C#-specific (name = csdroid); only environment-awareness is stripped.

#### Generic C# rules to fold in from `csdroid-implement` (currently 23 lines)

The retired skill's non-env content must survive inside the agent:
- Place classes per `Source Code Structure` / `Layers Dependency` from `ARCHITECTURE.md` **if
  pointed**, else infer from neighboring files found during EXPLORATION.
- Apply `Solution Design Strategy` / ADRs from `ARCHITECTURE.md` **if pointed**, else follow existing
  code's design choices.
- Write code using `CODE.md` conventions **if pointed**, else match surrounding style. Prefer deep
  modules; avoid speculative features.
- Write tests when: adding a new public method, changing existing behavior, or touching conditional
  logic. Follow `TESTS.md` **if pointed**, else match existing test patterns.

(Reword these so they reference "pointed docs" rather than `$CSDROID_HARNESS_ROOT`.)

### 2.3 Skills

- **DELETE** `plugins/pet/skills/csdroid-setup/` entirely — `SKILL.md`, `scripts/detect-env.sh`,
  `scripts/detect-env.ps1`. Drop the `.csdroid.env` mechanism.
- **RETIRE** `plugins/pet/skills/csdroid-implement/` — remove the directory; its generic C# rules are
  folded into the agent (§2.2); its doc selection/loading logic moves to `ralph:dev` (§2.4b).
- **KEEP** `plugins/pet/skills/csdroid-feedback/` — strip all `CSDROID_HARNESS_ROOT` detection and
  the "look for VERIFY.md at `$CSDROID_HARNESS_ROOT`" resolution. It now receives a **`VERIFY.md`
  path pointer** from the caller (reads that file), or uses the fallback loop in `WORKSPACE_ROOT`.
  Preserve the loop mechanics: Step 0 collect changed files → Step 1 verify (diagnostics/build/test)
  → Step 2 refactoring review; retry cap (3) and the "environment blocker → STATUS: blocked" vs
  "code error → fix & retry" handling.
- **REPURPOSE** `plugins/pet/skills/csdroid-memory/` as a **`ralph:dev` helper** — store mechanics
  only: read-to-select, JSONL record schema, Add/Update workflows, Confidence rules
  (`low`→`medium`→`high`), commit & push once at the harness root. Remove agent-facing framing (the
  "Read Workflow (mandatory before implementation)" is now dev's selection step). The agent no longer
  invokes this skill. Keep the store location `<harness>/agent/decisions.jsonl` and the
  commit-from-harness-root (never worktree) rule.

### 2.4 `ralph:dev` skill (`plugins/ralph/skills/dev/SKILL.md`) — sole env + memory owner

Existing structure to preserve: WORKTREE SETUP (resolve milestone, feature branch, invoke
`/worktree` → captures `SOURCE_REPO`, `WORKTREE_PATH`, `BRANCH`), then the ORCHESTRATOR LOOP
(read state → exit conditions → select task → invoke agent → distill → commit → update PRD → handle
result), then CREATE PULL REQUEST. Add the following:

- **(a) Path resolution** — harness root = the repo `dev` runs in (where the milestone/issues live);
  workspace root = `WORKTREE_PATH` from the `/worktree` skill.
- **(b) Build task context (new sub-step before invoking the agent, currently step 4)** — select the
  relevant `ARCHITECTURE.md` / `CODE.md` / `TESTS.md` sections (+ ADR/SDR rows) and the relevant
  `decisions.jsonl` IDs; assemble the task-instructions contract (§2.1) with `WORKSPACE_ROOT` +
  **path pointers only** (convention files, the `decisions.jsonl` path + relevant IDs, and a
  `VERIFY.md` path pointer). Replace the current bare `## TASK` + `## RECENT CHANGES` prompt.
- **(c) Record reusable decisions (new sub-step after the agent returns)** — take the agent's
  `CANDIDATE DECISIONS`, apply the repurposed `csdroid-memory` qualification + Add/Update/Confidence
  mechanics, record to `<harness>/agent/decisions.jsonl`, and commit + push once at the harness root.
- Existing steps (distill SUMMARY → commit code with `dcode:` prefix → update PRD Implementation
  Decisions / Behavior Rules → handle result complete/partial/blocked → PR) stay.

### 2.5 Memory model — two distinct kinds (do not conflate)

- **PRD implementation decisions** — scoped to one PRD/milestone; live in the **PRD issue**
  (`## Implementation Decisions` / `## Behavior Rules` sections `dev` already maintains).
- **Reusable cross-PRD decisions** — durable, usable for any development; live in
  `<harness>/agent/decisions.jsonl`. **`ralph:dev` owns both selection and save.** The agent only
  *uses* the decisions it is pointed at and *proposes* candidates via its status report; it never
  reads or writes the store directly.

## 3. Out of scope / untouched

- **`to-droid`** (`plugins/pet/skills/to-droid/SKILL.md`) — explicitly out of scope; leave untouched.
  (Note: it still invokes `csdroid`; behavior there is not this refactor's concern.)
- **`docs/handoffs/2026-07-03-decision-memory-refactor.md`** — a dated, divergent older handoff;
  leave untouched.
- **`.github/plugin/marketplace.json`** — registers plugins, not individual skills; **no change**
  needed when deleting/retiring skill directories.
- The pre-commit module-sync hook (`.githooks/pre-commit`) does not sync into these skills; **no
  change**.

## 4. Implementation todos (in dependency order)

1. **agent-rewrite** — Rewrite `csdroid.agent.md`: remove ENV SETUP + path detection; add the task
   contract; revise the flow (§2.2); fold in generic C# rules; update the status report
   (+`CANDIDATE DECISIONS`, −`DECISIONS APPLIED/RECORDED`).
2. **delete-setup** — Delete `plugins/pet/skills/csdroid-setup/` (SKILL.md + both `detect-env`
   scripts); remove `.csdroid.env` usage.
3. **retire-implement** — Remove `plugins/pet/skills/csdroid-implement/`; confirm its rules are
   captured in the agent. (depends on: agent-rewrite)
4. **strip-feedback** — Remove `CSDROID_HARNESS_ROOT` detection from `csdroid-feedback`; it now reads
   a `VERIFY.md` pointer or uses the fallback in `WORKSPACE_ROOT`.
5. **repurpose-memory** — Repurpose `csdroid-memory` as a `ralph:dev` helper (store mechanics only;
   remove agent-facing framing).
6. **dev-skill** — Update `ralph:dev` with (a) path resolution, (b) build-task-context step, (c)
   record-reusable-decisions step; wire the new contract into the agent invocation.
   (depends on: agent-rewrite, repurpose-memory)
7. **rewrite-readme** — Rewrite `plugins/pet/README.md` for the new architecture (its mermaid
   diagrams + prose currently describe `csdroid-setup`, `.csdroid.env`, `CSDROID_HARNESS_ROOT`, the
   old skill wiring). (depends on: all of 1–6)
8. **verify** — Sanity pass: grep for lingering `CSDROID_HARNESS_ROOT` / `csdroid-setup` /
   `.csdroid.env` references outside `_backup/`, `to-droid`, and the handoff doc; confirm internal
   cross-references between the agent and skills are consistent. (depends on: all of 1–7)

## 5. Validation

- These are Copilot skill/agent **markdown** files, not Python — no unit tests apply. Validation is a
  reference-consistency grep (todo 8) plus manual review.
- Suggested check:
  `grep -rn "CSDROID_HARNESS_ROOT\|csdroid-setup\|\.csdroid\.env\|csdroid-implement" --include=*.md
  plugins/ | grep -v _backup` should return only intentional references (e.g. `to-droid`, the
  handoff doc) after the refactor.
