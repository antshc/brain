---
name: architecture
description: Audit architecture drift between ARCHITECTURE.md (excluding ADRs) plus the SSR docs and the actual codebase. Use when the user wants to check whether the code still matches the documented architecture, audit SSR compliance, or find where the implementation has diverged from a documented decision. Argument `auto` (default, non-interactive, log-only) or `human` (interactive, may edit docs).
disable-model-invocation: true
---

Scope: codebase vs `ARCHITECTURE.md` (non-ADR) + `docs/ssr/*.md`. ADRs out of scope. Verify codebase facts via `explore` agent, never ask. Exclude claims already in `docs/architecture-drift-log.md` (any status). Docs-only — never edit code.

## Mode

Argument hint: `auto` (default) | `human`.

- Detect explicit mode word in invocation (e.g. "human", "interactively"); else **auto**.
- State resolved mode at run start.
- Discovery Step 0–2: shared setup, run once. Discovery Step 3: hand off — `auto` → Auto mode Step 1, `human` → Human mode Step 1.

## Discovery

### Step 0: Prior findings

- Read `docs/architecture-drift-log.md` (empty if missing).
- Set of already-recorded (Source, Documented) pairs, any Status.

### Step 1: Claims

- Read every non-ADR `ARCHITECTURE.md` section + full text of every SSR in its index table.
- Extract atomic, checkable claims: folder structure, naming rule, layering/reference direction, wiring pattern.
- Skip non-verifiable prose.
- Drop claims matching Discovery Step 0 pairs.

### Step 2: Legwork

- Per claim/claim group: spawn `explore` agent (`runSubagent`); prefer LSP (usages/definitions/implementations) for layering/reference-direction/wiring claims, else grep/semantic search/`list_dir`; require verdict + supporting path(s).
- Never verify inline.
- Verdict: `Aligned` | `Drifted` | `Unverifiable` (drop `Unverifiable`).

### Step 3: Log drift process

- Hand off per Mode: `auto` → Auto mode Step 1; `human` → Human mode Step 1.
- Sub-flow logs/resolves drift (own Step 1–3), loops back to Discovery Step 2 for next unverdicted claim.
- Terminal when every Discovery Step 1 claim resolved.

## Auto mode

Entered via Discovery Step 3. Autonomous — no user interaction, never touch `ARCHITECTURE.md`/`docs/ssr/*.md`.

### Step 1: Accept

- Auto-confirm every `Drifted` verdict from Discovery Step 2.

### Step 2: Log

- Append one row per confirmed `Drifted` claim to `docs/architecture-drift-log.md` (create with table format below if missing), Status `Open`.
- Append immediately, don't batch.

### Step 3: Loop

- Return to Discovery Step 2 for next unverdicted claim; re-enter Auto mode Step 1 per verdict.
- On terminal state (all Discovery Step 1 claims resolved): report full drift summary, new vs. already-recorded.

## Human mode

Entered via Discovery Step 3. Interactive — confirm with user, apply resolution immediately.

### Step 1: Confirm

- One `Drifted` claim per question: claim, evidence, recommended verdict. Wait for answer before next. No batching.

### Step 2: Resolve

- Per confirmed drift, recommend one:
  1. **Update `ARCHITECTURE.md`** — rewrite to match code.
  2. **Update the SSR** — rewrite the record.
  3. **Log it** — append row to `docs/architecture-drift-log.md` (create with table below if missing).
- Fold user clarifications into the edit before applying.
- User disagrees with verdict: revert to unconfirmed, return to Human mode Step 1.
- Apply immediately, never batch to end of run.
- Edits confined to `ARCHITECTURE.md`, `docs/ssr/*.md`, `docs/architecture-drift-log.md` — never source code.

### Step 3: Loop

- Return to Discovery Step 2 for next unverdicted claim; re-enter Human mode Step 1 per verdict.
- On terminal state (all Discovery Step 1 claims resolved): report full drift summary, new vs. already-recorded.

### `docs/architecture-drift-log.md` format

| Date | Source (Architecture section / SSR #) | Documented | Observed | Status | Notes |
|------|----------------------------------------|------------|----------|--------|-------|
| YYYY-MM-DD | e.g. SSR 0009 | what the doc says | what the code does | Open / Resolved | owner, follow-up |
