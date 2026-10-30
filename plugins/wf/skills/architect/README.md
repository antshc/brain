# architect

Human quick reference. Sketch types, signatures, and module structure before code; writes production code only after you reply **implement**. Agent rules live in [SKILL.md](SKILL.md).

## Use

Trigger: `/architect`, "architect this", "design this". Use for non-trivial work where jumping to code locks in the wrong shape.

```
/architect add a GSI on orders by customerId + createdAt, no downtime during backfill
/architect arena-agents=2 design retries
/architect arena-agents=3 design retries
```

`arena-agents`: 1–3, default 1. One candidate skips the judge and grafting; multiple viable candidates use the cross-family judge. The parent architect screens and verifies in both cases.

## Flow

| Phase | What happens | Output |
|---|---|---|
| A Ground | `how` explains the touched subsystems; `why` adds history and rationale when the design redefines ownership or layering; technical unknowns automatically route to Research or Experiment | grounding notes and evidence |
| B Sketch | `arena`: one runner by default; with 2–3, compare candidates and graft good ideas | usage sketch, module map, types, rationale |
| C Review | resolve technical questions and challenge material claims automatically, then loop until you reply **accept** or **implement**; otherwise **corrections**, **interrogate**, **prototype**, or **ask** | `review-log.md` |
| D Hand off | after **accept**, run `/to-spec` | spec issue |
| E Implement | after **implement**: scaffold commit, then fill in code in the current branch; deviations surfaced to you | scaffold commit, code |
| F Scrap | repeated friction during E (same workaround, escape-hatch types, repeated deviations): re-ground, subtract, re-run B and C | new sketch |

Artifacts: `<repo-root>/tmp/architect-<slug>/`.

## Features

| Feature | Helps when | Example request |
|---|---|---|
| `how` | you need a mental model of existing code before designing | `/architect how does the webhook delivery pipeline work, then design retries` |
| `why` | you must know why code has its shape before changing it (history, PRs, tickets, incidents) | `/architect why is billing split from orders? then redesign the boundary` |
| `arena` | you want a design candidate or competing whole-shape designs | automatic in Phase B; use `arena-agents=2` or `3` for comparison |
| corrections | the sketch is close; you want a direct edit, no re-run (add `; arena` for a fresh candidate) | `corrections: make Retry a policy object, drop the scheduler interface` |
| `interrogate` | you want the sketch attacked before accepting; findings need a run as proof | see below |
| `prototype` | one uncertain part needs observation; Experiment selects a command, script, test, simulation, or throwaway app, then Interrogate checks it | `prototype: concurrent GSI creation limit; target: DynamoDB Local` |
| accept | the sketch is right; you want a spec | `accept` |
| implement | the sketch is right; build it now in this branch, no spec | `implement` |

Reply in plain chat. An ambiguous reply is never treated as accept or implement.

## Open questions and risks

Architect resolves source facts through Research and runtime uncertainty through Experiment before review. Material falsifiable claims automatically trigger Interrogate when a safe runnable target exists. Examples: SDK-version contracts need research; CLI capabilities or concurrency need execution; retry duplication needs an adversarial probe. Research owns its specialist fan-out.

Open questions and risks remain phrased as questions; your answer resolves intent and tradeoffs. Design corrections wait for your reply. Unanswered ones carry into the spec. Unchanged evidence and existing Interrogate coverage are reused; changes recheck only affected assumptions. Review includes evidence, limitations, and proposed corrections.

| Your call | Reply | Result |
|---|---|---|
| You know the answer | `corrections: Q2 → keep per-tenant tables` | sketch, design, rationale updated together; logged in `review-log.md`; no arena re-run |
| Risk unproven | `interrogate, scope: risk 1 ...` + intent + runnable target | adversaries try to prove it; verified findings return as proposed corrections |
| You don't know | ask in chat, or request `how`/`why` | facts first, then `corrections` |
| Acceptable | `accept` | Phase D |
| Build now | `implement` | Phase E |

Resolve shape-changing items (ownership, boundaries, data keys) before accepting. ADR, Concept, or glossary conflicts need a decision: change the design or knowingly accept the deviation.

```
corrections:
- Q1: yes, retries live in the delivery worker
- Q2: no, drop the scheduler interface
- Risk 2: accept, note for the spec
```
Interrogate Risk 1 in a separate reply: a mixed reply may trigger a clarifying question.

## Interrogate

Runs automatically for material falsifiable claims with a safe target, or on request. Three adversaries (different model families) use Experiment to select executable probes and try to break the change in their own worktrees. A finding survives only if its command, rerun by the skill, shows the failure and the failure breaks your intent. Reports findings; applies nothing. You then accept proposed corrections one by one.

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

## Prototype

One question, one minimal experiment. A builder subagent runs the `experiment` skill in its own worktree (code changes allowed there), the skill reruns its command, then `interrogate` attacks the diff or the command and observation. Evidence returns as proposed corrections; the sketch stays `not implemented` and no prototype code enters it. The worktree is removed after the round; `report.md` and a patch only when code was created stay under `tmp/architect-<slug>/prototype/<question-id>-<revision>-<attempt>/`.

```
prototype: does a second GSI creation fail while the first backfills? target: DynamoDB Local on :8000
```

## Files

| Path | Role |
|---|---|
| [models.md](models.md) | model per role; edit to retune |
| `how/`, `why/` | grounding procedures and prompts |
| `arena/` | multi-model synthesis procedure and runner prompt |
| `interrogate/` | adversarial review procedure |
| `prototype/` | throwaway prototype plus interrogate procedure |
| `references/` | evidence routing, principles, red flags, rationale template, subagent rules |

