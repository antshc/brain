# Output Format

Write for Product Owners and analysts — plain business language, no code, class names, or technical jargon. Emit one block per capability.

## Writing Style
- **Solution-agnostic**: every sentence names a behavior and entity, never a widget, table, endpoint, or access role.
- **Testable**: each functional requirement names an externally visible behavior that can be verified.
- **Compressed**: remove words that carry no meaning; keep every word that does.
- **Domain vocabulary**: use `CONTEXT.md` terms where they exist; fall back to plainest business language.

## Template

```markdown
## <Capability title — behavior + entity, no surface or placement>

### Stakeholder Requirement
The <actor> needs to <behavior> <entity>, so <value>.

### Functional Requirements
- The system must <behavior> when <condition>.
- ...

### Business Rules
- If <condition>, <invariant>.
- ...

### Edge Cases
- <boundary/failure condition> → <expected handling>.
- ...
```

For worked examples, see [examples.md](examples.md).
