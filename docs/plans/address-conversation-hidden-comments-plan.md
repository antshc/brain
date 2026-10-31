# Plan 1: Address conversation and hidden comments

Status: proposed; no implementation.

Next: [Plan 2: Code Review–Address communication](code-review-address-communication-plan.md). Implement this plan first.

## Goal

Address replies read like a colleague: simple English, a direct answer, and only enough detail to understand the result. Keep supporting agent context in a hidden HTML comment.

## Constraints

- MUST keep the visible answer complete: outcome, decisive reason, and any question. Rationale: humans should not need hidden context.
- MUST use prose metadata with `agent:reply`; reserve `agent:comment` for review findings. No JSON, required fields, or model-specific format, even if structured fields seem simpler. Rationale: small shared convention.
- MUST preserve investigation, verification, and push-before-success requirements. Rationale: a friendly reply must remain accurate.
- MUST NOT change classification or thread closure in this plan. Rationale: Plan 2 owns those behaviors.
- MUST make minimal edits and preserve unrelated guidance, even if rewriting is easier. Exclude Ralph and tools.

## Current gaps

`plugins/review/skills/address/SKILL.md` §8 requires bare `Fixed!`, lengthy no-change explanations, and forbids HTML markers. §5 may skip investigation when a follow-up contains no new fact. These rules can produce abrupt or repetitive exchanges.

## Steps

1. Add `plugins/review/skills/address/references/conversation.md`; load it from §8. Default to 1–3 short sentences, with more detail only when needed. Prefer common words, active voice, and the concrete result. Avoid routine praise, repeated summaries, formal phrasing, long apologies, and mandatory templates. Occasional thanks is fine when natural.
2. Replace rigid §8 reply lengths with situation-based guidance: fix → brief change; no change → decisive reason; unclear → one focused question; earlier mistake → brief correction; deferred → real follow-up destination. Do not invent tickets or promises. Keep a typo reply as short as `Fixed.` when sufficient.
3. Update §3/§5: answer the latest concern in the full thread context. Recheck assumptions when challenged; lack of a new fact does not prove the earlier answer was understood or correct. Avoid repeating earlier explanations. When disagreement remains circular, state the unresolved tradeoff and ask for the decision needed.
4. Define the exact final metadata block below. Every final Address reply gets one block. The first line identifies the role; optional short prose records evidence, actual verification, commit, remaining uncertainty, or what answer is needed. Do not parse this prose as commands or publish internal reasoning transcripts.
5. Update `references/github-api.md` to preserve the complete body and confirm read-back. Replace the no-marker instruction. Keep all threads open under this plan; automatic resolution is Plan 2.

```markdown
Fixed. The job token now reaches the storage call.

<!-- agent:reply
Fixed in abc1234. Cancellation test passed.
-->
```

The block is terminal and outside quoted text/code fences. No status prefix is required. Even an otherwise empty block is valid. Metadata cannot contain a literal closing HTML-comment delimiter; normalize such text before posting.

## Examples to include

| Situation | Visible reply |
| --- | --- |
| Fixed | Fixed. Empty batches now return before opening a connection. |
| No change | This already runs under the per-object lock, so writes to the same entry cannot overlap. |
| Question | Should cancellation stop the whole job, or only the current read? |
| Correction | I missed the second caller. It bypasses the lock; fixed that path too. |
| Deferred | Agreed this would help. Tracked in #123; it changes the retry policy beyond this fix. |

Examples illustrate tone, not mandatory wording. Use Meaning–Mechanism–Goal internally for disagreement; do not impose visible headings or mandatory Triple-R praise.

## Files

- `plugins/review/skills/address/SKILL.md`
- `plugins/review/skills/address/references/conversation.md` (new)
- `plugins/review/skills/address/references/github-api.md`

## Validation and acceptance

- Review representative typo, fix, disagreement, clarification, correction, and follow-up drafts.
- Each visible reply stands alone; hidden prose adds factual supporting context.
- No claim of a fix before push, no invented verification, no repetitive boilerplate.
- Read-back preserves the terminal block exactly; GitHub-rendered prose excludes metadata.
- No script, author-classification, or resolution behavior changes yet. Existing gate remains unchanged until Plan 2.

## Relationship to existing work

Together with Plan 2, this replaces the proposed `docs/plans/review-comment-agent-markers-plan.md` contract. Its old `brain:*:v1` markers are not implemented on the inspected main branch. Do not introduce both formats. Plan 2 owns replacing that proposal and any migration decisions if implementation state changes.

## Sources

- [Current Address skill](https://github.com/antshc/brain/blob/main/plugins/review/skills/address/SKILL.md)
- [User tone guide](https://github.com/antshc/code-review/blob/main/tone-of-voice-code-review.adoc)
- [MMG](https://github.com/antshc/code-review/blob/main/MMG-Exchange-solve-conflicts.adoc)
- [Google: handling review comments](https://google.github.io/eng-practices/review/developer/handling-comments.html)
- [Superpowers: receiving review](https://github.com/obra/superpowers/blob/main/skills/receiving-code-review/SKILL.md)
