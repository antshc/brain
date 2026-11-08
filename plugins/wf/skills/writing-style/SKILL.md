---
name: writing-style
description: >-
  Write, edit, or review prose. Use for technical docs, PR descriptions and commit messages, unslop, solution-agnostic requirements and stories, or research bottom lines. Also use for 'deepen this task', 'rewrite this prompt', or 'in your own words'.
---

# Writing style

Orchestrator. Pick the task row, read each listed reference fully (no previews), apply them in order. Load nothing the row does not list. For Sharpen, apply its own output procedure and return. Use Pipeline for the other routes unless the row supplies its own output.

## Top rules

- **Cut words that add no information.**
- **Prefer everyday words.** Use a longer word when it is more precise.
- **When a rule makes a sentence worse, fix the sentence another way or leave it alone.** A sentence that follows every rule and sounds machine-written has failed.
- **The codebase is the word list.** Write the real symbol, file, flag, or command name, not a synonym or a description.
- **Describe the operation in plain language.** Define named patterns on first use.

## Routing

| Task | Read, in order |
|---|---|
| Write a new doc (README, RFC, guide, explanation) | [references/modes-diataxis.md](references/modes-diataxis.md), [references/sentences-google.md](references/sentences-google.md), [references/ambiguity-global-english.md](references/ambiguity-global-english.md), [references/rhythm.md](references/rhythm.md), [references/unslop.md](references/unslop.md) |
| Write or review instructions, procedures, runbooks | [references/sentences-google.md](references/sentences-google.md), [references/steps-ste.md](references/steps-ste.md), [references/ambiguity-global-english.md](references/ambiguity-global-english.md), [references/unslop.md](references/unslop.md) |
| Write a PR description or commit message | [references/docs-and-prs.md](references/docs-and-prs.md), [references/sentences-google.md](references/sentences-google.md), [references/unslop.md](references/unslop.md) |
| Review or tighten existing text | [references/rhythm.md](references/rhythm.md), [references/ambiguity-global-english.md](references/ambiguity-global-english.md), [references/unslop.md](references/unslop.md) |
| Unslop only, remove AI tells | [references/unslop.md](references/unslop.md) |
| Write a bottom line (research conclusion, key finding, recommended action, executive takeaway) | [references/bottom-line.md](references/bottom-line.md), [references/steps-ste.md](references/steps-ste.md), [references/unslop.md](references/unslop.md) |
| Normalize requirements, capabilities, features, functional slices, or stories (scrub implementation artifacts) | [references/solution-agnostic.md](references/solution-agnostic.md), [references/solution-agnostic-terms.md](references/solution-agnostic-terms.md); its Output replaces Pipeline |
| Sharpen a task prompt or restate the user's intent (`/writing-style sharpen`, deepen, rewrite this prompt, in your own words) | [Sharpen](tactics/sharpen.md) |
| Another skill needs text written through this style | The row matching the text kind |

Doc-mode choice (tutorial, how-to, reference, explanation) applies to whole documents only. Skip `references/modes-diataxis.md` for short text.

## Pipeline

1. Draft with the structure and sentence references.
2. Apply Unslop last. Preserve meaning and tone.
3. Hand back the text. For a review, list each fix with its guideline heading from `references/unslop.md`.
