# Module and Interface Design

## Deep Modules

From "A Philosophy of Software Design": **deep module** = small interface + lots of implementation.

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
└─────────────────────┘
```

Avoid shallow modules (large interface, thin implementation — just passes through).

When designing, ask:
- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Interface Design for Testability

1. **Accept dependencies, don't create them** — inject via constructor; never `new` inside (makes replacement impossible in tests)
2. **Return results, don't produce side effects** — prefer queries that return values (CQS) over void methods that mutate state
3. **Small surface area** — fewer methods = fewer tests needed; fewer params = simpler test setup

## Refactor Candidates

After TDD cycle, look for:

- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic
