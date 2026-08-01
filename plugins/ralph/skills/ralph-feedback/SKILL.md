---
name: ralph-feedback
description: Use when verifying changed files with initialized, skill-owned FEEDBACK.md guidance.
---

# Feedback

## Initialize guidance

When `/ralph-init` requests setup, preserve substantive sibling `FEEDBACK.md`; otherwise create it from `templates/FEEDBACK.template.md` and add only evidence-supported changed-file verification commands.

## Verify changed files

Read sibling `FEEDBACK.md` and follow every step in order.

If verification exposes a code error, fix it and repeat this step for the complete changed-file set. After three failed retries for the same error, report `STATUS: partial`.