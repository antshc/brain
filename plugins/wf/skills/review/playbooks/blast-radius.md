# Blast radius

Find what a change breaks somewhere else, before it ships. Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

Use How and Why from Research to ground what the code does and what led to the change.

Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you.

## Scope and constraints

Accept a diff, commit, branch, local change, or PR, with an optional original defect. Identify repository instructions, target head, comparison baseline, changed paths, affected behavior, and relevant test entry points. Ask when the target or baseline is ambiguous.

Pin committed refs to SHAs. For PRs, inspect the actual head and base, title, body, and commits. For local changes, record the dirty-worktree state. Read the glossary and relevant ADRs when present.

- **MUST NOT** edit tracked production code or existing tests, post PR comments, commit, push, deploy, or reset or clean the user's checkout.
- Run proof scripts or disposable tests in a run-owned location and clean up afterward. Record the exact command, result, and proof level. If safe execution is unavailable, mark the claim unproven.
- Redact secrets, credentials, and customer data. Distinguish source evidence, observed execution, and inference.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it's true. So don't hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code.

### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You showed the bad case can't happen. You walked the failure step by step and it doesn't reach.
4. You ran it. A script or test that calls the real code and fails loud if you're wrong.
5. You reproduced it in the running app.

Step 4 is usually one small script that imports the same library the app ships and calls the exact function you're worried about.

## Steps

1. Read the change. The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. *Run `research` skill to investigate primary sources and return cited findings* using **Why code anchor** (`@mode=why`, `@whyDepth=anchor`). Pass the diff scope and any known PR or commit refs. Request the PR and commit context inline.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. *Run `research` skill to investigate primary sources and return cited findings* using **default Research** for current and downstream behavior around the changed boundary. Pass the changed symbols and safety question. Request `tmp/blast-radius-<slug>/grounding-how.md` as the report path. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run: microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. Be honest about each risk. Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed. List the ones you checked and cleared separately. Distinguish evidence from inference. Cite a real `file:line`, a search that finds nothing is still an answer, and never make up a caller or an API.
5. Prove the one fact. Write a script or test that runs the real code, run it, and paste what happened.
6. For a big or wide change, *run `subagents` skill to compare independent candidates and synthesize findings* using **Arena** with two or three distinct model perspectives. Pass the same diff, safety question, grounding, and report contract to each reviewer, with isolated outputs under `tmp/blast-radius-<slug>/`. Have reviewers return evidence without starting another Arena. Screen for reproducible proof and cited risks. Merge every distinct supported risk into the report, including findings outside the chosen base.

## What to hand back

Recheck the pinned head before reporting when remote state may have changed. State scope and baseline, and give every inspected behavior a supported risk verdict or named uncertainty.

- **What it does.** What changed, including the part that isn't obvious.
- **The one fact it's safe because of.** State it, say which step you got it to, and show the proof. If you couldn't prove it, write unproven.
- **Risks.** Each names how it breaks, the `file:line`, how likely and how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it's fine.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the script you wrote.

*Run `writing-style` skill to review prose and remove AI tells* using **Unslop only** on the assembled report. Edit prose only. Preserve citations, commands, observed output, proof status, and risk judgments. Strip private details before sharing publicly.

**Reply:** the writeup above, with the one safety fact either proven or marked unproven.
