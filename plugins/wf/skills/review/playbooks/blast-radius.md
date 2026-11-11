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
- Run proofs in run-owned locations. Preserve reusable regression patches and evidence outside the worktrees before cleanup; use `git` for owned worktree cleanup and report leftovers. If safe execution is unavailable, mark the claim unproven with the reason and next step.
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

For each claim, record a stable ID, failure mechanism, `file:line`, likelihood, impact, verdict, ladder level, proof method, and evidence. For execution, include target SHA or local-state identity, environment, exact command, test names, observed output, and artifact paths. Without executable proof, write **unproven**, why it could not run or establish the claim, and the next verification step; retain any supported source-level conclusion.

Associate each execution with the hashes of its applied patches. Never weaken valid assertions or skip failing tests to obtain proof. For production instrumentation, rerun without it or explain why it preserves the behavior being claimed. To attribute a defect to this change, compare the same proof on the pinned baseline and target; otherwise mark regression attribution unproven with the reason.

## Steps

1. Read the change. The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. *Run `research` skill to investigate primary sources and return cited findings* using **Why code anchor** (`@mode=why`, `@whyDepth=anchor`). Pass the diff scope and any known PR or commit refs. Request the PR and commit context inline.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. *Run `research` skill to investigate primary sources and return cited findings* using **default Research** for current and downstream behavior around the changed boundary. Pass the changed symbols and safety question. Pass `@outputPath=grounding-how.md` and the absolute run directory as `@outputBase`; identify the code checkout separately. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run: microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. Inventory affected behaviors, boundaries, and downstream consumers. Assign IDs to concrete risks and safety claims, including the central safety fact. Give each risk a real likelihood and cost. Keep confirmed, cleared, and unresolved claims; distinguish evidence from inference and never invent a caller or API.
5. *Run `testing-integrations` skill to discover suites and select the smallest test seam that exercises each claim's failure mechanism.* Pass the pinned target, original launch/harness root, explicit code checkout, behavior inventory, and claim IDs. Map each claim to an existing test and inspect its fixtures and assertions; mocks that remove the suspect boundary cannot prove it. Use documented commands and narrow filters. Add or adapt a test in an owned proof worktree when coverage is missing; use the skill's experiment route for an uncertain question. Report unavailable suites, skipped tests, and prerequisites instead of inventing commands.
6. Prove every claim. Dispatch independent claim groups to parallel workers; use `git` worktrees at the same pinned target whenever workers modify files. For dirty local targets, reproduce and record the same tracked and untracked input state in each proof worktree without altering the original. Give each worker claim IDs, target identity, test seam, permitted edits, resource ownership, and the evidence contract above. Share read-only discovery; serialize runs sharing mutable databases, cloud resources, ports, or fixtures unless isolated. Keep the original launch root and explicit checkout separate when invoking `testing-integrations`. Require real assertions and confirm intended tests executed; exit code alone or zero collected tests proves nothing. If parallel execution is unavailable, run the same groups sequentially and report the limitation. Reconcile every worker result, including failures and blockers, into its claim record. Preserve regression patches and instrumentation diffs; report their effect on proof validity.
7. For a big or wide change, *run `subagents` skill to compare independent candidates and synthesize findings* using **Arena** with two or three distinct model perspectives. Pass the same diff, safety question, grounding, and report contract to each reviewer, with isolated outputs under the absolute run directory. Have reviewers return evidence without starting another Arena. Screen for reproducible proof and cited risks. Merge every distinct supported risk into the report, including findings outside the chosen base. Send newly discovered claims through steps 5–6.

## Completeness verification

Before reporting, reconcile the diff and behavior inventory with the evidence records:

- Every changed behavior maps to affected boundaries and downstream consumers, or an evidenced explanation that none apply.
- Every affected behavior maps to a confirmed risk, clearance, or named uncertainty; check relevant contracts, failure paths, configuration, and concurrency beyond the happy path.
- Every risk and safety claim, including cleared claims, has a verdict, ladder level, method, evidence, and an unproven reason/next step when executable proof is missing.
- Every dispatched proof has a completed result or explicit unresolved status. Include newly discovered risks and conflicting results.
- Every proof patch, artifact, worktree, and external resource has a recorded retention or cleanup outcome.

Report **coverage complete | incomplete** with omitted or inaccessible scope, separately from **risks resolved | unresolved**. Coverage complete means the inventory was reconciled, not that every claim was proved or the change is safe. Any unresolved claim makes risks unresolved; confirmed defects remain visible even when verification is complete.

## What to hand back

Recheck the pinned head before reporting when remote state may have changed. State scope and baseline, and give every inspected behavior a supported risk verdict or named uncertainty.

- **What it does.** What changed, including the part that isn't obvious.
- **The one fact it's safe because of.** State it, say which step you got it to, and show the proof. If you couldn't prove it, write unproven.
- **Risks and cleared claims.** Include every claim in the table below; link shared evidence by claim ID without dropping individual verdicts. Keep unresolved risks visible.

  | ID / risk or safety claim | Failure mechanism, location, likelihood / impact | Verdict | Ladder level | Proof method and evidence | Unproven reason / next step |
  | --- | --- | --- | --- | --- | --- |
  | Stable ID and claim | Concrete mechanism and `file:line` | confirmed / cleared / unresolved | 1–5 | Source trace or exact command, test, environment, observed result, artifacts | Reason and next check, or none |

- **Completeness.** Coverage and risk-resolution statuses, behavior-to-claim mapping, omitted scope, conflicts, and blockers.
- **Before you merge.** The cheapest test or repro that catches the real bug, reusable regression patches, remaining checks, and cleanup/retention outcomes.

*Run `writing-style` skill to review prose and remove AI tells* using **Unslop only** on the assembled report. Edit prose only. Preserve citations, commands, observed output, proof status, and risk judgments. Strip private details before sharing publicly.

**Reply:** the writeup above, with every claim's proof level and method, explicit reasons for unproven claims, and both completeness statuses.
