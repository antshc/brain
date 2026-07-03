# Handoff — decision-memory refactor (grilling → implementation)

**Date:** 2026-07-03
**Status:** Design agreed via grilling session. NOT yet implemented. One point left at a recommended default (see §4).
**Next session focus:** Continue grilling if needed, otherwise implement the plan below.

## Goal (user's original request)

Move `csdroid-memory` out of the `pet` plugin, make it independent, and drive it from the `ralph` plugin's `dev` skill:
- In `ralph/dev` **step 4**, surface prior decisions helpful for task implementation.
- In `ralph/dev` **step 5**, durable decisions must be saved to `decisions.jsonl`.

## Agreed design (converged answers)

### 1. Move & genericize the skill
- Move `plugins/pet/skills/csdroid-memory/` → **`skills/decision-memory/`** (top-level, not wrapped in a plugin.json — same as other top-level skills like `qa`, `analyze-prompt`). Delete the pet copy.
- Rename skill `csdroid-memory` → **`decision-memory`**.
- Fully genericize: remove C#/pet framing and the `CSDROID_HARNESS_ROOT` env var; use a generic caller-supplied **STORE path** variable.
- Store stays at `<harness-root>/agent/decisions.jsonl` (same relative location).
- Keep the workflows: Read, Lookup, Add, Update, Confidence Bump, and the Record Schema/Confidence rules.

### 2. Make `plugins/pet/agents/csdroid.agent.md` stateless/isolated
- **Remove** the `## DECISION CONTEXT` and `## RECORD DECISIONS` steps.
- **Keep** ENVIRONMENT SETUP, EXPLORATION, IMPLEMENTATION, FEEDBACK LOOPS (convention-doc skills `csdroid-implement`/`csdroid-feedback` still depend on `CSDROID_HARNESS_ROOT` from `csdroid-setup`, so ENVIRONMENT SETUP stays).
- **Remove both** `DECISIONS APPLIED` and `DECISIONS RECORDED` lines from the STATUS REPORT block.

### 3. `plugins/ralph/skills/dev/SKILL.md` orchestration
- At the very start (before worktree), capture `HARNESS_ROOT` via `git rev-parse --show-toplevel`. Store = `$HARNESS_ROOT/agent/decisions.jsonl`.
- **Step 4 (Invoke implementation agent):** orchestrator runs the decision-memory **Read/filter** workflow (filter by matching decision `scope`/`tags`/`topic` against the task **title+body text**), then injects a new **`## PRIOR DECISIONS`** block into the agent task prompt AND explicitly passes the **`WORKTREE_PATH`** (code path) in the prompt. The agent is stateless — it consumes this context and never touches the store itself.
- **Step 5 (Distill):** keep the existing per-task *Implementation Decisions* + *Behavior Rules* outputs (they feed the commit body and PRD — global/task context, unchanged). **Additionally**, write durable decisions to `decisions.jsonl` via the decision-memory Add/Update workflow. NOTE the user's distinction: *Implementation Decisions* = per-task context (commit/PRD); *decisions.jsonl* entries = reusable global memory for any future development.

### 4. Persistence of decisions.jsonl — ⚠ UNRESOLVED (recommended default)
- Store lives at the harness repo root, which is a **separate git working tree** from the feature-branch worktree (`WORKTREE_PATH`). So it cannot ride along in the step-6 feature-branch commit.
- **Recommended default (agreed as fallback):** `ralph/dev` commits+pushes `decisions.jsonl` as a **separate harness-repo commit** immediately after the step-5 write; the `decision-memory` skill **drops its own "Commit & Push" section**.
- **Open ambiguity:** in the last (cancelled) round the user typed "call the /handoff skill, save to docs/handoffs" in answer to the commit question. `/handoff` (in `plugins/wf/skills/handoff/`) only writes a conversation summary doc — it does NOT persist `decisions.jsonl`. It is unclear whether the user wants, in addition, a `/handoff`-generated doc in `docs/handoffs/` at end-of-dev or per-task. **Resolve this before implementing** — options presented were: (a) no /handoff involvement, (b) call /handoff → docs/handoffs at END of the whole /dev run, (c) per-task /handoff → docs/handoffs.

### 5. Cleanup / references to update
- Delete `plugins/pet/skills/csdroid-memory/` entirely.
- Update `plugins/pet/README.md` — mermaid diagrams and prose reference `csdroid-memory` skill and `agent/decisions.jsonl` (lines ~7, 12, 23, 33, 45, 52-53, 65, 83, 101).
- Update `plugins/pet/skills/csdroid-setup/SKILL.md:14` wording that says `CSDROID_HARNESS_ROOT` "owns `agent/decisions.jsonl`" (pet no longer manages the store).
- Top-level `skills/` are NOT registered in any plugin.json/marketplace; no marketplace.json change needed for a top-level skill. (`.github/plugin/marketplace.json` only lists plugins.)

## Key facts about the codebase (verified this session)
- `ralph/dev` invokes the `csdroid` agent via `runSubagent` (falls back to `general-purpose`). It works in `WORKTREE_PATH`; only milestone/issue commands target the harness `repo`.
- The worktree is created by the `/worktree` skill from `SOURCE_REPO` (the `workspace/` source repo when it has a `.git`, else the harness repo). Harness root and worktree can be different repos.
- Current store contract: `$CSDROID_HARNESS_ROOT/agent/decisions.jsonl`; original skill committed it from `CSDROID_HARNESS_ROOT`, never the worktree — the separate-commit approach in §4 preserves that.
- `CSDROID_HARNESS_ROOT` is the outermost enclosing repo, resolved/persisted (`.csdroid.env`) by the `csdroid-setup` skill's idempotent `detect-env` script.

## Files in scope
- `plugins/pet/skills/csdroid-memory/SKILL.md` (move + genericize → `skills/decision-memory/SKILL.md`)
- `plugins/pet/agents/csdroid.agent.md` (strip decision steps + status fields)
- `plugins/ralph/skills/dev/SKILL.md` (steps 4 & 5 + HARNESS_ROOT capture + step-6 commit of store)
- `plugins/pet/README.md`, `plugins/pet/skills/csdroid-setup/SKILL.md` (reference cleanup)

## Suggested skills for the next session
- **grill-me** — if the user wants to resolve the §4 commit/handoff ambiguity before coding.
- **to-issues** / **to-prd** — if this refactor should be tracked as GitHub issues/PRD first.
- **to-commit** — to commit the changes once implemented.
- **local** (code review) — to review the implemented diff before committing.
