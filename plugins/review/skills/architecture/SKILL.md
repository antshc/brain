---
name: architecture
description: Audit architecture drift between ARCHITECTURE.md (excluding ADRs) plus the SSR docs and the actual codebase. Use when the user wants to check whether the code still matches the documented architecture, audit SSR compliance, or find where the implementation has diverged from a documented decision.
disable-model-invocation: true
---

Scope: the codebase vs `ARCHITECTURE.md` (non-ADR sections only) + `docs/ssr/*.md`. ADRs (table + linked files) out of scope. Codebase facts: verify yourself via `explore` agent, never ask. Drift verdict + resolution: user's call, always confirm. Docs-only — never edit code.

## Step 1: Claims

- Read every non-ADR `ARCHITECTURE.md` section + full text of every SSR in its index table (index line alone is insufficient).
- Extract atomic, checkable claims: folder structure, naming rule, layering/reference direction, wiring pattern.
- Skip non-verifiable prose (overview, glossary pointers).
- Done when: every section/SSR → claims, or tagged "no verifiable claim."

## Step 2: Legwork

- Per claim (or claim group): spawn `explore` agent (`runSubagent`) with the claim; instruct it to prefer LSP (usages/definitions/implementations) for layering/reference-direction/wiring claims, grep/semantic search/`list_dir` otherwise; require verdict + supporting path(s) back.
- Never verify inline yourself.
- Verdict per claim: `Aligned` | `Drifted` | `Unverifiable` (drop `Unverifiable` — not drift).
- Done when: every claim has a verdict; every `Drifted` cites the contradicting path(s).

## Step 3: Confirm

- One `Drifted` claim per question: claim, evidence, your recommended verdict (real drift vs. search miss). Wait for answer before the next.
- No batching.
- Done when: every `Drifted` claim confirmed or dismissed.

## Step 4: Resolve

- Per confirmed drift, offer + recommend one:
  1. **Update `ARCHITECTURE.md`** — rewrite to match code.
  2. **Update the SSR** — rewrite the record.
  3. **Log it** — append row to `docs/architecture-drift-log.md` (create with table below if missing).
- User clarifies/amends: fold into the edit before applying.
- User disagrees with the verdict: revert claim to unconfirmed, return to Step 3.
- Apply directly. Edits confined to `ARCHITECTURE.md`, `docs/ssr/*.md`, `docs/architecture-drift-log.md` — never the source codebase.
- Done when: every confirmed drift has exactly one resolution applied.

## Step 5: Loop

- Go back to Step 2 for the next unverdicted claim. Repeat Steps 2–4 claim by claim.
- Never stop after one claim or one batch.
- Done when: every claim from Step 1 has reached a terminal state (`Aligned`, `Unverifiable`, dismissed, or resolved) — only then report the full drift summary.

### `docs/architecture-drift-log.md` format

| Date | Source (Architecture section / SSR #) | Documented | Observed | Status | Notes |
|------|----------------------------------------|------------|----------|--------|-------|
| YYYY-MM-DD | e.g. SSR 0009 | what the doc says | what the code does | Open / Resolved | owner, follow-up |
