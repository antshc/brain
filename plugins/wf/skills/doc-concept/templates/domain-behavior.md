# Domain behavior — body template

```md
## Purpose
<Business outcome; workflows and building blocks governed.>

## Rules
- MUST <one domain invariant, enforcement point, or visible validation behavior>.

## Design Guidance
<Explain how actors, components, and domain objects share responsibility.>

| Trigger / step | Responsible role | Input → outcome | Rule / invariant |
|---|---|---|---|
| <one representative step> | <owner> | <observable result> | <condition> |

<Describe relevant alternate paths, user-facing errors, cancellation, or safety checks.>

## Violation signals
- <Observable breach; omit heading if none.>

## Exceptions
- <Permitted variation and its condition; omit if none.>

## Examples
- <One concrete scenario with input and expected result; cite code/test if present.>

## Consequences
- <Material trade-off; omit if none.>
```

Include only applicable optional headings and table columns. Business processes, business rules, validation, safety, and domain-oriented batch processing belong here when the shared domain outcome is the central rule.
