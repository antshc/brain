# architect

Human quick reference. Sketch types, signatures, and module structure, then implement by default. Add `checkpoint` to review the design first. Factory Mode requests a design-only handoff to `/design spec`. Agent rules live in [SKILL.md](SKILL.md) and [design/design.md](design/design.md).

## Use

Trigger: `/architect`, "architect this", "design this". Use for non-trivial work where jumping to code locks in the wrong shape.

```
/architect add a GSI on orders by customerId + createdAt, no downtime during backfill
/architect checkpoint design retries
/architect arena-agents=2 design retries
/architect arena-agents=3 design retries
/architect interrogate intent: no rejected writes during backfill; target: DynamoDB Local
/architect deep-module design: deepen the order pricing cluster; where should the seam go?
```

`arena-agents`: 1–3, default 1. One candidate skips the judge and grafting; multiple viable candidates use the cross-family judge. The parent architect screens and verifies in both cases.

`/architect interrogate <request>` runs only Interrogate on the named scope (default: branch diff), skipping all design phases; reports findings and stops. `adversaries=1`–`3` (default 1) sets the Interrogate adversary count.

## Flow

| Phase | What happens | Output |
|---|---|---|
| A Ground | Research How explains the touched subsystems; Research Why adds history and rationale when the design redefines ownership or layering; technical unknowns automatically route to Research or Experiment | grounding notes and evidence |
| B Sketch | `arena`: one runner by default; with 2–3, compare candidates and graft good ideas | usage sketch, module map, types, rationale |
| C Review | resolve technical questions and challenge material claims automatically; pause only for an explicit checkpoint, then support **accept**, **implement**, **corrections**, **interrogate**, **prove**, or **ask** | `review-log.md` |
| D Hand off | when the caller requests a design-only handoff, return the sketch for `/design spec` | design artifacts |
| E Implement | default: scaffold commit, then fill in code in the current branch; log and resolve deviations | scaffold commit, code |
| F Scrap | repeated friction during E (same workaround, escape-hatch types, repeated deviations): re-ground, subtract, re-run B and C | new sketch |

Artifacts: `<repo-root>/tmp/architect-<slug>/`.

## Features

| Feature | Helps when | Example request |
|---|---|---|
| `how` | you need a mental model of existing code before designing | `/architect how does the webhook delivery pipeline work, then design retries` |
| `why` | you must know why code has its shape before changing it (history, PRs, tickets, incidents) | `/architect why is billing split from orders? then redesign the boundary` |
| `arena` | you want a design candidate or competing whole-shape designs | automatic in Phase B; use `arena-agents=2` or `3` for comparison |
| `checkpoint` | you want to approve the sketch before implementation or handoff | `/architect checkpoint design retries` |
| corrections | during a checkpoint, edit the sketch without re-running Arena (add `; arena` for a fresh candidate) | `corrections: make Retry a policy object, drop the scheduler interface` |
| `interrogate` | you want the sketch attacked; findings need a run as proof | see below |
| deep-module design | you want a deeper module interface, a seam placed, or testability improved; also resolves contract findings from Interrogate via Design It Twice (3+ radically different interfaces, compared on depth, locality, seam placement) | `/architect deep-module design: deepen the retry cluster` |
| `prove` | one uncertain part needs real evidence; Experiment selects the smallest sufficient method (command, script, test, simulation, or throwaway prototype); add `; interrogate` to have adversaries attack it | `prove: concurrent GSI creation limit; target: DynamoDB Local` |
| accept | approve a checkpoint and continue the requested flow | `accept` |
| implement | at a checkpoint, implement directly even if the caller requested a design-only handoff | `implement` |

Checkpoint replies use plain chat. An ambiguous reply is never treated as accept or implement.

## Open questions and risks

