# Plan: Identify PR review agents with hidden HTML comment markers

Status: proposed. No implementation changes.

## Goal

Distinguish human PR discussion from agent-written Code Review findings and Address replies, including when both use the same GitHub login. Keep the rendered comment text unchanged. Scope: Code Review and Address only. The bundled Address script is the runtime implementation; `tools` and Ralph are excluded.

## Constraints

- **MUST** append exact hidden markers to new Code Review findings and final Address replies. Rationale: classify comments from their content, not their account.
- **MUST NOT** infer agent identity or whether a thread is answered from the GitHub author, even if the same-author rule seems faster or simpler. Rationale: humans and agents may share credentials.
- **MUST NOT** change `tools` or Ralph scripts, filters, handlers, or tests. Rationale: Address invokes its own script; shared-code rewrites are unnecessary even if simpler.
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
- `brain:address:v1`: final Address reply that answers the thread for the current run, including clarification questions.
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
3. **Address discussion gate.** Update only `plugins/review/skills/address/scripts/pr_discussion_state.py`. Replace login-driven state with marker-driven state. Preserve its pagination/truncation safeguards and pending-review filtering. Remove redundant acting-login lookup if no longer needed. This bundled script already differs from the `tools` version (`self_opened` exists only here); do not replace it wholesale from `tools`.
4. **Decouple hook synchronization.** In `.githooks/pre-commit`, remove only the block that copies `tools/src/modules/github/pr_discussion_state.py` to Address. Rationale: otherwise the pre-commit hook would overwrite the skill-local fix. Keep the Ralph synchronization blocks unchanged; do not alter `tools` or Ralph code.

## Tests

- Add focused tests for `plugins/review/skills/address/scripts/pr_discussion_state.py` (e.g., `plugins/review/skills/address/tests/test_pr_discussion_state.py`): same login for human and agent; self-authored opening finding pending; marked answer skips; follow-up reopens; unmarked legacy comments pending; draft/resolved behavior unchanged; rerun idempotency.
- Verify comment posting/read-back preserves the exact final marker. Verify the pre-commit hook no longer overwrites Address and all existing Ralph synchronization remains unchanged.
- Do not update `tools/tests/` because `tools/src/modules/github/pr_discussion_state.py` is out of scope.

## Legacy policy

Unmarked legacy agent comments are indistinguishable from human comments. Treat them as human/unknown, without same-login fallback. Some legacy answered threads can therefore reappear as pending. Do not bulk-edit old GitHub discussions; a separate migration would require explicit approval.

## Acceptance

- Code Review findings and Address replies are tagged automatically while GitHub-rendered prose remains unchanged.
- Re-running Address after a marked answer skips until a new unmarked human comment or new Code Review finding appears.
- Shared-account authorship never causes a finding to be skipped or a human reply to be considered answered.
- No `tools` or Ralph skill, script, test, generated copy, or runtime behavior changes. The Address script owns its classification independently.
- Address-local tests pass; only the Address synchronization portion of the pre-commit hook changes.
