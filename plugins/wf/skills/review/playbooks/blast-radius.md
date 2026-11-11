# Blast radius

Find what a change breaks somewhere else, before it ships. Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

Use How and Why from Research to ground what the code does and what led to the change.

Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you.

## Scope and constraints

Accept a diff, commit, branch, local change, or PR, with an optional original defect. Identify repository instructions, target head, comparison baseline, changed paths, affected behavior, and relevant test entry points. Ask when the target or baseline is ambiguous.

Pin committed refs to SHAs. For PRs, inspect the actual head and base, title, body, and commits. For local changes, record the dirty-worktree state. Read the glossary and relevant ADRs when present.

Allocate an absolute run directory outside the user's checkout and proof worktrees. Store grounding, worker outputs, evidence, and retained patches there; pass it explicitly to delegated skills.

- **MUST NOT** modify the user's checkout, post PR comments, commit, push, deploy, or reset or clean the user's checkout.
- Permit test additions, test changes, and temporary production instrumentation only in owned proof worktrees created through `git`. Record every patch. Establish verdicts against the original target: changes to production behavior cannot prove the original safe. Keep fixes separate from verification.
- Run proofs in run-owned locations. Preserve reusable regression patches and evidence outside the worktrees before cleanup; *use `git` skill for verified worktree lifecycle and removal* using Worktrees and report leftovers. If safe execution is unavailable, mark the claim unproven with the reason and next step.
- Redact secrets, credentials, and customer data. Distinguish source evidence, observed execution, and inference.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it's true. So don't hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code.

### How sure are you

Apply this ladder to every risk, cleared risk, and safety claim. Attempt executable proof for each; record the highest supported level, method, and where verification stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You traced the failure step by step and established whether it can reach the bad case, including the relevant guards and assumptions.
4. You ran it. A script or test that calls the real code and fails loud if you're wrong.
5. You reproduced it in the running app.

Keep verdict (`confirmed | cleared | unresolved`) separate from evidence level. Execution can confirm a defect or clear it for the exercised conditions. Levels 1–2 alone cannot establish safety. A missing caller in search results is a search observation, not proof of unreachability. Scope every clearance to its evidence; never generalize one passing case to all inputs.

Resolve this playbook's relative links from its own directory. Use the [worker prompt](../references/blast-radius-worker-prompt.md) for the per-claim evidence contract. Read it and the [final report contract](../references/blast-radius-report.md) in full before dispatch and fill every worker placeholder; pass absolute resource paths to workers.

## Steps

1. Read the change. The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. *Run `research` skill to investigate primary sources and return cited findings* using **Why code anchor** (`@mode=why`, `@whyDepth=anchor`). Pass the diff scope and any known PR or commit refs. Request the PR and commit context inline.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. *Run `research` skill to investigate primary sources and return cited findings* using **default Research** for current and downstream behavior around the changed boundary. Pass the changed symbols and safety question. Pass `@outputPath=grounding-how.md` and the absolute run directory as `@outputBase`; identify the code checkout separately. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run: microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. Inventory affected behaviors, boundaries, and downstream consumers. Assign IDs to concrete risks and safety claims, including the central safety fact. Give each risk a real likelihood and cost. Keep confirmed, cleared, and unresolved claims; distinguish evidence from inference and never invent a caller or API.
5. *Run `testing-integrations` skill to pick the minimal seam for regression tests.* Discover suites that exercise each claim's failure mechanism. Pass target identity, original launch/harness root, explicit checkout, behavior inventory, and claim IDs. Retain cited suite commands and prerequisites for worker briefs; discovery does not establish proof.
6. Prove every claim. *Run `subagents` skill to dispatch independent workers with isolated outputs* using **Dispatch** for independent claim groups, supplying the filled worker prompt, evidence contract, exact artifact destinations, and worktree requirements. Require the same pinned target and, for dirty targets, the same recorded tracked/untracked inputs. Require separate owned `git` worktrees for writers; share discovery and serialize groups using shared mutable resources unless isolated. Let Dispatch own launch, parallel execution, collection, and worktree creation. If parallel execution is unavailable, use the same briefs sequentially and report the limitation; unavailable required isolation blocks that proof.
7. For a big or wide change, *run `subagents` skill using **Arena** to compare independent candidates and synthesize findings* with two or three distinct model perspectives. Pass the same diff, safety question, grounding, and loaded report contract to each reviewer, with isolated outputs under the absolute run directory. Request an evidence union of every distinct supported finding from all candidates, with claim IDs, candidate provenance, and dropouts; do not retain only the winning report. Require evidence and no recursive Arena. Treat Arena synthesis and candidate evidence as input to aggregation, not the final verdict.

## Aggregate and deliver

The coordinator owns risk judgment and the final result; no separate synthesizer is required.

1. Reconcile every assignment and claim ID with a terminal result or named blocker. Verify target/patch identity, decisive citations, assertions, executed test names, observed results, and evidence paths. Missing workers or invalid evidence leave claims unresolved.
2. Merge findings describing the same failure mechanism; preserve original IDs, worker provenance, and distinct affected behaviors. Keep supported findings outside the original groups and label their scope.
3. Resolve conflicting verdicts with focused evidence checks, never majority vote or a higher ladder number alone. Send newly discovered risks and material gaps through steps 5–6. Bound each follow-up to the missing fact; if unavailable or inconclusive, retain the conflict, consequence, and exact next check.
4. Run completeness verification below. Inspect returned diffs, preserve reusable patches and evidence outside worktrees, then *use `git` skill for verified worktree lifecycle and removal* using Worktrees; report retained worktrees and external resources.
5. Recheck the pinned head when remote state may have changed. If it changed, label evidence with the reviewed revision; reverify affected claims before asserting coverage of the new head. Fill the [final report](../references/blast-radius-report.md) in full and return one aggregated result.

## Completeness verification

Before reporting, reconcile the diff and behavior inventory with the evidence records:

- Every changed behavior maps to affected boundaries and downstream consumers, or an evidenced explanation that none apply.
- Every affected behavior maps to a confirmed risk, clearance, or named uncertainty; check relevant contracts, failure paths, configuration, and concurrency beyond the happy path.
- Every risk and safety claim, including cleared claims, has a verdict, ladder level, method, evidence, and an unproven reason/next step when executable proof is missing.
- Every dispatched proof has a completed result or explicit unresolved status. Include newly discovered risks and conflicting results.
- Every proof patch, artifact, worktree, and external resource has a recorded retention or cleanup outcome.

Report **coverage complete | incomplete** with omitted or inaccessible scope, separately from **risks resolved | unresolved**. Coverage complete means the inventory was reconciled, not that every claim was proved or the change is safe. Any unresolved claim makes risks unresolved; confirmed defects remain visible even when verification is complete.

## Final prose check

*Run `writing-style` skill to review prose with unslop and remove AI tells* using **Unslop only** on the assembled report. Edit prose only. Preserve citations, commands, observed output, proof status, and risk judgments. Strip private details before sharing publicly.

**Reply:** one final report following the loaded report contract, not concatenated worker reports.
