# Research map template

## Map

```markdown
# {{destination short name}} — research map

## Destination

{{decision, explanation, design, or action the findings must support — one or two lines}}

## Notes

{{constraints that can change the answer; resolved API/SDK versions; standing preferences}}

## Topics

<!-- @: repeat the Topic block below for open topics, ordered by risk -->

## Findings so far

<!-- @: one line per resolved topic -->

- [{{topic title}}]({{findings file or experiment link}}) — {{one-line gist of the finding}}

## Not yet specified

{{coarse in-scope areas not yet sharp enough to become topics}}

## Out of scope

{{excluded work and one-line reason per item}}
```

## Topic

```markdown
### {{topic title}}

- **Type:** {{type| research | hypothesis }}
- **Question:** {{research: the fact to surface}} | **Claim:** {{hypothesis: the falsifiable claim}} — **confirmed when** {{observable condition}}, **refuted when** {{observable condition}}
- **Resolve via:** {{resolver| research | experiment }}
- **Blocked by:** {{titles of open topics this waits on, or none}}
```

## Rules

- Emit Question for research, Claim with observable confirm/refute conditions for hypotheses. Remove the unused alternative.
- Blocked by names topic titles, or none. Refer to topics by title in narration and tables.
- Keep unresolved topics in Topics; add Status with the partial, blocked, declined, or inconclusive reason when applicable.
- Findings so far links only resolved topics and states their supported finding. Preserve existing links when resuming.
- Remove template comments and placeholders from output. Keep every map section; use none for empty sections.
