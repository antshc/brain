---
description: Use when verifying changed files with initialized, skill-owned FEEDBACK.md guidance.
metadata:
    github-path: plugins/ralph/skills/ralph-feedback
    github-ref: refs/tags/v0.1.0-479
    github-repo: https://github.com/antshc/brain
    github-tree-sha: 64d874c24847374059fa123821f8806c06cd8c68
name: ralph-feedback
---
# Feedback

## Initialize guidance

When `/ralph-init` requests setup, preserve substantive sibling `FEEDBACK.md`; otherwise create it from `templates/FEEDBACK.template.md` and add only evidence-supported changed-file verification commands.

## Verify changed files

Read sibling `FEEDBACK.md` and follow every step in order.

If verification exposes a code error, fix it and repeat this step for the complete changed-file set. After three failed retries for the same error, report `STATUS: partial`.
