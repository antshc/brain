---
name: writing-style
description: >-
  Writes, edits, or reviews prose against loaded style references. Use for technical writing, unslop, docs, PR descriptions, commit messages, AI tells, normalizing requirements and stories of leaked implementation artifacts, or a research bottom line. Returns text clear on first read.
---

# Writing style

Orchestrator. Pick the task row, read each listed reference fully (no previews), apply them in order. Load nothing the row does not list.

## Top rules

- **Cut every word that does no work.** "In order to" is "to". "It is important to note that" is nothing.
- **Use the short, everyday word.** "Use", not "utilize". "Do", not "perform". A long word must buy its length with precision.
- **When a rule makes a sentence worse, fix the sentence another way or leave it alone.** A sentence that follows every rule and sounds machine-written has failed.
- **The codebase is the word list.** Write the real symbol, file, flag, or command name, not a synonym or a description.
- **Don't invent jargon.** Use words a developer says out loud: "move", "delete", "a budget that only decreases", not "evacuate", "ratchet", "endgame". A named pattern is fine when the doc defines it on first use. Report a new offender and its replacement as a diff to Jargon in `references/ai-tells.md`.

## Routing

| Task | Read, in order |
|---|---|
| Write a new doc (README, RFC, guide, explanation) | [references/modes-diataxis.md](references/modes-diataxis.md), [references/sentences-google.md](references/sentences-google.md), [references/ambiguity-global-english.md](references/ambiguity-global-english.md), [references/rhythm.md](references/rhythm.md), [references/ai-tells.md](references/ai-tells.md) |
| Write or review instructions, procedures, runbooks | [references/sentences-google.md](references/sentences-google.md), [references/steps-ste.md](references/steps-ste.md), [references/ambiguity-global-english.md](references/ambiguity-global-english.md), [references/ai-tells.md](references/ai-tells.md) |
| Write a PR description or commit message | [references/docs-and-prs.md](references/docs-and-prs.md), [references/sentences-google.md](references/sentences-google.md), [references/ai-tells.md](references/ai-tells.md) |
| Review or tighten existing text | [references/ai-tells.md](references/ai-tells.md), [references/rhythm.md](references/rhythm.md), [references/ambiguity-global-english.md](references/ambiguity-global-english.md) |
| Unslop only, remove AI tells | [references/ai-tells.md](references/ai-tells.md) |
| Write a bottom line (research conclusion, key finding, recommended action, executive takeaway) | [references/bottom-line.md](references/bottom-line.md), [references/steps-ste.md](references/steps-ste.md), [references/ai-tells.md](references/ai-tells.md) |
| Normalize requirements, capabilities, features, functional slices, or stories (scrub implementation artifacts) | [references/solution-agnostic.md](references/solution-agnostic.md), [references/solution-agnostic-terms.md](references/solution-agnostic-terms.md); its Output replaces Pipeline |
| Another skill needs text written through this style | The row matching the text kind |

Doc-mode choice (tutorial, how-to, reference, explanation) applies to whole documents only. Skip `references/modes-diataxis.md` for short text.

## Pipeline

1. Draft with the structure and sentence references.
2. Run the AI tells pass last. Preserve meaning and tone.
3. Hand back the text. For a review, list each fix with its rule number from `references/ai-tells.md`.
