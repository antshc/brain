# Wayfinder ticket types

Unknowns/risks stay in root **Not yet specified** until resolved; concrete child issues track progress. One unknown may need several work items. HLD Open Questions are user-owned presentation content, never a discovery tracker.

| Type | Use when | Execution / completion |
| --- | --- | --- |
| Research | Facts or coarse fog need clarification | AFK cited findings through Research; integrated deciding evidence resolves factual question |
| Experiment | A falsifiable claim needs an actual check | AFK Prove generation/verification; HITL prototype approval before integration/closure; inconclusive stays open/blocked |
| Grilling | Requirements, preferences or trade-offs need a user choice | HITL Grill; explicit answer and closing sweep |
| Contract design | New/significantly changed interface, inheritance abstraction, invariant/error/ordering/seam choice | AFK Deep Module generates 3+ Code Sketch options with individual Markdown rationales; retain worktree without merge. HITL Choice on same ticket, then selected-only merge plus considered-option notes and closure |
| Task | Code Sketch or prerequisite access/data work unblocks a decision | AFK artifact generation or authorized work; Code Sketch awaits HITL prototype approval before integration/closure; otherwise HITL checklist; never implementation of the destination |

Challenge this is supporting verification inside an existing issue or root-owned run, **not its own tracking ticket**. Record scope, evidence, coverage and pending steps on that owner; create follow-up issues only for actual discovered work. It can target the whole HLD but requires a safe runnable boundary for retained findings.

## Rules

- Contract test: new/significantly changed contract or inheritance abstraction → Contract design, not Grilling. Human Choice remains on the same open issue after Options; release claim while waiting.
- Default human decisions → Grilling. Helpers clarify supporting facts automatically; no agent speaks for the user.
- Directly spawn skill-capable general-purpose helpers using Wayfinder's supplied `@helperDispatch`; no Subagents skill. Forward to nested helpers. Use the Git skill for worktrees where isolation is needed.
- Reassess root fog after every result/answer; retain partially resolved risks and blocked choices. Supported resolution moves to Decisions so far before removing active fog; reopening preserves stable ID.
- A completed helper run does not by itself resolve its parent unknown or imply verified mitigation. No counterexample found establishes only tested coverage.

## Artifact lifecycle

Wayfinder pins integration HEAD and exact outputs. Research uses `docs/research/<initiative-slug>/`; proof/sketch evidence uses `docs/prototype/<initiative-slug>/`. Every prototype-producing run uses an owned result worktree, even read-only checks emitting reports. Producers do not commit/push. Follow Wayfinder Prototype approval: generated → verified → awaiting approval → approved → integrated. Retain exact payload identity, worktree and open issue/root state until explicit approval; Research-only artifacts remain automatic. Wayfinder owns verified local commits/merges and cleanup after approved integration, synchronization and all consumers finish. Contract design merges **after user selection**, selected artifacts and considered-option notes only; retain candidates through Choice/review. No evidence appendices, Confluence subpages/attachments, automatic push or PR.

## Source

- [Wayfinder origin](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md)
