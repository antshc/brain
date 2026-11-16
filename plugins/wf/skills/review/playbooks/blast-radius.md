# Blast radius

Find what a change breaks somewhere else, before it ships. Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

Use How and Why from Research to ground what the code does and what led to the change.

Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you.

## Scope and constraints

Accept a diff, commit, branch, local change, or PR, with an optional original defect. Identify repository instructions, target head, comparison baseline, changed paths, affected behavior, and relevant test entry points. Ask when the target or baseline is ambiguous.

Pin committed refs to SHAs. For PRs, inspect the actual head and base, title, body, and commits. For local changes, record the dirty-worktree state. Read the glossary and relevant ADRs when present.

Allocate an absolute run directory outside the user's checkout and proof worktrees. Store grounding, Prove reports, evidence, and retained patches there; pass it explicitly to delegated skills.

- **MUST NOT** modify the user's checkout, post PR comments, commit, push, deploy, or reset or clean the user's checkout.
- Permit test additions, test changes, and temporary production instrumentation only in Prove-owned proof worktrees. Record every patch. Establish verdicts against the original target: changes to production behavior cannot prove the original safe. Keep fixes separate from verification.
- Run proofs through Prove, which owns proof worktrees and their cleanup. Preserve reusable regression patches and evidence in the run directory; report leftovers. If safe execution is unavailable, mark the claim unproven with the reason and next step.
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

Resolve this playbook's relative links from its own directory. Use the [proof framing](../references/blast-radius-proof-framing.md) for the per-claim evidence contract. Read it and the [final report contract](../references/blast-radius-report.md) in full before proving and fill every placeholder; pass absolute resource paths.

## Steps

Prove's workers own proof principles; retain the ladder, original-target attribution and per-claim evidence contract in the proof framing.

1. Read the change. The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. *Load and follow the `research` skill to investigate technical questions about why source code was built this way and return cited findings* using **Why**: a request naming the diff scope and any known PR or commit refs, asking only for code, commit, and PR context; read the returned report in full.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. *Load and follow the `research` skill to investigate technical questions across source code via codebase navigation and save cited findings* using **How** (`Route: How`, Flow and Data lenses) for current and downstream behavior around the changed boundary. In the request, name the changed symbols, safety question, code checkout, and save path `<absolute run directory>/grounding-how.md`. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run: microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. Inventory affected behaviors, boundaries, and downstream consumers. Assign IDs to concrete risks and safety claims, including the central safety fact. Give each risk a real likelihood and cost. Keep confirmed, cleared, and unresolved claims; distinguish evidence from inference and never invent a caller or API.
5. Prove every claim. *Load and follow the `prove` skill to confirm or refute technical claims by executing tests, runnable prototypes, GUI E2E checks, or cloud experiments* once with every claim ID from step 4 as a batch, filled from the proof framing: Claims with Baseline and Groups, Facts with grounding and any already-cited suites, Limits, Framing and the run directory's report folder. Prove spawns one prover per claim in parallel, isolates writers in owned worktrees, and reruns each deciding command. Read every returned report in full. Source analysis is grounding; without deciding execution evidence, keep the claim unproven and unresolved. *Done when* every claim ID has a Prove report or blocker.
6. Re-evaluate the blast radius from the Prove reports, in rounds:
   - Central safety fact refuted or narrowed → reopen every claim it cleared and redo step 4 for the affected behaviors.
   - Confirmed defect → hunt the same mechanism at other consumers and boundaries named in `grounding-how.md`; a consumer it does not cover → *Load and follow the `research` skill to investigate technical questions across source code via codebase navigation and save cited findings* using **How** bounded to that consumer, saving beside the original grounding. Each sibling gets a new claim ID.
   - Prover **New claims** and inconclusive reports with a concrete next check → add to the inventory with new IDs.
   - New or reopened IDs → run step 5 with only those claims.

   Stop when a round adds no new claim or after 3 extra rounds; report what remains as unresolved with its next check. *Done when* the last round added no claim or the cap is reached with leftovers listed.
7. For a big or wide change, *Load and follow the `subagents` skill to run an Arena comparison of independent candidates* using **Arena** with two or three distinct model perspectives. Pass the same diff, safety question, grounding, and loaded report contract to each reviewer, with isolated outputs under the absolute run directory. Request an evidence union of every distinct supported finding from all candidates, with claim IDs, candidate provenance, and dropouts; do not retain only the winning report. Require evidence and no recursive Arena. Treat Arena synthesis and candidate evidence as input to aggregation, not the final verdict.

## Aggregate and deliver

The coordinator owns risk judgment and the final result; no separate synthesizer is required.

1. Reconcile every claim ID with a Prove report or named blocker. Verify target/patch identity, decisive citations, assertions, executed test names, observed results, and evidence paths. Missing reports or invalid evidence leave claims unresolved.
2. Merge findings describing the same failure mechanism; preserve original IDs, report provenance, and distinct affected behaviors. Keep supported findings outside the original groups and label their scope.
3. Resolve conflicting verdicts with focused evidence checks, never majority vote or a higher ladder number alone. Bound each conflict follow-up to the missing fact and run it as a step 5 batch; if unavailable or inconclusive, retain the conflict, consequence, and exact next check.
4. Run completeness verification below. Inspect returned diffs and confirm reusable patches and evidence are in the run directory; report worktrees and external resources Prove retained.
5. Recheck the pinned head when remote state may have changed. If it changed, label evidence with the reviewed revision; reverify affected claims before asserting coverage of the new head. Fill the [final report](../references/blast-radius-report.md) in full and return one aggregated result.

## Completeness verification

Before reporting, reconcile the diff and behavior inventory with the evidence records:

- Every changed behavior maps to affected boundaries and downstream consumers, or an evidenced explanation that none apply.
- Every affected behavior maps to a confirmed risk, clearance, or named uncertainty; check relevant contracts, failure paths, configuration, and concurrency beyond the happy path.
- Every risk and safety claim, including cleared claims, has a verdict, ladder level, method, evidence, and an unproven reason/next step when executable proof is missing.
- Every dispatched proof has a completed result or explicit unresolved status. Include newly discovered risks and conflicting results.
- Re-evaluation ended with a round adding no claim, or hit the 3-round cap with leftovers listed.
- Every proof patch, artifact, worktree, and external resource has a recorded retention or cleanup outcome.

Report **coverage complete | incomplete** with omitted or inaccessible scope, separately from **risks resolved | unresolved**. Coverage complete means the inventory was reconciled, not that every claim was proved or the change is safe. Any unresolved claim makes risks unresolved; confirmed defects remain visible even when verification is complete.

## Final prose check

*Load and follow the `writing-style` skill to apply clear, precise writing to review prose with unslop and remove AI tells* using **Unslop only** on the assembled report. Edit prose only. Preserve citations, commands, observed output, proof status, and risk judgments. Strip private details before sharing publicly.

**Reply:** one final report following the loaded report contract, not concatenated Prove reports.
