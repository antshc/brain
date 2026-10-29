# architect

Human quick reference. Sketch types, signatures, and module structure before code; never writes production code. Agent rules live in [SKILL.md](SKILL.md).

## Use

Trigger: `/architect`, "architect this", "design this". Use for non-trivial work where jumping to code locks in the wrong shape.

```
/architect add a GSI on orders by customerId + createdAt, no downtime during backfill
```

## Flow

| Phase | What happens | Output |
|---|---|---|
| A Ground | `how` explains the touched subsystems; `why` adds history and rationale when the design redefines ownership or layering | grounding notes |
| B Sketch | `arena`: 3 models design in parallel, a cross-family judge scores, best base wins, good ideas grafted | usage sketch, module map, types, rationale |
| C Review | loop until you reply **accept**; otherwise **corrections**, **interrogate**, or **ask** | `review-log.md` |
| D Hand off | run `/to-spec`, then optionally `/implement-spec <spec issue URL>` | spec issue, draft PR |

Artifacts: `<repo-root>/tmp/architect-<slug>/`.

## Features

| Feature | Helps when | Example request |
|---|---|---|
| `how` | you need a mental model of existing code before designing | `/architect how does the webhook delivery pipeline work, then design retries` |
| `why` | you must know why code has its shape before changing it (history, PRs, tickets, incidents) | `/architect why is billing split from orders? then redesign the boundary` |
| `arena` | you want competing whole-shape designs, not one model's first idea | automatic in Phase B; no request needed |
| corrections | the sketch is close; you want a direct edit, no re-run | `corrections: make Retry a policy object, drop the scheduler interface` |
| `interrogate` | you want the sketch attacked before accepting; findings need a run as proof | see below |
| accept | the sketch is right | `accept` |

Reply in plain chat. An ambiguous reply is never treated as accept.

## Open questions and risks

Phrased as questions; your answer resolves them. Nothing moves until you reply. Unanswered ones carry into the spec.

| Your call | Reply | Result |
|---|---|---|
| You know the answer | `corrections: Q2 → keep per-tenant tables` | sketch, design, rationale updated together; logged in `review-log.md`; no arena re-run |
| Risk unproven | `interrogate, scope: risk 1 ...` + intent + runnable target | adversaries try to prove it; verified findings return as proposed corrections |
| You don't know | ask in chat, or request `how`/`why` | facts first, then `corrections` |
| Acceptable | `accept` | Phase D |

Resolve shape-changing items (ownership, boundaries, data keys) before accepting. ADR, Concept, or glossary conflicts need a decision: change the design or knowingly accept the deviation.

```
corrections:
- Q1: yes, retries live in the delivery worker
- Q2: no, drop the scheduler interface
- Risk 2: accept, note for the spec
```
Interrogate Risk 1 in a separate reply: a mixed reply may trigger a clarifying question.

## Interrogate

Three adversaries (different model families) try to break the change in their own worktrees. A finding survives only if its command, rerun by the skill, shows the failure and the failure breaks your intent. Reports findings; applies nothing. You then accept proposed corrections one by one.

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

## Files

| Path | Role |
|---|---|
| [models.md](models.md) | model per role; edit to retune |
| `how/`, `why/` | grounding procedures and prompts |
| `arena/` | multi-model synthesis procedure and runner prompt |
| `interrogate/` | adversarial review procedure |
| `references/` | principles, red flags, rationale template, subagent rules |