Architect resolves source facts (codebase, NuGet packages, cloud, web) through Research, which routes codebase and NuGet parts through its Explore route and NuGet tactic, and runtime uncertainty through Experiment before review. Material falsifiable claims automatically trigger Interrogate when a safe runnable target exists. Examples: SDK-version contracts need research; CLI capabilities or concurrency need execution; retry duplication needs an adversarial probe. Research owns its specialist fan-out.

Open questions and risks remain phrased as questions; without checkpoint, apply evidence-backed corrections and document reasonable defaults. With checkpoint, design corrections wait for your reply. Unanswered ones carry into the spec. Unchanged evidence and existing Interrogate coverage are reused; changes recheck only affected assumptions. Review includes evidence, limitations, and proposed corrections.

| Your call | Reply | Result |
|---|---|---|
| You know the answer | `corrections: Q2 → keep per-tenant tables` | sketch, design, rationale updated together; logged in `review-log.md`; no arena re-run |
| Risk unproven | `interrogate, scope: risk 1 ...` + intent + runnable target | adversaries try to prove it; verified findings return as proposed corrections |
| You don't know | ask in chat, or request `how`/`why` | facts first, then `corrections` |
| Acceptable | `accept` | Phase E, or Phase D for a design-only handoff |
| Build now | `implement` | Phase E |

Resolve shape-changing items (ownership, boundaries, data keys) before accepting. ADR, Concept, or glossary conflicts need a decision: change the design or knowingly accept the deviation.

```
corrections:
- Q1: yes, retries live in the delivery worker
- Q2: no, drop the scheduler interface
- Risk 2: accept, note for the spec
```
With checkpoint, interrogate Risk 1 in a separate reply: a mixed reply may trigger a clarifying question.

## Interrogate

Runs automatically for material falsifiable claims with a safe target, on request in review, or standalone via `/architect interrogate <request>`. Three adversaries by default (different model families; `adversaries=N` for 1–3) use Experiment to select executable probes and try to break the change in their own worktrees. A finding survives only if its command, rerun by the skill, shows the failure and the failure breaks your intent. Reports findings; applies nothing. You then accept proposed corrections one by one.

```
interrogate
```

```
interrogate, scope: tmp/architect-orders-index/sketch.md
Intent: existing items queryable by customerId sorted by createdAt, no rejected writes during backfill.
Use DynamoDB Local on :8000; do not touch real AWS.
```

Tips:
- Name the intent; unclear intent triggers a question.
- Name the runnable target (DynamoDB Local, moto, LocalStack, test DB). Claims without a run are dropped, so real-AWS-only behavior (throttling, backfill cost) needs permission to use a dev account.
- Default scope with no scope named: branch diff from merge base through the working tree.
- Output: Intent, verified Findings (command, output, how it breaks intent, finders), Dropped counts per adversary. "No verified findings" is a valid result.

## Prove

One question, proven or refuted by real evidence: observed output, never reasoning alone. A prover subagent runs the `experiment` skill in its own worktree (code changes allowed there); Experiment picks the smallest method that settles it, and a throwaway prototype is only one option. The skill reruns its command. Add `; interrogate` to the reply to have `interrogate` attack the diff or the command and observation; otherwise it is skipped. Evidence returns as proposed corrections; the sketch stays `not implemented` and no proof code enters it. The worktree is removed after the round; `report.md` and a patch only when code was created stay under `tmp/architect-<slug>/prove/<question-id>-<revision>-<attempt>/`.

```
prove: does a second GSI creation fail while the first backfills? target: DynamoDB Local on :8000; interrogate
```

## Files

| Path | Role |
|---|---|
| `design/` | design workflow procedure (Phases A–F), evidence routing, red flags, rationale template, deep-module vocabulary, Design It Twice |
| [Research](../research/SKILL.md) | How and Why grounding |
| [Subagents](../subagents/SKILL.md) | Arena, dispatch and model roles |
| `arena/runner-prompt.md` | architecture runner and sketch discipline |
| `interrogate/` | adversarial review procedure |
| `prove/` | evidence procedure via Experiment (command to prototype), optional interrogate |

