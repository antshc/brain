# Structural implementation — body template

Retain the existing record's fixed heading set and order. `Design Guidance` must explain the pattern itself, not point to one implementation as its definition.

```md
## Purpose
<Recurring architectural or component problem; affected building blocks.>

## Rules
- MUST <one checkable structural obligation>.

## Design Guidance
<Participants, responsibilities, and extension points.>
<Trigger/input → interactions → observable outcome; contract/API/event/data shape and identity/key types where relevant.>
<Consistency boundary, ordering, concurrency, idempotency, cache invalidation, and failure behavior where relevant.>
<State criteria for choosing the pattern and how to apply it without opening a referenced file.>

## Violation signals
- <2–4 observable or greppable breach patterns; omit if none.>

## Exceptions
- <Permitted deviation and its condition; omit if none.>

## Examples
- <One representative implementation or test link, after the general rule; omit if none.>

## Consequences
- <Accepted trade-off; omit if none.>
```

Include only applicable details and optional headings. A recurring local pattern need not have a standard name. Keep each `Rules` bullet atomic; use resolvable anchors for governed locations; keep volatile lists and runbook commands outside the concept.
