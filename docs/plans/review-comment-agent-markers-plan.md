# Plan: Identify PR review agents with hidden HTML comment markers

Status: proposed. No implementation changes.

## Goal

Distinguish human PR discussion from agent-written code-review findings and Address replies, including when both use the same GitHub login. Keep the rendered comment text unchanged.

## Constraints

- **MUST** append exact hidden markers to new Code Review findings and final Address replies. Rationale: classify comments from their content, not their account.
- **MUST NOT** infer agent identity or whether a thread is answered from the GitHub author, even if the same-author rule seems faster or simpler. Rationale: humans and agents may share credentials.
- **MUST** preserve human `fix!:` and `suggest!:` support in Ralph. Rationale: existing reviewer commands continue to work.
- **MUST** preserve resolved-thread and pending-draft-review exclusions. Rationale: no spurious work.
- **MUST NOT** mutate old PR comments, introduce speculative abstraction, or duplicate shared parsing logic. Rationale: minimal, safe migration.

## Marker contract

Append one exact, standalone marker as the final line of the corresponding GitHub comment body:

```markdown
Evidence-backed finding text.

<!-- brain:code-review:v1 -->
```

```markdown
Fixed.

<!-- brain:address:v1 -->
```

- `brain:code-review:v1`: agent-authored finding that requires review/response.
- `brain:address:v1`: final agent reply that answers the thread for the current run; use for both Address and Ralph fix replies, including clarification questions.
- Detect only the exact marker on its own final line, allowing trailing whitespace. Do not mistake inline examples or quoted text for markers.
- Keep the marker out of visible prose and reviewer JSON. The posting/reply layer appends it once; read-back checks the complete body.
- Treat markers as routing metadata, not proof of authenticated identity.

## Classification

| Latest relevant comment | Result |
|---|---|
| New Code Review marker | Pending first pass |
| Unmarked human/unknown comment, no prior Address reply | Pending first pass |
| Address marker last | Answered / skip |
| Unmarked comment after Address marker | Pending follow-up |
| Code Review marker after Address marker | Pending follow-up |
| First comment authored by acting GitHub login | Pending unless it is an Address reply to earlier content |
| Resolved thread or pending draft-only review | Exclude (unchanged) |

Track the last marked Address answer and all later comments, not whether their authors match the acting login. Remove `self_opened`, `origin: self`, same-author answered checks, and the author-dependent `fix!:` bypass. Keep first-pass/follow-up context based on marker position. Strip metadata markers only for semantic comparison/display, retain raw comment bodies for classification and GitHub read-back.

## Implementation sequence

1. **Code Review publication.** Update `plugins/review/skills/code-review/SKILL.md` and `references/posting.md`. Append `brain:code-review:v1` in the posting layer after the validated finding, without changing reviewer output or review format. Deduplication compares substantive content, not markers.
2. **Address instructions and replies.** Update `plugins/review/skills/address/SKILL.md` and `references/github-api.md`. Append `brain:address:v1` to every final reply, including no-change and clarification outcomes. Keep progress-only comments distinct from final answers.
3. **Shared discussion gate.** Update `tools/src/modules/github/pr_discussion_state.py`. Replace login-driven state with marker-driven state. Retain pagination/truncation safeguards and pending-review filtering. Remove redundant acting-login lookup if no remaining consumer needs it.
4. **Ralph/tools filter.** Update `tools/src/modules/github/domain/comment.py` and `domain/review_thread.py` (and the existing thread-filter path only if required). Recognize Code Review markers as actionable and Address markers as answered; keep unmarked `fix!:`/`suggest!:` semantics. Update `plugins/ralph/skills/fix/SKILL.md` to append Address markers to its replies.
5. **Synchronize copies.** `.githooks/pre-commit` copies the shared GitHub module into `plugins/ralph/skills/{fix,dev}/github/` and the discussion script into `plugins/review/skills/address/scripts/`. Modify the authoritative `tools` source and regenerate mirrors; verify they are identical. Existing Address copy has `self_opened` logic absent from the current shared source, so explicitly reconcile that drift.

## Tests

- In `tools/tests/unit/pr_discussion_state_test.py`: same GitHub login for human/agent; self-authored opening review remains pending; marked answer skips; human or review follow-up reopens; markerless comments remain pending; draft and resolved behavior unchanged.
- In `tools/tests/unit/domain/services/thread_filter_test.py`: marked review is actionable without `fix!:`; marked Address reply excludes; unmarked `fix!:` and `suggest!:` remain actionable.
- In `tools/tests/integration/features/fetch_threads_test.py` and relevant AFK fix/address handler tests: end-to-end filtered thread selection, reply state, rerun idempotency.
- Verify comment posting/read-back preserves the exact final marker and generated Ralph/Address copies match shared source.

## Legacy policy

Unmarked legacy agent comments are indistinguishable from human comments. Treat them as human/unknown, without same-login fallback. Some legacy answered threads can therefore reappear as pending. Do not bulk-edit old GitHub discussions; a separate migration would require explicit approval.

## Acceptance

- Code Review and Address/Ralph replies are tagged automatically while GitHub-rendered prose remains unchanged.
- Re-running Address after a marked answer skips until a new unmarked human comment or new Code Review finding appears.
- Shared-account authorship never causes a finding to be skipped or a human reply to be considered answered.
- Ralph retains existing human command behavior and recognizes new marked findings.
- Tests pass; no unrelated workflow changes.
