---
name: to-review-comment
description: Draft a single, actionable code review comment for a code change or finding. Use when the user wants to write, phrase, or improve a review comment on a specific piece of code.
argument-hint: '<code change, finding, or context to comment on>'
---

**Goal:** turn one finding into a single review comment that names the problem, its impact, and the minimal fix.

**Step 1 — Get the finding**
If `{{input}}` already contains the code change, feedback, or context to comment on, use it.
Otherwise ask: *"Paste the code change, finding, or context you'd like a review comment for."* and wait for the response.

**Step 2 — Draft**
Write the comment in the tone `Tone of Voice in Code Reviews` from `<skill-directory>/references/tone.md` and the template structure from `<skill-directory>/references/comment-template.md`.
Complete when the comment carries one finding with its label, the exact problem, the concrete impact, and the minimal change requested.
