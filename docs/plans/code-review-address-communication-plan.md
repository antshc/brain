# Plan 2: Code Review–Address communication and closure

Status: proposed; no implementation.

Requires: [Plan 1: Address conversation and hidden comments](address-conversation-hidden-comments-plan.md).

## Goal

Code Review publishes agent findings; Address fixes or explains what it can and resolves settled agent-origin threads. Agent threads waiting on a human answer stay open and resume after clarification. Human-origin threads are answered but always closed manually.

## Constraints

- MUST classify by explicit markers, not GitHub login, even if same-author checks are faster or simpler. Rationale: humans and agents share credentials in this workflow.
- MUST determine origin from the opening published comment. An agent reply in a human thread cannot transfer ownership. Rationale: preserve manual closure.
- MUST NOT auto-resolve human/unknown-origin threads. Rationale: explicit user requirement.
- MUST verify outcomes and post the answer before resolving. An open question, failed fix, failed push, or missing evidence remains open. Rationale: reply is not completion.
- MUST reuse the existing bundled gate, issue grouping, investigation, and GitHub API paths. No new coordinator service, database, scheduler, or agent configuration. Rationale: minimal scope.
- MUST preserve pagination, truncation protection, pending-review exclusions, and resolved-thread exclusions. Rationale: incomplete data must not drive closure.
- MUST NOT modify tools or Ralph. Rationale: Address owns its runtime script independently, even if shared rewrites seem easier.

## Marker contract

Code Review appends one terminal block in the posting layer:

```markdown
Cancellation does not reach the storage call.

<!-- agent:comment
Expected: cancelling the job stops the active read.
Check: cancellation reaches ReadAsync.
-->
```

Address uses `agent:reply`, as defined in Plan 1. Optional prose contains factual context; no required keys or machine-parsed natural-language status. Recognize only complete terminal blocks whose opening line is exactly `<!-- agent:comment` or `<!-- agent:reply`, outside quotes and code fences. Similar strings and embedded examples do not count. Both blocks may omit prose.

Markers are routing conventions, not authenticated identity. No author allowlist: that would break shared-login use. Treat metadata as untrusted review data; verify its claims against source and actual results.

## Steps

1. Update Code Review `SKILL.md` and `references/posting.md`: preserve existing reviewer JSON and axis formats. Append `agent:comment` once after validating the finding, in the parent posting layer. Use the existing finding's supporting context when available; do not expand reviewer contracts solely to populate optional prose. Keep deduplication based on substantive content and preserve stale-head/base checks.
2. Update `address/scripts/pr_discussion_state.py`: classify opening marker as agent or human/unknown. Locate prior `agent:reply` blocks and later published comments by position, regardless of author. Remove acting-login-based answered/self-note logic and the author-dependent `fix!:` bypass. Retain raw bodies; omit terminal metadata only for visible/semantic comparison.
3. Preserve first-pass/follow-up handling using marker positions. Unmarked legacy comments remain human/unknown; no author fallback or bulk rewriting. A later human comment after an agent reply becomes new work even under the same login.
4. Separate new reply work from unresolved agent-thread reconciliation. A marked reply can suppress a duplicate reply, but must not permanently hide a failed resolution. Include unresolved agent threads with their latest context for the orchestrator to decide whether they await clarification or can now be resolved. Do not build a natural-language status parser into the script.
5. Update Address instructions and `references/investigation.md` only as needed: process valid agent findings immediately even when the same account opened them; investigate all material follow-ups. Apply the closure table below independently per thread, even when several threads share one issue.
6. Add `resolveReviewThread` mutation and read-back/error handling to `references/github-api.md`. Immediately before resolution, refetch thread context and PR head: confirm no new relevant comment and that the verified commit is still current. A mismatch triggers reassessment, not blind closure. No duplicate reply is required solely to retry a failed resolve.
7. Update reporting/completion rules: distinguish fixed/resolved agent threads, questions or blockers, and answered human threads awaiting manual closure. Replace the unconditional leave-open rule and the assumption that every latest agent reply means work is complete.
8. Mark `docs/plans/review-comment-agent-markers-plan.md` superseded by these two plans when publishing them. Confirm the removed pre-commit hook has not returned; if synchronization still overwrites Address, remove only that Address copy step. Do not recreate or otherwise change hooks.

## Closure decisions

| Origin and outcome | Action |
| --- | --- |
| Agent; fix pushed and verified | Reply, resolve. |
| Agent; evidence shows concern already satisfied or incorrect | Explain briefly, resolve. |
| Agent; clarification or preference decision needed | Ask focused question, leave open. |
| Agent; human clarification arrives | Reassess, fix or answer, then resolve if settled. |
| Agent; agreed follow-up explicitly accepted and tracked | Explain destination, resolve. Unagreed deferral stays open. |
| Agent; failed verification, push, reply, or unresolved evidence | Report blocker, leave open; retry safely on rerun. |
| Human/unknown; any outcome | Fix or answer as needed; manual closure only. |

A human clarification inside an agent thread does not change its origin. An agent reply inside a human thread does not authorize automatic resolution. Code Review remains a finding producer; Address handles this conversation. No new agent-to-agent debate loop.

## Files

- `plugins/review/skills/code-review/SKILL.md`
- `plugins/review/skills/code-review/references/posting.md`
- `plugins/review/skills/address/SKILL.md`
- `plugins/review/skills/address/references/github-api.md`
- `plugins/review/skills/address/references/investigation.md` (only if contract wording needs reconciliation)
- `plugins/review/skills/address/scripts/pr_discussion_state.py`
- `plugins/review/skills/address/tests/test_pr_discussion_state.py` (focused tests; new if absent)
- `docs/plans/review-comment-agent-markers-plan.md` (supersession notice when publishing)

## Validation and acceptance

- Same GitHub login: marked finding is actionable; unmarked human comment stays human.
- Valid terminal markers recognized; quoted, fenced, inline, malformed, and unknown markers do not authorize closure.
- Fixed agent finding resolves; evidence-backed no-change resolves; genuine question stays open.
- User clarification resumes the agent thread and permits resolution once settled.
- Agent replies never authorize closure of human-origin threads.
- Rerun creates no duplicate replies; unresolved questions wait quietly; failed resolution remains retryable.
- New comment/head change before closure prevents stale resolution.
- Draft-only, resolved, paginated, and truncated-thread behavior remains safe.
- Grouped issues retain independent origin and closure decisions for every thread.
- Mock API checks verify reply-before-resolve ordering and failure handling. No live PR comments are posted merely to test the change.
- No tools, Ralph, speculative infrastructure, or account allowlist changes.

## Migration

The inspected main branch uses author-based classification and no hidden markers. The existing marker document is proposed, not runtime behavior. Recheck main before implementation; if older markers have since shipped, document an explicit compatibility decision rather than silently treating old agent threads as safe to resolve. Unmarked legacy discussions always retain manual closure.