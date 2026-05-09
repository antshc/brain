# Tone of Voice in Code Reviews

Tone of voice is **how your message feels**, not just what it says. In code reviews, tone decides whether your comment is received as helpful guidance or personal criticism.

## Core Principles

1. **Aim for clarity, not superiority** — State what you see. Avoid implying the author is wrong or careless.
2. **Target the code, never the person** — Prefer "this method" over "your method." Prefer "this logic creates risk" over "you forgot…"
3. **Be specific about the outcome** — Offer a clear improvement or ask a focused question.
4. **Keep curiosity high and ego low** — Prefer "Could we simplify this by…?" over "Why would you do it like this?"
5. **Balance critique with recognition** — Quick positive notes make change requests easier to receive.

## Comment Format

```
<label>: <clear issue statement>. <concrete impact>. <minimal fix or question>.
```

Labels: `bug` | `suggest` | `nit`

## Rules

- One issue per comment.
- Always explain why it matters.
- Prefer minimal fix over redesign.
- Ground every comment in verified code evidence, not speculation.

## Tone Templates

**Asking a question (non-blocking):**
- "Question: how does this behave when the cache is empty?"
- "I might be missing something — why do we need a retry here?"

**Making a suggestion (respectful):**
- "Suggestion: extracting this into a helper could reduce duplication."
- "Consider using `TryParse` to avoid exceptions here."

**Raising a concern (code-focused):**
- "The current implementation may create a race condition. Could we guard the shared state?"
- "This loop is O(n²). Is that acceptable for the expected dataset size?"

## Pitfalls to Avoid

- **Imperatives**: "Fix this", "Rewrite this."
- **Absolutes**: "Always", "Never."
- **Sarcasm**: "Interesting choice…"
- **Unanchored judgment**: "This is bad code."
- **Personal attribution**: "You wrote this wrong", "You forgot error checks."

## Good vs Bad Examples

| Bad (avoid) | Good (use instead) |
|---|---|
| "You wrote this in a really confusing way." | "This part is a bit hard to follow. Could we rename the variable or add a comment?" |
| "Why didn't you use the standard API?" | "Would using the standard API simplify this flow?" |
| "This is wrong. Fix it." | "I think this condition might miss case X — what do you think?" |
| "You always forget error checks." | "Noticed error handling is missing here. Should we add a guard?" |
