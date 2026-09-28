# Canary Rule Verification

## Purpose

Editing an instructions, skill, or agent file changes how it's *read* — a `frontmatter` key, an `applyTo` glob,
disclosure depth, load order — and that kind of change has no visible effect unless the loading mechanism
itself is exercised. Silence reads as success even when the file never loaded, the glob never matched, or a
disclosed reference was never reached. This Concept fixes how to test that such a change actually took effect,
by observing behavior instead of trusting configuration.

## Rules

- A change to an instructions, skill, or agent file whose effect can't be told apart from doing nothing MUST be
  verified with a canary rule before being trusted.
- A canary rule MUST be obviously artificial and harmless — a marker no organic rule would produce — so that a
  match can only mean the file loaded.
- A canary rule MUST be added to the exact file and section under test, inside the same `applyTo` scope or
  trigger condition as the real change.
- The verifying prompt MUST fall inside that trigger/`applyTo` scope and MUST NOT mention the canary, so the
  observed behavior isn't primed.
- A canary rule MUST be removed immediately after the test, whether it fired or not; it MUST NOT be committed or
  left for a later session to find.
- A canary rule that fails to fire MUST be treated as a signal to check load order, `applyTo` matching, and
  disclosure — not as grounds to add a second canary hoping one sticks.

## Design Guidance

Reach for this test when changing how a file is loaded (frontmatter, `applyTo`, disclosure depth, ordering)
rather than what it says — a content-only edit inside a file already known to load correctly needs no canary.

Prefer a canary that produces a visible artifact in the agent's output or the code it writes (a distinctive
literal, a deliberately inverted style choice) over one that only changes an internal decision with nothing to
inspect afterward.

## Examples

Add, under a stack instructions file's rules section: "All exception handlers must log the literal string
`CANARY-7f3a` before rethrowing." Ask the agent to add error handling to a file matched by that file's
`applyTo`, without mentioning the canary. The string appearing in the generated code confirms the file loaded
and the section applied; its absence points at the file, the section, or the `applyTo` match. Remove the rule
either way once the test concludes.

## Consequences

Confirms load-bearing configuration behaviorally instead of by inspection, at the cost of one throwaway
edit-test-revert cycle per verification.
