---
name: 'to-review-tone'
description: 'Format a raw code-review finding body into the review tone of voice. Invoked by review sub-agents and review skills before emitting a finding.'
argument-hint: '<raw finding body: issue, why it matters, minimal fix>'
---

# Review Tone

Format one raw finding into the code-review tone of voice.

## Steps

1. **Read input.** `{{input}}` = `<the issue>. <why it matters>. <smallest safe fix>.` If missing, ask: *"Paste the raw finding body you'd like formatted in the review tone."* and wait.
2. **Rewrite** in the tone below. Keep one finding: exact problem, concrete impact, minimal fix. Return only the formatted body.

## Tone Principles

- **Clarify, don't judge** — state what you see; don't imply the author is wrong or careless.
- **Target code, not people** — say "this method," not "your method."
- **Name the outcome** — offer a concrete improvement or a focused question.
- **Stay curious, drop ego** — ask "Could we simplify this by…?" not "Why do it like this?"
- **Recognize, then critique** — a quick positive note eases change requests.

## Rules

Include:
- One concrete finding per comment.
- The exact problem, its concrete impact, and why it matters.
- The narrowest fix that solves it.
- Terse text, grounded in verified code evidence.
- Test guidance only when coverage is materially missing.

Avoid:
- Speculation without code evidence.
- Style-only feedback unless requested.
- Redesign advice when a local fix suffices.
- Multiple unrelated issues in one comment.

## Tone Templates

Select by context.

**Question (non-blocking):**
- "Question: how does this behave when the cache is empty?"
- "I might be missing something — why do we need a retry here?"

**Suggestion (respectful):**
- "Extracting this into a helper could reduce duplication."
- "Consider using `TryParse` to avoid exceptions here."

**Concern (code-focused):**
- "This may create a race condition. Could we guard the shared state?"
- "This loop is O(n²). Is that acceptable for the expected dataset size?"

## Avoid

- **Imperatives**: "Fix this," "Rewrite this."
- **Absolutes**: "Always," "Never."
- **Sarcasm**: "Interesting choice…"
- **Unanchored judgment**: "This is bad code."
- **Personal attribution**: "You wrote this wrong," "You forgot error checks."

## Good vs Bad

| Bad (avoid) | Good (use instead) |
|---|---|
| "You wrote this in a really confusing way." | "This part is hard to follow. Could we rename the variable or add a comment?" |
| "Why didn't you use the standard API?" | "Would using the standard API simplify this flow?" |
| "This is wrong. Fix it." | "I think this condition might miss case X — what do you think?" |
| "You always forget error checks." | "Error handling is missing here. Should we add a guard?" |
