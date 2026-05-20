# Tests

## Good Tests

Test through real interfaces, not mocks of internal parts. Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests (red flags)

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means (e.g. querying DB directly) instead of the public interface

## Verify Through the Interface

Always verify behavior by calling back through the same public API — not by inspecting internal state, database rows, or side effects directly.
