# Plan: Identify PR review agents with hidden HTML comment markers

Status: proposed. No implementation changes.

## Goal

Distinguish human PR discussion from agent-written Code Review findings and Address replies, including when both use the same GitHub login. Keep the rendered comment text unchanged. Scope: Code Review, Address, and the tools discussion-state gate; Ralph is excluded.

## Constraints

- **MUST** append exact hidden markers to new Code Review findings and final Address replies. Rationale: classify comments from their content, not their account.
- **MUST NOT** infer agent identity or whether a thread is answered from the GitHub author, even if the same-author rule seems faster or simpler. Rationale: humans and agents may share credentials.
- **MUST NOT** change Ralph skills, filters, handlers, or mirrored code. Rationale: Ralph is outside this change, even if updating a shared consumer seems simpler.
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
3. **Shared discussion gate.** Update `tools/src/modules/github/pr_discussion_state.py`. Replace login-driven state with marker-driven state. Retain pagination/truncation safeguards and pending-review filtering. Remove redundant acting-login lookup if no remaining consumer needs it.
4. **Synchronize Address only.** Update `plugins/review/skills/address/scripts/pr_discussion_state.py` from the authoritative `tools` source; verify the two agree. This Address copy currently has `self_opened` logic absent from the shared source, so reconcile the drift intentionally. `.githooks/pre-commit` also mirrors `tools/src/modules/github/` into Ralph; exclude `pr_discussion_state.py` from those Ralph syncs so no Ralph file changes or behavior updates are introduced. Preserve every other hook operation.

## Tests

- In `tools/tests/unit/pr_discussion_state_test.py`: same GitHub login for human/agent; self-authored opening review remains pending; marked answer skips; human or review follow-up reopens; markerless comments remain pending; draft and resolved behavior unchanged.
- In relevant AFK Address handler tests: pending/answered selection and rerun idempotency use the shared discussion-state classifier.
- Verify comment posting/read-back preserves the exact final marker, the Address copy matches the shared source, and Ralph files remain untouched.

## Legacy policy

Unmarked legacy agent comments are indistinguishable from human comments. Treat them as human/unknown, without same-login fallback. Some legacy answered threads can therefore reappear as pending. Do not bulk-edit old GitHub discussions; a separate migration would require explicit approval.

## Acceptance

- Code Review findings and Address replies are tagged automatically while GitHub-rendered prose remains unchanged.
- Re-running Address after a marked answer skips until a new unmarked human comment or new Code Review finding appears.
- Shared-account authorship never causes a finding to be skipped or a human reply to be considered answered.
- No Ralph skill, module, filter, generated copy, or runtime behavior changes.
- Tests pass; no unrelated workflow changes.
