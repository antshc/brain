---
name: challenge-this
description: >-
  Find problems in a change or design and show them with a run. Use for 'challenge this', 'stress test this code', 'find blind spots', 'tear this apart'. Not for one claim → `prove`; bug fixes → `diagnosing-bugs`.
---

# Challenge this

Adversaries try to break a change or design. Only findings proven by a run survive. Report findings; do not apply fixes. No verified findings means no counterexample found within the reported coverage, not proof of correctness.

For example requests, read [Examples](README.md) in full.

## Inputs

- Scope/diff/PR/design and intent; default scope is branch merge-base through working tree, including scoped dirty inputs.
- Pinned target/baseline, safe runnable target, repository facts, prior evidence and runtime/safety limits.
- `adversaries=1|2|3`, default `1`; independent of design candidate counts.
- `@outputPath`, `@outputBase` for a saved report and explicit worker artifact destinations; no save requested → inline. Missing requested destination → return findings inline and report the blocker.
- Supplied verified worktrees, ownership records and retention/cleanup needs when present.

## Frame

Read relevant repository architecture, ADRs/Concepts and glossary. Derive intent from the user, commits and PR description. *Load and follow the `principles` skill to load indexed engineering principles by name*. Select `In your own words`. Ask when intent is unclear. Pin committed refs and record dirty inputs; for CLI-only evidence scope the claim, command and observation instead of requiring a diff. Done when intent, scope/revision, safe target and limits are explicit.

Reject an adversary count outside the documented values before dispatch. Resolve relative report paths only against the supplied absolute base; an absent/ambiguous base blocks saving, not independent investigation.

## Fan out

Read [Adversary prompt](references/adversary-prompt.md) in full; fill every placeholder. *Load and follow the `subagents` skill to dispatch independent workers with isolated outputs* using Dispatch and the ordered `challenge-this reviewers` pool, with the resolved adversary count. Use skill-capable general-purpose reviewers; request one isolated owned worktree each, copying only scoped uncommitted changes, unless supplied verified checkouts already satisfy isolation. Pass Frame, facts, prior reproductions, limits, exact output destinations and the completed prompt. Keep ownership records and evidence outside worktrees. No safe target/isolation → report blocked scope; continue independent checks only. Done when every assignment has a terminal report or named blocker.

## Verify

Independently rerun each finding's exact command in the reviewer's recorded environment/checkout. Keep it only when actual output reproduces a failure that violates intent against the scoped target. An unrelated failure, missing assertion, zero tests or modified behavior cannot establish the claimed defect. Drop unsupported candidates with reasons; merge common root causes while retaining distinct supported findings and adversary provenance. Reuse reproductions only for unchanged scope/revision/dependencies/environment. Done when every candidate is verified, dropped or explicitly blocked.

## Output

- **Intent** — restatement and expected behavior.
- **Scope** — target/baseline, dirty inputs, environment, tested/excluded areas and blockers, including missing workers.
- **Findings** — each verified failure: title, root cause/location, exact command/working directory, expected/actual output, violated intent, evidence/patch paths and adversaries. Say `no verified findings` when empty; report incomplete coverage separately.
- **Dropped** — each adversary's dropped count and reasons.
- **Handoff** — retained evidence, resource/worktree ownership and cleanup outcome. Contract findings return to Design for proposed Deep Module corrections; Challenge this supplies no interface redesign or fixes.

Preserve reports, patches and rerun prerequisites until verification and requested follow-up finish. Remove only run-owned resources, using *Load and follow the `git` skill to run verified worktree lifecycle* with Worktrees; preserve caller-owned worktrees and report leftovers. Done when every resource is removed or explicitly handed back.

## Completion criteria

- Every assignment/candidate is accounted for; an unavailable worker/runtime is incomplete coverage, not a clean review.
- Every retained finding has reproduced evidence violating intent; every dropped finding has a reason.
- Requested reports and reusable patches survive cleanup at the caller-selected destinations, or missing artifacts are reported.
