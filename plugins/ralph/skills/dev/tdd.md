# Autonomous TDD Workflow

## Philosophy

Tests verify **behavior through public interfaces**, not implementation details. Code can change entirely; tests shouldn't break unless behavior changes.

- Test _what_ the system does, not _how_ it does it
- A good test reads like a specification: "user can checkout with valid cart"
- If you refactor internals and tests break but behavior hasn't changed, the tests were bad

See [tests.md](tests.md) for good/bad examples, [mocking.md](mocking.md) for mocking rules, [design.md](design.md) for module and interface design.

## Vertical Slices (mandatory)

**Never write all tests first, then all implementation.** That produces tests coupled to imagined behavior.

Write ONE test, make it pass, repeat:

```
RED→GREEN: test1 → impl1
RED→GREEN: test2 → impl2
RED→GREEN: test3 → impl3
```

Each test responds to what you learned from the previous cycle.

## Workflow

1. **Plan** — From the issue description, identify the behaviors to test. Prioritize critical paths and complex logic. Design interfaces for testability (small surface, deep implementation).

2. **Tracer bullet** — Write ONE test for the most important behavior. Make it fail. Write minimal code to pass.

3. **Incremental loop** — For each remaining behavior: write next test → fails → minimal code to pass → passes. One at a time. Don't anticipate future tests.

4. **Refactor** — Only after all tests pass. Extract duplication, deepen modules, apply SOLID where natural. Run tests after each refactor step. Never refactor while RED.

## Per-Cycle Checklist

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
