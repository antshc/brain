# Structure implementation — body template

```md
# <Concept Name>
**Type:** Architecture Pattern | Technical Approach | Code Pattern

## Purpose
<The problem this concept solves in this system, and why we use it.>

## Concept
<One sentence naming the general pattern (≤1 external link); then this system's structural decisions — bound, trigger, state store, signal, naming scheme, owner.>

## Rules

- MUST <mandatory rule>
- SHOULD <recommended rule>
- MUST NOT <forbidden practice>

<!-- @: repeat per variant in use; omit when only one approach -->
### Variant: <name>
**Selected when:** <condition>

- MUST <variant rule>

---

## Optional: Example
<Diagram (*run `doc-code-diagram` skill for class responsibilities, interfaces, dependencies*), flow (*run `doc-behavior-diagram` skill, preferring a **Sequence Diagram**, for call-chain order, cross-boundary calls, decision paths*), code example (real implementation trimmed to rule-relevant lines; an invented one is labelled `Sketch — not the implementation`; MAY pair with the sequence diagram, showing the code behind its key steps), configuration, or package structure.>

## Optional: Benefits and Trade-offs
**Benefits**

- 
**Trade-offs**

- 

## Optional: Validation
<How compliance is checked, e.g. tests, code review, linting, architecture rules.>

## Optional: References

-
```

Include only applicable optional sections. Keep each `Rules` bullet atomic and checkable.
