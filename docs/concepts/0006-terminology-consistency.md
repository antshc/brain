# Terminology Consistency

## Purpose

A term, once defined at its authoritative source (a skill's own wording, a Concept, an ADR, a glossary entry), gets referenced from many other places — other skills, later turns in the same session, future sessions. If a reference paraphrases or invents its own label instead of reusing the source's exact wording, that reference becomes unverifiable: nothing greps back to a definition, and the model can drift into treating one idea as two different things, or lose track that two mentions point to the same thing.

## Design Guidance

- Define a term once, at its authoritative source, in exact wording — don't leave it implicit across a list of criteria/rules if other documents need to name it as a unit.
- Every other reference to that same idea — in another skill, another document, or a later turn of the same session — must reuse that exact term verbatim. Never paraphrase it, invent a shorthand, or rename it into a "clearer" label; that severs the link back to its definition.
- Before introducing what looks like a new term, check whether it already exists at an authoritative source. If it does, cite it in place; don't redefine or restate it.
- If a needed term doesn't yet exist anywhere, name it explicitly at its actual source (the place that owns the rule/behavior) rather than inventing a label for it at the place that merely consumes it.
- This applies within a single session as much as across documents: once a term is used to name something, keep calling it that for the rest of the session — don't rename it mid-session, even if a rephrase reads more naturally.

## Examples

- `grill-design/SKILL.md`'s `Interview` section names its four decision criteria "the evidence checklist." Its `Domain Modeling` section references "the evidence checklist" verbatim in multiple places rather than restating the four criteria or inventing a different label (an earlier draft used the invented, unverifiable label "evidence-checklist" before the term existed at its source — corrected once the term was named).

