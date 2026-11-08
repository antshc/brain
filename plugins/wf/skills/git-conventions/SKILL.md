---
name: git-conventions
description: >-
  Format branch names, commit messages, pull request titles and descriptions, and review findings or replies. Use to read a PR initiative marker or apply the hidden HTML rules for agent review comments.
---

# Git Conventions

Select the tactic named by the caller and read its reference. Return formatted text, parsed metadata, or the missing input. The caller owns repository and tracker selection, Git operations, publication, approval, and thread closure.

| Tactic | Caller supplies | Reference |
| --- | --- | --- |
| Name branch | Change intent, work summary, any known work item IDs, optional worker ordinal | [Branches](references/branches.md) |
| Draft commit | Verified change and commit type, or the authorized WF ticket format and identities | [Commits](references/commits.md) |
| Draft PR | Verified head/base, initiative ID, change intent, summary, rationale, changes, verification, and optional references | [Pull requests](references/pull-requests.md) |
| Read PR initiative | PR title and description | [Pull requests](references/pull-requests.md) |
| Draft or finalize review comment | Kind, ownership, stage, verified evidence, and validated visible body for final | [Review comments](references/review-comments.md) |
