---
name: 'to-review-comment'
description: 'Format a raw code-review comment body into the review tone of voice.'
argument-hint: '<raw comment body>'
---

Format the raw comment as terse, actionable, specific, and calibrated.

**Structure:** `issue → impact → fix`

**Rules:**
- One issue per comment.
- State only essential context.
- Name the exact symbol or code path.
- Explain impact in one sentence.
- Suggest the smallest viable fix.
- Remove praise, repetition, hedging, and background.
