# Address conversation flows

[Address](SKILL.md) investigates PR review discussions, fixes verified concerns, and replies using [Review conversation](../review-conversation/SKILL.md).

These flows describe PR #172 behavior. The gaps below are limitations and proposed follow-ups, not implemented guarantees.

## Ownership and execution

- An opening published `agent:comment` block identifies an agent-origin thread.
- Unmarked findings, including human-approved HITL findings, retain manual closure.
- Address publishes `agent:reply` blocks. GitHub login does not determine origin or whether a reply needs work.
- A new human reply makes an unresolved thread pending, including replies under the same account used by the developer and review agents.
- A human reply does not launch Address. A user or external workflow must invoke it again.

## Conversation flows

```text
Flow: Review conversation

1. Developer agent creates PR.
2. Reviewer opens a thread.
   → A: /code-review finding → Run Agent Review
   → B: Human finding → Run Human Review
3. On each later /address invocation:
   → Read full thread.
   → Reevaluate new concerns and answers.
4. End


Subflow A: Agent Review

1. /code-review posts finding with agent:comment.
   → Same account as PR author is allowed.
2. /address investigates.
   → Fix clear: implement → verify → push → reply → resolve.
   → Finding incorrect: explain evidence → resolve.
   → Decision missing: ask focused question → leave open.
3. Author answers in a new comment.
   → Same account is allowed.
4. /address reevaluates against code and answer.
   → Enough information: fix or explain → resolve when settled.
   → Still unclear: ask focused question → leave open.
5. No answer:
   → Wait without duplicate replies.
6. Return


Subflow B: Human Review

1. Human posts unmarked finding.
   → Direct comment or human-approved /hitl comment.
2. /address investigates.
   → Agree: implement → verify → push → reply.
   → Unclear: ask focused question.
   → Disagree: explain decisive evidence.
3. Leave thread open for manual closure.
4. Reviewer answers or challenges the reply.
5. /address reevaluates the full conversation.
   → Valid concern: fix → verify → push → reply.
   → Missing decision: ask focused question.
   → Disagreement remains: explain tradeoff and request decision.
   → Acceptance: no further change needed.
6. Human resolves thread.
7. Return
```

Each continuation requires another invocation. Address handles each thread independently, even when several threads describe one issue.

## Closure and reruns

- Only settled agent-origin threads may resolve automatically. Verification, push, reply, or evidence failures leave closure unconfirmed.
- Unanswered questions stay open. Reruns wait without repeating the question.
- Unresolved agent threads with a marked reply enter reconciliation: reassess the outcome or retry safe closure without duplicating the reply.
- Before resolution, refetch complete comments and current head; changed context requires reassessment. Confirm resolution through API read-back.
- Human-origin threads remain open after fixes, disagreement, clarification, and acceptance until a human closes them.

See [the gate](scripts/pr_discussion_state.py) and [GitHub API reference](references/github-api.md).

## Known gaps and policy limits

| Case | Current behavior | Proposed follow-up |
|---|---|---|
| Human edits an earlier comment after Address replied | New work is selected by position after the last marked reply. An edited earlier comment can remain `answered` in a human-origin thread and be skipped. Agent reconciliation includes full context, but the gate does not flag the edit as new work. | Compare bodies and timestamps with the last handled snapshot; reevaluate material edits. |
| Human adds an objection to an already resolved thread | Resolved threads are excluded, so Address does not see the new objection. | Explicitly require reopening, or detect new activity after resolution. |
| Separate human contests the outcome in an agent-origin thread | Origin stays `agent`. Address can still resolve after an evidence-backed answer; human participation does not transfer closure control. | Decide whether an explicit human objection transfers closure control. Recommendation: require manual closure after that objection. |

Until these follow-ups are implemented, add clarification as a new reply in an unresolved thread. Reopen a resolved thread before requesting another Address pass.

## Review evidence

Reviewed at commit `120842d10454a4b5890f318409adae4a583103ae`. Direct gate checks reproduced:

- A new same-login clarification becomes `pending` / `follow-up`.
- An edited earlier human comment can remain `answered`.
- A new objection on a resolved agent thread is excluded and the gate returns `skip` when no other work exists.

These checks exercised classification locally; live GitHub posting and resolution were not exercised.
