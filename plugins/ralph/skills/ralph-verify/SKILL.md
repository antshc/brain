---
name: ralph-verify
description: Use when verifying changed files with the initialized, skill-owned VERIFY.md guidance.
---

# Feedback Loops

Copy this checklist and check off items as you complete them:

```
Feedback Loops Progress:
- [ ] Step 1: Collect changed files and verification counterparts
- [ ] Step 2: Verify diagnostics, build, tests, and repository checks
```

## Step 1: Collect changed files

Gather the current changed files. For each, identify its nearest module and verification counterpart from the repository structure. Deduplicate modules and counterparts.

**Emit**: "Changed files: [list]. Affected Modules: [list]. Verification counterparts: [list]."

## Step 2: Verify

Read sibling `VERIFY.md` and follow every step in order. `/ralph-init` creates this required guidance before Ralph performs verification.

If verification exposes a code error, fix it and repeat this step for the complete changed-file set. After three failed retries for the same error, report `STATUS: partial`.

If verification fails because of environment or access, report `STATUS: blocked` without attempting a workaround.

**Emit**: "Verify guidance: VERIFY.md."